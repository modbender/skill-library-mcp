/**
 * Speech-to-Text providers
 */

import * as net from "node:net";
import type { DiscordVoiceConfig } from "./config.js";
import { validateWhisperModel, validateDeepgramModel } from "./config.js";
import { pipeline, env } from "@xenova/transformers";
import { WaveFile } from "wavefile";

/** Truncate API error bodies to prevent leaking sensitive information in logs */
function truncateError(text: string, maxLen = 200): string {
  return text.length > maxLen ? `${text.slice(0, maxLen)}…` : text;
}

// Disable local model checks if not using local models, but here we want local
env.allowLocalModels = true; // Allow loading from local file system
env.useBrowserCache = false; // Ensure Node cache is used

export interface STTResult {
  text: string;
  confidence?: number;
  language?: string;
}

export interface STTProvider {
  transcribe(audioBuffer: Buffer, sampleRate: number): Promise<STTResult>;
}

/**
 * OpenAI Whisper STT Provider
 */
export class WhisperSTT implements STTProvider {
  private apiKey: string;
  private model: string;

  constructor(config: DiscordVoiceConfig) {
    this.apiKey = config.openai?.apiKey || process.env["OPENAI_API_KEY"] || "";
    this.model = config.openai?.whisperModel || "whisper-1";

    if (!this.apiKey) {
      throw new Error("OpenAI API key required for Whisper STT");
    }
  }

  async transcribe(audioBuffer: Buffer, sampleRate: number): Promise<STTResult> {
    // Convert raw PCM to WAV format for Whisper API
    const wavBuffer = this.pcmToWav(audioBuffer, sampleRate);

    const formData = new FormData();
    formData.append("file", new Blob([new Uint8Array(wavBuffer)], { type: "audio/wav" }), "audio.wav");
    formData.append("model", this.model);
    formData.append("response_format", "json");

    const response = await fetch("https://api.openai.com/v1/audio/transcriptions", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${this.apiKey}`,
      },
      body: formData,
    });

    if (!response.ok) {
      const error = await response.text();
      throw new Error(`Whisper API error: ${response.status} ${truncateError(error)}`);
    }

    const result = (await response.json()) as { text: string; language?: string };
    return {
      text: result.text.trim(),
      language: result.language,
    };
  }

  /**
   * Convert raw PCM audio to WAV format
   */
  private pcmToWav(pcmBuffer: Buffer, sampleRate: number): Buffer {
    const wav = new WaveFile();
    wav.fromScratch(1, sampleRate, "16", pcmBuffer);
    return Buffer.from(wav.toBuffer());
  }
}

/** Shared PCM-to-WAV conversion for OpenAI transcribe providers */
function pcmToWavOpenAI(pcmBuffer: Buffer, sampleRate: number): Buffer {
  const numChannels = 1;
  const bitsPerSample = 16;
  const byteRate = (sampleRate * numChannels * bitsPerSample) / 8;
  const blockAlign = (numChannels * bitsPerSample) / 8;
  const dataSize = pcmBuffer.length;
  const headerSize = 44;
  const fileSize = headerSize + dataSize - 8;

  const buffer = Buffer.alloc(headerSize + dataSize);
  buffer.write("RIFF", 0);
  buffer.writeUInt32LE(fileSize, 4);
  buffer.write("WAVE", 8);
  buffer.write("fmt ", 12);
  buffer.writeUInt32LE(16, 16);
  buffer.writeUInt16LE(1, 20);
  buffer.writeUInt16LE(numChannels, 22);
  buffer.writeUInt32LE(sampleRate, 24);
  buffer.writeUInt32LE(byteRate, 28);
  buffer.writeUInt16LE(blockAlign, 32);
  buffer.writeUInt16LE(bitsPerSample, 34);
  buffer.write("data", 36);
  buffer.writeUInt32LE(dataSize, 40);
  pcmBuffer.copy(buffer, headerSize);
  return buffer;
}

/**
 * Generic OpenAI Transcribe STT Provider
 *
 * Uses the /audio/transcriptions endpoint with configurable models:
 * - gpt-4o-mini-transcribe (faster, lower cost)
 * - gpt-4o-transcribe (higher quality)
 * - gpt-4o-transcribe-diarize (speaker diarization)
 * See: https://platform.openai.com/docs/models
 */
export class OpenAITranscribeSTT implements STTProvider {
  private apiKey: string;
  private model: string;

  constructor(config: DiscordVoiceConfig, model: string) {
    this.apiKey = config.openai?.apiKey || process.env["OPENAI_API_KEY"] || "";
    this.model = model;

    if (!this.apiKey) {
      throw new Error("OpenAI API key required for OpenAI transcribe STT");
    }
  }

  async transcribe(audioBuffer: Buffer, sampleRate: number): Promise<STTResult> {
    const wavBuffer = pcmToWavOpenAI(audioBuffer, sampleRate);

    const formData = new FormData();
    formData.append("file", new Blob([new Uint8Array(wavBuffer)], { type: "audio/wav" }), "audio.wav");
    formData.append("model", this.model);
    formData.append("response_format", "json");

    const response = await fetch("https://api.openai.com/v1/audio/transcriptions", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${this.apiKey}`,
      },
      body: formData,
    });

    if (!response.ok) {
      const error = await response.text();
      throw new Error(`OpenAI transcribe API error (${this.model}): ${response.status} ${truncateError(error)}`);
    }

    const result = (await response.json()) as {
      text?: string;
      language?: string;
      segments?: Array<{ text: string }>;
    };

    // gpt-4o-transcribe-diarize returns segments; plain models return text
    const text = result.text ?? result.segments?.map((s) => s.text).join(" ") ?? "";
    return {
      text: text.trim(),
      language: result.language,
    };
  }
}

/**
 * Deepgram STT Provider
 */
export class DeepgramSTT implements STTProvider {
  private apiKey: string;
  private model: string;

  constructor(config: DiscordVoiceConfig) {
    this.apiKey = config.deepgram?.apiKey || process.env["DEEPGRAM_API_KEY"] || "";
    this.model = validateDeepgramModel(config.deepgram?.model || "nova-2");

    if (!this.apiKey) {
      throw new Error("Deepgram API key required for Deepgram STT");
    }
  }

  async transcribe(audioBuffer: Buffer, sampleRate: number): Promise<STTResult> {
    // Deepgram expects: encoding=linear16, sample_rate, channels=1
    const url = new URL("https://api.deepgram.com/v1/listen");
    url.searchParams.set("model", this.model);
    url.searchParams.set("encoding", "linear16");
    url.searchParams.set("sample_rate", sampleRate.toString());
    url.searchParams.set("channels", "1");
    url.searchParams.set("punctuate", "true");
    url.searchParams.set("smart_format", "true");

    const response = await fetch(url.toString(), {
      method: "POST",
      headers: {
        Authorization: `Token ${this.apiKey}`,
        "Content-Type": "application/octet-stream",
      },
      body: audioBuffer,
    });

    if (!response.ok) {
      const error = await response.text();
      throw new Error(`Deepgram API error: ${response.status} ${truncateError(error)}`);
    }

    const result = (await response.json()) as {
      results?: {
        channels?: Array<{
          alternatives?: Array<{
            transcript?: string;
            confidence?: number;
          }>;
        }>;
      };
    };

    const transcript = result.results?.channels?.[0]?.alternatives?.[0];
    return {
      text: transcript?.transcript?.trim() || "",
      confidence: transcript?.confidence,
    };
  }
}

/** OpenAI transcribe model IDs */
export const OPENAI_TRANSCRIBE_MODELS = {
  "gpt4o-mini": "gpt-4o-mini-transcribe",
  "gpt4o-transcribe": "gpt-4o-transcribe",
  "gpt4o-transcribe-diarize": "gpt-4o-transcribe-diarize",
} as const;

// Type definitions for the pipeline
interface ASRPipelineOutput {
  text: string;
}

type ASRPipeline = (audio: Float32Array, options?: Record<string, unknown>) => Promise<ASRPipelineOutput>;

// Shared instance for the pipeline (Singleton)
let sharedWhisperPipeline: ASRPipeline | null = null;

/**
 * Local Whisper STT Provider (Offline)
 */
export class LocalWhisperSTT implements STTProvider {
  private model: string;
  private quantized: boolean;
  private static initializationPromise: Promise<void> | null = null;

  constructor(config: DiscordVoiceConfig) {
    this.model = validateWhisperModel(config.localWhisper?.model || "Xenova/whisper-tiny.en");
    this.quantized = config.localWhisper?.quantized ?? true;
  }

  private async ensureInitialized() {
    if (sharedWhisperPipeline) return;

    if (!LocalWhisperSTT.initializationPromise) {
      LocalWhisperSTT.initializationPromise = (async () => {
        try {
          console.log(`Loading local Whisper model: ${this.model} (quantized: ${this.quantized})...`);
          sharedWhisperPipeline = (await pipeline("automatic-speech-recognition", this.model, {
            quantized: this.quantized,
          })) as unknown as ASRPipeline;
          console.log("Local Whisper model loaded.");
        } catch (error) {
          console.error("Failed to load local Whisper model:", error);
          LocalWhisperSTT.initializationPromise = null; // Reset on failure to allow retry
          throw error;
        }
      })();
    }

    await LocalWhisperSTT.initializationPromise;
  }

  async transcribe(audioBuffer: Buffer, sampleRate: number): Promise<STTResult> {
    await this.ensureInitialized();

    if (!sharedWhisperPipeline) {
      throw new Error("Failed to initialize Whisper pipeline");
    }

    // Convert to 16kHz float32 for Whisper
    const audioData = this.convertPcmToFloat32(audioBuffer, sampleRate);

    // Run transcription
    const output = await sharedWhisperPipeline(audioData, {
      language: "english", // optional, but helps
      chunk_length_s: 30,
      stride_length_s: 5,
    });

    // Output format depends on the pipeline options, but usually has .text
    const text = (output?.text || "").trim();

    return {
      text,
      language: "en", // assumed/detected
    };
  }

  /**
   * Convert raw PCM (Int16) to Float32 and resample to 16kHz
   */
  private convertPcmToFloat32(pcmBuffer: Buffer, inputSampleRate: number): Float32Array {
    // 1. Create Wav file from raw PCM to handle resampling easily
    const wav = new WaveFile();

    // Create a new WAV from the raw PCM data
    // 1 channel, inputSampleRate, '16' bit depth
    wav.fromScratch(1, inputSampleRate, "16", pcmBuffer);

    // 2. Resample to 16000Hz if needed (Whisper expects 16kHz)
    if (inputSampleRate !== 16000) {
      wav.toSampleRate(16000);
    }

    // 3. Get samples as Float32Array
    const samples = wav.getSamples(false, Float32Array);

    // Check if samples is a Float32Array (it should be due to the second argument)
    if (samples instanceof Float32Array) {
      return samples;
    }

    // Fallback/Safety cast if types are weird
    return samples as unknown as Float32Array;
  }
}

/**
 * Wyoming Whisper STT Provider (Remote)
 *
 * Connects to a Wyoming Faster Whisper server (e.g. wyoming-faster-whisper)
 * over TCP. Server runs on host:port (default 10300).
 * See: https://github.com/rhasspy/wyoming-faster-whisper
 */
export class WyomingWhisperSTT implements STTProvider {
  private host: string;
  private port: number;
  private language: string | undefined;
  private connectTimeoutMs: number;

  constructor(config: DiscordVoiceConfig) {
    const ww = config.wyomingWhisper ?? {};
    this.host = ww.host ?? "127.0.0.1";
    this.port = ww.port ?? 10300;
    this.language = typeof ww.language === "string" && ww.language.trim() ? ww.language.trim() : undefined;
    this.connectTimeoutMs =
      typeof ww.connectTimeoutMs === "number" && ww.connectTimeoutMs > 0 ? ww.connectTimeoutMs : 10000;
  }

  async transcribe(audioBuffer: Buffer, sampleRate: number): Promise<STTResult> {
    return new Promise((resolve, reject) => {
      let resolved = false;
      const finish = (text: string) => {
        if (resolved) return;
        resolved = true;
        socket.removeAllListeners();
        socket.end();
        resolve({ text: text.trim(), language: this.language });
      };

      const socket = net.createConnection({ host: this.host, port: this.port }, () => {
        let transcriptText = "";
        const rate = sampleRate;
        const width = 2;
        const channels = 1;

        const sendMessage = (type: string, data: Record<string, unknown>, payload?: Buffer) => {
          const payloadLen = payload ? payload.length : 0;
          const header =
            JSON.stringify({
              type,
              data,
              data_length: 0,
              payload_length: payloadLen,
            }) + "\n";
          socket.write(header);
          if (payload && payloadLen > 0) socket.write(payload);
        };

        let rawBuffer = Buffer.alloc(0);
        let state: "header" | "data" | "payload" = "header";
        let dataLength = 0;
        let payloadLength = 0;
        let lastHeader: { type: string } | null = null;

        const processEvent = (h: { type: string }, data: { text?: string }) => {
          if (h.type === "transcript" && data.text !== undefined && data.text !== null) {
            transcriptText = data.text;
            finish(transcriptText);
          } else if (h.type === "transcript-chunk" && data.text !== undefined && data.text !== null) {
            transcriptText += data.text;
          } else if (h.type === "transcript-stop") {
            finish(transcriptText);
          }
        };

        socket.on("data", (chunk: Buffer) => {
          rawBuffer = Buffer.concat([rawBuffer, chunk]);
          while (rawBuffer.length > 0) {
            if (state === "header") {
              const idx = rawBuffer.indexOf(0x0a);
              if (idx === -1) break;
              const line = rawBuffer.slice(0, idx).toString("utf8");
              rawBuffer = rawBuffer.slice(idx + 1);
              try {
                const h = JSON.parse(line) as { type: string; data_length?: number; payload_length?: number };
                lastHeader = h;
                dataLength = h.data_length ?? 0;
                payloadLength = h.payload_length ?? 0;
                state = dataLength > 0 ? "data" : payloadLength > 0 ? "payload" : "header";
                if (state === "header") {
                  processEvent(h, {});
                  if (resolved) return;
                }
              } catch {
                break;
              }
            }
            if (state === "data") {
              if (rawBuffer.length < dataLength) break;
              const dataBytes = rawBuffer.slice(0, dataLength);
              rawBuffer = rawBuffer.slice(dataLength);
              try {
                const data = JSON.parse(dataBytes.toString("utf8")) as { text?: string };
                processEvent(lastHeader!, data);
                if (resolved) return;
              } catch {
                // skip malformed data
              }
              dataLength = 0;
              state = payloadLength > 0 ? "payload" : "header";
              lastHeader = null;
            }
            if (state === "payload") {
              if (rawBuffer.length < payloadLength) break;
              rawBuffer = rawBuffer.slice(payloadLength);
              payloadLength = 0;
              state = "header";
            }
          }
        });

        socket.on("error", (err) => {
          if (!resolved) {
            resolved = true;
            reject(new Error(`Wyoming Whisper connection error: ${err.message}`));
          }
        });

        // Wyoming STT flow: transcribe -> audio-start -> audio-chunk -> audio-stop
        sendMessage("transcribe", this.language ? { language: this.language } : {});
        sendMessage("audio-start", { rate, width, channels });
        sendMessage("audio-chunk", { rate, width, channels }, audioBuffer);
        sendMessage("audio-stop", {});
      });

      socket.setTimeout(this.connectTimeoutMs, () => {
        if (!resolved) {
          resolved = true;
          socket.destroy();
          reject(new Error(`Wyoming Whisper connection timeout (${this.host}:${this.port})`));
        }
      });

      socket.on("error", (err) => {
        if (!resolved) {
          resolved = true;
          reject(new Error(`Wyoming Whisper error: ${err.message}`));
        }
      });
    });
  }
}

/**
 * Create STT provider based on config
 */
export function createSTTProvider(config: DiscordVoiceConfig): STTProvider {
  switch (config.sttProvider) {
    case "deepgram":
      return new DeepgramSTT(config);
    case "local-whisper":
      return new LocalWhisperSTT(config);
    case "wyoming-whisper":
      return new WyomingWhisperSTT(config);
    case "gpt4o-mini":
    case "gpt4o-transcribe":
    case "gpt4o-transcribe-diarize":
      return new OpenAITranscribeSTT(config, OPENAI_TRANSCRIBE_MODELS[config.sttProvider]);
    case "whisper":
    default:
      return new WhisperSTT(config);
  }
}
