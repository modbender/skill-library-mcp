#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const ROOT = path.resolve(__dirname, "..");
const STATE_DIR = path.join(ROOT, "state");
const CFG_PATH = path.join(STATE_DIR, "spawn-profiles.json");
const LOG_PATH = path.join(STATE_DIR, "build-log.jsonl");

function usage() {
  console.error(`Build sessions_spawn payload from local JSON profiles\n\n` +
`Usage:\n` +
`  node scripts/build_spawn_payload.mjs --profile <name> --task <text> [options]\n\n` +
`Options:\n` +
`  --profile <name>              profile key in state/spawn-profiles.json (required)\n` +
`  --task <text>                 task text for subagent (required)\n` +
`  --label <text>                sessions_spawn.label\n` +
`  --agent-id <id>               sessions_spawn.agentId\n` +
`  --model <name>                sessions_spawn.model\n` +
`  --thinking <value>            sessions_spawn.thinking\n` +
`  --run-timeout-seconds <int>   sessions_spawn.runTimeoutSeconds\n` +
`  --cleanup <keep|delete>       sessions_spawn.cleanup\n` +
`  -h, --help                    show this help\n`);
}

function parseArgs(argv) {
  const out = {
    profile: "",
    task: "",
    label: "",
    agentId: "",
    model: "",
    thinking: "",
    runTimeoutSeconds: undefined,
    cleanup: "",
  };

  const map = new Map([
    ["--profile", "profile"],
    ["--task", "task"],
    ["--label", "label"],
    ["--agent-id", "agentId"],
    ["--model", "model"],
    ["--thinking", "thinking"],
    ["--run-timeout-seconds", "runTimeoutSeconds"],
    ["--cleanup", "cleanup"],
  ]);

  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === "-h" || a === "--help") {
      usage();
      process.exit(0);
    }

    if (!map.has(a)) {
      throw new Error(`Unknown option: ${a}`);
    }

    const key = map.get(a);
    const val = argv[i + 1];
    if (val == null || val.startsWith("--")) {
      throw new Error(`Missing value for ${a}`);
    }
    i += 1;

    if (key === "runTimeoutSeconds") {
      const n = Number.parseInt(val, 10);
      if (!Number.isFinite(n)) throw new Error(`Invalid integer for ${a}: ${val}`);
      out[key] = n;
    } else {
      out[key] = val;
    }
  }

  if (!out.profile) throw new Error("--profile is required");
  if (!out.task) throw new Error("--task is required");
  if (out.cleanup && !["keep", "delete"].includes(out.cleanup)) {
    throw new Error(`--cleanup must be keep|delete, got: ${out.cleanup}`);
  }

  return out;
}

function loadCfg() {
  if (!fs.existsSync(CFG_PATH)) {
    const templatePath = path.join(STATE_DIR, "spawn-profiles.template.json");
    throw new Error(`Missing config: ${CFG_PATH}\nCreate it from template: ${templatePath}`);
  }
  return JSON.parse(fs.readFileSync(CFG_PATH, "utf8"));
}

function pick(cliVal, profile, defaults, key) {
  if (cliVal !== undefined && cliVal !== null && cliVal !== "") return cliVal;
  if (Object.hasOwn(profile, key) && profile[key] !== undefined && profile[key] !== null && profile[key] !== "") return profile[key];
  return defaults[key];
}

function main() {
  const args = parseArgs(process.argv.slice(2));
  const cfg = loadCfg();

  const profile = (cfg.profiles || {})[args.profile];
  if (!profile) throw new Error(`Unknown profile: ${args.profile}`);
  const defaults = cfg.defaults || {};

  const payload = { task: args.task };

  const label = pick(args.label, profile, defaults, "label");
  payload.label = (label !== undefined && label !== null && label !== "")
    ? label
    : `${args.profile}-${Math.floor(Date.now() / 1000)}`;

  const agentId = pick(args.agentId, profile, defaults, "agentId");
  if (agentId !== undefined && agentId !== null && agentId !== "") payload.agentId = agentId;

  const model = pick(args.model, profile, defaults, "model");
  if (model !== undefined && model !== null && model !== "" && model !== "<set-by-user>") payload.model = model;

  const thinking = pick(args.thinking, profile, defaults, "thinking");
  if (thinking !== undefined && thinking !== null && thinking !== "") payload.thinking = thinking;

  const rts = pick(args.runTimeoutSeconds, profile, defaults, "runTimeoutSeconds");
  if (rts !== undefined && rts !== null && rts !== "") payload.runTimeoutSeconds = Number.parseInt(String(rts), 10);

  const cleanup = pick(args.cleanup, profile, defaults, "cleanup");
  if (cleanup !== undefined && cleanup !== null && cleanup !== "") payload.cleanup = cleanup;

  fs.mkdirSync(STATE_DIR, { recursive: true });
  const logLine = JSON.stringify({ ts: Math.floor(Date.now() / 1000), profile: args.profile, payload }, null, 0) + "\n";
  fs.appendFileSync(LOG_PATH, logLine, "utf8");

  process.stdout.write(JSON.stringify(payload, null, 2) + "\n");
}

try {
  main();
} catch (err) {
  console.error(err instanceof Error ? err.message : String(err));
  process.exit(1);
}
