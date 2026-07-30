"""USB/MTP 设备交互模块。

通过 Windows Shell.Application COM（pywin32）访问 MTP 便携设备（小米手机），
提供设备枚举、存储探测、图片递归扫描与安全复制能力。

同时提供 LocalSource，用本地目录模拟设备，便于无手机时联调测试。
"""
import os
import shutil
import time
import uuid

import config

# Shell 特殊文件夹常量：ssfDRIVES = 0x11（此电脑）
SSF_DRIVES = 0x11

# CopyHere 标志：静默 + 不确认 + 不确认建目录 + 不弹错误框
FOF_SILENT = 0x4
FOF_NOCONFIRMATION = 0x10
FOF_NOCONFIRMMKDIR = 0x200
FOF_NOERRORUI = 0x400
COPY_FLAGS = FOF_SILENT | FOF_NOCONFIRMATION | FOF_NOCONFIRMMKDIR | FOF_NOERRORUI


class MtpError(Exception):
    """MTP 操作异常。"""


def _com_init():
    """在当前线程初始化 COM（MTP 访问必需）。幂等。"""
    try:
        import pythoncom
        pythoncom.CoInitialize()
    except Exception:
        # pythoncom 在非 Windows 或未安装 pywin32 时不可用
        pass


def _com_uninit():
    try:
        import pythoncom
        pythoncom.CoUninitialize()
    except Exception:
        pass


def _is_drive_letter_path(path):
    """判断是否为盘符路径，如 'C:\\'。"""
    if not path or len(path) < 2:
        return False
    return path[1] == ":"


def list_portable_devices():
    """枚举「此电脑」下的便携设备（无盘符的文件夹项）。

    返回 [{name, type}]。MTP 设备（手机）的 Path 为空、IsFolder 为 True。
    """
    _com_init()
    try:
        import win32com.client
        shell = win32com.client.Dispatch("Shell.Application")
        this_pc = shell.NameSpace(SSF_DRIVES)
        devices = []
        for item in this_pc.Items():
            try:
                if not item.IsFolder:
                    continue
                path = item.Path or ""
                if _is_drive_letter_path(path):
                    continue  # 跳过普通盘符驱动器
                devices.append({"name": str(item.Name), "type": str(item.Type)})
            except Exception:
                continue
        return devices
    finally:
        _com_uninit()


def probe_device(device_name):
    """探测设备存储是否可访问（用于判断是否已授权 USB 传输）。

    返回 {authorized: bool, storages: [name]}。
    """
    _com_init()
    try:
        import win32com.client
        shell = win32com.client.Dispatch("Shell.Application")
        this_pc = shell.NameSpace(SSF_DRIVES)
        target = None
        for item in this_pc.Items():
            try:
                if item.IsFolder and str(item.Name) == device_name:
                    target = item
                    break
            except Exception:
                continue
        if target is None:
            return {"authorized": False, "storages": [], "error": "设备未找到"}
        try:
            device_folder = target.GetFolder()
        except Exception as e:
            return {"authorized": False, "storages": [], "error": str(e)}
        storages = []
        try:
            for sub in device_folder.Items():
                try:
                    if sub.IsFolder:
                        storages.append(str(sub.Name))
                except Exception:
                    continue
        except Exception as e:
            return {"authorized": False, "storages": [], "error": str(e)}
        return {"authorized": len(storages) > 0, "storages": storages}
    finally:
        _com_uninit()


def _find_item(folder, name):
    """在 folder 中按名称查找 FolderItem（大小写不敏感），未找到返回 None。"""
    target = name.lower()
    try:
        items = folder.Items()
    except Exception:
        return None
    for it in items:
        try:
            if str(it.Name).lower() == target:
                return it
        except Exception:
            continue
    return None


def _get_subitem(folder, name):
    """ParseName 优先，失败回退遍历。"""
    try:
        item = folder.ParseName(name)
        if item is not None:
            return item
    except Exception:
        pass
    return _find_item(folder, name)


def _wait_for_file(path, expected_size, timeout=None):
    """等待文件写入完成：命中预期大小或体积连续 1s 不变。"""
    if timeout is None:
        timeout = config.COPY_TIMEOUT
    deadline = time.time() + timeout
    last_size = -1
    stable_since = None
    while time.time() < deadline:
        if os.path.exists(path):
            try:
                size = os.path.getsize(path)
            except OSError:
                size = -1
            if expected_size is not None and size == expected_size and size >= 0:
                return True
            if size > 0:
                if size == last_size:
                    if stable_since is None:
                        stable_since = time.time()
                    elif time.time() - stable_since >= 1.0:
                        return True
                else:
                    stable_since = None
            last_size = size
        time.sleep(0.3)
    return os.path.exists(path)


def _clear_dir(path):
    if os.path.isdir(path):
        for entry in os.listdir(path):
            full = os.path.join(path, entry)
            try:
                if os.path.isdir(full):
                    shutil.rmtree(full, ignore_errors=True)
                else:
                    os.remove(full)
            except Exception:
                pass


class MtpDevice:
    """单台 MTP 设备的连接封装。

    注意：COM 对象绑定到创建它的线程。本实例应在同一线程内使用
    （流水线后台线程或 Flask 处理线程），并在使用前调用 connect()。
    """

    def __init__(self, device_name):
        self.device_name = device_name
        self._shell = None
        self._device_folder = None
        self._storage_name = None
        self._storage_folder = None
        self._folder_cache = {}

    def connect(self):
        """打开设备并定位内部存储。返回存储名。"""
        _com_init()
        import win32com.client
        self._shell = win32com.client.Dispatch("Shell.Application")
        this_pc = self._shell.NameSpace(SSF_DRIVES)
        target = None
        for item in this_pc.Items():
            try:
                if item.IsFolder and str(item.Name) == self.device_name:
                    target = item
                    break
            except Exception:
                continue
        if target is None:
            raise MtpError(f"未找到设备：{self.device_name}")
        self._device_folder = target.GetFolder()
        storages = self.list_storages()
        if not storages:
            raise MtpError("设备无可访问存储，请在手机端授权 USB 文件传输")
        self._storage_name = storages[0]
        for s in storages:
            low = s.lower()
            if "内部" in s or "internal" in low or "shared" in low:
                self._storage_name = s
                break
        sub = _get_subitem(self._device_folder, self._storage_name)
        if sub is None or not sub.IsFolder:
            raise MtpError(f"无法进入存储：{self._storage_name}")
        self._storage_folder = sub.GetFolder()
        return self._storage_name

    def list_storages(self):
        names = []
        if self._device_folder is None:
            return names
        for sub in self._device_folder.Items():
            try:
                if sub.IsFolder:
                    names.append(str(sub.Name))
            except Exception:
                continue
        return names

    def _get_folder(self, parts):
        """根据相对存储根的文件夹路径段导航到 Folder，带缓存。"""
        key = tuple(parts)
        if key in self._folder_cache:
            return self._folder_cache[key]
        folder = self._storage_folder
        for p in parts:
            sub = _get_subitem(folder, p)
            if sub is None or not sub.IsFolder:
                raise MtpError(f"无法进入文件夹：{p}")
            folder = sub.GetFolder()
        self._folder_cache[key] = folder
        return folder

    def get_file_item(self, rel_parts):
        """rel_parts 为相对存储根的路径段（末段为文件名），返回 FolderItem。"""
        if len(rel_parts) == 1:
            parent = self._storage_folder
        else:
            parent = self._get_folder(rel_parts[:-1])
        item = _get_subitem(parent, rel_parts[-1])
        if item is None:
            raise MtpError(f"设备上未找到文件：{'/'.join(rel_parts)}")
        return item

    def walk_images(self, scan_dirs=None):
        """递归扫描图片/视频文件。

        返回 [{rel, name, size}]，rel 为相对存储根的路径段列表。
        自动跳过隐藏/缓存目录与 .nomedia 等。
        """
        if scan_dirs is None:
            scan_dirs = config.SCAN_DIRS
        results = []
        if self._storage_folder is None:
            raise MtpError("设备未连接")
        for top in scan_dirs:
            top_item = _get_subitem(self._storage_folder, top)
            if top_item is None or not top_item.IsFolder:
                continue
            self._walk(top_item.GetFolder(), [top], results)
        return results

    def _walk(self, folder, prefix, results):
        try:
            items = folder.Items()
        except Exception:
            return
        for it in items:
            try:
                name = str(it.Name)
                is_folder = it.IsFolder
            except Exception:
                continue
            if is_folder:
                if name.lower() in config.SKIP_DIRS or name.startswith("."):
                    continue
                try:
                    self._walk(it.GetFolder(), prefix + [name], results)
                except Exception:
                    continue
            else:
                ext = os.path.splitext(name)[1].lower()
                if ext in config.ALL_EXTS and ext not in config.SKIP_EXTS:
                    size = None
                    try:
                        size = int(it.Size)
                    except Exception:
                        size = None
                    results.append({
                        "rel": prefix + [name],
                        "name": name,
                        "size": size,
                    })

    def copy_file(self, entry, staging_dir):
        """将设备文件复制到本地暂存目录，返回 (本地路径, 预期大小)。"""
        os.makedirs(staging_dir, exist_ok=True)
        src_item = self.get_file_item(entry["rel"])
        orig_name = entry["name"]
        try:
            expected_size = int(src_item.Size)
        except Exception:
            expected_size = entry.get("size")

        target_name = orig_name
        target_path = os.path.join(staging_dir, target_name)
        if os.path.exists(target_path):
            stem, ext = os.path.splitext(orig_name)
            target_name = f"{stem}_{uuid.uuid4().hex[:8]}{ext}"
            target_path = os.path.join(staging_dir, target_name)

        # 临时子目录拷贝，规避 CopyHere 重名交互
        tmp_dir = os.path.join(staging_dir, "_tmp")
        _clear_dir(tmp_dir)
        os.makedirs(tmp_dir, exist_ok=True)
        tmp_folder = self._shell.NameSpace(tmp_dir)
        tmp_folder.CopyHere(src_item, COPY_FLAGS)
        tmp_file = os.path.join(tmp_dir, orig_name)
        if not _wait_for_file(tmp_file, expected_size):
            raise MtpError(f"复制超时：{orig_name}")
        shutil.move(tmp_file, target_path)
        _clear_dir(tmp_dir)
        return target_path, expected_size

    def close(self):
        self._folder_cache.clear()
        self._storage_folder = None
        self._device_folder = None
        self._shell = None
        _com_uninit()

    @property
    def is_local(self):
        return False


class LocalSource:
    """本地目录数据源。

    用于「图片分类」模式：直接对本地已备份目录（如 D:\\photo）进行分类整理。
    支持 copy 与 move 两种操作（move 同卷即时完成，避免重复占用空间）。
    """

    def __init__(self, local_root):
        self.local_root = os.path.abspath(local_root)
        import threading
        self._write_lock = threading.Lock()  # 串行化同名冲突检查+写入，避免并发覆盖

    def connect(self):
        if not os.path.isdir(self.local_root):
            raise MtpError(f"本地目录不存在：{self.local_root}")
        return self.local_root

    @property
    def is_local(self):
        return True

    def walk_images(self, scan_dirs=None):
        if scan_dirs is None:
            scan_dirs = config.SCAN_DIRS
        results = []
        for top in scan_dirs:
            top_path = os.path.join(self.local_root, top)
            if not os.path.isdir(top_path):
                continue
            self._walk_local(top_path, [top], results)
        return results

    def _walk_local(self, root_dir, prefix, results):
        try:
            entries = os.listdir(root_dir)
        except OSError:
            return
        for fn in entries:
            full = os.path.join(root_dir, fn)
            if os.path.isdir(full):
                if fn.lower() in config.SKIP_DIRS or fn.startswith("."):
                    continue
                self._walk_local(full, prefix + [fn], results)
            else:
                ext = os.path.splitext(fn)[1].lower()
                if ext in config.ALL_EXTS and ext not in config.SKIP_EXTS:
                    try:
                        size = os.path.getsize(full)
                    except OSError:
                        size = None
                    results.append({
                        "rel": prefix + [fn],
                        "name": fn,
                        "size": size,
                        "abs": full,
                    })

    def transfer(self, entry, target_root, rel_target, new_name, operation="copy"):
        """本地文件直接归位到最终目录（copy 或 move）。返回 (最终路径, 源大小)。

        加锁串行化「冲突检查 + 写入」，确保并发线程不会因同名（同秒时间戳）互相覆盖。
        """
        src = entry.get("abs") or os.path.join(self.local_root, *entry["rel"])
        dest_dir = os.path.join(target_root, *rel_target)
        os.makedirs(dest_dir, exist_ok=True)
        try:
            src_size = os.path.getsize(src)
        except OSError:
            src_size = None
        with self._write_lock:
            final_path = os.path.join(dest_dir, new_name)
            # 同名冲突 → 重命名
            if os.path.exists(final_path):
                stem, ext = os.path.splitext(new_name)
                long_suffix = ""
                if stem.endswith("_long"):
                    stem = stem[: -len("_long")]
                    long_suffix = "_long"
                idx = 2
                while True:
                    cand = os.path.join(dest_dir, f"{stem}_{idx}{long_suffix}{ext}")
                    if not os.path.exists(cand):
                        final_path = cand
                        break
                    idx += 1
            if operation == "move":
                shutil.move(src, final_path)
            else:
                shutil.copy2(src, final_path)
        return final_path, src_size

    def close(self):
        pass
