// ── TTS 引擎管理 ──

import os from 'os';
import { execFile } from 'child_process';
import { mkdtemp, unlink, rmdir, readFile } from 'fs/promises';
import { createReadStream } from 'fs';
import path from 'path';

const TTS_ENGINES = {
  macos: { name: 'macOS Say', available: process.platform === 'darwin' },
  edge: { name: 'Edge TTS', available: true },
};

let currentEngine = 'edge';
let macosVoice = 'Samantha';
let edgeVoice = 'zh-TW-HsiaoChenNeural';

export function initTTS(config) {
  currentEngine = config.engine || (process.platform === 'darwin' ? 'macos' : 'edge');
  macosVoice = config.voice || 'Samantha';
  edgeVoice = config.edgeVoice || 'zh-TW-HsiaoChenNeural';
}

export function stripMarkdown(str) {
  return str
    .replace(/```[\s\S]*?```/g, '')          // code blocks
    .replace(/`([^`]+)`/g, '$1')             // inline code
    .replace(/!\[.*?\]\(.*?\)/g, '')         // images
    .replace(/\[([^\]]+)\]\(.*?\)/g, '$1')   // links → text only
    .replace(/^#{1,6}\s+/gm, '')             // headings
    .replace(/(\*\*|__)(.*?)\1/g, '$2')      // bold
    .replace(/(\*|_)(.*?)\1/g, '$2')         // italic
    .replace(/~~(.*?)~~/g, '$1')             // strikethrough
    .replace(/^[\s]*[-*+]\s+/gm, '')         // unordered list markers
    .replace(/^[\s]*\d+\.\s+/gm, '')         // ordered list markers
    .replace(/^>\s+/gm, '')                  // blockquotes
    .replace(/^---+$/gm, '')                 // horizontal rules
    .replace(/\|/g, '')                      // table pipes
    .replace(/[\p{Emoji_Presentation}\p{Extended_Pictographic}]/gu, '')  // emoji
    .replace(/\s{2,}/g, ' ')
    .trim();
}

export function stripEmoji(str) {
  return str.replace(/[\p{Emoji_Presentation}\p{Extended_Pictographic}]/gu, '').replace(/\s{2,}/g, ' ').trim();
}

export function getEngines() {
  return {
    current: currentEngine,
    engines: Object.entries(TTS_ENGINES).map(([id, e]) => ({ id, ...e, selected: id === currentEngine })),
  };
}

export function setEngine(engine) {
  if (!TTS_ENGINES[engine]) throw new Error('unknown engine');
  if (!TTS_ENGINES[engine].available) throw new Error('engine not available');
  currentEngine = engine;
  return currentEngine;
}

export function getCurrentVoice() { return macosVoice; }

// 生成 MP3 並串流到 response
export async function synthesizeToResponse(text, voice, res) {
  const cleanText = stripMarkdown(text);
  if (!cleanText) { res.status(400).json({ error: 'no speakable text' }); return; }

  const dir = await mkdtemp(path.join(os.tmpdir(), 'jarvis-tts-'));
  try {
    let mp3Path;
    if (currentEngine === 'edge') {
      mp3Path = path.join(dir, 'speech.mp3');
      const v = voice || edgeVoice;
      await execAsync('python3', ['-m', 'edge_tts', '--text', cleanText, '--voice', v, '--rate', '+10%', '--write-media', mp3Path]);
    } else {
      const aiff = path.join(dir, 'speech.aiff');
      mp3Path = path.join(dir, 'speech.mp3');
      const v = voice || macosVoice;
      await execAsync('say', ['-v', v, '-o', aiff, cleanText]);
      await execAsync('ffmpeg', ['-i', aiff, '-y', '-q:a', '4', mp3Path]);
      try { await unlink(aiff); } catch {}
    }
    res.setHeader('Content-Type', 'audio/mpeg');
    const stream = createReadStream(mp3Path);
    stream.pipe(res);
    stream.on('end', async () => { try { await unlink(mp3Path); await rmdir(dir); } catch {} });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
}

// 生成單句音訊 buffer（voice chat 用）
export async function ttsSentence(text, voice) {
  const clean = stripMarkdown(text);
  if (!clean) return Buffer.alloc(0);

  const dir = await mkdtemp(path.join(os.tmpdir(), 'jarvis-vtts-'));
  const aiff = path.join(dir, 'speech.aiff');
  const m4a = path.join(dir, 'speech.m4a');
  try {
    await execAsync('say', ['-v', voice, '-o', aiff, clean]);
    await execAsync('ffmpeg', ['-i', aiff, '-y', '-c:a', 'aac', '-b:a', '64k', m4a]);
    return await readFile(m4a);
  } finally {
    try { await unlink(aiff); } catch {}
    try { await unlink(m4a); } catch {}
    try { await rmdir(dir); } catch {}
  }
}

// 句子分割
export function splitSentences(text) {
  return text.split(/(?<=[。！？.!?\n])\s*/).filter(s => s.trim().length > 0);
}

function execAsync(cmd, args) {
  return new Promise((resolve, reject) => {
    execFile(cmd, args, (err) => err ? reject(err) : resolve());
  });
}
