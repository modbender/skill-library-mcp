#!/usr/bin/env node
/**
 * patch-config.js — Merge social-media-ops agent configuration into openclaw.json
 *
 * Usage:
 *   node patch-config.js --config ~/.openclaw/openclaw.json
 *   node patch-config.js --config ~/.openclaw/openclaw.json --agents leader,content,designer,engineer
 *   node patch-config.js --dry-run --config ~/.openclaw/openclaw.json
 *
 * Options:
 *   --config PATH         Path to openclaw.json (required)
 *   --agents LIST         Comma-separated agent list (default: all 7)
 *   --base-dir DIR        OpenClaw root directory (default: ~/.openclaw)
 *   --ops-channel ID      Operations channel ID for cron job delivery (overrides auto-detection)
 *   --skip-qmd            Skip QMD memory setup even if available
 *   --force-qmd           Enable QMD memory even if binary not detected
 *   --dry-run             Print changes without writing
 *   --help                Show help
 */

const fs = require("fs");
const path = require("path");
const { execSync } = require("child_process");

// ── Defaults ──────────────────────────────────────────────────────────

const DEFAULT_AGENTS = [
  "leader",
  "researcher",
  "content",
  "designer",
  "operator",
  "engineer",
  "reviewer",
];

const AGENT_TOOL_DENY = {
  leader: ["exec", "apply_patch", "browser"],
  researcher: ["exec", "edit", "apply_patch", "browser"],
  content: ["exec", "edit", "apply_patch", "browser"],
  designer: ["edit", "apply_patch", "browser"],
  operator: ["exec", "edit", "apply_patch"],
  engineer: ["browser"],
  reviewer: ["exec", "edit", "apply_patch", "write", "browser"],
};

const AGENT_NAMES = {
  leader: "Leader",
  researcher: "Researcher",
  content: "Content",
  designer: "Designer",
  operator: "Operator",
  engineer: "Engineer",
  reviewer: "Reviewer",
};

// ── Argument Parsing ──────────────────────────────────────────────────

function parseArgs(argv) {
  const args = {
    config: null,
    agents: DEFAULT_AGENTS,
    baseDir: path.join(process.env.HOME || require("os").homedir(), ".openclaw"),
    skipQmd: false,
    forceQmd: false,
    dryRun: false,
  };

  for (let i = 2; i < argv.length; i++) {
    switch (argv[i]) {
      case "--config":
        args.config = argv[++i];
        break;
      case "--agents":
        args.agents = argv[++i].split(",").map((s) => s.trim());
        break;
      case "--base-dir":
        args.baseDir = argv[++i];
        break;
      case "--skip-qmd":
        args.skipQmd = true;
        break;
      case "--force-qmd":
        args.forceQmd = true;
        break;
      case "--dry-run":
        args.dryRun = true;
        break;
      case "--help":
      case "-h":
        console.log(
          "Usage: node patch-config.js --config <path> [--agents <list>] [--base-dir <dir>] [--ops-channel <id>] [--skip-qmd] [--force-qmd] [--dry-run]"
        );
        process.exit(0);
      default:
        console.error(`[ERROR] Unknown option: ${argv[i]}`);
        process.exit(1);
    }
  }

  if (!args.config) {
    console.error("[ERROR] --config is required");
    process.exit(1);
  }

  // Validate leader is included
  if (!args.agents.includes("leader")) {
    console.error("[ERROR] Leader agent is required");
    process.exit(1);
  }

  return args;
}

// ── QMD Detection ────────────────────────────────────────────────────

function isQmdAvailable() {
  try {
    execSync("which qmd", { stdio: "ignore" });
    return true;
  } catch {
    return false;
  }
}

// ── Deep Merge ────────────────────────────────────────────────────────

function deepMerge(target, source) {
  const result = { ...target };
  for (const key of Object.keys(source)) {
    if (
      source[key] &&
      typeof source[key] === "object" &&
      !Array.isArray(source[key]) &&
      target[key] &&
      typeof target[key] === "object" &&
      !Array.isArray(target[key])
    ) {
      result[key] = deepMerge(target[key], source[key]);
    } else {
      result[key] = source[key];
    }
  }
  return result;
}

// ── Build Agent Entry ─────────────────────────────────────────────────

function buildAgentEntry(agentId, args) {
  const wsDir =
    agentId === "leader" ? "workspace" : `workspace-${agentId}`;
  const entry = {
    id: agentId,
    name: AGENT_NAMES[agentId] || agentId,
    workspace: path.join(args.baseDir, wsDir),
    // No model key — inherits from agents.defaults.model (set during onboard)
    tools: {
      deny: AGENT_TOOL_DENY[agentId] || [],
    },
  };

  // Leader is the default agent
  if (agentId === "leader") {
    entry.default = true;
    // Identity will be filled during instance-setup
    entry.identity = { name: "Assistant", emoji: "🤖" };
  }

  // Reviewer gets sandbox
  if (agentId === "reviewer") {
    entry.sandbox = { mode: "non-main", scope: "session" };
  }

  return entry;
}

// ── Patch Config ──────────────────────────────────────────────────────

function patchConfig(config, args) {
  const patched = { ...config };

  // ── Ensure agents section exists ──
  if (!patched.agents) {
    patched.agents = {};
  }

  // ── Set agent defaults ──
  patched.agents.defaults = deepMerge(patched.agents.defaults || {}, {
    compaction: { mode: "safeguard" },
    bootstrapMaxChars: 30000,
    timeoutSeconds: 1800,
    maxConcurrent: 4,
    subagents: { maxConcurrent: 8 },
    heartbeat: { directPolicy: "allow" },
  });

  // ── Clean stale fields from defaults ──
  // These cause an implicit "Main" agent alongside the explicit Leader.
  // The default agent is determined by agents.list[].default, not agents.defaults.workspace.
  delete patched.agents.defaults.workspace;
  delete patched.agents.defaults.models;

  // ── Build agent list ──
  const existingList = patched.agents.list || [];
  const existingIds = new Set(existingList.map((a) => a.id));
  const newEntries = [];

  for (const agentId of args.agents) {
    if (!existingIds.has(agentId)) {
      newEntries.push(buildAgentEntry(agentId, args));
      console.log(`[ADD]  Agent: ${agentId}`);
    } else {
      console.log(`[SKIP] Agent: ${agentId} (already exists)`);
    }
  }

  patched.agents.list = [...existingList, ...newEntries];

  // ── Set A2A configuration ──
  if (!patched.tools) patched.tools = {};
  patched.tools.agentToAgent = {
    enabled: true,
    allow: [...args.agents],
  };
  patched.tools.sessions = { visibility: "all" };
  console.log("[SET]  tools.agentToAgent");

  // v2026.2.24+ restricts safe-bin trusted dirs to /bin, /usr/bin only.
  // Designer and Engineer need Homebrew paths for exec (uv run, CLI tools).
  if (!patched.tools.exec) patched.tools.exec = {};
  if (!patched.tools.exec.safeBinTrustedDirs) {
    patched.tools.exec.safeBinTrustedDirs = [
      "/bin",
      "/usr/bin",
      "/opt/homebrew/bin",
      "/usr/local/bin",
    ];
    console.log(
      "[SET]  tools.exec.safeBinTrustedDirs (Homebrew paths for Designer/Engineer exec)"
    );
  }

  // ── Set session configuration ──
  if (!patched.session) patched.session = {};
  patched.session.agentToAgent = { maxPingPongTurns: 3 };
  if (!patched.session.parentForkMaxTokens) {
    patched.session.parentForkMaxTokens = 100000;
  }
  console.log("[SET]  session.agentToAgent.maxPingPongTurns: 3");
  console.log("[SET]  session.parentForkMaxTokens: 100000");

  // ── Set memory (QMD if available, skip if not) ──
  if (args.skipQmd) {
    console.log("[SKIP] QMD memory (--skip-qmd flag)");
  } else if (args.forceQmd || isQmdAvailable()) {
    patched.memory = deepMerge(patched.memory || {}, {
      backend: "qmd",
      qmd: {
        includeDefaultMemory: true,
        paths: [
          { path: "memory", name: "daily-notes", pattern: "**/*.md" },
          { path: "skills", name: "agent-skills", pattern: "**/*.md" },
          { path: "shared", name: "shared-knowledge", pattern: "**/*.md" },
        ],
        update: { interval: "5m" },
      },
    });
    if (args.forceQmd) {
      console.log("[SET]  memory.qmd paths (--force-qmd)");
    } else {
      console.log("[SET]  memory.qmd paths (qmd detected)");
    }
  } else {
    console.log("[SKIP] QMD memory (qmd binary not found)");
    console.log("[TIP]  For enhanced semantic search memory, install QMD:");
    console.log("       bun install -g @tobilu/qmd");
    console.log("       Then re-run this script, or use the qmd-setup skill.");
  }

  // ── Set hooks ──
  patched.hooks = deepMerge(patched.hooks || {}, {
    internal: {
      enabled: true,
      entries: {
        "boot-md": { enabled: true },
        "bootstrap-extra-files": { enabled: true },
        "command-logger": { enabled: true },
        "session-memory": { enabled: true },
      },
    },
  });
  console.log("[SET]  hooks.internal entries");

  // ── Set message settings ──
  if (!patched.messages) patched.messages = {};
  if (!patched.messages.ackReactionScope) {
    patched.messages.ackReactionScope = "all";
    console.log("[SET]  messages.ackReactionScope: all");
  }

  // ── Set commands ──
  patched.commands = deepMerge(patched.commands || {}, {
    native: "auto",
    nativeSkills: "auto",
    restart: true,
  });

  return patched;
}

// ── Cron Merge ────────────────────────────────────────────────────────

function patchCron(args) {
  const skillDir = path.dirname(__dirname);
  const cronTemplatePath = path.join(skillDir, "assets", "config", "cron-jobs.json");

  if (!fs.existsSync(cronTemplatePath)) {
    console.log("[SKIP] No cron-jobs.json template found in assets/config/");
    return;
  }

  const cronDir = path.join(args.baseDir, "cron");
  const cronPath = path.join(cronDir, "jobs.json");

  // Read template
  const template = JSON.parse(fs.readFileSync(cronTemplatePath, "utf8"));
  const templateJobs = template.jobs || [];

  if (templateJobs.length === 0) {
    console.log("[SKIP] Cron template has no jobs");
    return;
  }

  // Read existing cron jobs (or start fresh)
  let existing = { version: 1, jobs: [] };
  if (fs.existsSync(cronPath)) {
    existing = JSON.parse(fs.readFileSync(cronPath, "utf8"));
  }
  const existingIds = new Set((existing.jobs || []).map((j) => j.id));

  // Resolve operations channel placeholder
  let opsChannel = null;

  // Check CLI arg
  const opsIdx = process.argv.indexOf("--ops-channel");
  if (opsIdx !== -1 && process.argv[opsIdx + 1]) {
    opsChannel = process.argv[opsIdx + 1];
  }

  // Fallback: read from openclaw.json groups config
  if (!opsChannel && args.config && fs.existsSync(args.config)) {
    try {
      const config = JSON.parse(fs.readFileSync(args.config, "utf8"));
      const groups = config?.channels?.telegram?.groups;
      if (Array.isArray(groups) && groups.length > 0) {
        opsChannel = groups[0].chatId || groups[0].id || null;
      }
    } catch {}
  }

  // Merge missing jobs
  const newJobs = [];
  for (const job of templateJobs) {
    if (!existingIds.has(job.id)) {
      // Replace placeholder in delivery channel
      const jobCopy = JSON.parse(JSON.stringify(job));
      if (opsChannel) {
        const raw = JSON.stringify(jobCopy);
        const replaced = raw.replace(/\{\{OPERATIONS_CHANNEL\}\}/g, opsChannel);
        newJobs.push(JSON.parse(replaced));
      } else {
        newJobs.push(jobCopy);
        if (JSON.stringify(jobCopy).includes("{{OPERATIONS_CHANNEL}}")) {
          console.log(
            "[WARN] Cron job contains {{OPERATIONS_CHANNEL}} placeholder. Use --ops-channel or configure channels.telegram.groups in openclaw.json."
          );
        }
      }
      console.log(`[ADD]  Cron job: ${job.id}`);
    } else {
      console.log(`[SKIP] Cron job: ${job.id} (already exists)`);
    }
  }

  if (newJobs.length === 0) {
    console.log("[OK]   All cron jobs already present");
    return;
  }

  const merged = {
    ...existing,
    jobs: [...(existing.jobs || []), ...newJobs],
  };

  if (args.dryRun) {
    console.log("[DRY RUN] Would write cron/jobs.json:");
    console.log(JSON.stringify(merged, null, 2));
    return;
  }

  // Backup existing cron file
  if (fs.existsSync(cronPath)) {
    const backupPath = cronPath + ".backup-" + Date.now();
    fs.copyFileSync(cronPath, backupPath);
    console.log(`[OK]   Cron backup: ${backupPath}`);
  }

  if (!fs.existsSync(cronDir)) {
    fs.mkdirSync(cronDir, { recursive: true });
  }

  fs.writeFileSync(cronPath, JSON.stringify(merged, null, 2) + "\n");
  console.log(`[OK]   Written: ${cronPath}`);
}

// ── Main ──────────────────────────────────────────────────────────────

function main() {
  const args = parseArgs(process.argv);

  console.log(`[INFO] Config: ${args.config}`);
  console.log(`[INFO] Agents: ${args.agents.join(", ")}`);
  console.log(`[INFO] Base dir: ${args.baseDir}`);
  if (args.dryRun) console.log("[INFO] DRY RUN — no changes will be written");
  console.log("");

  // Read existing config
  let config = {};
  if (fs.existsSync(args.config)) {
    const raw = fs.readFileSync(args.config, "utf8");
    config = JSON.parse(raw);
    console.log("[OK]   Read existing openclaw.json");
  } else {
    console.log("[INFO] No existing openclaw.json — creating new");
  }

  // Apply patches
  const patched = patchConfig(config, args);

  // Write result
  if (args.dryRun) {
    console.log("\n[DRY RUN] Would write:");
    console.log(JSON.stringify(patched, null, 2));
  } else {
    // Backup original
    if (fs.existsSync(args.config)) {
      const backupPath = args.config + ".backup-" + Date.now();
      fs.copyFileSync(args.config, backupPath);
      console.log(`\n[OK]   Backup: ${backupPath}`);
    }

    fs.writeFileSync(args.config, JSON.stringify(patched, null, 2) + "\n");
    console.log(`[OK]   Written: ${args.config}`);
  }

  // Merge cron jobs
  console.log("");
  patchCron(args);

  console.log("\n[OK]   Config patching complete");
  console.log("\nNext steps:");
  console.log("  1. openclaw gateway restart");
  console.log(
    "  2. openclaw doctor           (validate config + DM allowlist inheritance)"
  );
  console.log(
    "  3. openclaw secrets audit    (optional: check for plaintext secrets)"
  );
}

main();
