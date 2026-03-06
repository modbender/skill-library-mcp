// ── 手機版浮動工具列 ──

import { resizeAllCanvases } from './spectrum.js';

const isMobile = window.matchMedia('(max-width: 768px)').matches;

const panelMap = {
  'spectrum': '.spectrum-analyzer',
  'info-center': '.info-center',
  /* [DISABLED] COMMAND CENTER 已合併至 DATA CENTER
  'control': '.control-panel',
  */
};

let activePanel = null;

function closePanel() {
  if (!activePanel) return;
  const panel = document.querySelector(panelMap[activePanel]);
  if (panel) {
    panel.classList.remove('mobile-open');
    // 等動畫結束後移除 mobile-slide（恢復原本隱藏）
    setTimeout(() => {
      if (!panel.classList.contains('mobile-open')) {
        panel.classList.remove('mobile-slide');
      }
    }, 300);
  }
  const btn = document.querySelector(`.mobile-toolbar-btn[data-panel="${activePanel}"]`);
  if (btn) btn.classList.remove('active');

  document.getElementById('mobile-overlay').classList.remove('visible');
  document.querySelector('.terminal-panel.chat-panel').classList.remove('panel-behind');
  activePanel = null;
}

function openPanel(name) {
  // 先關已開的
  if (activePanel) closePanel();

  const panel = document.querySelector(panelMap[name]);
  if (!panel) return;

  // 加 mobile-slide class，先讓它出現在畫面外（translateY 100%）
  panel.classList.add('mobile-slide');
  // 強制 reflow 讓 transition 生效
  panel.offsetHeight;
  // 滑入
  panel.classList.add('mobile-open');

  // 觸發 canvas resize（spectrum/waveform 在 display:none 時大小為 0）
  setTimeout(() => resizeAllCanvases(), 350);

  const btn = document.querySelector(`.mobile-toolbar-btn[data-panel="${name}"]`);
  if (btn) btn.classList.add('active');

  document.getElementById('mobile-overlay').classList.add('visible');
  document.querySelector('.terminal-panel.chat-panel').classList.add('panel-behind');
  activePanel = name;
}

export function initMobileToolbar() {
  if (!isMobile) return;

  const toolbar = document.getElementById('mobile-toolbar');
  if (!toolbar) return;

  // 工具列按鈕點擊
  toolbar.addEventListener('click', (e) => {
    const btn = e.target.closest('.mobile-toolbar-btn');
    if (!btn) return;
    const panel = btn.dataset.panel;
    if (activePanel === panel) {
      closePanel();
    } else {
      openPanel(panel);
    }
  });

  // 點 overlay 關閉
  document.getElementById('mobile-overlay').addEventListener('click', closePanel);
}
