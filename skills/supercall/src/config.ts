import { z } from "zod";

// -----------------------------------------------------------------------------
// Phone Number Validation
// -----------------------------------------------------------------------------

/**
 * E.164 phone number format: +[country code][number]
 * Examples use 555 prefix (reserved for fictional numbers)
 */
export const E164Schema = z
  .string()
  .regex(/^\+[1-9]\d{1,14}$/, "Expected E.164 format, e.g. +15550001234");

// -----------------------------------------------------------------------------
// Inbound Policy
// -----------------------------------------------------------------------------

/**
 * Controls how inbound calls are handled:
 * - "disabled": Block all inbound calls (outbound only)
 * - "allowlist": Only accept calls from numbers in allowFrom
 * - "pairing": Unknown callers can request pairing (future)
 * - "open": Accept all inbound calls (dangerous!)
 */
// Inbound calls are not supported in this skill.

export const TwilioConfigSchema = z
  .object({
    /** Twilio Account SID */
    accountSid: z.string().min(1).optional(),
    /** Twilio Auth Token */
    authToken: z.string().min(1).optional(),
  })
  .strict();
export type TwilioConfig = z.infer<typeof TwilioConfigSchema>;

// -----------------------------------------------------------------------------
// TTS Configuration
// -----------------------------------------------------------------------------
// -----------------------------------------------------------------------------
// Webhook Server Configuration
// -----------------------------------------------------------------------------

export const VoiceCallServeConfigSchema = z
  .object({
    /** Port to listen on */
    port: z.number().int().positive().default(3334),
    /** Bind address */
    bind: z.string().default("127.0.0.1"),
    /** Webhook path */
    path: z.string().min(1).default("/voice/webhook"),
  })
  .strict()
  .default({ port: 3334, bind: "127.0.0.1", path: "/voice/webhook" });
export type VoiceCallServeConfig = z.infer<typeof VoiceCallServeConfigSchema>;

export const VoiceCallTailscaleConfigSchema = z
  .object({
    /**
     * Tailscale exposure mode:
     * - "off": No Tailscale exposure
     * - "serve": Tailscale serve (private to tailnet)
     * - "funnel": Tailscale funnel (public HTTPS)
     */
    mode: z.enum(["off", "serve", "funnel"]).default("off"),
    /** Path for Tailscale serve/funnel (should usually match serve.path) */
    path: z.string().min(1).default("/voice/webhook"),
  })
  .strict()
  .default({ mode: "off", path: "/voice/webhook" });
export type VoiceCallTailscaleConfig = z.infer<
  typeof VoiceCallTailscaleConfigSchema
>;

// -----------------------------------------------------------------------------
// Tunnel Configuration (unified ngrok/tailscale)
// -----------------------------------------------------------------------------

export const VoiceCallTunnelConfigSchema = z
  .object({
    /**
     * Tunnel provider:
     * - "none": No tunnel (use publicUrl if set, or manual setup)
     * - "ngrok": Use ngrok for public HTTPS tunnel
     * - "tailscale-serve": Tailscale serve (private to tailnet)
     * - "tailscale-funnel": Tailscale funnel (public HTTPS)
     */
    provider: z
      .enum(["none", "ngrok", "tailscale-serve", "tailscale-funnel"])
      .default("none"),
    /** ngrok auth token (optional, enables longer sessions and more features) */
    ngrokAuthToken: z.string().min(1).optional(),
    /** ngrok custom domain (optional, e.g., "myapp.ngrok.app") */
    ngrokDomain: z.string().min(1).optional(),
  })
  .strict()
  .default({ provider: "none" });
export type VoiceCallTunnelConfig = z.infer<typeof VoiceCallTunnelConfigSchema>;

// -----------------------------------------------------------------------------
// Streaming Configuration (OpenAI Realtime)
// -----------------------------------------------------------------------------

export const VoiceCallStreamingConfigSchema = z
  .object({
    /** OpenAI API key for Realtime API (uses OPENAI_API_KEY env if not set) */
    openaiApiKey: z.string().min(1).optional(),
    /** VAD silence duration in ms before considering speech ended */
    silenceDurationMs: z.number().int().positive().default(800),
    /** VAD threshold 0-1 (higher = less sensitive) */
    vadThreshold: z.number().min(0).max(1).default(0.5),
    /** WebSocket path for media stream connections */
    streamPath: z.string().min(1).default("/voice/stream"),
  })
  .strict()
  .default({
    silenceDurationMs: 800,
    vadThreshold: 0.5,
    streamPath: "/voice/stream",
  });
export type VoiceCallStreamingConfig = z.infer<
  typeof VoiceCallStreamingConfigSchema
>;

// -----------------------------------------------------------------------------
// Main Voice Call Configuration
// -----------------------------------------------------------------------------

export const VoiceCallConfigSchema = z
  .object({
    /** Enable voice call functionality */
    enabled: z.boolean().default(false),

    /** Active provider (twilio or mock) */
    provider: z.enum(["twilio", "mock"]).optional(),

    /** Twilio-specific configuration */
    twilio: TwilioConfigSchema.optional(),


    /** Phone number to call from (E.164) */
    fromNumber: E164Schema.optional(),

    /** Default phone number to call (E.164) */
    toNumber: E164Schema.optional(),

    /** Maximum call duration in seconds */
    maxDurationSeconds: z.number().int().positive().default(300),

    /** Silence timeout for end-of-speech detection (ms) */
    silenceTimeoutMs: z.number().int().positive().default(800),

    /** Timeout for user transcript (ms) */
    transcriptTimeoutMs: z.number().int().positive().default(180000),

    /** Maximum concurrent calls */
    maxConcurrentCalls: z.number().int().positive().default(1),

    /** Webhook server configuration */
    serve: VoiceCallServeConfigSchema,

    /** Tailscale exposure configuration (legacy, prefer tunnel config) */
    tailscale: VoiceCallTailscaleConfigSchema,

    /** Tunnel configuration (unified ngrok/tailscale) */
    tunnel: VoiceCallTunnelConfigSchema,

    /** Real-time audio streaming configuration */
    streaming: VoiceCallStreamingConfigSchema,

    /** Public webhook URL override (if set, bypasses tunnel auto-detection) */
    publicUrl: z.string().url().optional(),

    /** Store path for call logs */
    store: z.string().optional(),

  })
  .strict();

export type VoiceCallConfig = z.infer<typeof VoiceCallConfigSchema>;

// -----------------------------------------------------------------------------
// Configuration Helpers
// -----------------------------------------------------------------------------

/**
 * Validate that the configuration has all required fields for the selected provider.
 */
export function validateProviderConfig(config: VoiceCallConfig): {
  valid: boolean;
  errors: string[];
} {
  const errors: string[] = [];

  if (!config.enabled) {
    return { valid: true, errors: [] };
  }

  if (!config.provider) {
    errors.push("plugins.entries.supercall.config.provider is required");
  }

  if (!config.fromNumber && config.provider !== "mock") {
    errors.push("plugins.entries.supercall.config.fromNumber is required");
  }

  if (config.provider === "twilio") {
    if (!config.twilio?.accountSid) {
      errors.push(
        "plugins.entries.supercall.config.twilio.accountSid is required (or set TWILIO_ACCOUNT_SID env)",
      );
    }
    if (!config.twilio?.authToken) {
      errors.push(
        "plugins.entries.supercall.config.twilio.authToken is required (or set TWILIO_AUTH_TOKEN env)",
      );
    }
  }

  const realtimeApiKey =
    config.streaming?.openaiApiKey ?? process.env.OPENAI_API_KEY;
  if (!realtimeApiKey) {
    errors.push(
      "plugins.entries.supercall.config.streaming.openaiApiKey is required (or set OPENAI_API_KEY env)",
    );
  }

  if (config.provider && config.provider !== "twilio" && config.provider !== "mock") {
    errors.push("full realtime mode currently supports twilio (or mock) only");
  }

  return { valid: errors.length === 0, errors };
}
