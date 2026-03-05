/**
 * Low-latency Text-to-Speech using Deepgram Aura.
 *
 * Note: Deepgram's TTS WebSocket endpoint streams only linear16/mulaw/alaw.
 * For best Discord compatibility we stream Ogg/Opus over HTTP from /v1/speak.
 */

import { Readable } from "node:stream";
import type { DiscordVoiceConfig } from "./config.js";

export interface StreamingTTSResult {
  stream: Readable;
  format: "opus";
  sampleRate: number;
}

export interface StreamingTTSProvider {
  synthesizeStream(text: string): Promise<StreamingTTSResult>;
}

function mustGetDeepgramKey(cfg: DiscordVoiceConfig): string {
  const key = cfg.deepgram?.apiKey || process.env.DEEPGRAM_API_KEY || "";
  if (!key) throw new Error("Deepgram API key required for TTS");
  return key;
}

function mustGetVoice(cfg: DiscordVoiceConfig): string {
  return cfg.ttsVoice || "aura-2-thalia-en";
}

export class DeepgramHttpStreamingTTS implements StreamingTTSProvider {
  private apiKey: string;
  private voiceModel: string;
  private sampleRate: number;

  constructor(cfg: DiscordVoiceConfig, opts?: { sampleRate?: number }) {
    this.apiKey = mustGetDeepgramKey(cfg);
    this.voiceModel = mustGetVoice(cfg);
    this.sampleRate = opts?.sampleRate ?? 48000;
  }

  async synthesizeStream(text: string): Promise<StreamingTTSResult> {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 25_000);

    try {
      const url = new URL("https://api.deepgram.com/v1/speak");
      url.searchParams.set("model", this.voiceModel);
      url.searchParams.set("encoding", "opus");
      url.searchParams.set("container", "ogg");
      url.searchParams.set("sample_rate", String(this.sampleRate));

      const resp = await fetch(url.toString(), {
        method: "POST",
        headers: {
          Authorization: `Token ${this.apiKey}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ text }),
        signal: controller.signal,
      });

      if (!resp.ok) {
        const errText = await resp.text().catch(() => "");
        throw new Error(`Deepgram TTS error: ${resp.status} ${resp.statusText} ${errText}`);
      }

      if (!resp.body) {
        throw new Error("Deepgram TTS response missing body stream");
      }

      // Node 18+ provides Readable.fromWeb for streaming WebResponse bodies.
      const nodeStream = Readable.fromWeb(resp.body as any);

      return {
        stream: nodeStream,
        format: "opus",
        sampleRate: this.sampleRate,
      };
    } finally {
      clearTimeout(timeout);
    }
  }
}

export function createStreamingTTSProvider(cfg: DiscordVoiceConfig): StreamingTTSProvider | null {
  if (!cfg.streamingTTS) return null;
  return new DeepgramHttpStreamingTTS(cfg, { sampleRate: 48000 });
}
