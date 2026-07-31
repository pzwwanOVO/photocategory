"""手机品牌 → 图片存放目录识别。

根据 MTP 设备名推断品牌（小米/三星/华为…），返回该品牌常见的图片/截图
存放目录（相对存储根的路径）。前端调用 /api/mtp/suggest_dirs 时，后端会
逐个检查这些候选目录在设备上是否存在，仅返回存在的目录供用户勾选。

注意：MTP 扫描是递归的，因此这里给出的是「入口目录」（如 DCIM/Camera），
其下的所有图片都会被扫描到。候选目录宁可多列，由存在性检查过滤。
"""

# 品牌识别关键字（按优先级排序；先匹配的优先）
# (关键字列表[小写匹配], 品牌 key)。中文关键字原样匹配。
_BRAND_RULES = [
    (["redmi"], "redmi"),
    (["xiaomi", "小米"], "xiaomi"),
    (["samsung", "galaxy", "sm-"], "samsung"),
    (["honor", "荣耀"], "honor"),
    (["huawei", "华为"], "huawei"),
    (["iqoo"], "iqoo"),
    (["vivo"], "vivo"),
    (["oneplus", "一加"], "oneplus"),
    (["oppo"], "oppo"),
    (["realme"], "realme"),
    (["pixel"], "pixel"),
    (["iphone", "apple", "苹果"], "iphone"),
    (["meizu", "魅族"], "meizu"),
    (["letv", "乐视"], "letv"),
    (["nubia", "努比亚"], "nubia"),
    (["motorola", "moto"], "motorola"),
]

# 通用顶级图片目录（所有品牌都会检查）
# 这是 Android 标准目录，在「传输图片」模式下几乎必然存在
COMMON_DIRS = ["DCIM", "Pictures"]

# 品牌 → 额外候选图片子目录（相对存储根）
# 供用户精确选择某个子目录扫描；顶级 DCIM/Pictures 已由 COMMON_DIRS 覆盖
BRAND_DIRS = {
    "xiaomi":   ["DCIM/Camera", "DCIM/Screenshot", "DCIM/MultiCapture", "Pictures/Screenshots", "MIUI/Gallery"],
    "redmi":    ["DCIM/Camera", "DCIM/Screenshot", "DCIM/MultiCapture", "Pictures/Screenshots", "MIUI/Gallery"],
    "samsung":  ["DCIM/Camera", "DCIM/Screenshots", "DCIM/Video", "Pictures/Screenshots", "Pictures/Instagram"],
    "huawei":   ["DCIM/Camera", "DCIM/Screenshots", "Pictures/Screenshots", "Pictures/WeiXin", "Pictures/qq_images"],
    "honor":    ["DCIM/Camera", "DCIM/Screenshots", "Pictures/Screenshots", "Pictures/WeiXin"],
    "oppo":     ["DCIM/Camera", "DCIM/Screenshots", "Pictures/Screenshots"],
    "vivo":     ["DCIM/Camera", "DCIM/Screenshots", "Pictures/Screenshots"],
    "iqoo":     ["DCIM/Camera", "DCIM/Screenshots", "Pictures/Screenshots"],
    "oneplus":  ["DCIM/Camera", "DCIM/Screenshots", "Pictures/Screenshots"],
    "realme":   ["DCIM/Camera", "DCIM/Screenshots", "Pictures/Screenshots"],
    "pixel":    ["DCIM/Camera", "DCIM/Screenshots", "Pictures/Screenshots"],
    "meizu":    ["DCIM/Camera", "DCIM/Screenshot", "Pictures/Screenshots"],
    "letv":     ["DCIM/Camera", "DCIM/Screenshot", "Pictures/Screenshots"],
    "nubia":    ["DCIM/Camera", "DCIM/Screenshots", "Pictures/Screenshots"],
    "motorola": ["DCIM/Camera", "DCIM/Screenshots", "Pictures/Screenshots"],
    "iphone":   ["DCIM"],
}

# 未识别品牌时的通用候选（同 COMMON_DIRS）
DEFAULT_DIRS = list(COMMON_DIRS)

# 品牌展示名（中英）
BRAND_LABELS = {
    "xiaomi":   "小米 Xiaomi",
    "redmi":    "Redmi",
    "samsung":  "三星 Samsung",
    "huawei":   "华为 Huawei",
    "honor":    "荣耀 Honor",
    "oppo":     "OPPO",
    "vivo":     "vivo",
    "iqoo":     "iQOO",
    "oneplus":  "一加 OnePlus",
    "realme":   "realme",
    "pixel":    "Google Pixel",
    "meizu":    "魅族 Meizu",
    "letv":     "乐视 Letv",
    "nubia":    "努比亚 nubia",
    "motorola": "摩托罗拉 Motorola",
    "iphone":   "Apple iPhone",
}


def detect_brand(device_name):
    """从设备名推断品牌（小写 key），未识别返回 None。

    设备名例：'Redmi K70E' → 'redmi'；'SM-G998B' → 'samsung'。
    """
    if not device_name:
        return None
    low = device_name.lower()
    for keywords, key in _BRAND_RULES:
        for kw in keywords:
            # 中文关键字直接子串匹配；英文关键字用小写子串匹配
            if kw in device_name or kw in low:
                return key
    return None


def candidate_dirs(device_name):
    """返回该设备推荐的图片目录列表（相对存储根，未做存在性检查）。

    通用顶级目录（DCIM, Pictures）排在最前，后接品牌特有子目录。
    前端自动勾选时会优先选顶级目录，跳过已被父目录覆盖的子目录。
    """
    brand = detect_brand(device_name)
    dirs = list(COMMON_DIRS)
    if brand and brand in BRAND_DIRS:
        for d in BRAND_DIRS[brand]:
            if d not in dirs:
                dirs.append(d)
    return dirs


def brand_label(brand):
    """返回品牌的展示名，未知则返回 None。"""
    if not brand:
        return None
    return BRAND_LABELS.get(brand)
