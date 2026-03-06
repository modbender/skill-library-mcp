#!/usr/bin/env node
"use strict";

const fs = require("fs");

const CANDIDATES = [
  { label: "agents.defaults.memorySearch", path: ["agents", "defaults", "memorySearch"] },
  { label: "memorySearch", path: ["memorySearch"] },
  { label: "agents.memorySearch", path: ["agents", "memorySearch"] },
  { label: "agents.defaults.memory.search", path: ["agents", "defaults", "memory", "search"] },
  { label: "memory.search", path: ["memory", "search"] },
];

function getAt(obj, path) {
  let cur = obj;
  for (const key of path) {
    if (!cur || typeof cur !== "object" || !(key in cur)) return undefined;
    cur = cur[key];
  }
  return cur;
}

function ensureAt(obj, path) {
  let cur = obj;
  for (const key of path) {
    if (!cur[key] || typeof cur[key] !== "object" || Array.isArray(cur[key])) cur[key] = {};
    cur = cur[key];
  }
  return cur;
}

function resolveActive(cfg) {
  const canonical = CANDIDATES[0];
  const canonicalVal = getAt(cfg, canonical.path);
  if (canonicalVal && typeof canonicalVal === "object" && !Array.isArray(canonicalVal)) return canonical;
  for (const c of CANDIDATES.slice(1)) {
    const v = getAt(cfg, c.path);
    if (v && typeof v === "object" && !Array.isArray(v)) return c;
  }
  return canonical;
}

function resolveMs(cfg) {
  const active = resolveActive(cfg);
  return { active, ms: getAt(cfg, active.path) || {} };
}

function readConfig(path) {
  try {
    return JSON.parse(fs.readFileSync(path, "utf8"));
  } catch (_) {
    return {};
  }
}

function writeConfig(path, cfg) {
  fs.writeFileSync(path, JSON.stringify(cfg, null, 2));
}

function fingerprint(ms) {
  return {
    provider: ms.provider || "",
    model: ms.model || "",
    baseUrl: ms?.remote?.baseUrl || "",
    apiKeySet: !!(ms?.remote?.apiKey || ""),
  };
}

function usage() {
  process.stderr.write(
    "Usage:\n" +
      "  config.js resolve-model <configPath>\n" +
      "  config.js resolve-model-base <configPath>\n" +
      "  config.js fingerprint <configPath>\n" +
      "  config.js check-drift <configPath> <model> <baseUrl>\n" +
      "  config.js plan-enforce <configPath> <model> <baseUrl> <apiKey>\n" +
      "  config.js apply-enforce <configPath> <model> <baseUrl> <apiKey>\n" +
      "  config.js sanity <configPath>\n",
  );
}

function planEnforce(cfg, model, base, desiredApiKey) {
  const before = JSON.stringify(cfg);
  const canonical = CANDIDATES[0];
  const active = resolveActive(cfg);
  const targets = [canonical];
  if (active.label !== canonical.label) targets.push(active);
  for (const t of targets) {
    const ms = ensureAt(cfg, t.path);
    ms.provider = "openai";
    ms.model = model;
    ms.remote = ms.remote || {};
    ms.remote.baseUrl = base;
    if (!ms.remote.apiKey) ms.remote.apiKey = desiredApiKey;
  }
  const afterObj = getAt(cfg, canonical.path) || {};
  const changed = before !== JSON.stringify(cfg);
  return {
    changed,
    providerNow: afterObj.provider || "",
    modelNow: afterObj.model || "",
    baseNow: (afterObj.remote && afterObj.remote.baseUrl) || "",
    apiKeyNow: (afterObj.remote && afterObj.remote.apiKey) ? "(set)" : "(missing)",
    activePath: active.label,
    mirroringLegacy: active.label !== canonical.label ? "yes" : "no",
    cfg,
  };
}

const cmd = process.argv[2];
if (!cmd) {
  usage();
  process.exit(1);
}

try {
  if (cmd === "resolve-model") {
    const configPath = process.argv[3];
    if (!configPath) throw new Error("missing configPath");
    const cfg = readConfig(configPath);
    const { ms } = resolveMs(cfg);
    process.stdout.write(ms.model || "");
    process.exit(0);
  }

  if (cmd === "resolve-model-base") {
    const configPath = process.argv[3];
    if (!configPath) throw new Error("missing configPath");
    const cfg = readConfig(configPath);
    const { ms } = resolveMs(cfg);
    const model = ms.model || "";
    const base = (ms?.remote?.baseUrl || "http://127.0.0.1:11434/v1/").trim();
    process.stdout.write(`${model}\n${base}\n`);
    process.exit(0);
  }

  if (cmd === "fingerprint") {
    const configPath = process.argv[3];
    if (!configPath) throw new Error("missing configPath");
    const cfg = readConfig(configPath);
    const { ms } = resolveMs(cfg);
    process.stdout.write(JSON.stringify(fingerprint(ms)));
    process.exit(0);
  }

  if (cmd === "check-drift") {
    const configPath = process.argv[3];
    const model = process.argv[4] || "";
    const base = process.argv[5] || "";
    if (!configPath || !model || !base) throw new Error("missing required args");
    const cfg = readConfig(configPath);
    const { ms } = resolveMs(cfg);
    const apiKey = ms?.remote?.apiKey || "";
    const drift =
      ms.provider !== "openai" ||
      (ms.model || "") !== model ||
      (ms?.remote?.baseUrl || "") !== base ||
      apiKey === "";
    process.exit(drift ? 10 : 0);
  }

  if (cmd === "plan-enforce") {
    const configPath = process.argv[3];
    const model = process.argv[4] || "";
    const base = process.argv[5] || "";
    const apiKey = process.argv[6] || "";
    if (!configPath || !model || !base || !apiKey) throw new Error("missing required args");
    const cfg = readConfig(configPath);
    const plan = planEnforce(cfg, model, base, apiKey);
    process.stdout.write([
      plan.changed ? "changed" : "unchanged",
      plan.providerNow,
      plan.modelNow,
      plan.baseNow,
      plan.apiKeyNow,
      plan.activePath,
      plan.mirroringLegacy,
    ].join("\n") + "\n");
    process.exit(0);
  }

  if (cmd === "apply-enforce") {
    const configPath = process.argv[3];
    const model = process.argv[4] || "";
    const base = process.argv[5] || "";
    const apiKey = process.argv[6] || "";
    if (!configPath || !model || !base || !apiKey) throw new Error("missing required args");
    const cfg = readConfig(configPath);
    const plan = planEnforce(cfg, model, base, apiKey);
    writeConfig(configPath, plan.cfg);
    process.exit(0);
  }

  if (cmd === "sanity") {
    const configPath = process.argv[3];
    if (!configPath) throw new Error("missing configPath");
    const cfg = readConfig(configPath);
    const ms = cfg?.agents?.defaults?.memorySearch || {};
    const provider = ms.provider || "(missing)";
    const model = ms.model || "(missing)";
    const baseUrl = ms?.remote?.baseUrl || "(missing)";
    const apiKeySet = ms?.remote?.apiKey ? "(set)" : "(missing)";
    process.stdout.write(
      `provider:${provider}\n` +
        `model:${model}\n` +
        `baseUrl:${baseUrl}\n` +
        `apiKey:${apiKeySet}\n`,
    );
    if (ms.provider !== "openai" || !ms.model || !ms?.remote?.baseUrl) {
      if (ms.provider && ms.provider !== "openai") {
        process.stderr.write(
          "OpenClaw expects memorySearch.provider to be 'openai' for OpenAI-compatible endpoints (e.g. Ollama). " +
            "Other values (e.g. 'remote') cause config validation to fail. Run enforce.sh to fix.\n",
        );
      }
      process.exit(1);
    }
    process.exit(0);
  }

  usage();
  process.exit(1);
} catch (err) {
  process.stderr.write(`config.js error: ${err.message}\n`);
  process.exit(1);
}
