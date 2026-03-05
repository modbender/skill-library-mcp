/**
 * @file retry.js
 * @author kelexine <https://github.com/kelexine>
 * @description Exponential backoff retry with full jitter, Retry-After header
 *              support, and pluggable retry predicates.
 */
import { RateLimitError } from "./errors.js";
import { logger as rootLogger } from "./logger.js";

const log = rootLogger.child("retry");

/**
 * Execute `fn` with automatic retries on transient failures.
 *
 * @template T
 * @param {(attempt: number) => Promise<T>} fn
 * @param {object}   opts
 * @param {number}   [opts.attempts=3]         - Maximum total attempts
 * @param {number}   [opts.baseDelay=500]       - Base delay for backoff (ms)
 * @param {number}   [opts.maxDelay=30000]      - Max delay cap (ms)
 * @param {Function} [opts.shouldRetry]         - (err, attempt) => boolean
 * @param {string}   [opts.context="operation"] - Label for log messages
 * @returns {Promise<T>}
 */
export async function withRetry(fn, {
	attempts   = 3,
	baseDelay  = 500,
	maxDelay   = 30_000,
	shouldRetry = defaultShouldRetry,
	context    = "operation",
} = {}) {
	let lastError;

	for (let attempt = 1; attempt <= attempts; attempt++) {
		try {
			return await fn(attempt);
		} catch (err) {
			lastError = err;

			const isLast   = attempt === attempts;
			const canRetry = shouldRetry(err, attempt);

			if (isLast || !canRetry) {
				log.debug(`Giving up on ${context}`, { attempt, reason: err.message });
				throw err;
			}

			// Respect Retry-After header for rate-limit errors
			const delay = err instanceof RateLimitError && err.retryAfter != null
				? err.retryAfter * 1000
				: jitteredDelay(attempt, baseDelay, maxDelay);

			log.warn(`Retrying ${context}`, {
				attempt,
				maxAttempts: attempts,
				delayMs:     delay,
				error:       err.message,
			});

			await sleep(delay);
		}
	}

	throw lastError;
}

/**
 * Default retry predicate — retries on network errors, 429, and 5xx.
 * Does NOT retry on 4xx client errors (except 429).
 */
function defaultShouldRetry(err, _attempt) {
	if (err.code === "NETWORK_ERROR") return true;
	if (err.status === 429)           return true;
	if (err.status >= 500)            return true;
	return false;
}

/**
 * Full-jitter exponential delay:
 * random value in [0, min(maxDelay, baseDelay * 2^(attempt-1))]
 * This avoids thundering-herd on simultaneous retries.
 */
function jitteredDelay(attempt, base, max) {
	const ceiling = Math.min(max, base * 2 ** (attempt - 1));
	return Math.floor(Math.random() * ceiling);
}

function sleep(ms) {
	return new Promise((resolve) => setTimeout(resolve, ms));
}
