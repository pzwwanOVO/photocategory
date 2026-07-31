"""分类决策模块（进化版）。

核心改进：
- 以「目录来源」作为首要分类信号（适配手机备份的真实结构：WeiXin/QQ/bili/Screenshots 等）
- 四大类别：照片 / 截图 / 应用图片 / 录屏(视频)
- 文件名时间戳解析增强：支持 Unix 毫秒/秒时间戳（mmexport...、Image_...、纯数字）
- 保留包名解析作为截图应用来源的补充判据
"""
import os
import re
from datetime import datetime, timezone, timedelta

import config
from core import app_names

# 包名正则：com/cn/org/net 开头，至少三段
PACKAGE_RE = re.compile(
    r"(?:^|[^a-z0-9])((?:com|cn|org|net)\.[a-z0-9_]+(?:\.[a-z0-9_]+)+)",
    re.IGNORECASE,
)

# 截图文件名前缀
SCREENSHOT_PREFIXES = (
    "screenshot", "longscreenshot", "截屏", "截图", "屏幕截图", "screen",
)

# 截图目录关键字
SCREENSHOT_DIR_KEYWORDS = tuple(k.lower() for k in config.SCREENSHOT_DIR_KEYWORDS)

LONG_KEYWORDS = ("long", "_long", "长截图", "长截屏")

# 文件名时间戳正则（按优先级）
_TS_PATTERNS = [
    # 2024-01-15-10-30-45 或 2024_01_15_10_30_45
    re.compile(r"(\d{4})[-_](\d{2})[-_](\d{2})[-_](\d{2})[-_](\d{2})[-_](\d{2})"),
    # 20240115_103045
    re.compile(r"(\d{4})(\d{2})(\d{2})[-_](\d{2})(\d{2})(\d{2})"),
    # 20241128171425（14 位紧凑 YYYYMMDDHHMMSS）
    re.compile(r"(?<!\d)(\d{4})(\d{2})(\d{2})(\d{2})(\d{2})(\d{2})(?!\d)"),
    # 2024-01-15（仅日期）
    re.compile(r"(\d{4})[-_](\d{2})[-_](\d{2})"),
]

# Unix 时间戳数字串（10~16 位）
_UNIX_RUN_RE = re.compile(r"(?<!\d)(\d{10,16})(?!\d)")

CN_TZ = timezone(timedelta(hours=8))


def detect_source(rel_parts):
    """根据路径段判断来源类别。

    返回 (category, source_name) 或 (None, None)。
    category: photo / screenshot / app / recording
    """
    for seg in rel_parts:
        low = seg.lower()
        if low in config.DIR_SOURCE_MAP:
            return config.DIR_SOURCE_MAP[low]
    # 关键字兜底：截图目录
    joined = "/".join(rel_parts).lower()
    if any(k in joined for k in SCREENSHOT_DIR_KEYWORDS):
        return ("screenshot", None)
    return (None, None)


def detect_prefix_app(name):
    """根据文件名前缀识别应用来源。

    返回 (category, app_name) 或 (None, None)。
    用于无目录信号时按文件名特征（mmexport...、bili_... 等）识别。
    """
    low = name.lower()
    for prefix, (cat, app) in config.FILE_PREFIX_APP_MAP.items():
        if low.startswith(prefix):
            return (cat, app)
    return (None, None)


def _is_screenshot_dir(rel_parts):
    joined = "/".join(rel_parts[:-1]).lower() if len(rel_parts) > 1 else ""
    return any(kw in joined for kw in SCREENSHOT_DIR_KEYWORDS)


def extract_package(name):
    """从文件名提取包名，未找到返回 None。先去掉扩展名再匹配。"""
    stem = os.path.splitext(name)[0]
    m = PACKAGE_RE.search(stem)
    if m:
        return m.group(1).lower()
    return None


def extract_time_from_name(name):
    """从文件名解析时间戳，失败返回 None。

    支持：YYYY-MM-DD-HH-MM-SS、YYYYMMDD_HHMMSS、YYYY-MM-DD、Unix 毫秒/秒。
    """
    stem, _ = os.path.splitext(name)
    # 1. 结构化时间戳
    for pat in _TS_PATTERNS:
        m = pat.search(stem)
        if m:
            groups = m.groups()
            try:
                if len(groups) >= 6:
                    return datetime(
                        int(groups[0]), int(groups[1]), int(groups[2]),
                        int(groups[3]), int(groups[4]), int(groups[5]),
                    )
                elif len(groups) >= 3:
                    return datetime(int(groups[0]), int(groups[1]), int(groups[2]))
            except ValueError:
                continue
    # 2. Unix 时间戳：数字串中取前 13 位（毫秒）或前 10 位（秒）
    for m in _UNIX_RUN_RE.finditer(stem):
        digits = m.group(1)
        if len(digits) >= 13:
            try:
                return datetime.fromtimestamp(int(digits[:13]) / 1000.0, tz=CN_TZ).replace(tzinfo=None)
            except (ValueError, OSError):
                pass
        if len(digits) >= 10:
            ts = int(digits[:10])
            if 1000000000 <= ts <= 2147483647:
                try:
                    return datetime.fromtimestamp(ts, tz=CN_TZ).replace(tzinfo=None)
                except (ValueError, OSError):
                    pass
    return None


def detect_type(rel_parts, name, exif, ext):
    """判定文件类别：photo / screenshot / app / recording / other。"""
    is_video = ext in config.VIDEO_EXTS
    # 优先：目录来源
    cat, _src = detect_source(rel_parts)
    if cat:
        if is_video and cat != "recording":
            # 来自相机/应用的视频 → 归为视频
            return "video"
        return cat
    # 视频兜底
    if is_video:
        return "video"
    # 文件名前缀 → 应用图片（mmexport...、bili_... 等）
    pcat, _papp = detect_prefix_app(name)
    if pcat:
        return pcat
    # 文件名启发式
    low = name.lower()
    if _is_screenshot_dir(rel_parts) or any(low.startswith(p) for p in SCREENSHOT_PREFIXES):
        return "screenshot"
    if extract_package(name):
        return "screenshot"
    if exif.get("make") or exif.get("model") or exif.get("gps"):
        return "photo"
    if low.startswith(("img_", "img-", "dsc", "image_")):
        return "photo"
    # 无任何来源信号 → 归入「其他图片」，避免污染照片库
    return "other"


def _is_long(name):
    low = name.lower()
    return any(k in low for k in LONG_KEYWORDS)


def build_region(geo):
    """地理编码结果 → 地区字符串（省-市）。"""
    if not geo or not geo.get("ok"):
        return config.UNKNOWN_REGION
    province = geo.get("province", "").strip()
    city = geo.get("city", "").strip()
    if not province:
        return config.UNKNOWN_REGION
    if city and city != province:
        return f"{province}-{city}"
    return province


def build_new_name(dt, ext, is_long=False):
    """统一命名：YYYYMMDD_HHMMSS.ext（长截图保留 _long）。"""
    if not isinstance(dt, datetime):
        dt = datetime.now()
    base = dt.strftime("%Y%m%d_%H%M%S")
    if is_long:
        base = base + "_long"
    if not ext:
        ext = ""
    elif not ext.startswith("."):
        ext = "." + ext
    return f"{base}{ext}"


def classify(entry, exif, geo=None):
    """对单个文件做分类决策。

    返回 dict：type, region, app, source, datetime, new_name, rel_target, is_long
    """
    rel_parts = entry["rel"]
    name = entry["name"]
    ext = os.path.splitext(name)[1].lower()
    fn_dt = extract_time_from_name(name)
    exif_dt = exif.get("datetime_original")
    _cat, src = detect_source(rel_parts)
    file_type = detect_type(rel_parts, name, exif, ext)

    if file_type == "photo":
        dt = exif_dt or fn_dt or datetime.now()
        region = build_region(geo)
        new_name = build_new_name(dt, ext)
        year = dt.strftime("%Y年")
        month = dt.strftime("%Y-%m月")
        rel_target = [config.PHOTO_ROOT, region, year, month]
        return _result("photo", dt, new_name, rel_target, region=region)

    if file_type == "screenshot":
        dt = fn_dt or exif_dt or datetime.now()
        package = extract_package(name)
        is_long = _is_long(name)
        new_name = build_new_name(dt, ext, is_long=is_long)
        year = dt.strftime("%Y年")
        month = dt.strftime("%Y-%m月")
        if package:
            app_name = app_names.lookup(package)
            rel_target = [config.SCREENSHOT_ROOT, app_name, year, month]
            return _result("screenshot", dt, new_name, rel_target, app=app_name, package=package)
        rel_target = [config.SCREENSHOT_ROOT, year, month]
        return _result("screenshot", dt, new_name, rel_target)

    if file_type == "app":
        dt = fn_dt or exif_dt or datetime.now()
        # 目录来源名优先，其次文件名前缀识别的应用名
        _pcat, papp = detect_prefix_app(name)
        app_name = src or papp or config.UNKNOWN_APP
        new_name = build_new_name(dt, ext)
        year = dt.strftime("%Y年")
        month = dt.strftime("%Y-%m月")
        rel_target = [config.APP_IMAGE_ROOT, app_name, year, month]
        return _result("app", dt, new_name, rel_target, app=app_name, source=src)

    if file_type == "other":
        dt = fn_dt or exif_dt or datetime.now()
        new_name = build_new_name(dt, ext)
        year = dt.strftime("%Y年")
        month = dt.strftime("%Y-%m月")
        rel_target = [config.OTHER_ROOT, year, month]
        return _result("other", dt, new_name, rel_target)

    # video / recording
    dt = fn_dt or exif_dt or datetime.now()
    new_name = build_new_name(dt, ext)
    year = dt.strftime("%Y年")
    month = dt.strftime("%Y-%m月")
    root = config.RECORDING_ROOT if file_type == "recording" else config.VIDEO_ROOT
    rel_target = [root, year, month]
    return _result(file_type, dt, new_name, rel_target)


def _result(file_type, dt, new_name, rel_target, region=None, app=None, package=None, source=None):
    return {
        "type": file_type,
        "region": region,
        "app": app,
        "package": package,
        "source": source,
        "datetime": dt,
        "new_name": new_name,
        "rel_target": rel_target,
        "is_long": new_name.endswith("_long" + os.path.splitext(new_name)[1]),
    }
