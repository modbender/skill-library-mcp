#!/usr/bin/env bun
"use strict";

const fs = require("fs");
const path = require("path");
const os = require("os");
const readline = require("readline");
const { getSkillDir, getAgentsDir, getRegistryPath } = require("../lib/registry");
const { parseAgentFile } = require("../lib/parse");
const { track } = require("../lib/telemetry");

// ANSI colors
const C = {
  header: "\x1b[95m",
  blue: "\x1b[94m",
  cyan: "\x1b[96m",
  green: "\x1b[92m",
  yellow: "\x1b[93m",
  red: "\x1b[91m",
  bold: "\x1b[1m",
  dim: "\x1b[2m",
  reset: "\x1b[0m",
};

function colorize(text, color) {
  return process.stdout.isTTY ? `${color}${text}${C.reset}` : text;
}

function parseOptions(argv) {
  const options = {
    mode: "copy",
    help: false,
  };

  for (const arg of argv) {
    if (arg === "--move") options.mode = "move";
    else if (arg === "--copy") options.mode = "copy";
    else if (arg === "--help" || arg === "-h") options.help = true;
    else {
      process.stderr.write(`Unknown option: ${arg}\n`);
      options.help = true;
      options.invalid = true;
    }
  }

  return options;
}

function printHelp() {
  console.log("Usage: bun bin/init.js [OPTIONS]\n");
  console.log("Interactive agent migration wizard.\n");
  console.log("Options:");
  console.log("  --copy        Copy selected agents into registry (default)");
  console.log("  --move        Move selected agents into registry (destructive)");
  console.log("  --help, -h    Show this help");
}

function walkDir(dir) {
  const results = [];
  if (!fs.existsSync(dir)) return results;
  const entries = fs.readdirSync(dir, { withFileTypes: true });
  for (const entry of entries) {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) results.push(...walkDir(full));
    else if (entry.isFile() && entry.name.endsWith(".md")) results.push(full);
  }
  return results;
}

function findAgentLocations() {
  const locations = [];
  const home = os.homedir();
  const globalAgents = path.join(home, ".claude", "agents");
  if (fs.existsSync(globalAgents)) locations.push(globalAgents);

  const projectAgents = path.join(process.cwd(), ".claude", "agents");
  if (fs.existsSync(projectAgents) && projectAgents !== globalAgents) {
    locations.push(projectAgents);
  }
  return locations;
}

function scanAgents(directory) {
  const agents = [];
  for (const filepath of walkDir(directory)) {
    const info = parseAgentFile(filepath);
    if (info) {
      info.source_dir = directory;
      agents.push(info);
    }
  }
  return agents;
}

function scanExistingRegistry() {
  const agentsDir = getAgentsDir();
  if (!fs.existsSync(agentsDir)) return [];
  const agents = [];
  for (const filepath of walkDir(agentsDir)) {
    const info = parseAgentFile(filepath);
    if (info) {
      info.source_dir = agentsDir;
      agents.push(info);
    }
  }
  return agents;
}

function displayAgentList(agents, title) {
  console.log(colorize(`\n${title}`, C.header + C.bold));
  console.log("=".repeat(60));
  if (agents.length === 0) {
    console.log(colorize("  No agents found", C.dim));
    return;
  }
  for (let i = 0; i < agents.length; i++) {
    const agent = agents[i];
    const tokens = agent.token_estimate;
    const tokenColor = tokens < 1000 ? C.green : tokens < 3000 ? C.yellow : C.red;
    console.log(`  [${i + 1}] ${colorize(agent.name, C.cyan)}`);
    const summary = agent.summary.length > 60 ? agent.summary.slice(0, 60) + "..." : agent.summary;
    console.log(`      ${colorize(summary, C.dim)}`);
    console.log(`      Tokens: ${colorize(String(tokens), tokenColor)} | Source: ${path.basename(agent.source_dir)}`);
    console.log();
  }
}

function getCategory(agent) {
  try {
    const agentPath = agent.path;
    const sourceDir = agent.source_dir || "";
    const relPath = path.relative(sourceDir, agentPath);
    const parts = relPath.split(path.sep);
    if (parts.length > 1) return parts[0].toUpperCase().replace(/-/g, " ");
  } catch {}
  return "ROOT";
}

// Try @clack/prompts for interactive TUI
async function interactiveSelectionClack(agents) {
  const clack = require("@clack/prompts");

  // Build grouped options
  const categories = {};
  for (const agent of agents) {
    const cat = getCategory(agent);
    if (!categories[cat]) categories[cat] = [];
    categories[cat].push(agent);
  }

  const groups = {};
  for (const cat of Object.keys(categories).sort()) {
    const items = categories[cat].sort((a, b) => a.name.localeCompare(b.name));
    groups[cat] = items.map((agent) => {
      const tokens = agent.token_estimate;
      const indicator = tokens < 1000 ? "\uD83D\uDFE2" : tokens < 3000 ? "\uD83D\uDFE1" : "\uD83D\uDD34";
      const summary = agent.summary.length > 50 ? agent.summary.slice(0, 50) + "..." : agent.summary;
      return {
        value: agent.name,
        label: `${agent.name} ${indicator} ${tokens}`,
        hint: summary,
      };
    });
  }

  const selected = await clack.groupMultiselect({
    message: "Select agents to add to registry",
    options: groups,
    required: false,
  });

  if (clack.isCancel(selected)) {
    console.log(colorize("\nMigration cancelled.", C.yellow));
    return [];
  }

  // Map selected names back to agent objects
  const selectedNames = new Set(selected);
  return agents.filter((a) => selectedNames.has(a.name));
}

// Fallback: readline-based selection
async function interactiveSelectionFallback(agents) {
  const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
  const ask = (q) => new Promise((resolve) => rl.question(q, resolve));

  console.log(colorize("\nSelect agents to add to the registry:", C.bold));
  console.log(colorize("  Enter numbers separated by commas (e.g., 1,3,5)", C.dim));
  console.log(colorize("  Enter 'all' to add all agents", C.dim));
  console.log(colorize("  Enter 'none' or press Enter to skip migration", C.dim));
  console.log();

  while (true) {
    const selection = (await ask(colorize("Your selection: ", C.cyan))).trim().toLowerCase();

    if (selection === "" || selection === "none") {
      rl.close();
      return [];
    }
    if (selection === "all") {
      rl.close();
      return agents;
    }

    try {
      const indices = selection.split(",").map((s) => parseInt(s.trim(), 10));
      const selected = [];
      let invalid = false;
      for (const idx of indices) {
        if (idx >= 1 && idx <= agents.length) {
          selected.push(agents[idx - 1]);
        } else {
          console.log(colorize(`  Invalid index: ${idx}. Valid range: 1-${agents.length}`, C.red));
          invalid = true;
        }
      }
      if (!invalid && selected.length > 0) {
        rl.close();
        return selected;
      }
    } catch {
      console.log(colorize("  Invalid input. Please enter numbers separated by commas.", C.red));
    }
  }
}

async function interactiveSelection(agents) {
  if (agents.length === 0) return [];

  try {
    const clack = require("@clack/prompts");
    if (typeof clack.groupMultiselect !== "function") throw new Error("groupMultiselect not available");
    return await interactiveSelectionClack(agents);
  } catch {
    console.log(colorize("\nNote: Install @clack/prompts for a better interactive UI", C.yellow));
    return await interactiveSelectionFallback(agents);
  }
}

function migrateAgents(agents, targetDir, mode) {
  const migrated = [];
  const errors = [];
  if (!fs.existsSync(targetDir)) fs.mkdirSync(targetDir, { recursive: true });

  for (const agent of agents) {
    const source = agent.path;
    const target = path.join(targetDir, agent.filename);

    try {
      if (fs.existsSync(target)) {
        console.log(colorize(`  Skipping ${agent.name}: already exists in registry`, C.yellow));
        agent.path = target;
        migrated.push(agent);
        continue;
      }

      if (mode === "move") {
        fs.renameSync(source, target);
      } else {
        fs.copyFileSync(source, target);
      }

      agent.path = target;
      migrated.push(agent);
      const action = mode === "move" ? "Moved" : "Copied";
      console.log(colorize(`  \u2713 ${action}: ${agent.name}`, C.green));
    } catch (e) {
      if (mode === "move") {
        // renameSync fails across devices; fall back to copy+delete
        try {
          fs.copyFileSync(source, target);
          fs.unlinkSync(source);
          agent.path = target;
          migrated.push(agent);
          console.log(colorize(`  \u2713 Moved: ${agent.name}`, C.green));
          continue;
        } catch (e2) {
          errors.push(`${agent.name}: ${e2.message}`);
          console.log(colorize(`  \u2717 Failed: ${agent.name} - ${e2.message}`, C.red));
          continue;
        }
      }

      errors.push(`${agent.name}: ${e.message}`);
      console.log(colorize(`  \u2717 Failed: ${agent.name} - ${e.message}`, C.red));
    }
  }

  return { migrated, errors };
}

function buildRegistry(agents, registryPath) {
  const agentsDir = getAgentsDir();
  const dir = path.dirname(registryPath);
  if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });

  const totalTokens = agents.reduce((sum, a) => sum + a.token_estimate, 0);

  const registry = {
    version: 1,
    generated_at: new Date().toISOString(),
    skill_dir: getSkillDir(),
    agents: [],
    stats: {
      total_agents: agents.length,
      total_tokens: totalTokens,
      tokens_saved_vs_preload: totalTokens,
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

  fs.writeFileSync(registryPath, JSON.stringify(registry));

  console.log(colorize(`\n\u2713 Registry built: ${registryPath}`, C.green));
  console.log(`  Agents indexed: ${agents.length}`);
  console.log(`  Total tokens available: ${totalTokens.toLocaleString()}`);
  console.log(colorize(`  Tokens saved by lazy loading: ~${totalTokens.toLocaleString()}`, C.green + C.bold));
}

async function main() {
  const options = parseOptions(process.argv.slice(2));
  if (options.help) {
    printHelp();
    process.exit(options.invalid ? 1 : 0);
  }

  console.log(colorize("\n\u2554\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2557", C.header));
  console.log(colorize("\u2551          Agent Registry Initialization                   \u2551", C.header));
  console.log(colorize("\u2551  Reduce token overhead by lazy-loading agents            \u2551", C.header));
  console.log(colorize("\u255a\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u255d", C.header));
  console.log(colorize(`Mode: ${options.mode === "move" ? "move (destructive)" : "copy (non-destructive)"}`, C.cyan));

  // Find agent locations
  const locations = findAgentLocations();

  if (locations.length === 0) {
    console.log(colorize("\nNo agent directories found at:", C.yellow));
    console.log("  - ~/.claude/agents/");
    console.log("  - .claude/agents/");

    const existing = scanExistingRegistry();
    if (existing.length > 0) {
      console.log(colorize(`\nFound ${existing.length} agents already in registry.`, C.cyan));
      console.log("Rebuilding registry index...");
      buildRegistry(existing, getRegistryPath());
      return;
    }

    console.log("\nCreate agent files in these directories, then run this script again.");
    return;
  }

  // Scan all locations
  const allAgents = [];
  for (const loc of locations) {
    console.log(colorize(`\nScanning: ${loc}`, C.blue));
    const agents = scanAgents(loc);
    allAgents.push(...agents);
    console.log(`  Found ${agents.length} agent(s)`);
  }

  // Scan existing registry agents
  const existingRegistryAgents = scanExistingRegistry();
  const existingNames = new Set(existingRegistryAgents.map((a) => a.name));

  // Filter out agents already in registry
  const newAgents = allAgents.filter((a) => !existingNames.has(a.name));

  if (existingRegistryAgents.length > 0) {
    console.log(colorize(`\nAlready in registry: ${existingRegistryAgents.length} agent(s)`, C.cyan));
  }

  if (newAgents.length === 0 && existingRegistryAgents.length === 0) {
    console.log(colorize("\nNo agents found to migrate.", C.yellow));
    return;
  }

  let allRegistryAgents;
  let selectedCount = 0;

  if (newAgents.length > 0) {
    displayAgentList(newAgents, "Available Agents to Add");

    const selected = await interactiveSelection(newAgents);
    selectedCount = selected.length;

    if (selected.length > 0) {
      const action = options.mode === "move" ? "Moving" : "Copying";
      console.log(colorize(`\n${action} ${selected.length} agent(s)...`, C.blue));
      const { migrated, errors } = migrateAgents(selected, getAgentsDir(), options.mode);

      if (errors.length > 0) {
        console.log(colorize(`\nEncountered ${errors.length} error(s):`, C.red));
        for (const err of errors) console.log(`  - ${err}`);
      }

      allRegistryAgents = [...existingRegistryAgents, ...migrated];
    } else {
      console.log(colorize("\nNo agents selected for migration.", C.yellow));
      allRegistryAgents = existingRegistryAgents;
    }
  } else {
    console.log(colorize("\nNo new agents to migrate.", C.cyan));
    allRegistryAgents = existingRegistryAgents;
  }

  if (allRegistryAgents.length > 0) {
    console.log(colorize("\nBuilding registry index...", C.blue));
    buildRegistry(allRegistryAgents, getRegistryPath());

    const totalTokens = allRegistryAgents.reduce((sum, a) => sum + (a.token_estimate || 0), 0);
    track("init", {
      selected: selectedCount,
      available: newAgents.length,
      total: allRegistryAgents.length,
      tokens_saved: totalTokens,
    });

    console.log(colorize("\n\u2713 Setup complete!", C.green + C.bold));
    console.log("\nNext steps:");
    console.log("  1. The skill is ready to use");
    console.log("  2. Claude will now search agents on-demand instead of loading all upfront");
    console.log("  3. Run 'bun bin/list.js' to see indexed agents");
    console.log("  4. Run 'bun bin/search.js <query>' to search");
  } else {
    console.log(colorize("\nNo agents in registry. Run this script again after adding agents.", C.yellow));
  }
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
