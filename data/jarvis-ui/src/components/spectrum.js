// ── 頻譜分析器（收合 + 波形顯示） ──

import { getAccentRGB, getThemeHue } from '../config/theme.js';

// 取得當前主題色（用於 canvas 繪圖）
function getThemeRgbaValue(alpha) {
  return `rgba(${getAccentRGB()}, ${alpha})`;
}

// 收合功能
export function initSpectrumCollapse() {
  const collapseBtn = document.getElementById('spectrum-collapse');
  if (collapseBtn) {
    collapseBtn.addEventListener('click', () => {
      const analyzer = document.querySelector('.spectrum-analyzer');
      if (analyzer) analyzer.classList.toggle('collapsed');
    });
  }
}

// 頻譜繪製
const spectrumCanvas = document.getElementById('spectrum-canvas');
const spectrumCtx = spectrumCanvas ? spectrumCanvas.getContext('2d') : null;

function resizeSpectrumCanvas() {
  if (!spectrumCanvas) return;
  spectrumCanvas.width = spectrumCanvas.offsetWidth;
  spectrumCanvas.height = spectrumCanvas.offsetHeight;
}

export function drawSpectrumAnalyzer(frequencyData, audioSensitivity) {
  if (!spectrumCtx || !spectrumCanvas) return;
  const width = spectrumCanvas.width;
  const height = spectrumCanvas.height;
  spectrumCtx.clearRect(0, 0, width, height);

  const barWidth = width / 256;
  let x = 0;
  for (let i = 0; i < 256; i++) {
    const barHeight = (frequencyData[i] / 255) * height * (audioSensitivity / 5);
    const hue = getThemeHue() + (i / 256) * 20;
    spectrumCtx.fillStyle = `hsl(${hue}, 100%, 50%)`;
    spectrumCtx.fillRect(x, height - barHeight, barWidth - 1, barHeight);
    x += barWidth;
  }

  // 網格線
  spectrumCtx.strokeStyle = getThemeRgbaValue(0.2);
  spectrumCtx.lineWidth = 1;
  for (let i = 0; i < 5; i++) {
    const y = height * (i / 4);
    spectrumCtx.beginPath();
    spectrumCtx.moveTo(0, y);
    spectrumCtx.lineTo(width, y);
    spectrumCtx.stroke();
  }
  for (let i = 0; i < 9; i++) {
    const lx = width * (i / 8);
    spectrumCtx.beginPath();
    spectrumCtx.moveTo(lx, 0);
    spectrumCtx.lineTo(lx, height);
    spectrumCtx.stroke();
  }

  // 頻率標籤
  spectrumCtx.fillStyle = getThemeRgbaValue(0.7);
  spectrumCtx.font = '10px "TheGoodMonolith", monospace';
  spectrumCtx.textAlign = 'center';
  const freqLabels = ['0', '1K', '2K', '4K', '8K', '16K'];
  for (let i = 0; i < freqLabels.length; i++) {
    const lx = (width / (freqLabels.length - 1)) * i;
    spectrumCtx.fillText(freqLabels[i], lx, height - 5);
  }
}

// 環形視覺化
const circularCanvas = document.getElementById('circular-canvas');
const circularCtx = circularCanvas ? circularCanvas.getContext('2d') : null;

function resizeCircularCanvas() {
  if (!circularCanvas) return;
  circularCanvas.width = circularCanvas.offsetWidth;
  circularCanvas.height = circularCanvas.offsetHeight;
}

export function drawCircularVisualizer(frequencyData, audioSensitivity, audioReactivity) {
  if (!circularCtx || !circularCanvas) return;
  const width = circularCanvas.width;
  const height = circularCanvas.height;
  const centerX = width / 2;
  const centerY = height / 2;
  circularCtx.clearRect(0, 0, width, height);

  const numPoints = 180;
  const baseRadius = Math.min(width, height) * 0.4;

  circularCtx.beginPath();
  circularCtx.arc(centerX, centerY, baseRadius * 1.2, 0, Math.PI * 2);
  circularCtx.fillStyle = getThemeRgbaValue(0.05);
  circularCtx.fill();

  const numRings = 3;
  const analyserBinCount = frequencyData.length;

  for (let ring = 0; ring < numRings; ring++) {
    const ringRadius = baseRadius * (0.7 + ring * 0.15);
    const opacity = 0.8 - ring * 0.2;

    circularCtx.beginPath();
    for (let i = 0; i < numPoints; i++) {
      const freqRangeStart = Math.floor((ring * analyserBinCount) / (numRings * 1.5));
      const freqRangeEnd = Math.floor(((ring + 1) * analyserBinCount) / (numRings * 1.5));
      const freqRange = freqRangeEnd - freqRangeStart;
      let sum = 0;
      const segmentSize = Math.floor(freqRange / numPoints);
      for (let j = 0; j < segmentSize; j++) {
        const freqIndex = freqRangeStart + ((i * segmentSize + j) % freqRange);
        sum += frequencyData[freqIndex];
      }
      const value = sum / (segmentSize * 255);
      const adjustedValue = value * (audioSensitivity / 5) * audioReactivity;
      const dynamicRadius = ringRadius * (1 + adjustedValue * 0.5);
      const angle = (i / numPoints) * Math.PI * 2;
      const x = centerX + Math.cos(angle) * dynamicRadius;
      const y = centerY + Math.sin(angle) * dynamicRadius;
      if (i === 0) circularCtx.moveTo(x, y);
      else circularCtx.lineTo(x, y);
    }
    circularCtx.closePath();

    // 使用主題顏色計算 gradient (從 CSS 變數取得 HSL)
    const accentRGB = getAccentRGB();
    let gradient;
    gradient = circularCtx.createRadialGradient(
      centerX, centerY, ringRadius * 0.8,
      centerX, centerY, ringRadius * 1.2
    );
    gradient.addColorStop(0, `rgba(${accentRGB}, ${opacity})`);
    gradient.addColorStop(1, `rgba(${accentRGB}, ${opacity * 0.7})`);

    circularCtx.strokeStyle = gradient;
    circularCtx.lineWidth = 2 + (numRings - ring);
    circularCtx.stroke();
    circularCtx.shadowBlur = 15;
    circularCtx.shadowColor = getThemeRgbaValue(0.7);
  }
  circularCtx.shadowBlur = 0;
}

// 波形圖 (data-center metrics)
const waveformCanvas = document.getElementById('waveform-canvas');
const waveformCtx = waveformCanvas ? waveformCanvas.getContext('2d') : null;

function resizeWaveformCanvas() {
  if (!waveformCanvas || !waveformCtx) return;
  waveformCanvas.width = waveformCanvas.offsetWidth * window.devicePixelRatio;
  waveformCanvas.height = waveformCanvas.offsetHeight * window.devicePixelRatio;
  waveformCtx.scale(window.devicePixelRatio, window.devicePixelRatio);
}

export function drawWaveform(audioData) {
  if (!waveformCtx || !waveformCanvas) return;
  const width = waveformCanvas.width / window.devicePixelRatio;
  const height = waveformCanvas.height / window.devicePixelRatio;
  waveformCtx.clearRect(0, 0, width, height);
  waveformCtx.fillStyle = 'rgba(0, 0, 0, 0.2)';
  waveformCtx.fillRect(0, 0, width, height);

  if (audioData) {
    waveformCtx.beginPath();
    waveformCtx.strokeStyle = getThemeRgbaValue(0.8);
    waveformCtx.lineWidth = 2;
    const sliceWidth = width / audioData.length;
    let x = 0;
    for (let i = 0; i < audioData.length; i++) {
      const v = audioData[i] / 128.0;
      const y = (v * height) / 2;
      if (i === 0) waveformCtx.moveTo(x, y);
      else waveformCtx.lineTo(x, y);
      x += sliceWidth;
    }
    waveformCtx.stroke();
  } else {
    // 無音訊時的預設波形
    waveformCtx.beginPath();
    waveformCtx.strokeStyle = getThemeRgbaValue(0.8);
    waveformCtx.lineWidth = 1;
    const time = Date.now() / 1000;
    const sliceWidth = width / 100;
    let x = 0;
    for (let i = 0; i < 100; i++) {
      const t = i / 100;
      const y = height / 2 + Math.sin(t * 10 + time) * 5 + Math.sin(t * 20 + time * 1.5) * 3 + Math.sin(t * 30 + time * 0.5) * 7 + (Math.random() - 0.5) * 2;
      if (i === 0) waveformCtx.moveTo(x, y);
      else waveformCtx.lineTo(x, y);
      x += sliceWidth;
    }
    waveformCtx.stroke();
  }
}

// resize 監聽
export function initVisualizers() {
  resizeSpectrumCanvas();
  resizeCircularCanvas();
  resizeWaveformCanvas();
  window.addEventListener('resize', () => {
    resizeSpectrumCanvas();
    resizeCircularCanvas();
    resizeWaveformCanvas();
  });
}

export function resizeAllCanvases() {
  resizeSpectrumCanvas();
  resizeCircularCanvas();
  resizeWaveformCanvas();
}
