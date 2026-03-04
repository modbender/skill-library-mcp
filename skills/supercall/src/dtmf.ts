/**
 * DTMF Tone Generator
 *
 * Generates µ-law (8kHz, mono) encoded DTMF audio for injection into
 * Twilio media streams. This allows the AI to navigate phone trees (IVR)
 * by sending touch-tone digits directly through the audio stream.
 *
 * No external dependencies — µ-law encoding is pure math.
 */

const SAMPLE_RATE = 8000;

/**
 * Standard ITU DTMF frequency pairs.
 *
 *         1209 Hz  1336 Hz  1477 Hz  1633 Hz
 * 697 Hz    1        2        3        A
 * 770 Hz    4        5        6        B
 * 852 Hz    7        8        9        C
 * 941 Hz    *        0        #        D
 */
const DTMF_FREQUENCIES: Record<string, [number, number]> = {
  "1": [697, 1209],
  "2": [697, 1336],
  "3": [697, 1477],
  A: [697, 1633],
  "4": [770, 1209],
  "5": [770, 1336],
  "6": [770, 1477],
  B: [770, 1633],
  "7": [852, 1209],
  "8": [852, 1336],
  "9": [852, 1477],
  C: [852, 1633],
  "*": [941, 1209],
  "0": [941, 1336],
  "#": [941, 1477],
  D: [941, 1633],
};

/**
 * Convert a 16-bit linear PCM sample to 8-bit µ-law.
 * Standard ITU-T G.711 compression.
 */
function linearToMulaw(sample: number): number {
  const BIAS = 0x84; // 132
  const CLIP = 32635;
  const sign = sample < 0 ? 0x80 : 0;

  if (sample < 0) sample = -sample;
  if (sample > CLIP) sample = CLIP;

  sample += BIAS;

  let exponent = 7;
  let mask = 0x4000;
  while (exponent > 0 && (sample & mask) === 0) {
    exponent--;
    mask >>= 1;
  }

  const mantissa = (sample >> (exponent + 3)) & 0x0f;
  const mulaw = ~(sign | (exponent << 4) | mantissa) & 0xff;

  return mulaw;
}

/**
 * Generate µ-law encoded DTMF audio for a string of digits.
 *
 * @param digits - Characters to encode: 0-9, *, #, A-D, w (500ms pause)
 * @param options.toneDurationMs - Duration of each tone in ms (default: 100)
 * @param options.gapMs - Silence gap between tones in ms (default: 80)
 * @returns Single Buffer of µ-law audio containing all tones
 */
export function generateDtmfAudio(
  digits: string,
  options?: { toneDurationMs?: number; gapMs?: number },
): Buffer {
  const toneDurationMs = options?.toneDurationMs ?? 100;
  const gapMs = options?.gapMs ?? 80;
  const toneSamples = Math.floor((SAMPLE_RATE * toneDurationMs) / 1000);
  const gapSamples = Math.floor((SAMPLE_RATE * gapMs) / 1000);
  const pauseSamples = Math.floor((SAMPLE_RATE * 500) / 1000); // 'w' = 500ms

  // µ-law silence is 0xFF (linear zero maps to 0xFF)
  const SILENCE = 0xff;

  const chunks: Buffer[] = [];

  for (let i = 0; i < digits.length; i++) {
    const digit = digits[i].toUpperCase();

    if (digit === "W") {
      // 500ms pause
      const pause = Buffer.alloc(pauseSamples, SILENCE);
      chunks.push(pause);
      continue;
    }

    const freqs = DTMF_FREQUENCIES[digit];
    if (!freqs) {
      // Skip unknown characters
      continue;
    }

    const [f1, f2] = freqs;
    const tone = Buffer.alloc(toneSamples);

    // Amplitude ~65% of max to avoid clipping when two tones sum
    const amplitude = 0.65 * 16384; // ~10650 out of 32767

    for (let s = 0; s < toneSamples; s++) {
      const t = s / SAMPLE_RATE;
      const sample =
        amplitude * Math.sin(2 * Math.PI * f1 * t) +
        amplitude * Math.sin(2 * Math.PI * f2 * t);
      tone[s] = linearToMulaw(Math.round(sample));
    }

    chunks.push(tone);

    // Add gap after each tone (except the last)
    if (i < digits.length - 1) {
      const gap = Buffer.alloc(gapSamples, SILENCE);
      chunks.push(gap);
    }
  }

  return Buffer.concat(chunks);
}

/**
 * Split a DTMF audio buffer into frames suitable for Twilio media stream.
 *
 * @param audio - µ-law audio buffer from generateDtmfAudio
 * @param frameSize - Bytes per frame (default: 160 = 20ms at 8kHz µ-law)
 * @returns Array of frame Buffers
 */
export function chunkDtmfAudio(audio: Buffer, frameSize = 160): Buffer[] {
  const chunks: Buffer[] = [];

  for (let offset = 0; offset < audio.length; offset += frameSize) {
    const end = Math.min(offset + frameSize, audio.length);
    const chunk = Buffer.alloc(frameSize, 0xff); // Pad last frame with silence
    audio.copy(chunk, 0, offset, end);
    chunks.push(chunk);
  }

  return chunks;
}
