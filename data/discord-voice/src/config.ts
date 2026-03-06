/**
 * Discord Voice Plugin Configuration
 */

// Placeholder for core TTS config compatibility
export interface VoiceCallTtsConfig {
  enabled?: boolean;
  voice?: string;
  [key: string]: unknown;
}

export interface DiscordVoiceConfig {
  enabled: boolean;
  sttProvider:
    | "whisper"
    | "gpt4o-mini"
    | "gpt4o-transcribe"
    | "gpt4o-transcribe-diarize"
    | "deepgram"
    | "local-whisper"
    | "wyoming-whisper";
  /** Fallback STT providers when primary fails (quota, rate limit, unreachable), tried in order */
  sttFallbackProviders?: readonly (
    | "whisper"
    | "gpt4o-mini"
    | "gpt4o-transcribe"
    | "gpt4o-transcribe-diarize"
    | "deepgram"
    | "local-whisper"
    | "wyoming-whisper"
  )[];
  streamingSTT: boolean; // Use streaming STT (Deepgram only) for lower latency
  ttsProvider: "openai" | "elevenlabs" | "deepgram" | "polly" | "kokoro" | "edge";
  ttsVoice: string;
  /** Fallback TTS providers when primary fails (quota, rate limit), tried in order. E.g. ["edge", "kokoro"] */
  ttsFallbackProviders?: readonly ("openai" | "elevenlabs" | "deepgram" | "polly" | "kokoro" | "edge")[];
  vadSensitivity: "low" | "medium" | "high";
  bargeIn: boolean; // Stop speaking when user starts talking
  allowedUsers: string[];
  silenceThresholdMs: number;
  minAudioMs: number;
  maxRecordingMs: number;
  autoJoinChannel?: string; // Channel ID to auto-join on startup
  heartbeatIntervalMs?: number; // Connection health check interval
  /** OpenClaw package root (if auto-detection fails); path to openclaw package dir containing dist/extensionAPI.js */
  openclawRoot?: string;

  /** Thinking sound played while processing; path relative to plugin root or absolute */
  thinkingSound?: {
    enabled?: boolean;
    path?: string; // default: "assets/thinking.mp3"
    volume?: number; // 0–1, default 0.7
    stopDelayMs?: number; // delay after stopping before response (default 50, was 100)
  };

  // LLM settings for voice responses (use fast models for low latency)
  model?: string; // e.g. "anthropic/claude-3-5-haiku-latest" or "openai/gpt-4o-mini"
  thinkLevel?: string; // "off", "low", "medium", "high" - lower = faster
  /**
   * Inject TTS-friendly hint into agent prompt.
   * - `true` (default): use default text ("do not use emojis…")
   * - `false`: do not inject
   * - `string`: use this custom text
   */
  noEmojiHint?: boolean | string;

  openai?: {
    apiKey?: string;
    whisperModel?: string;
    ttsModel?: string;
    /** OpenAI TTS voice: nova, shimmer, echo, onyx, fable, alloy, ash, sage, coral. Default: nova */
    voice?: string;
  };
  elevenlabs?: {
    apiKey?: string;
    voiceId?: string;
    /**
     * Model ID: eleven_turbo_v2_5 (default), eleven_flash_v2_5, eleven_multilingual_v2, eleven_multilingual_v3, etc.
     */
    modelId?: string;
  };
  deepgram?: {
    apiKey?: string;
    model?: string;
    /** TTS model (Aura): aura-asteria-en, aura-2-thalia-en, etc. Default: aura-asteria-en */
    ttsModel?: string;
  };
  /** Amazon Polly TTS */
  polly?: {
    region?: string;
    voiceId?: string;
    engine?: "standard" | "neural" | "long-form" | "generative";
    accessKeyId?: string;
    secretAccessKey?: string;
  };
  localWhisper?: {
    model?: string; // e.g., "Xenova/whisper-tiny.en"
    quantized?: boolean;
  };
  /** Wyoming Faster Whisper (remote STT over TCP, e.g. wyoming-faster-whisper) */
  wyomingWhisper?: {
    host?: string; // default: 127.0.0.1
    port?: number; // default: 10300
    uri?: string; // alternative: "host:port" or "tcp://host:port"
    language?: string; // e.g. "de", "en"
    connectTimeoutMs?: number;
  };
  /** Edge TTS (Microsoft, free, no API key). Default voice: de-DE-KatjaNeural */
  edge?: {
    voice?: string;
    lang?: string;
    outputFormat?: string;
    rate?: string;
    pitch?: string;
    volume?: string;
    proxy?: string;
    timeoutMs?: number;
  };
  kokoro?: {
    modelId?: string;
    dtype?: "fp32" | "fp16" | "q8" | "q4" | "q4f16";
    /** Kokoro voice: af_heart, af_bella, af_nicole, etc. Default: af_heart */
    voice?: string;
  };
}

export const DEFAULT_CONFIG: DiscordVoiceConfig = {
  enabled: true,
  sttProvider: "whisper",
  streamingSTT: true, // Enable streaming by default when using Deepgram
  ttsProvider: "openai",
  ttsVoice: "nova",
  vadSensitivity: "medium",
  bargeIn: true, // Enable barge-in by default
  allowedUsers: [],
  silenceThresholdMs: 800, // 800ms - snappy response after speech ends
  minAudioMs: 300, // 300ms minimum - filter very short noise
  maxRecordingMs: 30000,
  heartbeatIntervalMs: 30000,
  // model: undefined - uses system default, recommend "anthropic/claude-3-5-haiku-latest" for speed
  // thinkLevel: undefined - defaults to "off" for voice (fastest)
};

/** Default text for noEmojiHint when true */
export const DEFAULT_NO_EMOJI_HINT = "Do not use emojis—your response will be read aloud by a TTS engine.";

/** Maximum length for custom noEmojiHint strings (prevents excessive prompt bloat) */
const MAX_NO_EMOJI_HINT_LENGTH = 500;

/**
 * Sanitize a custom noEmojiHint string:
 * - Strip control characters (except common whitespace)
 * - Enforce length limit
 */
export function sanitizeNoEmojiHint(raw: string): string {
  // Strip control characters except spaces, tabs, and newlines
  // eslint-disable-next-line no-control-regex
  const cleaned = raw.replace(/[\u0000-\u0008\u000B\u000C\u000E-\u001F\u007F]/g, "").trim();
  if (cleaned.length > MAX_NO_EMOJI_HINT_LENGTH) {
    return cleaned.slice(0, MAX_NO_EMOJI_HINT_LENGTH);
  }
  return cleaned;
}

/** ElevenLabs model shorthands → full model IDs */
export const ELEVENLABS_MODELS = {
  turbo: "eleven_turbo_v2_5",
  flash: "eleven_flash_v2_5",
  v2: "eleven_multilingual_v2",
  v3: "eleven_multilingual_v3",
} as const;

/** Resolve ElevenLabs model ID; supports shorthands turbo, flash, v2, v3 */
function resolveElevenLabsModelId(raw: unknown): string {
  const s = typeof raw === "string" ? raw.trim().toLowerCase() : "";
  const mapped = ELEVENLABS_MODELS[s as keyof typeof ELEVENLABS_MODELS];
  if (mapped) return mapped;
  if (typeof raw === "string" && raw.trim()) return raw.trim();
  return "eleven_turbo_v2_5";
}

function getStr(obj: unknown, ...path: string[]): string | undefined {
  let cur: unknown = obj;
  for (const key of path) {
    if (cur === null || cur === undefined || typeof cur !== "object") return undefined;
    cur = (cur as Record<string, unknown>)[key];
  }
  return typeof cur === "string" && cur.trim() ? cur.trim() : undefined;
}

/**
 * Main OpenClaw config shape for fallback resolution.
 * See: agents.defaults.model, tts, talk, providers, plugins.entries
 */
export type MainConfig = Record<string, unknown>;

function resolveFromMain(main: MainConfig | undefined): {
  model?: string;
  ttsProvider?: "openai" | "elevenlabs";
  ttsVoice?: string;
  openaiApiKey?: string;
  elevenlabsApiKey?: string;
} {
  if (!main || typeof main !== "object") return {};

  const m = main as Record<string, unknown>;
  const modelObj = m["agents"] as Record<string, unknown> | undefined;
  const defaults = modelObj?.["defaults"] as Record<string, unknown> | undefined;
  const modelCfg = defaults?.["model"];
  const modelPrimary =
    typeof modelCfg === "string"
      ? modelCfg
      : modelCfg && typeof modelCfg === "object" && "primary" in modelCfg
        ? (modelCfg as { primary?: string }).primary
        : undefined;

  const list = modelObj?.["list"] as unknown[] | undefined;
  const firstAgentModel =
    Array.isArray(list) && list[0] && typeof list[0] === "object"
      ? (list[0] as Record<string, unknown>)["model"]
      : undefined;
  const agentModel =
    typeof firstAgentModel === "string"
      ? firstAgentModel
      : firstAgentModel && typeof firstAgentModel === "object" && "primary" in firstAgentModel
        ? (firstAgentModel as { primary?: string }).primary
        : undefined;

  const tts = m["tts"] as Record<string, unknown> | undefined;
  const ttsProviderRaw = tts?.["provider"];
  const ttsProvider =
    ttsProviderRaw === "elevenlabs"
      ? ("elevenlabs" as const)
      : ttsProviderRaw === "openai"
        ? ("openai" as const)
        : undefined;

  const talk = m["talk"] as Record<string, unknown> | undefined;
  const providers = m["providers"] as Record<string, unknown> | undefined;
  const openaiProvider = providers?.["openai"] as Record<string, unknown> | undefined;
  const openaiApiKey =
    getStr(talk, "apiKey") || getStr(openaiProvider, "apiKey") || getStr(m, "models", "providers", "openai", "apiKey");

  const plugins = m["plugins"] as Record<string, unknown> | undefined;
  const pluginsEntries = plugins?.["entries"] as Record<string, unknown> | undefined;
  const elevenlabsPlugin = pluginsEntries?.["elevenlabs"] as Record<string, unknown> | undefined;
  const elevenlabsConfig = elevenlabsPlugin?.["config"] as Record<string, unknown> | undefined;
  const elevenlabsApiKey = getStr(elevenlabsConfig, "apiKey");

  return {
    model: modelPrimary || agentModel,
    ttsProvider,
    ttsVoice: getStr(tts, "voice"),
    openaiApiKey,
    elevenlabsApiKey,
  };
}

export function parseConfig(raw: unknown, mainConfig?: MainConfig): DiscordVoiceConfig {
  const fallback = resolveFromMain(mainConfig);

  if (!raw || typeof raw !== "object") {
    return {
      ...DEFAULT_CONFIG,
      model: fallback.model,
      ttsProvider: fallback.ttsProvider ?? DEFAULT_CONFIG.ttsProvider,
      ttsVoice: fallback.ttsVoice ?? DEFAULT_CONFIG.ttsVoice,
      openai: fallback.openaiApiKey
        ? { apiKey: fallback.openaiApiKey, whisperModel: "whisper-1", ttsModel: "tts-1" }
        : undefined,
      elevenlabs: fallback.elevenlabsApiKey
        ? { apiKey: fallback.elevenlabsApiKey, modelId: resolveElevenLabsModelId(undefined) }
        : undefined,
      thinkingSound: { enabled: true, path: "assets/thinking.mp3", volume: 0.7 },
    } as DiscordVoiceConfig;
  }

  const obj = raw as Record<string, unknown>;

  const ttsProviderRaw =
    obj["ttsProvider"] === "deepgram"
      ? "deepgram"
      : obj["ttsProvider"] === "elevenlabs"
        ? "elevenlabs"
        : obj["ttsProvider"] === "polly"
          ? "polly"
          : obj["ttsProvider"] === "edge"
            ? "edge"
            : obj["ttsProvider"] === "kokoro"
              ? "kokoro"
              : obj["ttsProvider"] === "openai"
                ? "openai"
                : null;

  const ttsVoiceVal = typeof obj["ttsVoice"] === "string" ? obj["ttsVoice"] : null;
  const ttsVoice = ttsVoiceVal ?? fallback.ttsVoice ?? DEFAULT_CONFIG.ttsVoice;

  const modelVal = typeof obj["model"] === "string" ? obj["model"] : null;
  const model = modelVal ?? fallback.model ?? undefined;

  return {
    enabled: typeof obj["enabled"] === "boolean" ? obj["enabled"] : DEFAULT_CONFIG.enabled,
    sttProvider:
      obj["sttProvider"] === "deepgram"
        ? "deepgram"
        : obj["sttProvider"] === "gpt4o-transcribe-diarize"
          ? "gpt4o-transcribe-diarize"
          : obj["sttProvider"] === "gpt4o-transcribe"
            ? "gpt4o-transcribe"
            : obj["sttProvider"] === "gpt4o-mini"
              ? "gpt4o-mini"
              : obj["sttProvider"] === "local-whisper"
                ? "local-whisper"
                : obj["sttProvider"] === "wyoming-whisper"
                  ? "wyoming-whisper"
                  : "whisper",
    streamingSTT: typeof obj["streamingSTT"] === "boolean" ? obj["streamingSTT"] : DEFAULT_CONFIG.streamingSTT,
    sttFallbackProviders: (() => {
      const valid = [
        "whisper",
        "gpt4o-mini",
        "gpt4o-transcribe",
        "gpt4o-transcribe-diarize",
        "deepgram",
        "local-whisper",
        "wyoming-whisper",
      ] as const;
      const primary = obj["sttProvider"] as (typeof valid)[number];
      const excludePrimary = (p: string) => p !== primary;
      const toProvider = (p: string): (typeof valid)[number] | null =>
        valid.includes(p as (typeof valid)[number]) ? (p as (typeof valid)[number]) : null;

      const arr = obj["sttFallbackProviders"];
      if (Array.isArray(arr) && arr.length > 0) {
        const list = arr
          .filter((x): x is string => typeof x === "string")
          .map((p) => toProvider(p))
          .filter((x): x is (typeof valid)[number] => x !== null)
          .filter((p) => excludePrimary(p));
        return list.length > 0 ? list : undefined;
      }
      const fb = obj["sttFallbackProvider"];
      if (typeof fb === "string" && valid.includes(fb as (typeof valid)[number]) && fb !== primary) {
        return [fb as (typeof valid)[number]];
      }
      return undefined;
    })(),
    ttsProvider: (["openai", "elevenlabs", "deepgram", "polly", "kokoro", "edge"].includes(obj["ttsProvider"] as string)
      ? obj["ttsProvider"]
      : ttsProviderRaw) as "openai" | "elevenlabs" | "deepgram" | "polly" | "kokoro" | "edge",
    ttsVoice,
    ttsFallbackProviders: (() => {
      const valid = ["openai", "elevenlabs", "deepgram", "polly", "kokoro", "edge"] as const;
      const primary = (
        valid.includes(obj["ttsProvider"] as (typeof valid)[number]) ? obj["ttsProvider"] : ttsProviderRaw
      ) as (typeof valid)[number];
      const excludePrimary = (p: string) => p !== primary;
      const toProvider = (p: string): (typeof valid)[number] | null =>
        valid.includes(p as (typeof valid)[number]) ? (p as (typeof valid)[number]) : null;

      const arr = obj["ttsFallbackProviders"];
      if (Array.isArray(arr) && arr.length > 0) {
        const list = arr
          .filter((x): x is string => typeof x === "string")
          .map((p) => toProvider(p))
          .filter((x): x is (typeof valid)[number] => x !== null)
          .filter((p) => excludePrimary(p));
        return list.length > 0 ? list : undefined;
      }
      const fb = obj["ttsFallbackProvider"];
      if (typeof fb === "string" && valid.includes(fb as (typeof valid)[number]) && fb !== primary) {
        return [fb as (typeof valid)[number]];
      }
      return undefined;
    })(),
    vadSensitivity: ["low", "medium", "high"].includes(obj["vadSensitivity"] as string)
      ? (obj["vadSensitivity"] as "low" | "medium" | "high")
      : DEFAULT_CONFIG.vadSensitivity,
    bargeIn: typeof obj["bargeIn"] === "boolean" ? obj["bargeIn"] : DEFAULT_CONFIG.bargeIn,
    allowedUsers: Array.isArray(obj["allowedUsers"])
      ? (obj["allowedUsers"] as unknown[]).filter((u): u is string => typeof u === "string")
      : [],
    silenceThresholdMs: (() => {
      const v =
        typeof obj["silenceThresholdMs"] === "number" ? obj["silenceThresholdMs"] : DEFAULT_CONFIG.silenceThresholdMs;
      return v >= 0 ? v : DEFAULT_CONFIG.silenceThresholdMs;
    })(),
    minAudioMs: (() => {
      const v = typeof obj["minAudioMs"] === "number" ? obj["minAudioMs"] : DEFAULT_CONFIG.minAudioMs;
      return v >= 0 ? v : DEFAULT_CONFIG.minAudioMs;
    })(),
    maxRecordingMs: (() => {
      const v = typeof obj["maxRecordingMs"] === "number" ? obj["maxRecordingMs"] : DEFAULT_CONFIG.maxRecordingMs;
      return v >= 0 ? v : DEFAULT_CONFIG.maxRecordingMs;
    })(),
    autoJoinChannel:
      typeof obj["autoJoinChannel"] === "string" && obj["autoJoinChannel"].trim()
        ? obj["autoJoinChannel"].trim()
        : undefined,
    openclawRoot:
      typeof obj["openclawRoot"] === "string" && obj["openclawRoot"].trim() ? obj["openclawRoot"].trim() : undefined,
    heartbeatIntervalMs: (() => {
      const v =
        typeof obj["heartbeatIntervalMs"] === "number"
          ? obj["heartbeatIntervalMs"]
          : DEFAULT_CONFIG.heartbeatIntervalMs;
      const def = DEFAULT_CONFIG.heartbeatIntervalMs ?? 30_000;
      return typeof v === "number" && v >= 0 ? v : def;
    })(),
    model,
    thinkLevel: typeof obj["thinkLevel"] === "string" ? obj["thinkLevel"] : undefined,
    noEmojiHint: (() => {
      if (obj["noEmojiHint"] === false) return false;
      const s = obj["noEmojiHint"];
      if (typeof s === "string" && s.trim()) return sanitizeNoEmojiHint(s);
      return true;
    })(),
    openai: (() => {
      const o = obj["openai"] && typeof obj["openai"] === "object" ? (obj["openai"] as Record<string, unknown>) : null;
      const apiKey = (o?.["apiKey"] as string | undefined) || fallback.openaiApiKey;
      if (!apiKey) return undefined;
      return {
        apiKey,
        whisperModel: (o?.["whisperModel"] as string) || "whisper-1",
        ttsModel: (o?.["ttsModel"] as string) || "tts-1",
        voice:
          typeof o?.["voice"] === "string" && (o["voice"] as string).trim() ? (o["voice"] as string).trim() : "nova",
      };
    })(),
    elevenlabs: (() => {
      const o =
        obj["elevenlabs"] && typeof obj["elevenlabs"] === "object"
          ? (obj["elevenlabs"] as Record<string, unknown>)
          : null;
      const apiKey = (o?.["apiKey"] as string | undefined) || fallback.elevenlabsApiKey;
      if (!apiKey) return undefined;
      return {
        apiKey,
        voiceId: o?.["voiceId"] as string | undefined,
        modelId: resolveElevenLabsModelId(o?.["modelId"]),
      };
    })(),
    deepgram: (() => {
      const dg =
        obj["deepgram"] && typeof obj["deepgram"] === "object" ? (obj["deepgram"] as Record<string, unknown>) : null;
      if (!dg) return undefined;
      const m = (typeof dg["model"] === "string" ? dg["model"] : "").trim();
      const tm = (typeof dg["ttsModel"] === "string" ? dg["ttsModel"] : "").trim();
      const isAura = (s: string) => s.toLowerCase().startsWith("aura-");
      return {
        apiKey: dg["apiKey"] as string | undefined,
        model: isAura(m) ? "nova-2" : m || "nova-2",
        ttsModel: tm || (isAura(m) ? m : "aura-asteria-en"),
      };
    })(),
    localWhisper:
      obj["localWhisper"] && typeof obj["localWhisper"] === "object"
        ? {
            model: ((obj["localWhisper"] as Record<string, unknown>)["model"] as string) || "Xenova/whisper-tiny.en",
            quantized:
              typeof (obj["localWhisper"] as Record<string, unknown>)["quantized"] === "boolean"
                ? ((obj["localWhisper"] as Record<string, unknown>)["quantized"] as boolean)
                : true,
          }
        : undefined,
    wyomingWhisper: (() => {
      const ww =
        obj["wyomingWhisper"] && typeof obj["wyomingWhisper"] === "object"
          ? (obj["wyomingWhisper"] as Record<string, unknown>)
          : null;
      if (!ww) return undefined;
      const uriStr = typeof ww["uri"] === "string" ? (ww["uri"] as string).trim() : "";
      if (uriStr) {
        const match = uriStr.match(/^(?:tcp:\/\/)?([^:]+):(\d+)$/);
        if (match && match[1] !== undefined && match[2] !== undefined) {
          return {
            host: match[1].trim(),
            port: parseInt(match[2], 10),
            language:
              typeof ww["language"] === "string" && (ww["language"] as string).trim()
                ? (ww["language"] as string).trim()
                : undefined,
            connectTimeoutMs:
              typeof ww["connectTimeoutMs"] === "number" && (ww["connectTimeoutMs"] as number) > 0
                ? (ww["connectTimeoutMs"] as number)
                : 10000,
          };
        }
      }
      const host =
        typeof ww["host"] === "string" && (ww["host"] as string).trim() ? (ww["host"] as string).trim() : "127.0.0.1";
      const port =
        typeof ww["port"] === "number" && (ww["port"] as number) > 0 && (ww["port"] as number) <= 65535
          ? (ww["port"] as number)
          : 10300;
      return {
        host,
        port,
        language:
          typeof ww["language"] === "string" && (ww["language"] as string).trim()
            ? (ww["language"] as string).trim()
            : undefined,
        connectTimeoutMs:
          typeof ww["connectTimeoutMs"] === "number" && (ww["connectTimeoutMs"] as number) > 0
            ? (ww["connectTimeoutMs"] as number)
            : 10000,
      };
    })(),
    kokoro:
      obj["kokoro"] && typeof obj["kokoro"] === "object"
        ? {
            modelId: (() => {
              const m = (obj["kokoro"] as Record<string, unknown>)["modelId"];
              return typeof m === "string" && (m as string).trim()
                ? (m as string).trim()
                : "onnx-community/Kokoro-82M-v1.0-ONNX";
            })(),
            dtype: (["fp32", "fp16", "q8", "q4", "q4f16"].includes(
              (obj["kokoro"] as Record<string, unknown>)["dtype"] as string,
            )
              ? (obj["kokoro"] as Record<string, unknown>)["dtype"]
              : "fp32") as "fp32" | "fp16" | "q8" | "q4" | "q4f16",
            voice:
              typeof (obj["kokoro"] as Record<string, unknown>)["voice"] === "string" &&
              (obj["kokoro"] as Record<string, unknown>)["voice"]
                ? String((obj["kokoro"] as Record<string, unknown>)["voice"]).trim()
                : "af_heart",
          }
        : undefined,
    edge: (() => {
      const e = obj["edge"] && typeof obj["edge"] === "object" ? (obj["edge"] as Record<string, unknown>) : null;
      if (!e) return undefined;
      return {
        voice:
          typeof e["voice"] === "string" && (e["voice"] as string).trim()
            ? String(e["voice"]).trim()
            : "de-DE-KatjaNeural",
        lang: typeof e["lang"] === "string" && (e["lang"] as string).trim() ? String(e["lang"]).trim() : "de-DE",
        outputFormat:
          typeof e["outputFormat"] === "string" && (e["outputFormat"] as string).trim()
            ? String(e["outputFormat"]).trim()
            : "webm-24khz-16bit-mono-opus",
        rate: typeof e["rate"] === "string" && (e["rate"] as string).trim() ? String(e["rate"]).trim() : undefined,
        pitch: typeof e["pitch"] === "string" && (e["pitch"] as string).trim() ? String(e["pitch"]).trim() : undefined,
        volume:
          typeof e["volume"] === "string" && (e["volume"] as string).trim() ? String(e["volume"]).trim() : undefined,
        proxy: typeof e["proxy"] === "string" && (e["proxy"] as string).trim() ? String(e["proxy"]).trim() : undefined,
        timeoutMs:
          typeof e["timeoutMs"] === "number" && (e["timeoutMs"] as number) >= 0
            ? (e["timeoutMs"] as number)
            : undefined,
      };
    })(),
    polly: (() => {
      const p = obj["polly"] && typeof obj["polly"] === "object" ? (obj["polly"] as Record<string, unknown>) : null;
      if (!p) return undefined;
      return {
        region:
          typeof p["region"] === "string" && (p["region"] as string).trim() ? String(p["region"]).trim() : undefined,
        voiceId:
          typeof p["voiceId"] === "string" && (p["voiceId"] as string).trim() ? String(p["voiceId"]).trim() : "Joanna",
        engine: ["standard", "neural", "long-form", "generative"].includes(p["engine"] as string)
          ? (p["engine"] as "standard" | "neural" | "long-form" | "generative")
          : undefined,
        accessKeyId:
          typeof p["accessKeyId"] === "string" && (p["accessKeyId"] as string).trim()
            ? String(p["accessKeyId"]).trim()
            : undefined,
        secretAccessKey:
          typeof p["secretAccessKey"] === "string" && p["secretAccessKey"] ? String(p["secretAccessKey"]) : undefined,
      };
    })(),
    thinkingSound: (() => {
      const t =
        obj["thinkingSound"] && typeof obj["thinkingSound"] === "object"
          ? (obj["thinkingSound"] as Record<string, unknown>)
          : null;
      if (!t) return { enabled: true, path: "assets/thinking.mp3", volume: 0.7, stopDelayMs: 50 };
      const enabled = "enabled" in t ? t["enabled"] !== false : true;
      const path =
        typeof t["path"] === "string" && (t["path"] as string).trim()
          ? (t["path"] as string).trim()
          : "assets/thinking.mp3";
      let volume = 0.7;
      if (typeof t["volume"] === "number" && t["volume"] >= 0 && t["volume"] <= 1) volume = t["volume"] as number;
      let stopDelayMs = 50;
      if (
        typeof t["stopDelayMs"] === "number" &&
        (t["stopDelayMs"] as number) >= 0 &&
        (t["stopDelayMs"] as number) <= 500
      )
        stopDelayMs = t["stopDelayMs"] as number;
      return { enabled, path, volume, stopDelayMs };
    })(),
  };
}

// ── Security: model / ID validation helpers ──────────────────────────

/** Allowed prefixes for local Whisper model IDs (prevents loading arbitrary HuggingFace models) */
const ALLOWED_WHISPER_PREFIXES = ["Xenova/whisper-", "openai/whisper-", "onnx-community/whisper-"] as const;

/** Allowed prefixes for Kokoro model IDs */
const ALLOWED_KOKORO_PREFIXES = ["onnx-community/Kokoro-", "kokoro-"] as const;

/** Known Deepgram STT model families */
const KNOWN_DEEPGRAM_MODELS = ["nova-2", "nova-3", "nova", "enhanced", "base", "whisper"] as const;

/** ElevenLabs voice IDs are alphanumeric */
const ELEVENLABS_VOICE_ID_RE = /^[a-zA-Z0-9]+$/;

export function validateWhisperModel(model: string): string {
  if (ALLOWED_WHISPER_PREFIXES.some((p) => model.startsWith(p))) return model;
  return "Xenova/whisper-tiny.en"; // safe default
}

export function validateKokoroModel(model: string): string {
  if (ALLOWED_KOKORO_PREFIXES.some((p) => model.startsWith(p))) return model;
  return "onnx-community/Kokoro-82M-v1.0-ONNX"; // safe default
}

export function validateDeepgramModel(model: string): string {
  if (KNOWN_DEEPGRAM_MODELS.some((m) => model === m || model.startsWith(`${m}-`))) return model;
  return "nova-2"; // safe default
}

export function validateElevenLabsVoiceId(voiceId: string): string {
  if (ELEVENLABS_VOICE_ID_RE.test(voiceId)) return voiceId;
  return "21m00Tcm4TlvDq8ikWAM"; // default: Rachel
}

/**
 * Extract available model IDs from OpenClaw main config (agents.list, agents.defaults).
 * Used for validation/suggestions when setting voice model at runtime.
 */
export function getAvailableModels(main: MainConfig | undefined): string[] {
  const seen = new Set<string>();
  const add = (s: string | undefined) => {
    if (typeof s === "string" && s.trim()) {
      const t = s.trim();
      if (t && !seen.has(t)) seen.add(t);
    }
  };

  if (!main || typeof main !== "object") return [];

  const m = main as Record<string, unknown>;
  const agents = m["agents"] as Record<string, unknown> | undefined;
  const defaults = agents?.["defaults"] as Record<string, unknown> | undefined;
  const defModel = defaults?.["model"];
  if (typeof defModel === "string") add(defModel);
  else if (defModel && typeof defModel === "object" && "primary" in defModel) {
    add((defModel as { primary?: string }).primary);
  }

  const list = agents?.["list"] as unknown[] | undefined;
  if (Array.isArray(list)) {
    for (const item of list) {
      if (item && typeof item === "object") {
        const o = item as Record<string, unknown>;
        const model = o["model"];
        if (typeof model === "string") add(model);
        else if (model && typeof model === "object" && "primary" in model) {
          add((model as { primary?: string }).primary);
        }
      }
    }
  }

  return [...seen];
}

/**
 * Get VAD threshold based on sensitivity setting
 */
export function getVadThreshold(sensitivity: "low" | "medium" | "high"): number {
  switch (sensitivity) {
    case "low":
      return 0.01; // Very sensitive - picks up quiet speech
    case "high":
      return 0.05; // Less sensitive - requires louder speech
    case "medium":
    default:
      return 0.02;
  }
}
