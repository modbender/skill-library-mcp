import { mkdirSync, writeFileSync } from "node:fs";
import { join } from "node:path";
import { homedir } from "node:os";

const RECORDINGS_DIR = join(homedir(), ".openclaw", "voice-calls-realtime", "recordings");

// ANSI color codes
const CYAN = "\x1b[36m";
const GREEN = "\x1b[32m";
const YELLOW = "\x1b[33m";
const RED = "\x1b[31m";
const DIM = "\x1b[2m";
const RESET = "\x1b[0m";

export class DebugRecorder {
  private enabled: boolean;
  private callId: string;
  private inboundChunks: Buffer[] = [];
  private outboundChunks: Buffer[] = [];
  private events: Array<{ ts: number; source: string; type: string; detail?: string }> = [];
  private startTime: number;
  private lastSpeechEnd: number | null = null;

  constructor(callId: string, enabled: boolean) {
    this.callId = callId;
    this.enabled = enabled;
    this.startTime = Date.now();

    if (enabled) {
      mkdirSync(RECORDINGS_DIR, { recursive: true, mode: 0o700 });
    }
  }

  logTwilio(eventType: string, detail?: string): void {
    if (!this.enabled) return;
    this.events.push({ ts: Date.now(), source: "twilio", type: eventType, detail });
    console.log(`${CYAN}[twilio]${RESET} ${DIM}${this.elapsed()}${RESET} ${eventType}${detail ? ` ${detail}` : ""}`);
  }

  logOpenAI(eventType: string, detail?: string): void {
    if (!this.enabled) return;
    this.events.push({ ts: Date.now(), source: "openai", type: eventType, detail });
    console.log(`${GREEN}[openai]${RESET} ${DIM}${this.elapsed()}${RESET} ${eventType}${detail ? ` ${detail}` : ""}`);

    if (eventType === "input_audio_buffer.speech_stopped") {
      this.lastSpeechEnd = Date.now();
    }
    if (eventType === "response.audio.delta" && this.lastSpeechEnd !== null) {
      const latency = Date.now() - this.lastSpeechEnd;
      console.log(`${YELLOW}[latency]${RESET} ${DIM}${this.elapsed()}${RESET} speech-to-response: ${latency}ms`);
      this.lastSpeechEnd = null;
    }
  }

  logTool(toolName: string, detail?: string): void {
    if (!this.enabled) return;
    this.events.push({ ts: Date.now(), source: "tool", type: toolName, detail });
    console.log(`${YELLOW}[tool]${RESET} ${DIM}${this.elapsed()}${RESET} ${toolName}${detail ? ` ${detail}` : ""}`);
  }

  logError(message: string, error?: unknown): void {
    const detail = error instanceof Error ? error.message : error ? String(error) : undefined;
    this.events.push({ ts: Date.now(), source: "error", type: message, detail });
    console.error(`${RED}[error]${RESET} ${DIM}${this.elapsed()}${RESET} ${message}${detail ? `: ${detail}` : ""}`);
  }

  recordInbound(audioBase64: string): void {
    if (!this.enabled) return;
    this.inboundChunks.push(Buffer.from(audioBase64, "base64"));
  }

  recordOutbound(audioBase64: string): void {
    if (!this.enabled) return;
    this.outboundChunks.push(Buffer.from(audioBase64, "base64"));
  }

  async finalize(transcript: Array<{ role: string; text: string; ts: number }>): Promise<void> {
    if (!this.enabled) return;

    const basePath = join(RECORDINGS_DIR, this.callId);

    // Save raw mu-law audio
    if (this.inboundChunks.length > 0) {
      const inboundPath = `${basePath}-inbound.raw`;
      writeFileSync(inboundPath, Buffer.concat(this.inboundChunks), { mode: 0o600 });
      console.log(`${GREEN}[debug]${RESET} Saved inbound audio: ${inboundPath}`);
    }

    if (this.outboundChunks.length > 0) {
      const outboundPath = `${basePath}-outbound.raw`;
      writeFileSync(outboundPath, Buffer.concat(this.outboundChunks), { mode: 0o600 });
      console.log(`${GREEN}[debug]${RESET} Saved outbound audio: ${outboundPath}`);
    }

    // Convert raw mu-law to WAV for easy playback
    for (const direction of ["inbound", "outbound"] as const) {
      const rawPath = `${basePath}-${direction}.raw`;
      const wavPath = `${basePath}-${direction}.wav`;
      try {
        const raw = await Bun.file(rawPath).arrayBuffer();
        if (raw.byteLength > 0) {
          const wav = createMulawWav(new Uint8Array(raw));
          writeFileSync(wavPath, wav, { mode: 0o600 });
          console.log(`${GREEN}[debug]${RESET} Converted to WAV: ${wavPath}`);
        }
      } catch {
        // Raw file may not exist if no audio was recorded
      }
    }

    // Save transcript
    const transcriptPath = `${basePath}-transcript.json`;
    writeFileSync(transcriptPath, JSON.stringify({ callId: this.callId, transcript, events: this.events }, null, 2), {
      mode: 0o600,
    });
    console.log(`${GREEN}[debug]${RESET} Saved transcript: ${transcriptPath}`);
  }

  private elapsed(): string {
    const ms = Date.now() - this.startTime;
    const s = Math.floor(ms / 1000);
    const m = Math.floor(s / 60);
    const remainS = s % 60;
    const remainMs = ms % 1000;
    return `${m}:${String(remainS).padStart(2, "0")}.${String(remainMs).padStart(3, "0")}`;
  }
}

/**
 * Create a WAV file from mu-law PCM data (8kHz, mono, 8-bit mu-law).
 */
function createMulawWav(mulawData: Uint8Array): Uint8Array {
  const dataSize = mulawData.byteLength;
  const headerSize = 44;
  const fileSize = headerSize + dataSize;
  const buffer = new Uint8Array(fileSize);
  const view = new DataView(buffer.buffer);

  // RIFF header
  buffer.set([0x52, 0x49, 0x46, 0x46]); // "RIFF"
  view.setUint32(4, fileSize - 8, true);
  buffer.set([0x57, 0x41, 0x56, 0x45], 8); // "WAVE"

  // fmt chunk
  buffer.set([0x66, 0x6d, 0x74, 0x20], 12); // "fmt "
  view.setUint32(16, 16, true); // chunk size
  view.setUint16(20, 7, true); // mu-law format (7)
  view.setUint16(22, 1, true); // mono
  view.setUint32(24, 8000, true); // sample rate
  view.setUint32(28, 8000, true); // byte rate
  view.setUint16(32, 1, true); // block align
  view.setUint16(34, 8, true); // bits per sample

  // data chunk
  buffer.set([0x64, 0x61, 0x74, 0x61], 36); // "data"
  view.setUint32(40, dataSize, true);
  buffer.set(mulawData, 44);

  return buffer;
}
