#!/usr/bin/env node

// web-search-pro extract: Extract readable content from URLs
// Supports: Tavily Extract, Exa livecrawl

import * as tavily from "./engines/tavily.mjs";
import * as exa from "./engines/exa.mjs";

function usage() {
  console.error(`web-search-pro extract — Extract readable content from URLs

Usage:
  extract.mjs "url1" ["url2" ...] [options]

Options:
  --engine <name>    Force engine: tavily|exa (default: auto)
  --json             Output raw JSON instead of Markdown

Environment variables (at least one):
  TAVILY_API_KEY     Tavily Extract API
  EXA_API_KEY        Exa contents API with livecrawl`);
  process.exit(2);
}

const args = process.argv.slice(2);
if (args.length === 0 || args[0] === "-h" || args[0] === "--help") usage();

let engineName = null;
let json = false;
const urls = [];

for (let i = 0; i < args.length; i++) {
  if (args[i] === "--engine") { engineName = args[++i]; continue; }
  if (args[i] === "--json") { json = true; continue; }
  if (!args[i].startsWith("-")) { urls.push(args[i]); continue; }
  console.error(`Unknown option: ${args[i]}`);
  usage();
}

if (urls.length === 0) {
  console.error("No URLs provided");
  usage();
}

const engines = [tavily, exa];

function selectEngine() {
  if (engineName) {
    const eng = engines.find((e) => e.name() === engineName);
    if (!eng) { console.error(`Unknown extract engine: ${engineName}`); process.exit(1); }
    if (!eng.isAvailable()) { console.error(`${engineName} API key not configured`); process.exit(1); }
    return eng;
  }
  // Prefer Tavily for extraction (purpose-built)
  for (const eng of engines) {
    if (eng.isAvailable()) return eng;
  }
  console.error("No extract engine available. Set TAVILY_API_KEY or EXA_API_KEY");
  process.exit(1);
}

try {
  const engine = selectEngine();
  const result = await engine.extract(urls);

  if (json) {
    console.log(JSON.stringify(result, null, 2));
  } else {
    for (const r of result.results) {
      console.log(`# ${r.url}\n`);
      console.log(r.content || "(no content extracted)");
      console.log("\n---\n");
    }
    if (result.failed?.length) {
      console.log("## Failed URLs\n");
      for (const f of result.failed) {
        console.log(`- ${f.url}: ${f.error}`);
      }
    }
  }
} catch (err) {
  console.error(`Error: ${err.message}`);
  process.exit(1);
}
