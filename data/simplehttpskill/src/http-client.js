"use strict";

const http = require("http");
const https = require("https");
const { URL } = require("url");

const RETRYABLE_STATUS_CODES = new Set([429, 500, 502, 503, 504]);

const DEFAULTS = {
  maxRetries: 3,
  timeout: 30_000,
  backoffBase: 500,
  backoffMax: 30_000,
};

/**
 * Calculate exponential backoff delay with jitter.
 * @param {number} attempt - Zero-based attempt index.
 * @param {number} base - Base delay in ms.
 * @param {number} max - Maximum delay cap in ms.
 * @returns {number} Delay in ms.
 */
function backoffDelay(attempt, base, max) {
  const delay = Math.min(base * 2 ** attempt, max);
  return delay * (0.5 + Math.random() * 0.5);
}

/**
 * Sleep for a given number of milliseconds.
 * @param {number} ms
 * @returns {Promise<void>}
 */
function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

/**
 * Parse a raw body buffer into a string, and attempt JSON parse if appropriate.
 * @param {Buffer} buf
 * @param {string|undefined} contentType
 * @returns {any}
 */
function parseBody(buf, contentType) {
  const text = buf.toString("utf-8");
  if (contentType && contentType.includes("json")) {
    try {
      return JSON.parse(text);
    } catch {
      return text;
    }
  }
  return text;
}

/**
 * Execute a single HTTP(S) request. Returns a Promise that always resolves.
 * @param {object} opts
 * @param {string} opts.method
 * @param {URL} opts.parsedUrl
 * @param {Record<string, string>} opts.headers
 * @param {Buffer|null} opts.body
 * @param {number} opts.timeout
 * @returns {Promise<{ok: boolean, status: number|null, headers: Record<string,string>, body: any, error: string|null}>}
 */
function doRequest({ method, parsedUrl, headers, body, timeout }) {
  return new Promise((resolve) => {
    const transport = parsedUrl.protocol === "https:" ? https : http;

    const req = transport.request(
      parsedUrl,
      { method, headers, timeout },
      (res) => {
        const chunks = [];
        res.on("data", (chunk) => chunks.push(chunk));
        res.on("end", () => {
          const buf = Buffer.concat(chunks);
          const contentType = res.headers["content-type"] || "";
          const responseHeaders = Object.assign({}, res.headers);
          resolve({
            ok: res.statusCode >= 200 && res.statusCode < 300,
            status: res.statusCode,
            headers: responseHeaders,
            body: parseBody(buf, contentType),
            error: null,
          });
        });
        res.on("error", (err) => {
          resolve({
            ok: false,
            status: res.statusCode || null,
            headers: Object.assign({}, res.headers),
            body: null,
            error: err.message,
          });
        });
      }
    );

    req.on("timeout", () => {
      req.destroy(new Error("Request timed out"));
    });

    req.on("error", (err) => {
      resolve({
        ok: false,
        status: null,
        headers: {},
        body: null,
        error: err.message,
      });
    });

    if (body) {
      req.write(body);
    }
    req.end();
  });
}

class HttpClient {
  /**
   * @param {object} [options]
   * @param {Record<string, string>} [options.defaultHeaders] - Headers applied to every request.
   * @param {number} [options.maxRetries] - Max retry attempts for retryable failures.
   * @param {number} [options.timeout] - Socket timeout in ms.
   * @param {number} [options.backoffBase] - Base delay (ms) for exponential backoff.
   * @param {number} [options.backoffMax] - Maximum delay cap (ms) for backoff.
   */
  constructor(options = {}) {
    this.defaultHeaders = options.defaultHeaders || {};
    this.maxRetries = options.maxRetries ?? DEFAULTS.maxRetries;
    this.timeout = options.timeout ?? DEFAULTS.timeout;
    this.backoffBase = options.backoffBase ?? DEFAULTS.backoffBase;
    this.backoffMax = options.backoffMax ?? DEFAULTS.backoffMax;
  }

  /**
   * Send an HTTP request with automatic retries.
   *
   * @param {string} method - HTTP method (GET, POST, PUT, PATCH, DELETE, HEAD, OPTIONS).
   * @param {string} url - Fully qualified URL.
   * @param {object} [options]
   * @param {Record<string, string>} [options.headers] - Per-request headers (merged with defaults).
   * @param {string|Buffer|object} [options.body] - Request body. Objects are JSON-serialized.
   * @param {number} [options.timeout] - Override instance timeout (ms).
   * @param {number} [options.maxRetries] - Override instance maxRetries.
   * @returns {Promise<{ok: boolean, status: number|null, headers: Record<string,string>, body: any, error: string|null}>}
   */
  async request(method, url, options = {}) {
    method = method.toUpperCase();
    const effectiveTimeout = options.timeout ?? this.timeout;
    const effectiveRetries = options.maxRetries ?? this.maxRetries;

    const mergedHeaders = { ...this.defaultHeaders, ...options.headers };

    let body = null;
    if (options.body != null) {
      if (typeof options.body === "object" && !Buffer.isBuffer(options.body)) {
        body = Buffer.from(JSON.stringify(options.body), "utf-8");
        if (!mergedHeaders["Content-Type"] && !mergedHeaders["content-type"]) {
          mergedHeaders["Content-Type"] = "application/json";
        }
      } else if (typeof options.body === "string") {
        body = Buffer.from(options.body, "utf-8");
      } else {
        body = options.body;
      }
    }

    const parsedUrl = new URL(url);
    let lastResult = null;

    for (let attempt = 0; attempt <= effectiveRetries; attempt++) {
      lastResult = await doRequest({
        method,
        parsedUrl,
        headers: mergedHeaders,
        body,
        timeout: effectiveTimeout,
      });

      const shouldRetry =
        lastResult.status === null ||
        RETRYABLE_STATUS_CODES.has(lastResult.status);

      if (!shouldRetry || attempt === effectiveRetries) {
        return lastResult;
      }

      await sleep(
        backoffDelay(attempt, this.backoffBase, this.backoffMax)
      );
    }

    return lastResult;
  }

  /** @param {string} url @param {object} [options] */
  get(url, options) {
    return this.request("GET", url, options);
  }
  /** @param {string} url @param {object} [options] */
  post(url, options) {
    return this.request("POST", url, options);
  }
  /** @param {string} url @param {object} [options] */
  put(url, options) {
    return this.request("PUT", url, options);
  }
  /** @param {string} url @param {object} [options] */
  patch(url, options) {
    return this.request("PATCH", url, options);
  }
  /** @param {string} url @param {object} [options] */
  delete(url, options) {
    return this.request("DELETE", url, options);
  }
  /** @param {string} url @param {object} [options] */
  head(url, options) {
    return this.request("HEAD", url, options);
  }
  /** @param {string} url @param {object} [options] */
  options(url, options) {
    return this.request("OPTIONS", url, options);
  }
}

module.exports = { HttpClient };
