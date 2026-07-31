"""分类流水线编排（进化版）。

支持两种数据源路径：
- MTP 设备：复制到暂存 → 校验 → 读 EXIF → 分类 → 移动归位（单线程，COM 绑定）
- 本地目录：直接读 EXIF → 分类 → 复制/移动归位（move 同卷免复制）
  本地模式支持多线程并发处理 EXIF 读取与文件归位，可调线程数。

通过回调推送进度，与传输层（SocketIO）解耦。
"""
import os
import shutil
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

import config
from core import exif_reader, geocoder, classifier, file_ops


class Pipeline:
    def __init__(self, source, target_root, callbacks=None, operation=None, workers=None, backup_only=False):
        self.source = source
        self.target_root = os.path.abspath(target_root)
        self.cb = callbacks or {}
        self.operation = operation or config.DEFAULT_OPERATION
        self.backup_only = bool(backup_only)
        # 本地模式才允许多线程；MTP 因 COM 线程绑定强制单线程
        if source.is_local:
            self.workers = max(1, int(workers or config.DEFAULT_WORKERS))
        else:
            self.workers = 1
        self._stop = False
        self._geo_cache = {}
        self._lock = threading.Lock()  # 保护 stats / geo_cache 并发更新

    def stop(self):
        self._stop = True

    @property
    def staging_dir(self):
        return os.path.join(self.target_root, config.STAGING_DIR_NAME)

    # ---- 回调辅助 ----
    def _emit(self, name, payload):
        fn = self.cb.get(name)
        if fn:
            try:
                fn(payload)
            except Exception:
                pass

    def scan(self):
        """扫描图片/视频，返回 entries 列表。"""
        return self.source.walk_images()

    def run(self, entries):
        """对 entries 执行分类归位。返回统计 dict。"""
        os.makedirs(self.target_root, exist_ok=True)
        # 仅 MTP 路径需要暂存区
        if not self.source.is_local:
            os.makedirs(self.staging_dir, exist_ok=True)

        total = len(entries)
        stats = {
            "total": total,
            "processed": 0,
            "by_category": {"photo": 0, "screenshot": 0, "app": 0, "recording": 0, "video": 0, "other": 0},
            "by_region": {},
            "by_app": {},
            "failures": [],
            "operation": self.operation,
            "workers": self.workers,
        }

        if self.workers > 1 and self.source.is_local:
            self._run_parallel(entries, stats, total)
        else:
            self._run_sequential(entries, stats, total)

        # 清理暂存
        if not self.source.is_local:
            file_ops.safe_remove(os.path.join(self.staging_dir, "_tmp"))
            try:
                if os.path.isdir(self.staging_dir) and not os.listdir(self.staging_dir):
                    os.rmdir(self.staging_dir)
            except OSError:
                pass

        stats["staging_dir"] = self.staging_dir if not self.source.is_local else None
        stats["stopped"] = self._stop
        self._emit("complete", stats)
        return stats

    def _run_sequential(self, entries, stats, total):
        for index, entry in enumerate(entries, start=1):
            if self._stop:
                self._emit("log", {"msg": "已收到停止信号，终止后续处理", "index": index})
                break
            name = entry.get("name", "?")
            result = self._process_one(entry)
            self._record(stats, result, name, index, total)

    def _run_parallel(self, entries, stats, total):
        """多线程并发处理（仅本地模式）。EXIF 读取为 I/O 密集，并行可显著提速。"""
        with ThreadPoolExecutor(max_workers=self.workers, thread_name_prefix="classify") as ex:
            futures = {}
            for entry in entries:
                if self._stop:
                    break
                fut = ex.submit(self._process_one, entry)
                futures[fut] = entry
            done = 0
            for fut in as_completed(futures):
                if self._stop:
                    # 取消未开始的；已运行的让其自然完成
                    for f in futures:
                        f.cancel()
                    break
                entry = futures[fut]
                name = entry.get("name", "?")
                try:
                    result = fut.result()
                except Exception as e:
                    result = {"ok": False, "error": str(e), "staging": None}
                done += 1
                self._record(stats, result, name, done, total)

    def _record(self, stats, result, name, index, total):
        """线程安全地更新统计并推送进度。"""
        with self._lock:
            stats["processed"] = index
            if result["ok"]:
                t = result["type"]
                stats["by_category"][t] = stats["by_category"].get(t, 0) + 1
                if result.get("region"):
                    r = result["region"]
                    stats["by_region"][r] = stats["by_region"].get(r, 0) + 1
                if result.get("app"):
                    a = result["app"]
                    stats["by_app"][a] = stats["by_app"].get(a, 0) + 1
            else:
                stats["failures"].append({
                    "name": name,
                    "error": result["error"],
                    "staging": result.get("staging"),
                })
            ok_counts = stats["by_category"]
            payload = {
                "index": index,
                "total": total,
                "percent": round(index * 100.0 / total, 1) if total else 100.0,
                "current": name,
                "type": result.get("type"),
                "ok": result["ok"],
                "error": result.get("error"),
                "photos": ok_counts.get("photo", 0),
                "screenshots": ok_counts.get("screenshot", 0),
                "apps": ok_counts.get("app", 0),
                "videos": ok_counts.get("recording", 0) + ok_counts.get("video", 0),
                "others": ok_counts.get("other", 0),
                "failures": len(stats["failures"]),
            }
        self._emit("progress", payload)

    def _process_one(self, entry):
        name = entry.get("name", "?")
        try:
            if self.backup_only:
                return self._process_backup(entry, name)
            if self.source.is_local:
                return self._process_local(entry, name)
            return self._process_mtp(entry, name)
        except Exception as e:
            return {"ok": False, "error": str(e), "staging": None}

    def _process_backup(self, entry, name):
        """备份模式：仅复制到目标目录，保留设备原始目录结构，不做分类。

        MTP：先复制到暂存 → 校验 → 移动到 <target>/<相对目录>/<原名>。
        本地：直接复制到 <target>/<相对目录>/<原名>。
        粗判类型仅用于进度展示，不影响文件归位。
        """
        ext = os.path.splitext(name)[1].lower()
        rough = classifier.detect_type(entry["rel"], name, {}, ext)
        if self.source.is_local:
            src = entry.get("abs") or os.path.join(self.source.local_root, *entry["rel"])
            if not os.path.exists(src):
                return {"ok": False, "error": "源文件不存在", "staging": None}
            rel_parts = entry["rel"][:-1]
            dest_dir = os.path.join(self.target_root, *rel_parts) if rel_parts else self.target_root
            file_ops.ensure_dir(dest_dir)
            final_path = file_ops.resolve_collision(os.path.join(dest_dir, name))
            shutil.copy2(src, final_path)
            return {"ok": True, "type": rough, "final": final_path, "new_name": name}

        # MTP 备份
        staging_path, expected_size = self.source.copy_file(entry, self.staging_dir)
        ok, msg = file_ops.verify_integrity(staging_path, expected_size)
        if not ok:
            return {"ok": False, "error": f"校验失败：{msg}", "staging": staging_path}
        rel_parts = entry["rel"][:-1]
        dest_dir = os.path.join(self.target_root, *rel_parts) if rel_parts else self.target_root
        file_ops.ensure_dir(dest_dir)
        final_path = file_ops.resolve_collision(os.path.join(dest_dir, name))
        shutil.move(staging_path, final_path)
        return {"ok": True, "type": rough, "final": final_path, "new_name": name}

    def _process_local(self, entry, name):
        src = entry.get("abs") or os.path.join(self.source.local_root, *entry["rel"])
        if not os.path.exists(src):
            return {"ok": False, "error": "源文件不存在", "staging": None}
        exif = exif_reader.read(src)
        ext = os.path.splitext(name)[1].lower()
        rough = classifier.detect_type(entry["rel"], name, exif, ext)
        geo = None
        if rough == "photo" and exif.get("gps"):
            geo = self._geocode(exif["gps"])
        info = classifier.classify(entry, exif, geo)
        final_path, src_size = self.source.transfer(
            entry, self.target_root, info["rel_target"], info["new_name"], self.operation
        )
        # 校验
        ok, msg = file_ops.verify_integrity(final_path, src_size)
        if not ok:
            return {"ok": False, "error": f"校验失败：{msg}", "staging": final_path}
        return {
            "ok": True,
            "type": info["type"],
            "region": info["region"],
            "app": info["app"],
            "final": final_path,
            "new_name": info["new_name"],
        }

    def _process_mtp(self, entry, name):
        staging_path = None
        staging_path, expected_size = self.source.copy_file(entry, self.staging_dir)
        ok, msg = file_ops.verify_integrity(staging_path, expected_size)
        if not ok:
            return {"ok": False, "error": f"校验失败：{msg}", "staging": staging_path}
        exif = exif_reader.read(staging_path)
        ext = os.path.splitext(name)[1].lower()
        rough = classifier.detect_type(entry["rel"], name, exif, ext)
        geo = None
        if rough == "photo" and exif.get("gps"):
            geo = self._geocode(exif["gps"])
        info = classifier.classify(entry, exif, geo)
        final_path = file_ops.move_to_final(
            staging_path, self.target_root, info["rel_target"], info["new_name"]
        )
        return {
            "ok": True,
            "type": info["type"],
            "region": info["region"],
            "app": info["app"],
            "final": final_path,
            "new_name": info["new_name"],
        }

    def _geocode(self, gps):
        lat = round(gps["lat"], 3)
        lng = round(gps["lng"], 3)
        key = (lat, lng)
        with self._lock:
            if key in self._geo_cache:
                return self._geo_cache[key]
        result = geocoder.reverse(lat, lng)
        with self._lock:
            self._geo_cache[key] = result
        return result
