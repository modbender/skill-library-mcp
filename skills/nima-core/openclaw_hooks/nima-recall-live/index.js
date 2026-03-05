/**
 * NIMA Live Recall Hook
 * ======================
 * Queries experiential memory on EVERY message via before_agent_start.
 * Lightweight: FTS5 search only (no full graph traversal), ~50-100ms.
 * 
 * Hooks:
 *   before_agent_start → query recent user message against graph → prepend memories
 * 
 * Author: NIMA Core Team
 * Date: Feb 14, 2026
 */

import { execFileSync } from "node:child_process";
import { execPython } from "../utils/async-python.js"; // Async wrapper
import { existsSync, writeFileSync, readFileSync, unlinkSync, mkdtempSync, mkdirSync } from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import os from "node:os";

// ESM __dirname polyfill
const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const GRAPH_DB = join(os.homedir(), ".nima", "memory", "graph.sqlite");
const DEBUG_RECALL = process.env.NIMA_DEBUG_RECALL === "1" || process.env.NIMA_DEBUG_RECALL === "true";
const LADYBUG_DB = join(os.homedir(), ".nima", "memory", "ladybug.lbug");
const MAX_RESULTS = 7; // Increased from 3 for richer context
const QUERY_TIMEOUT = 10000; // 10s max — includes Voyage embedding call
const MIN_QUERY_LENGTH = 3; // Skip very short messages (was 10, lowered for testing)
const COOLDOWN_MS = 10000; // Reduced from 30s for more responsive conversations
const MAX_QUERY_CHARS = 300;
const FTS_ONLY_MODE = false; // Hybrid mode: FTS first, then Voyage if needed (uses pre-computed index)
const USE_LADYBUG = true; // LadybugDB backend (13K+ memories) — multi-word CONTAINS bug fixed

// Session-level memory tracking for deduplication and budget
const SESSION_MEMORY_IDS = new Set();
let recallCounter = 0; // Cycles for dedup reset
const SESSION_TOKEN_BUDGET = 3000; // Max memory tokens per session (increased from 500)
const USE_COMPRESSED_FORMAT = true; // Compressed format saves ~80% tokens
let sessionTokensUsed = 0;
let lastConversationId = null; // Track conversation changes

/**
 * Reset session state when conversation changes
 */
function resetSessionIfNeeded(conversationId) {
  if (conversationId && conversationId !== lastConversationId) {
    if (lastConversationId !== null) {
      console.error(`[nima-recall-live] 🔄 New conversation detected, resetting session state`);
    }
    SESSION_MEMORY_IDS.clear();
    sessionTokensUsed = 0;
    lastConversationId = conversationId;
  }
}

// Simple cache to avoid redundant queries
let lastQuery = "";
let lastQueryTime = 0;
let lastResult = "";
let lastBleed = null;  // Cache affect bleed too

// =============================================================================
// SECURITY: Path Sanitization
// =============================================================================

/**
 * Sanitize a string for safe use in file paths.
 * Prevents path traversal attacks (e.g., "../../etc/passwd").
 * 
 * @param {string} name - Input string (e.g., identityName, conversationId)
 * @param {number} maxLength - Maximum allowed length (default 100)
 * @returns {string} Sanitized string containing only [a-zA-Z0-9_-]
 */
function sanitizePathComponent(name, maxLength = 100) {
  if (typeof name !== "string") {
    name = name != null ? String(name) : "";
  }
  // Remove path separators and parent directory references
  name = name.replace(/\//g, "_").replace(/\\/g, "_").replace(/\.\./g, "");
  // Keep only alphanumeric, dash, underscore
  name = name.replace(/[^a-zA-Z0-9_-]/g, "_");
  // Collapse multiple underscores
  name = name.replace(/_+/g, "_");
  // Remove leading/trailing underscores
  name = name.replace(/^_+|_+$/g, "");
  // Ensure non-empty
  if (!name) name = "default";
  // Truncate if too long
  if (name.length > maxLength) name = name.slice(0, maxLength);
  return name;
}

/**
 * Sanitize FTS5 query — escape operators
 */
function sanitizeFTS5(query) {
  return query
    .replace(/["():*^~{}[\]]/g, " ")
    .replace(/\b(AND|OR|NOT|NEAR)\b/gi, " ")
    .trim()
    .split(/\s+/)
    .filter(w => w.length > 2)
    .slice(0, 8)
    .map(w => `"${w.replace(/"/g, "")}"`)
    .join(" OR ");
}

/**
 * Strip channel prefix from message (e.g., [Telegram David id:123 ...] → actual message)
 */
function stripChannelPrefix(text) {
  return text.replace(/^\[(?:Telegram|Discord|Signal|SMS|Slack|Matrix|WhatsApp|iMessage|Email)\s+[^\]]*\]\s*/i, "").trim();
}

/**
 * Strip timestamp prefix from message (e.g., [Mon 2026-02-16 21:16 EST] → actual message)
 */
function stripTimestampPrefix(text) {
  return text.replace(/^\[[A-Z][a-z]{2}\s+\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}\s+[A-Z]{3}\]\s*/i, "").trim();
}

/**
 * Extract the user's actual message text from the prompt
 */
function extractUserMessage(prompt) {
  if (!prompt || typeof prompt !== "string") return "";
  
  // Early bail on system messages
  if (prompt.includes("GatewayRestart")) return "";
  if (prompt.includes("HEARTBEAT_OK") || prompt.includes("Read HEARTBEAT.md")) return "";
  if (prompt.includes("Pre-compaction memory flush")) return "";
  
  // Get the last meaningful user content — skip system prefixes, affect blocks
  const lines = prompt.split("\n");
  const userLines = [];
  
  for (let i = lines.length - 1; i >= 0 && userLines.length < 3; i--) {
    const line = lines[i].trim();
    if (!line) continue;
    if (line.includes("AFFECT STATE") || line.includes("[Dynamic affect")) continue;
    if (line.startsWith("🎭")) continue;
    if (line.length < 10) continue;
    if (line.startsWith("[message_id:")) continue;
    if (line.startsWith("<media:") && !line.includes("<media:audio>")) continue;
    if (line.startsWith("{") || line.startsWith("}")) continue; // JSON fragments
    if (line.startsWith('"') && line.endsWith(',')) continue; // JSON fields
    if (line.includes("doctorHint") || line.includes("sessionKey")) continue;
    if (line.includes("[NIMA RECALL")) continue; // Don't re-query our own output
    // Strip metadata injection lines
    if (line.includes("Conversation info (untrusted metadata)")) continue;
    if (line.includes('"sender"') || line.includes('"message_id"')) continue;
    if (line.startsWith("```json") || line.startsWith("```")) continue;
    if (line.includes("gateway-client")) continue;
    
    // Extract transcript from audio messages: "[Audio] User text: [...] <media:audio> Transcript: [ts] actual text"
    let cleaned = line;
    if (line.startsWith("[Audio]") || line.includes("<media:audio>")) {
      const transcriptMatch = line.match(/Transcript:\s*(?:\[\d{2}:\d{2}[^\]]*\]\s*)+(.*)/i);
      if (transcriptMatch) {
        cleaned = transcriptMatch[1].trim();
      } else {
        continue; // No transcript found — skip audio line
      }
    }

    // Strip channel prefix to get actual message content
    cleaned = stripChannelPrefix(cleaned);
    // Also strip timestamp prefix (e.g., [Mon 2026-02-16 21:16 EST])
    cleaned = stripTimestampPrefix(cleaned);
    if (cleaned.length > 5) {
      userLines.unshift(cleaned);
    }
  }
  
  return userLines.join(" ").substring(0, MAX_QUERY_CHARS);
}

/**
 * Run LAZY recall: Three-tier loading for context efficiency
 * Tier 1: Index scan (turn_ids only)
 * Tier 2: Summary load (compressed)
 * Tier 3: Full decode (on demand only)
 */
async function quickRecall(query) {
  console.error(`[nima-recall-live] 🚀 LAZY RECALL with: "${query.substring(0,50)}"`);
  
  // Try LadybugDB backend first (if enabled and available)
  if (USE_LADYBUG && existsSync(LADYBUG_DB)) {
    const ladybugPath = join(os.homedir(), ".openclaw", "extensions", "nima-recall-live", "ladybug_recall.py");
    if (existsSync(ladybugPath)) {
      try {
        const result = await execPython(ladybugPath, [query, "--top", String(MAX_RESULTS), "--json"], {
          timeout: QUERY_TIMEOUT,
          encoding: "utf-8",
          breakerId: "recall-ladybug"
        });
        
        if (result && result.trim() !== "[]") {
          console.error(`[nima-recall-live] ✅ LadybugDB backend`);
          return JSON.parse(result.trim());
        }
      } catch (err) {
        console.error(`[nima-recall-live] LadybugDB recall failed: ${err.message}, trying SQLite fallback`);
      }
    }
  }
  
  // Fallback to SQLite backend
  if (!existsSync(GRAPH_DB)) {
    console.error(`[nima-recall-live] ❌ Graph DB not found at ${GRAPH_DB}`);
    return null;
  }
  
  // Use the new lazy recall Python script
  // Use v3 with pre-computed index, query cache, and deferred loading
  const scriptPath = join(os.homedir(), ".openclaw", "extensions", "nima-recall-live", "lazy_recall.py");
  const fallbackPath = join(os.homedir(), ".openclaw", "extensions", "nima-recall-live", "lazy_recall_legacy_v2.py");
  const legacyPath = join(os.homedir(), ".openclaw", "extensions", "nima-recall-live", "lazy_recall_legacy_v1.py");
  
  // Try canonical first, then legacy v2, then legacy v1
  const actualPath = existsSync(scriptPath) ? scriptPath : 
                     existsSync(fallbackPath) ? fallbackPath : legacyPath;
  if (!existsSync(actualPath)) {
    console.error(`[nima-recall-live] ❌ No recall script found`);
    return null;
  }
  
  // Build args for v3+ scripts (canonical lazy_recall.py is v3+)
  const isV3 = actualPath.endsWith("lazy_recall.py") || actualPath.includes("lazy_recall_v3.py");
  const args = isV3 ? [
    query, 
    "--max-results", String(MAX_RESULTS),
    ...(FTS_ONLY_MODE ? ["--fts-only"] : [])
  ] : [query];
  
  try {
    const result = await execPython(actualPath, args, {
      timeout: QUERY_TIMEOUT,
      encoding: "utf-8",
      breakerId: "recall-lazy"
    });
    
    if (!result || result.trim() === "[]") {
      return null;
    }
    
    return JSON.parse(result.trim());
  } catch (err) {
    console.error(`[nima-recall-live] Lazy recall failed: ${err.message}`);
    return null;
  }
}

/**
 * DEPRECATED: Old inline recall (slower, loads all embeddings)
 * Kept for fallback if lazy_recall.py fails
 */
async function quickRecallLegacy(query) {
  console.error(`[nima-recall-live] 🚀 LEGACY quickRecall (slower) with: "${query.substring(0,50)}"`);
  if (!existsSync(GRAPH_DB)) {
    console.error(`[nima-recall-live] ❌ Graph DB not found at ${GRAPH_DB}`);
    return null;
  }
  
  const sanitized = sanitizeFTS5(query);
  if (!sanitized && !query) return null;
  
  // Build Python script for hybrid search
  const tmpDir = mkdtempSync(join(os.tmpdir(), "nima-recall-live-"));
  const queryFile = join(tmpDir, "query.json");
  
  try {
    writeFileSync(queryFile, JSON.stringify({
      db_path: GRAPH_DB,
      fts_query: sanitized,
      query_text: query.substring(0, 500),  // Full text for embedding
      max_results: MAX_RESULTS,
      use_embeddings: true
    }));
    
    const script = `
import json, sqlite3, sys, os, struct

# Unpack vector from blob
def decode_vector(blob):
    if not blob: return None
    n = len(blob) // 4
    return list(struct.unpack(f'{n}f', blob))

# Cosine similarity
def cosine_sim(a, b):
    if not a or not b: return 0.0
    dot = sum(x*y for x,y in zip(a,b))
    norm_a = sum(x*x for x in a)**0.5
    norm_b = sum(x*x for x in b)**0.5
    if norm_a == 0 or norm_b == 0: return 0.0
    return dot / (norm_a * norm_b)

# Voyage embedding
def get_embedding(text):
    import os
    api_key = os.environ.get("VOYAGE_API_KEY")
    if not api_key:
        raise ValueError("VOYAGE_API_KEY environment variable not set")
    import voyageai
    client = voyageai.Client(api_key=api_key)
    result = client.embed([text], model="voyage-3-lite")
    return result.embeddings[0]

with open(sys.argv[1]) as f:
    params = json.load(f)

db = sqlite3.connect(params["db_path"])
db.row_factory = sqlite3.Row

results = {}

# 1. FTS5 exact match (weight: 0.4)
if params.get("fts_query"):
    try:
        fts_rows = db.execute("""
            SELECT n.turn_id, n.layer, n.summary, n.who, n.timestamp, n.id,
                   fts.rank as score
            FROM memory_fts fts
            JOIN memory_nodes n ON fts.rowid = n.id
            WHERE memory_fts MATCH ?
            ORDER BY fts.rank
            LIMIT ?
        """, (params["fts_query"], params["max_results"] * 5)).fetchall()
        
        for r in fts_rows:
            tid = r["turn_id"]
            if tid not in results:
                results[tid] = {"layers": {}, "fts_score": 0, "emb_score": 0, "timestamp": r["timestamp"], "who": r["who"], "id": r["id"]}
            results[tid]["layers"][r["layer"]] = r["summary"] or ""
            results[tid]["fts_score"] += abs(r["score"] or 0)
    except Exception as e:
        pass

# 2. Voyage semantic search (weight: 0.6)
if params.get("use_embeddings") and params.get("query_text"):
    try:
        query_vec = get_embedding(params["query_text"][:500])
        
        # Get embedded nodes
        emb_rows = db.execute("""
            SELECT id, turn_id, layer, summary, who, timestamp, embedding
            FROM memory_nodes
            WHERE embedding IS NOT NULL
        """).fetchall()
        
        # Score by cosine similarity
        scored = []
        for r in emb_rows:
            vec = decode_vector(r["embedding"])
            sim = cosine_sim(query_vec, vec)
            if sim > 0.3:  # Threshold for relevance
                scored.append((sim, r))
        
        scored.sort(key=lambda x: x[0], reverse=True)
        
        for sim, r in scored[:params["max_results"] * 3]:
            tid = r["turn_id"]
            if tid not in results:
                results[tid] = {"layers": {}, "fts_score": 0, "emb_score": 0, "timestamp": r["timestamp"], "who": r["who"], "id": r["id"]}
            if r["layer"] not in results[tid]["layers"]:
                results[tid]["layers"][r["layer"]] = r["summary"] or ""
            results[tid]["emb_score"] = max(results[tid]["emb_score"], sim)
    except Exception as e:
        pass

# 3. Blend scores: 40% FTS5 + 60% semantic
for tid, r in results.items():
    fts_norm = min(r["fts_score"] / 100, 1.0) if r["fts_score"] else 0
    r["score"] = (fts_norm * 0.4) + (r["emb_score"] * 0.6)

ranked = sorted(results.values(), key=lambda t: t["score"], reverse=True)[:params["max_results"]]

output = []
for t in ranked:
    parts = []
    if t["layers"].get("input"):
        parts.append(f"In: {t['layers']['input'][:120]}")
    if t["layers"].get("output"):
        parts.append(f"Out: {t['layers']['output'][:120]}")
    if t["layers"].get("contemplation"):
        parts.append(f"Think: {t['layers']['contemplation'][:100]}")
    if parts:
        who = t.get("who", "unknown")
        output.append(f"[{who}] " + " | ".join(parts))

print(json.dumps(output))
db.close()
`;
    
    const result = await execPython("python3", ["-c", script, queryFile], {
      timeout: QUERY_TIMEOUT,
      encoding: "utf-8",
      breakerId: "recall-legacy"
    });
    
    return JSON.parse(result.trim());
  } catch (err) {
    console.error(`[nima-recall-live] Query failed: ${err.message}`);
    return null;
  } finally {
    try { unlinkSync(queryFile); } catch {}
    try { require("fs").rmdirSync(tmpDir); } catch {}
  }
}

/**
 * Format memories for context injection
 * Features:
 * - Session-level deduplication (won't repeat same memories)
 * - Token budget tracking (stops at SESSION_TOKEN_BUDGET)
 * - Compressed format (saves ~80% tokens)
 */
function formatMemories(memories) {
  if (!memories || memories.length === 0) return "";
  
  // Check token budget
  if (sessionTokensUsed >= SESSION_TOKEN_BUDGET) {
    console.error(`[nima-recall-live] ⚠️ Session token budget exhausted (${sessionTokensUsed}/${SESSION_TOKEN_BUDGET})`);
    return "";
  }
  
  // Deduplicate: filter out already-injected memories
  const newMemories = [];
  for (const m of memories) {
    const id = m.id || m.turn_id || m.summary?.slice(0, 50);
    if (id && !SESSION_MEMORY_IDS.has(id)) {
      SESSION_MEMORY_IDS.add(id);
      newMemories.push(m);
    }
  }
  
  if (newMemories.length === 0) {
    console.error(`[nima-recall-live] 📋 All memories already injected (dedup)`);
    return "";
  }
  
  console.error(`[nima-recall-live] 📋 Injecting ${newMemories.length} new memories (${SESSION_MEMORY_IDS.size} total this session)`);
  
  if (USE_COMPRESSED_FORMAT) {
    // Compressed format: 📌 [who: summary...]
    // Saves ~80% tokens vs full format
    const lines = newMemories.map(m => {
      const who = m.who || "unknown";
      const summary = (m.summary || m.text || "").slice(0, 80);
      return `[${who}] ${summary}`;
    });
    const compressed = lines.join(" | ");
    const tokens = Math.ceil(compressed.length / 4);
    sessionTokensUsed += tokens;
    
    console.error(`[nima-recall-live] 📊 Tokens: ${tokens} (session total: ${sessionTokensUsed}/${SESSION_TOKEN_BUDGET})`);
    
    return `\n[NIMA RECALL — ${newMemories.length} memories]\n${compressed}\n`;
  } else {
    // Original format (verbose)
    const lines = newMemories.map((m, i) => `  ${i + 1}. ${m}`);
    const formatted = `\n[NIMA RECALL — relevant memories from past conversations]\n${lines.join("\n")}\n[End recall — use naturally, don't announce]\n`;
    const tokens = Math.ceil(formatted.length / 4);
    sessionTokensUsed += tokens;
    return formatted;
  }
}

/**
 * Get active precognitions (predictions) for injection into recall context.
 * 
 * OPTIMIZATIONS (v2):
 * 1. Dedup: Hash-checks output, skips if identical to last injection
 * 2. Inject-once: Only injects on first message per session (or when predictions change)
 * 3. Compact format: Short tag format instead of full sentences
 */
let _lastPrecogHash = null;
let _precogInjectCount = 0;

async function getPrecognitions(queryText) {
  try {
    // Use standalone Python script — no inline code, no query injection
    const scriptPath = join(__dirname, "query_precognitions.py");
    if (!existsSync(scriptPath)) {
      return "";
    }
    
    // Pass query as argument (execPython uses execFile, not shell)
    const rawResult = await execPython(scriptPath, [queryText, "--limit", "3"], {
      timeout: 5000,
      breakerId: "recall-precog"
    });
    const trimmed = rawResult.trim();
    if (!trimmed) return "";
    
    // Parse JSON output from standalone script
    let parsed;
    try {
      parsed = JSON.parse(trimmed);
    } catch {
      return "";
    }
    
    const { parts, hash } = parsed;
    if (!parts || !parts.length) return "";
    
    // Dedup — skip if hash matches last injection
    if (hash === _lastPrecogHash) {
      return "";
    }
    
    _lastPrecogHash = hash;
    _precogInjectCount++;
    
    // Compact format
    const compact = "🔮 " + parts.join(" | ");
    if (DEBUG_RECALL) {
      console.error(`[nima-recall-live] Precog injected (${compact.length} chars, hash=${hash})`);
    }
    return compact;
  } catch (e) {
    if (DEBUG_RECALL) {
      console.error(`[nima-recall-live] Precognition query failed: ${e.message}`);
    }
    return "";
  }
}

/**
 * Apply affect bleed from recalled memories to current affect state.
 * Memories nudge emotions - not displayed as tags, just transferred.
 */
function applyAffectBleed(bleed, identityName = "agent", conversationId = null) {
  if (!bleed || Object.keys(bleed).length === 0) {
    console.error(`[nima-recall-live] 🎭 No bleed to apply`);
    return;
  }
  
  const nimaHome = process.env.NIMA_HOME || join(os.homedir(), ".nima");
  const affectDir = join(nimaHome, "affect");
  
  // Security: Sanitize inputs to prevent path traversal attacks
  const safeIdentity = sanitizePathComponent(identityName, 64);
  const safeConvId = conversationId ? sanitizePathComponent(conversationId, 64) : null;
  
  // Determine state file path
  let statePath;
  if (safeConvId) {
    const convDir = join(affectDir, "conversations");
    if (!existsSync(convDir)) {
      mkdirSync(convDir, { recursive: true });
    }
    statePath = join(convDir, `${safeIdentity}_${safeConvId}.json`);
    console.error(`[nima-recall-live] 🎭 Looking for: ${statePath}`);
  } else {
    statePath = join(affectDir, `affect_state_${safeIdentity}.json`);
    console.error(`[nima-recall-live] 🎭 No conversationId, using: ${statePath}`);
  }
  
  if (!existsSync(statePath)) {
    // No affect state yet - nothing to bleed into
    console.error(`[nima-recall-live] 🎭 State file not found: ${statePath}`);
    return;
  }
  
  try {
    const state = JSON.parse(readFileSync(statePath, "utf-8"));
    const AFFECTS = ["SEEKING", "RAGE", "FEAR", "LUST", "CARE", "PANIC", "PLAY"];
    
    // Apply bleed to each affect dimension
    for (const affect of AFFECTS) {
      if (bleed[affect] && state.current?.values) {
        const idx = AFFECTS.indexOf(affect);
        if (idx >= 0 && idx < state.current.values.length) {
          // Nudge the affect (max 0.1 total shift per recall)
          const nudge = Math.min(0.05, Math.max(-0.05, bleed[affect]));
          state.current.values[idx] = Math.max(0, Math.min(1, state.current.values[idx] + nudge));
        }
      }
    }
    
    // Update named values
    if (state.current?.values) {
      state.current.named = Object.fromEntries(
        AFFECTS.map((name, i) => [name, state.current.values[i]])
      );
      state.current.timestamp = Date.now() / 1000;
      state.current.source = "recall_bleed";
    }
    
    writeFileSync(statePath, JSON.stringify(state, null, 2));
    console.error(`[nima-recall-live] 🎭 Applied affect bleed: SEEKING ${bleed.SEEKING?.toFixed(3) || 0}, CARE ${bleed.CARE?.toFixed(3) || 0}`);
  } catch (err) {
    console.error(`[nima-recall-live] ⚠️ Could not apply affect bleed: ${err.message}`);
  }
}

// Export metadata for gateway hook registration
export const metadata = {
  events: ["before_agent_start", "before_compaction"],
  description: "NIMA Live Recall - Injects relevant memories from graph database",
  version: "1.0.0"
};

export default function nimaRecallLivePlugin(api, config) {
  const log = api.log || console;
  const skipSubagents = config?.skipSubagents !== false;
  
  log.info?.("[nima-recall-live] Live recall hook loaded");
  
  api.on("before_agent_start", async (event, ctx) => {
    // Extract conversation ID from prompt format: [Telegram David Dorta id:5556407150 ...]
    const promptText = typeof event?.prompt === 'string' ? event.prompt : '';
    const channelMatch = promptText.match(/\[(Telegram|Discord|Signal|WhatsApp)\s+[^\]]*id:(\d+)/i);
    let conversationId = ctx?.conversationId || ctx?.channelId || ctx?.chatId || null;
    if (!conversationId && channelMatch) {
      const channel = channelMatch[1].toLowerCase();
      const id = channelMatch[2];
      conversationId = `${channel}_${id}`;
    }
    
    // TRACE: Log full context to find conversation ID
    console.error(`[nima-recall-live] 🔍 CTX: conversationId=${conversationId}, ctx.conversationId=${ctx?.conversationId}`);
    
    // Reset session state if conversation changed
    resetSessionIfNeeded(conversationId);
    
    // Fix: Clear dedup set every 5 cycles to prevent aggressive blocking
    recallCounter++;
    if (recallCounter % 5 === 0) {
      console.error(`[nima-recall-live] 🔄 Cycle ${recallCounter}: Clearing dedup cache`);
      SESSION_MEMORY_IDS.clear();
    }
    
    try {
      // Debug: log that we fired
      console.error(`[nima-recall-live] FIRED. event keys: ${Object.keys(event || {}).join(",")}, ctx keys: ${Object.keys(ctx || {}).join(",")}`);
      console.error(`[nima-recall-live] event.prompt type: ${typeof event?.prompt}, length: ${event?.prompt?.length || 0}`);
      console.error(`[nima-recall-live] event.prompt first 200: ${String(event?.prompt || "").substring(0, 200)}`);
      
      // Skip subagents and heartbeats
      if (skipSubagents && ctx.sessionKey?.includes(":subagent:")) return;
      if (ctx.sessionKey?.includes("heartbeat")) return;
      
      const userMessage = extractUserMessage(event.prompt);
      console.error(`[nima-recall-live] extracted userMessage (${userMessage.length}): ${userMessage.substring(0, 100)}`);
      console.error(`[nima-recall-live] 🚀 Running ${FTS_ONLY_MODE ? 'FTS-only' : 'HYBRID'} recall (max ${MAX_RESULTS} results)`);
      if (!userMessage || userMessage.length < MIN_QUERY_LENGTH) {
        console.error(`[nima-recall-live] SKIP: too short (${userMessage.length} < ${MIN_QUERY_LENGTH})`);
        return;
      }
      
      // Cooldown — don't query if same topic recently
      const now = Date.now();
      const queryKey = userMessage.substring(0, 100);
      if (queryKey === lastQuery && (now - lastQueryTime) < COOLDOWN_MS) {
        // Return cached result, but still apply bleed
        if (lastBleed && Object.keys(lastBleed).length > 0) {
          const conversationId = ctx.conversationId || ctx.channelId || ctx.chatId || null;
          const identityName = config?.identity_name || "agent";
          applyAffectBleed(lastBleed, identityName, conversationId);
        }
        if (lastResult) return { prependContext: lastResult };
        return;
      }
      
      console.error(`[nima-recall-live] 🚀 About to call quickRecall with: "${userMessage.substring(0,30)}"`);
      const result = await quickRecall(userMessage);
      console.error(`[nima-recall-live] ✅ Recall complete: ${result?.memories?.length || 0} memories returned`);
      
      // Handle both old array format and new {memories, affect_bleed} format
      const memories = Array.isArray(result) ? result : (result?.memories || []);
      const affectBleed = result?.affect_bleed || null;
      let formatted = formatMemories(memories);
      
      // Inject precognitions (predictions based on patterns)
      try {
        const precogText = await getPrecognitions(userMessage);
        if (precogText) {
          formatted = precogText + "\n" + formatted;
        }
      } catch (e) {
        // Silent fail - don't break recall if precog fails
      }
      
      // Debug: ALWAYS write to file to trace execution
      const debugPath = join(os.homedir(), ".nima", "recall_trace.log");
      try {
        writeFileSync(debugPath, JSON.stringify({
          timestamp: new Date().toISOString(),
          userMessage: userMessage.substring(0, 50),
          hasResult: !!result,
          memoriesCount: memories?.length || 0,
          affectBleed: affectBleed,
        }, null, 2) + "\n", { flag: "a" });
      } catch (e) {}
      
      // Apply affect bleed if present (memories nudge current emotional state)
      if (affectBleed && Object.keys(affectBleed).length > 0) {
        const identityName = config?.identity_name || "agent";  // Match nima-affect default
        
        // Use conversationId extracted from prompt at top of hook
        console.error(`[nima-recall-live] 🎭 Applying bleed: identity=${identityName}, convId=${conversationId}`);
        applyAffectBleed(affectBleed, identityName, conversationId);
      }
      
      // Cache (including bleed for re-application on cache hit)
      lastQuery = queryKey;
      lastQueryTime = now;
      lastResult = formatted;
      lastBleed = affectBleed;
      
      if (formatted) {
        log.info?.(`[nima-recall-live] Injected ${memories.length} memories`);
        return { prependContext: formatted };
      }
    } catch (err) {
      console.error(`[nima-recall-live] Error: ${err.message}`);
      return undefined;
    }
  }, { priority: 15 }); // After nima-affect (priority 10)
  
  // Register before_compaction handler for memory flush
  api.on("before_compaction", async (event, ctx) => {
    console.error(`[nima-recall-live] 🔄 PRE-COMPACTION HOOK FIRED`);
    console.error(`[nima-recall-live] event: ${JSON.stringify(event || {})}`);
    
    // Signal that the hook fired successfully
    // The actual memory flush is handled by the HEARTBEAT.md workflow
    // This hook ensures we have a chance to preserve context before compaction
    return { 
      message: "Pre-compaction memory flush. Store durable memories now (use memory/YYYY-MM-DD.md; create memory/ if needed). If nothing to store, reply with NO_REPLY."
    };
  }, { priority: 10 });
}
