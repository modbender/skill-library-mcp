import { ContractValidationError } from "../common/contract-validation.js";

export type TickTickEnvSource = Record<string, string | undefined>;

export interface TickTickEnvSchema {
  clientId: string;
  clientSecret: string;
  redirectUri: string;
  oauthAuthorizeUrl: string;
  oauthTokenUrl: string;
  apiBaseUrl: string;
  apiTimeoutMs: number;
  apiMaxRetries: number;
  apiRetryBaseDelayMs: number;
  oauthScope?: string;
  userAgent?: string;
}

const CONTRACT = "ticktick-env";

const DEFAULTS = {
  oauthAuthorizeUrl: "https://ticktick.com/oauth/authorize",
  oauthTokenUrl: "https://ticktick.com/oauth/token",
  apiBaseUrl: "https://api.ticktick.com/open/v1",
  apiTimeoutMs: 10_000,
  apiMaxRetries: 3,
  apiRetryBaseDelayMs: 250,
} as const;

const ENV_KEYS = {
  clientId: "TICKTICK_CLIENT_ID",
  clientSecret: "TICKTICK_CLIENT_SECRET",
  redirectUri: "TICKTICK_REDIRECT_URI",
  oauthAuthorizeUrl: "TICKTICK_OAUTH_AUTHORIZE_URL",
  oauthTokenUrl: "TICKTICK_OAUTH_TOKEN_URL",
  apiBaseUrl: "TICKTICK_API_BASE_URL",
  apiTimeoutMs: "TICKTICK_API_TIMEOUT_MS",
  apiMaxRetries: "TICKTICK_API_MAX_RETRIES",
  apiRetryBaseDelayMs: "TICKTICK_API_RETRY_BASE_DELAY_MS",
  oauthScope: "TICKTICK_OAUTH_SCOPE",
  userAgent: "TICKTICK_USER_AGENT",
} as const;

export function parseTickTickEnv(source: TickTickEnvSource): TickTickEnvSchema {
  const clientId = readRequired(source, ENV_KEYS.clientId);
  const clientSecret = readRequired(source, ENV_KEYS.clientSecret);
  const redirectUri = validateUrl(readRequired(source, ENV_KEYS.redirectUri), ENV_KEYS.redirectUri, {
    requireHttps: false,
  });

  const oauthAuthorizeUrl = normalizeBaseUrl(
    validateUrl(
      readWithDefault(source, ENV_KEYS.oauthAuthorizeUrl, DEFAULTS.oauthAuthorizeUrl),
      ENV_KEYS.oauthAuthorizeUrl,
      { requireHttps: true }
    )
  );

  const oauthTokenUrl = normalizeBaseUrl(
    validateUrl(readWithDefault(source, ENV_KEYS.oauthTokenUrl, DEFAULTS.oauthTokenUrl), ENV_KEYS.oauthTokenUrl, {
      requireHttps: true,
    })
  );

  const apiBaseUrl = normalizeBaseUrl(
    validateUrl(readWithDefault(source, ENV_KEYS.apiBaseUrl, DEFAULTS.apiBaseUrl), ENV_KEYS.apiBaseUrl, {
      requireHttps: true,
    })
  );

  const apiTimeoutMs = readInteger(
    source,
    ENV_KEYS.apiTimeoutMs,
    DEFAULTS.apiTimeoutMs,
    (value) => value > 0,
    "must be a positive integer"
  );

  const apiMaxRetries = readInteger(
    source,
    ENV_KEYS.apiMaxRetries,
    DEFAULTS.apiMaxRetries,
    (value) => value >= 0,
    "must be zero or a positive integer"
  );

  const apiRetryBaseDelayMs = readInteger(
    source,
    ENV_KEYS.apiRetryBaseDelayMs,
    DEFAULTS.apiRetryBaseDelayMs,
    (value) => value > 0,
    "must be a positive integer"
  );

  const oauthScope = readOptional(source, ENV_KEYS.oauthScope);
  const userAgent = readOptional(source, ENV_KEYS.userAgent);

  const parsed: TickTickEnvSchema = {
    clientId,
    clientSecret,
    redirectUri,
    oauthAuthorizeUrl,
    oauthTokenUrl,
    apiBaseUrl,
    apiTimeoutMs,
    apiMaxRetries,
    apiRetryBaseDelayMs,
  };

  if (oauthScope !== undefined) {
    parsed.oauthScope = oauthScope;
  }
  if (userAgent !== undefined) {
    parsed.userAgent = userAgent;
  }

  return parsed;
}

export function parseTickTickEnvFromRuntime(): TickTickEnvSchema {
  const runtime = globalThis as { process?: { env?: TickTickEnvSource } };
  return parseTickTickEnv(runtime.process?.env ?? {});
}

function readRequired(source: TickTickEnvSource, key: string): string {
  const value = source[key];
  if (typeof value !== "string" || value.trim().length === 0) {
    throw new ContractValidationError(CONTRACT, `Missing required env var '${key}'.`);
  }
  return value;
}

function readOptional(source: TickTickEnvSource, key: string): string | undefined {
  const value = source[key];
  if (value === undefined || value === "") {
    return undefined;
  }
  return value;
}

function readWithDefault(source: TickTickEnvSource, key: string, fallback: string): string {
  const value = source[key];
  if (value === undefined || value.trim().length === 0) {
    return fallback;
  }
  return value;
}

function readInteger(
  source: TickTickEnvSource,
  key: string,
  fallback: number,
  validate: (value: number) => boolean,
  validationMessage: string
): number {
  const raw = source[key];
  if (raw === undefined || raw.trim().length === 0) {
    return fallback;
  }

  const value = Number.parseInt(raw, 10);
  if (!Number.isFinite(value) || !validate(value)) {
    throw new ContractValidationError(CONTRACT, `Invalid env var '${key}' (${validationMessage}).`);
  }

  return value;
}

function validateUrl(value: string, key: string, options: { requireHttps: boolean }): string {
  let parsed: URL;
  try {
    parsed = new URL(value);
  } catch {
    throw new ContractValidationError(CONTRACT, `Invalid URL in '${key}'.`);
  }

  if (!["http:", "https:"].includes(parsed.protocol)) {
    throw new ContractValidationError(CONTRACT, `Invalid protocol in '${key}'.`);
  }

  if (options.requireHttps && parsed.protocol !== "https:") {
    throw new ContractValidationError(CONTRACT, `Expected '${key}' to use https.`);
  }

  return parsed.toString();
}

function normalizeBaseUrl(value: string): string {
  return value.endsWith("/") ? value.slice(0, -1) : value;
}
