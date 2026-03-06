#!/usr/bin/env node

import { spawnSync } from "node:child_process";
function usage() {
  console.error("Usage: notebooklm.mjs <command> [args...]");
  console.error("Examples:");
  console.error("  notebooklm.mjs status");
  console.error("  notebooklm.mjs login");
  console.error("  notebooklm.mjs list");
  console.error("  notebooklm.mjs ask \"Summarize this notebook\" --notebook <id>");
  console.error("  notebooklm.mjs source add https://example.com --notebook <id>");
  console.error("  notebooklm.mjs artifact list --notebook <id> --json");
  process.exit(2);
}

const args = process.argv.slice(2);
if (args.length === 0 || args[0] === "-h" || args[0] === "--help") usage();

const result = spawnSync("notebooklm", args, { stdio: "inherit" });

if (result.error) {
  console.error(`Failed to run notebooklm: ${result.error.message}`);
  process.exit(1);
}

process.exit(result.status ?? 1);
