#!/usr/bin/env node
/**
 * @file content.js
 * @author kelexine <https://github.com/kelexine>
 * @description CLI tool to extract readable Markdown content from a webpage.
 *              Validates the URL, retries on transient failures, and exits with
 *              meaningful status codes for use in scripts and pipelines.
 */
import { parseArgs } from "node:util";
import process       from "node:process";
import { config }    from "./config.js";
import { ValidationError } from "./errors.js";
import { logger }          from "./logger.js";
import { fetchPageContent } from "./content-fetcher.js";
import { parseURL }         from "./utils.js";

// ── Argument parsing ─────────────────────────────────────────────────────────

const CLI_OPTIONS = {
	json: { type: "boolean", short: "j", default: false },
	help: { type: "boolean", short: "h", default: false },
	"max-length": { type: "string", default: String(config.MAX_CONTENT_LENGTH) },
};

let args;
try {
	args = parseArgs({ args: process.argv.slice(2), options: CLI_OPTIONS, allowPositionals: true });
} catch (e) {
	console.error(`Argument error: ${e.message}`);
	process.exit(1);
}

if (args.values.help) {
	console.log(`
Usage: content.js <url> [options]

Options:
  -j, --json          Output result as JSON (includes title, url, method)
  --max-length <n>    Max characters of extracted content (default: ${config.MAX_CONTENT_LENGTH})
  -h, --help          Show this help message

Exit codes:
  0  — Content extracted successfully
  1  — Unrecoverable error (bad URL, config issue)
  2  — Content could not be extracted from this page
  130 — Interrupted (SIGINT)

Examples:
  content.js https://example.com/article
  content.js https://docs.nodejs.org/en/learn/asynchronous-work/event-loop-timers-and-nexttick --json
`);
	process.exit(0);
}

const rawUrl = args.positionals[0];

// ── Validate URL ──────────────────────────────────────────────────────────────

if (!rawUrl) {
	console.error("Error: A URL is required.");
	console.error("Usage: content.js <url> [--json] [--max-length <n>]");
	process.exit(1);
}

const { valid, error: urlError } = parseURL(rawUrl);
if (!valid) {
	console.error(`Error: ${urlError}`);
	process.exit(1);
}

const maxLength = parseInt(args.values["max-length"], 10);
if (isNaN(maxLength) || maxLength < 100) {
	console.error("Error: --max-length must be an integer >= 100.");
	process.exit(1);
}

// ── Main ──────────────────────────────────────────────────────────────────────

process.on("SIGINT",  () => { logger.info("Interrupted"); process.exit(130); });
process.on("SIGTERM", () => { logger.info("Terminated");  process.exit(143); });

logger.info("Fetching content", { url: rawUrl });

try {
	const result = await fetchPageContent(rawUrl, { maxLength, retry: true });

	if (!result) {
		console.error("Error: Could not extract readable content from this page.");
		console.error("The page may require JavaScript, be behind a login, or contain no parseable text.");
		process.exit(2);
	}

	if (args.values.json) {
		console.log(JSON.stringify({
			title:   result.title,
			url:     result.url,
			method:  result.method,
			content: result.content,
		}, null, 2));
	} else {
		if (result.title) {
			console.log(`# ${result.title}\n`);
		}
		console.log(result.content);
	}

	process.exit(0);

} catch (err) {
	if (err instanceof ValidationError) {
		console.error(err.message);
		process.exit(1);
	}
	logger.error("Unhandled error", { error: err.message, code: err.code });
	console.error(`Error: ${err.message}`);
	process.exit(1);
}
