/**
 * @file errors.js
 * @author kelexine <https://github.com/kelexine>
 * @description Structured error hierarchy for typed, contextual error handling.
 */

/**
 * Base error class. All application errors extend this.
 */
export class BraveSearchError extends Error {
	/**
	 * @param {string} message
	 * @param {string} code    - Machine-readable error code
	 * @param {object} context - Arbitrary metadata for diagnostics
	 */
	constructor(message, code = "UNKNOWN_ERROR", context = {}) {
		super(message);
		this.name = this.constructor.name;
		this.code = code;
		this.context = context;
		this.timestamp = new Date().toISOString();
		Error.captureStackTrace?.(this, this.constructor);
	}

	toJSON() {
		return {
			name: this.name,
			code: this.code,
			message: this.message,
			context: this.context,
			timestamp: this.timestamp,
		};
	}
}

/** Thrown when environment variables or CLI arguments are invalid. */
export class ValidationError extends BraveSearchError {
	constructor(message, context = {}) {
		super(message, "VALIDATION_ERROR", context);
	}
}

/** Thrown on network-level failures (DNS, timeout, connection refused). */
export class NetworkError extends BraveSearchError {
	constructor(message, context = {}) {
		super(message, "NETWORK_ERROR", context);
	}
}

/** Thrown when an upstream HTTP API returns a non-success status. */
export class APIError extends BraveSearchError {
	/**
	 * @param {string} message
	 * @param {number} status  - HTTP status code
	 * @param {object} context
	 */
	constructor(message, status, context = {}) {
		super(message, "API_ERROR", { status, ...context });
		this.status = status;
	}
}

/** Thrown specifically on HTTP 429 responses. Carries a retryAfter hint. */
export class RateLimitError extends APIError {
	/**
	 * @param {number|null} retryAfter - Seconds to wait before retrying
	 * @param {object}      context
	 */
	constructor(retryAfter = null, context = {}) {
		super("Rate limit exceeded", 429, context);
		this.code = "RATE_LIMIT_ERROR";
		this.retryAfter = retryAfter;
	}
}

/** Thrown when HTML/Markdown parsing fails. */
export class ParseError extends BraveSearchError {
	constructor(message, context = {}) {
		super(message, "PARSE_ERROR", context);
	}
}

/** Thrown when the circuit breaker is open and requests are blocked. */
export class CircuitBreakerError extends BraveSearchError {
	constructor(context = {}) {
		super("Circuit breaker is OPEN — service temporarily unavailable", "CIRCUIT_BREAKER_OPEN", context);
	}
}
