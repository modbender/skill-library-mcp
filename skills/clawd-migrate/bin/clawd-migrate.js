#!/usr/bin/env node
"use strict";

const path = require("path");
const { spawnSync } = require("child_process");

const libDir = path.join(__dirname, "..", "lib");
const env = { ...process.env, PYTHONPATH: libDir };

const candidates = process.platform === "win32" ? ["python"] : ["python3", "python"];
let result;
for (const python of candidates) {
  result = spawnSync(
    python,
    ["-m", "clawd_migrate", ...process.argv.slice(2)],
    { stdio: "inherit", env, shell: process.platform === "win32" }
  );
  if (result.error && result.error.code === "ENOENT") continue;
  break;
}

if (result.status === null && result.error) {
  console.error("clawd-migrate: Python not found. Install Python 3 and ensure it is on PATH.");
  process.exit(1);
}
process.exit(result.status != null ? result.status : 1);
