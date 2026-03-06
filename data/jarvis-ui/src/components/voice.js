// ── 語音對話模組 ──
// VAD（語音活動偵測）+ 自動錄音 + 打斷功能

import { MicVAD, utils } from '@ricky0123/vad-web';

let vad = null;
let isVoiceMode = false;
let isProcessing = false;  // 正在處理語音（避免重複送出）
let playbackQueue = [];     // TTS 音訊播放佇列
let currentAudio = null;    // 正在播放的音訊
let isPlaying = false;

// ── 狀態回調 ──
let onStateChange = null;   // (state: 'idle'|'listening'|'processing'|'speaking') => void

function setState(state) {
  if (onStateChange) onStateChange(state);
  // 同步 orb 視覺
  window.dispatchEvent(new CustomEvent('voice-state', { detail: state }));
}

// ── VAD 初始化 ──

async function initVAD() {
  vad = await MicVAD.new({
    model: 'v5',
    baseAssetPath: '/vad/',
    onnxWASMBasePath: '/vad/',
    positiveSpeechThreshold: 0.8,
    negativeSpeechThreshold: 0.3,
    minSpeechFrames: 5,
    preSpeechPadFrames: 10,
    redemptionFrames: 8,

    onSpeechStart: () => {
      console.log('[VOICE] 偵測到說話');
      // 打斷：如果 AI 正在播放語音，立刻停止
      if (isPlaying) {
        console.log('[VOICE] 打斷播放');
        stopPlayback();
      }
      setState('listening');
    },

    onSpeechEnd: async (audioData) => {
      console.log('[VOICE] 說話結束，送出音訊');
      if (isProcessing) return; // 上一段還在處理

      isProcessing = true;
      setState('processing');

      try {
        // Float32Array 16kHz → WAV
        const wavBuffer = utils.encodeWAV(audioData);
        const blob = new Blob([wavBuffer], { type: 'audio/wav' });

        // 送到 server
        await sendVoice(blob);
      } catch (err) {
        console.error('[VOICE] 處理失敗:', err);
        setState('listening');
      } finally {
        isProcessing = false;
      }
    },

    onVADMisfire: () => {
      console.log('[VOICE] VAD misfire（太短）');
      setState('listening');
    },
  });
}

// ── 送出語音到 server ──

async function sendVoice(audioBlob) {
  const formData = new FormData();
  formData.append('audio', audioBlob, 'voice.wav');

  // 使用 SSE 接收句子級 TTS 回應
  const res = await fetch('/api/voice', {
    method: 'POST',
    body: formData,
  });

  if (!res.ok) {
    console.error('[VOICE] API 錯誤:', res.status);
    setState('listening');
    return;
  }

  // 回應是 NDJSON 串流（每行一個 TTS 片段）
  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buffer = '';

  setState('speaking');

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split('\n');
    buffer = lines.pop(); // 最後一行可能不完整

    for (const line of lines) {
      if (!line.trim()) continue;
      try {
        const data = JSON.parse(line);

        if (data.type === 'transcript') {
          // 顯示使用者說的話
          window.dispatchEvent(new CustomEvent('voice-transcript', { detail: data.text }));
        }

        if (data.type === 'tts-chunk') {
          // 收到一段 TTS 音訊（base64）
          queueAudio(data.audio, data.contentType || 'audio/mp4');
        }

        if (data.type === 'text-chunk') {
          // 文字回應（給 chat 面板顯示用）
          window.dispatchEvent(new CustomEvent('voice-response-text', { detail: data.text }));
        }

        if (data.type === 'done') {
          console.log('[VOICE] 回應完成');
        }

        if (data.type === 'error') {
          console.error('[VOICE] Server error:', data.message);
        }
      } catch {}
    }
  }

  // 等播放完才回到 listening
  await waitPlaybackDone();
  if (isVoiceMode) setState('listening');
}

// ── 音訊播放佇列 ──

function queueAudio(base64, contentType) {
  const binary = atob(base64);
  const bytes = new Uint8Array(binary.length);
  for (let i = 0; i < binary.length; i++) bytes[i] = binary.charCodeAt(i);
  const blob = new Blob([bytes], { type: contentType });
  const url = URL.createObjectURL(blob);

  playbackQueue.push(url);
  if (!isPlaying) playNext();
}

function playNext() {
  if (playbackQueue.length === 0) {
    isPlaying = false;
    return;
  }

  isPlaying = true;
  const url = playbackQueue.shift();
  currentAudio = new Audio(url);
  currentAudio.onended = () => {
    URL.revokeObjectURL(url);
    currentAudio = null;
    playNext();
  };
  currentAudio.onerror = () => {
    console.error('[VOICE] 音訊播放失敗');
    URL.revokeObjectURL(url);
    currentAudio = null;
    playNext();
  };
  currentAudio.play().catch(() => playNext());
}

function stopPlayback() {
  if (currentAudio) {
    currentAudio.pause();
    currentAudio.onended = null;
    currentAudio = null;
  }
  // 清空佇列
  playbackQueue.forEach(url => URL.revokeObjectURL(url));
  playbackQueue = [];
  isPlaying = false;
}

function waitPlaybackDone() {
  return new Promise((resolve) => {
    const check = () => {
      if (!isPlaying && playbackQueue.length === 0) return resolve();
      setTimeout(check, 200);
    };
    check();
  });
}

// ── 公開 API ──

export async function startVoiceMode() {
  if (isVoiceMode) return;
  console.log('[VOICE] 啟動語音模式');

  try {
    if (!vad) await initVAD();
    await vad.start();
    isVoiceMode = true;
    setState('listening');
  } catch (err) {
    console.error('[VOICE] 啟動失敗:', err);
    // 通知 UI
    window.dispatchEvent(new CustomEvent('voice-error', {
      detail: err.name === 'NotAllowedError' ? '麥克風權限被拒絕' : `語音模式啟動失敗: ${err.message}`
    }));
    setState('idle');
  }
}

export async function stopVoiceMode() {
  if (!isVoiceMode) return;
  console.log('[VOICE] 關閉語音模式');

  isVoiceMode = false;
  if (vad) await vad.pause();
  stopPlayback();
  setState('idle');
}

export function toggleVoiceMode() {
  return isVoiceMode ? stopVoiceMode() : startVoiceMode();
}

export function isVoiceActive() {
  return isVoiceMode;
}

export function setOnStateChange(cb) {
  onStateChange = cb;
}
