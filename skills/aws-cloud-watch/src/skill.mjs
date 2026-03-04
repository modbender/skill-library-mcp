#!/usr/bin/env node
import { spawnSync } from "child_process";

const args = process.argv.slice(2);
const result = spawnSync("node", ["./src/cli.mjs", ...args], {
  stdio: "inherit",
  shell: process.platform === "win32",
});

process.exit(result.status ?? 0);
