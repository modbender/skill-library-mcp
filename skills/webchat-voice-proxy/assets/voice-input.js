(function () {
  'use strict';

  // --- CSS Animations (injected once) ---
  const STYLE_ID = 'oc-voice-animations';
  if (!document.getElementById(STYLE_ID)) {
    const style = document.createElement('style');
    style.id = STYLE_ID;
    style.textContent = `
      @keyframes oc-pulse {
        0%   { box-shadow: 0 0 0 0 rgba(192,57,43,0.6); }
        70%  { box-shadow: 0 0 0 10px rgba(192,57,43,0); }
        100% { box-shadow: 0 0 0 0 rgba(192,57,43,0); }
      }
      @keyframes oc-pulse-purple {
        0%   { box-shadow: 0 0 0 0 rgba(142,68,173,0.7); }
        50%  { box-shadow: 0 0 0 12px rgba(142,68,173,0.3); }
        100% { box-shadow: 0 0 0 0 rgba(142,68,173,0); }
      }
      @keyframes oc-spin {
        0%   { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
      }
    `;
    document.head.appendChild(style);
  }

  const TRANSCRIBE_URL = location.port === '8443' ? '/transcribe' : 'http://127.0.0.1:18790/transcribe';

  // --- Auth: read gateway token from Control UI localStorage ---
  function getAuthToken() {
    try {
      const raw = localStorage.getItem('openclaw.control.settings.v1');
      if (!raw) return null;
      const settings = JSON.parse(raw);
      return (settings && typeof settings.token === 'string' && settings.token) ? settings.token : null;
    } catch (_) { return null; }
  }

  function getAuthHeaders() {
    const token = getAuthToken();
    const headers = { 'Content-Type': 'application/octet-stream' };
    if (token) headers['Authorization'] = 'Bearer ' + token;
    return headers;
  }
  const STORAGE_KEY = 'oc-voice-beep';
  const MODE_KEY = 'oc-voice-mode';
  const LANG_KEY = 'oc-voice-lang';
  let beepEnabled = localStorage.getItem(STORAGE_KEY) !== 'false'; // default: on
  let pttMode = localStorage.getItem(MODE_KEY) !== 'toggle'; // default: PTT

  // --- i18n ---
  const I18N = {
    en: {
      tooltip_ptt: "Hold to talk",
      tooltip_toggle: "Click to start/stop",
      tooltip_next_toggle: "Toggle mode",
      tooltip_next_ptt: "Push-to-Talk",
      tooltip_beep_off: "Disable beep",
      tooltip_beep_on: "Enable beep",
      tooltip_dblclick: "Double-click",
      tooltip_rightclick: "Right-click",
      toast_ptt: "Push-to-Talk",
      toast_toggle: "Toggle mode",
      toast_beep_on: "Beep enabled",
      toast_beep_off: "Beep disabled",
      placeholder_suffix: " \u2014 Voice: (Ctrl+Space Push-To-Talk, Ctrl+Shift+M start/stop recording, Ctrl+Shift+B start/stop live transcription [beta])",
      continuous_start: "\ud83c\udf99\ufe0f Continuous recording...",
      continuous_silence: "\u23f9 Silence detected",
      continuous_keyword: "\u23f9 Stop keyword detected",
      continuous_manual: "\u23f9 Stopped",
      continuous_edit: "\u270f\ufe0f Edit text...",
      continuous_sent: "\u2705 Sent",
      continuous_limit: "\u23f9 Max recording length reached"
    },
    de: {
      tooltip_ptt: "Gedr\u00fcckt halten zum Sprechen",
      tooltip_toggle: "Klick zum Starten/Stoppen",
      tooltip_next_toggle: "Klick-Modus",
      tooltip_next_ptt: "Push-to-Talk",
      tooltip_beep_off: "Beep ausschalten",
      tooltip_beep_on: "Beep anschalten",
      tooltip_dblclick: "Doppelklick",
      tooltip_rightclick: "Rechtsklick",
      toast_ptt: "Push-to-Talk",
      toast_toggle: "Klick-Modus",
      toast_beep_on: "Beep aktiviert",
      toast_beep_off: "Beep deaktiviert",
      placeholder_suffix: " \u2014 Sprache: (Strg+Leertaste Push-To-Talk, Strg+Umschalt+M Start/Stop Daueraufnahme, Strg+Umschalt+B Start/Stop Live-Transkription [Beta])",
      continuous_start: "\ud83c\udf99\ufe0f Daueraufnahme...",
      continuous_silence: "\u23f9 Stille erkannt",
      continuous_keyword: "\u23f9 Stop-Keyword erkannt",
      continuous_manual: "\u23f9 Gestoppt",
      continuous_edit: "\u270f\ufe0f Text bearbeiten...",
      continuous_sent: "\u2705 Gesendet",
      continuous_limit: "\u23f9 Maximale Aufnahmedauer erreicht"
    },
    zh: {
      tooltip_ptt: "\u6309\u4f4f\u8bf4\u8bdd",
      tooltip_toggle: "\u70b9\u51fb\u5f00\u59cb/\u505c\u6b62",
      tooltip_next_toggle: "\u70b9\u51fb\u6a21\u5f0f",
      tooltip_next_ptt: "\u6309\u4f4f\u8bf4\u8bdd\u6a21\u5f0f",
      tooltip_beep_off: "\u5173\u95ed\u63d0\u793a\u97f3",
      tooltip_beep_on: "\u5f00\u542f\u63d0\u793a\u97f3",
      tooltip_dblclick: "\u53cc\u51fb",
      tooltip_rightclick: "\u53f3\u952e",
      toast_ptt: "\u6309\u4f4f\u8bf4\u8bdd\u6a21\u5f0f",
      toast_toggle: "\u70b9\u51fb\u6a21\u5f0f",
      toast_beep_on: "\u63d0\u793a\u97f3\u5df2\u5f00\u542f",
      toast_beep_off: "\u63d0\u793a\u97f3\u5df2\u5173\u95ed",
      placeholder_suffix: " \u2014 \u8bed\u97f3\uff1a(Ctrl+\u7a7a\u683c \u6309\u4f4f\u8bf4\u8bdd\uff0cCtrl+Shift+M \u5f55\u97f3\uff0cCtrl+Shift+B \u5b9e\u65f6\u8f6c\u5f55)",
      continuous_start: "\ud83c\udf99\ufe0f \u8fde\u7eed\u5f55\u97f3...",
      continuous_silence: "\u23f9 \u68c0\u6d4b\u5230\u9759\u97f3",
      continuous_keyword: "\u23f9 \u68c0\u6d4b\u5230\u505c\u6b62\u5173\u952e\u8bcd",
      continuous_manual: "\u23f9 \u5df2\u505c\u6b62",
      continuous_edit: "\u270f\ufe0f \u7f16\u8f91\u6587\u672c...",
      continuous_sent: "\u2705 \u5df2\u53d1\u9001",
      continuous_limit: "\u23f9 \u5df2\u8fbe\u6700\u5927\u5f55\u97f3\u65f6\u957f"
    }
  };

  function getLang() {
    const override = localStorage.getItem(LANG_KEY);
    if (override && I18N[override]) return override;
    const nav = (navigator.language || 'en').slice(0, 2);
    return I18N[nav] ? nav : 'en';
  }

  function t(key) {
    return (I18N[getLang()] || I18N.en)[key] || I18N.en[key] || key;
  }
  const MIN_TEXT_CHARS = 2;
  const MIN_CONFIDENCE = 0.15;
  const MAX_NO_SPEECH = 0.95;

  let mediaRecorder = null;
  let audioChunks = [];
  let recording = false;
  let processing = false;
  let starting = false;
  let stream = null;
  let btn = null;
  let observer = null;
  let recordingStartedAt = 0;
  const MIN_RECORDING_MS = 250;
  let analyser = null;
  let audioCtx = null;
  let vuRAF = null;

  const MIC_ICON = `
    <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
      <path d="M9 8a3 3 0 1 1 6 0v4a3 3 0 1 1 -6 0z" />
      <path d="M5 10v2a7 7 0 0 0 14 0v-2" />
      <path d="M12 19v3" />
      <path d="M8 22h8" />
    </svg>
  `;

  const STOP_ICON = `
    <svg viewBox="0 0 24 24" width="24" height="24" fill="currentColor" aria-hidden="true">
      <rect x="5" y="5" width="14" height="14" rx="2.5" ry="2.5" />
    </svg>
  `;

  const HOURGLASS_ICON = `
    <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
      <path d="M7 4h10" />
      <path d="M7 20h10" />
      <path d="M8 4c0 4 4 4 4 8s-4 4-4 8" />
      <path d="M16 4c0 4-4 4-4 8s4 4 4 8" />
    </svg>
  `;

  let toastEl = null;
  let toastTimer = null;
  function showToast(text) {
    if (!toastEl) {
      toastEl = document.createElement('div');
      toastEl.style.cssText = 'position:fixed;bottom:80px;left:50%;transform:translateX(-50%);z-index:100000;background:rgba(20,20,24,.92);color:#fff;border:1px solid rgba(255,255,255,.15);border-radius:8px;padding:8px 16px;font-size:13px;pointer-events:none;opacity:0;transition:opacity .25s;white-space:nowrap;box-shadow:0 4px 12px rgba(0,0,0,.3);';
      document.body.appendChild(toastEl);
    }
    toastEl.textContent = text;
    toastEl.style.opacity = '1';
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => { if (toastEl) toastEl.style.opacity = '0'; }, 1500);
  }

  function getApp() {
    return document.querySelector('openclaw-app');
  }

  function sendMessage(text) {
    const app = getApp();
    if (!app || typeof app.handleSendChat !== 'function') return false;
    app.handleSendChat(text);
    return true;
  }

  function setIdleStyle() {
    if (!btn) return;
    btn.style.background = '#e52b31';
    btn.style.border = '1px solid #d3272f';
    btn.style.color = '#fff';
    btn.style.boxShadow = '0 1px 3px rgba(0,0,0,0.16)';
    btn.style.animation = 'none';
    btn.innerHTML = MIC_ICON;
  }

  function setRecordingStyle() {
    if (!btn) return;
    btn.style.background = '#c0392b';
    btn.style.border = '1px solid #ffffff';
    btn.style.color = '#fff';
    btn.style.boxShadow = '0 0 0 4px rgba(255,255,255,0.16), 0 1px 3px rgba(0,0,0,0.16)';
    btn.style.animation = 'none';
    btn.innerHTML = STOP_ICON;
  }

  function startVU() {
    if (!stream) return;
    try {
      audioCtx = new (window.AudioContext || window.webkitAudioContext)();
      const source = audioCtx.createMediaStreamSource(stream);
      analyser = audioCtx.createAnalyser();
      analyser.fftSize = 256;
      analyser.smoothingTimeConstant = 0.4;
      source.connect(analyser);
      const data = new Uint8Array(analyser.frequencyBinCount);
      function tick() {
        if (!recording || !analyser) return;
        analyser.getByteFrequencyData(data);
        let sum = 0;
        for (let i = 0; i < data.length; i++) sum += data[i];
        const avg = sum / data.length / 255;
        const level = Math.min(1, avg * 3);
        const spread = 4 + level * 22;
        const alpha = 0.2 + level * 0.6;
        if (btn) {
          btn.style.boxShadow = '0 0 0 ' + spread.toFixed(1) + 'px rgba(192,57,43,' + alpha.toFixed(2) + '), 0 1px 3px rgba(0,0,0,0.16)';
          btn.style.transform = 'scale(' + (1 + level * 0.25).toFixed(3) + ')';
        }
        vuRAF = requestAnimationFrame(tick);
      }
      vuRAF = requestAnimationFrame(tick);
    } catch (_) {}
  }

  function stopVU() {
    if (vuRAF) { cancelAnimationFrame(vuRAF); vuRAF = null; }
    if (audioCtx) { try { audioCtx.close(); } catch (_) {} audioCtx = null; }
    analyser = null;
    if (btn) btn.style.transform = 'scale(1)';
  }

  function setProcessingStyle() {
    if (!btn) return;
    btn.style.background = '#d6452f';
    btn.style.border = '1px solid #ffffff';
    btn.style.color = '#fff';
    btn.style.boxShadow = '0 1px 3px rgba(0,0,0,0.16)';
    btn.style.animation = 'none';
    btn.innerHTML = `<span style="display:inline-flex;animation:oc-spin 1.2s linear infinite">${HOURGLASS_ICON}</span>`;
  }

  function styleInline(sendBtn) {
    if (!btn) return;
    const h = Math.round(sendBtn?.getBoundingClientRect?.().height || 52);
    const radius = Math.max(10, Math.round(h * 0.22));
    btn.style.cssText = `
      width:${h}px;height:${h}px;border-radius:${radius}px;
      border:1px solid #d3272f;background:#e52b31;color:#fff;
      display:inline-flex;align-items:center;justify-content:center;
      cursor:pointer;user-select:none;flex:0 0 auto;margin:0 10px;
      box-shadow:0 1px 3px rgba(0,0,0,0.16);transition:all .15s ease;
    `;
  }

  function styleFloating() {
    if (!btn) return;
    btn.style.cssText = `
      position:fixed;bottom:24px;right:24px;z-index:99999;
      width:48px;height:48px;border-radius:50%;
      border:1px solid #d3272f;background:#e52b31;color:#fff;
      display:flex;align-items:center;justify-content:center;
      cursor:pointer;user-select:none;box-shadow:0 2px 8px rgba(0,0,0,.25);
    `;
  }

  let ignoreNextClick = false;
  let pttDown = false;
  let aborted = false;

  function updateButtonTitle() {
    if (!btn) return;
    const mode = pttMode ? t('tooltip_ptt') : t('tooltip_toggle');
    const nextMode = pttMode ? t('tooltip_next_toggle') : t('tooltip_next_ptt');
    const beep = beepEnabled ? t('tooltip_beep_off') : t('tooltip_beep_on');
    btn.title = `🎤 ${mode}\n${t('tooltip_dblclick')}: ${nextMode}\n${t('tooltip_rightclick')}: ${beep}`;
  }

  function switchMode() {
    pttMode = !pttMode;
    localStorage.setItem(MODE_KEY, pttMode ? 'ptt' : 'toggle');
    showToast(pttMode ? t('toast_ptt') : t('toast_toggle'));
    updateButtonTitle();
  }

  function bindButton(el) {
    if (!el || el.dataset.ocVoiceBound === '1') return;
    el.dataset.ocVoiceBound = '1';

    el.addEventListener('pointerdown', (e) => {
      if (e.button !== 0) return;
      e.preventDefault();
      e.stopPropagation();
      if (processing) return;

      if (pttMode) {
        // PTT: hold to record, immediate start
        if (!recording) {
          pttDown = true;
          ignoreNextClick = true;
          starting = true;
          setRecordingStyle();
          startRecording();
        }
      } else {
        // Toggle: pointerdown starts
        if (!recording) {
          ignoreNextClick = true;
          setTimeout(() => { ignoreNextClick = false; }, 500);
          starting = true;
          setRecordingStyle();
          startRecording();
        }
      }
    });

    el.addEventListener('pointerup', (e) => {
      if (e.button !== 0) return;
      if (pttMode && pttDown) {
        pttDown = false;
        ignoreNextClick = true;
        setTimeout(() => { ignoreNextClick = false; }, 300);
        if (recording) stopRecording();
      }
    });

    el.addEventListener('pointerleave', () => {
      if (pttMode && pttDown) {
        pttDown = false;
        if (recording) stopRecording();
      }
    });

    el.addEventListener('click', (e) => {
      e.preventDefault();
      e.stopPropagation();
      if (ignoreNextClick) {
        ignoreNextClick = false;
        return;
      }
      // Toggle mode: click to stop
      if (!pttMode && recording) stopRecording();
    });

    el.addEventListener('dblclick', (e) => {
      e.preventDefault();
      e.stopPropagation();
      pttDown = false;
      // Abort any running recording — flag ensures stop-handler discards audio
      if (recording) {
        aborted = true;
        if (mediaRecorder?.state === 'recording') {
          try { mediaRecorder.stop(); } catch (_) {}
        } else {
          // Recorder already stopped, clean up manually
          aborted = false;
          recording = false;
          mediaRecorder = null;
          audioChunks = [];
          stopVU();
          if (stream) { stream.getTracks().forEach((t) => t.stop()); stream = null; }
          setIdleStyle();
        }
      }
      if (!processing) switchMode();
    });

    el.addEventListener('contextmenu', (e) => {
      e.preventDefault();
      e.stopPropagation();
      beepEnabled = !beepEnabled;
      localStorage.setItem(STORAGE_KEY, beepEnabled ? 'true' : 'false');
      showToast(beepEnabled ? t('toast_beep_on') : t('toast_beep_off'));
      updateButtonTitle();
    });
  }

  function findSendButton() {
    return Array.from(document.querySelectorAll('button')).find((b) => /send/i.test((b.textContent || '').trim()));
  }

  function renderButton() {
    if (!btn) {
      btn = document.createElement('button');
      btn.id = 'oc-voice-btn';
      btn.type = 'button';
      btn.title = '';
      bindButton(btn);
    }

    const sendBtn = findSendButton();
    if (sendBtn && sendBtn.parentElement) {
      styleInline(sendBtn);
      if (btn.parentElement !== sendBtn.parentElement || btn.nextSibling !== sendBtn) {
        btn.remove();
        sendBtn.parentElement.insertBefore(btn, sendBtn);
      }
    } else if (!document.body.contains(btn)) {
      styleFloating();
      document.body.appendChild(btn);
    }

    if (continuousMode) setContinuousRecordingStyle();
    else if (recording) setRecordingStyle();
    else if (processing) setProcessingStyle();
    else setIdleStyle();
    updateButtonTitle();
  }

  async function sendToTranscribe(blob) {
    processing = true;
    setProcessingStyle();
    try {
      const resp = await fetch(TRANSCRIBE_URL, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: blob,
      });
      if (!resp.ok) throw new Error('HTTP ' + resp.status);
      const data = await resp.json();
      const text = (data.text || '').trim();
      const confidence = typeof data.confidence === 'number' ? data.confidence : null;
      const noSpeech = typeof data.no_speech_prob === 'number' ? data.no_speech_prob : null;

      if (!text) return;
      if (text.length < MIN_TEXT_CHARS) return;
      if (confidence !== null && confidence < MIN_CONFIDENCE) return;
      if (noSpeech !== null && noSpeech > MAX_NO_SPEECH) return;

      sendMessage(text);
    } catch (_) {
    } finally {
      processing = false;
      if (!recording) setIdleStyle();
    }
  }

  async function startRecording() {
    if (recording || processing) return;
    try {
      if (stream) {
        stream.getTracks().forEach((t) => t.stop());
        stream = null;
      }

      stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      audioChunks = [];

      const mimeType = MediaRecorder.isTypeSupported('audio/webm;codecs=opus')
        ? 'audio/webm;codecs=opus'
        : MediaRecorder.isTypeSupported('audio/ogg;codecs=opus')
          ? 'audio/ogg;codecs=opus' : '';

      mediaRecorder = new MediaRecorder(stream, mimeType ? { mimeType } : {});

      mediaRecorder.addEventListener('dataavailable', (e) => {
        if (e.data?.size > 0) audioChunks.push(e.data);
      });

      mediaRecorder.addEventListener('stop', () => {
        stopVU();
        if (stream) {
          stream.getTracks().forEach((t) => t.stop());
          stream = null;
        }
        recording = false;
        recordingStartedAt = 0;

        // If aborted (e.g. dblclick mode switch), discard everything
        if (aborted) {
          aborted = false;
          audioChunks = [];
          mediaRecorder = null;
          setIdleStyle();
          return;
        }

        const total = audioChunks.reduce((s, c) => s + c.size, 0);
        if (!audioChunks.length || total < 20) {
          mediaRecorder = null;
          setIdleStyle();
          return;
        }

        const blob = new Blob(audioChunks, { type: mediaRecorder?.mimeType || 'audio/webm' });
        audioChunks = [];
        mediaRecorder = null;
        sendToTranscribe(blob);
      }, { once: true });

      mediaRecorder.addEventListener('start', () => {
        recording = true;
        starting = false;
        recordingStartedAt = Date.now();
        setRecordingStyle();
        startVU();
        if (beepEnabled && audioCtx) {
          try {
            const osc = audioCtx.createOscillator();
            const gain = audioCtx.createGain();
            osc.type = 'sine';
            osc.frequency.value = 880;
            gain.gain.value = 0.15;
            osc.connect(gain);
            gain.connect(audioCtx.destination);
            osc.start();
            osc.stop(audioCtx.currentTime + 0.08);
          } catch (_) {}
        }
      }, { once: true });
      mediaRecorder.start();
    } catch (_) {
      recording = false;
      starting = false;
      mediaRecorder = null;
      setIdleStyle();
    }
  }

  function stopRecording() {
    if (!recording) return;

    const elapsed = Date.now() - recordingStartedAt;
    if (elapsed < MIN_RECORDING_MS) {
      setTimeout(() => {
        if (recording) stopRecording();
      }, MIN_RECORDING_MS - elapsed);
      return;
    }

    if (mediaRecorder?.state === 'recording') {
      try { mediaRecorder.requestData(); } catch (_) {}
      try { mediaRecorder.stop(); } catch (_) {
        recording = false;
        mediaRecorder = null;
        setIdleStyle();
      }
      return;
    }

    recording = false;
    mediaRecorder = null;
    if (stream) {
      stream.getTracks().forEach((t) => t.stop());
      stream = null;
    }
    setIdleStyle();
  }

  function toggle() {
    // Self-heal stale state: if UI thinks recording but recorder is gone/stopped
    if (recording && (!mediaRecorder || mediaRecorder.state !== 'recording')) {
      recording = false;
      mediaRecorder = null;
      setIdleStyle();
    }

    if (recording) stopRecording();
    else startRecording();
  }

  // --- Continuous Transcription Mode ---
  const CONTINUOUS_SILENCE_MS = 5000;    // stop after 5s silence
  const CONTINUOUS_CHUNK_MS = 1000;      // transcribe every 1s
  const CONTINUOUS_MAX_CHUNKS = 120;     // max ~2 minutes of chunks, then auto-stop
  const CONTINUOUS_AUTOSEND_MS = 2000;   // auto-send after 2s review
  const CONTINUOUS_STOP_KEYWORDS = ['stop hugo', 'stopp hugo', 'hugo stop', 'hugo stopp', 'stop hue', 'stopp hue', 'stop huo', 'stopp huo', 'stop hubo', 'stopp hubo'];
  const SILENCE_THRESHOLD = 0.02;        // VU level below this = silence

  let continuousMode = false;
  let continuousStream = null;
  let continuousRecorder = null;
  let continuousChunks = [];
  let continuousText = '';
  let continuousTranscribeTimer = null;
  let continuousKeywordTimer = null;
  let continuousSilenceStart = 0;
  let continuousAutoSendTimer = null;
  let continuousAnalyser = null;
  let continuousAudioCtx = null;
  let continuousVuRAF = null;
  let continuousUserClicked = false;
  let continuousStopped = false;
  let continuousSent = false;

  function getTextarea() {
    return document.querySelector('textarea');
  }

  function setTextareaValue(text) {
    const ta = getTextarea();
    if (!ta) return;
    // Use native setter to trigger framework reactivity
    const nativeSetter = Object.getOwnPropertyDescriptor(HTMLTextAreaElement.prototype, 'value')?.set;
    if (nativeSetter) {
      nativeSetter.call(ta, text);
    } else {
      ta.value = text;
    }
    ta.dispatchEvent(new Event('input', { bubbles: true }));
  }

  const REC_ICON = `
    <svg viewBox="0 0 24 24" width="22" height="22" fill="currentColor" aria-hidden="true">
      <circle cx="12" cy="10" r="4" fill="#ff4444"/>
      <text x="12" y="21" text-anchor="middle" font-size="7" font-weight="bold" fill="white" font-family="sans-serif">REC</text>
    </svg>
  `;

  function setContinuousRecordingStyle() {
    if (!btn) return;
    btn.style.background = '#8e44ad';
    btn.style.border = '2px solid #ffffff';
    btn.style.color = '#fff';
    btn.style.boxShadow = '0 0 0 4px rgba(142,68,173,0.4), 0 1px 3px rgba(0,0,0,0.16)';
    btn.style.animation = 'oc-pulse-purple 1.5s ease-in-out infinite';
    btn.innerHTML = REC_ICON;
  }

  function setContinuousReviewStyle() {
    if (!btn) return;
    btn.style.background = '#27ae60';
    btn.style.border = '1px solid #ffffff';
    btn.style.color = '#fff';
    btn.style.boxShadow = '0 1px 3px rgba(0,0,0,0.16)';
    btn.style.animation = 'none';
    btn.innerHTML = MIC_ICON;
  }

  function startContinuousVU() {
    if (!continuousStream) return;
    try {
      continuousAudioCtx = new (window.AudioContext || window.webkitAudioContext)();
      const source = continuousAudioCtx.createMediaStreamSource(continuousStream);
      continuousAnalyser = continuousAudioCtx.createAnalyser();
      continuousAnalyser.fftSize = 256;
      continuousAnalyser.smoothingTimeConstant = 0.4;
      source.connect(continuousAnalyser);
      const data = new Uint8Array(continuousAnalyser.frequencyBinCount);

      function tick() {
        if (!continuousMode || !continuousAnalyser) return;
        continuousAnalyser.getByteFrequencyData(data);
        let sum = 0;
        for (let i = 0; i < data.length; i++) sum += data[i];
        const avg = sum / data.length / 255;
        const level = Math.min(1, avg * 3);

        // VU animation on button — only scale, keep pulse animation for boxShadow
        if (btn) {
          btn.style.transform = 'scale(' + (1 + level * 0.25).toFixed(3) + ')';
        }

        // Silence detection
        if (level < SILENCE_THRESHOLD) {
          if (!continuousSilenceStart) continuousSilenceStart = Date.now();
          const silentMs = Date.now() - continuousSilenceStart;
          if (silentMs >= CONTINUOUS_SILENCE_MS) {
            stopContinuous('silence');
            return;
          }
        } else {
          continuousSilenceStart = 0;
        }

        continuousVuRAF = requestAnimationFrame(tick);
      }
      continuousVuRAF = requestAnimationFrame(tick);
    } catch (_) {}
  }

  function stopContinuousVU() {
    if (continuousVuRAF) { cancelAnimationFrame(continuousVuRAF); continuousVuRAF = null; }
    if (continuousAudioCtx) { try { continuousAudioCtx.close(); } catch (_) {} continuousAudioCtx = null; }
    continuousAnalyser = null;
    if (btn) btn.style.transform = 'scale(1)';
  }

  let continuousKeywordPending = false;

  // Fast keyword check: only last 1-2 chunks (~1-2s audio)
  async function checkKeywordChunk() {
    if (continuousStopped || continuousKeywordPending) return;
    // Take only the last 2 chunks for fast keyword detection
    const recent = continuousChunks.slice(-2);
    if (!recent.length) return;
    const blob = new Blob(recent, { type: continuousRecorder?.mimeType || 'audio/webm' });
    continuousKeywordPending = true;
    try {
      const resp = await fetch(TRANSCRIBE_URL, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: blob,
      });
      if (!resp.ok) return;
      const data = await resp.json();
      const text = (data.text || '').trim();
      if (!text) return;
      const lower = text.toLowerCase().replace(/[.,!?;:'"]/g, '');
      for (const kw of CONTINUOUS_STOP_KEYWORDS) {
        if (lower.includes(kw)) {
          stopContinuous('keyword');
          return;
        }
      }
    } catch (_) {
    } finally {
      continuousKeywordPending = false;
    }
  }

  // Full transcription: all accumulated chunks for display
  async function transcribeContinuousChunk() {
    if (!continuousChunks.length || continuousStopped) return;
    const blob = new Blob(continuousChunks, { type: continuousRecorder?.mimeType || 'audio/webm' });
    try {
      const resp = await fetch(TRANSCRIBE_URL, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: blob,
      });
      if (!resp.ok || continuousStopped) return;
      const data = await resp.json();
      const text = (data.text || '').trim();
      const noSpeech = typeof data.no_speech_prob === 'number' ? data.no_speech_prob : null;
      if (!text || text.length < MIN_TEXT_CHARS) return;
      if (noSpeech !== null && noSpeech > MAX_NO_SPEECH) return;
      if (continuousStopped) return;

      // Remove any stop keywords from displayed text
      let cleaned = text;
      const lower = text.toLowerCase().replace(/[.,!?;:'"]/g, '');
      for (const kw of CONTINUOUS_STOP_KEYWORDS) {
        if (lower.includes(kw)) {
          const kwPattern = new RegExp('[.,!?;:\'"\\s]*' + kw.replace(/\s+/g, '[.,!?;:\'"\\s]+') + '[.,!?;:\'"\\s]*', 'gi');
          cleaned = cleaned.replace(kwPattern, ' ').trim();
        }
      }

      continuousText = cleaned;
      setTextareaValue(cleaned);
    } catch (_) {}
  }

  async function startContinuous() {
    if (continuousMode || recording || processing) return;

    try {
      continuousStream = await navigator.mediaDevices.getUserMedia({ audio: true });
    } catch (_) { return; }

    continuousMode = true;
    continuousText = '';
    continuousChunks = [];
    continuousSilenceStart = 0;
    continuousUserClicked = false;
    continuousStopped = false;
    continuousSent = false;

    const mimeType = MediaRecorder.isTypeSupported('audio/webm;codecs=opus')
      ? 'audio/webm;codecs=opus'
      : MediaRecorder.isTypeSupported('audio/ogg;codecs=opus')
        ? 'audio/ogg;codecs=opus' : '';

    continuousRecorder = new MediaRecorder(continuousStream, mimeType ? { mimeType } : {});

    continuousRecorder.addEventListener('dataavailable', (e) => {
      if (e.data?.size > 0) {
        continuousChunks.push(e.data);
        if (continuousChunks.length >= CONTINUOUS_MAX_CHUNKS) {
          stopContinuous('limit');
        }
      }
    });

    continuousRecorder.addEventListener('stop', () => {
      // Final transcription with all chunks (skip if already sent)
      if (continuousChunks.length && !continuousSent) {
        const blob = new Blob(continuousChunks, { type: continuousRecorder?.mimeType || 'audio/webm' });
        fetch(TRANSCRIBE_URL, {
          method: 'POST',
          headers: getAuthHeaders(),
          body: blob,
        }).then(r => r.json()).then(data => {
          const text = (data.text || '').trim();
          if (text && text.length >= MIN_TEXT_CHARS) {
            // Remove stop keywords (with surrounding punctuation)
            let cleaned = text;
            for (const kw of CONTINUOUS_STOP_KEYWORDS) {
              const kwPattern = new RegExp('[.,!?;:\'"\\s]*' + kw.replace(/\s+/g, '[.,!?;:\'"\\s]+') + '[.,!?;:\'"\\s]*', 'gi');
              cleaned = cleaned.replace(kwPattern, ' ').trim();
            }
            if (cleaned) {
              continuousText = cleaned;
              setTextareaValue(cleaned);
            }
          }
          startReviewPhase();
        }).catch(() => {
          startReviewPhase();
        });
      } else {
        startReviewPhase();
      }
    }, { once: true });

    setContinuousRecordingStyle();
    showToast(t('continuous_start'));
    startContinuousVU();

    // Start recording with timeslice for periodic chunks
    continuousRecorder.start(CONTINUOUS_CHUNK_MS);

    // Periodic full transcription (for text display)
    continuousTranscribeTimer = setInterval(() => {
      if (continuousMode && continuousChunks.length && !continuousStopped) {
        transcribeContinuousChunk();
      }
    }, CONTINUOUS_CHUNK_MS * 3);

    // Fast keyword detection (every chunk, lightweight)
    continuousKeywordTimer = setInterval(() => {
      if (continuousMode && continuousChunks.length && !continuousStopped) {
        checkKeywordChunk();
      }
    }, CONTINUOUS_CHUNK_MS + 200);

    // Beep
    if (beepEnabled && continuousAudioCtx) {
      try {
        const osc = continuousAudioCtx.createOscillator();
        const gain = continuousAudioCtx.createGain();
        osc.type = 'sine';
        osc.frequency.value = 660;
        gain.gain.value = 0.12;
        osc.connect(gain);
        gain.connect(continuousAudioCtx.destination);
        osc.start();
        osc.stop(continuousAudioCtx.currentTime + 0.15);
      } catch (_) {}
    }
  }

  function stopContinuous(reason) {
    if (!continuousMode && !continuousStopped) return;
    continuousMode = false;
    continuousStopped = true;

    if (continuousTranscribeTimer) {
      clearInterval(continuousTranscribeTimer);
      continuousTranscribeTimer = null;
    }
    if (continuousKeywordTimer) {
      clearInterval(continuousKeywordTimer);
      continuousKeywordTimer = null;
    }

    stopContinuousVU();

    if (continuousRecorder?.state === 'recording') {
      try { continuousRecorder.requestData(); } catch (_) {}
      try { continuousRecorder.stop(); } catch (_) {}
    } else {
      // Recorder already stopped
      startReviewPhase();
    }

    if (continuousStream) {
      continuousStream.getTracks().forEach((t) => t.stop());
      continuousStream = null;
    }

    if (reason === 'silence') showToast(t('continuous_silence'));
    else if (reason === 'keyword') showToast(t('continuous_keyword'));
    else if (reason === 'manual') showToast(t('continuous_manual'));
    else if (reason === 'limit') showToast(t('continuous_limit'));
  }

  function startReviewPhase() {
    if (!continuousText) {
      setIdleStyle();
      continuousRecorder = null;
      continuousChunks = [];
      return;
    }

    setContinuousReviewStyle();
    continuousUserClicked = false;

    // Listen for click into textarea → cancel auto-send
    const ta = getTextarea();
    function onFocus() {
      continuousUserClicked = true;
      if (continuousAutoSendTimer) {
        clearTimeout(continuousAutoSendTimer);
        continuousAutoSendTimer = null;
      }
      showToast(t('continuous_edit'));
      setIdleStyle();
      if (ta) ta.removeEventListener('focus', onFocus);
      if (ta) ta.removeEventListener('click', onFocus);
    }
    if (ta) {
      ta.addEventListener('focus', onFocus, { once: true });
      ta.addEventListener('click', onFocus, { once: true });
    }

    // Auto-send after review period
    continuousAutoSendTimer = setTimeout(() => {
      continuousAutoSendTimer = null;
      if (!continuousUserClicked && continuousText && !continuousSent) {
        continuousSent = true;
        sendMessage(continuousText);
        setTextareaValue('');
        showToast(t('continuous_sent'));
      }
      continuousText = '';
      continuousChunks = [];
      continuousRecorder = null;
      setIdleStyle();
      if (ta) {
        ta.removeEventListener('focus', onFocus);
        ta.removeEventListener('click', onFocus);
      }
    }, CONTINUOUS_AUTOSEND_MS);
  }

  function toggleContinuous() {
    if (continuousMode) {
      stopContinuous('manual');
    } else {
      // If in normal recording, stop it first
      if (recording) {
        aborted = true;
        if (mediaRecorder?.state === 'recording') {
          try { mediaRecorder.stop(); } catch (_) {}
        }
        recording = false;
      }
      startContinuous();
    }
  }

  // --- Keyboard shortcuts ---
  let spaceDown = false;

  function isTextInput(el) {
    if (!el) return false;
    const tag = el.tagName;
    if (tag === 'INPUT' || tag === 'TEXTAREA') return true;
    if (el.isContentEditable) return true;
    return false;
  }

  document.addEventListener('keydown', (e) => {
    // Ctrl+Shift+M → toggle recording (simple start/stop)
    if (e.ctrlKey && e.shiftKey && e.key === 'M') {
      e.preventDefault();
      toggle();
      return;
    }
    // Ctrl+Shift+B → continuous transcription mode
    if (e.ctrlKey && e.shiftKey && e.key === 'B') {
      e.preventDefault();
      toggleContinuous();
      return;
    }
    // Ctrl+Space PTT (hold to talk) — works even when text field is focused
    if (e.ctrlKey && !e.shiftKey && e.code === 'Space' && !e.repeat) {
      e.preventDefault();
      e.stopPropagation();
      if (!recording && !processing) {
        spaceDown = true;
        startRecording();
      }
    }
  });

  document.addEventListener('keyup', (e) => {
    if (e.code === 'Space' && spaceDown) {
      e.preventDefault();
      spaceDown = false;
      if (recording) stopRecording();
    }
  });

  const PLACEHOLDER_MARKER = '\u2014 Voice:';
  const PLACEHOLDER_MARKER_DE = '\u2014 Sprache:';
  const PLACEHOLDER_MARKER_ZH = '\u2014 \u8bed\u97f3';

  function patchPlaceholder() {
    const ta = document.querySelector('textarea');
    if (!ta) return;
    const current = ta.placeholder || '';
    // Already patched?
    if (current.includes(PLACEHOLDER_MARKER) || current.includes(PLACEHOLDER_MARKER_DE) || current.includes(PLACEHOLDER_MARKER_ZH)) return;
    // No base placeholder yet?
    if (!current) return;
    ta.placeholder = current + t('placeholder_suffix');
  }

  function boot() {
    renderButton();
    patchPlaceholder();
    let queued = false;
    observer = new MutationObserver(() => {
      if (recording || processing || starting || continuousMode) return;
      if (queued) return;
      queued = true;
      requestAnimationFrame(() => {
        queued = false;
        renderButton();
        patchPlaceholder();
      });
    });
    observer.observe(document.body, { childList: true, subtree: true });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => setTimeout(boot, 500));
  } else {
    setTimeout(boot, 500);
  }
})();
