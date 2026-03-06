import { ContractValidationError } from "../common/contract-validation.js";

type TickTickApiPrimitive = string | number | boolean;

export type TickTickApiMethod = "GET" | "POST" | "PUT" | "PATCH" | "DELETE";

export interface TickTickApiClientConfig {
  baseUrl: string;
  getAccessToken: () => string | Promise<string>;
  timeoutMs?: number;
  maxRetries?: number;
  retryBaseDelayMs?: number;
  defaultHeaders?: Record<string, string>;
  fetchImplementation?: TickTickFetchLike;
}

export interface TickTickApiRequest<TBody = unknown> {
  path: string;
  method?: TickTickApiMethod;
  query?: Record<string, TickTickApiPrimitive | null | undefined>;
  body?: TBody;
  headers?: Record<string, string>;
  timeoutMs?: number;
}

export interface TickTickApiRequestOptions {
  query?: Record<string, TickTickApiPrimitive | null | undefined>;
  headers?: Record<string, string>;
  timeoutMs?: number;
}

export interface TickTickApiErrorContext {
  status: number;
  statusText: string;
  retryable: boolean;
  retryAfterMs?: number;
  body?: unknown;
}

export class TickTickApiTimeoutError extends Error {
  readonly timeoutMs: number;
  override readonly cause?: unknown;

  constructor(timeoutMs: number, cause?: unknown) {
    super(`TickTick API request timed out after ${timeoutMs}ms.`);
    this.name = "TickTickApiTimeoutError";
    this.timeoutMs = timeoutMs;
    this.cause = cause;
  }
}

export class TickTickApiError extends Error {
  readonly status: number;
  readonly statusText: string;
  readonly retryable: boolean;
  readonly retryAfterMs?: number;
  readonly body?: unknown;

  constructor(context: TickTickApiErrorContext) {
    super(`TickTick API request failed with ${context.status} ${context.statusText}.`);
    this.name = "TickTickApiError";
    this.status = context.status;
    this.statusText = context.statusText;
    this.retryable = context.retryable;
    if (context.retryAfterMs !== undefined) {
      this.retryAfterMs = context.retryAfterMs;
    }
    if (context.body !== undefined) {
      this.body = context.body;
    }
  }
}

export class TickTickApiClient {
  private readonly config: ResolvedTickTickApiClientConfig;

  constructor(config: TickTickApiClientConfig) {
    this.config = resolveConfig(config);
  }

  async request<TResponse, TBody = unknown>(request: TickTickApiRequest<TBody>): Promise<TResponse> {
    const method = request.method ?? (request.body === undefined ? "GET" : "POST");
    const timeoutMs = request.timeoutMs ?? this.config.timeoutMs;
    const maxAttempts = this.config.maxRetries + 1;

    let attempt = 0;
    let latestError: unknown;

    while (attempt < maxAttempts) {
      try {
        const response = await this.execute(method, request, timeoutMs);
        if (!response.ok) {
          const errorBody = await readResponseBody(response);
          const retryAfterMs = parseRetryAfterMs(response.headers.get("retry-after"));
          const errorContext: TickTickApiErrorContext = {
            status: response.status,
            statusText: response.statusText,
            retryable: isRetryableStatus(response.status),
          };
          if (retryAfterMs !== undefined) {
            errorContext.retryAfterMs = retryAfterMs;
          }
          if (errorBody !== undefined) {
            errorContext.body = errorBody;
          }

          const apiError = new TickTickApiError(errorContext);

          if (apiError.retryable && attempt < maxAttempts - 1) {
            await sleep(retryAfterMs ?? computeBackoffMs(this.config.retryBaseDelayMs, attempt));
            attempt += 1;
            latestError = apiError;
            continue;
          }

          throw apiError;
        }

        return (await readResponseBody(response)) as TResponse;
      } catch (error) {
        const retryable = isRetryableThrownError(error);
        if (retryable && attempt < maxAttempts - 1) {
          await sleep(computeBackoffMs(this.config.retryBaseDelayMs, attempt));
          attempt += 1;
          latestError = error;
          continue;
        }
        throw error;
      }
    }

    throw latestError ?? new Error("TickTick API request failed after all retries.");
  }

  get<TResponse>(path: string, options?: TickTickApiRequestOptions): Promise<TResponse> {
    const request: TickTickApiRequest = {
      path,
      method: "GET",
    };
    if (options?.query !== undefined) {
      request.query = options.query;
    }
    if (options?.headers !== undefined) {
      request.headers = options.headers;
    }
    if (options?.timeoutMs !== undefined) {
      request.timeoutMs = options.timeoutMs;
    }

    return this.request<TResponse>(request);
  }

  post<TResponse, TBody = unknown>(
    path: string,
    body?: TBody,
    options?: TickTickApiRequestOptions
  ): Promise<TResponse> {
    const request: TickTickApiRequest<TBody> = {
      path,
      method: "POST",
    };
    if (body !== undefined) {
      request.body = body;
    }
    if (options?.query !== undefined) {
      request.query = options.query;
    }
    if (options?.headers !== undefined) {
      request.headers = options.headers;
    }
    if (options?.timeoutMs !== undefined) {
      request.timeoutMs = options.timeoutMs;
    }

    return this.request<TResponse, TBody>(request);
  }

  private async execute<TBody>(
    method: TickTickApiMethod,
    request: TickTickApiRequest<TBody>,
    timeoutMs: number
  ): Promise<TickTickFetchResponse> {
    const token = await this.config.getAccessToken();
    if (typeof token !== "string" || token.trim().length === 0) {
      throw new ContractValidationError("ticktick-api-client", "Access token provider returned an empty value.");
    }

    const headers = mergeHeaders(this.config.defaultHeaders, request.headers, {
      accept: "application/json",
      authorization: `Bearer ${token}`,
    });

    let body: string | undefined;
    if (request.body !== undefined) {
      headers["content-type"] = headers["content-type"] ?? "application/json";
      body = JSON.stringify(request.body);
    }

    const url = buildRequestUrl(this.config.baseUrl, request.path, request.query);

    const fetchInit: TickTickFetchInit = {
      method,
      headers,
    };
    if (body !== undefined) {
      fetchInit.body = body;
    }

    return runWithTimeout(
      () => this.config.fetchImplementation(url, fetchInit),
      timeoutMs
    );
  }
}

interface TickTickResponseHeadersLike {
  get(name: string): string | null;
}

interface TickTickFetchResponse {
  ok: boolean;
  status: number;
  statusText: string;
  headers: TickTickResponseHeadersLike;
  json(): Promise<unknown>;
  text(): Promise<string>;
}

type TickTickFetchLike = (url: string, init: TickTickFetchInit) => Promise<TickTickFetchResponse>;

interface TickTickFetchInit {
  method: TickTickApiMethod;
  headers: Record<string, string>;
  body?: string;
}

interface ResolvedTickTickApiClientConfig {
  baseUrl: string;
  timeoutMs: number;
  maxRetries: number;
  retryBaseDelayMs: number;
  defaultHeaders: Record<string, string>;
  getAccessToken: () => string | Promise<string>;
  fetchImplementation: TickTickFetchLike;
}

function resolveConfig(config: TickTickApiClientConfig): ResolvedTickTickApiClientConfig {
  if (config.baseUrl.trim().length === 0) {
    throw new ContractValidationError("ticktick-api-client", "baseUrl must be a non-empty string.");
  }

  const fetchImplementation = config.fetchImplementation ?? resolveDefaultFetch();

  const timeoutMs = config.timeoutMs ?? 10_000;
  if (!Number.isFinite(timeoutMs) || timeoutMs <= 0) {
    throw new ContractValidationError("ticktick-api-client", "timeoutMs must be a positive number.");
  }

  const maxRetries = config.maxRetries ?? 3;
  if (!Number.isInteger(maxRetries) || maxRetries < 0) {
    throw new ContractValidationError("ticktick-api-client", "maxRetries must be zero or a positive integer.");
  }

  const retryBaseDelayMs = config.retryBaseDelayMs ?? 250;
  if (!Number.isFinite(retryBaseDelayMs) || retryBaseDelayMs <= 0) {
    throw new ContractValidationError("ticktick-api-client", "retryBaseDelayMs must be a positive number.");
  }

  return {
    baseUrl: normalizeBaseUrl(config.baseUrl),
    timeoutMs,
    maxRetries,
    retryBaseDelayMs,
    defaultHeaders: normalizeHeaderNames(config.defaultHeaders ?? {}),
    getAccessToken: config.getAccessToken,
    fetchImplementation,
  };
}

function resolveDefaultFetch(): TickTickFetchLike {
  const fetchImpl = (globalThis as { fetch?: unknown }).fetch;
  if (typeof fetchImpl !== "function") {
    throw new ContractValidationError("ticktick-api-client", "fetch is not available in this runtime.");
  }

  return fetchImpl as TickTickFetchLike;
}

function normalizeBaseUrl(baseUrl: string): string {
  let parsed: URL;
  try {
    parsed = new URL(baseUrl);
  } catch {
    throw new ContractValidationError("ticktick-api-client", "baseUrl must be an absolute URL.");
  }

  const asString = parsed.toString();
  return asString.endsWith("/") ? asString.slice(0, -1) : asString;
}

function buildRequestUrl(
  baseUrl: string,
  path: string,
  query?: Record<string, TickTickApiPrimitive | null | undefined>
): string {
  const normalizedPath = path.startsWith("/") ? path : `/${path}`;
  const url = new URL(`${baseUrl}${normalizedPath}`);

  if (query !== undefined) {
    for (const [key, value] of Object.entries(query)) {
      if (value === undefined || value === null) {
        continue;
      }
      url.searchParams.set(key, String(value));
    }
  }

  return url.toString();
}

function mergeHeaders(...layers: Array<Record<string, string> | undefined>): Record<string, string> {
  const merged: Record<string, string> = {};

  for (const layer of layers) {
    if (layer === undefined) {
      continue;
    }
    const normalizedLayer = normalizeHeaderNames(layer);
    for (const [key, value] of Object.entries(normalizedLayer)) {
      merged[key] = value;
    }
  }

  return merged;
}

function normalizeHeaderNames(headers: Record<string, string>): Record<string, string> {
  const normalized: Record<string, string> = {};
  for (const [key, value] of Object.entries(headers)) {
    normalized[key.toLowerCase()] = value;
  }
  return normalized;
}

async function readResponseBody(response: TickTickFetchResponse): Promise<unknown> {
  if (response.status === 204) {
    return undefined;
  }

  const contentType = response.headers.get("content-type")?.toLowerCase() ?? "";
  if (contentType.includes("application/json")) {
    try {
      return await response.json();
    } catch {
      return undefined;
    }
  }

  const text = await response.text();
  return text.length === 0 ? undefined : text;
}

function isRetryableStatus(status: number): boolean {
  return status === 429 || status >= 500;
}

function isRetryableThrownError(error: unknown): boolean {
  if (error instanceof TickTickApiTimeoutError) {
    return true;
  }
  if (error instanceof TickTickApiError) {
    return error.retryable;
  }
  if (error instanceof Error) {
    return true;
  }

  return false;
}

function parseRetryAfterMs(retryAfterHeader: string | null): number | undefined {
  if (retryAfterHeader === null) {
    return undefined;
  }

  const seconds = Number.parseInt(retryAfterHeader, 10);
  if (Number.isFinite(seconds) && seconds >= 0) {
    return seconds * 1000;
  }

  const dateMs = Date.parse(retryAfterHeader);
  if (Number.isNaN(dateMs)) {
    return undefined;
  }

  const diff = dateMs - Date.now();
  return diff > 0 ? diff : 0;
}

function computeBackoffMs(baseDelayMs: number, attempt: number): number {
  const exponentialDelay = baseDelayMs * 2 ** attempt;
  const jitter = Math.floor(Math.random() * Math.max(50, Math.floor(baseDelayMs / 2)));
  return exponentialDelay + jitter;
}

async function runWithTimeout<T>(run: () => Promise<T>, timeoutMs: number): Promise<T> {
  let timeoutHandle: ReturnType<typeof setTimeout> | undefined;

  const timeoutPromise = new Promise<never>((_, reject) => {
    timeoutHandle = setTimeout(() => {
      reject(new TickTickApiTimeoutError(timeoutMs));
    }, timeoutMs);
  });

  try {
    const value = await Promise.race([run(), timeoutPromise]);
    return value;
  } catch (error) {
    if (error instanceof TickTickApiTimeoutError) {
      throw error;
    }
    throw error;
  } finally {
    if (timeoutHandle !== undefined) {
      clearTimeout(timeoutHandle);
    }
  }
}

function sleep(durationMs: number): Promise<void> {
  return new Promise((resolve) => {
    setTimeout(resolve, durationMs);
  });
}
