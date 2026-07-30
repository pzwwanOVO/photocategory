"""小米图片分类管理程序 — Flask 后端入口。

提供设备检测、存储探测、扫描、目录浏览、启动/停止流水线等 HTTP API，
并通过 SocketIO 实时推送进度与统计。

支持两种工作模式：
- 传输备份：从 MTP 设备（小米手机）复制图片并分类
- 图片分类：对本地已备份目录（如 D:\\photo）直接分类整理（copy/move）

打包为单 exe 后，模板/静态资源从 _MEIPASS 加载，设置文件放在 exe 同级。
"""
import os
import sys
import json
import string
import threading
import webbrowser

from flask import Flask, request, jsonify, render_template
from flask_socketio import SocketIO

import config
from core import mtp_device, classifier
from core.pipeline import Pipeline

# 资源目录：打包后从 _MEIPASS 加载，开发时从项目目录加载
TEMPLATE_DIR = os.path.join(config.BASE_DIR, "templates")
STATIC_DIR = os.path.join(config.BASE_DIR, "static")

app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)
app.config["SECRET_KEY"] = "photocategory-local"
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")

# 运行时状态
_state = {
    "source_config": None,   # {"type": "mtp"|"local", "name"/"path"}
    "entries": None,         # 扫描结果
    "target_dir": None,
    "operation": config.DEFAULT_OPERATION,  # copy / move
    "workers": config.DEFAULT_WORKERS,      # 并发线程数（本地分类）
    "running": False,
    "pipeline": None,
    "last_stats": None,
    "last_progress": None,
}
_lock = threading.Lock()


# ---------------- 设置持久化 ----------------
def load_settings():
    """读取 settings.json，失败返回空 dict。"""
    try:
        with open(config.SETTINGS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_settings(data):
    """写入 settings.json（合并已有字段）。"""
    try:
        current = load_settings()
        current.update(data)
        with open(config.SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(current, f, ensure_ascii=False, indent=2)
        return True
    except Exception:
        return False


# 启动时载入默认设置
_initial = load_settings()
if _initial.get("target_dir") and os.path.isdir(_initial["target_dir"]):
    _state["target_dir"] = os.path.abspath(_initial["target_dir"])
if _initial.get("operation") in ("copy", "move"):
    _state["operation"] = _initial["operation"]
if isinstance(_initial.get("workers"), int) and _initial["workers"] in config.WORKERS_OPTIONS:
    _state["workers"] = _initial["workers"]


def _json_error(msg, code=400):
    return jsonify({"ok": False, "error": msg}), code


# ---------------- 页面 ----------------
@app.route("/")
def index():
    return render_template("index.html")


# ---------------- 设置 ----------------
@app.route("/api/settings", methods=["GET"])
def api_settings_get():
    with _lock:
        return jsonify({
            "ok": True,
            "target_dir": _state["target_dir"],
            "operation": _state["operation"],
            "workers": _state["workers"],
            "workers_options": config.WORKERS_OPTIONS,
            "geo_available": _geocoder_available(),
        })


@app.route("/api/settings", methods=["POST"])
def api_settings_set():
    data = request.get_json(force=True) or {}
    changed = {}
    with _lock:
        if "target_dir" in data:
            path = data["target_dir"]
            if path and os.path.isdir(path):
                _state["target_dir"] = os.path.abspath(path)
                changed["target_dir"] = _state["target_dir"]
            elif not path:
                _state["target_dir"] = None
                changed["target_dir"] = None
        if data.get("operation") in ("copy", "move"):
            _state["operation"] = data["operation"]
            changed["operation"] = _state["operation"]
        if isinstance(data.get("workers"), int) and data["workers"] in config.WORKERS_OPTIONS:
            _state["workers"] = data["workers"]
            changed["workers"] = _state["workers"]
    if changed:
        save_settings(changed)
    return jsonify({"ok": True, **changed})


# ---------------- 设备 ----------------
@app.route("/api/devices")
def api_devices():
    try:
        devs = mtp_device.list_portable_devices()
    except Exception as e:
        return _json_error(f"枚举设备失败：{e}", 500)
    return jsonify({"ok": True, "devices": devs})


@app.route("/api/devices/<path:name>/storages")
def api_storages(name):
    try:
        info = mtp_device.probe_device(name)
    except Exception as e:
        return _json_error(f"探测设备失败：{e}", 500)
    return jsonify({"ok": True, **info})


# ---------------- 扫描 ----------------
@app.route("/api/scan", methods=["POST"])
def api_scan():
    data = request.get_json(force=True) or {}
    mode = data.get("mode", "mtp")
    try:
        if mode == "local":
            path = data.get("path")
            if not path or not os.path.isdir(path):
                return _json_error("本地目录无效")
            source = mtp_device.LocalSource(path)
            source.connect()
            entries = source.walk_images()
            source_config = {"type": "local", "path": os.path.abspath(path)}
            source.close()
        else:
            name = data.get("name")
            if not name:
                return _json_error("缺少设备名")
            source = mtp_device.MtpDevice(name)
            storage = source.connect()
            entries = source.walk_images()
            source_config = {"type": "mtp", "name": name, "storage": storage}
            source.close()
    except Exception as e:
        return _json_error(f"扫描失败：{e}")

    # 预览：粗判类型 + 取前若干条
    preview = []
    type_counts = {"photo": 0, "screenshot": 0, "app": 0, "recording": 0, "video": 0, "other": 0}
    for e in entries:
        rough = classifier.detect_type(e["rel"], e["name"], {}, os.path.splitext(e["name"])[1].lower())
        if rough in type_counts:
            type_counts[rough] += 1
        else:
            type_counts["other"] += 1
    for e in entries[:50]:
        rough = classifier.detect_type(e["rel"], e["name"], {}, os.path.splitext(e["name"])[1].lower())
        preview.append({"name": e["name"], "type": rough, "size": e.get("size")})

    with _lock:
        _state["source_config"] = source_config
        _state["entries"] = entries

    return jsonify({
        "ok": True,
        "count": len(entries),
        "preview": preview,
        "type_counts": type_counts,
        "source": source_config,
    })


# ---------------- 目录浏览 ----------------
@app.route("/api/browse")
def api_browse():
    path = request.args.get("path", "").strip()
    if not path:
        # 列出盘符
        drives = []
        for letter in string.ascii_uppercase:
            d = f"{letter}:\\"
            if os.path.exists(d):
                drives.append({"name": f"{letter}:", "path": d})
        return jsonify({"ok": True, "current": "", "items": drives})
    if not os.path.isdir(path):
        return _json_error("路径不存在")
    items = []
    try:
        for entry in os.listdir(path):
            full = os.path.join(path, entry)
            if os.path.isdir(full):
                items.append({"name": entry, "path": full})
    except Exception as e:
        return _json_error(f"读取目录失败：{e}")
    items.sort(key=lambda x: x["name"].lower())
    return jsonify({"ok": True, "current": path, "items": items})


@app.route("/api/target", methods=["POST"])
def api_target():
    data = request.get_json(force=True) or {}
    path = data.get("path")
    if not path or not os.path.isdir(path):
        return _json_error("目标目录无效")
    with _lock:
        _state["target_dir"] = os.path.abspath(path)
    save_settings({"target_dir": _state["target_dir"]})
    return jsonify({"ok": True, "target": _state["target_dir"]})


# ---------------- 流水线 ----------------
@app.route("/api/start", methods=["POST"])
def api_start():
    data = request.get_json(silent=True) or {}
    operation = data.get("operation") or _state["operation"]
    if operation not in ("copy", "move"):
        operation = config.DEFAULT_OPERATION
    with _lock:
        if _state["running"]:
            return _json_error("已有任务在运行")
        if not _state["entries"]:
            return _json_error("请先扫描图片")
        if not _state["target_dir"]:
            return _json_error("请先选择目标目录")
        source_config = _state["source_config"]
        entries = _state["entries"]
        target_dir = _state["target_dir"]
        _state["operation"] = operation
        _state["running"] = True
        _state["last_stats"] = None

    # move 仅对本地同卷整理有意义；MTP 强制 copy
    if source_config["type"] != "local":
        operation = "copy"
    workers = _state["workers"]

    thread = threading.Thread(
        target=_run_pipeline, args=(source_config, entries, target_dir, operation, workers), daemon=True
    )
    thread.start()
    return jsonify({"ok": True, "count": len(entries), "target": target_dir, "operation": operation, "workers": workers})


def _make_source(source_config):
    if source_config["type"] == "local":
        s = mtp_device.LocalSource(source_config["path"])
    else:
        s = mtp_device.MtpDevice(source_config["name"])
    s.connect()
    return s


def _run_pipeline(source_config, entries, target_dir, operation, workers):
    source = None
    pipeline = None
    try:
        source = _make_source(source_config)
        callbacks = {
            "progress": _on_progress,
            "complete": lambda s: socketio.emit("complete", _sanitize_stats(s)),
            "log": lambda p: socketio.emit("log", p),
        }
        pipeline = Pipeline(source, target_root=target_dir, callbacks=callbacks,
                            operation=operation, workers=workers)
        with _lock:
            _state["pipeline"] = pipeline
        stats = pipeline.run(entries)
        with _lock:
            _state["last_stats"] = stats
    except Exception as e:
        socketio.emit("error", {"message": f"流水线异常：{e}"})
    finally:
        if source:
            try:
                source.close()
            except Exception:
                pass
        with _lock:
            _state["running"] = False
            _state["pipeline"] = None


def _on_progress(payload):
    socketio.emit("progress", payload)
    with _lock:
        _state["last_progress"] = payload


@app.route("/api/stop", methods=["POST"])
def api_stop():
    with _lock:
        pipeline = _state["pipeline"]
    if pipeline:
        pipeline.stop()
        return jsonify({"ok": True, "msg": "已请求停止"})
    return _json_error("无运行中的任务")


@app.route("/api/status")
def api_status():
    with _lock:
        return jsonify({
            "ok": True,
            "running": _state["running"],
            "scanned": len(_state["entries"]) if _state["entries"] else 0,
            "target_dir": _state["target_dir"],
            "operation": _state["operation"],
            "workers": _state["workers"],
            "source": _state["source_config"],
            "geo_available": _geocoder_available(),
        })


def _geocoder_available():
    try:
        from core import geocoder
        return geocoder.available()
    except Exception:
        return False


@app.route("/api/stats")
def api_stats():
    with _lock:
        stats = _state["last_stats"]
    if not stats:
        return jsonify({"ok": False})
    return jsonify({"ok": True, "stats": _sanitize_stats(stats)})


@app.route("/api/progress")
def api_progress():
    """轮询用：返回运行状态、最近一次进度与已完成统计。"""
    with _lock:
        return jsonify({
            "ok": True,
            "running": _state["running"],
            "progress": _state["last_progress"],
            "stats": _sanitize_stats(_state["last_stats"]) if _state["last_stats"] else None,
        })


def _sanitize_stats(stats):
    """让 stats 可 JSON 序列化。"""
    if not stats:
        return None
    s = dict(stats)
    s["by_region"] = dict(s.get("by_region", {}))
    s["by_app"] = dict(s.get("by_app", {}))
    s["by_category"] = dict(s.get("by_category", {}))
    s["failures"] = list(s.get("failures", []))
    return s


def _start_server():
    """在后台线程启动 Flask-SocketIO 服务。"""
    socketio.run(
        app, host=config.HOST, port=config.PORT,
        debug=False, allow_unsafe_werkzeug=True,
    )


class WindowApi:
    """暴露给前端 JS 的窗口控制接口（无边框窗口的自定义标题栏按钮调用）。"""

    def __init__(self):
        self._window = None

    def bind(self, window):
        self._window = window

    def minimize(self):
        if self._window:
            self._window.minimize()

    def maximize(self):
        if self._window:
            self._window.maximize()

    def restore(self):
        if self._window:
            self._window.restore()

    def close(self):
        if self._window:
            self._window.destroy()


def _open_native_window():
    """用 pywebview 打开无边框原生应用窗口（非浏览器）。

    Win11 下使用 Edge WebView2 渲染；frameless 去除系统标题栏，
    由应用内自定义标题栏（含拖拽区与最小化/最大化/关闭按钮）接管。
    窗口关闭后主进程退出。
    """
    try:
        import webview
    except Exception as e:
        # 回退：打开系统浏览器
        print(f"pywebview 不可用（{e}），回退到浏览器")
        webbrowser.open(f"http://{config.HOST}:{config.PORT}")
        socketio.run(app, host=config.HOST, port=config.PORT,
                     debug=False, allow_unsafe_werkzeug=True)
        return

    server_thread = threading.Thread(target=_start_server, daemon=True)
    server_thread.start()

    # 等待服务就绪
    import time
    import urllib.request
    url = f"http://{config.HOST}:{config.PORT}/api/status"
    for _ in range(50):
        try:
            urllib.request.urlopen(url, timeout=0.5)
            break
        except Exception:
            time.sleep(0.1)

    api = WindowApi()
    win = webview.create_window(
        title="小米图片分类整理",
        url=f"http://{config.HOST}:{config.PORT}/",
        js_api=api,
        width=1180,
        height=760,
        min_size=(960, 600),
        frameless=True,      # 去除系统标题栏
        easy_drag=False,     # 仅 .pywebview-drag-region 区域可拖拽
        text_select=False,
    )
    api.bind(win)
    webview.start()
    # 窗口关闭 → 退出进程
    os._exit(0)


if __name__ == "__main__":
    print(f"启动服务：http://{config.HOST}:{config.PORT}")
    _open_native_window()
