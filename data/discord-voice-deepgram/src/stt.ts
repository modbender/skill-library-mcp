/**
 * Buffered Speech-to-Text using Deepgram (fallback path).
 */

import type { DiscordVoiceConfig } from "./config.js";

export interface STTResult {
  text: string;
  confidence?: number;
}

export interface STTProvider {
  transcribe(audioBuffer: Buffer, sampleRate: number): Promise<STTResult>;
}

export class DeepgramSTT implements STTProvider {
  private apiKey: string;
  private model: string;
  private language?: string;

  constructor(cfg: DiscordVoiceConfig) {
    this.apiKey = cfg.deepgram?.apiKey || process.env.DEEPGRAM_API_KEY || "";
    this.model = cfg.deepgram?.sttModel || process.env.DEEPGRAM_STT_MODEL || "nova-2";
    this.language = cfg.deepgram?.language || process.env.DEEPGRAM_LANGUAGE || undefined;
    if (!this.apiKey) throw new Error("Deepgram API key required for STT");
  }

  async transcribe(audioBuffer: Buffer, sampleRate: number): Promise<STTResult> {
    const url = new URL("https://api.deepgram.com/v1/listen");
    url.searchParams.set("model", this.model);
    url.searchParams.set("encoding", "linear16");
    url.searchParams.set("sample_rate", String(sampleRate));
    url.searchParams.set("channels", "1");
    url.searchParams.set("punctuate", "true");
    url.searchParams.set("smart_format", "true");
    if (this.language) url.searchParams.set("language", this.language);

    const resp = await fetch(url.toString(), {
      method: "POST",
      headers: {
        Authorization: `Token ${this.apiKey}`,
        "Content-Type": "application/octet-stream",
      },
      body: audioBuffer,
    });

    if (!resp.ok) {
      const errText = await resp.text().catch(() => "");
      throw new Error(`Deepgram STT error: ${resp.status} ${resp.statusText} ${errText}`);
    }

    const result = (await resp.json()) as any;
    const alt = result?.results?.channels?.[0]?.alternatives?.[0];
    return {
      text: (alt?.transcript || "").trim(),
      confidence: alt?.confidence,
    };
  }
}

export function createSTTProvider(cfg: DiscordVoiceConfig): STTProvider {
  return new DeepgramSTT(cfg);
}
