// 小米图片分类整理 — 前端逻辑（Win11 风格）
const $ = (id) => document.getElementById(id);
const TYPE_LABEL = {
  photo: "照片", screenshot: "截图", app: "应用图片",
  recording: "录屏", video: "视频", other: "其他",
};
const TYPE_TAG = { recording: "video" };

let state = {
  mode: "transfer",          // transfer | classify
  device: null,
  storage: null,
  source: null,              // {type, name/path}
  scanned: false,
  scanCount: 0,
  typeCounts: {},
  target: null,
  operation: "copy",         // copy | move（仅本地分类用）
  workers: 1,                // 并发线程数
  running: false,
  pollTimer: null,
  devTimer: null,
};
const WORKERS_HINT = {
  1: "1 线程 · 最低占用（推荐后台整理）",
  2: "2 线程 · 平衡速度与占用",
  4: "4 线程 · 较快，磁盘/CPU 占用较高",
};

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

function switchMode(mode) {
  state.mode = mode;
  document.querySelectorAll(".nav-item").forEach((b) => {
    b.classList.toggle("active", b.dataset.mode === mode);
  });
  $("transfer-views").style.display = mode === "transfer" ? "" : "none";
  $("classify-views").style.display = mode === "classify" ? "" : "none";
  if (mode === "transfer") {
    $("modeTitle").textContent = "传输备份";
    $("modeDesc").textContent = "USB 连接手机 → 授权传输 → 自动分类归档";
    if (state.running) showSharedView("view-running");
    else if (state.scanned && state.source && state.source.type === "mtp") showTrfView("trf-ready");
    else showTrfView(state.device ? "trf-detected" : "trf-waiting");
  } else {
    $("modeTitle").textContent = "图片分类";
    $("modeDesc").textContent = "选择本地备份目录 → 自动分类整理（可复制或移动）";
    if (state.running) showSharedView("view-running");
    else if (state.scanned && state.source && state.source.type === "local") showClsView("cls-ready");
    else showClsView("cls-select");
  }
}

// ---------- API ----------
async function api(path, opts = {}) {
  const res = await fetch(path, {
    headers: { "Content-Type": "application/json" },
    ...opts,
  });
  return res.json();
}

// ---------- 初始化 ----------
async function init() {
  const st = await api("/api/status");
  // 载入设置
  if (st.target_dir) { state.target = st.target_dir; }
  if (st.operation) { state.operation = st.operation; }
  if (st.workers) { state.workers = st.workers; }
  refreshTargetUI();
  refreshOpSeg();
  refreshWorkersSeg();
  // 默认进入传输备份模式
  switchMode("transfer");
  startDevicePoll();
}

function setGeoBadge(ok) {
  const badge = $("setGeoStatus");
  if (!badge) return;
  badge.className = "badge";
  if (ok === true) { badge.classList.add("ok"); badge.textContent = "可用"; }
  else if (ok === false) { badge.classList.add("warn"); badge.textContent = "未安装"; }
  else { badge.textContent = "检测中"; }
}

// ---------- 整理位置 ----------
function refreshTargetUI() {
  const path = state.target || "未选择";
  $("targetPath").textContent = path;
  $("targetPath").title = state.target || "点击更改";
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

function refreshWorkersSeg() {
  document.querySelectorAll("#workersSeg .seg-btn, #setWorkersSeg .seg-btn").forEach((b) => {
    b.classList.toggle("active", parseInt(b.dataset.w, 10) === state.workers);
  });
  const hint = $("workersHint");
  if (hint) hint.textContent = WORKERS_HINT[state.workers] || "";
}

function updateStartBtns() {
  $("btnTrfStart").disabled = !(state.scanned && state.target && state.source && state.source.type === "mtp");
  $("btnClsStart").disabled = !(state.scanned && state.target && state.source && state.source.type === "local");
}

// ---------- 设备轮询 ----------
function startDevicePoll() {
  stopDevicePoll();
  if (state.mode !== "transfer") return;
  if (state.scanned && state.source && state.source.type === "mtp") { showTrfView("trf-ready"); return; }
  showTrfView("trf-waiting");
  $("pollHint").textContent = "正在检测设备…";
  state.devTimer = setInterval(pollDevices, 2000);
  pollDevices();
}
function stopDevicePoll() {
  if (state.devTimer) { clearInterval(state.devTimer); state.devTimer = null; }
}

async function pollDevices() {
  try {
    const r = await api("/api/devices");
    if (r.ok && r.devices && r.devices.length > 0) {
      stopDevicePoll();
      state.device = r.devices[0].name;
      $("deviceName").textContent = state.device;
      showTrfView("trf-detected");
      pollStorages();
    } else {
      $("pollHint").textContent = "未检测到便携设备，请连接手机…";
    }
  } catch (e) {
    $("pollHint").textContent = "检测异常：" + e.message;
  }
}

async function pollStorages() {
  try {
    const r = await api("/api/devices/" + encodeURIComponent(state.device) + "/storages");
    if (r.ok && r.authorized) {
      state.storage = r.storages && r.storages[0];
      $("storageInfo").textContent = "存储：" + (state.storage || "—");
      enterTrfReady();
      return true;
    }
    $("storageInfo").textContent = r.error
      ? "无法访问：" + r.error
      : "未授权，请在手机端选择「传输文件」";
  } catch (e) {
    $("storageInfo").textContent = "探测失败：" + e.message;
  }
  if (!state.running && $("trf-detected").classList.contains("active")) {
    setTimeout(pollStorages, 2000);
  }
  return false;
}

function enterTrfReady() {
  showTrfView("trf-ready");
  if (!state.scanned || (state.source && state.source.type !== "mtp")) {
    doScan({ mode: "mtp", name: state.device });
  }
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
    if (!r.ok) { alert("扫描失败：" + r.error); countEl.textContent = "—"; return; }
    state.source = r.source;
    state.scanned = true;
    state.scanCount = r.count;
    state.typeCounts = r.type_counts || {};
    countEl.textContent = r.count;
    renderTypeBreak(breakEl, state.typeCounts);
    if (isLocal) $("clsSource").textContent = r.source.path;
    // 预览
    listEl.innerHTML = "";
    (r.preview || []).forEach((p) => {
      const li = document.createElement("li");
      const tag = TYPE_TAG[p.type] || p.type;
      const label = TYPE_LABEL[p.type] || p.type;
      li.innerHTML = `<span class="name">${p.name}</span><span class="tag ${tag}">${label}</span>`;
      listEl.appendChild(li);
    });
    prevEl.style.display = r.preview && r.preview.length ? "block" : "none";
    updateStartBtns();
  } catch (e) {
    alert("扫描异常：" + e.message);
    countEl.textContent = "—";
  }
}

function renderTypeBreak(el, counts) {
  el.innerHTML = "";
  Object.entries(counts).forEach(([k, v]) => {
    if (!v) return;
    const chip = document.createElement("span");
    chip.className = "type-chip";
    chip.innerHTML = `${TYPE_LABEL[k] || k} <b>${v}</b>`;
    el.appendChild(chip);
  });
}

// ---------- 目录选择 ----------
let dirState = { current: "", purpose: "target" };  // purpose: target | source

async function openDirModal(purpose) {
  dirState = { current: "", purpose };
  $("dirModalTitle").textContent = purpose === "source" ? "选择来源目录" : "选择目标目录";
  $("dirModal").style.display = "grid";
  $("dirManual").value = "";
  await loadDir("");
}

const FOLDER_SVG = '<svg viewBox="0 0 24 24" width="16" height="16"><path fill="currentColor" d="M10 4H4a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V8a2 2 0 0 0-2-2h-8l-2-2z"/></svg>';
const UP_SVG = '<svg viewBox="0 0 24 24" width="16" height="16"><path fill="currentColor" d="M10 4H4a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V8a2 2 0 0 0-2-2h-8l-2-2z"/></svg>';

async function loadDir(path) {
  dirState.current = path;
  const r = await api("/api/browse?path=" + encodeURIComponent(path));
  if (!r.ok) { alert(r.error); return; }
  $("dirCrumbs").textContent = path ? path : "此电脑";
  const list = $("dirList");
  list.innerHTML = "";
  if (path) {
    const up = document.createElement("li");
    up.innerHTML = UP_SVG + " ..";
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
  if (!path) { alert("请选择一个目录"); return; }
  $("dirModal").style.display = "none";
  if (dirState.purpose === "target") {
    setTarget(path);
  } else if (dirState.purpose === "source") {
    // 本地分类：扫描来源目录
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
  const body = operation ? { operation } : {};
  const r2 = await api("/api/start", { method: "POST", body: JSON.stringify(body) });
  if (!r2.ok) { alert(r2.error); return; }
  state.running = true;
  const wTag = $("runningWorkers");
  if (wTag) {
    wTag.textContent = state.source && state.source.type === "local"
      ? `${r2.workers || state.workers} 线程`
      : "单线程";
  }
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
    ? "暂存区：" + stats.staging_dir + "（失败文件保留于此）"
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
}

function renderKV(ul, obj) {
  ul.innerHTML = "";
  const entries = Object.entries(obj).sort((a, b) => b[1] - a[1]);
  if (!entries.length) {
    const li = document.createElement("li");
    li.innerHTML = `<span class="muted">无</span>`;
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
  if (state.mode === "transfer") {
    startDevicePoll();
  } else {
    showClsView("cls-select");
  }
}

// ---------- 设置弹窗 ----------
async function loadSettingsPanel() {
  try {
    const r = await api("/api/settings");
    if (r.ok) {
      $("setTargetPath").textContent = r.target_dir || "未选择";
      document.querySelectorAll("#setOpSeg .seg-btn").forEach((b) => {
        b.classList.toggle("active", b.dataset.op === r.operation);
      });
      document.querySelectorAll("#setWorkersSeg .seg-btn").forEach((b) => {
        b.classList.toggle("active", parseInt(b.dataset.w, 10) === r.workers);
      });
      setGeoBadge(r.geo_available);
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

// ---------- 事件绑定 ----------
// 导航
document.querySelectorAll(".nav-item").forEach((b) => {
  b.onclick = () => switchMode(b.dataset.mode);
});
// 整理位置
$("btnPickTarget").onclick = () => openDirModal("target");
$("targetPath").onclick = () => openDirModal("target");
// 传输备份
$("btnRetry").onclick = startDevicePoll;
$("btnBackWaiting").onclick = startDevicePoll;
$("btnCheckAuth").onclick = pollStorages;
$("btnTrfScan").onclick = () => doScan({ mode: "mtp", name: state.device });
$("btnTrfStart").onclick = () => startRun("copy");
// 图片分类
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
// 操作方式分段
document.querySelectorAll("#opSeg .seg-btn").forEach((b) => {
  b.onclick = () => setOperation(b.dataset.op);
});
document.querySelectorAll("#setOpSeg .seg-btn").forEach((b) => {
  b.onclick = () => setOperation(b.dataset.op);
});
// 性能分段
document.querySelectorAll("#workersSeg .seg-btn").forEach((b) => {
  b.onclick = () => setWorkers(parseInt(b.dataset.w, 10));
});
document.querySelectorAll("#setWorkersSeg .seg-btn").forEach((b) => {
  b.onclick = () => setWorkers(parseInt(b.dataset.w, 10));
});
// 目录弹窗
$("dirClose").onclick = () => ($("dirModal").style.display = "none");
$("dirConfirm").onclick = confirmDir;
$("dirManual").addEventListener("keydown", (e) => { if (e.key === "Enter") confirmDir(); });
// 设置弹窗
$("btnSettings").onclick = () => { loadSettingsPanel(); $("settingsModal").style.display = "grid"; };
$("settingsClose").onclick = () => ($("settingsModal").style.display = "none");
$("btnSetTarget").onclick = () => { $("settingsModal").style.display = "none"; openDirModal("target"); };
// 运行/完成
$("btnStop").onclick = async () => { await api("/api/stop", { method: "POST" }); };
$("btnRestart").onclick = restart;
// 点击弹窗遮罩关闭
[$("dirModal"), $("settingsModal")].forEach((m) => {
  m.addEventListener("click", (e) => { if (e.target === m) m.style.display = "none"; });
});

// ---------- 无边框窗口控制 ----------
// 仅在 pywebview 环境下生效（浏览器中为空操作）
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
  btn.title = winMaximized ? "向下还原" : "最大化";
}
$("winMax").onclick = async () => {
  // 切换最大化/还原（JS 端跟踪状态）
  if (winMaximized) { await callWin("restore"); winMaximized = false; }
  else { await callWin("maximize"); winMaximized = true; }
  refreshMaxIcon();
};
$("winClose").onclick = () => callWin("close");
// pywebview 就绪后，同步真实窗口状态
window.addEventListener("pywebviewready", () => {
  try {
    const st = window.pywebview.state || {};
    if (st.maximized !== undefined) { winMaximized = !!st.maximized; refreshMaxIcon(); }
  } catch (e) {}
});

init();
