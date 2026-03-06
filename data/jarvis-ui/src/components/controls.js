// ── 控制滑桿 + 重設 / 分析按鈕 + 主題調色盤 ──

import { showNotification } from './notifications.js';
import { setThemeHue, getThemeHue, THEME_PRESETS } from '../config/theme.js';
import { savePanelPositions, resetPanelPositions } from './draggable.js';

let audioReactivity = 1.0;
let audioSensitivity = 5.0;
let distortionAmount = 1.0;
let resolution = 32;
let onDistortionChange = null;
let onResolutionChange = null;

export function getAudioReactivity() { return audioReactivity; }
export function getAudioSensitivity() { return audioSensitivity; }
export function getDistortion() { return distortionAmount; }
export function getResolution() { return resolution; }

export function setCallbacks({ onDistortion, onResolution }) {
  onDistortionChange = onDistortion;
  onResolutionChange = onResolution;
}

export function initControls() {
  const rotationSlider = document.getElementById('rotation-slider');
  const resolutionSlider = document.getElementById('resolution-slider');
  const distortionSlider = document.getElementById('distortion-slider');
  const reactivitySlider = document.getElementById('reactivity-slider');
  const sensitivitySlider = document.getElementById('sensitivity-slider');

  rotationSlider?.addEventListener('input', function () {
    document.getElementById('rotation-value').textContent = this.value;
  });

  resolutionSlider?.addEventListener('input', function () {
    const value = parseInt(this.value);
    document.getElementById('resolution-value').textContent = value;
    resolution = value;
    if (onResolutionChange) onResolutionChange(value);
  });

  distortionSlider?.addEventListener('input', function () {
    const value = parseFloat(this.value);
    document.getElementById('distortion-value').textContent = value.toFixed(1);
    distortionAmount = value;
    if (onDistortionChange) onDistortionChange(value);
  });

  reactivitySlider?.addEventListener('input', function () {
    audioReactivity = parseFloat(this.value);
    document.getElementById('reactivity-value').textContent = audioReactivity.toFixed(1);
  });

  sensitivitySlider?.addEventListener('input', function () {
    audioSensitivity = parseFloat(this.value);
    document.getElementById('sensitivity-value').textContent = audioSensitivity.toString();
  });

  document.getElementById('reset-btn')?.addEventListener('click', function () {
    // 重置滑桿
    rotationSlider.value = 1.0;
    document.getElementById('rotation-value').textContent = '1.0';
    resolutionSlider.value = 32;
    document.getElementById('resolution-value').textContent = '32';
    distortionSlider.value = 1.0;
    document.getElementById('distortion-value').textContent = '1.0';
    reactivitySlider.value = 1.0;
    document.getElementById('reactivity-value').textContent = '1.0';
    audioReactivity = 1.0;
    sensitivitySlider.value = 5.0;
    document.getElementById('sensitivity-value').textContent = '5.0';
    audioSensitivity = 5.0;
    distortionAmount = 1.0;
    resolution = 32;
    if (onDistortionChange) onDistortionChange(1.0);
    if (onResolutionChange) onResolutionChange(32);
    
    // 重置面板位置
    resetPanelPositions();
    
    // 重置 Orb
    if (window.__jarvisResetAnomaly) window.__jarvisResetAnomaly();
    
    showNotification('ALL RESET TO DEFAULT');
  });

  document.getElementById('save-btn')?.addEventListener('click', function () {
    savePanelPositions();
    showNotification('LAYOUT SAVED');
  });
  
  // 初始化調色盤
  initThemePalette();
  
  // 初始化 TTS 引擎選擇
  initTTSEngineSelector();
}

// 調色盤初始化
function initThemePalette() {
  const paletteContainer = document.getElementById('theme-palette');
  if (!paletteContainer) return;
  
  const currentHue = getThemeHue();
  
  THEME_PRESETS.forEach(preset => {
    const btn = document.createElement('button');
    btn.className = 'theme-color-btn';
    btn.title = preset.name;
    btn.dataset.hue = preset.hue;
    const isSelected = preset.hue === currentHue;
    
    // 純色圓點
    btn.style.cssText = `
      width: 24px;
      height: 24px;
      border: 2px solid ${isSelected ? 'rgba(255,255,255,0.6)' : 'transparent'};
      background: hsl(${preset.hue}, 80%, 55%);
      border-radius: 50%;
      cursor: pointer;
      transition: all 0.3s ease;
      box-shadow: ${isSelected ? `0 0 8px hsl(${preset.hue}, 80%, 55%)` : 'none'};
    `;
    
    btn.addEventListener('mouseenter', function() {
      this.style.transform = 'scale(1.2)';
      this.style.boxShadow = `0 0 10px hsl(${preset.hue}, 80%, 55%)`;
    });
    
    btn.addEventListener('mouseleave', function() {
      this.style.transform = 'scale(1)';
      if (parseInt(this.dataset.hue) !== getThemeHue()) {
        this.style.boxShadow = 'none';
      }
    });
    
    // 點擊切換主題
    btn.addEventListener('click', function() {
      const hue = parseInt(this.dataset.hue);
      setThemeHue(hue);
      showNotification(`THEME CHANGED TO ${preset.name.toUpperCase()}`);
      updatePaletteSelection();
    });
    
    paletteContainer.appendChild(btn);
  });
}

// 更新調色盤選中狀態
function updatePaletteSelection() {
  const currentHue = getThemeHue();
  const buttons = document.querySelectorAll('.theme-color-btn');
  
  buttons.forEach(btn => {
    const hue = parseInt(btn.dataset.hue);
    const isSelected = hue === currentHue;
    btn.style.border = `2px solid ${isSelected ? 'rgba(255,255,255,0.6)' : 'transparent'}`;
    btn.style.boxShadow = isSelected ? `0 0 8px hsl(${hue}, 80%, 55%)` : 'none';
  });
}

// ── TTS 引擎選擇 ──
async function initTTSEngineSelector() {
  const container = document.getElementById('tts-engine-btns');
  const label = document.getElementById('tts-engine-label');
  if (!container) return;

  try {
    const res = await fetch('/api/tts/engines');
    if (!res.ok) return;
    const data = await res.json();

    label.textContent = data.engines.find(e => e.selected)?.name || '—';

    data.engines.forEach(engine => {
      if (!engine.available) return;
      const btn = document.createElement('button');
      btn.className = 'btn tts-engine-btn';
      btn.textContent = engine.name.toUpperCase();
      btn.dataset.engine = engine.id;
      btn.style.cssText = `
        flex: 1;
        padding: 6px 12px;
        font-size: 0.6875rem;
        border: 1px solid ${engine.selected ? 'rgba(var(--accent-rgb), 0.8)' : 'rgba(var(--accent-rgb), 0.3)'};
        background: ${engine.selected ? 'rgba(var(--accent-rgb), 0.15)' : 'transparent'};
        color: var(--text-primary);
        cursor: pointer;
        font-family: "TheGoodMonolith", monospace;
        letter-spacing: 1px;
      `;

      btn.addEventListener('click', async () => {
        const r = await fetch('/api/tts/engine', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ engine: engine.id })
        });
        if (r.ok) {
          showNotification(`TTS ENGINE: ${engine.name.toUpperCase()}`);
          label.textContent = engine.name;
          updateTTSButtons(engine.id);
        }
      });

      container.appendChild(btn);
    });
  } catch {}
}

function updateTTSButtons(selectedId) {
  document.querySelectorAll('.tts-engine-btn').forEach(btn => {
    const isSelected = btn.dataset.engine === selectedId;
    btn.style.border = `1px solid rgba(var(--accent-rgb), ${isSelected ? '0.8' : '0.3'})`;
    btn.style.background = isSelected ? 'rgba(var(--accent-rgb), 0.15)' : 'transparent';
  });
}
