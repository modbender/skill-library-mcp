import { createRequire } from "module";
import { URL } from "url";
import fs from "fs";

const require = createRequire(import.meta.url);
const TurndownService = require("turndown");

const turndownService = new TurndownService();
const SENSITIVE_PARAM_HINTS = [
  "key",
  "token",
  "auth",
  "password",
  "secret",
  "access_token",
  "api_key",
];

function redactUrl(urlStr) {
  if (!urlStr || typeof urlStr !== "string") return null;
  try {
    const url = new URL(urlStr);
    if (url.pathname && url.pathname !== "/") {
      url.pathname = "/[redacted-path]";
    }
    url.hash = "";
    const keys = Array.from(url.searchParams.keys());
    for (const key of keys) {
      const lower = key.toLowerCase();
      const value = SENSITIVE_PARAM_HINTS.some((k) => lower.includes(k))
        ? "[redacted]"
        : "[masked]";
      url.searchParams.set(key, value);
    }
    return url.toString();
  } catch {
    return "INVALID_URL";
  }
}

function parseContentSignal(headerValue) {
  const signal = { "ai-input": "unknown", search: "unknown", "ai-train": "unknown" };
  if (!headerValue || typeof headerValue !== "string") return signal;
  headerValue.split(",").forEach((part) => {
    const [key, value] = part.split("=").map((s) => s.trim().toLowerCase());
    if (key && value && Object.prototype.hasOwnProperty.call(signal, key)) {
      signal[key] = value;
    }
  });
  return signal;
}

function parseTokenEstimate(rawValue) {
  if (!rawValue) return null;
  const value = Number.parseInt(rawValue, 10);
  return Number.isFinite(value) ? value : null;
}

function getPolicyAction(signal) {
  const aiInput = signal["ai-input"];
  if (aiInput === "no") return "block_input";
  if (aiInput === "yes") return "allow_input";
  return "needs_review";
}

function normalizeFromWebFetch(text, contentType) {
  const ct = (contentType || "").toLowerCase();
  if (ct.includes("text/markdown")) {
    return { content: typeof text === "string" ? text : "", format: "markdown", fallbackUsed: false };
  }
  if (ct.includes("text/html")) {
    const html = typeof text === "string" ? text : "";
    return { content: turndownService.turndown(html), format: "html-fallback", fallbackUsed: true };
  }
  return { content: typeof text === "string" ? text : "", format: "text", fallbackUsed: false };
}

/**
 * Wrapper mode only: process existing web_fetch result.
 *
 * Input contract:
 * {
 *   "url": "...",
 *   "finalUrl": "...",
 *   "contentType": "text/markdown|text/html|...",
 *   "text": "...",
 *   "status": 200
 * }
 */
export function process_web_fetch_result({
  web_fetch_result,
  content_signal_header,
  markdown_tokens_header,
}) {
  if (!web_fetch_result || typeof web_fetch_result !== "object") {
    throw new Error("web_fetch_result is required and must be an object");
  }

  const contentType =
    typeof web_fetch_result.contentType === "string" ? web_fetch_result.contentType : "";
  const statusCode =
    Number.isFinite(web_fetch_result.status) ? Number(web_fetch_result.status) : null;
  const sourceUrl =
    typeof web_fetch_result.finalUrl === "string"
      ? web_fetch_result.finalUrl
      : typeof web_fetch_result.url === "string"
        ? web_fetch_result.url
        : null;
  const sourceText = typeof web_fetch_result.text === "string" ? web_fetch_result.text : "";

  const normalized = normalizeFromWebFetch(sourceText, contentType);
  const contentSignal = parseContentSignal(content_signal_header);
  const policyAction = getPolicyAction(contentSignal);
  const tokenEstimate = parseTokenEstimate(markdown_tokens_header);

  return {
    content: normalized.content,
    format: normalized.format,
    token_estimate: tokenEstimate,
    content_signal: contentSignal,
    policy_action: policyAction,
    source_url: redactUrl(sourceUrl),
    status_code: statusCode,
    fallback_used: normalized.fallbackUsed,
  };
}

function readJsonFromStdin() {
  const input = fs.readFileSync(0, "utf8").trim();
  if (!input) {
    throw new Error("stdin is empty");
  }
  return JSON.parse(input);
}

function parseArgs(argv) {
  const args = { input: null, contentSignal: null, markdownTokens: null };
  for (let i = 2; i < argv.length; i += 1) {
    const arg = argv[i];
    if (arg === "--input") {
      args.input = argv[i + 1] || null;
      i += 1;
    } else if (arg === "--content-signal") {
      args.contentSignal = argv[i + 1] || null;
      i += 1;
    } else if (arg === "--markdown-tokens") {
      args.markdownTokens = argv[i + 1] || null;
      i += 1;
    } else if (arg === "--help" || arg === "-h") {
      console.log(
        "Usage: node browser.js [--input web_fetch.json] [--content-signal \"ai-input=yes,...\"] [--markdown-tokens 123]\n" +
          "If --input is omitted, reads web_fetch JSON from stdin.",
      );
      process.exit(0);
    }
  }
  return args;
}

if (process.argv[1] === import.meta.url.replace("file://", "")) {
  try {
    const args = parseArgs(process.argv);
    const webFetchResult = args.input
      ? JSON.parse(fs.readFileSync(args.input, "utf8"))
      : readJsonFromStdin();
    const result = process_web_fetch_result({
      web_fetch_result: webFetchResult,
      content_signal_header: args.contentSignal,
      markdown_tokens_header: args.markdownTokens,
    });
    console.log(JSON.stringify(result, null, 2));
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    console.error(JSON.stringify({ error: message }, null, 2));
    process.exit(1);
  }
}
