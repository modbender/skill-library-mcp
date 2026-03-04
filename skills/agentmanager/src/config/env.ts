import { z } from 'zod';

const EnvSchema = z.object({
  LLM_PROVIDER: z.string().optional(),
  DEFAULT_PROVIDER_ID: z.string().optional(),
  GATEWAY_URL: z.string().optional(),
  GATEWAY_STEP_PATH: z.string().default('/v1/llm/step'),
  GATEWAY_API_KEY: z.string().optional(),
  GATEWAY_TIMEOUT_MS: z.coerce.number().int().positive().default(30_000),
  OUTBOUND_ALLOWLIST: z.string().default(''),
  TOOL_CALLBACK_ALLOWLIST: z.string().default(''),
  ALLOW_INSECURE_HTTP_TOOLS: z.string().default('0'),
  MAX_PROVIDER_REQUEST_BYTES: z.coerce.number().int().positive().default(1_000_000),
  MAX_TOOL_CALLBACK_REQUEST_BYTES: z.coerce.number().int().positive().default(200_000),
  REDACT_TELEMETRY: z.string().default('0'),
  REDACT_TELEMETRY_MODE: z.enum(['none', 'hash', 'truncate']).default('none'),
  REDACT_TELEMETRY_TRUNCATE_CHARS: z.coerce.number().int().positive().default(200)
});

export type Env = z.infer<typeof EnvSchema>;

export const getEnv = (): Env => EnvSchema.parse(process.env);
