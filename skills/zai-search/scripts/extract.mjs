#!/usr/bin/env node

/**
 * Extract text content from URLs.
 * Note: Z.AI does not provide an extract API. This script uses native fetch
 * to retrieve pages and strips HTML tags for basic text extraction.
 * For richer extraction, consider using z.ai Web Search results (content field).
 */

function usage() {
  console.error(`Usage: extract.mjs "url1" ["url2" ...]`);
  process.exit(2);
}

const args = process.argv.slice(2);
if (args.length === 0 || args[0] === "-h" || args[0] === "--help") usage();

const urls = args.filter(a => !a.startsWith("-"));

if (urls.length === 0) {
  console.error("No URLs provided");
  usage();
}

function stripHtml(html) {
  return html
    .replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, "")
    .replace(/<style\b[^<]*(?:(?!<\/style>)<[^<]*)*<\/style>/gi, "")
    .replace(/<[^>]+>/g, " ")
    .replace(/&nbsp;/g, " ")
    .replace(/&amp;/g, "&")
    .replace(/&lt;/g, "<")
    .replace(/&gt;/g, ">")
    .replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'")
    .replace(/\s+/g, " ")
    .trim();
}

async function fetchUrl(url) {
  const resp = await fetch(url, {
    headers: { "User-Agent": "Mozilla/5.0 (compatible; ZAI-Extract/1.0)" },
  });
  if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
  const html = await resp.text();
  return stripHtml(html);
}

for (const url of urls) {
  try {
    const content = await fetchUrl(url);
    console.log(`# ${url}\n`);
    console.log(content || "(no content extracted)");
    console.log("\n---\n");
  } catch (err) {
    console.log(`# ${url}\n`);
    console.log(`(failed: ${err.message})`);
    console.log("\n---\n");
  }
}
