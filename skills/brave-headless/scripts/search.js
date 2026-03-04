#!/usr/bin/env node
/**
 * @file search.js
 * @author kelexine <https://github.com/kelexine>
 * @description CLI tool for Brave Search with parallel content extraction,
 *              retry, circuit breaker protection, and structured output.
 */
import { parseArgs }        from "node:util";
import process              from "node:process";
import { requireConfig }    from "./config.js";
import { APIError, RateLimitError, ValidationError } from "./errors.js";
import { logger }           from "./logger.js";
import { withRetry }        from "./retry.js";
import { CircuitBreaker }   from "./circuit-breaker.js";
import { ConcurrencyPool }  from "./concurrency.js";
import { fetchPageContent } from "./content-fetcher.js";
import { stripHtml }        from "./utils.js";

// ── Argument parsing ─────────────────────────────────────────────────────────

const CLI_OPTIONS = {
	content: { type: "boolean", short: "c", default: false },
	n:       { type: "string",  short: "n", default: "5"   },
	json:    { type: "boolean", short: "j", default: false  },
	help:    { type: "boolean", short: "h", default: false  },
};

let args;
try {
	args = parseArgs({ args: process.argv.slice(2), options: CLI_OPTIONS, allowPositionals: true });
} catch (e) {
	console.error(`Argument error: ${e.message}`);
	console.error('Run with --help for usage.');
	process.exit(1);
}

if (args.values.help) {
	console.log(`
Usage: search.js <query> [options]

Options:
  -n <num>         Number of results (1–20, default: 5)
  -c, --content    Fetch and include full page content as Markdown
  -j, --json       Output results as newline-delimited JSON
  -h, --help       Show this help message

Environment variables:
  BRAVE_API_KEY       (required) Brave Search API key
  LOG_LEVEL           debug | info | warn | error | silent  (default: info)
  LOG_JSON            true | false  (default: false)
  CONCURRENCY_LIMIT   Max parallel page fetches  (default: 3)
  FETCH_TIMEOUT_MS    Per-page fetch timeout in ms  (default: 15000)
  SEARCH_TIMEOUT_MS   Brave API timeout in ms  (default: 10000)
  MAX_CONTENT_LENGTH  Max chars of extracted content  (default: 5000)
  MAX_RETRY_ATTEMPTS  Retry attempts on transient errors  (default: 3)

Examples:
  search.js "OpenAI GPT-5 release"
  search.js "Node.js streams" -n 10 --content
  search.js "Rust async" -n 3 --content --json
`);
	process.exit(0);
}

const query = args.positionals.join(" ").trim();

if (!query) {
	console.error("Error: A search query is required.");
	console.error("Usage: search.js <query> [-n <num>] [-c] [-j]");
	process.exit(1);
}

const numResults = parseInt(args.values.n, 10);
if (isNaN(numResults) || numResults < 1 || numResults > 20) {
	console.error("Error: -n must be an integer between 1 and 20.");
	process.exit(1);
}

// ── Config & startup ─────────────────────────────────────────────────────────

let cfg;
try {
	cfg = requireConfig();
} catch (err) {
	if (err instanceof ValidationError) {
		console.error(err.message);
	} else {
		console.error(`Startup error: ${err.message}`);
	}
	process.exit(1);
}

const outputJson  = args.values.json;
const fetchContent = args.values.content;

// Circuit breaker shared for the lifetime of this process
const breaker = new CircuitBreaker({
	name:             "brave-api",
	threshold:        cfg.CB_FAILURE_THRESHOLD,
	resetTimeout:     cfg.CB_RESET_TIMEOUT_MS,
});

// ── Brave API call ────────────────────────────────────────────────────────────

/**
 * @param {string} searchQuery
 * @param {number} count
 * @returns {Promise<Array>}
 */
async function fetchBraveResults(searchQuery, count) {
	return withRetry(
		async () => breaker.call(async () => {
			const url = new URL("https://api.search.brave.com/res/v1/web/search");
			url.searchParams.set("q",     searchQuery);
			url.searchParams.set("count", String(Math.min(count, 20)));

			const response = await fetch(url.toString(), {
				headers: {
					"Accept":              "application/json",
					"Accept-Encoding":     "gzip",
					"X-Subscription-Token": cfg.BRAVE_API_KEY,
				},
				signal: AbortSignal.timeout(cfg.SEARCH_TIMEOUT_MS),
			});

			if (response.status === 429) {
				const retryAfter = parseInt(response.headers.get("Retry-After") ?? "0", 10) || null;
				throw new RateLimitError(retryAfter, { query: searchQuery });
			}

			if (!response.ok) {
				const body = await response.text().catch(() => "");
				throw new APIError(`Brave API error: ${body || response.statusText}`, response.status);
			}

			const data = await response.json();
			return data.web?.results ?? [];
		}),
		{
			attempts:  cfg.MAX_RETRY_ATTEMPTS,
			baseDelay: cfg.RETRY_BASE_DELAY_MS,
			maxDelay:  cfg.RETRY_MAX_DELAY_MS,
			context:   "brave-search",
		},
	);
}

// ── Output helpers ────────────────────────────────────────────────────────────

function printResult(result, index) {
	if (outputJson) {
		console.log(JSON.stringify(result));
		return;
	}

	console.log(`--- Result ${index + 1} ---`);
	console.log(`Title:   ${result.title}`);
	console.log(`URL:     ${result.url}`);
	console.log(`Snippet: ${result.snippet}`);

	if (result.content != null) {
		if (result.content) {
			console.log(`Content:\n${result.content}`);
		} else {
			console.log(`Content: [Could not extract readable content]`);
		}
	}

	console.log("");
}

// ── Main ──────────────────────────────────────────────────────────────────────

process.on("SIGINT",  () => { logger.info("Interrupted"); process.exit(130); });
process.on("SIGTERM", () => { logger.info("Terminated");  process.exit(143); });

try {
	logger.info("Searching", { query, n: numResults, content: fetchContent });

	const raw = await fetchBraveResults(query, numResults);

	if (raw.length === 0) {
		logger.warn("No results found", { query });
		process.exit(0);
	}

	logger.info(`Found ${raw.length} results`);

	// Build base result objects
	const results = raw.slice(0, numResults).map((r) => ({
		title:   stripHtml(r.title       ?? ""),
		url:     r.url                   ?? "",
		snippet: stripHtml(r.description ?? ""),
		...(fetchContent ? { content: null } : {}),
	}));

	// Fetch content in parallel with bounded concurrency
	if (fetchContent) {
		logger.info(`Fetching content for ${results.length} pages`, { concurrency: cfg.CONCURRENCY_LIMIT });

		const contentResults = await ConcurrencyPool.mapSettled(
			results,
			async (result) => fetchPageContent(result.url),
			cfg.CONCURRENCY_LIMIT,
		);

		contentResults.forEach((settled, i) => {
			if (settled.status === "fulfilled" && settled.value) {
				results[i].content = settled.value.content;
			} else {
				results[i].content = "";
			}
		});
	}

	results.forEach(printResult);

} catch (err) {
	if (err instanceof ValidationError) {
		console.error(err.message);
		process.exit(1);
	}
	logger.error("Search failed", { error: err.message, code: err.code });
	console.error(`Error: ${err.message}`);
	process.exit(1);
}