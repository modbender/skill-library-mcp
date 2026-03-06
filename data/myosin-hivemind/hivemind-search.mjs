#!/usr/bin/env node

import { parseArgs } from "node:util";
import { readFileSync } from "node:fs";
import { join } from "node:path";
import { homedir } from "node:os";

// ---------------------------------------------------------------------------
// Env resolution: process.env → .openclaw/.env → openclaw.json env object
// Only HIVEMIND_* keys are ever read from config files.
// ---------------------------------------------------------------------------

const ALLOWED_KEYS = new Set([
  "HIVEMIND_API_URL",
  "HIVEMIND_API_KEY",
  "HIVEMIND_VERCEL_BYPASS",
]);

function loadDotEnvKey(path, key) {
  try {
    const content = readFileSync(path, "utf-8");
    for (const line of content.split("\n")) {
      const trimmed = line.trim();
      if (!trimmed || trimmed.startsWith("#")) continue;
      const eq = trimmed.indexOf("=");
      if (eq === -1) continue;
      const k = trimmed.slice(0, eq).trim();
      if (k === key) return trimmed.slice(eq + 1).trim();
    }
    return null;
  } catch {
    return null;
  }
}

function loadOpenclawJsonEnvKey(path, key) {
  try {
    const json = JSON.parse(readFileSync(path, "utf-8"));
    if (json.env && typeof json.env === "object" && typeof json.env[key] === "string") {
      return json.env[key];
    }
    return null;
  } catch {
    return null;
  }
}

function resolveEnv(key) {
  if (!ALLOWED_KEYS.has(key)) return null;

  // 1. process.env (set by shell or OpenClaw runtime)
  if (process.env[key]) return process.env[key];

  const openclawDir = join(homedir(), ".openclaw");

  // 2. .openclaw/.env file — extract only the requested key
  const dotVal = loadDotEnvKey(join(openclawDir, ".env"), key);
  if (dotVal) return dotVal;

  // 3. openclaw.json → env object — extract only the requested key
  const jsonVal = loadOpenclawJsonEnvKey(join(openclawDir, "openclaw.json"), key);
  if (jsonVal) return jsonVal;

  return null;
}

// ---------------------------------------------------------------------------
// CLI args
// ---------------------------------------------------------------------------

const { values } = parseArgs({
  options: {
    query: { type: "string", short: "q" },
    persona: { type: "string", short: "p" },
    threshold: { type: "string", short: "t" },
    max: { type: "string", short: "m" },
    intent: { type: "boolean", default: false },
    objective: { type: "boolean", default: false },
    "no-rerank": { type: "boolean", default: false },
    "no-boost": { type: "boolean", default: false },
    raw: { type: "boolean", default: false },
    help: { type: "boolean", short: "h", default: false },
  },
  strict: true,
});

if (values.help || !values.query) {
  console.log(`Usage: hivemind-search --query <text> [options]

Options:
  -q, --query <text>        Search query (required)
  -p, --persona <id>        Persona: genius-strategist, gtm-architect, ghostwriter, general-assistant
  -t, --threshold <0-1>     Relevance threshold (default: 0.4)
  -m, --max <1-25>          Max results (default: 10)
      --intent              Enable intent filtering
      --objective           Enable objective filtering
      --no-rerank           Disable LLM reranking
      --no-boost            Disable metadata boosting
      --raw                 Output raw JSON response
  -h, --help                Show this help

Environment (checked in order):
  1. Shell environment variables
  2. ~/.openclaw/.env
  3. ~/.openclaw/openclaw.json → env object`);
  process.exit(values.help ? 0 : 1);
}

// ---------------------------------------------------------------------------
// Validate config
// ---------------------------------------------------------------------------

const VALID_PERSONAS = ["genius-strategist", "gtm-architect", "ghostwriter", "general-assistant"];

const url = resolveEnv("HIVEMIND_API_URL");
const apiKey = resolveEnv("HIVEMIND_API_KEY");
const bypass = resolveEnv("HIVEMIND_VERCEL_BYPASS");

if (!url || !apiKey || !bypass) {
  const missing = [];
  if (!url) missing.push("HIVEMIND_API_URL");
  if (!apiKey) missing.push("HIVEMIND_API_KEY");
  if (!bypass) missing.push("HIVEMIND_VERCEL_BYPASS");
  console.error(`Error: Missing: ${missing.join(", ")}`);
  console.error("Checked: process.env → ~/.openclaw/.env → ~/.openclaw/openclaw.json env");
  process.exit(1);
}

if (values.persona && !VALID_PERSONAS.includes(values.persona)) {
  console.error(`Error: Invalid persona "${values.persona}". Valid: ${VALID_PERSONAS.join(", ")}`);
  process.exit(1);
}

// ---------------------------------------------------------------------------
// Build request
// ---------------------------------------------------------------------------

const body = {
  query: values.query,
  relevanceThreshold: parseFloat(values.threshold ?? "0.4"),
  maxResults: parseInt(values.max ?? "10", 10),
  metadataBoosting: !values["no-boost"],
  reRanking: !values["no-rerank"],
};

if (values.persona) body.personaId = values.persona;
if (values.intent) body.intentFiltering = true;
if (values.objective) body.objectiveFiltering = true;

// ---------------------------------------------------------------------------
// Execute search
// ---------------------------------------------------------------------------

try {
  const res = await fetch(`${url}/api/knowledge/search`, {
    method: "POST",
    headers: {
      "x-api-key": apiKey,
      "x-vercel-protection-bypass": bypass,
      "Content-Type": "application/json",
    },
    body: JSON.stringify(body),
  });

  if (!res.ok) {
    const text = await res.text().catch(() => "");
    console.error(`Error: API returned ${res.status} ${res.statusText}`);
    if (text) console.error(text);
    process.exit(1);
  }

  const json = await res.json();

  if (values.raw) {
    console.log(JSON.stringify(json, null, 2));
    process.exit(0);
  }

  const chunks = json.data?.chunks ?? [];
  if (chunks.length === 0) {
    console.log("No results found.");
    process.exit(0);
  }

  console.log(`Found ${chunks.length} results (${json.data?.metrics?.searchTime ?? "?"}ms)\n`);

  for (const [i, chunk] of chunks.entries()) {
    const meta = [
      chunk.doc_type,
      chunk.objective,
      ...(chunk.industry ?? []),
      ...(chunk.channels ?? []),
    ].filter(Boolean).join(", ");

    console.log(`--- [${i + 1}] ${chunk.title ?? "Untitled"} (${chunk.relevance ?? chunk.score ?? "?"}) ---`);
    if (chunk.author) console.log(`Author: ${chunk.author}`);
    if (meta) console.log(`Meta: ${meta}`);
    console.log("");
    console.log(chunk.content ?? "(no content)");
    console.log("");
  }
} catch (err) {
  console.error(`Error: ${err.message}`);
  process.exit(1);
}
