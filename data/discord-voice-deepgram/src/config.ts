/**
 * Deepgram Discord Voice - Plugin Configuration
 */

export interface DeepgramConfig {
  apiKey?: string;
  sttModel?: string;
  language?: string; // BCP-47 tag, optional
}

export interface DiscordVoiceConfig {
  enabled: boolean;

  // Low-latency paths
  streamingSTT: boolean;
  streamingTTS: boolean;

  // Deepgram Aura TTS voice model name (example: "aura-2-thalia-en")
  ttsVoice: string;

  // Voice UX
  vadSensitivity: "low" | "medium" | "high";
  bargeIn: boolean;
  allowedUsers: string[];

  // Speaker safelist / switching
  primaryUser?: string; // Discord user ID or name (best: user ID)
  allowVoiceSwitch: boolean; // allow voice commands to switch active speaker
  wakeWord: string; // word to start commands, e.g. "openclaw"

  // Recording / endpointing
  silenceThresholdMs: number;
  minAudioMs: number;
  maxRecordingMs: number;

  // Optional features
  autoJoinChannel?: string;
  heartbeatIntervalMs?: number;

  // LLM response tuning (fast models recommended)
  model?: string;
  thinkLevel?: string;

  deepgram?: DeepgramConfig;
}

export const DEFAULT_CONFIG: DiscordVoiceConfig = {
  enabled: true,
  streamingSTT: true,
  streamingTTS: true,
  ttsVoice: "aura-2-thalia-en",
  vadSensitivity: "medium",
  bargeIn: true,
  allowedUsers: [],
  primaryUser: undefined,
  allowVoiceSwitch: true,
  wakeWord: "openclaw",
  silenceThresholdMs: 1000,
  minAudioMs: 300,
  maxRecordingMs: 30_000,
  heartbeatIntervalMs: 30_000,
};

export function parseConfig(raw: unknown): DiscordVoiceConfig {
  if (!raw || typeof raw !== "object") return { ...DEFAULT_CONFIG };
  const obj = raw as Record<string, unknown>;

  const deepgramRaw = obj.deepgram && typeof obj.deepgram === "object" ? (obj.deepgram as Record<string, unknown>) : undefined;

  return {
    enabled: typeof obj.enabled === "boolean" ? obj.enabled : DEFAULT_CONFIG.enabled,
    streamingSTT: typeof obj.streamingSTT === "boolean" ? obj.streamingSTT : DEFAULT_CONFIG.streamingSTT,
    streamingTTS: typeof obj.streamingTTS === "boolean" ? obj.streamingTTS : DEFAULT_CONFIG.streamingTTS,
    ttsVoice: typeof obj.ttsVoice === "string" && obj.ttsVoice.trim() ? obj.ttsVoice.trim() : DEFAULT_CONFIG.ttsVoice,
    vadSensitivity: (obj.vadSensitivity === "low" || obj.vadSensitivity === "medium" || obj.vadSensitivity === "high")
      ? (obj.vadSensitivity as "low" | "medium" | "high")
      : DEFAULT_CONFIG.vadSensitivity,
    bargeIn: typeof obj.bargeIn === "boolean" ? obj.bargeIn : DEFAULT_CONFIG.bargeIn,
    allowedUsers: Array.isArray(obj.allowedUsers) ? obj.allowedUsers.filter((u): u is string => typeof u === "string") : [],
    primaryUser: typeof obj.primaryUser === "string" && obj.primaryUser.trim() ? obj.primaryUser.trim() : undefined,
    allowVoiceSwitch: typeof obj.allowVoiceSwitch === "boolean" ? obj.allowVoiceSwitch : DEFAULT_CONFIG.allowVoiceSwitch,
    wakeWord: typeof obj.wakeWord === "string" && obj.wakeWord.trim() ? obj.wakeWord.trim().toLowerCase() : DEFAULT_CONFIG.wakeWord,
    silenceThresholdMs: typeof obj.silenceThresholdMs === "number" ? obj.silenceThresholdMs : DEFAULT_CONFIG.silenceThresholdMs,
    minAudioMs: typeof obj.minAudioMs === "number" ? obj.minAudioMs : DEFAULT_CONFIG.minAudioMs,
    maxRecordingMs: typeof obj.maxRecordingMs === "number" ? obj.maxRecordingMs : DEFAULT_CONFIG.maxRecordingMs,
    autoJoinChannel: typeof obj.autoJoinChannel === "string" && obj.autoJoinChannel.trim() ? obj.autoJoinChannel.trim() : undefined,
    heartbeatIntervalMs: typeof obj.heartbeatIntervalMs === "number" ? obj.heartbeatIntervalMs : DEFAULT_CONFIG.heartbeatIntervalMs,
    model: typeof obj.model === "string" && obj.model.trim() ? obj.model.trim() : undefined,
    thinkLevel: typeof obj.thinkLevel === "string" && obj.thinkLevel.trim() ? obj.thinkLevel.trim() : undefined,
    deepgram: deepgramRaw ? {
      apiKey: typeof deepgramRaw.apiKey === "string" ? deepgramRaw.apiKey : undefined,
      sttModel: typeof deepgramRaw.sttModel === "string" && deepgramRaw.sttModel.trim() ? deepgramRaw.sttModel.trim() : "nova-2",
      language: typeof deepgramRaw.language === "string" && deepgramRaw.language.trim() ? deepgramRaw.language.trim() : undefined,
    } : undefined,
  };
}

export function getVadRmsThreshold(sensitivity: "low" | "medium" | "high"): number {
  // RMS thresholds tuned for decoded 16-bit PCM from Discord Opus.
  // Larger threshold = less sensitive.
  switch (sensitivity) {
    case "low":
      return 400;
    case "high":
      return 1200;
    case "medium":
    default:
      return 800;
  }
}
