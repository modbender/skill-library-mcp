// ── 省電模式 ──

import { showNotification } from './notifications.js';

let powerSaveEnabled = false;
let onPowerSaveChange = null;

const POWERSAVE_KEY = 'jarvis-powersave';

export function isPowerSave() { return powerSaveEnabled; }

export function setPowerSaveCallback(cb) { onPowerSaveChange = cb; }

export function initPowerSave() {
  // 讀取 localStorage
  powerSaveEnabled = localStorage.getItem(POWERSAVE_KEY) === 'true';

  const btn = document.getElementById('powersave-btn');
  if (!btn) return;

  updateButton(btn);

  btn.addEventListener('click', () => {
    powerSaveEnabled = !powerSaveEnabled;
    localStorage.setItem(POWERSAVE_KEY, powerSaveEnabled);
    updateButton(btn);
    applyPowerSave();
    showNotification(powerSaveEnabled ? '🔋 POWER SAVE ON' : '⚡ POWER SAVE OFF');
  });

  // 初始套用
  if (powerSaveEnabled) applyPowerSave();
}

function updateButton(btn) {
  btn.style.border = `1px solid rgba(var(--accent-rgb), ${powerSaveEnabled ? '0.8' : '0.3'})`;
  btn.style.background = powerSaveEnabled ? 'rgba(var(--accent-rgb), 0.15)' : 'transparent';
  btn.title = powerSaveEnabled ? 'Power Save: ON' : 'Power Save: OFF';
}

function applyPowerSave() {
  if (powerSaveEnabled) {
    document.body.classList.add('power-save');
  } else {
    document.body.classList.remove('power-save');
  }

  // 通知 main.js 調整渲染
  if (onPowerSaveChange) onPowerSaveChange(powerSaveEnabled);
  window.dispatchEvent(new CustomEvent('powersave-change', { detail: { enabled: powerSaveEnabled } }));
}
