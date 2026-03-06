/**
 * @file utils.js
 * @author kelexine <https://github.com/kelexine>
 * @description Shared utilities: HTML-to-Markdown conversion and smart content
 *              truncation that preserves paragraph boundaries.
 */
import TurndownService from "turndown";
import { gfm } from "turndown-plugin-gfm";

let _td = null;

/**
 * Lazily initialize and return a configured TurndownService.
 * Shared instance — safe because Turndown has no mutable request state.
 */
function getTurndown() {
	if (_td) return _td;

	_td = new TurndownService({
		headingStyle:     "atx",
		codeBlockStyle:   "fenced",
		hr:               "---",
		bulletListMarker: "-",
	});

	_td.use(gfm);

	// Drop empty anchor tags produced by icon fonts / decorative links
	_td.addRule("removeEmptyAnchors", {
		filter:      (node) => node.nodeName === "A" && !node.textContent?.trim(),
		replacement: () => "",
	});

	// Collapse data-URI images — they bloat output and carry no textual value
	_td.addRule("removeDataUriImages", {
		filter: (node) =>
			node.nodeName === "IMG" &&
			(node.getAttribute("src") ?? "").startsWith("data:"),
		replacement: () => "",
	});

	return _td;
}

/**
 * Convert an HTML fragment to GitHub-Flavored Markdown.
 * @param {string} html
 * @returns {string}
 */
export function htmlToMarkdown(html) {
	if (!html?.trim()) return "";

	return getTurndown()
		.turndown(html)
		// Remove orphaned empty markdown links left by icon or image-only anchors
		.replace(/\[\\?\[\s*\\?\]\]\([^)]*\)/g, "")
		// Collapse 3+ blank lines to 2
		.replace(/\n{3,}/g, "\n\n")
		.trim();
}

/**
 * Truncate `text` to at most `maxChars` characters, snapping to the nearest
 * paragraph boundary. Appends a truncation indicator when cut.
 *
 * Strategy (in order of preference):
 *   1. If text fits, return as-is.
 *   2. Snap to last double-newline (paragraph break) within the window.
 *   3. Snap to last sentence-ending punctuation (.!?) followed by whitespace.
 *   4. Snap to last word boundary.
 *   5. Hard-cut at maxChars.
 *
 * @param {string} text
 * @param {number} maxChars
 * @returns {string}
 */
export function smartTruncate(text, maxChars) {
	if (!text || text.length <= maxChars) return text;

	const window = text.slice(0, maxChars);
	const minCut = Math.floor(maxChars * 0.5); // Never cut below 50% of budget

	// 1. Paragraph boundary
	const paraBreak = window.lastIndexOf("\n\n");
	if (paraBreak >= minCut) {
		return window.slice(0, paraBreak).trimEnd() + "\n\n\u2026"; // …
	}

	// 2. Sentence boundary — scan backwards
	for (let i = window.length - 1; i >= minCut; i--) {
		const ch   = window[i];
		const next = window[i + 1];
		if ((ch === "." || ch === "!" || ch === "?") && (!next || /\s/.test(next))) {
			return window.slice(0, i + 1).trimEnd() + " \u2026";
		}
	}

	// 3. Word boundary
	const lastSpace = window.lastIndexOf(" ");
	if (lastSpace >= minCut) {
		return window.slice(0, lastSpace).trimEnd() + " \u2026";
	}

	// 4. Hard cut
	return window.trimEnd() + " \u2026";
}

/**
 * Strip HTML tags and decode common HTML entities from a string.
 * Used to sanitize Brave API snippets/titles which contain inline markup
 * (e.g. <strong> for query-match highlighting) and encoded characters.
 *
 * @param {string} html
 * @returns {string}
 */
export function stripHtml(html) {
	if (!html) return "";
	return html
		.replace(/<[^>]+>/g, "")           // Remove all HTML tags
		.replace(/&amp;/g,   "&")
		.replace(/&lt;/g,    "<")
		.replace(/&gt;/g,    ">")
		.replace(/&quot;/g,  '"')
		.replace(/&#39;/g,   "'")
		.replace(/&nbsp;/g,  " ")
		.replace(/&#(\d+);/g, (_, code) => String.fromCharCode(Number(code)))
		.replace(/\s+/g, " ")
		.trim();
}

/**
 * Validate that a string is a fully-qualified HTTP/HTTPS URL.
 * @param {string} input
 * @returns {{ valid: boolean; url?: URL; error?: string }}
 */
export function parseURL(input) {
	if (!input?.trim()) {
		return { valid: false, error: "URL must not be empty" };
	}
	try {
		const url = new URL(input);
		if (url.protocol !== "http:" && url.protocol !== "https:") {
			return { valid: false, error: `Unsupported protocol: "${url.protocol}". Only http and https are allowed.` };
		}
		return { valid: true, url };
	} catch {
		return { valid: false, error: `"${input}" is not a valid URL. Hint: include the scheme, e.g. https://example.com` };
	}
}