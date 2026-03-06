#!/usr/bin/env node

/**
 * ClawAudit File Integrity Monitor
 * Creates SHA256 baselines for critical OpenClaw cognitive files and detects drift.
 *
 * Usage:
 *   node check-integrity.mjs              # Check against baseline (creates one if missing)
 *   node check-integrity.mjs --baseline   # (Re-)create baseline from current state
 *   node check-integrity.mjs --json       # JSON output
 */

import { createHash } from "crypto";
import { readFileSync, writeFileSync, existsSync } from "fs";
import { join } from "path";
import { homedir } from "os";
import { parseFlag, createFindingCollector, COLORS } from "./lib/utils.mjs";

const HOME = homedir();
const JSON_OUTPUT = parseFlag("--json");
const CREATE_BASELINE = parseFlag("--baseline");

const BASELINE_PATH = join(HOME, ".openclaw", "claw-audit-baseline.json");

// --- Config ---

const CONFIG_PATHS = [
  join(HOME, ".openclaw", "claw-audit-config.json"),
  join(HOME, ".openclaw", "workspace", "skills", "claw-audit", "claw-audit-config.json"),
];

function loadConfig() {
  for (const p of CONFIG_PATHS) {
    if (existsSync(p)) {
      try { return JSON.parse(readFileSync(p, "utf-8")); } catch { /* ignore */ }
    }
  }
  return {};
}

const CONFIG = loadConfig();

// Cognitive files that define agent identity and behaviour — high-value tamper targets.
// Override via claw-audit-config.json: { "cognitiveFiles": ["SOUL.md", "AGENTS.md", ...] }
const DEFAULT_COGNITIVE_FILES = [
  "SOUL.md",
  "AGENTS.md",
  "IDENTITY.md",
  "MEMORY.md",
  "USER.md",
  "TOOLS.md",
];

const COGNITIVE_FILES = Array.isArray(CONFIG.cognitiveFiles)
  ? CONFIG.cognitiveFiles
  : DEFAULT_COGNITIVE_FILES;

// --- Helpers ---

function getWorkspacePath() {
  const candidates = [
    join(HOME, ".openclaw", "openclaw.json"),
    join(HOME, ".openclaw", "config.json"),
  ];
  for (const p of candidates) {
    if (!existsSync(p)) continue;
    try {
      const cfg = JSON.parse(readFileSync(p, "utf-8"));
      const ws = cfg?.agents?.defaults?.workspace;
      if (ws) return ws.replace(/^~/, HOME);
    } catch { /* ignore parse errors */ }
  }
  return join(HOME, ".openclaw", "workspace");
}

function sha256(content) {
  return createHash("sha256").update(content, "utf-8").digest("hex");
}

function scanFiles(workspace) {
  const result = {};
  for (const filename of COGNITIVE_FILES) {
    const fullPath = join(workspace, filename);
    if (!existsSync(fullPath)) continue;
    try {
      const content = readFileSync(fullPath, "utf-8");
      result[filename] = {
        hash: sha256(content),
        size: content.length,
        path: fullPath,
        scannedAt: new Date().toISOString(),
      };
    } catch { /* unreadable — skip */ }
  }
  return result;
}

function loadBaseline() {
  if (!existsSync(BASELINE_PATH)) return null;
  try {
    return JSON.parse(readFileSync(BASELINE_PATH, "utf-8"));
  } catch {
    return null;
  }
}

function saveBaseline(files, workspace) {
  const baseline = {
    createdAt: new Date().toISOString(),
    workspace,
    files,
  };
  writeFileSync(BASELINE_PATH, JSON.stringify(baseline, null, 2), "utf-8");
  return baseline;
}

// --- Audit ---

function runIntegrityCheck() {
  const collector = createFindingCollector();
  const workspace = getWorkspacePath();
  const current = scanFiles(workspace);

  // --- Baseline creation mode ---
  if (CREATE_BASELINE) {
    const baseline = saveBaseline(current, workspace);
    const count = Object.keys(current).length;

    if (!JSON_OUTPUT) {
      const { BOLD, GREEN, RESET, GRAY } = COLORS;
      console.log(`\n${BOLD}🔐 ClawAudit — File Integrity Baseline${RESET}\n`);
      console.log(`${GREEN}✅ Baseline created: ${BASELINE_PATH}${RESET}`);
      console.log(`   Workspace: ${workspace}`);
      console.log(`   Files hashed: ${count}`);
      for (const [name, info] of Object.entries(current)) {
        console.log(`   ${GRAY}${name}${RESET}  ${info.hash.slice(0, 16)}…  (${info.size} bytes)`);
      }
      console.log();
    } else {
      console.log(JSON.stringify({
        action: "baseline_created",
        path: BASELINE_PATH,
        workspace,
        files: baseline.files,
      }, null, 2));
    }
    return;
  }

  // --- Check mode ---
  const baseline = loadBaseline();
  // 1 check for baseline existence + 1 per file when baseline is available
  collector.check(1 + (baseline ? Object.keys(current).length : 0));

  if (!baseline) {
    collector.add(
      "info",
      "INTEG-001",
      "No integrity baseline established",
      `No baseline found at ${BASELINE_PATH}. Run with --baseline to create one. Without a baseline, file tampering cannot be detected.`,
      `node scripts/check-integrity.mjs --baseline`
    );
  } else {
    const baseFiles = baseline.files || {};

    for (const [filename, current_info] of Object.entries(current)) {
      if (!baseFiles[filename]) {
        // New file since baseline — informational
        collector.add(
          "info",
          "INTEG-003",
          `New cognitive file since baseline: ${filename}`,
          `${filename} was not present when the baseline was created. Update the baseline if this is expected.`,
          `node scripts/check-integrity.mjs --baseline`
        );
      } else if (baseFiles[filename].hash !== current_info.hash) {
        // Hash changed — potential drift or tampering
        collector.add(
          "warning",
          "INTEG-002",
          `Cognitive file changed since baseline: ${filename}`,
          `${filename} hash changed.\n   Baseline: ${baseFiles[filename].hash.slice(0, 24)}…\n   Current:  ${current_info.hash.slice(0, 24)}…\n   If you edited this file intentionally, update the baseline.`,
          `Review changes: diff ${current_info.path} <(git show HEAD:${filename} 2>/dev/null)\nThen update baseline: node scripts/check-integrity.mjs --baseline`
        );
      }
    }

    // Files in baseline that are now gone
    for (const filename of Object.keys(baseFiles)) {
      if (!current[filename]) {
        collector.add(
          "warning",
          "INTEG-002",
          `Cognitive file deleted since baseline: ${filename}`,
          `${filename} existed when the baseline was created but is now missing.`,
          `Restore the file or update baseline: node scripts/check-integrity.mjs --baseline`
        );
      }
    }
  }

  // --- Output ---
  const findings = collector.getAll();
  const counts = collector.countBySeverity();

  if (JSON_OUTPUT) {
    console.log(JSON.stringify({
      critical: counts.critical,
      warnings: counts.warnings,
      info: counts.info,
      totalChecks: collector.getTotalChecks(),
      passed: collector.getPassed(),
      findings,
    }, null, 2));
    return;
  }

  const { BOLD, GREEN, RESET, GRAY } = COLORS;
  console.log(`\n${BOLD}🔐 ClawAudit — File Integrity Check${RESET}\n`);

  if (findings.length === 0) {
    const count = Object.keys(current).length;
    console.log(`${GREEN}✅ All ${count} cognitive files match the baseline.${RESET}\n`);
    return;
  }

  const icons = { critical: "🔴", warning: "🟡", info: "🔵" };
  const labels = { critical: "CRITICAL", warning: "WARNING", info: "INFO" };
  for (const f of findings) {
    console.log(`${icons[f.severity]} ${labels[f.severity]}: ${f.code} — ${f.title}`);
    console.log(`   ${f.detail}`);
    console.log();
  }

  console.log(`${GRAY}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}`);
  console.log(`${GRAY}Integrity: ${counts.critical} critical, ${counts.warnings} warnings, ${counts.info} info${RESET}\n`);
}

runIntegrityCheck();
