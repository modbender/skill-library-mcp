// ── 音頻系統 ──

import { showNotification } from '../components/notifications.js';

// 透過 CustomEvent 寫入 terminal（避免循環依賴 chat.js）
function addTerminalMessage(message, isCommand = false) {
  window.dispatchEvent(new CustomEvent('terminal-message', { detail: { message, isCommand } }));
}

let audioContext = null;
let audioAnalyser = null;
let audioSource = null;
let audioData;
let frequencyData;
let isAudioInitialized = false;
let isAudioPlaying = false;
let audioContextStarted = false;
let audioSourceConnected = false;
let currentAudioElement = null;
let currentAudioSrc = null;
let onZoomCamera = null;

export function getAudioData() { return audioData; }
export function getFrequencyData() { return frequencyData; }
export function getAnalyser() { return audioAnalyser; }
export function getIsPlaying() { return isAudioPlaying; }
export function getIsInitialized() { return isAudioInitialized; }

export function setZoomCallback(cb) { onZoomCamera = cb; }

export function initAudio() {
  if (isAudioInitialized) return true;
  try {
    audioContext = new (window.AudioContext || window.webkitAudioContext)();
    audioAnalyser = audioContext.createAnalyser();
    audioAnalyser.fftSize = 2048;
    audioAnalyser.smoothingTimeConstant = 0.8;
    audioData = new Uint8Array(audioAnalyser.frequencyBinCount);
    frequencyData = new Uint8Array(audioAnalyser.frequencyBinCount);
    audioAnalyser.connect(audioContext.destination);
    isAudioInitialized = true;
    addTerminalMessage('AUDIO ANALYSIS SYSTEM INITIALIZED.');
    showNotification('AUDIO ANALYSIS SYSTEM ONLINE');
    return true;
  } catch (error) {
    console.error('Audio initialization error:', error);
    addTerminalMessage('ERROR: AUDIO SYSTEM INITIALIZATION FAILED.');
    showNotification('AUDIO SYSTEM ERROR');
    return false;
  }
}

export function ensureAudioContextStarted() {
  if (!audioContext) {
    if (!initAudio()) return false;
  }
  if (audioContext.state === 'suspended') {
    audioContext.resume().then(() => {
      if (!audioContextStarted) {
        audioContextStarted = true;
        addTerminalMessage('AUDIO CONTEXT RESUMED.');
      }
    }).catch((err) => {
      console.error('Failed to resume audio context:', err);
      addTerminalMessage('ERROR: FAILED TO RESUME AUDIO CONTEXT.');
    });
  } else {
    audioContextStarted = true;
  }
  return true;
}

function cleanupAudioSource() {
  if (audioSource) {
    try {
      audioSource.disconnect();
      audioSourceConnected = false;
      audioSource = null;
    } catch (e) {
      console.log('Error disconnecting previous source:', e);
    }
  }
}

function createNewAudioElement() {
  if (currentAudioElement && currentAudioElement.parentNode) {
    currentAudioElement.parentNode.removeChild(currentAudioElement);
  }
  const newAudioElement = document.createElement('audio');
  newAudioElement.id = 'audio-player';
  newAudioElement.className = 'audio-player';
  newAudioElement.crossOrigin = 'anonymous';
  const controlsRow = document.querySelector('.controls-row');
  const audioControls = document.querySelector('.audio-controls');
  if (audioControls && controlsRow) {
    audioControls.insertBefore(newAudioElement, controlsRow);
  }
  currentAudioElement = newAudioElement;

  // 重新綁定 ended 事件
  newAudioElement.addEventListener('ended', () => {
    isAudioPlaying = false;
    if (onZoomCamera) onZoomCamera(false);
    addTerminalMessage('AUDIO PLAYBACK COMPLETE.');
  });

  return newAudioElement;
}

function setupAudioSource(audioElement) {
  try {
    if (!ensureAudioContextStarted()) {
      addTerminalMessage('ERROR: AUDIO CONTEXT NOT AVAILABLE. CLICK ANYWHERE TO ENABLE AUDIO.');
      return false;
    }
    cleanupAudioSource();
    try {
      if (!audioSourceConnected) {
        audioSource = audioContext.createMediaElementSource(audioElement);
        audioSource.connect(audioAnalyser);
        audioSourceConnected = true;
      }
      return true;
    } catch (error) {
      console.error('Error creating media element source:', error);
      if (error.name === 'InvalidStateError' && error.message.includes('already connected')) {
        addTerminalMessage('AUDIO SOURCE ALREADY CONNECTED. ATTEMPTING TO PLAY ANYWAY.');
        return true;
      }
      addTerminalMessage('ERROR: FAILED TO SETUP AUDIO SOURCE. ' + error.message);
      return false;
    }
  } catch (error) {
    console.error('Error setting up audio source:', error);
    addTerminalMessage('ERROR: FAILED TO SETUP AUDIO SOURCE.');
    return false;
  }
}

export function initAudioFile(file) {
  try {
    if (!isAudioInitialized && !initAudio()) return;
    const audioPlayer = createNewAudioElement();
    const fileURL = URL.createObjectURL(file);
    currentAudioSrc = fileURL;
    audioPlayer.src = fileURL;
    audioPlayer.onloadeddata = function () {
      if (setupAudioSource(audioPlayer)) {
        audioPlayer.play().then(() => {
          isAudioPlaying = true;
          if (onZoomCamera) onZoomCamera(true);
        }).catch((e) => {
          console.warn('Auto-play prevented:', e);
          addTerminalMessage('WARNING: AUTO-PLAY PREVENTED BY BROWSER. CLICK PLAY TO START AUDIO.');
        });
      }
    };
    document.getElementById('file-label').textContent = file.name;
    document.querySelectorAll('.demo-track-btn').forEach((btn) => btn.classList.remove('active'));
    addTerminalMessage(`AUDIO FILE LOADED: ${file.name}`);
    showNotification('AUDIO FILE LOADED');
  } catch (error) {
    console.error('Audio file error:', error);
    addTerminalMessage('ERROR: AUDIO FILE PROCESSING FAILED.');
    showNotification('AUDIO FILE ERROR');
  }
}

export function loadAudioFromURL(url) {
  try {
    if (!isAudioInitialized && !initAudio()) return;
    ensureAudioContextStarted();
    const audioPlayer = createNewAudioElement();
    currentAudioSrc = url;
    audioPlayer.src = url;
    audioPlayer.onloadeddata = function () {
      if (setupAudioSource(audioPlayer)) {
        audioPlayer.play().then(() => {
          isAudioPlaying = true;
          if (onZoomCamera) onZoomCamera(true);
          addTerminalMessage(`PLAYING DEMO TRACK: ${url.split('/').pop()}`);
          showNotification(`PLAYING: ${url.split('/').pop()}`);
        }).catch((e) => {
          console.warn('Play prevented:', e);
          addTerminalMessage('WARNING: AUDIO PLAYBACK PREVENTED BY BROWSER. CLICK PLAY TO START AUDIO.');
          showNotification('CLICK PLAY TO START AUDIO');
        });
      }
    };
    const filename = url.split('/').pop();
    document.getElementById('file-label').textContent = filename;
    addTerminalMessage(`LOADING AUDIO FROM URL: ${url.substring(0, 40)}...`);
    showNotification('AUDIO URL LOADED');
  } catch (error) {
    console.error('Audio URL error:', error);
    addTerminalMessage('ERROR: AUDIO URL PROCESSING FAILED.');
    showNotification('AUDIO URL ERROR');
  }
}

// TTS 專用播放（不改 file-label，不在 terminal 顯示 blob URL）
function playTTSAudio(url, label) {
  try {
    if (!isAudioInitialized && !initAudio()) return;
    ensureAudioContextStarted();
    const audioPlayer = createNewAudioElement();
    currentAudioSrc = url;
    audioPlayer.src = url;
    audioPlayer.onloadeddata = function () {
      if (setupAudioSource(audioPlayer)) {
        audioPlayer.play().then(() => {
          isAudioPlaying = true;
          if (onZoomCamera) onZoomCamera(true);
        }).catch((e) => {
          console.warn('TTS play prevented:', e);
        });
      }
    };
    audioPlayer.onerror = () => {
      console.error('TTS audio load error');
    };
  } catch (error) {
    console.error('TTS audio error:', error);
  }
}

// 音訊指標計算（frequencyData 已由呼叫端填充）
export function calculateAudioMetrics(audioSensitivity) {
  if (!audioAnalyser) return;

  let maxValue = 0;
  let maxIndex = 0;
  for (let i = 0; i < frequencyData.length; i++) {
    if (frequencyData[i] > maxValue) {
      maxValue = frequencyData[i];
      maxIndex = i;
    }
  }
  const sampleRate = audioContext.sampleRate;
  const peakFrequency = (maxIndex * sampleRate) / (audioAnalyser.frequencyBinCount * 2);

  let sum = 0;
  for (let i = 0; i < frequencyData.length; i++) sum += frequencyData[i];
  const amplitude = sum / (frequencyData.length * 255);

  // 更新 DOM
  /* [DISABLED] METRICS tab 暫時停用
  const peakEl = document.getElementById('peak-value');
  const ampEl = document.getElementById('amplitude-value');
  if (peakEl) peakEl.textContent = `${Math.round(peakFrequency)} HZ`;
  if (ampEl) ampEl.textContent = amplitude.toFixed(2);

  // 只更新音訊相關的 phase（~每 3 秒跳一次）
  if (Math.random() < 0.005) {
    const phases = ['π/4', 'π/2', 'π/6', '3π/4'];
    const phaseEl = document.getElementById('phase-value');
    if (phaseEl) phaseEl.textContent = phases[Math.floor(Math.random() * phases.length)];
  }
  */
}

// 音波 UI（audioData 已由呼叫端填充）
export function updateAudioWave(audioReactivity, audioSensitivity) {
  if (!audioAnalyser) return;
  let sum = 0;
  for (let i = 0; i < audioData.length; i++) {
    sum += Math.abs(audioData[i] - 128);
  }
  const average = sum / audioData.length;
  const normalizedAverage = average / audioData.length;
  const wave = document.getElementById('audio-wave');
  if (!wave) return;
  const scale = 1 + normalizedAverage * audioReactivity * (audioSensitivity / 5);
  wave.style.transform = `translate(-50%, -50%) scale(${scale})`;
  wave.style.borderColor = `rgba(255, 78, 66, ${0.1 + normalizedAverage * 0.3})`;
}

// 初始化音訊控制（按鈕 + 檔案上傳）
export function initAudioControls() {
  // 用戶互動時提前初始化 AudioContext（解決手機首次 TTS 無聲）
  window.addEventListener('user-interaction', () => {
    if (!isAudioInitialized) initAudio();
    ensureAudioContextStarted();
  }, { once: true });

  // TTS 播放事件（來自 chat.js，避免循環依賴）
  window.addEventListener('tts-play', async (e) => {
    const { url, label } = e.detail;
    if (!isAudioInitialized) initAudio();
    // 等待 resume 完成再播放
    if (audioContext && audioContext.state === 'suspended') {
      try { await audioContext.resume(); } catch {}
    }
    playTTSAudio(url, label);
  });

  document.querySelectorAll('.demo-track-btn').forEach((btn) => {
    btn.addEventListener('click', function () {
      if (!isAudioInitialized) initAudio();
      if (audioContext && audioContext.state === 'suspended') audioContext.resume();
      const url = this.dataset.url;
      currentAudioSrc = url;
      document.querySelectorAll('.demo-track-btn').forEach((b) => b.classList.remove('active'));
      this.classList.add('active');
      loadAudioFromURL(url);
    });
  });

  document.getElementById('file-btn')?.addEventListener('click', function () {
    if (!isAudioInitialized) initAudio();
    if (audioContext && audioContext.state === 'suspended') audioContext.resume();
    document.getElementById('audio-file-input').click();
  });

  document.getElementById('audio-file-input')?.addEventListener('change', function (e) {
    if (e.target.files.length > 0) initAudioFile(e.target.files[0]);
  });

  // 初始 audio player ended
  const initialPlayer = document.getElementById('audio-player');
  if (initialPlayer) {
    initialPlayer.addEventListener('ended', () => {
      isAudioPlaying = false;
      if (onZoomCamera) onZoomCamera(false);
      addTerminalMessage('AUDIO PLAYBACK COMPLETE.');
    });
  }

  // 點擊頁面自動啟用音訊
  document.addEventListener('click', function () {
    if (!isAudioInitialized) initAudio();
    else if (audioContext && audioContext.state === 'suspended') audioContext.resume();
  });
}

// 取得即時音訊等級（frequencyData 已由呼叫端填充）
export function getAudioLevel(audioSensitivity) {
  if (!audioAnalyser) return 0;
  let sum = 0;
  for (let i = 0; i < frequencyData.length; i++) sum += frequencyData[i];
  return ((sum / frequencyData.length / 255) * audioSensitivity) / 5;
}
