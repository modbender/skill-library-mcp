/**
 * DTMF tone generation as mu-law 8kHz audio for Twilio media streams.
 *
 * Each DTMF tone is a combination of two sine wave frequencies from the
 * standard telephony matrix. Generated as PCM, converted to mu-law,
 * and base64 encoded for transmission over the Twilio WebSocket.
 */

const DTMF_FREQUENCIES: Record<string, [number, number]> = {
  "1": [697, 1209],
  "2": [697, 1336],
  "3": [697, 1477],
  "A": [697, 1633],
  "4": [770, 1209],
  "5": [770, 1336],
  "6": [770, 1477],
  "B": [770, 1633],
  "7": [852, 1209],
  "8": [852, 1336],
  "9": [852, 1477],
  "C": [852, 1633],
  "*": [941, 1209],
  "0": [941, 1336],
  "#": [941, 1477],
  "D": [941, 1633],
};

const SAMPLE_RATE = 8000;
const TONE_DURATION_MS = 200;
const TONE_AMPLITUDE = 0.5;

/**
 * Convert a 16-bit linear PCM sample to 8-bit mu-law.
 */
function linearToMulaw(sample: number): number {
  const MU = 255;
  const MAX = 32768;

  // Clamp
  sample = Math.max(-MAX, Math.min(MAX - 1, sample));

  const sign = sample < 0 ? 0x80 : 0;
  const magnitude = Math.abs(sample);

  // Mu-law compression
  const compressed = Math.log1p((magnitude / MAX) * MU) / Math.log1p(MU);
  const quantized = Math.floor(compressed * 127);

  return ~(sign | quantized) & 0xff;
}

/**
 * Generate a DTMF tone as base64-encoded mu-law audio.
 */
export function generateDtmfTone(digit: string): string {
  const freqs = DTMF_FREQUENCIES[digit.toUpperCase()];
  if (!freqs) {
    throw new Error(`Invalid DTMF digit: ${digit}`);
  }

  const [f1, f2] = freqs;
  const numSamples = Math.floor(SAMPLE_RATE * (TONE_DURATION_MS / 1000));
  const buffer = new Uint8Array(numSamples);

  for (let i = 0; i < numSamples; i++) {
    const t = i / SAMPLE_RATE;
    const pcm =
      (Math.sin(2 * Math.PI * f1 * t) + Math.sin(2 * Math.PI * f2 * t)) *
      TONE_AMPLITUDE *
      16384; // Scale to 16-bit range
    buffer[i] = linearToMulaw(Math.round(pcm));
  }

  return Buffer.from(buffer).toString("base64");
}

/**
 * Generate a sequence of DTMF tones with gaps between them.
 * Returns an array of base64-encoded mu-law audio chunks.
 */
export function generateDtmfSequence(digits: string): string[] {
  return digits.split("").map((d) => generateDtmfTone(d));
}
