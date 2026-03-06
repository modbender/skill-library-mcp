/**
 * @file config.js
 * @author kelexine <https://github.com/kelexine>
 * @description Centralized configuration with environment variable validation,
 *              typed parsing, and descriptive startup errors.
 */
import { ValidationError } from "./errors.js";

/**
 * @typedef {object} EnvSchema
 * @property {boolean}  [required]    - Fail hard at startup if missing
 * @property {string}   [default]     - Fallback raw string value
 * @property {string}   [description] - Human-readable description
 * @property {string[]} [enum]        - Allowed values
 * @property {Function} [parse]       - Transform raw string to final type
 * @property {Function} [validate]    - Additional validation (returns string | null)
 */

/** @type {Record<string, EnvSchema>} */
const SCHEMA = {
	BRAVE_API_KEY: {
		required: true,
		description: "Brave Search API subscription token",
	},
	LOG_LEVEL: {
		default: "info",
		enum: ["debug", "info", "warn", "error", "silent"],
		description: "Minimum log level",
	},
	LOG_JSON: {
		default: "false",
		enum: ["true", "false"],
		description: "Emit logs as newline-delimited JSON",
	},

	// Timeouts
	FETCH_TIMEOUT_MS: {
		default: "15000",
		parse: Number,
		validate: (v) => (v > 0 ? null : "must be a positive integer"),
		description: "Timeout (ms) for individual page fetches",
	},
	SEARCH_TIMEOUT_MS: {
		default: "10000",
		parse: Number,
		validate: (v) => (v > 0 ? null : "must be a positive integer"),
		description: "Timeout (ms) for Brave Search API calls",
	},

	// Content
	MAX_CONTENT_LENGTH: {
		default: "5000",
		parse: Number,
		validate: (v) => (v >= 100 ? null : "must be >= 100"),
		description: "Max characters of extracted page content",
	},

	// Retry
	MAX_RETRY_ATTEMPTS: {
		default: "3",
		parse: Number,
		validate: (v) => (v >= 1 && v <= 10 ? null : "must be between 1 and 10"),
		description: "Max retry attempts for transient failures",
	},
	RETRY_BASE_DELAY_MS: {
		default: "500",
		parse: Number,
		validate: (v) => (v >= 0 ? null : "must be >= 0"),
		description: "Base delay (ms) for exponential backoff",
	},
	RETRY_MAX_DELAY_MS: {
		default: "30000",
		parse: Number,
		validate: (v) => (v >= 0 ? null : "must be >= 0"),
		description: "Maximum delay cap (ms) for backoff",
	},

	// Concurrency
	CONCURRENCY_LIMIT: {
		default: "3",
		parse: Number,
		validate: (v) => (v >= 1 && v <= 20 ? null : "must be between 1 and 20"),
		description: "Max simultaneous content-fetch requests",
	},

	// Circuit Breaker
	CB_FAILURE_THRESHOLD: {
		default: "5",
		parse: Number,
		validate: (v) => (v >= 1 ? null : "must be >= 1"),
		description: "Consecutive failures before opening circuit breaker",
	},
	CB_RESET_TIMEOUT_MS: {
		default: "60000",
		parse: Number,
		validate: (v) => (v >= 1000 ? null : "must be >= 1000"),
		description: "Time (ms) before circuit breaker attempts recovery",
	},
};

/**
 * Parse and validate environment variables against the schema.
 * @param {boolean} [requireApiKey=true]
 * @returns {Record<string, any>}
 */
function buildConfig(requireApiKey = true) {
	const errors = [];
	const cfg = {};

	for (const [key, def] of Object.entries(SCHEMA)) {
		const raw = process.env[key];

		if (!raw && def.required && requireApiKey) {
			errors.push(`${key}: required — ${def.description}`);
			continue;
		}

		const value = raw ?? def.default ?? "";

		if (def.enum && value && !def.enum.includes(value)) {
			errors.push(`${key}: invalid value "${value}" — must be one of [${def.enum.join(", ")}]`);
			continue;
		}

		const parsed = def.parse ? def.parse(value) : value;

		if (def.parse && isNaN(parsed)) {
			errors.push(`${key}: "${value}" is not a valid number`);
			continue;
		}

		if (def.validate) {
			const msg = def.validate(parsed);
			if (msg) {
				errors.push(`${key}: ${msg}`);
				continue;
			}
		}

		cfg[key] = parsed;
	}

	if (errors.length > 0) {
		throw new ValidationError(
			`Configuration validation failed:\n${errors.map((e) => `  ✗ ${e}`).join("\n")}\n\nSet these as environment variables and retry.`,
		);
	}

	return cfg;
}

// Lazily evaluated — API key is only enforced at call time, not on import.
export const config = buildConfig(false);

/**
 * Validate that the API key is present and return full config.
 * Call this once at the start of any command that requires Brave API access.
 */
export function requireConfig() {
	return buildConfig(true);
}
