import { z } from "zod";
import { normalizeAndValidatePublicUrl } from "./public-url.ts";

export const TwilioConfigSchema = z.object({
  accountSid: z.string().regex(/^AC[a-f0-9]{32}$/, "Invalid Twilio Account SID"),
  authToken: z.string().min(1, "Auth token is required"),
});

export const OpenAIConfigSchema = z.object({
  apiKey: z.string().min(1, "OpenAI API key is required"),
  model: z.string().default("gpt-realtime-1.5"),
  voice: z
    .enum(["alloy", "ash", "ballad", "coral", "echo", "sage", "shimmer", "verse"])
    .default("coral"),
});

export const VadConfigSchema = z.object({
  type: z.enum(["semantic_vad", "server_vad"]).default("semantic_vad"),
  eagerness: z.enum(["low", "medium", "high", "auto"]).default("medium"),
});

export const ServerConfigSchema = z.object({
  port: z.number().int().min(1).max(65535).default(3335),
  bind: z.string().default("127.0.0.1"),
});

export const CallsConfigSchema = z.object({
  maxDurationSeconds: z.number().int().min(60).default(600),
  timeoutSeconds: z.number().int().min(10).default(30),
  enableAmd: z.boolean().default(true),
  maxConcurrent: z.number().int().min(1).max(50).default(5),
});

export const InboundConfigSchema = z.object({
  enabled: z.boolean().default(false),
  policy: z.enum(["disabled", "open", "allowlist"]).default("disabled"),
  allowFrom: z.array(z.string()).default([]),
  greeting: z.string().default("Hey! What's up?"),
  systemPrompt: z.string().optional(),
});

export const PluginConfigSchema = z.object({
  twilio: TwilioConfigSchema,
  fromNumber: z.string().regex(/^\+[1-9]\d{1,14}$/, "Phone number must be E.164 format"),
  openai: OpenAIConfigSchema,
  vad: VadConfigSchema.default({}),
  publicUrl: z.string().url("Public URL must be a valid URL").transform((value, ctx) => {
    try {
      return normalizeAndValidatePublicUrl(value);
    } catch (err) {
      ctx.addIssue({
        code: z.ZodIssueCode.custom,
        message: err instanceof Error ? err.message : String(err),
      });
      return z.NEVER;
    }
  }),
  server: ServerConfigSchema.default({}),
  calls: CallsConfigSchema.default({}),
  inbound: InboundConfigSchema.default({}),
  debug: z.boolean().default(false),
});

export type PluginConfig = z.infer<typeof PluginConfigSchema>;
export type TwilioConfig = z.infer<typeof TwilioConfigSchema>;
export type OpenAIConfig = z.infer<typeof OpenAIConfigSchema>;

export function parseConfig(raw: unknown): PluginConfig {
  return PluginConfigSchema.parse(raw);
}
