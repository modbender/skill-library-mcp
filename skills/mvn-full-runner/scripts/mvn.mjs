#!/usr/bin/env node
import { spawn } from "node:child_process";
import { existsSync, statSync } from "node:fs";
import path from "node:path";

const args = process.argv.slice(2);

function printUsage() {
  console.error(
    "Usage: node mvn.mjs [--dir <path>] [--] <any maven args>\n" +
      "Example: node mvn.mjs --dir /repo -- clean test -DskipTests\n" +
      "Example: node mvn.mjs -- -v\n" +
      "Note: Only --dir is consumed by this wrapper. Everything else is passed to mvn as-is.",
  );
}

if (args.includes("--help") || args.includes("-h") || args.includes("--help-skill")) {
  printUsage();
  process.exit(0);
}

let dir = process.cwd();
const mvnArgs = [];

for (let i = 0; i < args.length; i += 1) {
  const token = args[i];
  if (token === "--") {
    mvnArgs.push(...args.slice(i + 1));
    break;
  }
  if (token === "--dir") {
    const value = args[i + 1];
    if (!value || value.startsWith("--")) {
      console.error("Missing value for --dir");
      printUsage();
      process.exit(1);
    }
    dir = value;
    i += 1;
    continue;
  }
  mvnArgs.push(token);
}

if (mvnArgs.length === 0) {
  console.error("No Maven arguments provided.");
  printUsage();
  process.exit(1);
}

const absDir = path.resolve(dir);
if (!existsSync(absDir) || !statSync(absDir).isDirectory()) {
  console.error(`Directory not found: ${absDir}`);
  process.exit(1);
}

console.log(`[mvn-skill] Running: mvn ${mvnArgs.join(" ")} (cwd=${absDir})`);

const child = spawn("mvn", mvnArgs, {
  cwd: absDir,
  stdio: "inherit",
  shell: false,
});

child.on("error", (err) => {
  console.error(`[mvn-skill] Failed to start mvn: ${err.message}`);
  process.exit(1);
});

child.on("exit", (code) => {
  process.exit(code ?? 1);
});
