#!/usr/bin/env bun
"use strict";

const { loadRegistry } = require("../lib/registry");
const { track } = require("../lib/telemetry");

function formatTable(agents) {
  if (agents.length === 0) {
    return "No agents registered.\n\nRun 'bun bin/init.js' to set up the registry.";
  }

  const lines = [];
  lines.push(
    `${"Agent Name".padEnd(25)} ${"Tokens".padEnd(10)} Summary`
  );
  lines.push("-".repeat(80));

  let totalTokens = 0;
  const sorted = [...agents].sort((a, b) => a.name.localeCompare(b.name));
  for (const agent of sorted) {
    const name = agent.name.slice(0, 24);
    const tokens = agent.token_estimate || 0;
    totalTokens += tokens;
    let summary = (agent.summary || "").slice(0, 42);
    if ((agent.summary || "").length > 42) summary += "...";
    lines.push(
      `${name.padEnd(25)} ${tokens.toLocaleString().padEnd(10)} ${summary}`
    );
  }

  lines.push("-".repeat(80));
  lines.push(
    `Total: ${agents.length} agents, ${totalTokens.toLocaleString()} tokens (saved from preloading)`
  );

  return lines.join("\n");
}

function formatDetailed(agents) {
  if (agents.length === 0) return "No agents registered.";

  const lines = [];
  let totalTokens = 0;
  const sorted = [...agents].sort((a, b) => a.name.localeCompare(b.name));

  for (const agent of sorted) {
    const tokens = agent.token_estimate || 0;
    totalTokens += tokens;
    const dashLen = Math.max(2, 50 - agent.name.length);
    lines.push(`\u256d\u2500 ${agent.name} ${"\u2500".repeat(dashLen)}`);
    lines.push(`\u2502 Summary: ${agent.summary || "No description"}`);
    lines.push(`\u2502 Tokens:  ~${tokens.toLocaleString()}`);
    lines.push(
      `\u2502 Keywords: ${(agent.keywords || []).slice(0, 8).join(", ")}`
    );
    lines.push(`\u2502 Path:    ${agent.path || "unknown"}`);
    lines.push("\u2570" + "\u2500".repeat(55));
    lines.push("");
  }

  lines.push(
    `Total: ${agents.length} agents | ${totalTokens.toLocaleString()} tokens saved by lazy loading`
  );
  return lines.join("\n");
}

function formatJson(registry) {
  return JSON.stringify(
    {
      agents: registry.agents || [],
      stats: registry.stats || {},
      generated_at: registry.generated_at || "",
    },
    null,
    2
  );
}

function formatSimple(agents) {
  return [...agents]
    .sort((a, b) => a.name.localeCompare(b.name))
    .map((a) => a.name)
    .join("\n");
}

function main() {
  const args = process.argv.slice(2);

  let outputFormat = "table";
  for (const arg of args) {
    if (arg === "--json") outputFormat = "json";
    else if (arg === "--detailed" || arg === "-d") outputFormat = "detailed";
    else if (arg === "--simple" || arg === "-s") outputFormat = "simple";
    else if (arg === "--help" || arg === "-h") {
      console.log("Usage: bun bin/list.js [OPTIONS]\n");
      console.log("Options:");
      console.log("  --detailed, -d  Show full details for each agent");
      console.log("  --simple, -s    Show just agent names");
      console.log("  --json          Output as JSON");
      console.log("  --help, -h      Show this help");
      return;
    }
  }

  const registry = loadRegistry();
  if (!registry) process.exit(1);

  const agents = registry.agents || [];

  track("list", { count: agents.length, fmt: outputFormat });

  if (outputFormat === "json") console.log(formatJson(registry));
  else if (outputFormat === "detailed") console.log(formatDetailed(agents));
  else if (outputFormat === "simple") console.log(formatSimple(agents));
  else console.log(formatTable(agents));
}

main();
