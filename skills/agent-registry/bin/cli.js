#!/usr/bin/env bun
"use strict";

/**
 * Agent Registry CLI Dispatcher
 *
 * Routes subcommands to the appropriate bin/ script.
 * Usage: agent-registry <command> [args...]
 */

const path = require("path");

const commands = {
  search: "search.js",
  "search-paged": "search-paged.js",
  get: "get.js",
  list: "list.js",
  rebuild: "rebuild.js",
  init: "init.js",
};

const command = process.argv[2];

if (!command || command === "--help" || command === "-h" || !commands[command]) {
  console.log("Agent Registry — Lazy-loading system for Claude Code agents\n");
  console.log("Usage: agent-registry <command> [args...]\n");
  console.log("Commands:");
  console.log("  search        Search agents by intent");
  console.log("  search-paged  Search with pagination for large registries");
  console.log("  get           Load a specific agent's full instructions");
  console.log("  list          List all indexed agents");
  console.log("  rebuild       Rebuild the registry index");
  console.log("  init          Interactive agent migration wizard (copy by default)");
  console.log("\nExamples:");
  console.log('  agent-registry search "code review security"');
  console.log("  agent-registry get code-reviewer");
  console.log("  agent-registry list --detailed");
  console.log("  agent-registry init --move");

  if (command && command !== "--help" && command !== "-h" && !commands[command]) {
    console.error(`\nUnknown command: ${command}`);
    process.exit(1);
  }
  process.exit(0);
}

// Rewrite process.argv so the subcommand sees itself as argv[1]
process.argv = [process.argv[0], ...process.argv.slice(2)];

require(path.join(__dirname, commands[command]));
