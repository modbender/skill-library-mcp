// ── 系統監控面板（真實資料，從 SSE 接收） ──

import { getAccentHex, getAccentRGB } from '../config/theme.js';

function getThemeRgbaValue(alpha) {
  return `rgba(${getAccentRGB()}, ${alpha})`;
}

const cpuCanvas = document.getElementById('cpu-canvas');
const cpuCtx = cpuCanvas ? cpuCanvas.getContext('2d') : null;
const cpuHistory = new Array(60).fill(0);

const cpuEl = document.getElementById('cpu-value');
const memEl = document.getElementById('mem-value');
const uptimeEl = document.getElementById('uptime-value');
const procEl = document.getElementById('proc-value');
const indicator = document.getElementById('model-indicator');

// Uptime 本地補間（SSE 3 秒一次，本地每秒遞增）
let lastUptime = 0;
let uptimeTimer = null;

function drawCpuGraph() {
  if (!cpuCtx || !cpuCanvas) return;
  const w = cpuCanvas.width;
  const h = cpuCanvas.height;
  cpuCtx.clearRect(0, 0, w, h);

  // 網格線
  cpuCtx.strokeStyle = getThemeRgbaValue(0.1);
  cpuCtx.lineWidth = 0.5;
  for (let y = 0; y <= h; y += h / 4) {
    cpuCtx.beginPath();
    cpuCtx.moveTo(0, y);
    cpuCtx.lineTo(w, y);
    cpuCtx.stroke();
  }

  // CPU 使用率曲線
  const accentHex = getAccentHex();
  cpuCtx.strokeStyle = accentHex;
  cpuCtx.lineWidth = 1.5;
  cpuCtx.shadowColor = accentHex;
  cpuCtx.shadowBlur = 4;
  cpuCtx.beginPath();
  const step = w / (cpuHistory.length - 1);
  cpuHistory.forEach((val, i) => {
    const x = i * step;
    const y = h - (val / 100) * h;
    if (i === 0) cpuCtx.moveTo(x, y);
    else cpuCtx.lineTo(x, y);
  });
  cpuCtx.stroke();
  cpuCtx.shadowBlur = 0;

  // 曲線下方填色
  cpuCtx.lineTo(w, h);
  cpuCtx.lineTo(0, h);
  cpuCtx.closePath();
  cpuCtx.fillStyle = getThemeRgbaValue(0.08);
  cpuCtx.fill();
}

function formatUptime(seconds) {
  const d = Math.floor(seconds / 86400);
  const h = Math.floor((seconds % 86400) / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  const s = Math.floor(seconds % 60);
  if (d > 0) return `${d}d ${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
  return `${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
}

// 接收 SSE system 事件
export function updateSystemData(data) {
  const cpu = data.cpu || 0;

  cpuHistory.push(cpu);
  cpuHistory.shift();

  if (cpuEl) cpuEl.textContent = `${Math.round(cpu)}%`;
  if (memEl) memEl.textContent = `${data.mem.used} / ${data.mem.total} GB`;
  if (procEl) procEl.textContent = data.procs || 0;

  // Uptime：同步伺服器值，本地每秒遞增
  lastUptime = data.uptime;
  if (uptimeEl) uptimeEl.textContent = formatUptime(lastUptime);
  if (!uptimeTimer) {
    uptimeTimer = setInterval(() => {
      lastUptime++;
      if (uptimeEl) uptimeEl.textContent = formatUptime(lastUptime);
    }, 1000);
  }

  // 狀態指示燈
  if (indicator) {
    if (cpu > 80) indicator.style.color = getAccentHex();
    else if (cpu > 50) indicator.style.color = '#fbbf24';
    else indicator.style.color = '#4ade80';
  }

  drawCpuGraph();
}

export function initSystemMonitor() {
  // 初始繪製空圖表
  drawCpuGraph();
}
