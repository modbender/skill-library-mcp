// synth.mjs — Minimal software synthesizer for Strudel pattern events
// Renders pattern haps to PCM audio without any browser/WebAudio dependency.
// Supports oscillator synthesis AND sample playback from WAV files.

import { readFileSync, readdirSync, existsSync } from "node:fs";
import path from "node:path";

const TWO_PI = Math.PI * 2;

// ──────────────────────────────────────────────────
// Sample loading — reads WAV files from samples/ dir
// ──────────────────────────────────────────────────

const sampleCache = new Map();  // "bd:0" → Float32Array

/**
 * Load all WAV samples from a samples directory.
 * Structure: samplesDir/<name>/<files>.wav
 * Each dir becomes a sample bank (bd, sd, hh, etc.)
 */
export function loadSamples(samplesDir) {
  if (!existsSync(samplesDir)) return;
  for (const dir of readdirSync(samplesDir, { withFileTypes: true })) {
    if (!dir.isDirectory()) continue;
    const bankPath = path.join(samplesDir, dir.name);
    const files = readdirSync(bankPath)
      .filter(f => /\.wav$/i.test(f))
      .sort();
    files.forEach((f, idx) => {
      const key = `${dir.name}:${idx}`;
      try {
        sampleCache.set(key, readWavPcm(path.join(bankPath, f)));
      } catch { /* skip unreadable files */ }
    });
  }
  const banks = new Set([...sampleCache.keys()].map(k => k.split(':')[0]));
  console.error(`  Samples loaded: ${sampleCache.size} files in ${banks.size} banks`);
}

/**
 * Read a WAV file and return mono Float32Array of samples.
 * Supports 16-bit and 24-bit PCM.
 */
function readWavPcm(filePath) {
  const buf = readFileSync(filePath);
  // Find 'fmt ' chunk
  let fmtOffset = buf.indexOf('fmt ', 0, 'ascii');
  if (fmtOffset < 0) throw new Error('No fmt chunk');
  fmtOffset += 4; // skip 'fmt '
  const fmtSize = buf.readUInt32LE(fmtOffset); fmtOffset += 4;
  const audioFormat = buf.readUInt16LE(fmtOffset);
  const numChannels = buf.readUInt16LE(fmtOffset + 2);
  const sampleRate = buf.readUInt32LE(fmtOffset + 4);
  const bitsPerSample = buf.readUInt16LE(fmtOffset + 14);

  if (audioFormat !== 1) throw new Error(`Unsupported format: ${audioFormat}`);

  // Find 'data' chunk
  let dataOffset = buf.indexOf('data', fmtOffset, 'ascii');
  if (dataOffset < 0) throw new Error('No data chunk');
  dataOffset += 4; // skip 'data'
  const dataSize = buf.readUInt32LE(dataOffset); dataOffset += 4;

  const bytesPerSample = bitsPerSample / 8;
  const numSamples = Math.floor(dataSize / (bytesPerSample * numChannels));
  const pcm = new Float32Array(numSamples);

  for (let i = 0; i < numSamples; i++) {
    const offset = dataOffset + i * numChannels * bytesPerSample;
    // Read first channel only (mono mixdown)
    if (bitsPerSample === 16) {
      pcm[i] = buf.readInt16LE(offset) / 32768;
    } else if (bitsPerSample === 24) {
      const val = buf.readUIntLE(offset, 3);
      pcm[i] = (val > 0x7fffff ? val - 0x1000000 : val) / 8388608;
    } else if (bitsPerSample === 8) {
      pcm[i] = (buf.readUInt8(offset) - 128) / 128;
    }
  }
  return pcm;
}

/**
 * Get a sample by bank name and index (n).
 * Returns Float32Array or null.
 */
function getSample(bankName, n = 0) {
  const key = `${bankName}:${n}`;
  if (sampleCache.has(key)) return sampleCache.get(key);
  // Try index 0 if requested index doesn't exist
  const fallback = `${bankName}:0`;
  return sampleCache.get(fallback) ?? null;
}

/** Check if a name is a known oscillator type */
function isOscillator(name) {
  return name in oscillators;
}

/**
 * Convert a note name or MIDI number to frequency in Hz.
 */
export function noteToFreq(note) {
  if (typeof note === 'number') {
    return 440 * Math.pow(2, (note - 69) / 12);
  }
  if (typeof note === 'string') {
    const match = note.match(/^([a-gA-G])([#b]?)(\d+)$/);
    if (!match) return 440;
    const names = { c: 0, d: 2, e: 4, f: 5, g: 7, a: 9, b: 11 };
    let semitone = names[match[1].toLowerCase()] ?? 0;
    if (match[2] === '#') semitone += 1;
    if (match[2] === 'b') semitone -= 1;
    const octave = parseInt(match[3], 10);
    const midi = (octave + 1) * 12 + semitone;
    return 440 * Math.pow(2, (midi - 69) / 12);
  }
  return 440;
}

/**
 * Oscillator functions: sample → [-1, 1]
 */
const oscillators = {
  sine: (phase) => Math.sin(TWO_PI * phase),
  square: (phase) => (phase % 1) < 0.5 ? 1 : -1,
  sawtooth: (phase) => 2 * (phase % 1) - 1,
  triangle: (phase) => {
    const p = phase % 1;
    return p < 0.5 ? 4 * p - 1 : 3 - 4 * p;
  },
};

/**
 * Simple ADSR envelope.
 */
function envelope(t, duration, attack = 0.01, decay = 0.1, sustain = 0.7, release = 0.05) {
  if (t < 0) return 0;
  if (t < attack) return t / attack;
  if (t < attack + decay) return 1 - (1 - sustain) * ((t - attack) / decay);
  if (t < duration - release) return sustain;
  if (t < duration) return sustain * (1 - (t - (duration - release)) / release);
  return 0;
}

/**
 * Simple low-pass filter (one-pole IIR).
 */
function lpfCoeff(cutoffHz, sampleRate) {
  const dt = 1 / sampleRate;
  const rc = 1 / (TWO_PI * cutoffHz);
  return dt / (rc + dt);
}

/**
 * Extract haps (events) from a Strudel pattern for a given time span.
 */
export function queryPattern(pattern, startCycle, endCycle) {
  const haps = [];
  try {
    // Strudel Pattern.queryArc returns haps
    const result = pattern.queryArc(startCycle, endCycle);
    if (Array.isArray(result)) {
      return result;
    }
    // Some versions return an iterator
    if (result && typeof result[Symbol.iterator] === 'function') {
      for (const hap of result) {
        haps.push(hap);
      }
    }
  } catch (e) {
    // Fallback: try firstCycle/lastCycle
    try {
      for (let c = Math.floor(startCycle); c < Math.ceil(endCycle); c++) {
        const cycleHaps = pattern.firstCycle?.(c) ?? [];
        haps.push(...cycleHaps);
      }
    } catch {
      // Pattern may not support this query method
    }
  }
  return haps;
}

/**
 * Render a set of haps to stereo PCM float arrays.
 *
 * @param {Array} haps - Strudel hap objects with .whole, .value
 * @param {number} durationSec - Total duration in seconds
 * @param {number} sampleRate - Sample rate (default 44100)
 * @returns {[Float32Array, Float32Array]} - [left, right] channels
 */
export function renderHapsToAudio(haps, durationSec, sampleRate = 44100) {
  const numSamples = Math.ceil(durationSec * sampleRate);
  const left = new Float32Array(numSamples);
  const right = new Float32Array(numSamples);

  for (const hap of haps) {
    if (!hap?.whole) continue;

    const value = hap.value ?? {};
    const startSec = Number(hap.whole.begin) * durationSec / (Number(hap.whole.end) > 0 ? Number(hap.whole.end) : 1);
    const endSec = Number(hap.whole.end) * durationSec / (Number(hap.whole.end) > 0 ? Number(hap.whole.end) : 1);

    const hapStartSec = hap._renderStart ?? startSec;
    const hapEndSec = hap._renderEnd ?? endSec;
    const hapDuration = hapEndSec - hapStartSec;
    if (hapDuration <= 0) continue;

    // Extract common parameters
    const gain = value.gain ?? 0.3;
    const pan = value.pan ?? 0.5;
    const cutoff = value.lpf ?? value.cutoff ?? 20000;
    const hpf = value.hpf ?? 0;
    const sName = value.s ?? value.wave ?? 'sine';
    const sampleN = value.n ?? 0;

    const startSample = Math.max(0, Math.floor(hapStartSec * sampleRate));
    const panL = Math.cos(pan * Math.PI / 2);
    const panR = Math.sin(pan * Math.PI / 2);

    // Route: sample playback vs oscillator synthesis
    if (!isOscillator(sName) && !value.note && !value.freq) {
      // ── SAMPLE PLAYBACK ──
      const pcm = getSample(sName, sampleN);
      if (!pcm) continue;  // unknown sample, skip silently

      const sampleLen = pcm.length;
      
      // Determine playback speed (for pitch shifting via .speed())
      const speed = value.speed ?? 1;
      
      // Determine how long this hap should play:
      // If loopAt is set, or if clip/slow create a window longer than the sample,
      // loop the sample to fill the entire hap duration.
      // Otherwise play once (one-shot).
      const hapDurationSamples = Math.ceil(hapDuration * sampleRate);
      const loopAt = value.loopAt;
      const clip = value.clip;
      
      // Loop if: loopAt is set, OR the hap duration exceeds the sample length
      // (which means .slow() created a window the sample can't fill alone)
      const shouldLoop = loopAt != null || hapDurationSamples > sampleLen;
      
      const endSampleIdx = shouldLoop
        ? Math.min(numSamples, startSample + hapDurationSamples)
        : Math.min(numSamples, startSample + Math.ceil(sampleLen / Math.abs(speed || 1)));

      const alpha = lpfCoeff(Math.min(cutoff, sampleRate / 2), sampleRate);
      const hpfAlpha = hpf > 0 ? lpfCoeff(Math.min(hpf, sampleRate / 2), sampleRate) : 0;
      let filteredL = 0, filteredR = 0;
      let hpPrevL = 0, hpPrevR = 0;
      
      // Crossfade length for loop points (avoid clicks at loop boundary)
      const xfadeSamples = Math.min(2205, Math.floor(sampleLen * 0.05)); // 50ms or 5% of sample

      for (let i = startSample; i < endSampleIdx; i++) {
        const srcIdxRaw = (i - startSample) * Math.abs(speed || 1);
        let raw;
        
        if (shouldLoop && sampleLen > 0) {
          // Loop with crossfade at boundaries
          const pos = srcIdxRaw % sampleLen;
          const idx = Math.floor(pos);
          const frac = pos - idx;
          
          // Linear interpolation for smooth playback at non-integer speeds
          const s0 = pcm[idx % sampleLen];
          const s1 = pcm[(idx + 1) % sampleLen];
          let sample = s0 + frac * (s1 - s0);
          
          // Crossfade near loop boundary to avoid click
          const distToEnd = sampleLen - pos;
          if (distToEnd < xfadeSamples && xfadeSamples > 0) {
            const fadeOut = distToEnd / xfadeSamples;
            const fadeIn = 1 - fadeOut;
            // Blend with beginning of sample
            const loopPos = pos - (sampleLen - xfadeSamples);
            const loopIdx = Math.max(0, Math.floor(loopPos));
            const loopSample = pcm[loopIdx % sampleLen];
            sample = sample * fadeOut + loopSample * fadeIn;
          }
          
          raw = sample * gain;
        } else {
          // One-shot playback
          const srcIdx = Math.floor(srcIdxRaw);
          if (srcIdx >= sampleLen) break;
          raw = pcm[srcIdx] * gain;
        }

        // LPF
        filteredL = filteredL + alpha * (raw * panL - filteredL);
        filteredR = filteredR + alpha * (raw * panR - filteredR);

        // Optional HPF (one-pole)
        if (hpf > 0) {
          const outL = filteredL - hpPrevL; hpPrevL = filteredL; filteredL = outL;
          const outR = filteredR - hpPrevR; hpPrevR = filteredR; filteredR = outR;
        }

        left[i] += filteredL;
        right[i] += filteredR;
      }
    } else {
      // ── OSCILLATOR SYNTHESIS ──
      const oscName = isOscillator(sName) ? sName : 'sine';
      const oscFn = oscillators[oscName];
      const freq = value.freq ?? noteToFreq(value.note ?? value.n ?? 60);
      const attack = value.attack ?? 0.01;
      const decay = value.decay ?? 0.1;
      const sustain = value.sustain ?? 0.7;
      const release = value.release ?? 0.05;

      const endSampleIdx = Math.min(numSamples, Math.ceil(hapEndSec * sampleRate));

      const alpha = lpfCoeff(Math.min(cutoff, sampleRate / 2), sampleRate);
      const hpfAlpha = hpf > 0 ? lpfCoeff(Math.min(hpf, sampleRate / 2), sampleRate) : 0;
      let filteredL = 0, filteredR = 0;
      let hpPrevL = 0, hpPrevR = 0;
      let phase = 0;
      const phaseInc = freq / sampleRate;

      for (let i = startSample; i < endSampleIdx; i++) {
        const t = (i - startSample) / sampleRate;
        const env = envelope(t, hapDuration, attack, decay, sustain, release);
        const raw = oscFn(phase) * env * gain;
        phase += phaseInc;

        // LPF
        filteredL = filteredL + alpha * (raw * panL - filteredL);
        filteredR = filteredR + alpha * (raw * panR - filteredR);

        // Optional HPF
        if (hpf > 0) {
          const outL = filteredL - hpPrevL; hpPrevL = filteredL; filteredL = outL;
          const outR = filteredR - hpPrevR; hpPrevR = filteredR; filteredR = outR;
        }

        left[i] += filteredL;
        right[i] += filteredR;
      }
    }
  }

  // Soft clip to prevent clipping
  for (let i = 0; i < numSamples; i++) {
    left[i] = Math.tanh(left[i]);
    right[i] = Math.tanh(right[i]);
  }

  return [left, right];
}
