/**
 * HTTP client with proxy support and rate limiting
 */

import axios, { type AxiosInstance, type AxiosRequestConfig, type AxiosResponse } from 'axios';
import { createLogger } from '../../utils/logger.js';
import { config } from '../../config/index.js';
import { ProxyRotator, getProxyRotator, type Proxy } from './proxy-rotator.js';
import { TokenBucketRateLimiter } from './rate-limiter.js';
import { RateLimitError } from '../../errors/index.js';

const logger = createLogger('http-client');

/**
 * User agents for rotation
 */
const USER_AGENTS = [
  'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
  'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
  'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
  'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15',
  'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0',
];

/**
 * Get a random user agent
 */
function getRandomUserAgent(): string {
  return USER_AGENTS[Math.floor(Math.random() * USER_AGENTS.length)] ?? USER_AGENTS[0]!;
}

export interface HttpClientConfig {
  /** Base URL for requests */
  baseURL?: string;
  /** Request timeout in ms */
  timeout?: number;
  /** Rate limiter instance */
  rateLimiter?: TokenBucketRateLimiter;
  /** Proxy rotator instance */
  proxyRotator?: ProxyRotator;
  /** Whether to use proxies */
  useProxy?: boolean;
  /** Whether to rotate user agents */
  rotateUserAgent?: boolean;
  /** Default headers */
  headers?: Record<string, string>;
}

/**
 * HTTP client with built-in rate limiting and proxy rotation
 */
export class HttpClient {
  private client: AxiosInstance;
  private rateLimiter?: TokenBucketRateLimiter;
  private proxyRotator: ProxyRotator;
  private useProxy: boolean;
  private rotateUserAgent: boolean;
  private currentProxy?: Proxy;

  constructor(clientConfig: HttpClientConfig = {}) {
    this.rateLimiter = clientConfig.rateLimiter;
    this.proxyRotator = clientConfig.proxyRotator ?? getProxyRotator();
    this.useProxy = clientConfig.useProxy ?? false;
    this.rotateUserAgent = clientConfig.rotateUserAgent ?? true;

    this.client = axios.create({
      baseURL: clientConfig.baseURL,
      timeout: clientConfig.timeout ?? config.REQUEST_TIMEOUT_MS,
      headers: {
        Accept: 'application/json, text/html, */*',
        'Accept-Language': 'en-US,en;q=0.9',
        ...clientConfig.headers,
      },
    });

    // Request interceptor
    this.client.interceptors.request.use(async (reqConfig) => {
      // Rate limiting
      if (this.rateLimiter) {
        await this.rateLimiter.acquire();
      }

      // User agent rotation
      if (this.rotateUserAgent) {
        reqConfig.headers['User-Agent'] = getRandomUserAgent();
      }

      // Proxy
      if (this.useProxy && this.proxyRotator.hasProxies()) {
        this.currentProxy = this.proxyRotator.getNext() ?? undefined;
        if (this.currentProxy) {
          reqConfig.httpsAgent = this.proxyRotator.createAgent(this.currentProxy);
          reqConfig.httpAgent = this.proxyRotator.createAgent(this.currentProxy);
          logger.debug(`Using proxy: ${this.currentProxy.url}`);
        }
      }

      logger.debug(`${reqConfig.method?.toUpperCase()} ${reqConfig.url}`);
      return reqConfig;
    });

    // Response interceptor
    this.client.interceptors.response.use(
      (response) => {
        // Mark proxy as successful
        if (this.currentProxy) {
          this.proxyRotator.markSuccess(this.currentProxy);
        }
        return response;
      },
      (error) => {
        // Mark proxy as failed on error
        if (this.currentProxy) {
          this.proxyRotator.markFailure(this.currentProxy);
        }

        // Handle rate limiting
        if (axios.isAxiosError(error) && error.response?.status === 429) {
          const retryAfter = error.response.headers['retry-after'];
          const retryMs = retryAfter ? parseInt(retryAfter, 10) * 1000 : 60000;
          throw new RateLimitError(retryMs, error.config?.baseURL ?? 'unknown');
        }

        throw error;
      }
    );
  }

  /**
   * Make a GET request
   */
  async get<T = unknown>(url: string, config?: AxiosRequestConfig): Promise<AxiosResponse<T>> {
    return this.client.get<T>(url, config);
  }

  /**
   * Make a POST request
   */
  async post<T = unknown>(
    url: string,
    data?: unknown,
    config?: AxiosRequestConfig
  ): Promise<AxiosResponse<T>> {
    return this.client.post<T>(url, data, config);
  }

  /**
   * Make a PUT request
   */
  async put<T = unknown>(
    url: string,
    data?: unknown,
    config?: AxiosRequestConfig
  ): Promise<AxiosResponse<T>> {
    return this.client.put<T>(url, data, config);
  }

  /**
   * Make a DELETE request
   */
  async delete<T = unknown>(url: string, config?: AxiosRequestConfig): Promise<AxiosResponse<T>> {
    return this.client.delete<T>(url, config);
  }

  /**
   * Get the underlying axios instance
   */
  getAxiosInstance(): AxiosInstance {
    return this.client;
  }
}

/**
 * Create an HTTP client for API calls (no proxy, with rate limiting)
 */
export function createApiClient(
  baseURL: string,
  rateLimiter?: TokenBucketRateLimiter,
  headers?: Record<string, string>
): HttpClient {
  return new HttpClient({
    baseURL,
    rateLimiter,
    useProxy: false,
    rotateUserAgent: false,
    headers,
  });
}

/**
 * Create an HTTP client for scraping (proxy + user agent rotation)
 */
export function createScrapingClient(
  rateLimiter?: TokenBucketRateLimiter,
  proxyRotator?: ProxyRotator
): HttpClient {
  return new HttpClient({
    rateLimiter,
    proxyRotator,
    useProxy: true,
    rotateUserAgent: true,
  });
}
