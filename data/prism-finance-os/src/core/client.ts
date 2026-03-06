/**
 * PRISM API HTTP Client
 * Base URL: https://api.prismapi.ai
 * Auth: X-API-Key header
 */

export interface RequestOptions {
  params?: Record<string, string | number | boolean | undefined>;
  cacheTtl?: number; // seconds
}

interface CacheEntry {
  data: unknown;
  expiresAt: number;
}

export class PrismClient {
  private baseUrl: string;
  private apiKey: string;
  private timeout: number;
  private cache = new Map<string, CacheEntry>();

  constructor(config: { apiKey: string; baseUrl?: string; timeout?: number }) {
    this.apiKey  = config.apiKey;
    this.baseUrl = (config.baseUrl ?? 'https://api.prismapi.ai').replace(/\/$/, '');
    this.timeout = config.timeout ?? 10_000;
  }

  private buildUrl(path: string, params?: Record<string, string | number | boolean | undefined>): string {
    const url = new URL(`${this.baseUrl}${path}`);
    if (params) {
      for (const [k, v] of Object.entries(params)) {
        if (v !== undefined && v !== null) url.searchParams.set(k, String(v));
      }
    }
    return url.toString();
  }

  private cacheKey(url: string): string { return url; }

  async get<T = unknown>(path: string, opts: RequestOptions = {}): Promise<T> {
    const url = this.buildUrl(path, opts.params);
    const key = this.cacheKey(url);

    if (opts.cacheTtl) {
      const hit = this.cache.get(key);
      if (hit && Date.now() < hit.expiresAt) return hit.data as T;
    }

    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), this.timeout);

    try {
      const res = await fetch(url, {
        method: 'GET',
        headers: {
          'X-API-Key': this.apiKey,
          'Accept': 'application/json',
          'User-Agent': 'prism-os-sdk/1.0',
        },
        signal: controller.signal,
      });

      if (!res.ok) {
        const body = await res.text().catch(() => '');
        throw new PrismApiError(res.status, res.statusText, body, path);
      }

      const data = await res.json() as T;

      if (opts.cacheTtl) {
        this.cache.set(key, { data, expiresAt: Date.now() + opts.cacheTtl * 1000 });
      }

      return data;
    } finally {
      clearTimeout(timer);
    }
  }

  async post<T = unknown>(path: string, body: unknown): Promise<T> {
    const url = this.buildUrl(path);
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), this.timeout);

    try {
      const res = await fetch(url, {
        method: 'POST',
        headers: {
          'X-API-Key': this.apiKey,
          'Content-Type': 'application/json',
          'Accept': 'application/json',
          'User-Agent': 'prism-os-sdk/1.0',
        },
        body: JSON.stringify(body),
        signal: controller.signal,
      });

      if (!res.ok) {
        const errBody = await res.text().catch(() => '');
        throw new PrismApiError(res.status, res.statusText, errBody, path);
      }

      return res.json() as Promise<T>;
    } finally {
      clearTimeout(timer);
    }
  }

  clearCache(): void { this.cache.clear(); }
}

export type PrismHttpClient = PrismClient;

export class PrismApiError extends Error {
  constructor(
    public status: number,
    public statusText: string,
    public body: string,
    public path: string,
  ) {
    super(`PRISM API ${status} on ${path}: ${statusText}`);
    this.name = 'PrismApiError';
  }
}
