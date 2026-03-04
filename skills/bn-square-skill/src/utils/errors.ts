const SENSITIVE_KEYWORDS = ["cookie", "token", "session", "csrf", "authorization"] as const;

const KEY_VALUE_PATTERN =
  /\b([A-Za-z0-9_-]*(?:cookie|token|session|csrf|authorization)[A-Za-z0-9_-]*)=([^;\s,]+)/gi;
const BEARER_PATTERN = /\b(Bearer\s+)([A-Za-z0-9\-._~+/]+=*)/gi;

const REDACTED = "<redacted>";

export type AppErrorCode =
  | "CONFIG_ERROR"
  | "API_ERROR"
  | "SESSION_EXPIRED"
  | "NETWORK_ERROR"
  | "RATE_LIMIT_ERROR"
  | "VALIDATION_ERROR";

export type AppErrorOptions = {
  code: AppErrorCode;
  message: string;
  cause?: unknown;
  status?: number;
};

export const sanitizeSensitiveText = (text: string): string => {
  const sanitizedKeyValue = text.replace(KEY_VALUE_PATTERN, (_, key: string) => `${key}=${REDACTED}`);
  return sanitizedKeyValue.replace(BEARER_PATTERN, (_, prefix: string) => `${prefix}${REDACTED}`);
};

const isSensitiveKey = (key: string): boolean =>
  SENSITIVE_KEYWORDS.some((keyword) => key.toLowerCase().includes(keyword));

export const sanitizeRecord = (value: Record<string, string>): Record<string, string> =>
  Object.entries(value).reduce<Record<string, string>>((acc, [key, current]) => {
    acc[key] = isSensitiveKey(key) ? REDACTED : sanitizeSensitiveText(current);
    return acc;
  }, {});

export class AppError extends Error {
  public readonly code: AppErrorCode;
  public readonly status: number | undefined;

  public constructor(options: AppErrorOptions) {
    super(sanitizeSensitiveText(options.message));
    this.name = this.constructor.name;
    this.code = options.code;
    this.status = options.status;
    if (options.cause !== undefined) {
      this.cause = options.cause;
    }
  }
}

export class ConfigError extends AppError {
  public constructor(message: string, cause?: unknown) {
    super({
      code: "CONFIG_ERROR",
      message,
      ...(cause === undefined ? {} : { cause })
    });
  }
}

export class ApiError extends AppError {
  public constructor(message: string, status?: number, cause?: unknown) {
    super({
      code: "API_ERROR",
      message,
      ...(status === undefined ? {} : { status }),
      ...(cause === undefined ? {} : { cause })
    });
  }
}

export class SessionExpiredError extends AppError {
  public constructor(message = "Session expired or unauthorized", status?: number, cause?: unknown) {
    super({
      code: "SESSION_EXPIRED",
      message,
      ...(status === undefined ? {} : { status }),
      ...(cause === undefined ? {} : { cause })
    });
  }
}

export class NetworkError extends AppError {
  public constructor(message: string, cause?: unknown) {
    super({
      code: "NETWORK_ERROR",
      message,
      ...(cause === undefined ? {} : { cause })
    });
  }
}

export class RateLimitError extends AppError {
  public constructor(message: string, status = 429, cause?: unknown) {
    super({
      code: "RATE_LIMIT_ERROR",
      message,
      status,
      ...(cause === undefined ? {} : { cause })
    });
  }
}

export class ValidationError extends AppError {
  public constructor(message: string, cause?: unknown) {
    super({
      code: "VALIDATION_ERROR",
      message,
      ...(cause === undefined ? {} : { cause })
    });
  }
}

export const toSafeErrorMessage = (error: unknown, fallback = "Unexpected error"): string => {
  if (error instanceof AppError) {
    return sanitizeSensitiveText(error.message);
  }

  if (error instanceof Error) {
    return sanitizeSensitiveText(error.message);
  }

  if (typeof error === "string") {
    return sanitizeSensitiveText(error);
  }

  return fallback;
};
