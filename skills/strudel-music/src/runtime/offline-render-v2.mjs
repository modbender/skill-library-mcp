#!/usr/bin/env node
/**
 * Offline render v2: Strudel's real audio engine + node-web-audio-api
 * 
 * Evaluates pattern → queries haps → schedules via OfflineAudioContext
 * with proper oscillators, ADSR, filters, panning.
 *
 * Usage: node src/runtime/offline-render-v2.mjs <input.js> [output.wav] [cycles] [bpm]
 */

import { readFileSync, writeFileSync, readdirSync, existsSync } from 'fs';
import { createRequire } from 'module';
import path from 'path';

const require = createRequire(import.meta.url);

// ── Polyfill Web Audio for Node.js ──
const nwa = require('node-web-audio-api');
let _sharedCtx = null;
globalThis.AudioContext = class {
  constructor() {
    if (!_sharedCtx) {
      _sharedCtx = new nwa.OfflineAudioContext(2, 44100 * 600, 44100);
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

// Browser stubs
globalThis.window = {
  ...globalThis,
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

// ── Parse args ──
const input = process.argv[2];
const output = process.argv[3] || 'output.wav';
const cycles = parseInt(process.argv[4] || '8');
const bpm = parseInt(process.argv[5] || '120');

if (!input) {
  console.error('Usage: node src/runtime/offline-render-v2.mjs <input.js> [output.wav] [cycles] [bpm]');
  process.exit(1);
}

const cps = bpm / 60 / 4;
const duration = cycles / cps;
const sampleRate = 44100;
const totalSamples = Math.ceil(duration * sampleRate);

console.log(`Offline render: ${input} → ${output}`);
console.log(`  Cycles: ${cycles}, BPM: ${bpm}, CPS: ${cps.toFixed(3)}, Duration: ${duration.toFixed(1)}s`);

// ── Load Strudel ──
console.log('Loading Strudel...');
const core = await import('@strudel/core');
const mini = await import('@strudel/mini');
try { await import('@strudel/tonal'); } catch (e) { /* optional */ }

// CRITICAL: Manually register mini notation parser on the Pattern class.
// The dist bundles can have separate module instances, so mini's auto-registration
// may target a different Pattern. Same class of bug as openclaw/openclaw#22790.
if (core.setStringParser && mini.mini) {
  core.setStringParser(mini.mini);
}

// Register ALL Strudel exports (functions, signals, constants) on globalThis
let cpmValue = bpm / 4;
for (const [key, val] of Object.entries(core)) {
  globalThis[key] = val;
}
globalThis.setcpm = (v) => { cpmValue = v; };
globalThis.setcps = (v) => { cpmValue = v * 60; };
globalThis.samples = () => {};
globalThis.hush = () => {};

// Browser-only methods to strip from patterns before headless evaluation
const vizMethods = ['pianoroll', '_pianoroll', 'spiral', '_spiral', 'scope', '_scope', 'draw', '_draw'];

/**
 * Strip browser-only visualization methods using balanced-parenthesis scanning.
 * Handles nested parens, multi-line args, and string literals correctly.
 * e.g. `.pianoroll({ fold: 1, labels: true })` → removed
 *
 * Approach: find `.methodName(` then count balanced parens to find the close.
 * This is more reliable than regex for nested/multi-line args (fixes #4).
 */
function stripVizMethods(code) {
  for (const method of vizMethods) {
    // Match .method( or ._method( — we need to find each occurrence and remove it
    const pattern = new RegExp(`\\.(${method})\\s*\\(`, 'g');
    let match;
    while ((match = pattern.exec(code)) !== null) {
      const dotStart = match.index; // position of the '.'
      const parenStart = code.indexOf('(', dotStart + method.length + 1);
      if (parenStart === -1) continue;

      // Scan for balanced close paren, respecting strings
      let depth = 1;
      let i = parenStart + 1;
      let inStr = null; // null, "'", '"', '`'
      while (i < code.length && depth > 0) {
        const ch = code[i];
        if (inStr) {
          if (ch === '\\') { i += 2; continue; } // skip escaped chars
          if (ch === inStr) inStr = null;
        } else {
          if (ch === "'" || ch === '"' || ch === '`') inStr = ch;
          else if (ch === '(') depth++;
          else if (ch === ')') depth--;
        }
        i++;
      }
      if (depth === 0) {
        // Remove from dot to closing paren (inclusive)
        code = code.slice(0, dotStart) + code.slice(i);
        // Reset regex since string changed
        pattern.lastIndex = dotStart;
      }
    }
  }
  return code;
}

console.log('  ✅ Strudel loaded');

// ── Evaluate pattern ──
console.log('Evaluating pattern...');
let patternCode = readFileSync(input, 'utf8')
  .replace(/^\/\/ @\w+.*/gm, '')
  .trim();

// Strip visualization methods using balanced-paren scanner (fixes #4)
patternCode = stripVizMethods(patternCode);

// ── Security hardening: scrub sensitive globals before pattern eval ──
// Patterns are JS evaluated via new Function() in the current process.
// Remove access to environment variables and child_process to limit
// damage from malicious patterns. This is NOT a sandbox — patterns can
// still access fs, network, etc. For untrusted patterns, use a container.
const _savedEnv = process.env;
const _savedExec = process.execPath;
process.env = Object.freeze({ NODE_ENV: 'production' });
// Prevent require('child_process') by poisoning the module cache
const _savedCpModule = await import('module').then(m => {
  const orig = m.default._resolveFilename;
  m.default._resolveFilename = function(request, ...args) {
    if (request === 'child_process' || request === 'node:child_process') {
      throw new Error('child_process is blocked during pattern evaluation');
    }
    return orig.call(this, request, ...args);
  };
  return orig;
}).catch(() => null);

let pattern;
try {
  // Strudel patterns are typically: setcpm(...); stack(...).stuff()
  // The last expression is the pattern. We need to capture it.
  // Strategy: split into statements, wrap the last one in return.
  const lines = patternCode.split('\n');
  
  // Find the last non-empty, non-comment line that starts a pattern expression
  // Usually starts with stack(, note(, s(, n(, etc.
  let lastExprStart = -1;
  let depth = 0;
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i].trim();
    if (!line || line.startsWith('//')) continue;
    
    // Track if this line starts a new top-level expression
    if (depth === 0 && /^(stack|note|s|n|seq|cat|sequence|arrange|slowcat|fastcat)\s*\(/.test(line)) {
      lastExprStart = i;
    }
    // Track paren depth
    for (const ch of line) {
      if (ch === '(') depth++;
      if (ch === ')') depth--;
    }
  }
  
  if (lastExprStart >= 0) {
    const setup = lines.slice(0, lastExprStart).join('\n');
    const expr = lines.slice(lastExprStart).join('\n');
    const wrapped = setup + '\nreturn ' + expr;
    const fn = new Function(wrapped);
    pattern = fn();
  } else {
    // Try as-is, then with return
    try {
      const fn = new Function(patternCode);
      pattern = fn();
    } catch {
      const fn = new Function('return ' + patternCode);
      pattern = fn();
    }
  }
} catch (e) {
  console.error('  ❌ Pattern eval failed:', e.message);
  process.env = _savedEnv;  // Restore before exit
  process.exit(1);
} finally {
  // Restore environment after pattern evaluation
  process.env = _savedEnv;
  // Restore module resolution
  if (_savedCpModule) {
    import('module').then(m => { m.default._resolveFilename = _savedCpModule; }).catch(() => {});
  }
}

if (!pattern || typeof pattern.queryArc !== 'function') {
  console.error('  ❌ Pattern did not return a queryable pattern. Got:', typeof pattern);
  process.exit(1);
}

// ── Query haps ──
const actualCps = cpmValue / 60;
const actualDuration = cycles / actualCps;
const actualSamples = Math.ceil(actualDuration * sampleRate);

console.log(`  Using CPS: ${actualCps.toFixed(3)} (${cpmValue * 4} BPM), Duration: ${actualDuration.toFixed(1)}s`);

const haps = pattern.queryArc(0, cycles);
console.log(`  Found ${haps.length} haps`);

if (haps.length === 0) {
  console.error('  ⚠️ No haps. Output will be silence.');
}

// ── Load samples ──
const SAMPLES_DIR = path.resolve(
  import.meta.dirname || path.dirname(new URL(import.meta.url).pathname),
  '../../samples'
);
const sampleBuffers = new Map(); // "bd:0" → AudioBuffer

function loadWavToBuffer(filePath, ctx) {
  const raw = readFileSync(filePath);
  // Parse WAV header
  const view = new DataView(raw.buffer, raw.byteOffset, raw.byteLength);
  if (raw.toString('ascii', 0, 4) !== 'RIFF') return null;
  
  const channels = view.getUint16(22, true);
  const sr = view.getUint32(24, true);
  const bitsPerSample = view.getUint16(34, true);
  
  // Find data chunk
  let dataOffset = 12;
  while (dataOffset < raw.length - 8) {
    const chunkId = raw.toString('ascii', dataOffset, dataOffset + 4);
    const chunkSize = view.getUint32(dataOffset + 4, true);
    if (chunkId === 'data') {
      dataOffset += 8;
      const numSamples = chunkSize / (bitsPerSample / 8) / channels;
      const audioBuffer = ctx.createBuffer(channels, numSamples, sr);
      
      for (let ch = 0; ch < channels; ch++) {
        const channelData = audioBuffer.getChannelData(ch);
        for (let i = 0; i < numSamples; i++) {
          const byteIndex = dataOffset + (i * channels + ch) * (bitsPerSample / 8);
          if (bitsPerSample === 16) {
            channelData[i] = view.getInt16(byteIndex, true) / 32768;
          } else if (bitsPerSample === 24) {
            const s = (view.getUint8(byteIndex) | (view.getUint8(byteIndex+1) << 8) | (view.getInt8(byteIndex+2) << 16));
            channelData[i] = s / 8388608;
          }
        }
      }
      return audioBuffer;
    }
    dataOffset += 8 + chunkSize;
  }
  return null;
}

if (existsSync(SAMPLES_DIR)) {
  console.log('Loading samples...');
  let sampleCount = 0;
  // Preload a temporary OfflineAudioContext for buffer creation
  const tmpCtx = new nwa.OfflineAudioContext(2, 1, sampleRate);
  
  for (const dir of readdirSync(SAMPLES_DIR)) {
    const dirPath = path.join(SAMPLES_DIR, dir);
    try {
      const files = readdirSync(dirPath).filter(f => f.endsWith('.wav') || f.endsWith('.WAV')).sort();
      for (let i = 0; i < files.length; i++) {
        const buf = loadWavToBuffer(path.join(dirPath, files[i]), tmpCtx);
        if (buf) {
          sampleBuffers.set(`${dir}:${i}`, buf);
          if (i === 0) sampleBuffers.set(dir, buf); // default (index 0)
          sampleCount++;
        }
      }
    } catch { /* not a directory */ }
  }
  console.log(`  ✅ ${sampleCount} samples loaded from ${sampleBuffers.size} entries`);
} else {
  console.log('  ⚠️ No samples directory found. Sample-based sounds will be silent.');
}

// ── Render to OfflineAudioContext ──
console.log('Rendering...');
const offCtx = new nwa.OfflineAudioContext(2, actualSamples, sampleRate);

// Master compressor for clean output
// Gentler settings to avoid pumping artifacts on vocal material (#22)
const compressor = offCtx.createDynamicsCompressor();
compressor.threshold.setValueAtTime(-12, 0);
compressor.knee.setValueAtTime(10, 0);
compressor.ratio.setValueAtTime(4, 0);
compressor.connect(offCtx.destination);

// Oscillator type map (outside loop for performance)
const waveMap = {
  sine: 'sine', triangle: 'triangle', square: 'square',
  sawtooth: 'sawtooth', saw: 'sawtooth', tri: 'triangle',
  piano: 'triangle', bass: 'sawtooth', pluck: 'triangle',
  supersaw: 'sawtooth', supersquare: 'square', organ: 'sine',
};

const warnedSounds = new Set(); // track warned sound names to avoid spam
let scheduled = 0;
for (const hap of haps) {
  // Skip continuation fragments — only schedule onset haps.
  // Strudel's queryArc splits long events at integer cycle boundaries,
  // producing multiple haps with the same whole arc but different part arcs.
  // hasOnset() is true only for the first fragment (part.begin === whole.begin).
  // Without this filter, samples get stacked N times at the same start time (#22 v7).
  if (typeof hap.hasOnset === 'function' && !hap.hasOnset()) continue;

  const startCycle = hap.whole?.begin ?? hap.part?.begin ?? 0;
  const endCycle = hap.whole?.end ?? hap.part?.end ?? startCycle + 0.25;
  const hapStart = startCycle / actualCps;
  const hapDur = (endCycle - startCycle) / actualCps;

  if (hapStart >= actualDuration || hapStart < 0) continue;

  const v = hap.value;
  if (typeof v !== 'object' || v === null) continue;

  const gain = Math.min(v.gain ?? 0.3, 1.0);
  if (gain <= 0.001) continue; // Skip silent haps (saves memory on masked layers)
  const sound = v.s || '';
  const nVal = v.n !== undefined ? Math.round(Number(v.n)) : 0;
  const lpf = v.lpf ?? v.cutoff ?? 6000;
  const attack = v.attack ?? 0.005;
  const decay = v.decay ?? 0.1;
  const sustain = v.sustain ?? 0.7;
  const release = v.release ?? 0.3;
  const pan = v.pan ?? 0.5;

  // Check if this is a sample-based sound
  const sampleKey = `${sound}:${nVal}`;
  const sampleBuf = sampleBuffers.get(sampleKey) || sampleBuffers.get(sound);
  
  const isSynthSound = waveMap[sound] !== undefined;

  // Resolve note → frequency (for synth sounds)
  let freq = null;
  if (v.freq) freq = v.freq;
  else if (v.note) freq = noteToFreq(v.note);
  // TODO: resolve scale degree to freq using tonal's Scale.get() + degree mapping
  // Currently falls through to 440Hz for unresolved scale degrees
  else if (v.n !== undefined && isSynthSound) freq = 440;

  // Skip if neither sample nor synth — warn on unrecognized sounds
  if (!sampleBuf && !isSynthSound && sound) {
    if (!warnedSounds.has(sound)) {
      console.warn(`  ⚠️ Unrecognized sound "${sound}" — falling back to 440Hz synth`);
      warnedSounds.add(sound);
    }
    if (!freq) freq = 440;
  } else if (!sampleBuf && !freq && !isSynthSound) {
    if (!freq) freq = 440; // last resort fallback
  }

  try {
    const endTime = hapStart + hapDur;
    
    // Gain node
    const gn = offCtx.createGain();
    
    // Filter
    const flt = offCtx.createBiquadFilter();
    flt.type = 'lowpass';
    flt.frequency.setValueAtTime(Math.min(lpf, sampleRate / 2 - 100), hapStart);
    flt.Q.setValueAtTime(1.5, hapStart);
    
    // Panner
    const pnr = offCtx.createStereoPanner();
    pnr.pan.setValueAtTime((pan - 0.5) * 2, hapStart);

    if (sampleBuf) {
      // ── Sample playback ──
      const src = offCtx.createBufferSource();
      src.buffer = sampleBuf;
      
      // When clip=1, let the sample play its full natural duration
      // instead of cutting at the cycle/hap boundary (#22, dev#1)
      const clipVal = v.clip !== undefined ? Number(v.clip) : 0;
      
      // loopAt support: if loopAt is set OR the hap window exceeds the sample
      // length, enable looping so the sample fills the entire hap duration.
      // This is the offline-renderer counterpart to Ronan's synth.mjs loopfix.
      const loopAtVal = v.loopAt;
      const shouldLoop = loopAtVal != null || hapDur > sampleBuf.duration;
      
      if (shouldLoop) {
        src.loop = true;
        src.loopStart = 0;
        src.loopEnd = sampleBuf.duration;
      }
      
      const effectiveEnd = shouldLoop
        ? endTime  // fill the entire hap window when looping
        : clipVal >= 1
          ? hapStart + sampleBuf.duration
          : Math.min(endTime, hapStart + sampleBuf.duration);
      
      // Crossfade envelope: 30ms fade-in, 50ms fade-out (#22)
      // Replaces instant-on + 20ms fade-out which caused hard splice clicks
      const fadeIn = 0.03;   // 30ms
      const fadeOut = 0.05;  // 50ms
      const sampleEnd = effectiveEnd;
      gn.gain.setValueAtTime(0, hapStart);
      gn.gain.linearRampToValueAtTime(gain, hapStart + fadeIn);
      gn.gain.setValueAtTime(gain, Math.max(hapStart + fadeIn, sampleEnd - fadeOut));
      gn.gain.linearRampToValueAtTime(0, sampleEnd);
      
      // Apply playback rate if note specified (pitch shifting)
      if (v.note) {
        const semitones = noteToSemitones(v.note);
        if (semitones !== 0) src.playbackRate.setValueAtTime(Math.pow(2, semitones / 12), hapStart);
      }
      if (v.speed) src.playbackRate.setValueAtTime(Math.abs(v.speed), hapStart);
      
      src.connect(flt);
      flt.connect(gn);
      gn.connect(pnr);
      pnr.connect(compressor);
      
      src.start(hapStart);
      src.stop(sampleEnd + 0.05);
    } else {
      // ── Oscillator synth ──
      if (!freq) freq = 440;
      const oscType = waveMap[sound] || 'triangle';
      
      const osc = offCtx.createOscillator();
      osc.type = oscType;
      osc.frequency.setValueAtTime(freq, hapStart);

      // Slight detune for richness on saw/square
      if (oscType === 'sawtooth' || oscType === 'square') {
        osc.detune.setValueAtTime(Math.random() * 10 - 5, hapStart);
      }

      // ADSR envelope
      gn.gain.setValueAtTime(0, hapStart);
      gn.gain.linearRampToValueAtTime(gain, Math.min(hapStart + attack, endTime));
      gn.gain.linearRampToValueAtTime(gain * sustain, Math.min(hapStart + attack + decay, endTime));
      if (endTime - release > hapStart + attack + decay) {
        gn.gain.setValueAtTime(gain * sustain, endTime - release);
      }
      gn.gain.linearRampToValueAtTime(0, endTime + 0.01);

      osc.connect(flt);
      flt.connect(gn);
      gn.connect(pnr);
      pnr.connect(compressor);

      osc.start(hapStart);
      osc.stop(endTime + 0.05);
    }
    
    scheduled++;
  } catch (e) {
    // Skip problematic haps
  }
}

console.log(`  Scheduled ${scheduled}/${haps.length} haps`);

if (scheduled === 0) {
  console.error('  ❌ Nothing to render.');
  process.exit(1);
}

const buf = await offCtx.startRendering();
console.log(`  ✅ Rendered: ${buf.length} samples (${(buf.length / sampleRate).toFixed(1)}s)`);

// ── Master fade-out ──
// Apply 2-second linear fade-out to the end of the rendered buffer.
// Prevents the hard cliff exit heard in v7 (#22).
const fadeOutSeconds = 2;
const fadeOutSamples = Math.min(Math.ceil(fadeOutSeconds * sampleRate), buf.length);
const fadeOutStart = buf.length - fadeOutSamples;
for (let ch = 0; ch < buf.numberOfChannels; ch++) {
  const channelData = buf.getChannelData(ch);
  for (let i = 0; i < fadeOutSamples; i++) {
    const gain = 1 - (i / fadeOutSamples); // linear ramp from 1 → 0
    channelData[fadeOutStart + i] *= gain;
  }
}
console.log(`  ✅ Applied ${fadeOutSeconds}s master fade-out (${fadeOutSamples} samples)`);

// ── Write WAV ──
const left = buf.getChannelData(0);
const right = buf.numberOfChannels > 1 ? buf.getChannelData(1) : left;

const pcm = Buffer.alloc(buf.length * 4);
for (let i = 0; i < buf.length; i++) {
  pcm.writeInt16LE(Math.round(Math.max(-1, Math.min(1, left[i])) * 32767), i * 4);
  pcm.writeInt16LE(Math.round(Math.max(-1, Math.min(1, right[i])) * 32767), i * 4 + 2);
}

const wav = makeWav(pcm, sampleRate, 2, 16);
writeFileSync(output, wav);
console.log(`✅ ${output} (${(wav.length / 1024 / 1024).toFixed(1)}MB)`);
process.exit(0);

// ── Helpers ──
function noteToSemitones(note) {
  // Returns semitone offset from C4 (for sample pitch shifting)
  if (typeof note === 'number') return note - 60; // MIDI
  const m = String(note).match(/^([a-gA-G])(#|b|s)?(\d+)?$/);
  if (!m) return 0;
  const map = { c:0, d:2, e:4, f:5, g:7, a:9, b:11 };
  let semi = map[m[1].toLowerCase()] ?? 0;
  if (m[2] === '#' || m[2] === 's') semi++;
  if (m[2] === 'b') semi--;
  const oct = parseInt(m[3] ?? '4');
  return semi + (oct * 12) - 60; // offset from C4
}

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
