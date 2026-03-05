#!/usr/bin/env node

function usage() {
  console.error(`Usage: extract.mjs "url1,url2,..." [optionsURLs (comma-separated, max 20)
  --query <text>    Rerank chunks by relevance
  --chunks <n>       Chunks per URL (1-5, requires query)
  --depth <mode>     Extract depth: basic or advanced (default: basic)
  --format <fmt>     Output format: markdown or text (default: markdown)
  --timeout <sec>    Max wait time (1-60 seconds)
  --json              Output raw JSON

Examples:
  extract.mjs "https://docs.python.org/3/tutorial/classes.html"
  extract.mjs "https://example.com/page1,https://example.com/page2"
  extract.mjs "https://example.com/docs" --query "authentication API"
  extract.mjs "https://app.example.com" --depth advanced --timeout 60`);
  process.exit(2);
}

const args = process.argv.slice(2);
if (args.length === 0 || args[0] === "-h" || args[0] === "--help") usage();

const urlsInput = args[0];
let query = null;
let chunksPerSource = 3;
let extractDepth = "basic";
let format = "markdown";
let timeout = null;
let outputJson = false;

for (let i = 1; i < args.length; i++) {
  const a = args[i];
  if (a === "--query") {
    query = args[i + 1];
    i++;
    continue;
  }
  if (a === "--chunks") {
    chunksPerSource = Number.parseInt(args[i + 1] ?? "3", 10);
    i++;
    continue;
  }
  if (a === "--depth") {
    extractDepth = args[i + 1] ?? "basic";
    i++;
    continue;
  }
  if (a === "--format") {
    format = args[i + 1] ?? "markdown";
    i++;
    continue;
  }
  if (a === "--timeout") {
    timeout = Number.parseFloat(args[i + 1]);
    i++;
    continue;
  }
  if (a === "--json") {
    outputJson = true;
    continue;
  }
  console.error(`Unknown arg: ${a}`);
  usage();
}

const urls = urlsInput.split(",").map(u => u.trim()).filter(Boolean);
if (urls.length === 0) {
  console.error("Error: No URLs provided");
  process.exit(1);
}
if (urls.length > 20) {
  console.error("Error: Max 20 URLs per request");
  process.exit(1);
}

const apiKey = (process.env.TAVILY_API_KEY ?? "").trim();
if (!apiKey) {
  console.error("Error: TAVILY_API_KEY not set");
  console.error("Get your API key at https://tavily.com");
  process.exit(1);
}

const body = {
  urls: urls,
  extract_depth: extractDepth,
  format: format,
};

if (query) body.query = query;
if (query && chunksPerSource) body.chunks_per_source = chunksPerSource;
if (timeout) body.timeout = timeout;

const resp = await fetch("https://api.tavily.com/extract", {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
    "Authorization": `Bearer ${apiKey}`,
  },
  body: JSON.stringify(body),
});

if (!resp.ok) {
  const text = await resp.text().catch(() => "");
  throw new Error(`Tavily Extract failed (${resp.status}): ${text}`);
}

const data = await resp.json();

if (outputJson) {
  console.log(JSON.stringify(data, null, 2));
  process.exit(0);
}

// Print results
const results = data.results ?? [];
console.log(`## Extracted Content (${results.length} URLs)\n`);

for (const r of results) {
  const url = String(r?.url ?? "").trim();
  const content = String(r?.raw_content ?? "").trim();

  if (!url) continue;

  console.log(`### ${url}\n`);
  if (content) {
    console.log(content);
  }
  console.log("\n---\n");
}

// Print failed results
const failed = data.failed_results ?? [];
if (failed.length > 0) {
  console.log(`## Failed (${failed.length})\n`);
  for (const f of failed) {
    console.log(`- ${f.url}: ${f.error ?? "Unknown error"}`);
  }
}

if (data.response_time) {
  console.log(`\nResponse time: ${data.response_time}s`);
}
