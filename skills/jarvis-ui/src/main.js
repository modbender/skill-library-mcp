// ── OpenClaw JARVIS UI — 主入口 ──

// 設定載入（最先）
import { loadConfig } from './config/config-loader.js';
import { initTheme } from './config/theme.js';

// 核心
import { initScene, animateScene, onWindowResize, zoomCameraForAudio, setDistortion, setResolution, resetAnomaly, getOrbScreenPosition } from './core/scene.js';
import { initAudio, initAudioControls, getAnalyser, getAudioData, getFrequencyData, getAudioLevel, calculateAudioMetrics, updateAudioWave, setZoomCallback } from './core/audio.js';
import { initFloatingParticles } from './core/particles.js';

// 元件
import { initChat, updateUserActivity } from './components/chat.js';
import { showNotification } from './components/notifications.js';
import { initSystemMonitor } from './components/system-monitor.js';
import { initTabs } from './components/tabs.js';
import { initTasks } from './components/tasks.js';
import { initSkills } from './components/skills.js';
import { initMemory } from './components/memory.js';
import { initSchedule } from './components/schedule.js';
import { initControls, setCallbacks, getAudioReactivity, getAudioSensitivity } from './components/controls.js';
import { initSpectrumCollapse, drawSpectrumAnalyzer, drawCircularVisualizer, drawWaveform, initVisualizers, resizeAllCanvases } from './components/spectrum.js';
import { setupPreloader } from './components/preloader.js';
import { initDraggablePanels } from './components/draggable.js';
import { initTimestamp } from './components/timestamp.js';
import { initOrbMessages } from './components/orb-messages.js';
import { initThoughtStream } from './components/thought-stream.js';
import { initMobileToolbar } from './components/mobile-toolbar.js';
import { initPowerSave, isPowerSave } from './components/powersave.js';

document.addEventListener('DOMContentLoaded', async function () {
  // 載入設定
  const config = await loadConfig();
  
  // 初始化主題系統（最早執行，確保 CSS 變數正確）
  initTheme();

  // 動態更新 HTML 中的個人化文字
  document.title = config.name || 'JARVIS';
  const agentName = config.agent?.name || 'JARVIS';
  const chatLabel = document.querySelector('.terminal-panel.chat-panel .terminal-header span');
  if (chatLabel) chatLabel.textContent = `${agentName} CHAT`;

  // 設定 agent prefix CSS 變數
  const emoji = config.agent?.emoji || '⚡';
  document.documentElement.style.setProperty('--agent-prefix', `"${agentName} ${emoji} "`);

  // 載入畫面
  setupPreloader();

  // 元件初始化
  initChat();
  initTabs();
  initTasks();
  initSkills();
  initMemory();
  initSchedule();
  initControls();
  initPowerSave();
  initSpectrumCollapse();
  initSystemMonitor();
  initVisualizers();
  initTimestamp();
  initAudioControls();

  // 控制滑桿回呼（連結場景）
  setCallbacks({
    onDistortion: setDistortion,
    onResolution: setResolution,
  });

  // 音訊 → 場景 zoom 回呼
  setZoomCallback(zoomCameraForAudio);

  // Orb 狀態文字（agent-state → #orb-status）
  const orbStatus = document.getElementById('orb-status');
  if (orbStatus) {
    const labels = { idle: 'IDLE · 待命中', thinking: 'THINKING · 思考中...', responding: 'RESPONDING · 回覆中...' };
    window.addEventListener('agent-state', (e) => {
      orbStatus.textContent = labels[e.detail] || e.detail.toUpperCase();
      orbStatus.className = 'scanner-id state-' + (e.detail || 'idle');

      // 狀態視覺回饋：掃描線速度 + 粒子活躍度
      const scannerLine = document.querySelector('.scanner-line');
      const scannerFrame = document.querySelector('.scanner-frame');
      if (scannerLine) {
        switch (e.detail) {
          case 'thinking':
            scannerLine.style.animationDuration = '1.5s';
            scannerFrame?.classList.add('state-active');
            break;
          case 'responding':
            scannerLine.style.animationDuration = '2.5s';
            scannerFrame?.classList.add('state-active');
            break;
          default:
            scannerLine.style.animationDuration = '4s';
            scannerFrame?.classList.remove('state-active');
        }
      }
    });
  }

  // Orb 右側 meta（channel + 訊息數）
  const orbMeta = document.getElementById('orb-meta');
  if (orbMeta) {
    let msgCount = 0;
    let channelName = '';

    const updateMeta = () => {
      orbMeta.textContent = channelName
        ? `${channelName}${msgCount ? ` · ${msgCount} MSGS` : ''}`
        : (msgCount ? `${msgCount} MSGS` : '');
    };

    // 初始化：從 server 拿 channel + 今日計數
    fetch('/api/status').then(r => r.json()).then(d => {
      channelName = (d.channel || '').toUpperCase();
      msgCount = d.msgCount || 0;
      updateMeta();
    }).catch(() => {});

    // 每次發訊息後更新計數
    window.addEventListener('agent-state', (e) => {
      if (e.detail === 'thinking') { msgCount++; updateMeta(); }
    });
  }

  // 使用者活動追蹤
  document.addEventListener('mousemove', updateUserActivity);
  document.addEventListener('keydown', updateUserActivity);

  // 載入完成後啟動
  const loadingOverlay = document.getElementById('loading-overlay');
  setTimeout(() => {
    loadingOverlay.style.opacity = 0;
    setTimeout(() => {
      loadingOverlay.style.display = 'none';
      initAudio();
      initFloatingParticles();
      initDraggablePanels();
      initOrbMessages(getOrbScreenPosition);
      initThoughtStream();
      initMobileToolbar();
    }, 500);
  }, 3000);

  // Three.js 場景
  initScene();
  
  // 暴露 resetAnomaly 供 Controls 使用
  window.__jarvisResetAnomaly = resetAnomaly;
  
  // 重新觸發主題，確保 Three.js 顏色同步
  initTheme();

  // 視窗大小變更
  window.addEventListener('resize', () => {
    onWindowResize(resizeAllCanvases);
  });

  // 主動畫循環
  let lastFrameTime = 0;
  function animate(now) {
    requestAnimationFrame(animate);

    // 頁面隱藏時完全暫停
    if (window.__jarvisHiddenPause?.()) return;

    // 省電模式：限制 15fps
    if (isPowerSave()) {
      if (now - lastFrameTime < 66) return; // ~15fps
      lastFrameTime = now;
    }

    const analyser = getAnalyser();
    const frequencyData = getFrequencyData();
    const audioData = getAudioData();
    const audioSensitivity = getAudioSensitivity();
    const audioReactivity = getAudioReactivity();

    // 音訊視覺化（僅在有分析器且非省電時）
    let audioLevel = 0;
    if (analyser && !isPowerSave()) {
      // 先填充數據（一幀只讀一次）
      analyser.getByteFrequencyData(frequencyData);
      analyser.getByteTimeDomainData(audioData);
      audioLevel = getAudioLevel(audioSensitivity);  // 使用已填充的 frequencyData
      drawCircularVisualizer(frequencyData, audioSensitivity, audioReactivity);
      drawSpectrumAnalyzer(frequencyData, audioSensitivity);
      updateAudioWave(audioReactivity, audioSensitivity);
      calculateAudioMetrics(audioSensitivity);
    }

    // 波形圖（省電時不畫）
    if (!isPowerSave()) {
      drawWaveform(analyser ? audioData : null);
    }

    // 3D 場景
    const rotationSpeed = parseFloat(document.getElementById('rotation-slider')?.value || 1);
    animateScene(audioLevel, rotationSpeed, audioReactivity);
  }
  animate(0);

  // 1. 頁面切背景自動暫停渲染
  let hiddenPause = false;
  document.addEventListener('visibilitychange', () => {
    hiddenPause = document.hidden;
  });
  // 暴露給 animate loop
  window.__jarvisHiddenPause = () => hiddenPause;
});

// PWA Service Worker 註冊
if ('serviceWorker' in navigator) {
  navigator.serviceWorker.register('/sw.js').catch(() => {});
}
