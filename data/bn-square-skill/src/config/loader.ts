import { existsSync, readFileSync } from "node:fs";
import path from "node:path";
import dotenv from "dotenv";
import { ZodError } from "zod";
import { type BinanceConfig, binanceConfigSchema } from "./schema";
import { ConfigError, sanitizeSensitiveText } from "../utils/errors";

export type LoadConfigOptions = {
  cwd?: string;
  env?: NodeJS.ProcessEnv;
  envPath?: string;
  configPath?: string;
  skipEnvFile?: boolean;
};

const DEFAULT_CONFIG_FILENAME = "config.json";

const parseOptionalNumber = (rawValue: string | undefined): number | undefined => {
  if (rawValue === undefined || rawValue.trim().length === 0) {
    return undefined;
  }

  const parsed = Number(rawValue);
  if (!Number.isFinite(parsed)) {
    throw new ConfigError(`Invalid numeric value: "${sanitizeSensitiveText(rawValue)}"`);
  }

  return parsed;
};

const parseOptionalCsv = (rawValue: string | undefined): string[] | undefined => {
  if (rawValue === undefined || rawValue.trim().length === 0) {
    return undefined;
  }

  const parsed = rawValue
    .split(",")
    .map((item) => item.trim())
    .filter((item) => item.length > 0);
  return parsed.length > 0 ? parsed : undefined;
};

const resolveConfigPath = (cwd: string, options: LoadConfigOptions, env: NodeJS.ProcessEnv): string | undefined => {
  const configuredPath = options.configPath ?? env.BINANCE_CONFIG_PATH;
  if (configuredPath) {
    return path.resolve(cwd, configuredPath);
  }

  const defaultPath = path.resolve(cwd, DEFAULT_CONFIG_FILENAME);
  return existsSync(defaultPath) ? defaultPath : undefined;
};

const toValidationErrorMessage = (error: ZodError): string =>
  error.issues
    .map((issue) => {
      const issuePath = issue.path.length > 0 ? issue.path.join(".") : "config";
      return `${issuePath}: ${issue.message}`;
    })
    .join("; ");

const readEnv = (options: LoadConfigOptions, cwd: string): NodeJS.ProcessEnv => {
  if (options.env) {
    return options.env;
  }

  const envFromProcess: NodeJS.ProcessEnv = { ...process.env };
  if (options.skipEnvFile) {
    return envFromProcess;
  }

  const resolvedEnvPath = path.resolve(cwd, options.envPath ?? ".env");
  if (!existsSync(resolvedEnvPath)) {
    return envFromProcess;
  }

  const rawEnv = readFileSync(resolvedEnvPath, "utf8");
  const parsedEnv = dotenv.parse(rawEnv);

  return {
    ...parsedEnv,
    ...envFromProcess
  };
};

const buildConfigFromEnv = (env: NodeJS.ProcessEnv): BinanceConfig => {
  const configShape = {
    cdpUrl: env.BINANCE_CDP_URL,
    apiBaseUrl: env.BINANCE_API_BASE_URL,
    cookieHeader: env.BINANCE_COOKIE_HEADER,
    csrfToken: env.BINANCE_CSRF_TOKEN,
    sessionToken: env.BINANCE_SESSION_TOKEN,
    userAgent: env.BINANCE_USER_AGENT,
    referer: env.BINANCE_REFERER,
    requestTimeoutMs: parseOptionalNumber(env.BINANCE_REQUEST_TIMEOUT_MS),
    postUrlTemplate: env.BINANCE_POST_URL_TEMPLATE,
    endpoints: {
      validateSessionPath: env.BINANCE_VALIDATE_SESSION_PATH,
      publishPostPath: env.BINANCE_PUBLISH_POST_PATH,
      getPostStatusPath: env.BINANCE_GET_POST_STATUS_PATH,
      imageUploadPath: env.BINANCE_IMAGE_UPLOAD_PATH,
      statusQueryParam: env.BINANCE_STATUS_QUERY_PARAM
    },
    image: {
      uploadFieldName: env.BINANCE_IMAGE_UPLOAD_FIELD,
      maxBytes: parseOptionalNumber(env.BINANCE_IMAGE_MAX_BYTES),
      allowedMimeTypes: parseOptionalCsv(env.BINANCE_IMAGE_ALLOWED_MIME)
    }
  };

  try {
    return binanceConfigSchema.parse(configShape);
  } catch (error) {
    if (error instanceof ZodError) {
      throw new ConfigError(`Invalid environment configuration: ${toValidationErrorMessage(error)}`);
    }
    throw error;
  }
};

const parseConfigJson = (filePath: string): unknown => {
  try {
    const raw = readFileSync(filePath, "utf8");
    return JSON.parse(raw) as unknown;
  } catch (error) {
    throw new ConfigError(`Unable to parse config file at "${filePath}"`, error);
  }
};

export const loadConfig = (options: LoadConfigOptions = {}): BinanceConfig => {
  const cwd = options.cwd ?? process.cwd();
  const env = readEnv(options, cwd);
  const configPath = resolveConfigPath(cwd, options, env);

  if (!configPath) {
    return buildConfigFromEnv(env);
  }

  const parsedJson = parseConfigJson(configPath);
  const root = typeof parsedJson === "object" && parsedJson !== null ? parsedJson : undefined;

  const normalizedConfigCandidate =
    root && "binance" in root && typeof root.binance === "object" && root.binance !== null
      ? root.binance
      : parsedJson;

  try {
    return binanceConfigSchema.parse(normalizedConfigCandidate);
  } catch (error) {
    if (error instanceof ZodError) {
      throw new ConfigError(`Invalid config file "${configPath}": ${toValidationErrorMessage(error)}`);
    }
    throw error;
  }
};
