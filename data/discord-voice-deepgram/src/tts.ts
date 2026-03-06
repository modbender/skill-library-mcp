/**
 * Buffered Text-to-Speech using Deepgram Aura (fallback path).
 */

import type { DiscordVoiceConfig } from "./config.js";

export interface TTSResult {
  audioBuffer: Buffer;
  format: "opus";
  sampleRate: number;
}

export interface TTSProvider {
  synthesize(text: string): Promise<TTSResult>;
}

export class DeepgramTTS implements TTSProvider {
  private apiKey: string;
  private voiceModel: string;
  private sampleRate: number;

  constructor(cfg: DiscordVoiceConfig, opts?: { sampleRate?: number }) {
    this.apiKey = cfg.deepgram?.apiKey || process.env.DEEPGRAM_API_KEY || "";
    if (!this.apiKey) throw new Error("Deepgram API key required for TTS");
    this.voiceModel = cfg.ttsVoice || "aura-2-thalia-en";
    this.sampleRate = opts?.sampleRate ?? 48000;
  }

  async synthesize(text: string): Promise<TTSResult> {
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
    });

    if (!resp.ok) {
      const errText = await resp.text().catch(() => "");
      throw new Error(`Deepgram TTS error: ${resp.status} ${resp.statusText} ${errText}`);
    }

    const arr = await resp.arrayBuffer();
    return {
      audioBuffer: Buffer.from(arr),
      format: "opus",
      sampleRate: this.sampleRate,
    };
  }
}

export function createTTSProvider(cfg: DiscordVoiceConfig): TTSProvider {
  return new DeepgramTTS(cfg, { sampleRate: 48000 });
}
