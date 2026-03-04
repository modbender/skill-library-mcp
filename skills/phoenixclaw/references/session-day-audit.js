#!/usr/bin/env node

const fs = require("fs");
const os = require("os");
const path = require("path");

function parseArgs(argv) {
  const args = {
    day: null,
    tz: "Asia/Shanghai",
    verbose: false,
  };

  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i];
    if (arg === "--day" && i + 1 < argv.length) {
      args.day = argv[i + 1];
      i += 1;
      continue;
    }
    if (arg === "--tz" && i + 1 < argv.length) {
      args.tz = argv[i + 1];
      i += 1;
      continue;
    }
    if (arg === "--verbose") {
      args.verbose = true;
      continue;
    }
    if (arg === "--help" || arg === "-h") {
      printHelp();
      process.exit(0);
    }
  }

  if (!args.day) {
    args.day = formatDateInTz(new Date(), args.tz);
  }

  return args;
}

function printHelp() {
  console.log(`Session day audit for PhoenixClaw

Usage:
  node skills/phoenixclaw/references/session-day-audit.js [--day YYYY-MM-DD] [--tz Asia/Shanghai] [--verbose]

Examples:
  node skills/phoenixclaw/references/session-day-audit.js --day 2026-02-07 --tz Asia/Shanghai
  node skills/phoenixclaw/references/session-day-audit.js --verbose
`);
}

function formatDateInTz(date, tz) {
  const fmt = new Intl.DateTimeFormat("en-CA", {
    timeZone: tz,
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
  });
  const parts = fmt.formatToParts(date);
  const year = parts.find((p) => p.type === "year")?.value;
  const month = parts.find((p) => p.type === "month")?.value;
  const day = parts.find((p) => p.type === "day")?.value;
  if (!year || !month || !day) {
    throw new Error(`Unable to format date in timezone: ${tz}`);
  }
  return `${year}-${month}-${day}`;
}

function expandHome(inputPath) {
  if (!inputPath.startsWith("~/")) {
    return inputPath;
  }
  return path.join(os.homedir(), inputPath.slice(2));
}

function findJsonlFilesRecursive(dir) {
  const results = [];
  if (!fs.existsSync(dir)) return results;
  let entries;
  try {
    entries = fs.readdirSync(dir, { withFileTypes: true });
  } catch (e) {
    return results;
  }
  for (const entry of entries) {
    const fullPath = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      results.push(...findJsonlFilesRecursive(fullPath));
    } else if (entry.isFile() && entry.name.endsWith(".jsonl")) {
      results.push(fullPath);
    }
  }
  return results;
}

function listSessionFiles() {
  const roots = [
    "~/.openclaw/sessions",
    "~/.openclaw/agents",
    "~/.openclaw/cron/runs",
    "~/.agent/sessions",
  ].map(expandHome);
  const files = [];

  for (const root of roots) {
    files.push(...findJsonlFilesRecursive(root));
  }

  return files;
}

function safeJsonParse(line, file, lineNumber) {
  try {
    return JSON.parse(line);
  } catch {
    return {
      _parseError: true,
      _file: file,
      _line: lineNumber,
    };
  }
}

function getTimestamp(entry) {
  const ts = entry.timestamp || entry.created_at;
  if (typeof ts !== "string" || ts.length === 0) {
    return null;
  }
  const d = new Date(ts);
  if (Number.isNaN(d.getTime())) {
    return null;
  }
  return d;
}

function flattenText(value) {
  if (typeof value === "string") {
    return value;
  }
  if (Array.isArray(value)) {
    return value.map(flattenText).join(" ");
  }
  if (value && typeof value === "object") {
    return Object.values(value).map(flattenText).join(" ");
  }
  return "";
}

/**
 * Get role from entry, handling nested message structure
 * OpenClaw session logs store role in entry.message.role, not entry.role
 */
function getRole(entry) {
  // Try entry.message.role first (OpenClaw format)
  const nestedRole = entry.message?.role;
  if (typeof nestedRole === "string") {
    return nestedRole.toLowerCase();
  }
  // Fallback to entry.role for backward compatibility
  const directRole = entry.role;
  if (typeof directRole === "string") {
    return directRole.toLowerCase();
  }
  return "";
}

/**
 * Get content from entry, handling nested message structure
 */
function getContent(entry) {
  // Try entry.message.content first (OpenClaw format)
  if (entry.message?.content) {
    return entry.message.content;
  }
  // Fallback to entry.content for backward compatibility
  return entry.content;
}

function isLikelyUserEntry(entry) {
  const role = getRole(entry);
  if (role === "user") {
    return true;
  }

  const type = typeof entry.type === "string" ? entry.type.toLowerCase() : "";
  if (type.includes("user")) {
    return true;
  }

  const payloadText = flattenText(entry).toLowerCase();
  if (payloadText.includes("\"role\":\"user\"") || payloadText.includes("role:user")) {
    return true;
  }

  return false;
}

function isNoise(entry) {
  // Check both nested and direct content
  const nestedContent = flattenText(entry.message?.content);
  const directContent = flattenText(entry.content);
  const payloadText = (nestedContent + " " + directContent).toLowerCase();
  
  const noiseTokens = [
    "heartbeat",
    "cron",
    "nightly reflection",
    "scheduler",
    "system pulse",
    "system heartbeat",
  ];
  return noiseTokens.some((token) => payloadText.includes(token));
}

function auditDay({ day, tz, verbose }) {
  const files = listSessionFiles();
  const summary = {
    targetDay: day,
    timezone: tz,
    scannedFiles: files.length,
    parseErrors: 0,
    matchedMessages: 0,
    userMessages: 0,
    assistantMessages: 0,
    imageMessages: 0,
    noiseMessages: 0,
    filesWithMatches: new Map(),
  };

  for (const file of files) {
    const content = fs.readFileSync(file, "utf8");
    const lines = content.split(/\r?\n/);

    for (let i = 0; i < lines.length; i += 1) {
      const line = lines[i].trim();
      if (!line) {
        continue;
      }

      const entry = safeJsonParse(line, file, i + 1);
      if (entry._parseError) {
        summary.parseErrors += 1;
        continue;
      }

      const ts = getTimestamp(entry);
      if (!ts) {
        continue;
      }

      const messageDay = formatDateInTz(ts, tz);
      if (messageDay !== day) {
        continue;
      }

      summary.matchedMessages += 1;
      summary.filesWithMatches.set(file, (summary.filesWithMatches.get(file) || 0) + 1);

      // Use getRole() to handle nested message structure
      const role = getRole(entry);
      if (role === "assistant") {
        summary.assistantMessages += 1;
      }

      const type = typeof entry.type === "string" ? entry.type.toLowerCase() : "";
      if (type === "image") {
        summary.imageMessages += 1;
      }

      if (isLikelyUserEntry(entry)) {
        summary.userMessages += 1;
      }

      if (isNoise(entry)) {
        summary.noiseMessages += 1;
      }

      if (verbose) {
        const tsText = entry.timestamp || entry.created_at;
        const displayRole = getRole(entry) || "?";
        console.log(`[${path.basename(file)}:${i + 1}] ${tsText} role=${displayRole} type=${entry.type || "?"}`);
      }
    }
  }

  return summary;
}

function printSummary(summary) {
  console.log("PhoenixClaw Session Day Audit");
  console.log("-----------------------------");
  console.log(`target_day: ${summary.targetDay}`);
  console.log(`timezone: ${summary.timezone}`);
  console.log(`scanned_files: ${summary.scannedFiles}`);
  console.log(`matched_messages: ${summary.matchedMessages}`);
  console.log(`user_messages: ${summary.userMessages}`);
  console.log(`assistant_messages: ${summary.assistantMessages}`);
  console.log(`image_messages: ${summary.imageMessages}`);
  console.log(`noise_messages: ${summary.noiseMessages}`);
  console.log(`parse_errors: ${summary.parseErrors}`);

  const activeFiles = Array.from(summary.filesWithMatches.entries())
    .sort((a, b) => b[1] - a[1]);

  if (activeFiles.length === 0) {
    console.log("files_with_matches: none");
    return;
  }

  console.log("files_with_matches:");
  for (const [file, count] of activeFiles) {
    console.log(`  - ${file} (${count})`);
  }
}

function main() {
  const args = parseArgs(process.argv.slice(2));
  if (!/^\d{4}-\d{2}-\d{2}$/.test(args.day)) {
    throw new Error(`Invalid --day value: ${args.day} (expected YYYY-MM-DD)`);
  }

  const summary = auditDay(args);
  printSummary(summary);

  if (summary.userMessages === 0 && summary.matchedMessages > 0) {
    process.exitCode = 2;
  }
}

try {
  main();
} catch (error) {
  console.error(`Error: ${error.message}`);
  process.exit(1);
}
