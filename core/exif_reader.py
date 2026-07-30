"""图片 EXIF 元数据提取。

优先用 exifread 健壮解析 GPS 与时间，用 Pillow 获取尺寸与回退 EXIF。
对无 EXIF 的图片（如 PNG 截图）返回空字段，不抛异常。
"""
import os
from datetime import datetime


def _ratio_to_float(ratio):
    try:
        den = float(ratio.den)
        return float(ratio.num) / den if den else 0.0
    except Exception:
        try:
            return float(ratio)
        except Exception:
            return 0.0


def _dms_to_decimal(values, ref):
    """values: [度, 分, 秒] 的 IFDRatio 列表；ref: N/S/E/W。"""
    if not values or len(values) < 3:
        return None
    try:
        deg = _ratio_to_float(values[0])
        minute = _ratio_to_float(values[1])
        sec = _ratio_to_float(values[2])
        dec = deg + minute / 60.0 + sec / 3600.0
        if ref and str(ref).strip().upper() in ("S", "W"):
            dec = -dec
        return dec
    except Exception:
        return None


def _parse_exif_time(value):
    if not value:
        return None
    s = str(value).strip()
    for fmt in ("%Y:%m:%d %H:%M:%S", "%Y-%m-%d %H:%M:%S", "%Y:%m:%d %H:%M"):
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            continue
    # 仅含日期
    try:
        return datetime.strptime(s, "%Y:%m:%d")
    except ValueError:
        return None


def _read_with_exifread(path):
    """仅对 JPEG/TIFF 调用 exifread，避免对 PNG 等输出告警噪音。"""
    try:
        with open(path, "rb") as f:
            head = f.read(4)
        is_jpeg = head[:2] == b"\xff\xd8"
        is_tiff = head[:2] in (b"II", b"MM")
        if not (is_jpeg or is_tiff):
            return {}
        import exifread
        with open(path, "rb") as f:
            return exifread.process_file(f, details=False)
    except Exception:
        return {}


def _read_with_pillow(path):
    """返回 (width, height, exif_dict)。"""
    try:
        from PIL import Image
        with Image.open(path) as img:
            w, h = img.size
            exif = {}
            try:
                raw = img._getexif()
                if raw:
                    from PIL.ExifTags import TAGS
                    for k, v in raw.items():
                        name = TAGS.get(k, str(k))
                        exif[name] = v
            except Exception:
                pass
            return w, h, exif
    except Exception:
        return None, None, {}


def _pillow_gps(exif):
    try:
        gps = exif.get("GPSInfo")
        if not gps:
            return None, None
        from PIL.ExifTags import GPSTAGS
        g = {GPSTAGS.get(k, k): v for k, v in gps.items()}
        def conv(v):
            try:
                d, m, s = v
                return float(d) + float(m) / 60 + float(s) / 3600
            except Exception:
                return None
        lat = conv(g.get("GPSLatitude"))
        lng = conv(g.get("GPSLongitude"))
        if g.get("GPSLatitudeRef") == "S" and lat is not None:
            lat = -lat
        if g.get("GPSLongitudeRef") == "W" and lng is not None:
            lng = -lng
        return lat, lng
    except Exception:
        return None, None


def read(path):
    """提取图片元数据。

    返回 dict：
      datetime_original: datetime 或 None
      gps: {lat, lng} 或 None
      make, model: str 或 None
      width, height: int 或 None
    """
    result = {
        "datetime_original": None,
        "gps": None,
        "make": None,
        "model": None,
        "width": None,
        "height": None,
    }

    tags = _read_with_exifread(path)

    # 时间
    for key in ("EXIF DateTimeOriginal", "EXIF DateTimeDigitized", "Image DateTime"):
        if key in tags:
            dt = _parse_exif_time(tags[key].values)
            if dt:
                result["datetime_original"] = dt
                break

    # GPS
    lat = lng = None
    if "GPS GPSLatitude" in tags and "GPS GPSLongitude" in tags:
        lat = _dms_to_decimal(
            tags["GPS GPSLatitude"].values,
            tags["GPS GPSLatitudeRef"].values if "GPS GPSLatitudeRef" in tags else "N",
        )
        lng = _dms_to_decimal(
            tags["GPS GPSLongitude"].values,
            tags["GPS GPSLongitudeRef"].values if "GPS GPSLongitudeRef" in tags else "E",
        )
    if lat is not None and lng is not None:
        result["gps"] = {"lat": lat, "lng": lng}

    # 设备型号
    for key in ("Image Make",):
        if key in tags:
            result["make"] = str(tags[key].values).strip()
    for key in ("Image Model",):
        if key in tags:
            result["model"] = str(tags[key].values).strip()

    # 尺寸 + Pillow 回退 EXIF
    w, h, pexif = _read_with_pillow(path)
    result["width"] = w
    result["height"] = h
    if result["gps"] is None:
        plat, plng = _pillow_gps(pexif)
        if plat is not None and plng is not None:
            result["gps"] = {"lat": plat, "lng": plng}
    if result["datetime_original"] is None:
        dt = _parse_exif_time(pexif.get("DateTimeOriginal"))
        if dt:
            result["datetime_original"] = dt
    if result["make"] is None and "Make" in pexif:
        result["make"] = str(pexif["Make"]).strip()
    if result["model"] is None and "Model" in pexif:
        result["model"] = str(pexif["Model"]).strip()

    # 最终回退：文件修改时间
    if result["datetime_original"] is None:
        try:
            mtime = os.path.getmtime(path)
            result["datetime_original"] = datetime.fromtimestamp(mtime)
        except OSError:
            pass

    return result
