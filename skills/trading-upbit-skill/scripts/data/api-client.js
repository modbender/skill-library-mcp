const axios = require('axios');

/**
 * Public API client for Upbit endpoints (no auth).
 * - Retries on 429 / 5xx with exponential backoff
 * - Keeps interface minimal: request({ method, url, params, headers })
 */
async function sleep(ms) {
  return new Promise((r) => setTimeout(r, ms));
}

async function request(opts, retry = 5) {
  const { method, url, params, headers } = opts;
  const maxRetry = Math.max(0, retry);

  let attempt = 0;
  while (true) {
    try {
      const res = await axios({
        method,
        url,
        params,
        headers,
        timeout: 15000,
      });
      return res.data;
    } catch (err) {
      const status = err?.response?.status;
      const isRetryable = status === 429 || (status >= 500 && status < 600) || !status;
      if (!isRetryable || attempt >= maxRetry) {
        const msg = err?.response?.data?.error?.message || err.message;
        throw new Error(`Upbit public request failed (${status || 'NO_STATUS'}): ${msg}`);
      }

      // Rate limit: Upbit provides remaining-req header sometimes; simplest is backoff.
      const backoff = Math.min(2000 * Math.pow(2, attempt), 30000);
      await sleep(backoff);
      attempt += 1;
    }
  }
}

module.exports = { request };
