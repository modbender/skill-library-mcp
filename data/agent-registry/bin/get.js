#!/usr/bin/env bun
"use strict";

const fs = require("fs");
const { loadRegistry, resolveRegistryAgentPath } = require("../lib/registry");
const { track } = require("../lib/telemetry");

function findAgent(registry, name) {
  const agents = registry.agents || [];
  const nameLower = name.toLowerCase();

  // Exact match first
  for (const agent of agents) {
    if (agent.name.toLowerCase() === nameLower) return agent;
  }

  // Partial match
  const matches = agents.filter((a) => a.name.toLowerCase().includes(nameLower));
  if (matches.length === 1) return matches[0];
  if (matches.length > 1) {
    process.stderr.write(`Multiple agents match '${name}':\n`);
    for (const m of matches) process.stderr.write(`  - ${m.name}\n`);
    process.stderr.write("\nPlease specify the exact name.\n");
    return null;
  }

  return null;
}

function loadAgentContent(agent) {
  const resolved = resolveRegistryAgentPath(agent.path);
  if (!resolved.ok) {
    process.stderr.write(`Error: ${resolved.error}\n`);
    return null;
  }

  if (!fs.existsSync(resolved.path)) {
    process.stderr.write(`Error: Agent file not found: ${agent.path}\n`);
    return null;
  }

  try {
    return fs.readFileSync(resolved.path, "utf8");
  } catch (e) {
    process.stderr.write(`Error reading agent file: ${e.message}\n`);
    return null;
  }
}

function formatAgentOutput(agent, content, raw) {
  if (raw) return content;
  const sep = "=".repeat(70);
  const tokens = agent.token_estimate || 0;
  return `${sep}\nAGENT: ${agent.name}\nTokens: ~${tokens.toLocaleString()}\n${sep}\n\n${content}\n\n${sep}\nEND OF AGENT INSTRUCTIONS\n${sep}`;
}

function formatJsonOutput(agent, content) {
  return JSON.stringify(
    {
      name: agent.name,
      summary: agent.summary || "",
      token_estimate: agent.token_estimate || 0,
      keywords: agent.keywords || [],
      content,
    },
    null,
    2
  );
}

function listAvailableAgents(registry) {
  const agents = registry.agents || [];
  if (agents.length === 0) return "No agents in registry.";

  const lines = ["Available agents:"];
  const sorted = [...agents].sort((a, b) => a.name.localeCompare(b.name));
  for (const agent of sorted) {
    const summary = (agent.summary || "").slice(0, 50) + "...";
    lines.push(`  - ${agent.name}: ${summary}`);
  }
  lines.push("");
  lines.push("Usage: bun bin/get.js <agent-name>");
  return lines.join("\n");
}

function main() {
  const args = process.argv.slice(2);

  let jsonOutput = false;
  let rawOutput = false;
  const remaining = [];

  for (const arg of args) {
    if (arg === "--json") jsonOutput = true;
    else if (arg === "--raw") rawOutput = true;
    else if (arg === "--help" || arg === "-h") {
      console.log("Usage: bun bin/get.js <agent-name> [OPTIONS]\n");
      console.log("Loads the full content of a specific agent.\n");
      console.log("Arguments:");
      console.log("  agent-name    Name of the agent to load (case-insensitive)\n");
      console.log("Options:");
      console.log("  --json        Output as JSON with metadata");
      console.log("  --raw         Output raw content without headers");
      console.log("  --help, -h    Show this help\n");
      console.log("Examples:");
      console.log("  bun bin/get.js code-reviewer");
      console.log("  bun bin/get.js security --json");
      return;
    } else remaining.push(arg);
  }

  const registry = loadRegistry();
  if (!registry) process.exit(1);

  if (remaining.length === 0) {
    console.log(listAvailableAgents(registry));
    process.exit(0);
  }

  const agentName = remaining.join(" ");
  const agent = findAgent(registry, agentName);
  if (!agent) {
    process.stderr.write(`Error: Agent '${agentName}' not found.\n\n`);
    process.stderr.write(listAvailableAgents(registry) + "\n");
    process.exit(1);
  }

  const content = loadAgentContent(agent);
  if (!content) process.exit(1);

  track("get", {
    found: true,
    tokens: agent.token_estimate || 0,
    fmt: jsonOutput ? "json" : rawOutput ? "raw" : "formatted",
  });

  if (jsonOutput) {
    console.log(formatJsonOutput(agent, content));
  } else {
    console.log(formatAgentOutput(agent, content, rawOutput));
  }
}

main();
