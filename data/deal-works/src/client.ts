/**
 * Shared HTTP client for engine API calls
 * Handles authentication, retries, and circuit breaking
 */

import { z } from "zod";

export interface EngineClientConfig {
  apiKey?: string;
  baseUrls?: Record<string, string>;
  timeout?: number;
  maxRetries?: number;
}

export interface EngineResponse<T = unknown> {
  success: boolean;
  data?: T;
  error?: {
    code: string;
    message: string;
    retryable: boolean;
  };
}

const DEFAULT_BASE_URLS: Record<string, string> = {
  deal: "https://deal.works/api",
  fund: "https://fund.works/api",
  bourse: "https://bourse.works/api",
  cadre: "https://cadre.works/api",
  oath: "https://oath.works/api",
  parler: "https://parler.works/api",
  academy: "https://academy.works/api",
  hq: "https://hq.works/api",
  clause: "https://clause.works/api",
};

const RETRYABLE_STATUS_CODES = [429, 502, 503, 504];
const RETRY_DELAYS = [1000, 2000, 4000];

// Circuit breaker state per engine
const circuitState: Record<string, {
  failures: number;
  lastFailure: number;
  openUntil: number;
}> = {};

const CIRCUIT_FAILURE_THRESHOLD = 5;
const CIRCUIT_WINDOW_MS = 60000;
const CIRCUIT_OPEN_DURATION_MS = 30000;

function checkCircuit(engine: string): void {
  const state = circuitState[engine];
  if (!state) return;

  const now = Date.now();
  if (state.openUntil > now) {
    throw new Error(`Circuit open for ${engine} engine. Retry after ${Math.ceil((state.openUntil - now) / 1000)}s`);
  }

  // Reset if window expired
  if (now - state.lastFailure > CIRCUIT_WINDOW_MS) {
    state.failures = 0;
  }
}

function recordFailure(engine: string): void {
  if (!circuitState[engine]) {
    circuitState[engine] = { failures: 0, lastFailure: 0, openUntil: 0 };
  }

  const state = circuitState[engine];
  const now = Date.now();

  state.failures++;
  state.lastFailure = now;

  if (state.failures >= CIRCUIT_FAILURE_THRESHOLD) {
    state.openUntil = now + CIRCUIT_OPEN_DURATION_MS;
    state.failures = 0;
  }
}

function recordSuccess(engine: string): void {
  if (circuitState[engine]) {
    circuitState[engine].failures = 0;
  }
}

export class EngineClient {
  private readonly apiKey: string | undefined;
  private readonly baseUrls: Record<string, string>;
  private readonly timeout: number;
  private readonly maxRetries: number;

  constructor(config: EngineClientConfig = {}) {
    this.apiKey = config.apiKey ?? process.env.DEAL_WORKS_API_KEY;
    this.baseUrls = { ...DEFAULT_BASE_URLS, ...config.baseUrls };
    this.timeout = config.timeout ?? 30000;
    this.maxRetries = config.maxRetries ?? 3;
  }

  async fetch<T>(
    engine: string,
    path: string,
    options: {
      method?: "GET" | "POST" | "PUT" | "DELETE";
      body?: unknown;
      idempotencyKey?: string;
    } = {}
  ): Promise<EngineResponse<T>> {
    const { method = "GET", body, idempotencyKey } = options;

    checkCircuit(engine);

    const baseUrl = this.baseUrls[engine];
    if (!baseUrl) {
      return {
        success: false,
        error: {
          code: "UNKNOWN_ENGINE",
          message: `Unknown engine: ${engine}`,
          retryable: false,
        },
      };
    }

    const url = `${baseUrl}${path}`;
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
      "User-Agent": "@goettelman/deal-works-mcp/0.1.0",
    };

    if (this.apiKey) {
      headers["Authorization"] = `Bearer ${this.apiKey}`;
    }

    if (idempotencyKey) {
      headers["X-Idempotency-Key"] = idempotencyKey;
    }

    let lastError: Error | null = null;

    for (let attempt = 0; attempt <= this.maxRetries; attempt++) {
      try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), this.timeout);

        const response = await fetch(url, {
          method,
          headers,
          body: body ? JSON.stringify(body) : undefined,
          signal: controller.signal,
        });

        clearTimeout(timeoutId);

        if (response.ok) {
          recordSuccess(engine);
          const data = await response.json() as T;
          return { success: true, data };
        }

        const isRetryable = RETRYABLE_STATUS_CODES.includes(response.status);

        if (!isRetryable || attempt === this.maxRetries) {
          recordFailure(engine);
          const errorBody = await response.text();
          return {
            success: false,
            error: {
              code: `HTTP_${response.status}`,
              message: errorBody || response.statusText,
              retryable: isRetryable,
            },
          };
        }

        // Wait before retry
        await sleep(RETRY_DELAYS[attempt] ?? 4000);
      } catch (err) {
        lastError = err instanceof Error ? err : new Error(String(err));

        if (attempt === this.maxRetries) {
          recordFailure(engine);
          return {
            success: false,
            error: {
              code: "NETWORK_ERROR",
              message: lastError.message,
              retryable: true,
            },
          };
        }

        await sleep(RETRY_DELAYS[attempt] ?? 4000);
      }
    }

    return {
      success: false,
      error: {
        code: "MAX_RETRIES_EXCEEDED",
        message: lastError?.message ?? "Max retries exceeded",
        retryable: false,
      },
    };
  }
}

function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

// Singleton instance
let clientInstance: EngineClient | null = null;

export function getEngineClient(config?: EngineClientConfig): EngineClient {
  if (!clientInstance || config) {
    clientInstance = new EngineClient(config);
  }
  return clientInstance;
}
