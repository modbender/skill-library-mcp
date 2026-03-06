#!/usr/bin/env node
/**
 * Chunked offline renderer: Renders Strudel patterns in small cycle chunks
 * to avoid OOM on long/dense compositions.
 *
 * Usage: node src/runtime/chunked-render.mjs <input.js> [output.wav] [totalCycles] [chunkSize]
 */

import { readFileSync, writeFileSync, readdirSync, existsSync, appendFileSync, unlinkSync } from 'fs';
import { createRequire } from 'module';
import path from 'path';

const require = createRequire(import.meta.url);

// ── Polyfill Web Audio for Node.js ──
const nwa = require('node-web-audio-api');

// Browser stubs (minimal)
globalThis.window = {
  addEventListener: () => {}, removeEventListener: () => {}, dispatchEvent: () => true,
  location: { href: '', origin: '', protocol: 'https:' },
  navigator: { userAgent: 'node' },
  requestAnimationFrame: cb => setTimeout(cb, 16), cancelAnimationFrame: clearTimeout,
  innerWidth: 800, innerHeight: 600, getComputedStyle: () => ({}),
};
globalThis.document = {
  createElement: () => ({ getContext: () => null, style: {}, setAttribute: () => {}, appendChild: () => {} }),
  body: { appendChild: () => {}, removeChild: () => {} },
  addEventListener: () => {}, removeEventListener: () => {}, dispatchEvent: () => true,
  createEvent: () => ({ initEvent: () => {} }),
  head: { appendChild: () => {} }, querySelectorAll: () => [], querySelector: () => null,
};
globalThis.addEventListener = () => {};
globalThis.removeEventListener = () => {};

// Stub AudioContext for Strudel's import-time checks
let _sharedCtx = null;
globalThis.AudioContext = class {
  constructor() {
    if (!_sharedCtx) {
      _sharedCtx = new nwa.OfflineAudioContext(2, 44100 * 10, 44100);
      _sharedCtx.resume = async () => {};
      _sharedCtx.close = async () => {};
    }
    return _sharedCtx;
  }
};
globalThis.OfflineAudioContext = nwa.OfflineAudioContext;
globalThis.AudioBuffer = nwa.AudioBuffer;
globalThis.AudioBufferSourceNode = nwa.AudioBufferSourceNode;
globalThis.GainNode = nwa.GainNode;
globalThis.OscillatorNode = nwa.OscillatorNode;
globalThis.BiquadFilterNode = nwa.BiquadFilterNode;
globalThis.StereoPannerNode = nwa.StereoPannerNode;
globalThis.DynamicsCompressorNode = nwa.DynamicsCompressorNode;
globalThis.ConvolverNode = nwa.ConvolverNode;
globalThis.DelayNode = nwa.DelayNode;
globalThis.WaveShaperNode = nwa.WaveShaperNode;
globalThis.AnalyserNode = nwa.AnalyserNode;

// ── Parse args ──
const input = process.argv[2];
const output = process.argv[3] || 'output.wav';
const totalCycles = parseInt(process.argv[4] || '175');
const chunkSize = parseInt(process.argv[5] || '8');

if (!input) {
  console.error('Usage: node src/runtime/chunked-render.mjs <input.js> [output.wav] [totalCycles] [chunkSize]');
  process.exit(1);
}

const sampleRate = 44100;

// ── Load Strudel ──
console.log('Loading Strudel...');
const core = await import('@strudel/core');
const mini = await import('@strudel/mini');
try { await import('@strudel/tonal'); } catch (e) {}

if (core.setStringParser && mini.mini) {
  core.setStringParser(mini.mini);
}

let cpmValue = 120 / 4; // default
for (const [key, val] of Object.entries(core)) {
  globalThis[key] = val;
}
globalThis.setcpm = (v) => { cpmValue = v; };
globalThis.setcps = (v) => { cpmValue = v * 60; };
globalThis.samples = () => {};
globalThis.hush = () => {};

// Strip viz methods
const vizMethods = ['pianoroll', '_pianoroll', 'spiral', '_spiral', 'scope', '_scope', 'draw', '_draw'];
function stripVizMethods(code) {
  for (const method of vizMethods) {
    const pattern = new RegExp(`\\.(${method})\\s*\\(`, 'g');
    let match;
    while ((match = pattern.exec(code)) !== null) {
      const dotStart = match.index;
      const parenStart = code.indexOf('(', dotStart + method.length + 1);
      if (parenStart === -1) continue;
      let depth = 1, i = parenStart + 1, inStr = null;
      while (i < code.length && depth > 0) {
        const ch = code[i];
        if (inStr) { if (ch === '\\') { i += 2; continue; } if (ch === inStr) inStr = null; }
        else { if (ch === "'" || ch === '"' || ch === '`') inStr = ch; else if (ch === '(') depth++; else if (ch === ')') depth--; }
        i++;
      }
      if (depth === 0) { code = code.slice(0, dotStart) + code.slice(i); pattern.lastIndex = dotStart; }
    }
  }
  return code;
}

console.log('  ✅ Strudel loaded');

// ── Evaluate pattern ──
console.log('Evaluating pattern...');
let patternCode = readFileSync(input, 'utf8').replace(/^\/\/ @\w+.*/gm, '').trim();
patternCode = stripVizMethods(patternCode);

let pattern;
try {
  const lines = patternCode.split('\n');
  let lastExprStart = -1;
  let depth = 0;
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i].trim();
    if (!line || line.startsWith('//')) continue;
    if (depth === 0 && /^(stack|note|s|n|seq|cat|sequence|arrange|slowcat|fastcat)\s*\(/.test(line)) {
      lastExprStart = i;
    }
    for (const ch of line) { if (ch === '(') depth++; if (ch === ')') depth--; }
  }
  if (lastExprStart >= 0) {
    const setup = lines.slice(0, lastExprStart).join('\n');
    const expr = lines.slice(lastExprStart).join('\n');
    const fn = new Function(setup + '\nreturn ' + expr);
    pattern = fn();
  } else {
    try { pattern = new Function(patternCode)(); } catch { pattern = new Function('return ' + patternCode)(); }
  }
} catch (e) {
  console.error('  ❌ Pattern eval failed:', e.message);
  process.exit(1);
}

if (!pattern || typeof pattern.queryArc !== 'function') {
  console.error('  ❌ Pattern did not return a queryable pattern.');
  process.exit(1);
}

const actualCps = cpmValue / 60;
const totalDuration = totalCycles / actualCps;
console.log(`  CPS: ${actualCps.toFixed(3)} (${(cpmValue * 4).toFixed(1)} BPM), Total: ${totalCycles} cycles, Duration: ${totalDuration.toFixed(1)}s`);

// ── Load samples ──
const SAMPLES_DIR = path.resolve(
  import.meta.dirname || path.dirname(new URL(import.meta.url).pathname),
  '../../samples'
);
const sampleBufferData = new Map(); // sound → {channels, sampleRate, data[]}

function loadWavRaw(filePath) {
  const raw = readFileSync(filePath);
  const view = new DataView(raw.buffer, raw.byteOffset, raw.byteLength);
  if (raw.toString('ascii', 0, 4) !== 'RIFF') return null;
  const channels = view.getUint16(22, true);
  const sr = view.getUint32(24, true);
  const bitsPerSample = view.getUint16(34, true);
  let dataOffset = 12;
  while (dataOffset < raw.length - 8) {
    const chunkId = raw.toString('ascii', dataOffset, dataOffset + 4);
    const chunkSize = view.getUint32(dataOffset + 4, true);
    if (chunkId === 'data') {
      dataOffset += 8;
      const numSamples = Math.floor(chunkSize / (bitsPerSample / 8) / channels);
      const channelData = [];
      for (let ch = 0; ch < channels; ch++) {
        channelData.push(new Float32Array(numSamples));
      }
      for (let ch = 0; ch < channels; ch++) {
        for (let i = 0; i < numSamples; i++) {
          const byteIndex = dataOffset + (i * channels + ch) * (bitsPerSample / 8);
          if (bitsPerSample === 16) {
            channelData[ch][i] = view.getInt16(byteIndex, true) / 32768;
          } else if (bitsPerSample === 24) {
            const s = (view.getUint8(byteIndex) | (view.getUint8(byteIndex+1) << 8) | (view.getInt8(byteIndex+2) << 16));
            channelData[ch][i] = s / 8388608;
          }
        }
      }
      return { channels, sampleRate: sr, data: channelData, length: numSamples };
    }
    dataOffset += 8 + chunkSize;
  }
  return null;
}

// ── strudel.json root note manifest ──
// Maps bank name → MIDI root note (authoritative when present)
const strudelRootNotes = new Map();

/**
 * Parse a note key from strudel.json (e.g. "cs1", "a1", "d3") into MIDI note number.
 * Returns null for non-note keys like "0" or numeric indices.
 */
function parseStrudelNoteKey(key) {
  const m = String(key).match(/^([a-gA-G])(s|#|b)?(\d+)$/);
  if (!m) return null;
  const map = { c:0, d:2, e:4, f:5, g:7, a:9, b:11 };
  let semi = map[m[1].toLowerCase()] ?? 0;
  if (m[2] === 's' || m[2] === '#') semi++;
  if (m[2] === 'b') semi--;
  const oct = parseInt(m[3]);
  return semi + (oct + 1) * 12;
}

if (existsSync(SAMPLES_DIR)) {
  console.log('Loading samples...');
  let sampleCount = 0;

  // Load strudel.json manifest if present
  const strudelJsonPath = path.join(SAMPLES_DIR, 'strudel.json');
  let strudelManifest = null;
  if (existsSync(strudelJsonPath)) {
    try {
      strudelManifest = JSON.parse(readFileSync(strudelJsonPath, 'utf8'));
      console.log('  📋 Found strudel.json manifest');

      // Extract root notes from the manifest
      for (const [bankName, mapping] of Object.entries(strudelManifest)) {
        if (bankName.startsWith('_')) continue; // skip meta keys
        if (typeof mapping !== 'object' || mapping === null) continue;
        const noteKeys = Object.keys(mapping).map(k => parseStrudelNoteKey(k)).filter(n => n !== null);
        if (noteKeys.length > 0) {
          // For multi-sample banks, use the lowest note as root (closest to fundamental)
          // For single-sample banks, use that note
          const rootMidi = Math.min(...noteKeys);
          strudelRootNotes.set(bankName, rootMidi);
        }
      }

      if (strudelRootNotes.size > 0) {
        console.log(`  🎹 Root notes from manifest: ${[...strudelRootNotes.entries()].map(([k, v]) => `${k}→MIDI${v}`).join(', ')}`);
      }
    } catch (e) {
      console.warn('  ⚠️ Failed to parse strudel.json:', e.message);
    }
  }

  for (const dir of readdirSync(SAMPLES_DIR)) {
    const dirPath = path.join(SAMPLES_DIR, dir);
    try {
      const files = readdirSync(dirPath).filter(f => f.endsWith('.wav') || f.endsWith('.WAV')).sort();
      for (let i = 0; i < files.length; i++) {
        const buf = loadWavRaw(path.join(dirPath, files[i]));
        if (buf) {
          sampleBufferData.set(`${dir}:${i}`, buf);
          if (i === 0) sampleBufferData.set(dir, buf);
          sampleCount++;
        }
      }
    } catch { /* not a directory */ }
  }
  console.log(`  ✅ ${sampleCount} samples loaded`);
}

// ── Waveform generators ──
const waveMap = {
  sine: 'sine', triangle: 'triangle', square: 'square',
  sawtooth: 'sawtooth', saw: 'sawtooth', tri: 'triangle',
};

function noteToFreq(note) {
  if (typeof note === 'number') return note;
  const m = String(note).match(/^([a-gA-G])(#|b|s)?(\d+)?$/);
  if (!m) return 440;
  const map = { c:0, d:2, e:4, f:5, g:7, a:9, b:11 };
  let semi = map[m[1].toLowerCase()] ?? 0;
  if (m[2] === '#' || m[2] === 's') semi++;
  if (m[2] === 'b') semi--;
  const oct = parseInt(m[3] ?? '4');
  return 440 * Math.pow(2, (semi - 9 + (oct - 4) * 12) / 12);
}

function noteToMidi(note) {
  if (typeof note === 'number') return note;
  const m = String(note).match(/^([a-gA-G])(#|b|s)?(\d+)?$/);
  if (!m) return 60;
  const map = { c:0, d:2, e:4, f:5, g:7, a:9, b:11 };
  let semi = map[m[1].toLowerCase()] ?? 0;
  if (m[2] === '#' || m[2] === 's') semi++;
  if (m[2] === 'b') semi--;
  const oct = parseInt(m[3] ?? '4');
  return semi + (oct + 1) * 12; // C4 = MIDI 60
}

function noteToSemitones(note) {
  return noteToMidi(note) - 60;
}

// ── Pitch-shift utilities ──

/**
 * Detect root note from sample bank name.
 * 
 * Priority:
 * 1. strudel.json manifest (authoritative if present)
 * 2. Filename heuristic: e.g. "bass_Cs1" → MIDI 25 (C#1)
 * 3. Default: MIDI 60 (C3)
 */
function detectRootNote(sampleName) {
  // 1. Check strudel.json manifest first (authoritative)
  if (strudelRootNotes.has(sampleName)) {
    return strudelRootNotes.get(sampleName);
  }

  // 2. Try to match a trailing note name like _Cs1, _A1, _Fs2 etc.
  const m = String(sampleName).match(/[_-]([A-Ga-g])(s|#|b)?(\d+)$/);
  if (m) {
    const map = { c:0, d:2, e:4, f:5, g:7, a:9, b:11 };
    let semi = map[m[1].toLowerCase()] ?? 0;
    if (m[2] === 's' || m[2] === '#') semi++;
    if (m[2] === 'b') semi--;
    const oct = parseInt(m[3]);
    return semi + (oct + 1) * 12;
  }

  // 3. Default
  return 60; // C3 / MIDI 60
}

/**
 * Check if a sample name indicates a percussive sound.
 * Percussive sounds get simple resampling (speed change).
 * Tonal sounds get duration-preserving granular pitch shift.
 */
const PERC_PATTERNS = /kick|hat|clap|snare|perc|rim|tom|crash|ride|cymbal|808bd|808hc|808oh|808sd|bd|sd|hh|cp|cb|cr|ht|lt|mt|ghost/i;
function isPercussive(sampleName) {
  return PERC_PATTERNS.test(sampleName);
}

/**
 * Simple resampling by playback rate ratio (percussive mode).
 * ratio > 1 = higher pitch, shorter duration.
 * ratio < 1 = lower pitch, longer duration.
 * Uses linear interpolation.
 */
function resampleBuffer(float32Buf, ratio) {
  if (Math.abs(ratio - 1.0) < 0.001) return float32Buf;
  const outLen = Math.round(float32Buf.length / ratio);
  if (outLen <= 0) return new Float32Array(0);
  const out = new Float32Array(outLen);
  for (let i = 0; i < outLen; i++) {
    const srcIdx = i * ratio;
    const idx0 = Math.floor(srcIdx);
    const frac = srcIdx - idx0;
    const s0 = idx0 < float32Buf.length ? float32Buf[idx0] : 0;
    const s1 = idx0 + 1 < float32Buf.length ? float32Buf[idx0 + 1] : s0;
    out[i] = s0 * (1 - frac) + s1 * frac;
  }
  return out;
}

/**
 * Duration-preserving pitch shift (tonal mode).
 *
 * Two-step approach:
 * 1. Resample the buffer by the pitch ratio (changes both pitch AND duration)
 * 2. Time-stretch back to original length using WSOLA (Waveform Similarity
 *    Overlap-Add) to restore the original duration
 *
 * @param {Float32Array} input - mono audio buffer
 * @param {number} ratio - pitch ratio (>1 = higher, <1 = lower)
 * @param {number} sr - sample rate
 * @returns {Float32Array} pitch-shifted buffer of same length
 */
function granularPitchShift(input, ratio, sr) {
  if (Math.abs(ratio - 1.0) < 0.001) return input;
  
  // Step 1: Resample by pitch ratio (changes pitch + duration)
  const resampled = resampleBuffer(input, ratio);
  
  // Step 2: Time-stretch back to original length using WSOLA
  const targetLen = input.length;
  return wsolaStretch(resampled, targetLen, sr);
}

/**
 * WSOLA (Waveform Similarity Overlap-Add) time stretching.
 * Stretches or compresses audio to targetLen without changing pitch.
 *
 * @param {Float32Array} input - audio to stretch
 * @param {number} targetLen - desired output length in samples
 * @param {number} sr - sample rate
 * @returns {Float32Array} time-stretched audio
 */
function wsolaStretch(input, targetLen, sr) {
  if (input.length === 0) return new Float32Array(targetLen);
  if (Math.abs(input.length - targetLen) < 2) {
    const out = new Float32Array(targetLen);
    out.set(input.subarray(0, Math.min(input.length, targetLen)));
    return out;
  }
  
  const stretchRatio = targetLen / input.length;
  
  // Fixed grain size tuned for musical content (80ms works well for ≥100 Hz)
  const grainLen = Math.round(sr * 0.08); // 80ms
  const synthHop = Math.round(grainLen / 4); // 75% overlap
  const analysisHop = Math.max(1, Math.round(synthHop / stretchRatio));
  const tolerance = Math.round(grainLen / 4);
  
  const output = new Float32Array(targetLen);
  const normBuf = new Float32Array(targetLen);
  
  // Hanning window
  const win = new Float32Array(grainLen);
  for (let i = 0; i < grainLen; i++) {
    win[i] = 0.5 * (1 - Math.cos(2 * Math.PI * i / (grainLen - 1)));
  }
  
  let readPos = 0;
  
  for (let writePos = 0; writePos < targetLen; writePos += synthHop) {
    // WSOLA: find best overlap offset within tolerance
    let bestOffset = 0;
    if (writePos >= synthHop) {
      let bestCorr = -Infinity;
      const minOff = Math.max(-tolerance, -Math.round(readPos));
      const maxOff = Math.min(tolerance, input.length - Math.round(readPos) - grainLen);
      
      for (let off = minOff; off <= maxOff; off++) {
        let corr = 0;
        const ri = Math.round(readPos) + off;
        // Cross-correlate start of this grain with end of previous grain overlap
        const prevStart = writePos - synthHop;
        const checkLen = Math.min(synthHop, grainLen);
        for (let j = 0; j < checkLen; j++) {
          const inIdx = ri + j;
          const outIdx = prevStart + j;
          if (inIdx >= 0 && inIdx < input.length && outIdx >= 0 && outIdx < targetLen && normBuf[outIdx] > 0.001) {
            corr += input[inIdx] * (output[outIdx] / normBuf[outIdx]);
          }
        }
        if (corr > bestCorr) {
          bestCorr = corr;
          bestOffset = off;
        }
      }
    }
    
    const actualRead = Math.round(readPos + bestOffset);
    
    for (let i = 0; i < grainLen; i++) {
      const wi = writePos + i;
      if (wi >= targetLen) break;
      const idx = actualRead + i;
      const sample = (idx >= 0 && idx < input.length) ? input[idx] : 0;
      const w = win[i];
      output[wi] += sample * w;
      normBuf[wi] += w * w;
    }
    
    readPos += analysisHop;
  }
  
  // Normalize
  for (let i = 0; i < targetLen; i++) {
    if (normBuf[i] > 0.001) {
      output[i] /= normBuf[i];
    }
  }
  
  return output;
}

/**
 * Pitch-shift a multi-channel sample buffer.
 * Returns a new buffer object with shifted data (and possibly different length for percussive mode).
 *
 * @param {Object} sampleBuf - {channels, sampleRate, data[], length}
 * @param {number} semitones - semitone offset (positive = higher pitch)
 * @param {boolean} percussive - use simple resampling (true) or granular (false)
 * @returns {Object} new sample buffer with shifted data
 */
function pitchShiftBuffer(sampleBuf, semitones, percussive) {
  if (Math.abs(semitones) < 0.01) return sampleBuf;
  
  const ratio = Math.pow(2, semitones / 12);
  const newData = [];
  
  if (percussive) {
    // Percussive: simple resampling, changes duration
    for (let ch = 0; ch < sampleBuf.channels; ch++) {
      newData.push(resampleBuffer(sampleBuf.data[ch], ratio));
    }
    return {
      channels: sampleBuf.channels,
      sampleRate: sampleBuf.sampleRate,
      data: newData,
      length: newData[0].length,
    };
  } else {
    // Tonal: granular pitch shift, preserves duration
    for (let ch = 0; ch < sampleBuf.channels; ch++) {
      newData.push(granularPitchShift(sampleBuf.data[ch], ratio, sampleBuf.sampleRate));
    }
    return {
      channels: sampleBuf.channels,
      sampleRate: sampleBuf.sampleRate,
      data: newData,
      length: newData[0].length,
    };
  }
}

// ── Software mixer: render haps directly into Float32 buffers ──
// No Web Audio API nodes! Just raw sample mixing.

function renderChunk(startCycle, endCycle, pattern, cps) {
  const chunkStart = startCycle / cps;
  const chunkEnd = endCycle / cps;
  const chunkDur = chunkEnd - chunkStart;
  const numSamples = Math.ceil(chunkDur * sampleRate);
  
  const left = new Float32Array(numSamples);
  const right = new Float32Array(numSamples);
  
  const haps = pattern.queryArc(startCycle, endCycle);
  let scheduled = 0;
  
  for (const hap of haps) {
    const hapStartCycle = hap.part?.begin ?? hap.whole?.begin ?? 0;
    const hapEndCycle = hap.part?.end ?? hap.whole?.end ?? hapStartCycle + 0.25;
    const hapStartSec = hapStartCycle / cps;
    const hapEndSec = hapEndCycle / cps;
    
    // Convert to chunk-relative time
    const relStart = hapStartSec - chunkStart;
    const relEnd = hapEndSec - chunkStart;
    
    if (relStart >= chunkDur || relEnd <= 0) continue;
    
    const v = hap.value;
    if (typeof v !== 'object' || v === null) continue;
    
    const gain = Math.min(v.gain ?? 0.3, 1.0);
    if (gain <= 0.001) continue;
    
    const sound = v.s || '';
    const nVal = v.n !== undefined ? Math.round(Number(v.n)) : 0;
    const pan = v.pan ?? 0.5;
    const panL = Math.cos(pan * Math.PI / 2);
    const panR = Math.sin(pan * Math.PI / 2);
    
    const sampleKey = `${sound}:${nVal}`;
    const sampleBuf = sampleBufferData.get(sampleKey) || sampleBufferData.get(sound);
    
    if (sampleBuf) {
      // ── Pitch-shift logic ──
      // Determine if we need to pitch-shift this sample
      let activeBuf = sampleBuf;
      let playbackRate = 1.0;
      
      if (v.note) {
        const targetMidi = noteToMidi(v.note);
        const rootMidi = detectRootNote(sound);
        const semitoneOffset = targetMidi - rootMidi;
        
        if (Math.abs(semitoneOffset) > 0.01) {
          const perc = isPercussive(sound);
          if (perc) {
            // Percussive mode: playback rate resampling (changes duration)
            playbackRate = Math.pow(2, semitoneOffset / 12);
          } else {
            // Tonal mode: duration-preserving pitch shift via resample + WSOLA
            const cacheKey = `${sound}:${nVal}:ps:${semitoneOffset.toFixed(2)}`;
            let cached = sampleBufferData.get(cacheKey);
            if (!cached) {
              cached = pitchShiftBuffer(sampleBuf, semitoneOffset, false);
              sampleBufferData.set(cacheKey, cached);
              if (!renderChunk._loggedTonal) { renderChunk._loggedTonal = {}; }
              const lk = `${sound}:${v.note}`;
              if (!renderChunk._loggedTonal[lk]) {
                console.log(`  🎵 Pitch-shift: ${sound} note=${v.note} (${semitoneOffset > 0 ? '+' : ''}${semitoneOffset} st)`);
                renderChunk._loggedTonal[lk] = true;
              }
            }
            activeBuf = cached;
          }
        }
      }
      
      if (v.speed) playbackRate *= Math.abs(v.speed);
      
      const sampleDur = activeBuf.length / (activeBuf.sampleRate * playbackRate);
      const clipVal = v.clip !== undefined ? Number(v.clip) : 0;
      const effectiveEndSec = clipVal >= 1
        ? relStart + sampleDur
        : Math.min(relEnd, relStart + sampleDur);
      
      const fadeIn = 0.003;  // 3ms
      const fadeOut = 0.01;  // 10ms
      
      const startIdx = Math.max(0, Math.floor(relStart * sampleRate));
      const endIdx = Math.min(numSamples, Math.ceil(effectiveEndSec * sampleRate));
      
      for (let i = startIdx; i < endIdx; i++) {
        const t = i / sampleRate;
        const relT = t - relStart;
        if (relT < 0) continue;
        
        // Envelope
        let env = gain;
        if (relT < fadeIn) env *= relT / fadeIn;
        const timeToEnd = effectiveEndSec - relStart - relT;
        if (timeToEnd < fadeOut) env *= Math.max(0, timeToEnd / fadeOut);
        
        // Sample position with playback rate
        const samplePos = relT * activeBuf.sampleRate * playbackRate;
        const sIdx = Math.floor(samplePos);
        if (sIdx >= activeBuf.length) break;
        
        // Linear interpolation
        const frac = samplePos - sIdx;
        const s0 = activeBuf.data[0][sIdx];
        const s1 = sIdx + 1 < activeBuf.length ? activeBuf.data[0][sIdx + 1] : s0;
        const sample = s0 + frac * (s1 - s0);
        
        left[i] += sample * env * panL;
        if (activeBuf.channels > 1) {
          const sr0 = activeBuf.data[1][sIdx];
          const sr1 = sIdx + 1 < activeBuf.length ? activeBuf.data[1][sIdx + 1] : sr0;
          right[i] += (sr0 + frac * (sr1 - sr0)) * env * panR;
        } else {
          right[i] += sample * env * panR;
        }
      }
      scheduled++;
    } else if (waveMap[sound]) {
      // Synth oscillator
      let freq = v.freq || (v.note ? noteToFreq(v.note) : 440);
      const oscType = waveMap[sound];
      const attack = v.attack ?? 0.005;
      const decay = v.decay ?? 0.1;
      const sustain = v.sustain ?? 0.7;
      const release = v.release ?? 0.3;
      
      const startIdx = Math.max(0, Math.floor(relStart * sampleRate));
      const endIdx = Math.min(numSamples, Math.ceil((relEnd + 0.01) * sampleRate));
      
      for (let i = startIdx; i < endIdx; i++) {
        const t = i / sampleRate;
        const relT = t - relStart;
        if (relT < 0) continue;
        
        // ADSR
        let env;
        const hapDur = relEnd - relStart;
        if (relT < attack) env = gain * (relT / attack);
        else if (relT < attack + decay) env = gain * (1 - (1 - sustain) * (relT - attack) / decay);
        else if (relT < hapDur - release) env = gain * sustain;
        else env = gain * sustain * Math.max(0, (hapDur - relT) / release);
        
        // Oscillator
        let sample;
        const phase = relT * freq;
        const frac = phase - Math.floor(phase);
        switch (oscType) {
          case 'sine': sample = Math.sin(2 * Math.PI * phase); break;
          case 'triangle': sample = 4 * Math.abs(frac - 0.5) - 1; break;
          case 'sawtooth': sample = 2 * frac - 1; break;
          case 'square': sample = frac < 0.5 ? 1 : -1; break;
          default: sample = Math.sin(2 * Math.PI * phase);
        }
        
        left[i] += sample * env * panL;
        right[i] += sample * env * panR;
      }
      scheduled++;
    }
    // else: unrecognized sound, skip
  }
  
  return { left, right, scheduled, haps: haps.length };
}

// ── Main: chunk loop ──
// Two-pass approach: render into float buffers, find peak, then normalize and write.
console.log(`Rendering ${totalCycles} cycles in chunks of ${chunkSize}...`);

const allFloatChunks = [];  // Store raw float data for normalization pass
let totalScheduled = 0;
let totalHaps = 0;
let globalPeak = 0;

for (let c = 0; c < totalCycles; c += chunkSize) {
  const end = Math.min(c + chunkSize, totalCycles);
  const { left, right, scheduled, haps } = renderChunk(c, end, pattern, actualCps);
  totalScheduled += scheduled;
  totalHaps += haps;
  
  // Track raw peak levels
  for (let i = 0; i < left.length; i++) {
    const al = Math.abs(left[i]);
    const ar = Math.abs(right[i]);
    if (al > globalPeak) globalPeak = al;
    if (ar > globalPeak) globalPeak = ar;
  }
  
  allFloatChunks.push({ left, right });
  
  if ((c / chunkSize) % 5 === 0 || end >= totalCycles) {
    const pct = Math.round(end / totalCycles * 100);
    const memMB = Math.round(process.memoryUsage().heapUsed / 1024 / 1024);
    console.log(`  [${pct}%] Cycles ${c}-${end}: ${scheduled} events scheduled (${memMB}MB heap)`);
  }
}

console.log(`  Total: ${totalScheduled}/${totalHaps} haps scheduled`);
console.log(`  🔊 Raw peak: ${globalPeak.toFixed(4)} (${(20*Math.log10(globalPeak)).toFixed(1)} dBFS)`);

// ── Normalize and convert to 16-bit PCM ──
// Target: -3 dBTP (peak at 0.708) to leave headroom for MP3 encoding
const targetPeak = 0.708; // -3 dBTP
const normGain = globalPeak > 0 ? targetPeak / globalPeak : 1.0;
console.log(`  📐 Normalizing: gain = ${normGain.toFixed(6)} (${(20*Math.log10(normGain)).toFixed(1)} dB)`);

const allPcmChunks = [];
for (const { left, right } of allFloatChunks) {
  const pcm = Buffer.alloc(left.length * 4);
  for (let i = 0; i < left.length; i++) {
    const l = Math.max(-1, Math.min(1, left[i] * normGain));
    const r = Math.max(-1, Math.min(1, right[i] * normGain));
    pcm.writeInt16LE(Math.round(l * 32767), i * 4);
    pcm.writeInt16LE(Math.round(r * 32767), i * 4 + 2);
  }
  allPcmChunks.push(pcm);
}

// Free float buffers
allFloatChunks.length = 0;

// ── Concatenate and write WAV ──
const pcm = Buffer.concat(allPcmChunks);

const wav = makeWav(pcm, sampleRate, 2, 16);
writeFileSync(output, wav);
const durationSec = pcm.length / 4 / sampleRate;
console.log(`✅ ${output} (${(wav.length / 1024 / 1024).toFixed(1)}MB, ${durationSec.toFixed(1)}s)`);
process.exit(0);

function makeWav(pcm, sr, ch, bits) {
  const h = Buffer.alloc(44);
  h.write('RIFF', 0);
  h.writeUInt32LE(36 + pcm.length, 4);
  h.write('WAVE', 8);
  h.write('fmt ', 12);
  h.writeUInt32LE(16, 16);
  h.writeUInt16LE(1, 20);
  h.writeUInt16LE(ch, 22);
  h.writeUInt32LE(sr, 24);
  h.writeUInt32LE(sr * ch * bits / 8, 28);
  h.writeUInt16LE(ch * bits / 8, 32);
  h.writeUInt16LE(bits, 34);
  h.write('data', 36);
  h.writeUInt32LE(pcm.length, 40);
  return Buffer.concat([h, pcm]);
}
