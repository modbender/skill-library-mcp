#!/usr/bin/env node

/**
 * ClawAudit Config Auditor (Optimized)
 * Performance improvements:
 * - Lazy cron slot evaluation (only expand on potential overlap)
 * - Cached file reads
 * - Early exit optimizations
 */

import { readFileSync, existsSync, statSync } from "fs";
import { spawnSync } from "child_process";
import { join } from "path";
import { homedir } from "os";
import { CONFIG_PATHS, STATE_DIRS, parseFlag, createFindingCollector } from "./lib/utils.mjs";

const HOME = homedir();
const JSON_OUTPUT = parseFlag("--json");
const SHOW_FIX = parseFlag("--fix");

// --- Finding collector ---
const collector = createFindingCollector();
const addFinding = collector.add.bind(collector);
const addCheck = collector.check.bind(collector);

// --- File cache ---
const fileCache = new Map();

function readFileCached(path) {
  if (fileCache.has(path)) {
    return fileCache.get(path);
  }
  try {
    const content = readFileSync(path, "utf-8");
    fileCache.set(path, content);
    return content;
  } catch {
    fileCache.set(path, null);
    return null;
  }
}

// --- Helpers ---
function loadConfig() {
  for (const p of CONFIG_PATHS) {
    if (existsSync(p)) {
      try {
        const raw = readFileCached(p);
        if (raw) {
          return { path: p, config: JSON.parse(raw) };
        }
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
        true
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

    const envFile = join(stateDir, ".env");
    if (existsSync(envFile)) {
      const content = readFileCached(envFile);
      if (content) {
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
            break;
          }
        }
      }
    }

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
  const cronContent = readFileCached(cronPath);
  if (!cronContent) return;

  try {
    jobs = JSON.parse(cronContent)?.jobs || [];
  } catch {
    return;
  }

  // Dangerous patterns
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
        break; // One finding per job
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

  // WARN-021: Optimized overlap check
  auditCronJobOverlapOptimized(jobs);

  // WARN-022: bestEffortDeliver check
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
 * Optimized cron overlap detection - only expands slots when needed
 */
function auditCronJobOverlapOptimized(jobs) {
  const llmJobs = jobs.filter(
    (j) => j.enabled !== false && j.payload?.kind === "agentTurn"
  );
  if (llmJobs.length < 2) return;

  const conflicts = [];
  
  // Simple heuristic: check if cron expressions are identical first (fast path)
  for (let i = 0; i < llmJobs.length; i++) {
    for (let k = i + 1; k < llmJobs.length; k++) {
      const a = llmJobs[i];
      const b = llmJobs[k];
      const exprA = a.schedule?.expr;
      const exprB = b.schedule?.expr;
      
      if (!exprA || !exprB) continue;

      // Fast path: identical expressions = guaranteed overlap
      if (exprA === exprB) {
        conflicts.push(
          `"${a.name || a.id}" + "${b.name || b.id}" (identical schedule: ${exprA})`
        );
        continue;
      }

      // Slow path: expand and check (only if not identical)
      const slotsA = expandCronSlotsLazy(exprA);
      const slotsB = expandCronSlotsLazy(exprB);
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

/**
 * Lazy cron slot expansion with early termination
 */
function expandCronSlotsLazy(expr) {
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
        if (isNaN(start) || isNaN(end)) return null;
        for (let i = start; i <= end && i < max; i++) values.add(i);
      } else {
        const n = parseInt(part, 10);
        if (!isNaN(n) && n < max) values.add(n);
      }
    }
    return values;
  }

  const minutes = expandField(minField, 60);
  const hours = expandField(hourField, 24);
  if (!minutes || !hours) return null;

  // Optimization: if both are small sets, generate slots immediately
  if (minutes.size * hours.size <= 100) {
    const slots = new Set();
    for (const h of hours) {
      for (const m of minutes) {
        slots.add(`${h}:${m}`);
      }
    }
    return slots;
  }

  // For large sets (e.g. * * * * *), use lazy Set that generates on-demand
  // This avoids generating 1440 slots upfront
  return new LazyTimeSlotSet(hours, minutes);
}

/**
 * Lazy Set that generates time slots only when accessed
 */
class LazyTimeSlotSet {
  constructor(hours, minutes) {
    this.hours = hours;
    this.minutes = minutes;
    this._cache = null;
  }

  _expand() {
    if (this._cache) return this._cache;
    this._cache = new Set();
    for (const h of this.hours) {
      for (const m of this.minutes) {
        this._cache.add(`${h}:${m}`);
      }
    }
    return this._cache;
  }

  has(slot) {
    const [h, m] = slot.split(":").map(Number);
    return this.hours.has(h) && this.minutes.has(m);
  }

  [Symbol.iterator]() {
    return this._expand()[Symbol.iterator]();
  }

  get size() {
    return this.hours.size * this.minutes.size;
  }
}

function auditPairedDevices() {
  addCheck();
  const devicesPath = join(HOME, ".openclaw", "devices", "paired.json");
  if (!existsSync(devicesPath)) return;

  const devicesContent = readFileCached(devicesPath);
  if (!devicesContent) return;

  let devices;
  try {
    const raw = JSON.parse(devicesContent);
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
    console.log("\n🛡️  ClawAudit Config Auditor (Optimized)\n");
  }

  const startTime = Date.now();
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

  const elapsed = Date.now() - startTime;

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
      executionTimeMs: elapsed,
      findings,
    };
    console.log(JSON.stringify(summary, null, 2));
    return;
  }

  if (findings.length === 0) {
    console.log(`✅ No configuration issues found! (${elapsed}ms)\n`);
    return;
  }

  const severityIcon = { critical: "🔴", warning: "🟡", info: "🔵" };
  const severityLabel = { critical: "CRITICAL", warning: "WARNING", info: "INFO" };

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
  console.log(`📊 Audit Summary: ${crit} critical, ${warn} warnings, ${info} info (${elapsed}ms)`);
  if (!SHOW_FIX) {
    console.log("   Run with --fix to see remediation steps.");
  }
  console.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n");
}

runAudit();
