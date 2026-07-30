"""Android 包名 → 应用中文名 映射表。

小米截图文件名形如 Screenshot_2024-01-15-10-30-45-123_com.tencent.mm.jpg，
末尾的 com.tencent.mm 即截图时所在应用的包名。
"""


APP_NAMES = {
    # 社交 / 通讯
    "com.tencent.mm": "微信",
    "com.tencent.mobileqq": "QQ",
    "com.tencent.tim": "TIM",
    "com.sina.weibo": "微博",
    "com.smile.gifmaker": "快手",
    "com.ss.android.ugc.aweme": "抖音",
    "com.ss.android.ugc.aweme.lite": "抖音极速版",
    "com.tencent.qqlive": "腾讯视频",
    "com.tencent.tvideo": "腾讯视频",
    "com.netease.cloudmusic": "网易云音乐",
    "com.netease.mail": "网易邮箱",
    # 资讯
    "com.ss.android.article.news": "今日头条",
    "com.ss.android.article.lite": "今日头条极速版",
    "com.dragon.read": "番茄小说",
    "com.zhihu.android": "知乎",
    # 电商
    "com.taobao.taobao": "淘宝",
    "com.taobao.idlefish": "闲鱼",
    "com.eg.android.AlipayGphone": "支付宝",
    "com.xunmeng.pinduoduo": "拼多多",
    "com.jingdong.app.mall": "京东",
    "com.tencent.wqq": "微信",
    "com.taobao.livedeta": "淘宝直播",
    "com.tmall.wireless": "天猫",
    # 视频 / 二次元
    "tv.danmaku.bili": "哔哩哔哩",
    "tv.danmaku.bilibilihd": "哔哩哔哩",
    "com.hunantv.imgo.activity": "芒果TV",
    "com.qiyi.video": "爱奇艺",
    "com.youku.phone": "优酷",
    "com.ss.android.article.video": "西瓜视频",
    # 工具 / 系统
    "com.miui.home": "桌面",
    "com.miui.securitycenter": "手机管家",
    "com.miui.calculator": "计算器",
    "com.android.browser": "浏览器",
    "com.android.chrome": "Chrome浏览器",
    "com.mi.globalbrowser": "浏览器",
    "com.miui.gallery": "相册",
    "com.android.camera": "相机",
    "com.android.camera2": "相机",
    "com.android.settings": "设置",
    "com.miui.personalassistant": "智能助理",
    "com.android.mms": "短信",
    "com.android.contacts": "联系人",
    "com.android.dialer": "电话",
    "com.android.deskclock": "时钟",
    "com.android.documentsui": "文件管理",
    "com.mi.android.globalFileexplorer": "文件管理",
    # 地图 / 出行
    "com.autonavi.minimap": "高德地图",
    "com.baidu.BaiduMap": "百度地图",
    "com.sdu.didi.psnger": "滴滴出行",
    # 生活 / 笔记
    "com.xingin.xhs": "小红书",
    "com.xingin.outside": "小红书",
    "com.wuba": "58同城",
    "com.meituan": "美团",
    "com.sankuai.meituan": "美团",
    "com.dianping.v1": "大众点评",
    "com.evermemo": "备忘录",
    "com.miui.notes": "便签",
    "com.youdao.note": "有道云笔记",
    # 办公
    "com.tencent.wework": "企业微信",
    "com.alibaba.android.rimet": "钉钉",
    "com.feixin.work": "和飞书",
    "com.ss.android.lark": "飞书",
    # 浏览器 / 搜索
    "com.baidu.searchbox": "百度",
    "com.miui.yellowpage": "生活黄页",
}


def lookup(package):
    """包名 → 应用名。未命中返回包名末段，便于人工识别。"""
    if not package:
        return None
    key = package.lower().strip()
    if key in APP_NAMES:
        return APP_NAMES[key]
    parts = [p for p in key.split(".") if p]
    return parts[-1] if parts else package
