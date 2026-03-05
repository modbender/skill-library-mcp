#!/usr/bin/env node

/**
 * ClawAudit Auto-Fix
 * - Automatically fixes OpenClaw configuration issues (with confirmation)
 * - Shows manual fix commands for system-level findings (no auto-apply)
 *
 * Usage:
 *   node auto-fix.mjs           # Interactive mode (recommended)
 *   node auto-fix.mjs --dry-run # Show what would change without applying
 *   node auto-fix.mjs --yes     # Apply all OpenClaw config fixes without confirmation
 */

import { readFileSync, writeFileSync, existsSync, chmodSync, statSync, renameSync } from "fs";
import { join, resolve, dirname } from "path";
import { fileURLToPath } from "url";
import { homedir } from "os";
import { createInterface } from "readline";
import { execSync } from "child_process";
import { CONFIG_PATHS, STATE_DIRS, COLORS, parseFlag } from "./lib/utils.mjs";

const __dirname = dirname(fileURLToPath(import.meta.url));
const HOME = homedir();
const DRY_RUN = parseFlag("--dry-run");
const AUTO_YES = parseFlag("--yes");

const { BOLD, GREEN, YELLOW, RED, GRAY, CYAN, RESET } = COLORS;

// --- Helpers ---

function ask(question) {
  if (AUTO_YES) return Promise.resolve("y");
  const rl = createInterface({ input: process.stdin, output: process.stdout });
  return new Promise((res) => {
    rl.question(question, (answer) => {
      rl.close();
      res(answer.trim().toLowerCase());
    });
  });
}

function deepSet(obj, path, value) {
  const keys = path.split(".");
  let current = obj;
  for (let i = 0; i < keys.length - 1; i++) {
    if (!(keys[i] in current) || typeof current[keys[i]] !== "object") {
      current[keys[i]] = {};
    }
    current = current[keys[i]];
  }
  current[keys[keys.length - 1]] = value;
}

function deepGet(obj, path) {
  return path.split(".").reduce((o, k) => o && o[k], obj);
}

// Atomic write: write to temp file then rename to avoid corruption on crash
function atomicWrite(filePath, content) {
  const tmp = filePath + ".claw-audit.tmp";
  writeFileSync(tmp, content, "utf-8");
  renameSync(tmp, filePath);
}

// --- OpenClaw Config Fixes ---

const FIXES = [
  {
    id: "bind-loopback",
    title: "Bind gateway to loopback only",
    check: (cfg) => {
      const bind = deepGet(cfg, "gateway.bind");
      return bind && bind !== "loopback" && bind !== "127.0.0.1";
    },
    apply: (cfg) => deepSet(cfg, "gateway.bind", "loopback"),
    description: 'Sets gateway.bind to "loopback" to prevent network exposure.',
  },
  {
    id: "enable-sandbox",
    title: "Enable sandbox mode",
    check: (cfg) => !deepGet(cfg, "agents.defaults.sandbox.enabled"),
    apply: (cfg) => deepSet(cfg, "agents.defaults.sandbox.enabled", true),
    description: "Enables Docker sandbox for agent execution.",
  },
  {
    id: "restrict-exec",
    title: "Restrict patch execution to workspace",
    check: (cfg) => deepGet(cfg, "tools.exec.applyPatch.workspaceOnly") === false,
    apply: (cfg) => deepSet(cfg, "tools.exec.applyPatch.workspaceOnly", true),
    description: "Prevents the agent from writing files outside the workspace.",
  },
  {
    id: "restrict-fs",
    title: "Restrict file system to workspace",
    check: (cfg) => deepGet(cfg, "tools.fs.workspaceOnly") === false,
    apply: (cfg) => deepSet(cfg, "tools.fs.workspaceOnly", true),
    description: "Limits file read/write to the workspace directory.",
  },
];

// --- File Permission Fixes ---

const PERM_FIXES = [];

function findPermissionFixes() {
  const dirs = [join(HOME, ".openclaw"), join(HOME, ".clawdbot")];
  for (const dir of dirs) {
    if (!existsSync(dir)) continue;

    const sensitiveFiles = [
      join(dir, "openclaw.json"),
      join(dir, "config.json"),
      join(dir, ".env"),
    ];

    for (const f of sensitiveFiles) {
      if (!existsSync(f)) continue;
      const stats = statSync(f);
      const mode = stats.mode & 0o777;
      if (mode & 0o077) {
        PERM_FIXES.push({ file: f, currentMode: mode.toString(8), targetMode: "600" });
      }
    }

    const credDir = join(dir, "credentials");
    if (existsSync(credDir)) {
      const stats = statSync(credDir);
      const mode = stats.mode & 0o777;
      if (mode & 0o077) {
        PERM_FIXES.push({ file: credDir, currentMode: mode.toString(8), targetMode: "700" });
      }
    }
  }
}

// --- System Findings Display (read-only, no auto-apply) ---

const SEVERITY_ICON = { critical: "🔴", warning: "🟡", info: "🔵" };

function showSystemFindings(findings) {
  if (findings.length === 0) {
    console.log(`${GREEN}✅ No system-level issues found.${RESET}\n`);
    return;
  }

  console.log(`${BOLD}🖥️  System Findings — Manual Action Required${RESET}`);
  console.log(`${GRAY}These require root/sudo. Run the commands below yourself.${RESET}\n`);

  const sorted = [...findings].sort((a, b) => {
    const order = { critical: 0, warning: 1, info: 2 };
    return order[a.severity] - order[b.severity];
  });

  for (const f of sorted) {
    const icon = SEVERITY_ICON[f.severity] || "🔵";
    console.log(`${icon} ${BOLD}${f.code}${RESET} — ${f.title}`);
    console.log(`   ${GRAY}${f.detail}${RESET}`);
    if (f.fix) {
      console.log(`   ${CYAN}Fix:${RESET}`);
      // Print each command on its own line for easy copy-paste
      f.fix.split(/&&|\n/).map(s => s.trim()).filter(Boolean).forEach(cmd => {
        console.log(`   ${CYAN}  $ ${cmd}${RESET}`);
      });
    }
    console.log();
  }
}

// --- Main ---

async function main() {
  console.log(`\n${BOLD}🛡️  ClawAudit Auto-Fix${RESET}`);
  if (DRY_RUN) console.log(`${YELLOW}   (dry run — no changes will be applied)${RESET}`);
  console.log();

  // --- Load OpenClaw config ---
  let configPath = null;
  let config = {};
  for (const p of CONFIG_PATHS) {
    if (existsSync(p)) {
      configPath = p;
      try {
        config = JSON.parse(readFileSync(p, "utf-8"));
        console.log(`${GRAY}Config: ${configPath}${RESET}\n`);
      } catch {
        console.log(`${RED}✗ Config file is invalid JSON: ${p}${RESET}\n`);
      }
      break;
    }
  }

  if (!configPath) {
    console.log(`${YELLOW}No OpenClaw config file found. Skipping config fixes.${RESET}\n`);
  }

  // --- Find applicable fixes ---
  const applicableFixes = configPath ? FIXES.filter((f) => f.check(config)) : [];
  findPermissionFixes();

  // --- Load system audit findings ---
  let systemFindings = [];
  try {
    const out = execSync(`node "${resolve(__dirname, "audit-system.mjs")}" --json 2>/dev/null`, {
      encoding: "utf-8",
      timeout: 15000,
    });
    systemFindings = JSON.parse(out).findings || [];
  } catch {
    // System audit unavailable — skip
  }

  const hasAnything = applicableFixes.length > 0 || PERM_FIXES.length > 0 || systemFindings.length > 0;
  if (!hasAnything) {
    console.log(`${GREEN}✅ Nothing to fix — your setup looks great!${RESET}\n`);
    return;
  }

  let applied = 0;

  // --- Apply OpenClaw config fixes (automatic, with confirmation) ---
  if (applicableFixes.length > 0) {
    console.log(`${BOLD}⚙️  OpenClaw Config Fixes${RESET}\n`);
    for (const fix of applicableFixes) {
      console.log(`${YELLOW}⚡ ${fix.title}${RESET}`);
      console.log(`   ${GRAY}${fix.description}${RESET}`);

      if (DRY_RUN) {
        console.log(`   ${GRAY}Would apply${RESET}\n`);
      } else {
        const answer = await ask(`   Apply this fix? (y/N) `);
        if (answer === "y" || answer === "yes") {
          fix.apply(config);
          applied++;
          console.log(`   ${GREEN}✓ Applied${RESET}\n`);
        } else {
          console.log(`   ${GRAY}Skipped${RESET}\n`);
        }
      }
    }
  }

  // --- Apply file permission fixes (automatic, with confirmation) ---
  if (PERM_FIXES.length > 0) {
    if (applicableFixes.length > 0) console.log();
    console.log(`${BOLD}🔒 File Permission Fixes${RESET}\n`);
    for (const pf of PERM_FIXES) {
      console.log(`${YELLOW}⚡ Fix permissions: ${pf.file}${RESET}`);
      console.log(`   ${GRAY}Current: ${pf.currentMode} → Target: ${pf.targetMode}${RESET}`);

      if (DRY_RUN) {
        console.log(`   ${GRAY}Would apply${RESET}\n`);
      } else {
        const answer = await ask(`   Apply this fix? (y/N) `);
        if (answer === "y" || answer === "yes") {
          chmodSync(pf.file, parseInt(pf.targetMode, 8));
          applied++;
          console.log(`   ${GREEN}✓ Applied${RESET}\n`);
        } else {
          console.log(`   ${GRAY}Skipped${RESET}\n`);
        }
      }
    }
  }

  // --- Save config atomically ---
  if (applied > 0 && configPath && !DRY_RUN) {
    atomicWrite(configPath, JSON.stringify(config, null, 2) + "\n");
    console.log(`${GREEN}✓ Config saved to ${configPath}${RESET}`);
    console.log(`${GRAY}  Restart your OpenClaw gateway for changes to take effect.${RESET}\n`);
  }

  // --- Show system findings (display only, no auto-apply) ---
  if (systemFindings.length > 0) {
    console.log(`\n${"━".repeat(50)}\n`);
    showSystemFindings(systemFindings);
  }

  // --- Summary ---
  console.log(`${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}`);
  if (!DRY_RUN) {
    console.log(`Applied: ${applied} automatic fix${applied !== 1 ? "es" : ""}`);
  }
  if (systemFindings.length > 0) {
    console.log(`System findings: ${systemFindings.length} — run commands above manually`);
  }
  console.log(`${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}\n`);
}

main().catch(console.error);
