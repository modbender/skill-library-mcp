/**
 * @file circuit-breaker.js
 * @author kelexine <https://github.com/kelexine>
 * @description Circuit breaker pattern to prevent cascading failures against
 *              an unstable upstream service.
 *
 *              States:
 *                CLOSED    — Normal operation. Failures are counted.
 *                OPEN      — Requests are rejected immediately. Resets after timeout.
 *                HALF_OPEN — One probe request is allowed through to test recovery.
 */
import { CircuitBreakerError } from "./errors.js";
import { logger as rootLogger } from "./logger.js";

const STATES = Object.freeze({ CLOSED: "CLOSED", OPEN: "OPEN", HALF_OPEN: "HALF_OPEN" });

export class CircuitBreaker {
	/**
	 * @param {object} opts
	 * @param {string} [opts.name="default"]          - Breaker label for logs
	 * @param {number} [opts.threshold=5]             - Consecutive failures to open
	 * @param {number} [opts.resetTimeout=60000]      - ms before entering HALF_OPEN
	 * @param {number} [opts.successThreshold=2]      - Successes needed to close from HALF_OPEN
	 */
	constructor({
		name             = "default",
		threshold        = 5,
		resetTimeout     = 60_000,
		successThreshold = 2,
	} = {}) {
		this.name             = name;
		this.threshold        = threshold;
		this.resetTimeout     = resetTimeout;
		this.successThreshold = successThreshold;

		this._state          = STATES.CLOSED;
		this._failureCount   = 0;
		this._successCount   = 0;
		this._nextAttemptAt  = 0;

		this._log = rootLogger.child(`cb:${name}`);
	}

	/**
	 * Execute `fn` through the breaker.
	 * @template T
	 * @param {() => Promise<T>} fn
	 * @returns {Promise<T>}
	 */
	async call(fn) {
		if (this._state === STATES.OPEN) {
			if (Date.now() < this._nextAttemptAt) {
				const waitMs = this._nextAttemptAt - Date.now();
				throw new CircuitBreakerError({ breaker: this.name, retryInMs: waitMs });
			}
			this._transition(STATES.HALF_OPEN);
		}

		try {
			const result = await fn();
			this._onSuccess();
			return result;
		} catch (err) {
			this._onFailure(err);
			throw err;
		}
	}

	_onSuccess() {
		this._failureCount = 0;
		this._successCount++;

		if (this._state === STATES.HALF_OPEN) {
			if (this._successCount >= this.successThreshold) {
				this._log.info("Service recovered — circuit CLOSED");
				this._successCount = 0;
				this._transition(STATES.CLOSED);
			}
		}
	}

	_onFailure(err) {
		// Never trip on client errors (4xx except 429)
		const status = err.status;
		if (status && status < 500 && status !== 429) return;

		this._successCount = 0;
		this._failureCount++;

		const shouldOpen =
			this._failureCount >= this.threshold || this._state === STATES.HALF_OPEN;

		if (shouldOpen) {
			this._nextAttemptAt = Date.now() + this.resetTimeout;
			this._log.error("Circuit OPENED — too many failures", {
				failures:  this._failureCount,
				resetAt:   new Date(this._nextAttemptAt).toISOString(),
			});
			this._transition(STATES.OPEN);
		}
	}

	_transition(state) {
		this._state = state;
	}

	get state() { return this._state; }
	get isOpen() { return this._state === STATES.OPEN; }
}
