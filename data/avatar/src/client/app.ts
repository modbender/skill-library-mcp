/**
 * OpenClaw Avatar - Client Application
 *
 * Handles the browser-side avatar rendering, speech recognition,
 * and user interaction.
 */

import { SimliClient } from 'simli-client';

// Types
interface ClientConfig {
  app: {
    name: string;
    port: number;
  };
  avatars: Array<{
    id: string;
    name: string;
    faceId: string;
    voiceId: string;
    default?: boolean;
    zoom?: number;
    top?: number;
  }>;
  languages: Array<{
    code: string;
    name: string;
    flag?: string;
    default?: boolean;
  }>;
  fillers: {
    [lang: string]: {
      [category: string]: string[];
    };
  };
  simliApiKey: string;
}

interface ChatResponse {
  spoken: string;
  detail: string | null;
}

declare global {
  interface Window {
    avatarLang: string;
    marked: {
      parse(text: string): string;
    };
    SpeechRecognition: typeof SpeechRecognition;
    webkitSpeechRecognition: typeof SpeechRecognition;
  }
}

// DOM elements
const statusEl = document.getElementById('status') as HTMLElement;
const statusDot = document.getElementById('statusDot') as HTMLElement;
const msgEl = document.getElementById('msg') as HTMLInputElement;
const sendBtn = document.getElementById('send') as HTMLButtonElement;
const videoEl = document.getElementById('simli-video') as HTMLVideoElement;
const audioEl = document.getElementById('simli-audio') as HTMLAudioElement;
const spokenTextEl = document.getElementById('spoken-text') as HTMLElement;
const detailContentEl = document.getElementById('detail-content') as HTMLElement;
const thinkingOverlay = document.getElementById('thinking-overlay') as HTMLElement;
const thinkingGlow = document.getElementById('thinking-glow') as HTMLElement;
const sendSlackBtn = document.getElementById('send-slack') as HTMLButtonElement;
const settingsPage = document.getElementById('settings-page') as HTMLElement;
const langOptions = document.getElementById('lang-options') as HTMLElement;
const avatarOptions = document.getElementById('avatar-options') as HTMLElement;
const appNameEl = document.getElementById('app-name') as HTMLElement;

// State
let simli: SimliClient | null = null;
let audioUnlocked = false;
let clientConfig: ClientConfig | null = null;
let currentFaceId: string = '';
let currentVoiceId: string = '';

function setStatus(text: string, state: 'ready' | 'thinking' | 'speaking' = 'ready'): void {
  statusEl.textContent = text;
  statusDot.className = 'dot';
  if (state === 'thinking') statusDot.classList.add('thinking');
  if (state === 'speaking') statusDot.classList.add('speaking');

  if (state === 'thinking') {
    thinkingOverlay.classList.add('active');
    thinkingGlow.classList.add('active');
  } else {
    thinkingOverlay.classList.remove('active');
    thinkingGlow.classList.remove('active');
  }
}

// --- Load configuration ---

async function loadClientConfig(): Promise<ClientConfig> {
  const res = await fetch('/api/client-config');
  if (!res.ok) throw new Error('Failed to load config');
  return res.json();
}

// --- Ask Avatar ---

async function askAvatar(message: string): Promise<ChatResponse> {
  const res = await fetch('/api/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message, lang: window.avatarLang || 'en-US' }),
  });
  if (!res.ok) throw new Error(`Chat error: ${res.status}`);
  return res.json();
}

// --- Audio unlock ---

async function unlockAudio(): Promise<void> {
  if (audioUnlocked) return;
  try {
    const ctx = new AudioContext();
    await ctx.resume();
    ctx.close();
    audioEl.muted = false;
    await audioEl.play().catch(() => {});
    audioUnlocked = true;
  } catch {
    // Ignore
  }
}

// --- Simli ---

async function initSimli(): Promise<void> {
  if (!clientConfig) throw new Error('Config not loaded');

  simli = new SimliClient();

  simli.Initialize({
    apiKey: clientConfig.simliApiKey,
    faceID: currentFaceId,
    handleSilence: true,
    maxSessionLength: 3600,
    maxIdleTime: 600,
    videoRef: videoEl,
    audioRef: audioEl,
    enableConsoleLogs: false,
  });

  simli.on('connected', () => console.log('Simli connected'));

  setStatus('Starting...', 'thinking');
  await simli.start();
  setStatus('Ready', 'ready');
}

// --- TTS ---

async function fetchTTSAudio(text: string): Promise<Uint8Array> {
  const res = await fetch('/api/tts', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      text,
      lang: window.avatarLang || 'en-US',
      voiceId: currentVoiceId,
    }),
  });
  if (!res.ok) throw new Error(`TTS error: ${res.status}`);
  return new Uint8Array(await res.arrayBuffer());
}

function sendAudioToSimli(pcm16Data: Uint8Array): void {
  if (!simli) return;
  const CHUNK = 4096;
  for (let i = 0; i < pcm16Data.length; i += CHUNK) {
    simli.sendAudioData(pcm16Data.slice(i, i + CHUNK));
  }
}

// --- Fillers ---

function pickFiller(text: string): string {
  if (!clientConfig) return 'One moment...';

  const t = text.toLowerCase();
  let key = 'default';

  if (t.includes('email') || t.includes('inbox')) key = 'email';
  else if (t.includes('calendar') || t.includes('schedule') || t.includes('meeting')) {
    key = t.includes('pipeline') ? 'pipeline' : t.includes('meeting') ? 'meetings' : 'calendar';
  } else if (t.includes('hubspot')) key = 'hubspot';
  else if (t.includes('notion')) key = 'notion';
  else if (t.includes('slack') || t.includes('message') || t.includes('mention')) key = 'slack';
  else if (t.includes('customer') || t.includes('health score')) key = 'customers';
  else if (t.includes('pipeline') || t.includes('deal')) key = 'pipeline';
  else if (t.includes('briefing') || t.includes('brief')) key = 'brief';
  else if (t.includes('follow-up') || t.includes('followup') || t.includes('overdue')) key = 'followups';
  else if (t.includes('churn') || t.includes('at risk')) key = 'churn';
  else if (t.includes('prep')) key = 'prep';

  const lang = window.avatarLang || 'en-US';
  const fillers = clientConfig.fillers[lang] || clientConfig.fillers['en-US'] || {};
  const arr = fillers[key] || fillers['default'] || ['One moment...'];
  return arr[Math.floor(Math.random() * arr.length)];
}

// --- Main flow ---

async function handleSend(): Promise<void> {
  const text = msgEl.value.trim();
  console.log('handleSend called, text:', text, 'sendBtn.disabled:', sendBtn.disabled);
  setStatus(`Sending: "${text.substring(0, 20)}..."`, 'thinking');
  if (!text) return;

  msgEl.value = '';
  sendBtn.disabled = true;
  detailContentEl.innerHTML = '';
  setStatus('Thinking...', 'thinking');

  try {
    setStatus('Thinking...', 'thinking');

    const filler = pickFiller(text);

    const fillerPromise = fetchTTSAudio(filler)
      .then((pcm) => {
        sendAudioToSimli(pcm);
        return (pcm.length / 2 / 16000) * 1000;
      })
      .catch((e) => {
        console.warn('Filler TTS failed:', e);
        return 0;
      });

    const responsePromise = askAvatar(text);

    const fillerDuration = await fillerPromise;
    const [{ spoken, detail }] = await Promise.all([
      responsePromise,
      new Promise((r) => setTimeout(r, fillerDuration + 300)),
    ]);

    setStatus('Working...', 'thinking');

    if (detail) {
      detailContentEl.innerHTML = window.marked.parse(detail);
      sendSlackBtn.style.display = 'flex';
      sendSlackBtn.dataset.text = detail;
    } else {
      sendSlackBtn.style.display = 'none';
    }

    const spokenText = spoken || 'Here you go.';
    setStatus('Speaking...', 'speaking');
    const pcmData = await fetchTTSAudio(spokenText);
    sendAudioToSimli(pcmData);

    const durationMs = (pcmData.length / 2 / 16000) * 1000;
    setTimeout(() => {
      setStatus('Ready', 'ready');
      fetch('/api/speaking-done', { method: 'POST' }).catch(() => {});
    }, durationMs + 500);
  } catch (err) {
    console.error(err);
    setStatus('Error', 'ready');
    spokenTextEl.textContent = `Error: ${(err as Error).message}`;
  } finally {
    sendBtn.disabled = false;
    msgEl.focus();
  }
}

sendBtn.addEventListener('click', handleSend);

sendSlackBtn.addEventListener('click', async () => {
  const text = sendSlackBtn.dataset.text;
  if (!text) return;
  sendSlackBtn.disabled = true;
  try {
    await fetch('/api/send-slack', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text }),
    });
    sendSlackBtn.style.background = '#10b981';
    setTimeout(() => {
      sendSlackBtn.style.background = '';
      sendSlackBtn.disabled = false;
    }, 2000);
  } catch (e) {
    console.error('Slack send failed:', e);
    sendSlackBtn.disabled = false;
  }
});

msgEl.addEventListener('keydown', (e) => {
  if (e.key === 'Enter') handleSend();
});

// --- Stream Deck events ---

function initStreamDeckEvents(): void {
  const evtSource = new EventSource('/api/streamdeck-events');

  evtSource.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('Stream Deck event:', data);

    if (data.action === 'query' && data.prompt) {
      console.log('Stream Deck query received:', data.prompt);
      msgEl.value = data.prompt;
      sendBtn.disabled = false;
      handleSend().catch((e) => console.error('Stream Deck handleSend error:', e));
    }

    if (data.action === 'push_to_talk') {
      startListening();
    }

    if (data.action === 'stop') {
      stopListening();
    }

    if (data.action === 'send_slack') {
      sendSlackBtn.click();
    }

    if (data.action === 'clear') {
      detailContentEl.innerHTML = '';
      sendSlackBtn.style.display = 'none';
    }

    if (data.action === 'send_email') {
      const text = sendSlackBtn.dataset.text;
      if (text) {
        fetch('/api/send-email', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ text }),
        }).catch((e) => console.error('Email send failed:', e));
      }
    }

    if (data.action === 'interrupt') {
      if (simli) simli.ClearBuffer();
      setStatus('Ready', 'ready');
      fetch('/api/speaking-done', { method: 'POST' }).catch(() => {});
    }

    if (data.action === 'speak' && data.text) {
      (async () => {
        try {
          setStatus('Speaking...', 'speaking');
          const pcm = await fetchTTSAudio(data.text);
          sendAudioToSimli(pcm);
          setTimeout(() => {
            setStatus('Ready', 'ready');
            fetch('/api/speaking-done', { method: 'POST' }).catch(() => {});
          }, 3000);
        } catch (e) {
          console.error('Speak error:', e);
          setStatus('Ready', 'ready');
        }
      })();
    }

    if (data.action === 'mute') {
      audioEl.muted = true;
    }

    if (data.action === 'unmute') {
      audioEl.muted = false;
    }
  };

  evtSource.onerror = () => {
    console.log('Stream Deck SSE reconnecting...');
  };
}

// --- Audio unlock on first user interaction ---

function unlockOnGesture(): void {
  unlockAudio();
  document.removeEventListener('click', unlockOnGesture);
  document.removeEventListener('keydown', unlockOnGesture);
}
document.addEventListener('click', unlockOnGesture);
document.addEventListener('keydown', unlockOnGesture);

// --- Speech Recognition ---

let recognition: SpeechRecognition | null = null;
let isListening = false;

function startListening(): void {
  if (isListening) return;

  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SpeechRecognition) {
    console.error('Speech recognition not supported');
    setStatus('Speech not supported', 'ready');
    return;
  }

  recognition = new SpeechRecognition();
  recognition.lang = window.avatarLang || 'en-US';
  recognition.interimResults = true;
  recognition.continuous = true;
  recognition.maxAlternatives = 1;

  isListening = true;
  setStatus('Listening...', 'speaking');
  msgEl.placeholder = 'Listening...';
  msgEl.value = '';

  let finalTranscript = '';
  let silenceTimer: ReturnType<typeof setTimeout> | null = null;

  recognition.onresult = (event) => {
    let interim = '';
    finalTranscript = '';

    for (let i = 0; i < event.results.length; i++) {
      if (event.results[i].isFinal) {
        finalTranscript += event.results[i][0].transcript;
      } else {
        interim += event.results[i][0].transcript;
      }
    }

    msgEl.value = finalTranscript + interim;

    if (silenceTimer) clearTimeout(silenceTimer);
    silenceTimer = setTimeout(() => {
      if (finalTranscript.trim()) {
        stopListening();
        msgEl.value = finalTranscript.trim();
        handleSend();
      }
    }, 2000);
  };

  recognition.onerror = (event) => {
    console.error('Speech error:', event.error);
    stopListening();
  };

  recognition.onend = () => {
    if (isListening) {
      if (finalTranscript.trim()) {
        isListening = false;
        msgEl.value = finalTranscript.trim();
        msgEl.placeholder = 'Ask me anything...';
        setStatus('Ready', 'ready');
        handleSend();
      } else {
        stopListening();
      }
    }
  };

  recognition.start();
}

function stopListening(): void {
  if (recognition) {
    isListening = false;
    try {
      recognition.stop();
    } catch {
      // Ignore
    }
    recognition = null;
  }
  msgEl.placeholder = 'Ask me anything...';
  setStatus('Ready', 'ready');
}

// --- Dynamic UI rendering ---

function renderLanguageOptions(): void {
  if (!clientConfig) return;
  langOptions.innerHTML = '';

  for (const lang of clientConfig.languages) {
    const btn = document.createElement('button');
    btn.className = 'avatar-option';
    btn.dataset.lang = lang.code;
    if (lang.code === window.avatarLang) {
      btn.classList.add('active');
    }

    const flag = lang.flag ? getFlagEmoji(lang.flag) : '';
    btn.innerHTML = `<div class="avatar-label">${flag} ${lang.name}</div>`;
    langOptions.appendChild(btn);
  }
}

function renderAvatarOptions(): void {
  if (!clientConfig) return;
  avatarOptions.innerHTML = '';

  for (const avatar of clientConfig.avatars) {
    const btn = document.createElement('button');
    btn.className = 'avatar-option';
    btn.dataset.faceId = avatar.faceId;
    btn.dataset.voiceId = avatar.voiceId;
    if (avatar.zoom) btn.dataset.zoom = String(avatar.zoom);
    if (avatar.top) btn.dataset.top = String(avatar.top);

    if (avatar.faceId === currentFaceId) {
      btn.classList.add('active');
    }

    btn.innerHTML = `<div class="avatar-label">${avatar.name}</div>`;
    avatarOptions.appendChild(btn);
  }
}

function getFlagEmoji(countryCode: string): string {
  const flags: Record<string, string> = {
    gb: '\u{1F1EC}\u{1F1E7}',
    us: '\u{1F1FA}\u{1F1F8}',
    no: '\u{1F1F3}\u{1F1F4}',
    de: '\u{1F1E9}\u{1F1EA}',
    fr: '\u{1F1EB}\u{1F1F7}',
    es: '\u{1F1EA}\u{1F1F8}',
    it: '\u{1F1EE}\u{1F1F9}',
    jp: '\u{1F1EF}\u{1F1F5}',
    cn: '\u{1F1E8}\u{1F1F3}',
  };
  return flags[countryCode.toLowerCase()] || '';
}

// --- Settings: Language selection ---

langOptions.addEventListener('click', (e) => {
  const btn = (e.target as HTMLElement).closest('.avatar-option') as HTMLElement | null;
  if (!btn) return;
  const lang = btn.dataset.lang;
  if (!lang) return;

  document.querySelectorAll('#lang-options .avatar-option').forEach((b) => b.classList.remove('active'));
  btn.classList.add('active');

  window.avatarLang = lang;
  localStorage.setItem('avatar-lang', lang);

  if (recognition) {
    try {
      recognition.stop();
    } catch {
      // Ignore
    }
  }
});

// --- Settings: Avatar selection ---

avatarOptions.addEventListener('click', async (e) => {
  const btn = (e.target as HTMLElement).closest('.avatar-option') as HTMLElement | null;
  if (!btn) return;
  const faceId = btn.dataset.faceId;
  const voiceId = btn.dataset.voiceId;
  if (!faceId) return;

  document.querySelectorAll('#avatar-options .avatar-option').forEach((b) => b.classList.remove('active'));
  btn.classList.add('active');

  localStorage.setItem('avatar-faceId', faceId);
  if (voiceId) localStorage.setItem('avatar-voiceId', voiceId);

  const zoom = btn.dataset.zoom || '120';
  const top = btn.dataset.top || '-10';
  videoEl.style.height = zoom + '%';
  videoEl.style.top = top + '%';

  settingsPage.classList.remove('active');

  setStatus('Switching avatar...', 'thinking');
  try {
    if (simli) simli.close();
  } catch (e) {
    console.warn('Simli close error:', e);
  }

  currentFaceId = faceId;
  currentVoiceId = voiceId || currentVoiceId;
  await initSimli();
});

// --- Boot ---

async function boot(): Promise<void> {
  try {
    // Load config
    clientConfig = await loadClientConfig();

    // Update app name
    if (appNameEl) {
      appNameEl.textContent = clientConfig.app.name;
    }
    document.title = clientConfig.app.name;

    // Restore saved language or use default
    const savedLang = localStorage.getItem('avatar-lang');
    const defaultLang = clientConfig.languages.find((l) => l.default)?.code || clientConfig.languages[0]?.code || 'en-US';
    window.avatarLang = savedLang || defaultLang;

    // Restore saved avatar or use default
    const savedFaceId = localStorage.getItem('avatar-faceId');
    const savedVoiceId = localStorage.getItem('avatar-voiceId');
    const defaultAvatar = clientConfig.avatars.find((a) => a.default) || clientConfig.avatars[0];

    currentFaceId = savedFaceId || defaultAvatar?.faceId || '';
    currentVoiceId = savedVoiceId || defaultAvatar?.voiceId || '';

    // Apply saved zoom/position
    if (savedFaceId) {
      const avatar = clientConfig.avatars.find((a) => a.faceId === savedFaceId);
      if (avatar) {
        videoEl.style.height = (avatar.zoom || 120) + '%';
        videoEl.style.top = (avatar.top || -10) + '%';
      }
    }

    // Render dynamic UI
    renderLanguageOptions();
    renderAvatarOptions();

    // Start SSE for Stream Deck events
    initStreamDeckEvents();

    // Initialize Simli
    await initSimli();
  } catch (err) {
    console.error('Boot error:', err);
    setStatus(`Error: ${(err as Error).message}`, 'ready');
  }
}

boot();
