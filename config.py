"""全局配置。"""
import os
import sys


def _is_frozen():
    """是否以 PyInstaller 打包的 exe 运行。"""
    return getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS")


# 资源根目录：打包后指向 _MEIPASS，开发时指向项目目录
if _is_frozen():
    BASE_DIR = sys._MEIPASS
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 应用元信息
APP_NAME = "NestPics"
VERSION = "1.0.0"
AUTHOR = "pzwwanOVO"
GITHUB_URL = "https://github.com/pzwwanOVO/photocategory"

# 运行时数据目录（设置文件）放在用户 AppData，避免 exe 同级出现 settings.json
_appdata = os.environ.get("APPDATA") or os.path.expanduser("~")
APP_DATA_DIR = os.path.join(_appdata, "PhotoCategory")
try:
    os.makedirs(APP_DATA_DIR, exist_ok=True)
except Exception:
    APP_DATA_DIR = os.path.dirname(sys.executable) if _is_frozen() else BASE_DIR

# 服务监听
HOST = "127.0.0.1"
PORT = 5000

# 设置文件路径（持久化默认目标目录、操作方式、语言、主题、引导完成标记等）
SETTINGS_FILE = os.path.join(APP_DATA_DIR, "settings.json")

# 设备轮询相关
DEVICE_POLL_INTERVAL = 2  # 前端轮询间隔（秒）

# 扫描：设备/本地目录下重点扫描的目录（相对根）
SCAN_DIRS = ["DCIM", "Pictures", "MIUI"]
# 图片后缀
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".heic", ".webp", ".bmp"}
# 视频后缀（归入「录屏」类别）
VIDEO_EXTS = {".mp4", ".mov", ".3gp"}
# 全部支持的后缀
ALL_EXTS = IMAGE_EXTS | VIDEO_EXTS

# 扫描时跳过的目录名（隐藏目录、系统缓存、回收站）
SKIP_DIRS = {
    ".thumbnails", ".android", ".globaltrash", ".gs", ".gs_fs0", ".gs_fs6",
    ".nomedia", "cache", "thumbnails", ".trash", ".trashes",
}
# 跳过这些后缀的文件（缓存/索引）
SKIP_EXTS = {".nomedia", ".thumbcache_idx_001", ".database_uuid", ".prop", ".0"}

# 截图路径关键字（命中即视为截图）
SCREENSHOT_DIR_KEYWORDS = ("Screenshots", "SCREEN_CAP", "screenshot", "截屏", "截图")

# 逆地理编码坐标系：wgs84(默认GPS) / gcj02(高德/谷歌中国) / bd09(百度)
GEO_SOURCE_CRS = os.environ.get("PHOTOCAT_GEO_CRS", "wgs84")

# 暂存目录名（位于目标目录下）
STAGING_DIR_NAME = "_暂存区"

# 复制单文件超时（秒）
COPY_TIMEOUT = 120
# 复制失败重试次数
COPY_RETRIES = 2

# 分类目标根目录名
PHOTO_ROOT = "照片"
SCREENSHOT_ROOT = "截图"
APP_IMAGE_ROOT = "应用图片"
RECORDING_ROOT = "录屏"
VIDEO_ROOT = "视频"
OTHER_ROOT = "其他图片"

# 无 GPS 时照片归入的地区名
UNKNOWN_REGION = "未知地区"
# 截图无包名时归入的应用名
UNKNOWN_APP = "未识别应用"

# 默认操作方式：copy / move（move 仅本地同卷整理时使用）
DEFAULT_OPERATION = "copy"

# 并发处理线程数（仅本地分类模式生效；MTP 设备因 COM 线程绑定保持单线程）
# 保守起见默认 1 线程；档位参考：1=最低占用 2=平衡 4=较快
DEFAULT_WORKERS = 1
WORKERS_OPTIONS = [1, 2, 4]

# 界面语言：zh / en
DEFAULT_LANG = "zh"
LANG_OPTIONS = ["zh", "en"]

# 主题：light / dark / system（system 跟随系统深浅色）
DEFAULT_THEME = "system"
THEME_OPTIONS = ["light", "dark", "system"]

# 目录来源映射：路径段（小写）→ (类别, 来源名)
# 类别: photo / screenshot / app / recording
DIR_SOURCE_MAP = {
    # 相机
    "camera": ("photo", None),
    # 截图
    "screenshots": ("screenshot", None),
    "screen_cap": ("screenshot", None),
    "screenshot": ("screenshot", None),
    # 录屏
    "screenrecorder": ("recording", None),
    "screen_recorder": ("recording", None),
    "screenrecord": ("recording", None),
    # 应用保存的图片
    "weixin": ("app", "微信"),
    "wechat": ("app", "微信"),
    "qqimage": ("app", "QQ"),
    "qq": ("app", "QQ"),
    "tencent": ("app", "腾讯"),
    "telegram": ("app", "Telegram"),
    "bili": ("app", "哔哩哔哩"),
    "bilibili": ("app", "哔哩哔哩"),
    "douyin": ("app", "抖音"),
    "tiebalite": ("app", "贴吧"),
    "tieba": ("app", "贴吧"),
    "via": ("app", "Via浏览器"),
    "coolmarket": ("app", "酷安"),
    "alipay": ("app", "支付宝"),
    "toonpics": ("app", "Toonpics"),
    "vipaccount": ("app", "会员账户"),
    "kon": ("app", "kon"),
    "weibo": ("app", "微博"),
    "xhs": ("app", "小红书"),
    "xiaohongshu": ("app", "小红书"),
    "zhihu": ("app", "知乎"),
    "taobao": ("app", "淘宝"),
    "pinduoduo": ("app", "拼多多"),
    "jingdong": ("app", "京东"),
    "netease": ("app", "网易云"),
    "cloudmusic": ("app", "网易云音乐"),
    "gallery": ("app", "相册"),
    "dragimgs": ("app", "拖拽图片"),
}

# 文件名前缀 → (类别, 应用名)
# 用于无目录信号时按文件名特征识别应用来源
FILE_PREFIX_APP_MAP = {
    "mmexport": ("app", "微信"),
    "wechat_appreciation_": ("app", "微信"),
    "wxcamera": ("app", "微信"),
    "bili_": ("app", "哔哩哔哩"),
    "douyin_": ("app", "抖音"),
    "xhs_": ("app", "小红书"),
    "wb_": ("app", "微博"),
}
