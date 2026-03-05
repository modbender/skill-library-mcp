import { z } from 'zod';

const ConfigSchema = z.object({
  NODE_ENV: z.string().default('development'),
  PORT: z.coerce.number().int().positive().default(3000),
  PERSIST_RUNS: z.string().default('0').transform((v) => v === '1'),
  RUN_SYNC_TIMEOUT_MS: z.coerce.number().int().positive().default(30_000),

  REQUIRE_RUN_TOKEN: z.string().default('0').transform((v) => v === '1'),
  RUN_TOKENS: z.string().default(''),
  ALLOW_ANONYMOUS_READ: z.string().default('0').transform((v) => v === '1'),

  ENABLE_TOOL_REGISTER: z.string().optional(),
  ENABLE_TOOL_REGISTRATION: z.string().optional(),
  TOOL_ALLOWLIST: z.string().default(''),
  TOOL_CALLBACK_ALLOWLIST: z.string().default(''),
  TOOL_CALLBACK_ALLOW_LOCAL_TEST: z.string().default('0').transform((v) => v === '1'),
  TOOL_CALLBACK_MAX_BYTES: z.coerce.number().int().positive().default(256 * 1024),
  ALLOW_INSECURE_HTTP: z.string().default('0').transform((v) => v === '1'),
  ALLOW_INSECURE_HTTP_TOOLS: z.string().default('0').transform((v) => v === '1'),

  OUTBOUND_HOST_ALLOWLIST: z.string().default(''),
  OUTBOUND_ALLOWLIST: z.string().default(''),
  OUTBOUND_ALLOW_ALL: z.string().default('0').transform((v) => v === '1'),
  MAX_PROVIDER_REQUEST_BYTES: z.coerce.number().int().positive().default(1_000_000),
  MAX_TOOL_CALLBACK_REQUEST_BYTES: z.coerce.number().int().positive().default(200_000),

  PROVIDER: z.enum(['gateway', 'openai', 'mock']).optional(),
  LLM_PROVIDER: z.string().optional(),
  DEFAULT_PROVIDER_ID: z.string().optional(),
  GATEWAY_URL: z.string().default(''),
  GATEWAY_STEP_PATH: z.string().default('/v1/llm/step'),
  GATEWAY_API_KEY: z.string().default(''),
  GATEWAY_TIMEOUT_MS: z.coerce.number().int().positive().default(30_000),
  OPENAI_API_KEY: z.string().default(''),
  ANTHROPIC_API_KEY: z.string().default(''),

  TOKENOWNER_MAX_RUNNING: z.coerce.number().int().positive().default(8),
  TOKENOWNER_MAX_PER_MINUTE: z.coerce.number().int().positive().default(60),
  RUN_TTL_MS: z.coerce.number().int().positive().default(60 * 60 * 1000),
  RUN_TTL_TERMINAL_MS: z.coerce.number().int().positive().default(60 * 60 * 1000),
  MAX_RUNS_IN_MEMORY: z.coerce.number().int().positive().default(5000),

  MAX_EVENTS_PER_RUN: z.coerce.number().int().positive().default(2000),
  SSE_HEARTBEAT_MS: z.coerce.number().int().positive().default(15_000),
  MAX_ARTIFACT_BYTES_PER_RUN: z.coerce.number().int().positive().default(5_000_000),
  MAX_DEP_PAYLOAD_BYTES: z.coerce.number().int().positive().default(262_144),

  REDACT_TELEMETRY: z.string().default('0').transform((v) => v === '1'),
  REDACT_TELEMETRY_MODE: z.enum(['none', 'hash', 'truncate']).default('none'),
  REDACT_TELEMETRY_TRUNCATE_CHARS: z.coerce.number().int().positive().default(200),
  REDACT_EVENTS: z.string().default('0').transform((v) => v === '1')
});

export type AppConfig = z.infer<typeof ConfigSchema>;

export const getConfig = (): AppConfig => ConfigSchema.parse(process.env);

export const getToolAuth = (ref: string): string | undefined => process.env[`TOOL_AUTH_${ref}`];
