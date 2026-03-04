// ── Voice Chat Route: /api/voice ──

import { Router } from 'express';
import multer from 'multer';
import os from 'os';
import path from 'path';
import { execFile } from 'child_process';
import { unlink } from 'fs/promises';
import { gwRequest } from '../gateway.js';
import { addVoiceHandler, removeVoiceHandler } from '../sse.js';
import { ttsSentence, splitSentences, getCurrentVoice } from '../tts.js';

const router = Router();
const upload = multer({ dest: os.tmpdir(), limits: { fileSize: 10 * 1024 * 1024 } });
const WHISPER_MODEL = path.join(os.homedir(), '.whisper-models', 'ggml-base.bin');

function whisperTranscribe(audioPath, lang = 'zh') {
  return new Promise((resolve, reject) => {
    execFile('whisper-cli', ['-m', WHISPER_MODEL, '-f', audioPath, '-l', lang, '--no-timestamps', '-nt'],
      { timeout: 15000 }, (err, stdout) => {
        if (err) return reject(err);
        resolve(stdout.trim());
      });
  });
}

// 訊息計數（共用）
let msgCountToday = 0;
let msgCountDate = new Date().toLocaleDateString('en-CA', { timeZone: 'Asia/Taipei' });

router.post('/voice', upload.single('audio'), async (req, res) => {
  if (!req.file) return res.status(400).json({ error: 'audio file required' });

  res.writeHead(200, {
    'Content-Type': 'application/x-ndjson', 'Cache-Control': 'no-cache', 'Transfer-Encoding': 'chunked',
  });

  const send = (obj) => res.write(JSON.stringify(obj) + '\n');
  const audioPath = req.file.path;

  try {
    const transcript = await whisperTranscribe(audioPath);
    if (!transcript) { send({ type: 'error', message: '無法辨識語音' }); send({ type: 'done' }); res.end(); return; }

    send({ type: 'transcript', text: transcript });
    console.log(`[VOICE] 轉錄: "${transcript}"`);

    const today = new Date().toLocaleDateString('en-CA', { timeZone: 'Asia/Taipei' });
    if (today !== msgCountDate) { msgCountToday = 0; msgCountDate = today; }
    msgCountToday++;

    const idempotencyKey = `voice-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
    const voice = getCurrentVoice();

    const responseText = await new Promise((resolve, reject) => {
      let fullText = '';
      let sentenceBuffer = '';
      let currentRunId = null;
      let ttsQueue = [];
      let ttsRunning = false;

      const processTtsQueue = async () => {
        if (ttsRunning) return;
        ttsRunning = true;
        while (true) {
          const sentence = ttsQueue.shift();
          if (!sentence) break;
          try {
            const audioBuffer = await ttsSentence(sentence, voice);
            const base64 = audioBuffer.toString('base64');
            send({ type: 'tts-chunk', audio: base64, contentType: 'audio/mp4', text: sentence });
          } catch (err) { console.error('[VOICE] TTS 失敗:', err.message); }
        }
        ttsRunning = false;
        if (ttsQueue.length > 0) processTtsQueue();
      };

      const handler = (payload) => {
        const text = (() => {
          if (!payload.message?.content) return '';
          const c = payload.message.content;
          if (Array.isArray(c)) return c.filter(x => x.type === 'text').map(x => x.text).join('');
          return typeof c === 'string' ? c : '';
        })();

        if (!currentRunId && payload.runId) currentRunId = payload.runId;
        if (currentRunId && payload.runId !== currentRunId) return;

        if (payload.state === 'streaming' || payload.state === 'final') {
          const newChars = text.slice(fullText.length);
          fullText = text;
          if (newChars) {
            send({ type: 'text-chunk', text: newChars });
            sentenceBuffer += newChars;
            const sentences = splitSentences(sentenceBuffer);
            if (sentences.length > 1) {
              const complete = sentences.slice(0, -1);
              sentenceBuffer = sentences[sentences.length - 1];
              ttsQueue.push(...complete);
              processTtsQueue();
            }
          }
        }

        if (payload.state === 'final' || payload.state === 'aborted') {
          if (sentenceBuffer.trim()) ttsQueue.push(sentenceBuffer.trim());
          processTtsQueue().then(() => { removeVoiceHandler(handler); resolve(fullText); });
        }
      };

      addVoiceHandler(handler);

      gwRequest('chat.send', {
        message: transcript, sessionKey: req.app.locals.sessionKey,
        idempotencyKey, deliver: false,
      }).catch((err) => { removeVoiceHandler(handler); reject(err); });

      setTimeout(() => {
        removeVoiceHandler(handler);
        if (sentenceBuffer.trim()) { ttsQueue.push(sentenceBuffer.trim()); processTtsQueue().then(() => resolve(fullText)); }
        else resolve(fullText);
      }, 60000);
    });

    send({ type: 'done', fullText: responseText });
  } catch (err) {
    console.error('[VOICE] 錯誤:', err);
    send({ type: 'error', message: err.message });
  } finally {
    try { await unlink(audioPath); } catch {}
    res.end();
  }
});

export default router;
