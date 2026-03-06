// SPDX-License-Identifier: MIT
/**
 * Plugin configuration with sensible defaults.
 *
 * Every option can be left unset for a zero-config quickstart —
 * just export LOGFIRE_TOKEN and enable the plugin.
 */

export interface DistributedTracingConfig {
  enabled: boolean;
  injectIntoCommands: boolean;
  extractFromWebhooks: boolean;
  urlPatterns: string[];
}

export interface BatchConfig {
  maxQueueSize: number;
  maxExportBatchSize: number;
  scheduledDelayMs: number;
}

export interface LogfirePluginConfig {
  // Authentication
  token: string;

  // Logfire project
  projectUrl: string;
  region: 'us' | 'eu';
  environment: string;
  serviceName: string;

  // GenAI provider
  providerName: string;

  // Trace depth
  captureToolInput: boolean;
  captureToolOutput: boolean;
  toolInputMaxLength: number;
  toolOutputMaxLength: number;
  captureStackTraces: boolean;
  captureMessageContent: boolean;
  captureToolDefinitions: boolean;
  captureInferenceEvents: boolean;
  redactSecrets: boolean;

  // Distributed tracing
  distributedTracing: DistributedTracingConfig;

  // Metrics
  enableMetrics: boolean;
  metricsIntervalMs: number;

  // Output
  enableTraceLinks: boolean;
  logLevel: 'debug' | 'info' | 'warn' | 'error';

  // Advanced
  resourceAttributes: Record<string, string>;
  spanProcessorType: 'batch' | 'simple';
  batchConfig: BatchConfig;
}

const DEFAULTS: LogfirePluginConfig = {
  token: '',
  projectUrl: '',
  region: 'us',
  environment: '',
  serviceName: 'openclaw-agent',
  providerName: '',

  captureToolInput: true,
  captureToolOutput: false,
  toolInputMaxLength: 2048,
  toolOutputMaxLength: 512,
  captureStackTraces: true,
  captureMessageContent: false,
  captureToolDefinitions: false,
  captureInferenceEvents: false,
  redactSecrets: true,

  distributedTracing: {
    enabled: false,
    injectIntoCommands: true,
    extractFromWebhooks: true,
    urlPatterns: ['*'],
  },

  enableMetrics: true,
  metricsIntervalMs: 60_000,

  enableTraceLinks: true,
  logLevel: 'info',

  resourceAttributes: {},
  spanProcessorType: 'batch',
  batchConfig: {
    maxQueueSize: 2048,
    maxExportBatchSize: 512,
    scheduledDelayMs: 5000,
  },
};

/**
 * Merge user-provided config with defaults and env vars.
 * Env vars serve as fallbacks when explicit config is not set.
 */
export function resolveConfig(
  userConfig: Record<string, unknown> | undefined,
): LogfirePluginConfig {
  const raw = userConfig ?? {};

  const distributedTracingRaw =
    (raw.distributedTracing as Record<string, unknown>) ?? {};
  const batchConfigRaw = (raw.batchConfig as Record<string, unknown>) ?? {};

  return {
    token:
      asString(raw.token) ||
      process.env.LOGFIRE_TOKEN ||
      '',
    projectUrl:
      asString(raw.projectUrl) ||
      process.env.LOGFIRE_PROJECT_URL ||
      DEFAULTS.projectUrl,
    region: asEnum(raw.region, ['us', 'eu']) ?? DEFAULTS.region,
    environment:
      asString(raw.environment) ||
      process.env.LOGFIRE_ENVIRONMENT ||
      'development',
    serviceName: asString(raw.serviceName) || DEFAULTS.serviceName,
    providerName:
      asString(raw.providerName) ||
      process.env.LOGFIRE_PROVIDER_NAME ||
      DEFAULTS.providerName,

    captureToolInput: asBool(raw.captureToolInput) ?? DEFAULTS.captureToolInput,
    captureToolOutput:
      asBool(raw.captureToolOutput) ?? DEFAULTS.captureToolOutput,
    toolInputMaxLength:
      asInt(raw.toolInputMaxLength) ?? DEFAULTS.toolInputMaxLength,
    toolOutputMaxLength:
      asInt(raw.toolOutputMaxLength) ?? DEFAULTS.toolOutputMaxLength,
    captureStackTraces:
      asBool(raw.captureStackTraces) ?? DEFAULTS.captureStackTraces,
    captureMessageContent:
      asBool(raw.captureMessageContent) ?? DEFAULTS.captureMessageContent,
    captureToolDefinitions:
      asBool(raw.captureToolDefinitions) ?? DEFAULTS.captureToolDefinitions,
    captureInferenceEvents:
      asBool(raw.captureInferenceEvents) ?? DEFAULTS.captureInferenceEvents,
    redactSecrets: asBool(raw.redactSecrets) ?? DEFAULTS.redactSecrets,

    distributedTracing: {
      enabled:
        asBool(distributedTracingRaw.enabled) ??
        DEFAULTS.distributedTracing.enabled,
      injectIntoCommands:
        asBool(distributedTracingRaw.injectIntoCommands) ??
        DEFAULTS.distributedTracing.injectIntoCommands,
      extractFromWebhooks:
        asBool(distributedTracingRaw.extractFromWebhooks) ??
        DEFAULTS.distributedTracing.extractFromWebhooks,
      urlPatterns:
        asStringArray(distributedTracingRaw.urlPatterns) ??
        DEFAULTS.distributedTracing.urlPatterns,
    },

    enableMetrics: asBool(raw.enableMetrics) ?? DEFAULTS.enableMetrics,
    metricsIntervalMs:
      asInt(raw.metricsIntervalMs) ?? DEFAULTS.metricsIntervalMs,

    enableTraceLinks: asBool(raw.enableTraceLinks) ?? DEFAULTS.enableTraceLinks,
    logLevel:
      asEnum(raw.logLevel, ['debug', 'info', 'warn', 'error']) ??
      DEFAULTS.logLevel,

    resourceAttributes:
      asStringRecord(raw.resourceAttributes) ?? DEFAULTS.resourceAttributes,
    spanProcessorType:
      asEnum(raw.spanProcessorType, ['batch', 'simple']) ??
      DEFAULTS.spanProcessorType,
    batchConfig: {
      maxQueueSize:
        asInt(batchConfigRaw.maxQueueSize) ?? DEFAULTS.batchConfig.maxQueueSize,
      maxExportBatchSize:
        asInt(batchConfigRaw.maxExportBatchSize) ??
        DEFAULTS.batchConfig.maxExportBatchSize,
      scheduledDelayMs:
        asInt(batchConfigRaw.scheduledDelayMs) ??
        DEFAULTS.batchConfig.scheduledDelayMs,
    },
  };
}

// --- type coercion helpers ---

function asString(v: unknown): string {
  return typeof v === 'string' ? v : '';
}

function asBool(v: unknown): boolean | undefined {
  return typeof v === 'boolean' ? v : undefined;
}

function asInt(v: unknown): number | undefined {
  return typeof v === 'number' && Number.isInteger(v) ? v : undefined;
}

function asEnum<T extends string>(
  v: unknown,
  allowed: T[],
): T | undefined {
  return typeof v === 'string' && (allowed as string[]).includes(v)
    ? (v as T)
    : undefined;
}

function asStringArray(v: unknown): string[] | undefined {
  return Array.isArray(v) && v.every((x) => typeof x === 'string')
    ? v
    : undefined;
}

function asStringRecord(
  v: unknown,
): Record<string, string> | undefined {
  if (typeof v !== 'object' || v === null || Array.isArray(v)) return undefined;
  const entries = Object.entries(v as Record<string, unknown>);
  if (entries.every(([, val]) => typeof val === 'string')) {
    return v as Record<string, string>;
  }
  return undefined;
}
