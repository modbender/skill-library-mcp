#!/usr/bin/env node

/**
 * ClawAudit Config Auditor
 * Audits OpenClaw configuration for security misconfigurations.
 *
 * Usage:
 *   node audit-config.mjs            # Run full audit
 *   node audit-config.mjs --json     # Output as JSON
 *   node audit-config.mjs --fix      # Show fix commands
 */

import { readFileSync, existsSync, statSync } from "fs";
import { spawnSync } from "child_process";
import { join, resolve } from "path";
import { homedir } from "os";
import { CONFIG_PATHS, STATE_DIRS, parseFlag, createFindingCollector } from "./lib/utils.mjs";

const HOME = homedir();
const JSON_OUTPUT = parseFlag("--json");
const SHOW_FIX = parseFlag("--fix");

// --- Finding collector ---
const collector = createFindingCollector();
const addFinding = collector.add.bind(collector);
const addCheck = collector.check.bind(collector);

// --- Helpers ---
function loadConfig() {
  for (const p of CONFIG_PATHS) {
    if (existsSync(p)) {
      try {
        const raw = readFileSync(p, "utf-8");
        return { path: p, config: JSON.parse(raw) };
      } catch {
        addFinding(
          "warning",
          "WARN-011",
          "Config file is invalid JSON",
          `Could not parse: ${p}`,
          `Validate JSON syntax in ${p}`
        );
      }
    }
  }
  return null;
}

function checkFilePermissions(filepath) {
  try {
    const stats = statSync(filepath);
    const mode = (stats.mode & 0o777).toString(8);
    return { mode, isGroupReadable: !!(stats.mode & 0o040), isWorldReadable: !!(stats.mode & 0o004) };
  } catch {
    return null;
  }
}

// --- Audit Checks ---

function auditGatewayExposure(config) {
  addCheck();
  const bind = config?.gateway?.bind || config?.gateway?.host || "loopback";
  if (bind !== "loopback" && bind !== "127.0.0.1" && bind !== "::1" && bind !== "localhost") {
    addFinding(
      "critical",
      "WARN-001",
      "Gateway exposed to network",
      `Gateway bind is set to "${bind}" instead of loopback. This exposes your agent to the local network or internet.`,
      `Set gateway.bind to "loopback" in your config, or run: openclaw gateway run --bind loopback`
    );
  }

  const authToken = config?.gateway?.auth?.token || config?.gateway?.authToken;
  if (bind !== "loopback" && !authToken) {
    addFinding(
      "critical",
      "WARN-012",
      "Gateway exposed without authentication",
      "Gateway is network-accessible but has no auth token set. Anyone on your network can control your agent.",
      "Set gateway.auth.token in your config or use --auth-token flag"
    );
  }
}

function auditDMPolicy(config) {
  addCheck();
  const channels = config?.channels || {};
  for (const [name, ch] of Object.entries(channels)) {
    const policy = ch?.dmPolicy || ch?.dm?.policy || "pairing";
    const allowFrom = ch?.allowFrom || ch?.dm?.allowFrom || [];

    if (policy === "open") {
      if (allowFrom.includes("*")) {
        addFinding(
          "critical",
          "WARN-002",
          `DM policy is open with wildcard (${name})`,
          `Channel "${name}" accepts DMs from anyone. This means any stranger can send commands to your agent.`,
          `Set channels.${name}.dmPolicy to "pairing" or restrict allowFrom`
        );
      } else {
        addFinding(
          "warning",
          "WARN-002",
          `DM policy is open (${name})`,
          `Channel "${name}" has an open DM policy. Consider using "pairing" for better security.`,
          `Set channels.${name}.dmPolicy to "pairing"`
        );
      }
    }
  }
}

function auditSandbox(config) {
  addCheck();
  const sandbox = config?.agents?.defaults?.sandbox;
  const sandboxEnabled = sandbox?.enabled ?? sandbox?.docker?.enabled ?? false;

  if (!sandboxEnabled) {
    // Mitigating check: is OpenClaw running as an unprivileged user (no sudo/wheel)?
    const isRoot = process.getuid?.() === 0;
    const groupsResult = spawnSync("groups", { encoding: "utf-8", timeout: 3000 });
    const userGroups = (groupsResult.stdout || "").trim().split(/\s+/);
    const hasSudo = isRoot || userGroups.some((g) => ["sudo", "wheel", "admin"].includes(g));

    if (!hasSudo) {
      addFinding(
        "info",
        "WARN-003",
        "Sandbox not enabled (mitigated: unprivileged user)",
        "Sandbox is disabled, but OpenClaw runs as an unprivileged user without sudo access. Ability to cause system-level damage is limited.",
        "Enable sandbox for defense-in-depth: agents.defaults.sandbox.enabled = true",
        true // mitigated
      );
    } else {
      addFinding(
        "warning",
        "WARN-003",
        "Sandbox mode not enabled",
        "Agent runs with full system access. A sandbox would limit damage from malicious skills or prompt injection.",
        "Enable sandbox in config: agents.defaults.sandbox.enabled = true"
      );
    }
  }
}

function auditBrowserControl(config) {
  addCheck();
  const browser = config?.tools?.browser || config?.browser;
  if (browser?.enabled !== false) {
    const exposure = config?.gateway?.bind || "loopback";
    if (exposure !== "loopback" && exposure !== "127.0.0.1") {
      addFinding(
        "warning",
        "WARN-004",
        "Browser control exposed beyond localhost",
        "Browser automation is enabled and the gateway is network-accessible. Remote attackers could control a browser session.",
        "Restrict gateway to loopback or disable browser control for non-local setups"
      );
    }
  }
}

function auditExecPolicy(config) {
  addCheck();
  const workspaceOnly = config?.tools?.exec?.applyPatch?.workspaceOnly;
  if (workspaceOnly === false) {
    addFinding(
      "warning",
      "WARN-013",
      "Patch execution not restricted to workspace",
      "tools.exec.applyPatch.workspaceOnly is false. The agent can write files anywhere on your system.",
      "Set tools.exec.applyPatch.workspaceOnly to true"
    );
  }

  const fsWorkspaceOnly = config?.tools?.fs?.workspaceOnly;
  if (fsWorkspaceOnly === false) {
    addFinding(
      "warning",
      "WARN-014",
      "File system access not restricted to workspace",
      "tools.fs.workspaceOnly is false. The agent can read/write anywhere.",
      "Set tools.fs.workspaceOnly to true"
    );
  }
}

function auditCredentialFiles() {
  addCheck();
  for (const stateDir of STATE_DIRS) {
    if (!existsSync(stateDir)) continue;

    // Check main config permissions
    const configFiles = [
      join(stateDir, "openclaw.json"),
      join(stateDir, "config.json"),
      join(stateDir, ".env"),
    ];

    for (const f of configFiles) {
      if (!existsSync(f)) continue;
      const perms = checkFilePermissions(f);
      if (perms && (perms.isGroupReadable || perms.isWorldReadable)) {
        addFinding(
          "warning",
          "WARN-006",
          `Credential file has loose permissions`,
          `${f} is readable by group/others (mode: ${perms.mode}). Should be 600 or 700.`,
          `chmod 600 ${f}`
        );
      }
    }

    // Check for plaintext credentials in .env
    const envFile = join(stateDir, ".env");
    if (existsSync(envFile)) {
      try {
        const content = readFileSync(envFile, "utf-8");
        const sensitiveKeys = [
          "ANTHROPIC_API_KEY", "OPENAI_API_KEY", "DISCORD_TOKEN",
          "TELEGRAM_TOKEN", "SLACK_TOKEN", "GITHUB_TOKEN",
        ];
        for (const key of sensitiveKeys) {
          if (content.includes(key + "=")) {
            addFinding(
              "warning",
              "WARN-006",
              `Plaintext credential found: ${key}`,
              `${envFile} contains ${key} in plaintext. Consider using a secret manager.`,
              "Use environment variables from your shell or a secrets manager instead of .env files"
            );
            break; // One finding per file is enough
          }
        }
      } catch { /* ignore read errors */ }
    }

    // Check credential subdirectories
    const credDir = join(stateDir, "credentials");
    if (existsSync(credDir)) {
      const perms = checkFilePermissions(credDir);
      if (perms && (perms.isGroupReadable || perms.isWorldReadable)) {
        addFinding(
          "critical",
          "WARN-006",
          "Credentials directory has loose permissions",
          `${credDir} is accessible by others (mode: ${perms.mode}).`,
          `chmod -R 700 ${credDir}`
        );
      }
    }
  }
}

function auditSkillsAllowlist(config) {
  addCheck();
  const allowlist = config?.skills?.load?.allowlist;
  if (!allowlist) {
    addFinding(
      "info",
      "INFO-004",
      "No skills allowlist configured",
      "All eligible skills are loaded. Consider using an allowlist to limit which skills the agent can access.",
      "Set skills.load.allowlist in config to only load trusted skills"
    );
  }
}

function auditCronJobs() {
  addCheck();
  const cronPath = join(HOME, ".openclaw", "cron", "jobs.json");
  if (!existsSync(cronPath)) return;

  let jobs;
  try {
    jobs = JSON.parse(readFileSync(cronPath, "utf-8"))?.jobs || [];
  } catch {
    return;
  }

  // Dangerous patterns in cron job messages/commands
  const dangerousPatterns = [
    { pattern: /curl\s+.*\|\s*(ba)?sh/i,    label: "download-and-execute via curl|sh" },
    { pattern: /wget\s+.*\|\s*(ba)?sh/i,    label: "download-and-execute via wget|sh" },
    { pattern: /eval\s*\(/i,                label: "eval() call" },
    { pattern: /base64\s+.*-d/i,            label: "base64 decode (possible payload obfuscation)" },
    { pattern: /rm\s+-rf\s+\//,             label: "destructive rm -rf /" },
  ];

  const flagged = [];
  for (const job of jobs) {
    const cmd = job?.payload?.message || job?.payload?.command || "";
    for (const { pattern, label } of dangerousPatterns) {
      if (pattern.test(cmd)) {
        flagged.push(`Job "${job.name || job.id}": ${label}`);
      }
    }
  }

  if (flagged.length > 0) {
    addFinding(
      "critical",
      "WARN-020",
      `Suspicious pattern in ${flagged.length} cron job${flagged.length > 1 ? "s" : ""}`,
      `Potentially dangerous cron jobs detected: ${flagged.join("; ")}`,
      "Review the flagged cron jobs in ~/.openclaw/cron/jobs.json and remove or sanitize them"
    );
  }

  // WARN-021: LLM cron job schedule conflicts (risk of rate limiting)
  auditCronJobOverlap(jobs);

  // WARN-022: agentTurn jobs without bestEffortDeliver (risk of infinite retry loop)
  const noDeliverSafety = jobs.filter(
    (j) => j.enabled !== false &&
      j.payload?.kind === "agentTurn" &&
      !j.delivery?.bestEffort
  );

  if (noDeliverSafety.length > 0) {
    const names = noDeliverSafety.map((j) => `"${j.name || j.id}"`).join(", ");
    addFinding(
      "warning",
      "WARN-022",
      `${noDeliverSafety.length} LLM cron job${noDeliverSafety.length > 1 ? "s" : ""} without bestEffortDeliver`,
      `${names} — if announce delivery fails, OpenClaw retries without backoff (1 req/s forever), which can freeze the gateway and make the server unreachable.`,
      `Run: openclaw cron edit <id> --best-effort-deliver  for each affected job`
    );
  }
}

/**
 * Expands a 5-field cron expression into a Set of "H:M" time slot strings
 * covering one full day. Returns null if the expression can't be parsed.
 */
export function expandCronSlots(expr) {
  const parts = (expr || "").trim().split(/\s+/);
  if (parts.length !== 5) return null;

  const [minField, hourField] = parts;

  function expandField(field, max) {
    const values = new Set();
    for (const part of field.split(",")) {
      if (part === "*") {
        for (let i = 0; i < max; i++) values.add(i);
      } else if (part.includes("/")) {
        const [range, step] = part.split("/");
        const stepNum = parseInt(step, 10);
        const start = range === "*" ? 0 : parseInt(range, 10);
        if (isNaN(stepNum) || stepNum <= 0) return null;
        for (let i = start; i < max; i += stepNum) values.add(i);
      } else if (part.includes("-")) {
        const [start, end] = part.split("-").map(Number);
        for (let i = start; i <= end; i++) values.add(i);
      } else {
        const n = parseInt(part, 10);
        if (!isNaN(n)) values.add(n);
      }
    }
    return values;
  }

  const minutes = expandField(minField, 60);
  const hours = expandField(hourField, 24);
  if (!minutes || !hours) return null;

  const slots = new Set();
  for (const h of hours) {
    for (const m of minutes) {
      slots.add(`${h}:${m}`);
    }
  }
  return slots;
}

function auditCronJobOverlap(jobs) {
  // Only enabled agentTurn jobs use the LLM
  const llmJobs = jobs.filter(
    (j) => j.enabled !== false && j.payload?.kind === "agentTurn"
  );
  if (llmJobs.length < 2) return;

  const conflicts = [];
  for (let i = 0; i < llmJobs.length; i++) {
    for (let k = i + 1; k < llmJobs.length; k++) {
      const a = llmJobs[i];
      const b = llmJobs[k];
      const exprA = a.schedule?.expr;
      const exprB = b.schedule?.expr;
      if (!exprA || !exprB) continue;

      const slotsA = expandCronSlots(exprA);
      const slotsB = expandCronSlots(exprB);
      if (!slotsA || !slotsB) continue;

      const overlap = [...slotsA].filter((s) => slotsB.has(s));
      if (overlap.length === 0) continue;

      const examples = overlap.slice(0, 3).map((s) => {
        const [h, m] = s.split(":");
        return `${h.padStart(2, "0")}:${m.padStart(2, "0")}`;
      });
      const suffix = overlap.length > 3 ? ` (+${overlap.length - 3} more)` : "";
      conflicts.push(
        `"${a.name || a.id}" + "${b.name || b.id}" at ${examples.join(", ")}${suffix}`
      );
    }
  }

  if (conflicts.length > 0) {
    addFinding(
      "warning",
      "WARN-021",
      `${conflicts.length} LLM cron job schedule conflict${conflicts.length > 1 ? "s" : ""}`,
      `Concurrent LLM-based cron jobs risk API rate limits and timeouts. ${conflicts.join("; ")}`,
      "Stagger job schedules so no two agentTurn jobs fire at the same time"
    );
  }
}

function auditPairedDevices() {
  addCheck();
  const devicesPath = join(HOME, ".openclaw", "devices", "paired.json");
  if (!existsSync(devicesPath)) return;

  let devices;
  try {
    const raw = JSON.parse(readFileSync(devicesPath, "utf-8"));
    // paired.json is either an object (map of deviceId → device) or an array
    devices = Array.isArray(raw) ? raw : Object.values(raw);
  } catch {
    return;
  }

  const count = devices.length;
  if (count === 0) return;

  const severity = count > 5 ? "warning" : "info";
  const names = devices
    .map((d) => d.clientId || d.platform || d.deviceId?.slice(0, 8) || "unknown")
    .join(", ");

  addFinding(
    severity,
    "INFO-010",
    `${count} paired device${count > 1 ? "s" : ""} registered`,
    `Paired: ${names}. Verify all are known and authorized.`,
    `Review: cat ~/.openclaw/devices/paired.json — unpair unknown devices via OpenClaw settings`
  );
}

function auditSubAgentLimits(config) {
  addCheck();
  const maxConcurrent = config?.agents?.defaults?.maxConcurrent;
  const subMaxConcurrent = config?.agents?.defaults?.subagents?.maxConcurrent;

  if (maxConcurrent === undefined || subMaxConcurrent === undefined) {
    addFinding(
      "info",
      "INFO-011",
      "Sub-agent concurrency limits not set",
      `agents.defaults.maxConcurrent=${maxConcurrent ?? "unset"}, subagents.maxConcurrent=${subMaxConcurrent ?? "unset"}. Without limits, runaway sub-agents can exhaust API quotas.`,
      `Set agents.defaults.maxConcurrent and agents.defaults.subagents.maxConcurrent in config`
    );
  }
}

// --- Run All Checks ---

function runAudit() {
  if (!JSON_OUTPUT) {
    console.log("\n🛡️  ClawAudit Config Auditor\n");
  }

  const loaded = loadConfig();

  if (!loaded) {
    if (!JSON_OUTPUT) {
      console.log("⚠️  No OpenClaw config file found. Checked:");
      CONFIG_PATHS.forEach((p) => console.log(`   ${p}`));
      console.log("\nRunning file permission checks only...\n");
    }
    auditCredentialFiles();
    auditCronJobs();
    auditPairedDevices();
  } else {
    if (!JSON_OUTPUT) {
      console.log(`📁 Config: ${loaded.path}\n`);
    }

    const cfg = loaded.config;
    auditGatewayExposure(cfg);
    auditDMPolicy(cfg);
    auditSandbox(cfg);
    auditBrowserControl(cfg);
    auditExecPolicy(cfg);
    auditSkillsAllowlist(cfg);
    auditCredentialFiles();
    auditCronJobs();
    auditPairedDevices();
    auditSubAgentLimits(cfg);
  }

  // --- Output ---
  const findings = collector.getAll();
  const counts = collector.countBySeverity();

  if (JSON_OUTPUT) {
    const summary = {
      critical: counts.critical,
      warnings: counts.warnings,
      info: counts.info,
      totalChecks: collector.getTotalChecks(),
      passed: collector.getPassed(),
      findings,
    };
    console.log(JSON.stringify(summary, null, 2));
    return;
  }

  if (findings.length === 0) {
    console.log("✅ No configuration issues found!\n");
    return;
  }

  const severityIcon = { critical: "🔴", warning: "🟡", info: "🔵" };
  const severityLabel = { critical: "CRITICAL", warning: "WARNING", info: "INFO" };

  // Sort: critical first
  collector.sort();

  for (const f of findings) {
    console.log(`${severityIcon[f.severity]} ${severityLabel[f.severity]}: ${f.code} — ${f.title}`);
    console.log(`   ${f.detail}`);
    if (SHOW_FIX && f.fix) {
      console.log(`   💡 Fix: ${f.fix}`);
    }
    console.log();
  }

  const { critical: crit, warnings: warn, info } = counts;

  console.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
  console.log(`📊 Audit Summary: ${crit} critical, ${warn} warnings, ${info} info`);
  if (!SHOW_FIX) {
    console.log("   Run with --fix to see remediation steps.");
  }
  console.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n");
}

runAudit();
