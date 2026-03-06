import { z, ZodError, type ZodType } from "zod";
import type { BinanceConfig } from "../config/schema";
import {
  ApiError,
  NetworkError,
  RateLimitError,
  SessionExpiredError,
  ValidationError,
  sanitizeSensitiveText
} from "../utils/errors";

type QueryValue = string | number | boolean | undefined | null;
export type FetchLike = (input: RequestInfo | URL, init?: RequestInit) => Promise<Response>;

export type RequestOptions<TResponse> = {
  method: "GET" | "POST" | "PUT" | "PATCH" | "DELETE";
  path: string;
  query?: Record<string, QueryValue>;
  body?: unknown;
  formData?: FormData;
  headers?: Record<string, string>;
  responseSchema?: ZodType<TResponse>;
};

const textResponseSchema = z.string();

const isAbortError = (error: unknown): boolean =>
  error instanceof DOMException ? error.name === "AbortError" : false;

const buildQueryString = (query: Record<string, QueryValue> | undefined): string => {
  if (!query) {
    return "";
  }

  const params = new URLSearchParams();
  for (const [key, value] of Object.entries(query)) {
    if (value === undefined || value === null) {
      continue;
    }
    params.set(key, String(value));
  }

  const encoded = params.toString();
  return encoded.length > 0 ? `?${encoded}` : "";
};

const readResponseBody = async (response: Response): Promise<unknown> => {
  const contentType = response.headers.get("content-type")?.toLowerCase() ?? "";
  if (contentType.includes("application/json")) {
    return response.json();
  }

  const text = await response.text();
  return textResponseSchema.parse(text);
};

const getErrorPreview = async (response: Response): Promise<string | undefined> => {
  try {
    const body = await response.text();
    if (body.trim().length === 0) {
      return undefined;
    }

    const trimmed = body.length > 240 ? `${body.slice(0, 240)}...` : body;
    return sanitizeSensitiveText(trimmed);
  } catch {
    return undefined;
  }
};

export class BinanceHttpClient {
  private readonly config: BinanceConfig;
  private readonly fetchImpl: FetchLike;

  public constructor(config: BinanceConfig, fetchImpl: FetchLike = fetch) {
    this.config = config;
    this.fetchImpl = fetchImpl;
  }

  public async getJson<TResponse>(
    path: string,
    options: Omit<RequestOptions<TResponse>, "method" | "path" | "body" | "formData"> = {}
  ): Promise<TResponse> {
    return this.request<TResponse>({
      ...options,
      method: "GET",
      path
    });
  }

  public async postJson<TResponse>(
    path: string,
    body: unknown,
    options: Omit<RequestOptions<TResponse>, "method" | "path" | "body" | "formData"> = {}
  ): Promise<TResponse> {
    return this.request<TResponse>({
      ...options,
      method: "POST",
      path,
      body
    });
  }

  public async postFormData<TResponse>(
    path: string,
    formData: FormData,
    options: Omit<RequestOptions<TResponse>, "method" | "path" | "body" | "formData"> = {}
  ): Promise<TResponse> {
    return this.request<TResponse>({
      ...options,
      method: "POST",
      path,
      formData
    });
  }

  public async request<TResponse>(options: RequestOptions<TResponse>): Promise<TResponse> {
    const url = `${this.config.apiBaseUrl}${options.path}${buildQueryString(options.query)}`;
    const hasJsonBody = options.body !== undefined && !options.formData;

    const headers = new Headers({
      Accept: "application/json, text/plain, */*",
      Cookie: this.config.cookieHeader,
      Referer: this.config.referer,
      "User-Agent": this.config.userAgent,
      ...(hasJsonBody ? { "Content-Type": "application/json" } : {}),
      ...(this.config.csrfToken ? { "X-CSRF-Token": this.config.csrfToken } : {}),
      ...(this.config.sessionToken ? { "X-Session-Token": this.config.sessionToken } : {}),
      ...(options.headers ?? {})
    });

    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), this.config.requestTimeoutMs);

    try {
      const requestInit: RequestInit = {
        method: options.method,
        headers,
        signal: controller.signal
      };

      if (options.formData) {
        requestInit.body = options.formData;
      } else if (options.body !== undefined) {
        requestInit.body = JSON.stringify(options.body);
      }

      const response = await this.fetchImpl(url, requestInit);

      if (!response.ok) {
        const preview = await getErrorPreview(response);
        const fallbackMessage = `Request failed (${response.status}) for ${options.method} ${options.path}`;
        const message = preview ? `${fallbackMessage}: ${preview}` : fallbackMessage;

        if (response.status === 401 || response.status === 403) {
          throw new SessionExpiredError(message, response.status);
        }
        if (response.status === 429) {
          throw new RateLimitError(message, response.status);
        }
        throw new ApiError(message, response.status);
      }

      const parsedBody = await readResponseBody(response);

      if (!options.responseSchema) {
        return parsedBody as TResponse;
      }

      return options.responseSchema.parse(parsedBody);
    } catch (error) {
      if (error instanceof SessionExpiredError || error instanceof RateLimitError || error instanceof ApiError) {
        throw error;
      }

      if (error instanceof ZodError) {
        throw new ValidationError(`Response validation failed: ${error.issues.map((issue) => issue.message).join(", ")}`);
      }

      if (isAbortError(error)) {
        throw new NetworkError(`Request timed out after ${this.config.requestTimeoutMs}ms`);
      }

      throw new NetworkError(
        `Network request failed for ${options.method} ${options.path}: ${
          error instanceof Error ? sanitizeSensitiveText(error.message) : "Unknown error"
        }`,
        error
      );
    } finally {
      clearTimeout(timeout);
    }
  }
}
