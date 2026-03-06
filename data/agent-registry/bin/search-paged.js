#!/usr/bin/env bun
"use strict";

const { loadRegistry } = require("../lib/registry");
const { searchAgentsAll } = require("../lib/search");
const { track } = require("../lib/telemetry");

function paginateResults(results, opts) {
  const totalResults = results.length;
  const { page = 1, pageSize = 20, offset, limit } = opts;

  // Offset-based pagination takes precedence
  if (offset != null) {
    const startIdx = Math.max(0, offset);
    const endIdx = Math.min(totalResults, startIdx + (limit || pageSize));
    return {
      query: null,
      total_results: totalResults,
      offset: startIdx,
      limit: endIdx - startIdx,
      results: results.slice(startIdx, endIdx),
    };
  }

  // Page-based pagination
  const p = Math.max(1, page);
  const totalPages = pageSize > 0 ? Math.ceil(totalResults / pageSize) : 1;
  const startIdx = (p - 1) * pageSize;
  const endIdx = Math.min(totalResults, startIdx + pageSize);

  return {
    query: null,
    total_results: totalResults,
    page: p,
    page_size: pageSize,
    total_pages: totalPages,
    has_next: p < totalPages,
    has_prev: p > 1,
    results: results.slice(startIdx, endIdx),
  };
}

function formatResults(paginated, jsonOutput) {
  if (jsonOutput) return JSON.stringify(paginated, null, 2);

  const query = paginated.query || "N/A";
  const total = paginated.total_results;
  const results = paginated.results;

  if (total === 0) {
    return `No agents found matching: '${query}'\n\nTry broader search terms or run 'bun bin/list.js' to see all agents.`;
  }

  const lines = [];

  if (paginated.page != null) {
    lines.push(`Found ${total} matching agent(s) for: '${query}'`);
    lines.push(
      `Page ${paginated.page}/${paginated.total_pages} (${results.length} results on this page)`
    );
  } else {
    lines.push(`Found ${total} matching agent(s) for: '${query}'`);
    lines.push(
      `Showing results ${paginated.offset + 1}-${paginated.offset + results.length}`
    );
  }
  lines.push("");

  for (let i = 0; i < results.length; i++) {
    const r = results[i];
    const globalIdx =
      paginated.page != null
        ? (paginated.page - 1) * paginated.page_size + i + 1
        : paginated.offset + i + 1;

    const filled = Math.floor(r.score * 10);
    const scoreBar = "\u2588".repeat(filled) + "\u2591".repeat(10 - filled);
    lines.push(
      `${globalIdx}. ${r.name} (score: ${r.score.toFixed(2)}) [${scoreBar}]`
    );
    const summary =
      r.summary.length > 80 ? r.summary.slice(0, 80) + "..." : r.summary;
    lines.push(`   ${summary}`);
    lines.push(
      `   Tokens: ~${r.token_estimate.toLocaleString()} | Keywords: ${r.keywords.slice(0, 5).join(", ")}`
    );
    lines.push("");
  }

  if (paginated.page != null) {
    if (paginated.has_next)
      lines.push(`\u2192 Next page: --page ${paginated.page + 1}`);
    if (paginated.has_prev)
      lines.push(`\u2190 Previous page: --page ${paginated.page - 1}`);
  }

  lines.push("");
  lines.push("To load an agent: bun bin/get.js <agent-name>");
  return lines.join("\n");
}

function main() {
  const rawArgs = process.argv.slice(2);

  if (rawArgs.length === 0) {
    console.log(
      "Usage: bun bin/search-paged.js <query> [--page N] [--page-size N] [--offset N] [--limit N] [--json]\n"
    );
    console.log("Examples:");
    console.log(
      '  bun bin/search-paged.js "security" --page 1 --page-size 10'
    );
    console.log('  bun bin/search-paged.js "react" --offset 20 --limit 10');
    console.log('  bun bin/search-paged.js "backend" --json');
    process.exit(1);
  }

  let jsonOutput = false;
  let page = 1;
  let pageSize = 20;
  let offset = undefined;
  let limit = undefined;
  const queryParts = [];

  for (let i = 0; i < rawArgs.length; i++) {
    if (rawArgs[i] === "--json") {
      jsonOutput = true;
    } else if (rawArgs[i] === "--page" && i + 1 < rawArgs.length) {
      page = parseInt(rawArgs[++i], 10) || 1;
    } else if (rawArgs[i] === "--page-size" && i + 1 < rawArgs.length) {
      pageSize = parseInt(rawArgs[++i], 10) || 20;
    } else if (rawArgs[i] === "--offset" && i + 1 < rawArgs.length) {
      offset = parseInt(rawArgs[++i], 10) || 0;
    } else if (rawArgs[i] === "--limit" && i + 1 < rawArgs.length) {
      limit = parseInt(rawArgs[++i], 10) || undefined;
    } else {
      queryParts.push(rawArgs[i]);
    }
  }

  const query = queryParts.join(" ");

  const registry = loadRegistry();
  if (!registry) process.exit(1);

  const start = Date.now();
  const allResults = searchAgentsAll(query, registry);
  const elapsedMs = Date.now() - start;

  const paginated = paginateResults(allResults, { page, pageSize, offset, limit });
  paginated.query = query;

  track("search_paged", {
    n: allResults.length,
    page,
    size: pageSize,
    ms: elapsedMs,
  });

  console.log(formatResults(paginated, jsonOutput));
}

main();
