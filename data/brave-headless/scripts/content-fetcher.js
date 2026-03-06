/**
 * @file content-fetcher.js
 * @author kelexine <https://github.com/kelexine>
 * @description Core page-fetch and content-extraction pipeline with retry,
 *              structured errors, validated URL handling, and smart truncation.
 */
import { Readability } from "@mozilla/readability";
import { JSDOM }       from "jsdom";
import { config }      from "./config.js";
import { NetworkError, ParseError } from "./errors.js";
import { logger as rootLogger }     from "./logger.js";
import { withRetry }                from "./retry.js";
import { htmlToMarkdown, smartTruncate, parseURL } from "./utils.js";

const log = rootLogger.child("fetcher");

/** HTML elements that are purely structural / navigation noise. */
const NOISE_SELECTORS = [
	"script", "style", "noscript", "template",
	"nav", "header", "footer", "aside", "iframe",
	"[role='banner']", "[role='navigation']", "[role='complementary']",
	".cookie-banner", "#cookie-notice", ".ad", ".advertisement",
].join(", ");

/** Selectors for primary content containers (precedence order). */
const CONTENT_SELECTORS = [
	"main",
	"article",
	"[role='main']",
	".post-content",
	".article-body",
	".entry-content",
	"#content",
	".content",
];

/**
 * @typedef {object} FetchResult
 * @property {string} content - Extracted Markdown text
 * @property {string} title   - Page title (may be empty)
 * @property {string} url     - Final (post-redirect) URL
 * @property {string} method  - Extraction method: "readability" | "fallback"
 */

/**
 * Fetch a URL and extract its readable content as Markdown.
 *
 * @param {string}  rawUrl              - Target URL (must be http/https)
 * @param {object}  [opts]
 * @param {number}  [opts.maxLength]    - Override MAX_CONTENT_LENGTH
 * @param {boolean} [opts.retry=true]   - Enable retry on transient failures
 * @returns {Promise<FetchResult | null>} null if extraction yields no content
 */
export async function fetchPageContent(rawUrl, { maxLength, retry = true } = {}) {
	const { valid, url, error } = parseURL(rawUrl);
	if (!valid) {
		log.warn("Skipping invalid URL", { url: rawUrl, reason: error });
		return null;
	}

	const maxLen = maxLength ?? config.MAX_CONTENT_LENGTH;
	const doFetch = () => _fetchAndExtract(url.toString(), maxLen);

	try {
		if (retry) {
			return await withRetry(doFetch, {
				attempts:  config.MAX_RETRY_ATTEMPTS,
				baseDelay: config.RETRY_BASE_DELAY_MS,
				maxDelay:  config.RETRY_MAX_DELAY_MS,
				context:   `fetch(${url.hostname})`,
			});
		}
		return await doFetch();
	} catch (err) {
		// Content fetching is best-effort in bulk scenarios — log but don't throw
		log.debug("Content fetch failed", { url: url.toString(), code: err.code, error: err.message });
		return null;
	}
}

/**
 * @param {string} url
 * @param {number} maxLen
 * @returns {Promise<FetchResult | null>}
 */
async function _fetchAndExtract(url, maxLen) {
	let html;
	let finalUrl = url;

	try {
		const response = await fetch(url, {
			headers: {
				"User-Agent": "Mozilla/5.0 (compatible; BraveSearchBot/2.0; +https://github.com/kelexine)",
				"Accept":          "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
				"Accept-Language": "en-US,en;q=0.9",
				"Accept-Encoding": "gzip, deflate, br",
			},
			signal: AbortSignal.timeout(config.FETCH_TIMEOUT_MS),
			redirect: "follow",
		});

		finalUrl = response.url ?? url;

		if (!response.ok) {
			throw new NetworkError(`HTTP ${response.status} ${response.statusText}`, {
				url,
				status: response.status,
			});
		}

		const contentType = response.headers.get("content-type") ?? "";
		if (!contentType.includes("html") && !contentType.includes("xml")) {
			log.debug("Skipping non-HTML response", { url, contentType });
			return null;
		}

		html = await response.text();
	} catch (err) {
		if (err.name === "TimeoutError" || err.name === "AbortError") {
			throw new NetworkError(`Request timed out after ${config.FETCH_TIMEOUT_MS}ms`, { url });
		}
		if (err instanceof NetworkError) throw err;
		throw new NetworkError(err.message, { url, cause: err.name });
	}

	return _extractContent(html, finalUrl, maxLen);
}

/**
 * Extract readable content from HTML, trying Readability first then DOM fallback.
 * @param {string} html
 * @param {string} url
 * @param {number} maxLen
 * @returns {FetchResult | null}
 */
function _extractContent(html, url, maxLen) {
	let dom;
	try {
		dom = new JSDOM(html, { url });
	} catch (err) {
		throw new ParseError(`Failed to parse HTML: ${err.message}`, { url });
	}

	const doc = dom.window.document;

	// ── Strategy 1: Mozilla Readability ──────────────────────────────────────
	try {
		const reader  = new Readability(doc.cloneNode(true));
		const article = reader.parse();

		if (article?.content?.trim()) {
			const markdown = htmlToMarkdown(article.content);
			if (markdown.length >= 100) {
				log.debug("Extracted via Readability", { url, chars: markdown.length });
				return {
					content: smartTruncate(markdown, maxLen),
					title:   article.title ?? "",
					url:     finalUrl(url),
					method:  "readability",
				};
			}
		}
	} catch (err) {
		log.debug("Readability failed, trying fallback", { url, error: err.message });
	}

	// ── Strategy 2: Targeted DOM extraction ──────────────────────────────────
	doc.querySelectorAll(NOISE_SELECTORS).forEach((el) => el.remove());

	let contentEl = null;
	for (const selector of CONTENT_SELECTORS) {
		contentEl = doc.querySelector(selector);
		if (contentEl) break;
	}

	const source = contentEl ?? doc.body;
	if (!source) return null;

	const markdown = htmlToMarkdown(source.innerHTML ?? "");

	if (markdown.length < 100) {
		log.debug("Insufficient content extracted", { url, chars: markdown.length });
		return null;
	}

	log.debug("Extracted via DOM fallback", { url, chars: markdown.length });
	return {
		content: smartTruncate(markdown, maxLen),
		title:   doc.title ?? "",
		url:     finalUrl(url),
		method:  "fallback",
	};
}

function finalUrl(url) {
	try { return new URL(url).toString(); }
	catch { return url; }
}
