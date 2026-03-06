#!/usr/bin/env bun
"use strict";

const fs = require("fs");
const path = require("path");
const { getSkillDir, getAgentsDir, getRegistryPath } = require("../lib/registry");
const { parseAgentFile } = require("../lib/parse");
const { track } = require("../lib/telemetry");

function walkDir(dir) {
  const results = [];
  if (!fs.existsSync(dir)) return results;
  const entries = fs.readdirSync(dir, { withFileTypes: true });
  for (const entry of entries) {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      results.push(...walkDir(full));
    } else if (entry.isFile() && entry.name.endsWith(".md")) {
      results.push(full);
    }
  }
  return results;
}

function scanAgents() {
  const agentsDir = getAgentsDir();
  if (!fs.existsSync(agentsDir)) {
    process.stderr.write(`Agents directory not found: ${agentsDir}\n`);
    return [];
  }

  const agents = [];
  for (const filepath of walkDir(agentsDir)) {
    const info = parseAgentFile(filepath);
    if (info) agents.push(info);
  }
  return agents;
}

function buildRegistry(agents) {
  const skillDir = getSkillDir();
  const agentsDir = getAgentsDir();

  const registry = {
    version: 1,
    generated_at: new Date().toISOString(),
    skill_dir: skillDir,
    agents: [],
    stats: {
      total_agents: agents.length,
      total_tokens: agents.reduce((sum, a) => sum + a.token_estimate, 0),
      tokens_saved_vs_preload: agents.reduce((sum, a) => sum + a.token_estimate, 0),
    },
  };

  for (const agent of agents) {
    let relPath;
    try {
      relPath = path.relative(agentsDir, agent.path);
      if (relPath === "" || relPath === "." || relPath === ".." || relPath.startsWith(".." + path.sep)) {
        relPath = agent.filename;
      }
    } catch {
      relPath = agent.filename;
    }

    registry.agents.push({
      name: agent.name,
      path: relPath,
      summary: agent.summary,
      keywords: agent.keywords,
      token_estimate: agent.token_estimate,
      content_hash: agent.content_hash,
    });
  }

  return registry;
}

function main() {
  console.log("Scanning agents directory...");

  const agents = scanAgents();
  if (agents.length === 0) {
    console.log("No agents found in agents/ directory.");
    console.log(`Add .md files to: ${getAgentsDir()}`);
    process.exit(1);
  }

  console.log(`Found ${agents.length} agent(s)`);

  const registry = buildRegistry(agents);

  const registryPath = getRegistryPath();
  const registryDir = path.dirname(registryPath);
  if (!fs.existsSync(registryDir)) fs.mkdirSync(registryDir, { recursive: true });

  fs.writeFileSync(registryPath, JSON.stringify(registry));

  track("rebuild", {
    scanned: agents.length,
    tokens: registry.stats.total_tokens,
  });

  console.log(`\n\u2713 Registry rebuilt: ${registryPath}`);
  console.log(`  Agents indexed: ${agents.length}`);
  console.log(`  Total tokens: ${registry.stats.total_tokens.toLocaleString()}`);

  const sorted = [...agents].sort((a, b) => a.name.localeCompare(b.name));
  for (const agent of sorted) {
    console.log(`    - ${agent.name} (${agent.token_estimate.toLocaleString()} tokens)`);
  }
}

main();
