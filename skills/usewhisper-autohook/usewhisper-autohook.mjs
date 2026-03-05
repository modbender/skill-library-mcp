#!/usr/bin/env node
// usewhisper-autohook.mjs
// Minimal helper for "automatic" OpenClaw integration (Node 18+). No curl, no extra packages.

import { readFile } from "node:fs/promises";
import { mkdir, rename, writeFile } from "node:fs/promises";
import { homedir } from "node:os";
import path from "node:path";
import http from "node:http";

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

  if (!API_KEY) throw new Error("Missing WHISPER_CONTEXT_API_KEY");
  const apiUrl = flags.api_url || API_URL_DEFAULT;
  const project = flags.project || PROJECT_DEFAULT;
  if (!project) throw new Error("Missing WHISPER_CONTEXT_PROJECT (or pass --project)");

  if (cmd === "get_whisper_context") {
    const currentQuery = flags.current_query || flags.query || "";
    if (!currentQuery) throw new Error("Missing --current_query");

    const user_id = flags.user_id || "";
    const session_id = flags.session_id || "";
    if (!user_id) throw new Error("Missing --user_id");
    if (!session_id) throw new Error("Missing --session_id");

    // Default to delta compression across turns by persisting the prior context hash locally.
    // This makes "cost savings" the default for users who only paste the system prompt.
    const stateKey = makeStateKey({ apiUrl, project, user_id, session_id });
    const storedPrevHash = await readLastContextHash(stateKey);
    const previous_context_hash =
      flags.previous_context_hash || storedPrevHash || undefined;

    const body = {
      project,
      query: currentQuery,
      top_k: num(flags.top_k, 6),
      include_memories: bool(flags.include_memories, true),
      include_graph: bool(flags.include_graph, false),
      compress: bool(flags.compress, true),
      compression_strategy: flags.compression_strategy || "delta",
      use_cache: bool(flags.use_cache, true),
      user_id,
      session_id,
      previous_context_hash,
      max_tokens: flags.max_tokens ? num(flags.max_tokens) : undefined,
    };

    const res = await withAutoProject({ apiUrl, project }, () =>
      post(apiUrl, "/v1/context/query", body, { retry: true })
    );

    const contextHash =
      res?.meta?.context_hash ||
      res?.meta?.contextHash ||
      undefined;
    if (contextHash) {
      await writeLastContextHash(stateKey, String(contextHash));
    }

    // Keep the response small and tool-friendly: "context" is what gets injected.
    console.log(
      JSON.stringify(
        {
          context: String(res?.context || ""),
          context_hash: contextHash,
          meta: res?.meta || undefined,
        },
        null,
        2
      )
    );
    return;
  }

  if (cmd === "ingest_whisper_turn") {
    const session_id = flags.session_id || "";
    const user_id = flags.user_id || "";
    if (!session_id) throw new Error("Missing --session_id");
    if (!user_id) throw new Error("Missing --user_id");

    let userMsg;
    let assistantMsg;
    if (flags.turn_json) {
      const turn = await readJsonInput(flags.turn_json);
      userMsg = String(turn.user_msg || turn.user || "");
      assistantMsg = String(turn.assistant_msg || turn.assistant || "");
      if (!userMsg) throw new Error("turn_json missing 'user_msg' (or 'user')");
      if (!assistantMsg) throw new Error("turn_json missing 'assistant_msg' (or 'assistant')");
    } else {
      userMsg = await readTextInput(flags.user_msg || "");
      assistantMsg = await readTextInput(flags.assistant_msg || "");
      if (!userMsg) throw new Error("Missing --user_msg (or pass --turn_json)");
      if (!assistantMsg) throw new Error("Missing --assistant_msg (or pass --turn_json)");
    }

    const now = new Date();
    const body = {
      project,
      session_id,
      user_id,
      messages: [
        { role: "user", content: userMsg, timestamp: new Date(now.getTime() - 5_000).toISOString() },
        { role: "assistant", content: assistantMsg, timestamp: now.toISOString() },
      ],
    };

    const res = await withAutoProject({ apiUrl, project }, () => post(apiUrl, "/v1/memory/ingest/session", body));
    console.log(JSON.stringify(res, null, 2));
    return;
  }

  if (cmd === "serve_openai_proxy") {
    const port = num(flags.port, 8787);
    const upstreamBaseUrl =
      flags.upstream_base_url ||
      process.env.OPENAI_BASE_URL ||
      process.env.OPENAI_API_BASE ||
      process.env.WHISPER_UPSTREAM_OPENAI_BASE_URL ||
      "https://api.openai.com";
    const upstreamApiKey =
      flags.upstream_api_key ||
      process.env.OPENAI_API_KEY ||
      process.env.WHISPER_UPSTREAM_OPENAI_API_KEY ||
      "";

    if (!upstreamApiKey) {
      throw new Error(
        "Missing upstream API key (set OPENAI_API_KEY or pass --upstream_api_key)"
      );
    }

    const server = http.createServer(async (req, res) => {
      try {
        const url = new URL(req.url || "/", `http://${req.headers.host || "localhost"}`);

        if (req.method === "GET" && url.pathname === "/health") {
          res.writeHead(200, { "Content-Type": "application/json" });
          res.end(JSON.stringify({ ok: true }));
          return;
        }

        if (!(req.method === "POST" && url.pathname === "/v1/chat/completions")) {
          res.writeHead(404, { "Content-Type": "application/json" });
          res.end(JSON.stringify({ error: "Not found" }));
          return;
        }

        const bodyRaw = await readReqJson(req);
        const messages = Array.isArray(bodyRaw?.messages) ? bodyRaw.messages : [];
        const lastUserMsg = findLastUserMessage(messages);
        if (!lastUserMsg) {
          res.writeHead(400, { "Content-Type": "application/json" });
          res.end(JSON.stringify({ error: "Missing user message" }));
          return;
        }

        // IDs are required for stable memory and deltas.
        // Prefer explicit headers. If missing, try to infer from OpenClaw system prompt/session metadata.
        const headerUserId = header(req, "x-whisper-user-id") || header(req, "x-user-id") || "";
        const headerSessionId = header(req, "x-whisper-session-id") || header(req, "x-session-id") || "";
        const inferred = inferOpenClawIds({ messages, body: bodyRaw });
        const user_id = headerUserId || inferred.user_id || String(bodyRaw?.user || "anon");
        const session_id = headerSessionId || inferred.session_id || "default";

        const stateKey = makeStateKey({ apiUrl, project, user_id, session_id });
        const storedPrevHash = await readLastContextHash(stateKey);

        const ctxReq = {
          project,
          query: String(lastUserMsg.content || ""),
          top_k: 6,
          include_memories: true,
          include_graph: false,
          compress: true,
          compression_strategy: "delta",
          use_cache: true,
          user_id,
          session_id,
          previous_context_hash: storedPrevHash || undefined,
        };

        const ctxRes = await withAutoProject({ apiUrl, project }, () =>
          post(apiUrl, "/v1/context/query", ctxReq, { retry: true })
        );

        const context = String(ctxRes?.context || "");
        const contextHash = ctxRes?.meta?.context_hash || ctxRes?.meta?.contextHash || undefined;
        if (contextHash) await writeLastContextHash(stateKey, String(contextHash));

        // Build a minimal prompt for upstream: keep existing system messages, strip conversation history,
        // and replace the last user message with memory-injected text.
        const systemMessages = messages.filter((m) => m && m.role === "system");
        const injectedUser = {
          role: "user",
          content: context
            ? `Relevant long-term memory:\n${context}\n\nNow respond to:\n${String(lastUserMsg.content || "")}`
            : String(lastUserMsg.content || ""),
        };

        // Forward everything else mostly as-is (model/tools/etc), but disable streaming for simplicity.
        const upstreamBody = {
          ...bodyRaw,
          stream: false,
          messages: [...systemMessages, injectedUser],
        };

        const upstreamUrl = `${String(upstreamBaseUrl).replace(/\/+$/, "")}/v1/chat/completions`;
        const upstreamResp = await fetch(upstreamUrl, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${upstreamApiKey}`,
          },
          body: JSON.stringify(upstreamBody),
        });

        const upstreamText = await upstreamResp.text();
        res.writeHead(upstreamResp.status, {
          "Content-Type": upstreamResp.headers.get("content-type") || "application/json",
        });
        res.end(upstreamText);

        // Best-effort ingest after responding (ignore failures).
        try {
          const upstreamJson = safeJsonParseLoose(upstreamText);
          const assistantText = extractAssistantText(upstreamJson) || "";
          if (assistantText) {
            const now = new Date();
            const ingestBody = {
              project,
              session_id,
              user_id,
              messages: [
                { role: "user", content: String(lastUserMsg.content || ""), timestamp: new Date(now.getTime() - 5_000).toISOString() },
                { role: "assistant", content: assistantText, timestamp: now.toISOString() },
              ],
            };
            await withAutoProject({ apiUrl, project }, () =>
              post(apiUrl, "/v1/memory/ingest/session", ingestBody)
            );
          }
        } catch {
          // ignore
        }
      } catch (e) {
        res.writeHead(500, { "Content-Type": "application/json" });
        res.end(JSON.stringify({ error: String(e?.message || e) }));
      }
    });

    server.listen(port, "127.0.0.1", () => {
      // stdout is what OpenClaw sees; keep it simple.
      console.log(JSON.stringify({ ok: true, listening: `http://127.0.0.1:${port}`, upstream: upstreamBaseUrl }, null, 2));
    });
    return;
  }

  if (cmd === "serve_anthropic_proxy") {
    const port = num(flags.port, 8788);
    const upstreamBaseUrl =
      flags.upstream_base_url ||
      process.env.ANTHROPIC_BASE_URL ||
      process.env.WHISPER_UPSTREAM_ANTHROPIC_BASE_URL ||
      "https://api.anthropic.com";
    const upstreamApiKey =
      flags.upstream_api_key ||
      process.env.ANTHROPIC_API_KEY ||
      process.env.WHISPER_UPSTREAM_ANTHROPIC_API_KEY ||
      "";
    const upstreamVersion =
      flags.anthropic_version ||
      process.env.WHISPER_UPSTREAM_ANTHROPIC_VERSION ||
      "2023-06-01";

    if (!upstreamApiKey) {
      throw new Error(
        "Missing upstream Anthropic API key (set ANTHROPIC_API_KEY or pass --upstream_api_key)"
      );
    }

    const server = http.createServer(async (req, res) => {
      try {
        const url = new URL(req.url || "/", `http://${req.headers.host || "localhost"}`);

        if (req.method === "GET" && url.pathname === "/health") {
          res.writeHead(200, { "Content-Type": "application/json" });
          res.end(JSON.stringify({ ok: true }));
          return;
        }

        if (!(req.method === "POST" && url.pathname === "/v1/messages")) {
          res.writeHead(404, { "Content-Type": "application/json" });
          res.end(JSON.stringify({ error: "Not found" }));
          return;
        }

        const bodyRaw = await readReqJson(req);
        const messages = Array.isArray(bodyRaw?.messages) ? bodyRaw.messages : [];

        const lastUserMsg = findLastUserMessage(messages);
        const lastUserText = normalizeMessageContentToText(lastUserMsg?.content);
        if (!lastUserMsg || !lastUserText) {
          res.writeHead(400, { "Content-Type": "application/json" });
          res.end(JSON.stringify({ error: "Missing user message" }));
          return;
        }

        // IDs are required for stable memory and deltas.
        const headerUserId = header(req, "x-whisper-user-id") || header(req, "x-user-id") || "";
        const headerSessionId = header(req, "x-whisper-session-id") || header(req, "x-session-id") || "";
        const inferred = inferOpenClawIds({ messages, body: bodyRaw });
        const user_id =
          headerUserId ||
          inferred.user_id ||
          String(bodyRaw?.metadata?.user_id || bodyRaw?.user_id || bodyRaw?.user || "anon");
        const session_id =
          headerSessionId ||
          inferred.session_id ||
          String(bodyRaw?.metadata?.session_id || bodyRaw?.session_id || "default");

        const stateKey = makeStateKey({ apiUrl, project, user_id, session_id });
        const storedPrevHash = await readLastContextHash(stateKey);

        const ctxReq = {
          project,
          query: lastUserText,
          top_k: 6,
          include_memories: true,
          include_graph: false,
          compress: true,
          compression_strategy: "delta",
          use_cache: true,
          user_id,
          session_id,
          previous_context_hash: storedPrevHash || undefined,
        };

        const ctxRes = await withAutoProject({ apiUrl, project }, () =>
          post(apiUrl, "/v1/context/query", ctxReq, { retry: true })
        );

        const context = String(ctxRes?.context || "");
        const contextHash = ctxRes?.meta?.context_hash || ctxRes?.meta?.contextHash || undefined;
        if (contextHash) await writeLastContextHash(stateKey, String(contextHash));

        const injectedUserText = context
          ? `Relevant long-term memory:\n${context}\n\nNow respond to:\n${lastUserText}`
          : lastUserText;

        // Anthropic Messages API supports either:
        // - a top-level "system" field, and messages without system role
        // - messages with user/assistant roles
        // We'll preserve "system" as-is and strip history to just the last user message.
        const upstreamBody = {
          ...bodyRaw,
          stream: false,
          messages: [{ role: "user", content: injectedUserText }],
        };

        const upstreamUrl = `${String(upstreamBaseUrl).replace(/\/+$/, "")}/v1/messages`;
        const upstreamResp = await fetch(upstreamUrl, {
          method: "POST",
          headers: {
            "content-type": "application/json",
            "x-api-key": upstreamApiKey,
            "anthropic-version": upstreamVersion,
            // Forward betas if the caller set them.
            ...(header(req, "anthropic-beta") ? { "anthropic-beta": header(req, "anthropic-beta") } : {}),
          },
          body: JSON.stringify(upstreamBody),
        });

        const upstreamText = await upstreamResp.text();
        res.writeHead(upstreamResp.status, {
          "Content-Type": upstreamResp.headers.get("content-type") || "application/json",
        });
        res.end(upstreamText);

        // Best-effort ingest after responding (ignore failures).
        try {
          const upstreamJson = safeJsonParseLoose(upstreamText);
          const assistantText = extractAnthropicAssistantText(upstreamJson) || "";
          if (assistantText) {
            const now = new Date();
            const ingestBody = {
              project,
              session_id,
              user_id,
              messages: [
                { role: "user", content: lastUserText, timestamp: new Date(now.getTime() - 5_000).toISOString() },
                { role: "assistant", content: assistantText, timestamp: now.toISOString() },
              ],
            };
            await withAutoProject({ apiUrl, project }, () =>
              post(apiUrl, "/v1/memory/ingest/session", ingestBody)
            );
          }
        } catch {
          // ignore
        }
      } catch (e) {
        res.writeHead(500, { "Content-Type": "application/json" });
        res.end(JSON.stringify({ error: String(e?.message || e) }));
      }
    });

    server.listen(port, "127.0.0.1", () => {
      console.log(JSON.stringify({ ok: true, listening: `http://127.0.0.1:${port}`, upstream: upstreamBaseUrl }, null, 2));
    });
    return;
  }

  throw new Error(`Unknown command: ${cmd}`);
}

function getStatePath() {
  // Allow overrides for unusual OpenClaw setups.
  if (process.env.WHISPER_AUTOHOOK_STATE_PATH) return process.env.WHISPER_AUTOHOOK_STATE_PATH;

  // Default: keep it in the user's home dir under .openclaw to match typical installs.
  // (We create folders as needed.)
  return path.join(homedir(), ".openclaw", ".cache", "usewhisper-autohook", "state.json");
}

function makeStateKey({ apiUrl, project, user_id, session_id }) {
  return `${apiUrl}|${project}|${user_id}|${session_id}`;
}

async function readLastContextHash(stateKey) {
  try {
    const raw = await readFile(getStatePath(), "utf8");
    const json = JSON.parse(raw);
    const v = json?.last_context_hash?.[stateKey];
    return typeof v === "string" && v.trim() ? v : null;
  } catch {
    return null;
  }
}

async function writeLastContextHash(stateKey, hash) {
  const statePath = getStatePath();
  const dir = path.dirname(statePath);
  await mkdir(dir, { recursive: true });

  let json = {};
  try {
    json = JSON.parse(await readFile(statePath, "utf8"));
  } catch {
    json = {};
  }

  if (!json.last_context_hash || typeof json.last_context_hash !== "object") {
    json.last_context_hash = {};
  }
  json.last_context_hash[stateKey] = hash;

  const tmp = `${statePath}.${process.pid}.tmp`;
  await writeFile(tmp, JSON.stringify(json, null, 2), "utf8");
  await rename(tmp, statePath);
}

function printHelp() {
  const text = [
    "usewhisper-autohook.mjs",
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
    "  get_whisper_context --current_query <text> --user_id <id> --session_id <id> [--previous_context_hash <hash>]",
    "  ingest_whisper_turn --user_id <id> --session_id <id> --user_msg <text> --assistant_msg <text>",
    "                    or: --turn_json <json|@file|-> (stdin JSON: {\"user_msg\":\"...\",\"assistant_msg\":\"...\"})",
    "  serve_openai_proxy  --port 8787 --upstream_base_url <url> --upstream_api_key <key>",
    "  serve_anthropic_proxy --port 8788 --upstream_base_url <url> --upstream_api_key <key> [--anthropic_version 2023-06-01]",
    "",
    "Notes:",
    "  - get_whisper_context automatically persists the last context hash per (api_url, project, user_id, session_id) to enable delta compression by default.",
    "  - Override state file location via WHISPER_AUTOHOOK_STATE_PATH if needed.",
    "  - serve_openai_proxy provides an OpenAI-compatible /v1/chat/completions endpoint that strips chat history and injects Whisper memory, even if your agent would have sent the full history.",
    "    Pass IDs via headers: x-whisper-user-id and x-whisper-session-id (recommended).",
    "  - serve_anthropic_proxy provides an Anthropic-compatible /v1/messages endpoint that does the same for native Anthropic API usage.",
    "  - Proxies do not restrict models. Whatever 'model' you send will be forwarded to the upstream provider/base URL.",
    "",
    "Examples:",
    "  node usewhisper-autohook.mjs get_whisper_context --current_query \"...\" --user_id telegram:123 --session_id telegram:456",
    "  echo '{\"user_msg\":\"...\",\"assistant_msg\":\"...\"}' | node usewhisper-autohook.mjs ingest_whisper_turn --user_id telegram:123 --session_id telegram:456 --turn_json -",
    "  OPENAI_API_KEY=... node usewhisper-autohook.mjs serve_openai_proxy --port 8787",
    "  ANTHROPIC_API_KEY=... node usewhisper-autohook.mjs serve_anthropic_proxy --port 8788",
  ].join("\n");
  console.log(text);
}

function header(req, name) {
  const v = req.headers?.[String(name).toLowerCase()];
  if (Array.isArray(v)) return v[0] || "";
  return String(v || "");
}

function findLastUserMessage(messages) {
  for (let i = messages.length - 1; i >= 0; i--) {
    const m = messages[i];
    if (m && m.role === "user") {
      const text = normalizeMessageContentToText(m.content);
      if (text) return m;
    }
  }
  return null;
}

function normalizeMessageContentToText(content) {
  if (typeof content === "string") return content.trim() ? content : "";
  if (!content) return "";
  if (Array.isArray(content)) {
    // Anthropic content blocks: [{type:"text", text:"..."}, ...]
    const parts = [];
    for (const b of content) {
      if (b && b.type === "text" && typeof b.text === "string" && b.text.trim()) parts.push(b.text);
    }
    return parts.join("\n").trim();
  }
  return "";
}

function inferOpenClawIds({ messages, body }) {
  // Best-effort inference to avoid requiring app changes.
  // If OpenClaw includes a session key or inbound context fields in the system prompt, we can derive stable ids.
  const sysText = extractSystemText({ messages, body });
  const sessionKey = extractSessionKey(sysText);
  const senderId = extractSenderId(sysText);
  const chatId = extractChatId(sysText);

  // Prefer session key as session id because it's stable by definition in OpenClaw.
  const session_id = sessionKey || (chatId ? `chat:${chatId}` : null);

  // Prefer an explicit sender id; otherwise try to derive from sessionKey.
  let user_id = senderId || null;
  if (!user_id && sessionKey) {
    const dmPeer = match1(sessionKey, /:dm:([^\s:]+)/i);
    if (dmPeer) user_id = dmPeer;
  }

  // Normalize plain numerics when we can confidently tell the channel.
  if (user_id && /^[0-9]+$/.test(user_id) && sessionKey) {
    const channel = match1(sessionKey, /agent:[^:\s]+:([^:\s]+):/i);
    if (channel) user_id = `${channel}:${user_id}`;
  }
  if (session_id && /^chat:-?[0-9]+$/.test(session_id) && sessionKey) {
    const channel = match1(sessionKey, /agent:[^:\s]+:([^:\s]+):/i);
    if (channel) {
      const n = session_id.slice("chat:".length);
      // For groups/channels, session id should be stable per chat id.
      // This format matches the earlier Telegram recommendation but is safe for other channels too.
      // Example: telegram:-100123...
      return { user_id, session_id: `${channel}:${n}` };
    }
  }

  return { user_id, session_id };
}

function extractSystemText({ messages, body }) {
  const parts = [];

  // OpenAI-style system messages
  for (const m of messages || []) {
    if (m && m.role === "system") {
      const t = normalizeMessageContentToText(m.content);
      if (t) parts.push(t);
    }
  }

  // Anthropic top-level "system" can be a string or an array of blocks.
  const sys = body?.system;
  if (typeof sys === "string" && sys.trim()) parts.push(sys);
  if (Array.isArray(sys)) {
    const t = normalizeMessageContentToText(sys);
    if (t) parts.push(t);
  }

  return parts.join("\n");
}

function extractSessionKey(text) {
  if (!text) return null;

  // Common explicit labels.
  const labeled =
    match1(text, /\bsessionkey\s*[:=]\s*(agent:[^\s]+)/i) ||
    match1(text, /\bsession\s*key\s*[:=]\s*(agent:[^\s]+)/i);
  if (labeled) return labeled;

  // Otherwise pick the longest plausible "agent:..." token; group keys have many colons.
  const matches = text.match(/\bagent:[^\s]+/gi) || [];
  if (matches.length === 0) return null;
  matches.sort((a, b) => b.length - a.length);
  return matches[0];
}

function extractSenderId(text) {
  if (!text) return null;
  return (
    match1(text, /\bsender(?:_id|id)?\s*[:=]\s*([a-z0-9_+-]+:[a-z0-9_+-]+)/i) ||
    match1(text, /\bfrom(?:_id|id)?\s*[:=]\s*([a-z0-9_+-]+:[a-z0-9_+-]+)/i) ||
    match1(text, /\bfrom\.id\s*[:=]\s*([0-9]+)/i) ||
    null
  );
}

function extractChatId(text) {
  if (!text) return null;
  return (
    match1(text, /\bchat\.id\s*[:=]\s*(-?[0-9]+)/i) ||
    match1(text, /\bchat_id\s*[:=]\s*(-?[0-9]+)/i) ||
    match1(text, /\bgroup(?:_id|id)?\s*[:=]\s*(-?[0-9]+)/i) ||
    null
  );
}

function match1(text, re) {
  const m = String(text || "").match(re);
  return m && m[1] ? String(m[1]).trim() : null;
}

function safeJsonParseLoose(text) {
  try {
    return JSON.parse(text);
  } catch {
    return null;
  }
}

function extractAssistantText(upstreamJson) {
  // OpenAI-style chat.completions
  const c0 = upstreamJson?.choices?.[0];
  const content = c0?.message?.content;
  if (typeof content === "string") return content;
  // If tool call etc, return empty.
  return "";
}

function extractAnthropicAssistantText(upstreamJson) {
  // Anthropic Messages API: { content: [{type:"text", text:"..."}], ... }
  const blocks = upstreamJson?.content;
  if (typeof blocks === "string") return blocks;
  if (Array.isArray(blocks)) {
    const parts = [];
    for (const b of blocks) {
      if (b && b.type === "text" && typeof b.text === "string") parts.push(b.text);
    }
    return parts.join("\n").trim();
  }
  return "";
}

function readReqJson(req, maxBytes = 2 * 1024 * 1024) {
  return new Promise((resolve, reject) => {
    let size = 0;
    let data = "";
    req.setEncoding("utf8");
    req.on("data", (chunk) => {
      size += chunk.length;
      if (size > maxBytes) {
        reject(new Error("Request too large"));
        req.destroy();
        return;
      }
      data += chunk;
    });
    req.on("end", () => {
      try {
        resolve(JSON.parse(data || "{}"));
      } catch {
        reject(new Error("Invalid JSON body"));
      }
    });
    req.on("error", reject);
  });
}

function getTimeoutMs() {
  return num(flags.timeout_ms, 30_000);
}

async function fetchWithTimeout(url, init) {
  const timeoutMs = getTimeoutMs();
  const controller = new AbortController();
  const t = setTimeout(() => controller.abort(), timeoutMs);
  try {
    return await fetch(url, { ...init, signal: controller.signal });
  } finally {
    clearTimeout(t);
  }
}

async function post(apiUrl, path, body, options = {}) {
  return requestJson(
    `${apiUrl}${path}`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${API_KEY}`,
      },
      body: JSON.stringify(body),
    },
    options
  );
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

  const body = {
    name: project,
    description: "Auto-provisioned by OpenClaw usewhisper-autohook skill",
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
    if (process.stdin.isTTY) throw new Error("stdin is empty (did you mean @file or a literal string?)");
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
  });
}

function parseFlags(parts) {
  const out = {};
  for (let i = 0; i < parts.length; i++) {
    const p = parts[i];
    if (!p.startsWith("--")) continue;

    const eq = p.indexOf("=");
    if (eq !== -1) {
      const key = p.slice(2, eq);
      const val = p.slice(eq + 1) || "true";
      out[key] = val;
      continue;
    }

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

await main().catch((err) => {
  console.error(String(err?.message || err));
  process.exit(1);
});
