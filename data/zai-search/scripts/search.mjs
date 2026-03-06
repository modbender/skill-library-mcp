#!/usr/bin/env node

function usage() {
  console.error(`Usage: search.mjs "query" [-n 10] [--domain example.com] [--recency oneDay|oneWeek|oneMonth|oneYear|noLimit]`);
  process.exit(2);
}

const args = process.argv.slice(2);
if (args.length === 0 || args[0] === "-h" || args[0] === "--help") usage();

const query = args[0];
let n = 10;
let domainFilter = null;
let recencyFilter = "noLimit";

for (let i = 1; i < args.length; i++) {
  const a = args[i];
  if (a === "-n") {
    n = Number.parseInt(args[i + 1] ?? "10", 10);
    i++;
    continue;
  }
  if (a === "--domain") {
    domainFilter = args[i + 1] ?? null;
    i++;
    continue;
  }
  if (a === "--recency") {
    const val = args[i + 1] ?? "noLimit";
    if (["oneDay", "oneWeek", "oneMonth", "oneYear", "noLimit"].includes(val)) {
      recencyFilter = val;
    }
    i++;
    continue;
  }
  if (a === "--days") {
    const days = Number.parseInt(args[i + 1] ?? "7", 10);
    if (days <= 1) recencyFilter = "oneDay";
    else if (days <= 7) recencyFilter = "oneWeek";
    else if (days <= 30) recencyFilter = "oneMonth";
    else if (days <= 365) recencyFilter = "oneYear";
    else recencyFilter = "noLimit";
    i++;
    continue;
  }
  console.error(`Unknown arg: ${a}`);
  usage();
}

const apiKey = (process.env.ZAI_API_KEY ?? process.env.Z_AI_API_KEY ?? "").trim();
if (!apiKey) {
  console.error("Missing ZAI_API_KEY (get one at https://chat.z.ai)");
  process.exit(1);
}

const body = {
  search_engine: "search-prime",
  search_query: query,
  count: Math.max(1, Math.min(n, 50)),
  search_recency_filter: recencyFilter,
};

if (domainFilter) {
  body.search_domain_filter = domainFilter.startsWith("www.") ? domainFilter : `www.${domainFilter}`;
}

const resp = await fetch("https://api.z.ai/api/paas/v4/web_search", {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
    "Authorization": `Bearer ${apiKey}`,
    "Accept-Language": "en-US,en",
  },
  body: JSON.stringify(body),
});

if (!resp.ok) {
  const text = await resp.text().catch(() => "");
  throw new Error(`Z.AI Web Search failed (${resp.status}): ${text}`);
}

const data = await resp.json();

const results = data.search_result ?? [];
console.log("## Sources\n");

for (const r of results) {
  const title = String(r?.title ?? "").trim();
  const url = String(r?.link ?? "").trim();
  const content = String(r?.content ?? "").trim();
  const media = String(r?.media ?? "").trim();
  const publishDate = String(r?.publish_date ?? "").trim();

  if (!title || !url) continue;

  const meta = [media, publishDate].filter(Boolean).join(" • ");
  console.log(`- **${title}**${meta ? ` (${meta})` : ""}`);
  console.log(`  ${url}`);
  if (content) {
    console.log(`  ${content.slice(0, 400)}${content.length > 400 ? "..." : ""}`);
  }
  console.log();
}
