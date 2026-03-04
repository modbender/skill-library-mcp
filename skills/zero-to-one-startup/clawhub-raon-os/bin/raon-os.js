#!/usr/bin/env node
/**
 * raon-os — bin entry point
 * Delegates to scripts/raon.sh (bash implementation)
 */
const { spawnSync } = require("child_process");
const path = require("path");

const sh = path.join(__dirname, "..", "scripts", "raon.sh");
const result = spawnSync(sh, process.argv.slice(2), {
  stdio: "inherit",
  shell: false,
});
process.exit(result.status ?? 1);
