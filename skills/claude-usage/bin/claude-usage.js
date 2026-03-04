#!/usr/bin/env node
const { execFileSync } = require("child_process");
const { join } = require("path");

const script = join(__dirname, "..", "scripts", "claude-usage.py");
const args = process.argv.slice(2);

try {
  execFileSync("python3", [script, ...args], { stdio: "inherit" });
} catch (e) {
  process.exit(e.status || 1);
}
