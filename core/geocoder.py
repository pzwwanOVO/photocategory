"""离线逆地理编码封装（fast-geocn）。

经纬度 → 省/市/区。fast-geocn 支持 WGS-84/GCJ-02/BD-09 坐标系转换，
无需 API Key、完全离线。
"""
import config

_geocoder = None
_init_error = None

try:
    from fast_geocn import regeo as _regeo
    _geocoder = _regeo
except Exception as e:  # pragma: no cover - 依赖缺失时降级
    _init_error = e


def available():
    return _geocoder is not None


def reverse(lat, lng):
    """返回 {province, city, district, ok}。失败或无 GPS 数据时归入未知地区。"""
    if _geocoder is None:
        return {
            "province": config.UNKNOWN_REGION,
            "city": "",
            "district": "",
            "ok": False,
            "error": str(_init_error) if _init_error else "未安装",
        }
    try:
        r = _geocode_call(lat, lng)
        addr = r.get("address", {}) if isinstance(r, dict) else {}
        province = (addr.get("province") or "").strip()
        city = (addr.get("city") or "").strip()
        district = (addr.get("district") or "").strip()
        if not province:
            province = config.UNKNOWN_REGION
        return {"province": province, "city": city, "district": district, "ok": True}
    except Exception as e:
        return {
            "province": config.UNKNOWN_REGION,
            "city": "",
            "district": "",
            "ok": False,
            "error": str(e),
        }


def _geocode_call(lat, lng):
    return _geocoder(lng, lat, source_crs=config.GEO_SOURCE_CRS)
