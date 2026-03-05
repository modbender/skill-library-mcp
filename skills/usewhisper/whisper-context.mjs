#!/usr/bin/env node
// whisper-context.mjs
// Minimal helper for OpenClaw skills (Node 18+). No curl, no extra packages.

import { readFile } from "node:fs/promises";

const API_URL_DEFAULT = process.env.WHISPER_CONTEXT_API_URL || "https://context.usewhisper.dev";
const API_KEY = process.env.WHISPER_CONTEXT_API_KEY || "";
const PROJECT_DEFAULT = process.env.WHISPER_CONTEXT_PROJECT || "";

const args = process.argv.slice(2);
const cmd = args[0] || "";
const flags = parseFlags(args.slice(1));

class HttpError extends Error {
  constructor(status, text, json) {
    super(`HTTP ${status}: ${text}`);
    this.name = "HttpError";
    this.status = status;
    this.text = text;
    this.json = json;
  }
}

async function main() {
  if (!cmd || cmd === "help" || flags.help === "true") {
    printHelp();
    return;
  }

  if (!API_KEY) {
    throw new Error("Missing WHISPER_CONTEXT_API_KEY");
  }
  const apiUrl = flags.api_url || API_URL_DEFAULT;
  const project = flags.project || PROJECT_DEFAULT;
  if (!project) throw new Error("Missing WHISPER_CONTEXT_PROJECT (or pass --project)");

  if (cmd === "query_context") {
    const query = flags.query || "";
    if (!query) throw new Error("Missing --query");

    const body = {
      project,
      query,
      top_k: num(flags.top_k, 6),
      include_memories: bool(flags.include_memories, true),
      include_graph: bool(flags.include_graph, false),
      compress: bool(flags.compress, true),
      compression_strategy: flags.compression_strategy || "delta",
      use_cache: bool(flags.use_cache, true),
      user_id: flags.user_id || undefined,
      session_id: flags.session_id || undefined,
      previous_context_hash: flags.previous_context_hash || undefined,
      max_tokens: flags.max_tokens ? num(flags.max_tokens) : undefined,
    };

    const res = await withAutoProject({ apiUrl, project }, () => post(apiUrl, "/v1/context/query", body, { retry: true }));
    console.log(JSON.stringify(res, null, 2));
    return;
  }

  if (cmd === "ingest_session") {
    const session_id = flags.session_id || "";
    if (!session_id) throw new Error("Missing --session_id");

    let user;
    let assistant;
    if (flags.turn_json) {
      const turn = await readJsonInput(flags.turn_json);
      user = String(turn.user || "");
      assistant = String(turn.assistant || "");
      if (!user) throw new Error("turn_json missing 'user'");
      if (!assistant) throw new Error("turn_json missing 'assistant'");
    } else {
      user = await readTextInput(flags.user || "");
      assistant = await readTextInput(flags.assistant || "");
      if (!user) throw new Error("Missing --user (or pass --turn_json)");
      if (!assistant) throw new Error("Missing --assistant (or pass --turn_json)");
    }

    const now = new Date();
    const body = {
      project,
      session_id,
      user_id: flags.user_id || undefined,
      messages: [
        { role: "user", content: user, timestamp: new Date(now.getTime() - 5_000).toISOString() },
        { role: "assistant", content: assistant, timestamp: now.toISOString() },
      ],
    };

    const res = await withAutoProject({ apiUrl, project }, () => post(apiUrl, "/v1/memory/ingest/session", body));
    console.log(JSON.stringify(res, null, 2));
    return;
  }

  if (cmd === "memory_write") {
    const content = await readTextInput(flags.content || "");
    if (!content) throw new Error("Missing --content");

    const body = {
      project,
      content,
      memory_type: flags.memory_type || "factual",
      user_id: flags.user_id || undefined,
      session_id: flags.session_id || undefined,
      agent_id: flags.agent_id || undefined,
      importance: flags.importance ? num(flags.importance) : undefined,
      confidence: flags.confidence ? num(flags.confidence) : undefined,
      metadata: flags.metadata ? safeJsonParse(flags.metadata) : undefined,
      entity_mentions: flags.entity_mentions ? csv(flags.entity_mentions) : undefined,
      document_date: flags.document_date || undefined,
      event_date: flags.event_date || undefined,
    };

    const res = await withAutoProject({ apiUrl, project }, () => post(apiUrl, "/v1/memory", body));
    console.log(JSON.stringify(res, null, 2));
    return;
  }

  if (cmd === "memory_search") {
    const query = flags.query || "";
    if (!query) throw new Error("Missing --query");

    const body = {
      project,
      query,
      user_id: flags.user_id || undefined,
      session_id: flags.session_id || undefined,
      question_date: flags.question_date || undefined,
      top_k: flags.top_k ? num(flags.top_k) : undefined,
      memory_types: flags.memory_types ? csv(flags.memory_types) : undefined,
      include_inactive: flags.include_inactive ? bool(flags.include_inactive) : undefined,
      include_chunks: flags.include_chunks ? bool(flags.include_chunks) : undefined,
      include_relations: flags.include_relations ? bool(flags.include_relations) : undefined,
    };

    const res = await withAutoProject({ apiUrl, project }, () => post(apiUrl, "/v1/memory/search", body, { retry: true }));
    console.log(JSON.stringify(res, null, 2));
    return;
  }

  if (cmd === "oracle_search") {
    const query = flags.query || "";
    if (!query) throw new Error("Missing --query");

    const body = {
      project,
      query,
      mode: flags.mode || "search",
      max_results: flags.max_results ? num(flags.max_results) : undefined,
      max_steps: flags.max_steps ? num(flags.max_steps) : undefined,
    };

    const res = await withAutoProject({ apiUrl, project }, () => post(apiUrl, "/v1/oracle/search", body, { retry: true }));
    console.log(JSON.stringify(res, null, 2));
    return;
  }

  if (cmd === "get_cost_summary") {
    const start_date = flags.start_date || undefined;
    const end_date = flags.end_date || undefined;

    const qs = new URLSearchParams();
    qs.set("project", project);
    if (start_date) qs.set("start_date", start_date);
    if (end_date) qs.set("end_date", end_date);

    const res = await withAutoProject({ apiUrl, project }, () => get(apiUrl, `/v1/cost/summary?${qs.toString()}`, { retry: true }));
    console.log(JSON.stringify(res, null, 2));
    return;
  }

  if (cmd === "cache_stats") {
    const res = await get(apiUrl, "/v1/cache/stats", { retry: true });
    console.log(JSON.stringify(res, null, 2));
    return;
  }

  if (cmd === "cache_warm") {
    const ttl_seconds = flags.ttl_seconds ? num(flags.ttl_seconds) : undefined;
    let queries = [];
    if (flags.queries_json) {
      const v = await readJsonInput(flags.queries_json);
      if (!Array.isArray(v)) throw new Error("queries_json must be a JSON array of strings");
      queries = v.map((s) => String(s));
    } else if (flags.queries) {
      queries = csv(flags.queries);
    }
    if (queries.length === 0) throw new Error("Missing --queries (comma-separated) or --queries_json");

    const body = {
      project,
      queries,
      ttl_seconds,
    };

    const res = await withAutoProject({ apiUrl, project }, () => post(apiUrl, "/v1/cache/warm", body));
    console.log(JSON.stringify(res, null, 2));
    return;
  }

  throw new Error(`Unknown command: ${cmd}`);
}

function printHelp() {
  const text = [
    "whisper-context.mjs",
    "",
    "Env:",
    "  WHISPER_CONTEXT_API_KEY (required)",
    "  WHISPER_CONTEXT_PROJECT (required)",
    "  WHISPER_CONTEXT_API_URL (optional, default https://context.usewhisper.dev)",
    "",
    "Global flags:",
    "  --project <slugOrName>   (overrides WHISPER_CONTEXT_PROJECT)",
    "  --api_url <url>         (overrides WHISPER_CONTEXT_API_URL)",
    "  --timeout_ms <n>        (default 30000)",
    "",
    "Commands:",
    "  query_context   --query <text> [--user_id <id>] [--session_id <id>]",
    "  ingest_session  --user <text> --assistant <text> --session_id <id> [--user_id <id>]",
    "                 or: --turn_json <json|@file|-> (stdin JSON: {\"user\":\"...\",\"assistant\":\"...\"})",
    "  memory_write    --content <text> [--memory_type factual|preference|...] [--user_id <id>]",
    "                 (content can be @file or - for stdin)",
    "  memory_search   --query <text> [--user_id <id>] [--top_k 10] [--memory_types factual,preference]",
    "  oracle_search   --query <text> [--mode search|research] [--max_results 5] [--max_steps 5]",
    "  get_cost_summary [--start_date <ISO>] [--end_date <ISO>]",
    "  cache_stats",
    "  cache_warm     --queries \"q1,q2\" [--ttl_seconds 3600]",
    "",
    "Examples:",
    "  node whisper-context.mjs query_context --query \"...\" --user_id user-123 --session_id sess-123",
    "  node whisper-context.mjs ingest_session --user \"...\" --assistant \"...\" --session_id sess-123 --user_id user-123",
  ].join("\n");
  console.log(text);
}

function getTimeoutMs() {
  return num(flags.timeout_ms, 30_000);
}

async function fetchWithTimeout(url, init) {
  const timeoutMs = getTimeoutMs();
  const controller = new AbortController();
  const t = setTimeout(() => controller.abort(), timeoutMs);
  try {
    const r = await fetch(url, { ...init, signal: controller.signal });
    return r;
  } finally {
    clearTimeout(t);
  }
}

async function post(apiUrl, path, body, options = {}) {
  return requestJson(`${apiUrl}${path}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${API_KEY}`,
    },
    body: JSON.stringify(body),
  }, options);
}

async function get(apiUrl, path, options = {}) {
  return requestJson(`${apiUrl}${path}`, {
    method: "GET",
    headers: {
      Authorization: `Bearer ${API_KEY}`,
    },
  }, options);
}

async function requestJson(url, init, options = {}) {
  const retry = !!options.retry;
  const maxRetries = num(options.max_retries, 2);

  for (let attempt = 0; ; attempt++) {
    const r = await fetchWithTimeout(url, init);
    const text = await r.text();

    let json;
    try {
      json = JSON.parse(text);
    } catch {
      json = { raw: text };
    }

    if (r.ok) return json;

    const err = new HttpError(r.status, text, json);
    const retryable = r.status === 429 || r.status >= 500;

    if (!retry || !retryable || attempt >= maxRetries) throw err;

    const retryAfter = parseRetryAfterMs(r.headers?.get?.("retry-after"));
    const backoffMs = retryAfter ?? Math.min(2000, 250 * Math.pow(2, attempt));
    await sleep(backoffMs);
  }
}

function sleep(ms) {
  return new Promise((r) => setTimeout(r, ms));
}

function parseRetryAfterMs(v) {
  if (!v) return null;
  const n = Number(v);
  if (Number.isFinite(n) && n >= 0) return Math.round(n * 1000);
  return null;
}

let autoProjectEnsured = false;

function looksLikeProjectNotFound(err) {
  if (!(err instanceof HttpError)) return false;
  if (err.status !== 404) return false;
  const msg = (typeof err.json?.error === "string" ? err.json.error : "") || err.text || "";
  return /project not found/i.test(msg);
}

async function ensureProjectExistsOnce({ apiUrl, project }) {
  if (autoProjectEnsured) return;
  autoProjectEnsured = true;

  // Context API upserts on (orgId, slugified(name)) for POST /v1/projects.
  const body = {
    name: project,
    description: "Auto-provisioned by OpenClaw whisper-context skill",
  };

  await requestJson(`${apiUrl}/v1/projects`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${API_KEY}`,
    },
    body: JSON.stringify(body),
  });
}

async function withAutoProject(ctx, fn) {
  try {
    return await fn();
  } catch (err) {
    if (looksLikeProjectNotFound(err)) {
      await ensureProjectExistsOnce(ctx);
      return await fn();
    }
    throw err;
  }
}

async function readJsonInput(spec) {
  const raw = await readTextInput(spec);
  try {
    return JSON.parse(raw);
  } catch {
    throw new Error("Invalid JSON input");
  }
}

async function readTextInput(spec) {
  const s = String(spec || "");
  if (!s) return "";
  if (s === "-") {
    if (process.stdin.isTTY) {
      throw new Error("stdin is empty (did you mean @file or a literal string?)");
    }
    return readStdinAll();
  }
  if (s.startsWith("@")) return readFile(s.slice(1), "utf8");
  return s;
}

function readStdinAll() {
  return new Promise((resolve, reject) => {
    let data = "";
    process.stdin.setEncoding("utf8");
    process.stdin.on("data", (chunk) => (data += chunk));
    process.stdin.on("end", () => resolve(data));
    process.stdin.on("error", reject);
    // If nothing is piped, 'end' may never fire; caller shouldn't use '-' without piping.
  });
}

function parseFlags(parts) {
  const out = {};
  for (let i = 0; i < parts.length; i++) {
    const p = parts[i];
    if (!p.startsWith("--")) continue;

    // Support: --key=value
    const eq = p.indexOf("=");
    if (eq !== -1) {
      const key = p.slice(2, eq);
      const val = p.slice(eq + 1) || "true";
      out[key] = val;
      continue;
    }

    // Support: --key value, or boolean --key
    const key = p.slice(2);
    const next = parts[i + 1];
    const val = next && !next.startsWith("--") ? parts[++i] : "true";
    out[key] = val;
  }
  return out;
}

function bool(v, defaultValue) {
  if (v === undefined || v === null) return defaultValue;
  if (typeof v === "boolean") return v;
  const s = String(v).toLowerCase().trim();
  if (s === "true" || s === "1" || s === "yes") return true;
  if (s === "false" || s === "0" || s === "no") return false;
  return defaultValue ?? false;
}

function num(v, defaultValue) {
  if (v === undefined || v === null || v === "") return defaultValue;
  const n = Number(v);
  if (!Number.isFinite(n)) return defaultValue;
  return n;
}

function csv(v) {
  return String(v)
    .split(",")
    .map((s) => s.trim())
    .filter(Boolean);
}

function safeJsonParse(v) {
  try {
    return JSON.parse(String(v));
  } catch {
    throw new Error("Invalid --metadata JSON");
  }
}

await main().catch((err) => {
  console.error(String(err?.message || err));
  process.exit(1);
});
