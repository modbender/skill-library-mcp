// ── GSAP 面板拖曳系統 ──
/* global Draggable */

const STORAGE_KEY = 'jarvis-panel-positions';

// 可拖曳面板的選擇器
const PANEL_SELECTORS = [
  '.terminal-panel.chat-panel',
  '.spectrum-analyzer',
  '.info-center',
];

function waitForDraggable() {
  return new Promise((resolve) => {
    if (typeof Draggable !== 'undefined') return resolve();
    const check = setInterval(() => {
      if (typeof Draggable !== 'undefined') { clearInterval(check); resolve(); }
    }, 50);
    setTimeout(() => { clearInterval(check); resolve(); }, 5000);
  });
}

// 保存面板位置 + 尺寸
export function savePanelPositions() {
  const positions = {};
  PANEL_SELECTORS.forEach(sel => {
    const el = document.querySelector(sel);
    if (!el) return;
    const d = Draggable.get(el);
    const entry = {};
    if (d) {
      entry.x = d.x;
      entry.y = d.y;
    }
    // 保存用戶調整過的尺寸
    if (el.style.width) entry.width = el.style.width;
    if (el.style.height) entry.height = el.style.height;
    // 保存收合狀態
    if (el.classList.contains('chat-collapsed')) entry.collapsed = true;
    positions[sel] = entry;
  });
  localStorage.setItem(STORAGE_KEY, JSON.stringify(positions));
}

// 還原面板位置 + 尺寸
function loadPanelPositions() {
  try {
    const data = JSON.parse(localStorage.getItem(STORAGE_KEY));
    if (!data) return;
    Object.entries(data).forEach(([sel, pos]) => {
      const el = document.querySelector(sel);
      if (!el) return;
      // 還原位置
      if (pos.x != null && typeof gsap !== 'undefined') {
        gsap.set(el, { x: pos.x, y: pos.y });
        const d = Draggable.get(el);
        if (d) d.update();
      }
      // 還原尺寸
      if (pos.width) el.style.width = pos.width;
      if (pos.height) el.style.height = pos.height;
      // 還原收合
      if (pos.collapsed) el.classList.add('chat-collapsed');
    });
  } catch {}
}

// 重置面板位置 + 尺寸
export function resetPanelPositions() {
  PANEL_SELECTORS.forEach(sel => {
    const el = document.querySelector(sel);
    if (!el) return;
    if (typeof gsap !== 'undefined') {
      gsap.set(el, { x: 0, y: 0, clearProps: 'transform' });
    } else {
      el.style.transform = '';
    }
    el.style.width = '';
    el.style.height = '';
    el.classList.remove('chat-collapsed');
    const d = Draggable.get(el);
    if (d) d.update();
  });
  localStorage.removeItem(STORAGE_KEY);
}

export function makePanelDraggable(element, handle = null) {
  if (!element) return;
  if (typeof Draggable === 'undefined') return;
  Draggable.create(element, {
    type: 'x,y',
    edgeResistance: 0.65,
    bounds: document.body,
    handle: handle || element,
    inertia: true,
    throwResistance: 0.85,
    onDragStart: function () {
      const panels = document.querySelectorAll(
        '.terminal-panel, .spectrum-analyzer, .data-panel'
      );
      let maxZ = 10;
      panels.forEach((panel) => {
        const z = parseInt(window.getComputedStyle(panel).zIndex);
        if (z > maxZ) maxZ = z;
      });
      element.style.zIndex = maxZ + 1;
    },
    onDragEnd: function () {
      savePanelPositions();
    },
  });
}

const isMobile = window.matchMedia('(max-width: 768px)').matches;

export async function initDraggablePanels() {
  if (isMobile) return;  // 手機版不啟用拖曳

  await waitForDraggable();
  if (typeof Draggable === 'undefined') {
    console.warn('[JARVIS] GSAP Draggable not loaded, skipping drag');
    return;
  }

  /* [DISABLED] COMMAND CENTER 已合併至 DATA CENTER
  makePanelDraggable(
    document.querySelector('.control-panel'),
    document.getElementById('control-panel-handle')
  );
  */
  makePanelDraggable(
    document.querySelector('.terminal-panel'),
    document.querySelector('.terminal-header')
  );
  makePanelDraggable(
    document.querySelector('.spectrum-analyzer'),
    document.getElementById('spectrum-handle')
  );
  makePanelDraggable(
    document.querySelector('.info-center'),
    document.getElementById('info-center-handle')
  );

  // 載入已保存的面板位置
  loadPanelPositions();
}
