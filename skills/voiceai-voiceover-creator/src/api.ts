/**
 * Voice.ai API client — all HTTP calls in one place.
 *
 * Real endpoints from https://dev.voice.ai/api/v1
 * Includes --mock mode for full pipeline testing without API key.
 *
 * Reference: https://github.com/gizmoGremlin/openclaw-skill-voice-ai-voices
 */
import { probeDuration } from './ffmpeg.js';

/* ------------------------------------------------------------------ */
/*  Constants                                                          */
/* ------------------------------------------------------------------ */

const BASE_URL = 'https://dev.voice.ai';
const API_VERSION = 'v1';

export const AUDIO_FORMATS = {
  MP3: 'mp3',
  WAV: 'wav',
  PCM: 'pcm',
  MP3_44100_128: 'mp3_44100_128',
  MP3_44100_192: 'mp3_44100_192',
  WAV_22050: 'wav_22050',
  WAV_24000: 'wav_24000',
} as const;

export const MODELS = {
  TTS_V1_LATEST: 'voiceai-tts-v1-latest',
  MULTILINGUAL_V1_LATEST: 'voiceai-tts-multilingual-v1-latest',
} as const;

export const LANGUAGES = {
  en: 'English', es: 'Spanish', fr: 'French', de: 'German',
  it: 'Italian', pt: 'Portuguese', pl: 'Polish', ru: 'Russian',
  nl: 'Dutch', sv: 'Swedish', ca: 'Catalan',
} as const;

/* ------------------------------------------------------------------ */
/*  Types                                                              */
/* ------------------------------------------------------------------ */

export interface Voice {
  id: string;           // voice_id from API, normalized to `id`
  name: string;
  language: string;
  visibility?: string;  // PUBLIC | PRIVATE
  status?: string;      // PENDING | PROCESSING | AVAILABLE | FAILED
  gender?: string;
  style?: string;
  description?: string;
}

export interface TTSRequest {
  text: string;
  voice_id: string;
  audio_format?: string;
  temperature?: number;
  top_p?: number;
  model?: string;
  language?: string;
}

export interface TTSResponse {
  audio_data: Buffer;
  duration_seconds: number;
  sample_rate: number;
  format: string;
}

export interface VoiceListResponse {
  voices: Voice[];
  total: number;
}

/* ------------------------------------------------------------------ */
/*  Popular voices (real Voice.ai IDs)                                 */
/* ------------------------------------------------------------------ */

export const POPULAR_VOICES: Voice[] = [
  { id: 'd1bf0f33-8e0e-4fbf-acf8-45c3c6262513', name: 'Ellie', language: 'en', gender: 'female', style: 'Youthful, vibrant fashion vlogger', description: 'Youthful, vibrant — perfect for vlogs and social content.' },
  { id: 'f9e6a5eb-a7fd-4525-9e92-75125249c933', name: 'Oliver', language: 'en', gender: 'male', style: 'Friendly British, conversational', description: 'Friendly British tone — great for narration and tutorials.' },
  { id: '4388040c-8812-42f4-a264-f457a6b2b5b9', name: 'Lilith', language: 'en', gender: 'female', style: 'Soft, feminine', description: 'Soft, feminine — ideal for ASMR and calm content.' },
  { id: 'dbb271df-db25-4225-abb0-5200ba1426bc', name: 'Smooth Calm Voice', language: 'en', gender: 'male', style: 'Deep, smooth narrator', description: 'Deep, smooth narrator — documentaries and audiobooks.' },
  { id: '72d2a864-b236-402e-a166-a838ccc2c273', name: 'Corpse Husband', language: 'en', gender: 'male', style: 'Deep, distinctive YouTuber', description: 'Deep, distinctive — gaming and entertainment.' },
  { id: '559d3b72-3e79-4f11-9b62-9ec702a6c057', name: 'Skadi', language: 'en', gender: 'female', style: 'Anime, Arknights character', description: 'Anime-style character voice.' },
  { id: 'ed751d4d-e633-4bb0-8f5e-b5c8ddb04402', name: 'Zhongli', language: 'en', gender: 'male', style: 'Deep, Genshin Impact character', description: 'Deep, authoritative — gaming and dramatic content.' },
  { id: 'a931a6af-fb01-42f0-a8c0-bd14bc302bb1', name: 'Flora', language: 'en', gender: 'female', style: 'High pitch, cheerful', description: 'Cheerful, upbeat — kids content and bright promos.' },
  { id: 'bd35e4e6-6283-46b9-86b6-7cfa3dd409b9', name: 'Master Chief', language: 'en', gender: 'male', style: 'Deep heroic, Halo character', description: 'Heroic, commanding — gaming and action content.' },
];

/** Shorthand name → real voice_id lookup. */
export const VOICE_ALIASES: Record<string, string> = {
  ellie: 'd1bf0f33-8e0e-4fbf-acf8-45c3c6262513',
  oliver: 'f9e6a5eb-a7fd-4525-9e92-75125249c933',
  lilith: '4388040c-8812-42f4-a264-f457a6b2b5b9',
  smooth: 'dbb271df-db25-4225-abb0-5200ba1426bc',
  corpse: '72d2a864-b236-402e-a166-a838ccc2c273',
  skadi: '559d3b72-3e79-4f11-9b62-9ec702a6c057',
  zhongli: 'ed751d4d-e633-4bb0-8f5e-b5c8ddb04402',
  flora: 'a931a6af-fb01-42f0-a8c0-bd14bc302bb1',
  chief: 'bd35e4e6-6283-46b9-86b6-7cfa3dd409b9',
};

/** Resolve a voice alias ("ellie") or pass through a UUID unchanged. */
export function resolveVoiceId(input: string): string {
  return VOICE_ALIASES[input.toLowerCase()] ?? input;
}

/* ------------------------------------------------------------------ */
/*  WAV generator (mock mode)                                          */
/* ------------------------------------------------------------------ */

function generateMockWav(durationSeconds: number, sampleRate = 22050): Buffer {
  const numChannels = 1;
  const bitsPerSample = 16;
  const bytesPerSample = bitsPerSample / 8;
  const numSamples = Math.floor(sampleRate * durationSeconds);
  const dataSize = numSamples * numChannels * bytesPerSample;
  const headerSize = 44;
  const buffer = Buffer.alloc(headerSize + dataSize);

  // RIFF header
  buffer.write('RIFF', 0);
  buffer.writeUInt32LE(36 + dataSize, 4);
  buffer.write('WAVE', 8);

  // fmt sub-chunk (PCM)
  buffer.write('fmt ', 12);
  buffer.writeUInt32LE(16, 16);
  buffer.writeUInt16LE(1, 20);
  buffer.writeUInt16LE(numChannels, 22);
  buffer.writeUInt32LE(sampleRate, 24);
  buffer.writeUInt32LE(sampleRate * numChannels * bytesPerSample, 28);
  buffer.writeUInt16LE(numChannels * bytesPerSample, 32);
  buffer.writeUInt16LE(bitsPerSample, 34);

  // data sub-chunk
  buffer.write('data', 36);
  buffer.writeUInt32LE(dataSize, 40);

  // Generate an audible "mock speech" pattern
  const amp = 6000;
  const TWO_PI = 2 * Math.PI;

  for (let i = 0; i < numSamples; i++) {
    const t = i / sampleRate;
    const progress = i / numSamples;

    let envelope = 1.0;
    if (t < 0.05) envelope = t / 0.05;
    else if (progress > 0.9) envelope = (1.0 - progress) / 0.1;

    const vibrato = 1 + 0.15 * Math.sin(TWO_PI * 4.0 * t);
    const baseFreq = 180 * vibrato;
    let sample = Math.sin(TWO_PI * baseFreq * t);
    sample += 0.3 * Math.sin(TWO_PI * baseFreq * 1.5 * t);
    const cadence = 0.6 + 0.4 * Math.sin(TWO_PI * 2.0 * t);

    let cue = 0;
    if (t < 0.15) {
      const cueEnv = t < 0.02 ? t / 0.02 : (0.15 - t) / 0.13;
      cue = 0.7 * cueEnv * Math.sin(TWO_PI * 440 * t);
    }

    const value = Math.round(amp * envelope * (cadence * sample + cue));
    const clamped = Math.max(-32768, Math.min(32767, value));
    buffer.writeInt16LE(clamped, headerSize + i * 2);
  }

  return buffer;
}

/* ------------------------------------------------------------------ */
/*  Voice cache (in-memory, with TTL)                                  */
/* ------------------------------------------------------------------ */

interface CacheEntry<T> {
  data: T;
  expiresAt: number;
}

const voiceCache: { entry?: CacheEntry<VoiceListResponse> } = {};
const CACHE_TTL_MS = 10 * 60 * 1000; // 10 minutes

/* ------------------------------------------------------------------ */
/*  Helpers                                                            */
/* ------------------------------------------------------------------ */

/** Voice.ai per-request text length limit. */
const MAX_TEXT_LENGTH = 490; // API limit is 500; keep a small margin

/** Read the Voice.ai API key from environment (supports both naming conventions). */
export function getApiKey(): string | undefined {
  return process.env.VOICE_AI_API_KEY ?? process.env.VOICEAI_API_KEY;
}

/** Split text into chunks ≤ maxLen, respecting sentence boundaries. */
function splitTextForApi(text: string, maxLen = MAX_TEXT_LENGTH): string[] {
  if (text.length <= maxLen) return [text];

  const sentences = text.match(/[^.!?]+[.!?]+[\s]*/g);
  if (!sentences) {
    // No sentence boundaries — split by words
    const words = text.split(/\s+/);
    const chunks: string[] = [];
    let current = '';
    for (const word of words) {
      if ((current + ' ' + word).trim().length > maxLen && current) {
        chunks.push(current.trim());
        current = '';
      }
      current += (current ? ' ' : '') + word;
    }
    if (current.trim()) chunks.push(current.trim());
    return chunks.length ? chunks : [text.slice(0, maxLen)];
  }

  const chunks: string[] = [];
  let current = '';
  for (const sentence of sentences) {
    if ((current + sentence).length > maxLen && current) {
      chunks.push(current.trim());
      current = '';
    }
    current += sentence;
  }
  if (current.trim()) chunks.push(current.trim());
  return chunks;
}

/** Concatenate WAV buffers (all must share the same format). */
function concatWavBuffers(buffers: Buffer[]): Buffer {
  if (buffers.length === 1) return buffers[0];

  // Extract PCM data from each WAV (skip 44-byte header)
  const headerSize = 44;
  const dataParts = buffers.map((b) => b.subarray(headerSize));
  const totalDataSize = dataParts.reduce((s, d) => s + d.length, 0);

  // Build a new WAV with combined data, using header from first buffer
  const out = Buffer.alloc(headerSize + totalDataSize);
  buffers[0].copy(out, 0, 0, headerSize); // copy header from first
  out.writeUInt32LE(36 + totalDataSize, 4); // RIFF chunk size
  out.writeUInt32LE(totalDataSize, 40);      // data chunk size

  let offset = headerSize;
  for (const part of dataParts) {
    part.copy(out, offset);
    offset += part.length;
  }
  return out;
}

/** Concatenate raw audio buffers (MP3/other — just concat frames). */
function concatAudioBuffers(buffers: Buffer[]): Buffer {
  return buffers.length === 1 ? buffers[0] : Buffer.concat(buffers);
}

/** Estimate duration from audio buffer by writing to tmp and probing with ffprobe.
 *  Falls back to word-count heuristic if ffprobe unavailable. */
async function estimateDuration(audioBuffer: Buffer, text: string, tmpPath?: string): Promise<number> {
  if (tmpPath) {
    const { writeFile, unlink } = await import('node:fs/promises');
    try {
      await writeFile(tmpPath, audioBuffer);
      const dur = await probeDuration(tmpPath);
      await unlink(tmpPath).catch(() => {});
      if (dur !== null) return dur;
    } catch {
      // fall through
    }
  }
  // Heuristic: ~2.5 words/sec
  const words = text.split(/\s+/).filter(Boolean).length;
  return Math.max(0.5, words / 2.5);
}

/* ------------------------------------------------------------------ */
/*  API Client                                                         */
/* ------------------------------------------------------------------ */

export class VoiceAIClient {
  private apiKey: string | null;
  readonly mock: boolean;
  private baseUrl: string;

  constructor(options: { apiKey?: string; mock?: boolean }) {
    this.apiKey = options.apiKey ?? null;
    this.mock = options.mock ?? false;
    this.baseUrl = process.env.VOICEAI_API_BASE ?? BASE_URL;
  }

  private endpoint(path: string): string {
    return `${this.baseUrl}/api/${API_VERSION}${path}`;
  }

  /* ---------- Voices ------------------------------------------------ */

  async listVoices(options?: { limit?: number; query?: string; offset?: number }): Promise<VoiceListResponse> {
    if (this.mock) return this.mockListVoices(options);

    // Check cache
    if (voiceCache.entry && Date.now() < voiceCache.entry.expiresAt) {
      return this.filterVoices(voiceCache.entry.data, options);
    }

    const params = new URLSearchParams();
    if (options?.limit) params.set('limit', String(options.limit));
    if (options?.offset) params.set('offset', String(options.offset));

    const url = `${this.endpoint('/tts/voices')}?${params.toString()}`;

    const res = await fetch(url, {
      headers: {
        Authorization: `Bearer ${this.apiKey}`,
        'User-Agent': 'voiceai-creator-voiceover-pipeline/0.1.0',
      },
    });

    if (!res.ok) {
      const body = await res.text().catch(() => '');
      throw new Error(`Voice.ai API error ${res.status}: ${body}`);
    }

    const json = (await res.json()) as { voices: Array<Record<string, unknown>> };

    // Normalize voice_id → id
    const voices: Voice[] = (json.voices ?? []).map((v) => ({
      id: String(v.voice_id ?? v.id ?? ''),
      name: String(v.name ?? 'Unnamed'),
      language: String(v.language ?? 'en'),
      visibility: String(v.visibility ?? ''),
      status: String(v.status ?? ''),
    }));

    const data: VoiceListResponse = { voices, total: voices.length };
    voiceCache.entry = { data, expiresAt: Date.now() + CACHE_TTL_MS };
    return this.filterVoices(data, options);
  }

  /* ---------- TTS --------------------------------------------------- */

  async generateSpeech(request: TTSRequest, tmpDir?: string): Promise<TTSResponse> {
    if (this.mock) return this.mockGenerateSpeech(request);

    const audioFormat = request.audio_format ?? 'mp3';
    const language = request.language ?? 'en';

    // Auto-select model: multilingual for non-English
    const model = request.model ?? (
      language !== 'en' ? MODELS.MULTILINGUAL_V1_LATEST : MODELS.TTS_V1_LATEST
    );

    // Split long text into API-safe chunks
    const textChunks = splitTextForApi(request.text);
    const audioBuffers: Buffer[] = [];

    for (const chunk of textChunks) {
      const buf = await this.callTtsEndpoint(chunk, {
        voice_id: request.voice_id,
        audio_format: audioFormat,
        language,
        model,
        temperature: request.temperature,
        top_p: request.top_p,
      });
      audioBuffers.push(buf);
    }

    // Concatenate audio parts
    const audioBuffer = audioFormat === 'wav'
      ? concatWavBuffers(audioBuffers)
      : concatAudioBuffers(audioBuffers);

    // Estimate duration via ffprobe or heuristic
    const tmpPath = tmpDir ? `${tmpDir}/_probe_tmp.${audioFormat}` : undefined;
    const duration = await estimateDuration(audioBuffer, request.text, tmpPath);

    return {
      audio_data: audioBuffer,
      duration_seconds: duration,
      sample_rate: 32000,
      format: audioFormat,
    };
  }

  /** Single TTS API call (text must be ≤ 500 chars). */
  private async callTtsEndpoint(
    text: string,
    opts: {
      voice_id: string;
      audio_format: string;
      language: string;
      model: string;
      temperature?: number;
      top_p?: number;
    },
  ): Promise<Buffer> {
    const body: Record<string, unknown> = {
      text,
      audio_format: opts.audio_format,
      language: opts.language,
      model: opts.model,
    };
    if (opts.voice_id) body.voice_id = opts.voice_id;
    if (opts.temperature !== undefined) body.temperature = opts.temperature;
    if (opts.top_p !== undefined) body.top_p = opts.top_p;

    const res = await fetch(this.endpoint('/tts/speech'), {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${this.apiKey}`,
        'Content-Type': 'application/json',
        'User-Agent': 'voiceai-creator-voiceover-pipeline/0.1.0',
      },
      body: JSON.stringify(body),
    });

    if (!res.ok) {
      const errBody = await res.text().catch(() => '');
      if (res.status === 401) throw new Error('Voice.ai: Invalid or missing API key (401).');
      if (res.status === 402) throw new Error('Voice.ai: Insufficient credits (402). Check your dashboard.');
      if (res.status === 429) throw new Error('Voice.ai: Rate limited (429). Wait and retry.');
      throw new Error(`Voice.ai TTS error ${res.status}: ${errBody}`);
    }

    return Buffer.from(await res.arrayBuffer());
  }

  /* ---------- Mock implementations ---------------------------------- */

  private mockListVoices(options?: { limit?: number; query?: string }): VoiceListResponse {
    return this.filterVoices(
      { voices: POPULAR_VOICES, total: POPULAR_VOICES.length },
      options,
    );
  }

  private filterVoices(
    data: VoiceListResponse,
    options?: { limit?: number; query?: string },
  ): VoiceListResponse {
    let voices = [...data.voices];
    if (options?.query) {
      const q = options.query.toLowerCase();
      voices = voices.filter(
        (v) =>
          v.name.toLowerCase().includes(q) ||
          (v.style ?? '').toLowerCase().includes(q) ||
          (v.description ?? '').toLowerCase().includes(q) ||
          (v.gender ?? '').toLowerCase().includes(q),
      );
    }
    const total = voices.length;
    if (options?.limit) voices = voices.slice(0, options.limit);
    return { voices, total };
  }

  private mockGenerateSpeech(request: TTSRequest): TTSResponse {
    const wordCount = request.text.split(/\s+/).filter(Boolean).length;
    const duration = Math.max(0.5, wordCount / 2.5);
    const sampleRate = 22050;
    const audio = generateMockWav(duration, sampleRate);
    return {
      audio_data: audio,
      duration_seconds: duration,
      sample_rate: sampleRate,
      format: 'wav',
    };
  }
}
