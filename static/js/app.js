// NestPics — 前端逻辑（Win11 风格）
const $ = (id) => document.getElementById(id);

// ---------------- 多语言 ----------------
const I18N = {
  zh: {
    app_name: "NestPics",
    nav_features: "功能",
    mode_transfer: "传输备份", mode_transfer_desc: "从手机导入",
    mode_classify: "图片分类", mode_classify_desc: "整理本地目录",
    target_location: "整理位置", not_selected: "未选择", change_dir: "更改目录",
    settings: "设置",
    mode_transfer_desc_long: "USB 连接手机 → 选择传输图片 → 选择目录 → 备份到本地",
    mode_classify_desc_long: "选择本地备份目录 → 自动分类整理（可复制或移动）",
    trf_select_mode: "连接后请在手机上选择「传输文件 / 传输图片」模式",
    trf_connect_phone: "请用 USB 连接手机",
    detecting_device: "正在检测设备…",
    no_device: "未检测到便携设备，请连接手机…",
    poll_stopped: "已停止自动检测，点「重新检测」重试",
    auth_stopped: "未授权，请在手机端选择「传输文件」后点「我已授权，继续」",
    detect_error: "检测异常：{e}",
    re_detect: "重新检测",
    device_detected: "已检测到设备：",
    trf_authorize: "请在手机上授权并选择「传输文件」模式",
    storage: "存储：{s}", access_fail: "无法访问：{e}",
    not_authorized: "未授权，请在手机端选择「传输文件」",
    probe_fail: "探测失败：{e}",
    authorized_continue: "我已授权，继续", back: "返回",
    scan_result: "扫描结果", images_to_organize: "张图片待整理",
    images_to_backup: "张图片待备份",
    rescan: "重新扫描", start_organize: "开始整理",
    start_backup: "开始备份",
    target_dir: "目标目录", source_dir: "来源目录",
    op_copy_keep: "操作方式：复制（保留原文件）",
    device_folder: "设备目录", source_folder: "图片所在目录",
    browse_device: "浏览设备", select_this_folder: "选择此目录",
    select_checked: "选择选中目录",
    recog_dirs: "识别图片目录", re_recognize: "重新识别",
    select_and_scan: "选择并扫描",
    no_dirs_detected: "未识别到图片目录，请手动浏览",
    n_dirs_detected: "识别到 {n} 个图片目录",
    mtp_browse_hint: "勾选要备份的目录（可多选），或进入目录后点「选择此目录」",
    backup_target: "备份位置",
    backup_keep_original: "复制图片到此目录，保留原文件与目录结构",
    continue_classify: "继续分类",
    backup_done: "备份完成",
    backup_running: "正在备份",
    preview_50: "预览（前 50 张）",
    cls_select_dir: "选择要整理的本地目录",
    cls_select_hint: "选择手机图片备份目录（含 DCIM / Pictures 等子目录）",
    select_dir: "选择目录", confirm_dir: "选择此目录",
    operation: "操作方式", copy: "复制", move: "移动",
    move_warn: "移动将从源目录移除文件，请确认已备份。",
    performance: "处理性能",
    organizing: "正在整理", stop: "停止",
    photo: "照片", screenshot: "截图", app_image: "应用图片",
    video: "视频", fail: "失败", other: "其他",
    organize_done: "整理完成",
    photo_by_region: "照片 · 按地区", app_by_app: "应用图片/截图 · 按应用",
    fail_list: "失败列表", organize_again: "再整理一次",
    close: "关闭", win_min: "最小化", win_max: "最大化", win_close: "关闭",
    manual_input: "或手动输入完整路径",
    language: "界面语言", language_desc: "切换中英文界面",
    appearance: "外观", appearance_desc: "浅色 / 深色 / 跟随系统",
    theme_light: "浅色", theme_dark: "深色", theme_system: "跟随系统",
    default_target: "默认整理位置", default_target_desc: "分类后图片归档的根目录",
    change: "更改",
    default_operation: "默认操作方式", default_operation_desc: "本地分类时复制或移动源文件",
    performance_desc: "并发线程数，越高越快但占用更大",
    geocoding: "地理编码", geocoding_desc: "离线逆地理编码（省市区识别）",
    about: "关于", about_short: "NestPics · 本地运行 · 数据不离设备",
    view_details: "查看详情",
    about_desc: "把手机备份的图片按规则分类整理的本地小工具，数据不离设备。",
    author_label: "作者",
    ob_welcome: "欢迎使用 NestPics",
    ob_desc: "把手机备份的图片按地区、时间和应用来源自动分类整理。先选择你习惯的语言。",
    ob_start: "开始使用",
    available: "可用", not_installed: "未安装", detecting: "检测中",
    pick_a_dir: "请选择一个目录",
    scan_fail: "扫描失败：{e}", scan_error: "扫描异常：{e}",
    threads: "{n} 线程", single_thread: "单线程",
    staging: "暂存区：{dir}（失败文件保留于此）",
    workers_hint_1: "1 线程 · 最低占用（推荐后台整理）",
    workers_hint_2: "2 线程 · 平衡速度与占用",
    workers_hint_4: "4 线程 · 较快，磁盘/CPU 占用较高",
    this_pc: "此电脑", up_dir: "..",
    none: "无",
  },
  en: {
    app_name: "NestPics",
    nav_features: "Features",
    mode_transfer: "Transfer & Backup", mode_transfer_desc: "Import from phone",
    mode_classify: "Classify", mode_classify_desc: "Organize local folder",
    target_location: "Target location", not_selected: "Not selected", change_dir: "Change folder",
    settings: "Settings",
    mode_transfer_desc_long: "Connect phone via USB → select image transfer → pick folder → backup locally",
    mode_classify_desc_long: "Pick a backup folder → auto-organize (copy or move)",
    trf_connect_phone: "Please connect your phone via USB",
    trf_select_mode: 'Then select "Transfer files / Image transfer" mode on your phone',
    detecting_device: "Detecting device…",
    no_device: "No device detected, connect your phone…",
    poll_stopped: "Auto-detect stopped. Tap \"Re-detect\" to retry",
    auth_stopped: "Not authorized. Select \"Transfer files\" on your phone, then tap \"Authorized, continue\"",
    detect_error: "Detect error: {e}",
    re_detect: "Re-detect",
    device_detected: "Device detected: ",
    trf_authorize: 'Please authorize and select "Transfer files" on your phone',
    storage: "Storage: {s}", access_fail: "Access failed: {e}",
    not_authorized: 'Not authorized, select "Transfer files" on your phone',
    probe_fail: "Probe failed: {e}",
    authorized_continue: "Authorized, continue", back: "Back",
    scan_result: "Scan result", images_to_organize: "images to organize",
    images_to_backup: "images to backup",
    rescan: "Rescan", start_organize: "Start",
    start_backup: "Start backup",
    target_dir: "Target folder", source_dir: "Source folder",
    op_copy_keep: "Mode: copy (keep originals)",
    device_folder: "Device folder", source_folder: "Image folder",
    browse_device: "Browse device", select_this_folder: "Select this folder",
    select_checked: "Select checked",
    recog_dirs: "Detect image folders", re_recognize: "Re-detect",
    select_and_scan: "Select & scan",
    no_dirs_detected: "No image folders detected, browse manually",
    n_dirs_detected: "{n} image folders detected",
    mtp_browse_hint: "Check folders to backup (multi-select), or enter a folder and tap \"Select this folder\"",
    backup_target: "Backup location",
    backup_keep_original: "Copy images here, keeping originals and folder structure",
    continue_classify: "Continue to classify",
    backup_done: "Backup done",
    backup_running: "Backing up",
    preview_50: "Preview (first 50)",
    cls_select_dir: "Choose a local folder to organize",
    cls_select_hint: "Select your phone backup folder (with DCIM / Pictures, etc.)",
    select_dir: "Select folder", confirm_dir: "Select this folder",
    operation: "Mode", copy: "Copy", move: "Move",
    move_warn: "Move removes files from the source. Make sure you have a backup.",
    performance: "Performance",
    organizing: "Organizing", stop: "Stop",
    photo: "Photos", screenshot: "Screenshots", app_image: "App images",
    video: "Videos", fail: "Failed", other: "Other",
    organize_done: "Done",
    photo_by_region: "Photos · by region", app_by_app: "App/Screenshots · by app",
    fail_list: "Failures", organize_again: "Organize again",
    close: "Close", win_min: "Minimize", win_max: "Maximize", win_close: "Close",
    manual_input: "Or enter full path manually",
    language: "Language", language_desc: "Switch between Chinese and English",
    appearance: "Appearance", appearance_desc: "Light / Dark / Follow system",
    theme_light: "Light", theme_dark: "Dark", theme_system: "System",
    default_target: "Default target", default_target_desc: "Root folder for organized images",
    change: "Change",
    default_operation: "Default mode", default_operation_desc: "Copy or move when organizing locally",
    performance_desc: "More threads = faster but heavier",
    geocoding: "Geocoding", geocoding_desc: "Offline reverse geocoding",
    about: "About", about_short: "NestPics · Local · Data stays on device",
    view_details: "Details",
    about_desc: "A local tool that organizes phone backup photos by rules. Data never leaves your device.",
    author_label: "Author",
    ob_welcome: "Welcome to NestPics",
    ob_desc: "Auto-organize phone backup photos by location, time and app source. Pick your language first.",
    ob_start: "Get started",
    available: "Available", not_installed: "Not installed", detecting: "Detecting",
    pick_a_dir: "Please select a folder",
    scan_fail: "Scan failed: {e}", scan_error: "Scan error: {e}",
    threads: "{n} threads", single_thread: "single thread",
    staging: "Staging: {dir} (failed files kept here)",
    workers_hint_1: "1 thread · lowest usage (recommended)",
    workers_hint_2: "2 threads · balanced",
    workers_hint_4: "4 threads · faster, heavier on disk/CPU",
    this_pc: "This PC", up_dir: "..",
    none: "None",
  },
};

function typeLabel(k) {
  return t({ photo: "photo", screenshot: "screenshot", app: "app_image",
    recording: "video", video: "video", other: "other" }[k] || "other");
}

function t(key, vars) {
  const dict = I18N[state.lang] || I18N.zh;
  let s = dict[key] || I18N.zh[key] || key;
  if (vars) for (const k in vars) s = s.split("{" + k + "}").join(vars[k]);
  return s;
}

function applyI18n() {
  document.querySelectorAll("[data-i18n]").forEach((el) => {
    el.textContent = t(el.getAttribute("data-i18n"));
  });
  document.querySelectorAll("[data-i18n-title]").forEach((el) => {
    el.title = t(el.getAttribute("data-i18n-title"));
  });
  document.querySelectorAll("[data-i18n-ph]").forEach((el) => {
    el.placeholder = t(el.getAttribute("data-i18n-ph"));
  });
  document.documentElement.lang = state.lang === "en" ? "en" : "zh-CN";
  document.title = t("app_name");
  // 刷新依赖语言的动态文本
  refreshModeText();
  refreshWorkersHint();
  if (state.typeCounts && (state.scanned)) reRenderTypeBreak();
  if (state.previewItems) reRenderPreview();
  refreshTargetUI();
  refreshTrfDevicePath();
}

let state = {
  mode: "transfer",
  device: null, storage: null, source: null,
  scanPaths: [], recogDirs: [], recogBrand: null,
  scanned: false, scanCount: 0, typeCounts: {}, previewItems: null,
  target: null, operation: "copy", workers: 1,
  lang: "zh", theme: "system", onboarded: false,
  appName: "NestPics", version: "1.0.0",
  running: false, backupMode: false, pollTimer: null, devTimer: null,
};

// ---------------- 本地持久化（供首屏即时读取主题/语言） ----------------
function persistLocal() {
  try {
    localStorage.setItem("pc_settings", JSON.stringify({
      lang: state.lang, theme: state.theme,
    }));
  } catch (e) {}
}

// ---------------- 主题 ----------------
function applyTheme(theme) {
  state.theme = theme;
  const dark = theme === "dark" ||
    (theme === "system" && window.matchMedia("(prefers-color-scheme: dark)").matches);
  document.documentElement.setAttribute("data-theme", dark ? "dark" : "light");
}
window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change", () => {
  if (state.theme === "system") applyTheme("system");
});

async function setTheme(theme) {
  applyTheme(theme);
  persistLocal();
  await api("/api/settings", { method: "POST", body: JSON.stringify({ theme }) });
}

async function setLang(lang) {
  state.lang = lang;
  applyI18n();
  persistLocal();
  refreshLangSeg();
  await api("/api/settings", { method: "POST", body: JSON.stringify({ lang }) });
}

function refreshLangSeg() {
  document.querySelectorAll("#setLangSeg .seg-btn").forEach((b) => {
    b.classList.toggle("active", b.dataset.lang === state.lang);
  });
}
function refreshThemeSeg() {
  document.querySelectorAll("#setThemeSeg .seg-btn").forEach((b) => {
    b.classList.toggle("active", b.dataset.theme === state.theme);
  });
}

// ---------- 视图切换 ----------
const TRF_VIEWS = ["trf-waiting", "trf-detected", "trf-ready"];
const CLS_VIEWS = ["cls-select", "cls-ready"];
const SHARED_VIEWS = ["view-running", "view-done"];

function showTrfView(name) {
  TRF_VIEWS.forEach((v) => { const el = $(v); if (el) el.classList.toggle("active", v === name); });
  SHARED_VIEWS.forEach((v) => $(v).classList.remove("active"));
}
function showClsView(name) {
  CLS_VIEWS.forEach((v) => { const el = $(v); if (el) el.classList.toggle("active", v === name); });
  SHARED_VIEWS.forEach((v) => $(v).classList.remove("active"));
}
function showSharedView(name) {
  TRF_VIEWS.forEach((v) => $(v).classList.remove("active"));
  CLS_VIEWS.forEach((v) => $(v).classList.remove("active"));
  SHARED_VIEWS.forEach((v) => $(v).classList.toggle("active", v === name));
}

function refreshModeText() {
  if (state.mode === "transfer") {
    $("modeTitle").textContent = t("mode_transfer");
    $("modeDesc").textContent = t("mode_transfer_desc_long");
  } else {
    $("modeTitle").textContent = t("mode_classify");
    $("modeDesc").textContent = t("mode_classify_desc_long");
  }
}

function switchMode(mode) {
  state.mode = mode;
  document.querySelectorAll(".nav-item").forEach((b) => {
    b.classList.toggle("active", b.dataset.mode === mode);
  });
  $("transfer-views").style.display = mode === "transfer" ? "" : "none";
  $("classify-views").style.display = mode === "classify" ? "" : "none";
  refreshModeText();
  if (mode === "transfer") {
    if (state.running) showSharedView("view-running");
    else if (state.device && state.storage) enterTrfReady();
    else showTrfView(state.device ? "trf-detected" : "trf-waiting");
  } else {
    if (state.running) showSharedView("view-running");
    else if (state.scanned && state.source && state.source.type === "local") showClsView("cls-ready");
    else showClsView("cls-select");
  }
}

// ---------- API ----------
async function api(path, opts = {}) {
  const res = await fetch(path, { headers: { "Content-Type": "application/json" }, ...opts });
  return res.json();
}

// ---------- 初始化 ----------
async function init() {
  const st = await api("/api/status");
  if (st.target_dir) state.target = st.target_dir;
  if (st.operation) state.operation = st.operation;
  if (st.workers) state.workers = st.workers;
  if (st.lang) state.lang = st.lang;
  if (st.theme) state.theme = st.theme;
  if (typeof st.onboarded === "boolean") state.onboarded = st.onboarded;
  if (st.app_name) state.appName = st.app_name;
  if (st.version) state.version = st.version;
  applyTheme(state.theme);
  persistLocal();
  applyI18n();
  if (!state.onboarded) { showOnboarding(); return; }
  finishInit();
}

function finishInit() {
  refreshTargetUI();
  refreshOpSeg();
  refreshWorkersSeg();
  switchMode("transfer");
  startDevicePoll();
}

// ---------- 首次开启引导 ----------
let obLang = "zh";
function showOnboarding() {
  obLang = state.lang || "zh";
  document.querySelectorAll(".ob-lang-btn").forEach((b) => {
    b.classList.toggle("active", b.dataset.lang === obLang);
  });
  $("onboarding").style.display = "grid";
}
document.querySelectorAll(".ob-lang-btn").forEach((b) => {
  b.onclick = () => {
    obLang = b.dataset.lang;
    document.querySelectorAll(".ob-lang-btn").forEach((x) => x.classList.toggle("active", x === b));
    // 实时切换引导语言
    state.lang = obLang;
    applyI18n();
    persistLocal();
  };
});
$("obStart").onclick = async () => {
  state.lang = obLang;
  state.onboarded = true;
  applyI18n();
  persistLocal();
  await api("/api/settings", { method: "POST", body: JSON.stringify({ lang: obLang, onboarded: true }) });
  $("onboarding").style.display = "none";
  finishInit();
};

// ---------- 地理编码状态 ----------
function setGeoBadge(ok) {
  const badge = $("setGeoStatus");
  if (!badge) return;
  badge.className = "badge";
  if (ok === true) { badge.classList.add("ok"); badge.textContent = t("available"); }
  else if (ok === false) { badge.classList.add("warn"); badge.textContent = t("not_installed"); }
  else { badge.textContent = t("detecting"); }
}

// ---------- 整理位置 ----------
function refreshTargetUI() {
  const path = state.target || t("not_selected");
  $("targetPath").textContent = path;
  $("targetPath").title = state.target || "";
  $("trfTarget").textContent = path;
  $("clsTarget").textContent = path;
  $("setTargetPath").textContent = path;
  updateStartBtns();
}

function refreshOpSeg() {
  document.querySelectorAll("#opSeg .seg-btn, #setOpSeg .seg-btn").forEach((b) => {
    b.classList.toggle("active", b.dataset.op === state.operation);
  });
  const ow = $("opWarn");
  if (ow) ow.style.display = state.operation === "move" ? "" : "none";
}

function refreshWorkersHint() {
  const hint = $("workersHint");
  if (hint) hint.textContent = t("workers_hint_" + state.workers) || "";
}
function refreshWorkersSeg() {
  document.querySelectorAll("#workersSeg .seg-btn, #setWorkersSeg .seg-btn").forEach((b) => {
    b.classList.toggle("active", parseInt(b.dataset.w, 10) === state.workers);
  });
  refreshWorkersHint();
}

function updateStartBtns() {
  const hasScanPaths = state.scanPaths && state.scanPaths.length > 0;
  const trfReady = state.scanned && state.target && state.source && state.source.type === "mtp" && hasScanPaths;
  $("btnTrfStart").disabled = !trfReady;
  $("btnTrfScan").disabled = !hasScanPaths;
  $("btnClsStart").disabled = !(state.scanned && state.target && state.source && state.source.type === "local");
}

// ---------- 设备轮询 ----------
const POLL_TIMEOUT_MS = 60000;        // 设备检测总时限：60s 后停止自动轮询
const STORAGE_POLL_MAX = 15;          // 存储探测最大次数（≈30s）
let pollStartTime = 0;
let storagePollCount = 0;

function startDevicePoll() {
  stopDevicePoll();
  if (state.mode !== "transfer") return;
  if (state.device && state.storage) { enterTrfReady(); return; }
  showTrfView("trf-waiting");
  $("pollHint").textContent = t("detecting_device");
  pollStartTime = Date.now();
  state.devTimer = setInterval(pollDevices, 2000);
  pollDevices();
}
function stopDevicePoll() {
  if (state.devTimer) { clearInterval(state.devTimer); state.devTimer = null; }
}

async function pollDevices() {
  // 超时：长时间未检测到设备则停止自动轮询，等待用户手动「重新检测」
  if (Date.now() - pollStartTime > POLL_TIMEOUT_MS) {
    stopDevicePoll();
    $("pollHint").textContent = t("poll_stopped");
    return;
  }
  try {
    const r = await api("/api/devices");
    if (r.ok && r.devices && r.devices.length > 0) {
      stopDevicePoll();
      state.device = r.devices[0].name;
      $("deviceName").textContent = state.device;
      showTrfView("trf-detected");
      pollStorages();
    } else {
      $("pollHint").textContent = t("no_device");
    }
  } catch (e) {
    $("pollHint").textContent = t("detect_error", { e: e.message });
  }
}

async function pollStorages() {
  storagePollCount = 0;
  return await _pollStorageOnce();
}
async function _pollStorageOnce() {
  try {
    const r = await api("/api/devices/" + encodeURIComponent(state.device) + "/storages");
    if (r.ok && r.authorized) {
      state.storage = r.storages && r.storages[0];
      $("storageInfo").textContent = t("storage", { s: state.storage || "—" });
      enterTrfReady();
      return true;
    }
    $("storageInfo").textContent = r.error
      ? t("access_fail", { e: r.error })
      : t("not_authorized");
  } catch (e) {
    $("storageInfo").textContent = t("probe_fail", { e: e.message });
  }
  // 超过限定次数仍未授权，停止自动轮询；用户可在手机端授权后点「我已授权，继续」
  storagePollCount += 1;
  if (storagePollCount >= STORAGE_POLL_MAX) {
    $("storageInfo").textContent = t("auth_stopped");
    return false;
  }
  if (!state.running && $("trf-detected").classList.contains("active")) {
    setTimeout(_pollStorageOnce, 2000);
  }
  return false;
}

function enterTrfReady() {
  showTrfView("trf-ready");
  // 进入传输就绪视图：刷新路径并自动按机型识别图片目录
  refreshTrfDevicePath();
  updateStartBtns();
  loadSuggestedDirs();
}

// ---------- 设备目录浏览（MTP，多选） ----------
let mtpState = { current: "", checked: new Set() };
async function openMtpModal() {
  if (!state.device) return;
  mtpState = { current: "", checked: new Set() };
  updateMtpCheckedCount();
  $("mtpModal").style.display = "grid";
  await loadMtpDir("");
}
async function loadMtpDir(path) {
  mtpState.current = path;
  $("mtpCrumbs").textContent = path ? path : (state.device || t("this_pc"));
  const list = $("mtpList");
  list.innerHTML = '<li class="muted">…</li>';
  try {
    const r = await api("/api/mtp/browse?device=" + encodeURIComponent(state.device) +
      "&path=" + encodeURIComponent(path));
    if (!r.ok) { list.innerHTML = ""; alert(r.error); return; }
    list.innerHTML = "";
    if (path) {
      const up = document.createElement("li");
      up.innerHTML = FOLDER_SVG + " " + t("up_dir");
      up.onclick = () => {
        const parent = path.replace(/\/[^/]*\/?$/, "") || "";
        loadMtpDir(parent);
      };
      list.appendChild(up);
    }
    (r.items || []).forEach((it) => {
      const li = document.createElement("li");
      const ck = mtpState.checked.has(it.path) ? "checked" : "";
      li.innerHTML = `<input type="checkbox" class="row-check" ${ck}> ${FOLDER_SVG} <span>${it.name}</span>`;
      const cb = li.querySelector("input");
      cb.onclick = (e) => {
        e.stopPropagation();
        if (e.target.checked) mtpState.checked.add(it.path);
        else mtpState.checked.delete(it.path);
        updateMtpCheckedCount();
      };
      // 点击行内任意位置（复选框除外）进入子目录
      li.onclick = () => loadMtpDir(it.path);
      list.appendChild(li);
    });
    if (!(r.items || []).length && !path) {
      list.innerHTML = '<li class="muted">' + t("no_device") + "</li>";
    }
  } catch (e) {
    list.innerHTML = "";
    alert(t("detect_error", { e: e.message }));
  }
}
function updateMtpCheckedCount() {
  const el = $("mtpCheckedCount");
  if (el) el.textContent = mtpState.checked.size ? `(${mtpState.checked.size})` : "";
}
function setMtpScanPaths(paths) {
  $("mtpModal").style.display = "none";
  state.scanPaths = paths;
  state.scanned = false;
  refreshTrfDevicePath();
  updateStartBtns();
  doScan({ mode: "mtp", name: state.device, scan_paths: paths });
}
function confirmMtpDir() {
  const paths = Array.from(mtpState.checked);
  if (!paths.length) { alert(t("pick_a_dir")); return; }
  setMtpScanPaths(paths);
}
function selectCurrentMtpDir() {
  const path = mtpState.current;
  if (!path) { alert(t("pick_a_dir")); return; }
  setMtpScanPaths([path]);
}
function refreshTrfDevicePath() {
  const el = $("trfDevicePath");
  if (!el) return;
  const arr = state.scanPaths || [];
  el.textContent = arr.length ? arr.join("  ·  ") : t("not_selected");
  el.title = arr.join("\n");
}

// ---------- 识别图片目录（按机型） ----------
/** 智能选择目录：优先选浅层目录，跳过已被选中父目录覆盖的子目录。
 *  如 DCIM 已选 → 不自动勾选 DCIM/Camera，避免 MTP 重复遍历。 */
function smartSelectDirs(dirs) {
  const sorted = dirs.slice().sort((a, b) => a.split("/").length - b.split("/").length);
  const selected = [];
  for (const d of sorted) {
    const isChild = selected.some(s => d.startsWith(s + "/"));
    if (!isChild) selected.push(d);
  }
  return selected;
}
async function loadSuggestedDirs() {
  const list = $("recogList");
  const brandEl = $("recogBrand");
  const scanBtn = $("btnRecogScan");
  if (!state.device) return;
  if (list) list.innerHTML = `<li class="muted">${t("detecting")}</li>`;
  if (brandEl) brandEl.textContent = t("detecting");
  if (scanBtn) scanBtn.disabled = true;
  try {
    const r = await api("/api/mtp/suggest_dirs?device=" + encodeURIComponent(state.device));
    if (!r.ok) {
      if (list) list.innerHTML = `<li class="muted">${t("no_dirs_detected")}</li>`;
      if (brandEl) brandEl.textContent = "—";
      return;
    }
    state.recogBrand = r.brand_label || r.brand || "—";
    state.recogDirs = r.dirs || [];
    if (brandEl) brandEl.textContent = state.recogBrand;
    if (!state.recogDirs.length) {
      if (list) list.innerHTML = `<li class="muted">${t("no_dirs_detected")}</li>`;
      if (scanBtn) scanBtn.disabled = true;
      return;
    }
    // 自动选择识别到的目录（预勾选），同步到 scanPaths
    // 智能去重：优先选顶级目录，跳过已被父目录覆盖的子目录
    // （如 DCIM 已选则不再自动勾选 DCIM/Camera，避免重复扫描）
    state.scanPaths = smartSelectDirs(state.recogDirs);
    renderRecogList();
    refreshTrfDevicePath();
    if (scanBtn) scanBtn.disabled = false;
    updateStartBtns();
  } catch (e) {
    if (list) list.innerHTML = `<li class="muted">${t("no_dirs_detected")}</li>`;
    if (brandEl) brandEl.textContent = "—";
  }
}
function renderRecogList() {
  const list = $("recogList");
  if (!list) return;
  list.innerHTML = "";
  state.recogDirs.forEach((d) => {
    const li = document.createElement("li");
    const ck = state.scanPaths.includes(d) ? "checked" : "";
    li.innerHTML = `<label><input type="checkbox" class="row-check" ${ck}> ${FOLDER_SVG} <span>${d}</span></label>`;
    const cb = li.querySelector("input");
    cb.onchange = () => {
      if (cb.checked) {
        if (!state.scanPaths.includes(d)) state.scanPaths.push(d);
      } else {
        state.scanPaths = state.scanPaths.filter((x) => x !== d);
      }
      refreshTrfDevicePath();
      updateStartBtns();
      const sb = $("btnRecogScan");
      if (sb) sb.disabled = state.scanPaths.length === 0;
    };
    list.appendChild(li);
  });
}
function confirmRecogScan() {
  if (!state.scanPaths.length) return;
  state.scanned = false;
  doScan({ mode: "mtp", name: state.device, scan_paths: state.scanPaths });
}

// ---------- 扫描 ----------
async function doScan(body) {
  const isLocal = body.mode === "local";
  const countEl = isLocal ? $("clsScanCount") : $("trfScanCount");
  const breakEl = isLocal ? $("clsTypeBreak") : $("trfTypeBreak");
  const prevEl = isLocal ? $("clsPreview") : $("trfPreview");
  const listEl = isLocal ? $("clsPreviewList") : $("trfPreviewList");
  countEl.textContent = "…";
  prevEl.style.display = "none";
  breakEl.innerHTML = "";
  try {
    const r = await api("/api/scan", { method: "POST", body: JSON.stringify(body) });
    if (!r.ok) { alert(t("scan_fail", { e: r.error })); countEl.textContent = "—"; return; }
    state.source = r.source;
    state.scanned = true;
    state.scanCount = r.count;
    state.typeCounts = r.type_counts || {};
    state.previewItems = r.preview || [];
    // 同步 MTP 扫描路径（多目录）
    if (!isLocal && r.source && Array.isArray(r.source.scan_paths)) {
      state.scanPaths = r.source.scan_paths.slice();
      refreshTrfDevicePath();
    }
    countEl.textContent = r.count;
    renderTypeBreak(breakEl, state.typeCounts);
    if (isLocal) $("clsSource").textContent = r.source.path;
    renderPreviewList(listEl, state.previewItems);
    prevEl.style.display = state.previewItems.length ? "block" : "none";
    updateStartBtns();
  } catch (e) {
    alert(t("scan_error", { e: e.message }));
    countEl.textContent = "—";
  }
}

function renderTypeBreak(el, counts) {
  el.innerHTML = "";
  Object.entries(counts).forEach(([k, v]) => {
    if (!v) return;
    const chip = document.createElement("span");
    chip.className = "type-chip";
    chip.innerHTML = `${typeLabel(k)} <b>${v}</b>`;
    el.appendChild(chip);
  });
}
function reRenderTypeBreak() {
  renderTypeBreak($("trfTypeBreak"), state.typeCounts || {});
  renderTypeBreak($("clsTypeBreak"), state.typeCounts || {});
}

function renderPreviewList(listEl, items) {
  listEl.innerHTML = "";
  items.forEach((p) => {
    const li = document.createElement("li");
    const tag = (p.type === "recording") ? "video" : p.type;
    li.innerHTML = `<span class="name">${p.name}</span><span class="tag ${tag}">${typeLabel(p.type)}</span>`;
    listEl.appendChild(li);
  });
}
function reRenderPreview() {
  if (!state.previewItems) return;
  if (state.source && state.source.type === "local") renderPreviewList($("clsPreviewList"), state.previewItems);
  else renderPreviewList($("trfPreviewList"), state.previewItems);
}

// ---------- 目录选择 ----------
let dirState = { current: "", purpose: "target" };

async function openDirModal(purpose) {
  dirState = { current: "", purpose };
  $("dirModalTitle").textContent = purpose === "source" ? t("source_dir") : t("target_dir");
  $("dirModal").style.display = "grid";
  $("dirManual").value = "";
  await loadDir("");
}

const FOLDER_SVG = '<svg viewBox="0 0 24 24" width="16" height="16"><path fill="currentColor" d="M10 4H4a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V8a2 2 0 0 0-2-2h-8l-2-2z"/></svg>';

async function loadDir(path) {
  dirState.current = path;
  const r = await api("/api/browse?path=" + encodeURIComponent(path));
  if (!r.ok) { alert(r.error); return; }
  $("dirCrumbs").textContent = path ? path : t("this_pc");
  const list = $("dirList");
  list.innerHTML = "";
  if (path) {
    const up = document.createElement("li");
    up.innerHTML = FOLDER_SVG + " " + t("up_dir");
    up.onclick = () => {
      const parent = path.replace(/\\[^\\]*\\?$/, "") || "";
      loadDir(parent);
    };
    list.appendChild(up);
  }
  (r.items || []).forEach((it) => {
    const li = document.createElement("li");
    li.innerHTML = FOLDER_SVG + " " + it.name;
    li.onclick = () => loadDir(it.path);
    list.appendChild(li);
  });
}

function confirmDir() {
  let path = dirState.current;
  const manual = $("dirManual").value.trim();
  if (manual) path = manual;
  if (!path) { alert(t("pick_a_dir")); return; }
  $("dirModal").style.display = "none";
  if (dirState.purpose === "target") {
    setTarget(path);
  } else if (dirState.purpose === "source") {
    state.scanned = false;
    state.source = null;
    showClsView("cls-ready");
    doScan({ mode: "local", path });
  }
}

async function setTarget(path) {
  const r = await api("/api/target", { method: "POST", body: JSON.stringify({ path }) });
  if (!r.ok) { alert(r.error); return; }
  state.target = r.target;
  refreshTargetUI();
}

// ---------- 启动整理 ----------
async function startRun(operation) {
  if (!state.scanned || !state.target) return;
  // 传输备份模式：仅备份，不分类
  const isMtp = state.source && state.source.type === "mtp";
  const body = { operation: operation || state.operation };
  if (isMtp) body.backup_only = true;
  const r2 = await api("/api/start", { method: "POST", body: JSON.stringify(body) });
  if (!r2.ok) { alert(r2.error); return; }
  state.running = true;
  state.backupMode = !!r2.backup_only;
  const wTag = $("runningWorkers");
  if (wTag) {
    wTag.textContent = state.source && state.source.type === "local"
      ? t("threads", { n: r2.workers || state.workers })
      : t("single_thread");
  }
  // 备份模式标题不同
  const runTitle = document.querySelector("#view-running .card-head h3");
  if (runTitle) runTitle.textContent = state.backupMode ? t("backup_running") : t("organizing");
  showSharedView("view-running");
  startProgressPoll();
}

function startProgressPoll() {
  stopProgressPoll();
  state.pollTimer = setInterval(fetchProgress, 500);
  fetchProgress();
}
function stopProgressPoll() {
  if (state.pollTimer) { clearInterval(state.pollTimer); state.pollTimer = null; }
}

async function fetchProgress() {
  try {
    const r = await api("/api/progress");
    if (r.progress) {
      const p = r.progress;
      $("progressBar").style.width = (p.percent || 0) + "%";
      $("progressPercent").textContent = (p.percent || 0) + "%";
      $("progressCount").textContent = `${p.index} / ${p.total}`;
      $("currentFile").textContent = p.current || "—";
      $("cntPhoto").textContent = p.photos || 0;
      $("cntShot").textContent = p.screenshots || 0;
      $("cntApp").textContent = p.apps || 0;
      $("cntVideo").textContent = p.videos || 0;
      $("cntFail").textContent = p.failures || 0;
    }
    if (!r.running && r.stats) {
      stopProgressPoll();
      state.running = false;
      showDone(r.stats);
    }
  } catch (e) {
    // 忽略瞬时网络错误
  }
}

// ---------- 完成 ----------
function showDone(stats) {
  showSharedView("view-done");
  const doneTitle = document.querySelector("#view-done .card-head h3");
  if (doneTitle) doneTitle.textContent = state.backupMode ? t("backup_done") : t("organize_done");
  const cat = stats.by_category || {};
  $("finalPhoto").textContent = cat.photo || 0;
  $("finalShot").textContent = cat.screenshot || 0;
  $("finalApp").textContent = cat.app || 0;
  $("finalVideo").textContent = (cat.video || 0) + (cat.recording || 0);
  $("finalOther").textContent = cat.other || 0;
  $("finalFail").textContent = (stats.failures || []).length;
  renderKV($("regionList"), stats.by_region || {});
  renderKV($("appList"), stats.by_app || {});
  $("stagingInfo").textContent = stats.staging_dir
    ? t("staging", { dir: stats.staging_dir })
    : "";
  const fails = stats.failures || [];
  if (fails.length) {
    $("failDetails").style.display = "block";
    $("failCount").textContent = fails.length;
    const fl = $("failList");
    fl.innerHTML = "";
    fails.forEach((f) => {
      const li = document.createElement("li");
      li.innerHTML = `<span>${f.name}</span><b>${f.error}</b>`;
      fl.appendChild(li);
    });
  } else {
    $("failDetails").style.display = "none";
  }
  // 备份模式：显示「继续分类」按钮
  const goCls = $("btnGoClassify");
  if (goCls) goCls.style.display = state.backupMode && state.target ? "" : "none";
}

function renderKV(ul, obj) {
  ul.innerHTML = "";
  const entries = Object.entries(obj).sort((a, b) => b[1] - a[1]);
  if (!entries.length) {
    const li = document.createElement("li");
    li.innerHTML = `<span class="muted">${t("none")}</span>`;
    ul.appendChild(li);
    return;
  }
  entries.forEach(([k, v]) => {
    const li = document.createElement("li");
    li.innerHTML = `<span>${k}</span><b>${v}</b>`;
    ul.appendChild(li);
  });
}

function restart() {
  state.scanned = false;
  state.source = null;
  state.running = false;
  state.backupMode = false;
  if (state.mode === "transfer") {
    // 保留 scanPaths，回到就绪视图方便重新扫描或重新备份
    if (state.scanPaths && state.scanPaths.length) {
      enterTrfReady();
    } else {
      startDevicePoll();
    }
  } else {
    showClsView("cls-select");
  }
}

// 备份完成 → 跳转到图片分类，源目录设为备份位置
function goClassify() {
  state.mode = "classify";
  state.scanned = false;
  state.source = null;
  state.running = false;
  state.backupMode = false;
  // 备份目录作为分类源
  const backupDir = state.target;
  document.querySelectorAll(".nav-item").forEach((b) => {
    b.classList.toggle("active", b.dataset.mode === "classify");
  });
  $("transfer-views").style.display = "none";
  $("classify-views").style.display = "";
  refreshModeText();
  if (backupDir) {
    showClsView("cls-ready");
    doScan({ mode: "local", path: backupDir });
  } else {
    showClsView("cls-select");
  }
}

// ---------- 设置弹窗 ----------
async function loadSettingsPanel() {
  try {
    const r = await api("/api/settings");
    if (r.ok) {
      $("setTargetPath").textContent = r.target_dir || t("not_selected");
      document.querySelectorAll("#setOpSeg .seg-btn").forEach((b) => {
        b.classList.toggle("active", b.dataset.op === r.operation);
      });
      document.querySelectorAll("#setWorkersSeg .seg-btn").forEach((b) => {
        b.classList.toggle("active", parseInt(b.dataset.w, 10) === r.workers);
      });
      setGeoBadge(r.geo_available);
      refreshLangSeg();
      refreshThemeSeg();
    }
  } catch (e) {}
}

async function setOperation(op) {
  state.operation = op;
  refreshOpSeg();
  await api("/api/settings", { method: "POST", body: JSON.stringify({ operation: op }) });
}

async function setWorkers(w) {
  state.workers = w;
  refreshWorkersSeg();
  await api("/api/settings", { method: "POST", body: JSON.stringify({ workers: w }) });
}

// ---------- 关于弹窗 ----------
function openAbout() {
  $("aboutName").textContent = state.appName;
  $("aboutVersion").textContent = (state.lang === "en" ? "Version " : "版本 ") + state.version;
  $("aboutAuthor").textContent = "pzwwanOVO";
  const gh = $("aboutGithub");
  gh.textContent = "pzwwanOVO/photocategory";
  gh.onclick = (e) => { e.preventDefault(); openExternal("https://github.com/pzwwanOVO/photocategory"); };
  $("aboutModal").style.display = "grid";
}
function openExternal(url) {
  try {
    if (window.pywebview && window.pywebview.api && window.pywebview.api.open_url) {
      window.pywebview.api.open_url(url);
      return;
    }
  } catch (e) {}
  window.open(url, "_blank");
}

// ---------- 事件绑定 ----------
document.querySelectorAll(".nav-item").forEach((b) => {
  b.onclick = () => switchMode(b.dataset.mode);
});
$("btnPickTarget").onclick = () => openDirModal("target");
$("targetPath").onclick = () => openDirModal("target");
$("btnRetry").onclick = startDevicePoll;
$("btnBackWaiting").onclick = startDevicePoll;
$("btnCheckAuth").onclick = pollStorages;
$("btnBrowseDevice").onclick = () => openMtpModal();
$("btnRecogRefresh").onclick = () => loadSuggestedDirs();
$("btnRecogScan").onclick = confirmRecogScan;
$("btnTrfScan").onclick = () => {
  if (state.scanPaths && state.scanPaths.length) doScan({ mode: "mtp", name: state.device, scan_paths: state.scanPaths });
};
$("btnTrfStart").onclick = () => startRun("copy");
$("btnPickSource").onclick = () => openDirModal("source");
$("btnQuickPhoto").onclick = () => {
  state.scanned = false;
  state.source = null;
  showClsView("cls-ready");
  doScan({ mode: "local", path: "D:\\photo" });
};
$("btnClsRescan").onclick = () => {
  if (state.source && state.source.path) doScan({ mode: "local", path: state.source.path });
};
$("btnClsStart").onclick = () => startRun(state.operation);
document.querySelectorAll("#opSeg .seg-btn, #setOpSeg .seg-btn").forEach((b) => {
  b.onclick = () => setOperation(b.dataset.op);
});
document.querySelectorAll("#workersSeg .seg-btn, #setWorkersSeg .seg-btn").forEach((b) => {
  b.onclick = () => setWorkers(parseInt(b.dataset.w, 10));
});
// 语言 / 主题分段
document.querySelectorAll("#setLangSeg .seg-btn").forEach((b) => {
  b.onclick = () => setLang(b.dataset.lang);
});
document.querySelectorAll("#setThemeSeg .seg-btn").forEach((b) => {
  b.onclick = () => setTheme(b.dataset.theme);
});
// 目录弹窗
$("dirClose").onclick = () => ($("dirModal").style.display = "none");
$("dirConfirm").onclick = confirmDir;
$("dirManual").addEventListener("keydown", (e) => { if (e.key === "Enter") confirmDir(); });
// 设备目录浏览弹窗
$("mtpClose").onclick = () => ($("mtpModal").style.display = "none");
$("mtpConfirm").onclick = confirmMtpDir;
$("mtpSelectCurrent").onclick = selectCurrentMtpDir;
// 设置弹窗
$("btnSettings").onclick = () => { loadSettingsPanel(); $("settingsModal").style.display = "grid"; };
$("settingsClose").onclick = () => ($("settingsModal").style.display = "none");
$("btnSetTarget").onclick = () => { $("settingsModal").style.display = "none"; openDirModal("target"); };
$("btnAbout").onclick = () => { $("settingsModal").style.display = "none"; openAbout(); };
$("aboutClose").onclick = () => ($("aboutModal").style.display = "none");
// 运行/完成
$("btnStop").onclick = async () => { await api("/api/stop", { method: "POST" }); };
$("btnRestart").onclick = restart;
$("btnGoClassify").onclick = goClassify;
// 点击弹窗遮罩关闭
[$("dirModal"), $("mtpModal"), $("settingsModal"), $("aboutModal")].forEach((m) => {
  m.addEventListener("click", (e) => { if (e.target === m) m.style.display = "none"; });
});

// ---------- 无边框窗口控制 ----------
function hasPywebview() {
  return !!(window.pywebview && window.pywebview.api);
}
let winMaximized = false;
async function callWin(method) {
  try {
    if (hasPywebview()) await window.pywebview.api[method]();
  } catch (e) { /* 忽略 */ }
}
$("winMin").onclick = () => callWin("minimize");
const MAX_ICON = '<rect x="2.5" y="2.5" width="7" height="7" fill="none" stroke="currentColor" stroke-width="1" rx="1"/>';
const RESTORE_ICON = '<rect x="2" y="3.5" width="6" height="6" fill="none" stroke="currentColor" stroke-width="1" rx="1"/><path d="M4 3.5V2h6v6H8.5" fill="none" stroke="currentColor" stroke-width="1"/>';
function refreshMaxIcon() {
  const btn = $("winMax");
  if (!btn) return;
  const svg = btn.querySelector("svg");
  if (svg) svg.innerHTML = winMaximized ? RESTORE_ICON : MAX_ICON;
  btn.title = winMaximized ? t("win_close") === "关闭" ? "向下还原" : "Restore" : t("win_max");
}
$("winMax").onclick = async () => {
  if (winMaximized) { await callWin("restore"); winMaximized = false; }
  else { await callWin("maximize"); winMaximized = true; }
  refreshMaxIcon();
};
$("winClose").onclick = () => callWin("close");
window.addEventListener("pywebviewready", () => {
  try {
    const st = window.pywebview.state || {};
    if (st.maximized !== undefined) { winMaximized = !!st.maximized; refreshMaxIcon(); }
  } catch (e) {}
});

init();
