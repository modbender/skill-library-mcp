#!/usr/bin/env bun
"use strict";

const { loadRegistry } = require("../lib/registry");
const { searchAgents } = require("../lib/search");
const { track } = require("../lib/telemetry");

function formatResults(results, query) {
  if (results.length === 0) {
    return `No agents found matching: '${query}'\n\nTry broader search terms or run 'bun bin/list.js' to see all agents.`;
  }

  const lines = [`Found ${results.length} matching agent(s) for: '${query}'\n`];

  for (let i = 0; i < results.length; i++) {
    const r = results[i];
    const filled = Math.floor(r.score * 10);
    const scoreBar = "\u2588".repeat(filled) + "\u2591".repeat(10 - filled);
    lines.push(
      `${i + 1}. ${r.name} (score: ${r.score.toFixed(2)}) [${scoreBar}]`
    );
    const summary = r.summary.length > 80 ? r.summary.slice(0, 80) + "..." : r.summary;
    lines.push(`   ${summary}`);
    lines.push(
      `   Tokens: ~${r.token_estimate.toLocaleString()} | Keywords: ${r.keywords.slice(0, 5).join(", ")}`
    );
    lines.push("");
  }

  lines.push("To load an agent: bun bin/get.js <agent-name>");
  return lines.join("\n");
}

function main() {
  const rawArgs = process.argv.slice(2);

  if (rawArgs.length === 0) {
    console.log("Usage: bun bin/search.js <query> [--json] [--top N]\n");
    console.log("Examples:");
    console.log('  bun bin/search.js "code review security"');
    console.log('  bun bin/search.js "docker kubernetes" --top 3');
    console.log('  bun bin/search.js "python testing" --json');
    process.exit(1);
  }

  let jsonOutput = false;
  let topK = 5;
  const queryParts = [];

  for (let i = 0; i < rawArgs.length; i++) {
    if (rawArgs[i] === "--json") {
      jsonOutput = true;
    } else if (rawArgs[i] === "--top" && i + 1 < rawArgs.length) {
      const n = parseInt(rawArgs[i + 1], 10);
      if (!isNaN(n)) topK = n;
      i++;
    } else {
      queryParts.push(rawArgs[i]);
    }
  }

  const query = queryParts.join(" ");

  const registry = loadRegistry();
  if (!registry) process.exit(1);

  const start = Date.now();
  const results = searchAgents(query, registry, topK);
  const elapsedMs = Date.now() - start;

  const topScore = results.length > 0 ? results[0].score : 0;
  track("search", {
    n: results.length,
    score: Math.round(topScore * 100) / 100,
    ms: elapsedMs,
    fmt: jsonOutput ? "json" : "table",
  });

  if (jsonOutput) {
    console.log(JSON.stringify(results, null, 2));
  } else {
    console.log(formatResults(results, query));
  }
}

main();
