#!/usr/bin/env node

// web-search-pro: Unified multi-engine search with full parameter support
// Engines: Tavily, Exa, Serper, SerpAPI
// Priority: Tavily > Exa > Serper > SerpAPI (auto-select based on query + available keys)

import * as tavily from "./engines/tavily.mjs";
import * as exa from "./engines/exa.mjs";
import * as serper from "./engines/serper.mjs";
import * as serpapi from "./engines/serpapi.mjs";

const ENGINES = { tavily, exa, serper, serpapi };
const ENGINE_LIST = [tavily, exa, serper, serpapi]; // priority order

function usage() {
  console.error(`web-search-pro — Multi-engine AI search with full parameter control

Usage:
  search.mjs "query" [options]

Options:
  --engine <name>           Force engine: tavily|exa|serper|serpapi (default: auto)
  -n <count>                Number of results (default: 5)
  --deep                    Deep/advanced search mode
  --news                    News search mode
  --days <n>                Limit news to last N days (Tavily only)
  --include-domains <d,...> Only search these domains (comma-separated)
  --exclude-domains <d,...> Exclude these domains (comma-separated)
  --time-range <range>      Time filter: day|week|month|year
  --from <YYYY-MM-DD>       Results published after this date
  --to <YYYY-MM-DD>         Results published before this date
  --search-engine <name>    SerpAPI sub-engine: google|bing|baidu|yandex|duckduckgo
  --country <code>          Country code (e.g., us, cn, de)
  --lang <code>             Language code (e.g., en, zh, de)
  --json                    Output raw JSON instead of Markdown

Environment variables (configure at least one):
  TAVILY_API_KEY            Tavily API key (recommended, AI-optimized)
  EXA_API_KEY               Exa API key (semantic search)
  SERPER_API_KEY             Serper API key (Google SERP)
  SERPAPI_API_KEY             SerpAPI key (multi-engine)`);
  process.exit(2);
}

// Parse arguments
const args = process.argv.slice(2);
if (args.length === 0 || args[0] === "-h" || args[0] === "--help") usage();

const query = args[0];
const opts = {
  engine: null,
  count: 5,
  deep: false,
  news: false,
  days: null,
  includeDomains: null,
  excludeDomains: null,
  timeRange: null,
  fromDate: null,
  toDate: null,
  searchEngine: null,
  country: null,
  lang: null,
  json: false,
};

for (let i = 1; i < args.length; i++) {
  const a = args[i];
  switch (a) {
    case "--engine": opts.engine = args[++i]; break;
    case "-n": opts.count = parseInt(args[++i], 10); break;
    case "--deep": opts.deep = true; break;
    case "--news": opts.news = true; break;
    case "--days": opts.days = parseInt(args[++i], 10); break;
    case "--include-domains": opts.includeDomains = args[++i].split(",").map(s => s.trim()); break;
    case "--exclude-domains": opts.excludeDomains = args[++i].split(",").map(s => s.trim()); break;
    case "--time-range": opts.timeRange = args[++i]; break;
    case "--from": opts.fromDate = args[++i]; break;
    case "--to": opts.toDate = args[++i]; break;
    case "--search-engine": opts.searchEngine = args[++i]; break;
    case "--country": opts.country = args[++i]; break;
    case "--lang": opts.lang = args[++i]; break;
    case "--json": opts.json = true; break;
    default:
      console.error(`Unknown option: ${a}`);
      usage();
  }
}

// Engine selection logic
function selectEngine(opts) {
  // Explicit engine choice
  if (opts.engine) {
    const eng = ENGINES[opts.engine];
    if (!eng) {
      console.error(`Unknown engine: ${opts.engine}. Available: ${Object.keys(ENGINES).join(", ")}`);
      process.exit(1);
    }
    if (!eng.isAvailable()) {
      console.error(`Engine ${opts.engine} selected but API key not configured.`);
      process.exit(1);
    }
    return eng;
  }

  // SerpAPI sub-engine requested → force SerpAPI
  if (opts.searchEngine && opts.searchEngine !== "google") {
    if (serpapi.isAvailable()) return serpapi;
    console.error(`--search-engine ${opts.searchEngine} requires SERPAPI_API_KEY`);
    process.exit(1);
  }

  // News search → prefer Serper (Google News best coverage), then Tavily
  if (opts.news) {
    if (serper.isAvailable()) return serper;
    if (tavily.isAvailable()) return tavily;
  }

  // Deep search → prefer Tavily advanced, then Exa deep
  if (opts.deep) {
    if (tavily.isAvailable()) return tavily;
    if (exa.isAvailable()) return exa;
  }

  // Domain filtering → prefer Tavily/Exa (native support), then Serper/SerpAPI (query hack)
  if (opts.includeDomains?.length || opts.excludeDomains?.length) {
    if (tavily.isAvailable()) return tavily;
    if (exa.isAvailable()) return exa;
  }

  // Default priority: Tavily > Exa > Serper > SerpAPI
  for (const eng of ENGINE_LIST) {
    if (eng.isAvailable()) return eng;
  }

  console.error("No search engine configured. Set at least one API key:");
  console.error("  TAVILY_API_KEY, EXA_API_KEY, SERPER_API_KEY, or SERPAPI_API_KEY");
  process.exit(1);
}

// Format output
function formatMarkdown(result, query) {
  const lines = [];
  lines.push(`## Search: ${query}`);
  lines.push(`**Engine**: ${result.engine}\n`);

  if (result.answer) {
    lines.push(`### Answer\n`);
    lines.push(result.answer);
    lines.push("\n---\n");
  }

  lines.push(`### Results (${result.results.length})\n`);
  for (const r of result.results) {
    const score = r.score ? ` (${(r.score * 100).toFixed(0)}%)` : "";
    const date = r.date ? ` [${r.date}]` : r.publishedDate ? ` [${r.publishedDate.slice(0, 10)}]` : "";
    lines.push(`- **${r.title}**${score}${date}`);
    lines.push(`  ${r.url}`);
    if (r.content) {
      lines.push(`  ${r.content.slice(0, 400)}${r.content.length > 400 ? "..." : ""}`);
    }
    lines.push("");
  }
  return lines.join("\n");
}

// Main
try {
  const engine = selectEngine(opts);
  const result = await engine.search(query, opts);

  if (opts.json) {
    console.log(JSON.stringify(result, null, 2));
  } else {
    console.log(formatMarkdown(result, query));
  }
} catch (err) {
  console.error(`Error: ${err.message}`);
  process.exit(1);
}
