import path from "node:path";
import { randomUUID } from "node:crypto";
import { createHash } from "node:crypto";
import { resolveDbPath, ensureTables, sqliteQuery, sqliteExec, sanitizeValue, closeAllConnections } from "./lib/sqlite.js";
import { checkOllamaHealth, storeEmbedding, vectorSearch, backfillEmbeddings } from "./lib/embeddings.js";
import { loadEntitiesFromDb, addEntityToDb, mergeConfigEntities } from "./lib/entities.js";
import { consolidateMemories } from "./lib/consolidation.js";
import { buildFtsContext, buildRecallContext } from "./lib/recall.js";
import { captureFromMessages } from "./lib/capture.js";
import { extractTopicSignature, saveTopicHistory, checkStuck } from "./lib/stuck-detection.js";
import { checkSessionHealth, getContextPressure } from "./lib/session-guard.js";
import { DEFAULT_BUDGET } from "./lib/budget.js";
import { DEFAULT_PROTECTED_ENTITIES, getSecurityEvents } from "./lib/security.js";

// ============================================================================
// Lily-Memory v5 — budget-aware context injection
// ============================================================================

/** Max chars for a fact value stored via the memory_store tool. */
const STORE_MAX_VALUE_LENGTH = 200;

/** Max chars returned per tool search result. */
const TOOL_RESULT_MAX_CHARS = 4000;

/** Injection cooldown: skip if payload hash matches recent injections. */
const INJECTION_CACHE_SIZE = 3;

/** Runtime health check frequency: every Nth agent_end event. */
const HEALTH_CHECK_INTERVAL = 10;

export default function register(api) {
  const cfg = api.pluginConfig || {};
  const dbPath = resolveDbPath(cfg.dbPath);
  const autoRecall = cfg.autoRecall !== false;
  const autoCapture = cfg.autoCapture !== false;
  const maxRecallResults = cfg.maxRecallResults || 10;
  const maxCapturePerTurn = cfg.maxCapturePerTurn || 5;
  const stuckEnabled = cfg.stuckDetection !== false;
  const vecEnabled = cfg.vectorSearch !== false;
  const ollamaUrl = cfg.ollamaUrl || "http://localhost:11434";
  const embModel = cfg.embeddingModel || "nomic-embed-text";
  const vecThreshold = cfg.vectorSimilarityThreshold || 0.5;
  const histPath = cfg.topicHistoryPath || path.join(path.dirname(dbPath), "topic-history.json");
  const baseBudget = cfg.injectionBudget || DEFAULT_BUDGET;
  const contextCap = cfg.contextTokenCap || 120000;
  const capturePolicy = cfg.capturePolicy || "all";
  const log = api.logger || { info: (m) => console.log("[lily-memory]", m), warn: (m) => console.warn("[lily-memory]", m) };

  // Build protected entities set from config + defaults
  const protectedEntities = new Set(DEFAULT_PROTECTED_ENTITIES);
  if (Array.isArray(cfg.protectedEntities)) {
    for (const e of cfg.protectedEntities) {
      if (e && typeof e === "string") protectedEntities.add(e.toLowerCase());
    }
  }

  const securityOpts = { protectedEntities, capturePolicy };

  let vectorsAvailable = false;
  let runtimeEntities = new Set();
  let stuckNudge = null;

  // --- Injection cooldown state ---
  const recentInjectionHashes = [];
  let turnCounter = 0;
  let currentPressureScale = 1.0;

  function hashPayload(text) {
    return createHash("md5").update(text).digest("hex").substring(0, 12);
  }

  // --- Service lifecycle ---
  api.registerService({ id: "lily-memory", name: "lily-memory",
    async start() {
      if (!ensureTables(dbPath)) { log.warn("lily-memory: FATAL — failed to create database tables"); return; }
      runtimeEntities = mergeConfigEntities(cfg.entities || [], loadEntitiesFromDb(dbPath));
      log.info(`Entities loaded: ${runtimeEntities.size} total`);
      sqliteExec(dbPath, `DELETE FROM decisions WHERE expires_at IS NOT NULL AND expires_at <= ?`, [Date.now()]);
      if (cfg.consolidation !== false) consolidateMemories(dbPath, (m) => log.info(m));
      // Session health guard — reset overflowing sessions
      const guard = checkSessionHealth({ threshold: cfg.sessionOverflowThreshold || 0.8, log: (m) => log.info(m) });
      if (guard.reset.length > 0) log.warn(`Session overflow: ${guard.reset.join(", ")} auto-reset`);
      if (vecEnabled) {
        (async () => {
          const h = await checkOllamaHealth(ollamaUrl, embModel);
          vectorsAvailable = h.available;
          log.info(`Vectors: ${vectorsAvailable ? "available" : "unavailable"}${h.reason ? " (" + h.reason + ")" : ""}`);
          if (vectorsAvailable) await backfillEmbeddings(dbPath, ollamaUrl, embModel, log);
        })().catch((e) => log.warn?.(`Vector init error: ${e.message}`));
      }
    },
    stop() {
      closeAllConnections();
      log.info("lily-memory stopped");
    },
  });

  // --- Tool: memory_search (output-capped) ---
  api.registerTool({ name: "memory_search", label: "Memory Search",
    description: "Search persistent memory using full-text search. Use to recall facts, decisions, preferences, or past context.",
    parameters: { type: "object", properties: {
      query: { type: "string", description: "Search query (keywords)" },
      limit: { type: "number", description: "Max results (default: 10)" },
    }, required: ["query"] },
    async execute(_id, { query, limit = 10 }) {
      const now = Date.now();
      const safeLimit = Math.max(1, Math.min(100, parseInt(limit, 10) || 10));

      // FTS5 search with parameterized query
      let rows = sqliteQuery(dbPath, `
        SELECT d.entity, d.fact_key, d.fact_value, d.description, d.category, d.importance
        FROM decisions d
        JOIN decisions_fts fts ON d.rowid = fts.rowid
        WHERE decisions_fts MATCH ?
          AND (d.expires_at IS NULL OR d.expires_at > ?)
        ORDER BY rank
        LIMIT ?
      `, [query, now, safeLimit]);

      // Fallback to LIKE search
      if (!rows.length) {
        const likePattern = `%${query}%`;
        rows = sqliteQuery(dbPath, `
          SELECT entity, fact_key, fact_value, description, category, importance
          FROM decisions
          WHERE (description LIKE ? OR fact_value LIKE ? OR rationale LIKE ?)
            AND (expires_at IS NULL OR expires_at > ?)
          ORDER BY importance DESC
          LIMIT ?
        `, [likePattern, likePattern, likePattern, now, safeLimit]);
      }

      if (!rows.length) return { content: [{ type: "text", text: "No matching memories found." }], details: { count: 0 } };
      const lines = rows.map((r, i) => r.entity && r.fact_key ? `${i+1}. **${r.entity}**.${r.fact_key} = ${r.fact_value}` : `${i+1}. [${r.category}] ${r.description}`);
      let text = `Found ${rows.length} memories:\n\n${lines.join("\n")}`;
      if (text.length > TOOL_RESULT_MAX_CHARS) text = text.substring(0, TOOL_RESULT_MAX_CHARS - 20) + "\n\n...(truncated)";
      return { content: [{ type: "text", text }], details: { count: rows.length, results: rows } };
    },
  }, { name: "memory_search" });

  // --- Tool: memory_entity (output-capped) ---
  api.registerTool({ name: "memory_entity", label: "Memory Entity Lookup",
    description: "Look up all known facts about a specific entity (person, config, system). Use for targeted knowledge retrieval.",
    parameters: { type: "object", properties: { entity: { type: "string", description: "Entity name" } }, required: ["entity"] },
    async execute(_id, { entity }) {
      const rows = sqliteQuery(dbPath, `
        SELECT fact_key, fact_value, category, importance, ttl_class
        FROM decisions
        WHERE entity = ?
          AND (expires_at IS NULL OR expires_at > ?)
        ORDER BY importance DESC, timestamp DESC
        LIMIT 20
      `, [entity, Date.now()]);
      if (!rows.length) return { content: [{ type: "text", text: `No facts found for entity "${entity}".` }], details: { count: 0 } };
      const lines = rows.map((r) => `- **${r.fact_key}** = ${r.fact_value} _(${r.ttl_class})_`);
      let text = `Facts about **${entity}** (${rows.length}):\n\n${lines.join("\n")}`;
      if (text.length > TOOL_RESULT_MAX_CHARS) text = text.substring(0, TOOL_RESULT_MAX_CHARS - 20) + "\n\n...(truncated)";
      return { content: [{ type: "text", text }], details: { count: rows.length, results: rows } };
    },
  }, { name: "memory_entity" });

  // --- Tool: memory_store (VALUE LENGTH CAPPED) ---
  api.registerTool({ name: "memory_store", label: "Memory Store",
    description: `Save a fact to persistent memory. Values are capped at ${STORE_MAX_VALUE_LENGTH} chars. Use concise key=value pairs, not paragraphs. For preferences, decisions, and important information that should survive session resets.`,
    parameters: { type: "object", properties: {
      entity: { type: "string", description: "Entity name" },
      key: { type: "string", description: "Fact key" },
      value: { type: "string", description: `Fact value (max ${STORE_MAX_VALUE_LENGTH} chars — be concise)` },
      ttl: { type: "string", description: "TTL: permanent, stable (90d), active (14d), session (24h). Default: stable" },
    }, required: ["entity", "key", "value"] },
    async execute(_id, { entity, key, value, ttl = "stable" }) {
      // Enforce value length cap
      if (value && value.length > STORE_MAX_VALUE_LENGTH) {
        value = value.substring(0, STORE_MAX_VALUE_LENGTH - 3) + "...";
        log.info?.(`lily-memory: memory_store value truncated to ${STORE_MAX_VALUE_LENGTH} chars for ${entity}.${key}`);
      }

      const now = Date.now();
      const se = sanitizeValue(entity), sk = sanitizeValue(key), sv = sanitizeValue(value);
      const ttlMs = { permanent: null, stable: 90*86400000, active: 14*86400000, session: 86400000 };
      let tc = ttlMs[ttl] !== undefined ? ttl : "stable";

      // Status keyword auto-downgrade
      const STATUS_KEYWORDS = /(?:status|complete|deployed|spawned|launched|ready|sprint|checklist|final_state|session_|restart|attempt|debug|fix_|milestone|infrastructure|live_|validation_)/i;
      if (STATUS_KEYWORDS.test(key) && (tc === "permanent" || tc === "stable")) {
        tc = "active";
      }

      const exp = ttlMs[tc] === null ? null : now + ttlMs[tc];

      // Permanent cap — max 15 permanent entries
      if (tc === "permanent") {
        const permCount = sqliteQuery(dbPath, `SELECT COUNT(*) as cnt FROM decisions WHERE ttl_class = 'permanent'`);
        if (permCount[0]?.cnt >= 15) {
          const oldest = sqliteQuery(dbPath, `SELECT id FROM decisions WHERE ttl_class = 'permanent' ORDER BY timestamp ASC LIMIT 1`);
          if (oldest.length > 0) {
            sqliteExec(dbPath,
              `UPDATE decisions SET ttl_class = 'stable', expires_at = ? WHERE id = ?`,
              [now + 90*86400000, oldest[0].id]
            );
          }
        }
      }

      const existing = sqliteQuery(dbPath,
        `SELECT id FROM decisions WHERE entity = ? AND fact_key = ? AND (expires_at IS NULL OR expires_at > ?) LIMIT 1`,
        [se, sk, now]
      );
      let aid;
      if (existing.length > 0) {
        aid = existing[0].id;
        sqliteExec(dbPath,
          `UPDATE decisions SET fact_value = ?, timestamp = ?, last_accessed_at = ?, ttl_class = ?, expires_at = ? WHERE id = ?`,
          [sv, now, now, tc, exp, aid]
        );
      } else {
        aid = randomUUID();
        const description = `${se}.${sk} = ${sv}`;
        sqliteExec(dbPath,
          `INSERT INTO decisions (id, session_id, timestamp, category, description, rationale, classification, importance, ttl_class, expires_at, last_accessed_at, entity, fact_key, fact_value, tags)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`,
          [aid, 'tool', now, 'manual', description, 'Stored via memory_store tool', 'ARCHIVE', 0.9, tc, exp, now, se, sk, sv, '["tool"]']
        );
      }
      if (vectorsAvailable) storeEmbedding(dbPath, ollamaUrl, embModel, aid, `${entity}.${key} = ${value}`).catch((e) => log.warn?.(`lily-memory: embedding failed: ${e.message}`));
      const verb = existing.length > 0 ? "Updated" : "Stored";
      return { content: [{ type: "text", text: `${verb}: ${entity}.${key} = ${value} (${tc})` }], details: { action: verb.toLowerCase(), id: aid } };
    },
  }, { name: "memory_store" });

  // --- Tool: memory_semantic_search (output-capped) ---
  api.registerTool({ name: "memory_semantic_search", label: "Memory Semantic Search",
    description: "Search memory using semantic similarity (vector embeddings). Finds related memories even when exact keywords don't match.",
    parameters: { type: "object", properties: {
      query: { type: "string", description: "Natural language search query" },
      limit: { type: "number", description: "Max results (default: 5)" },
      threshold: { type: "number", description: "Min similarity 0-1 (default: 0.5)" },
    }, required: ["query"] },
    async execute(_id, params) {
      if (!vectorsAvailable) return { content: [{ type: "text", text: "Semantic search is unavailable (Ollama embeddings not configured). Use memory_search for keyword search." }], details: { count: 0, reason: "vectors_unavailable" } };
      const { query, limit = 5, threshold = vecThreshold } = params;
      const safeLimit = Math.max(1, Math.min(50, parseInt(limit, 10) || 5));
      const rows = await vectorSearch(dbPath, ollamaUrl, embModel, query, safeLimit, threshold);
      if (!rows.length) return { content: [{ type: "text", text: "No semantically similar memories found." }], details: { count: 0 } };
      const lines = rows.map((r, i) => { const s = (r.similarity*100).toFixed(0); return r.entity && r.fact_key ? `${i+1}. **${r.entity}**.${r.fact_key} = ${r.fact_value} _(${s}% similar)_` : `${i+1}. [${r.category}] ${r.description} _(${s}% similar)_`; });
      let text = `Found ${rows.length} semantically similar memories:\n\n${lines.join("\n")}`;
      if (text.length > TOOL_RESULT_MAX_CHARS) text = text.substring(0, TOOL_RESULT_MAX_CHARS - 20) + "\n\n...(truncated)";
      return { content: [{ type: "text", text }], details: { count: rows.length, results: rows } };
    },
  }, { name: "memory_semantic_search" });

  // --- Tool: memory_add_entity ---
  api.registerTool({ name: "memory_add_entity", label: "Add Memory Entity",
    description: "Register a new entity name so the memory system recognizes it during auto-capture.",
    parameters: { type: "object", properties: { name: { type: "string", description: "Entity name (letters, numbers, dots, underscores)" } }, required: ["name"] },
    async execute(_id, { name }) {
      if (!name || typeof name !== "string" || !/^[A-Za-z][A-Za-z0-9_.]*$/.test(name) || name.length < 2 || name.length > 60)
        return { content: [{ type: "text", text: `Invalid entity name "${name}". Must start with a letter, 2-60 chars, only letters/numbers/dots/underscores.` }] };
      if (!addEntityToDb(dbPath, name, "tool")) return { content: [{ type: "text", text: `Failed to register entity "${name}".` }] };
      runtimeEntities.add(name.toLowerCase());
      return { content: [{ type: "text", text: `Entity "${name}" registered (${runtimeEntities.size} total).` }] };
    },
  }, { name: "memory_add_entity" });

  // --- Tool: memory_security_log ---
  api.registerTool({ name: "memory_security_log", label: "Memory Security Log",
    description: "View recent blocked injection attempts against persistent memory. Use to identify suspicious sources and potential prompt injection attacks.",
    parameters: { type: "object", properties: {
      limit: { type: "number", description: "Max events to return (default: 10)" },
      since_hours: { type: "number", description: "Hours to look back (default: 24)" },
    } },
    async execute(_id, { limit = 10, since_hours = 24 } = {}) {
      const safeLimit = Math.max(1, Math.min(50, parseInt(limit, 10) || 10));
      const sinceMs = Date.now() - (Math.max(1, parseInt(since_hours, 10) || 24) * 3600000);
      const rows = getSecurityEvents(dbPath, sinceMs, safeLimit);
      if (!rows.length) return { content: [{ type: "text", text: "No security events in the specified time window." }], details: { count: 0 } };
      const lines = rows.map((r, i) => {
        const time = new Date(r.timestamp).toISOString();
        return `${i+1}. **${r.event_type}** [${time}]\n   Source: ${r.source_role} | Entity: ${r.entity} | Key: ${r.fact_key}\n   Value: ${r.fact_value}\n   Pattern: ${r.matched_pattern}\n   Snippet: ${r.source_snippet ? r.source_snippet.substring(0, 100) + "..." : "n/a"}`;
      });
      let text = `Security events (${rows.length}):\n\n${lines.join("\n\n")}`;
      if (text.length > TOOL_RESULT_MAX_CHARS) text = text.substring(0, TOOL_RESULT_MAX_CHARS - 20) + "\n\n...(truncated)";
      return { content: [{ type: "text", text }], details: { count: rows.length, events: rows } };
    },
  }, { name: "memory_security_log" });

  // --- Hook: before_agent_start (budget-aware recall with injection cooldown) ---
  if (autoRecall) {
    api.on("before_agent_start", async (event) => {
      try {
        // Apply context pressure scaling to budget
        const effectiveBudget = Math.floor(baseBudget * currentPressureScale);

        // If pressure is critical, skip injection entirely
        if (effectiveBudget <= 0) {
          log.info?.("lily-memory: injection skipped (context pressure: critical)");
          return;
        }

        const prompt = event.prompt || "", parts = [];

        // Build budget-aware FTS context
        const { lines: ftsLines, ftsIds, budgetReport } = buildFtsContext(dbPath, prompt, maxRecallResults, effectiveBudget);

        // Vector search uses remaining budget
        let vec = [];
        if (vectorsAvailable && prompt.length >= 10 && budgetReport.remaining > 100) {
          try { vec = await vectorSearch(dbPath, ollamaUrl, embModel, prompt, 5, vecThreshold); } catch {}
        }

        const ctx = buildRecallContext(ftsLines, ftsIds, vec, budgetReport.remaining);
        if (ctx) parts.push(ctx);

        if (stuckEnabled && stuckNudge) { parts.push("\n" + stuckNudge); stuckNudge = null; }
        if (!parts.length) return;

        const full = parts.join("\n");

        // Injection cooldown: skip if identical to recent injections
        const payloadHash = hashPayload(full);
        if (recentInjectionHashes.includes(payloadHash)) {
          log.info?.(`lily-memory: injection skipped (duplicate, hash ${payloadHash})`);
          return;
        }
        recentInjectionHashes.push(payloadHash);
        if (recentInjectionHashes.length > INJECTION_CACHE_SIZE) {
          recentInjectionHashes.shift();
        }

        log.info?.(`lily-memory: injecting ${full.length} chars (budget: ${effectiveBudget}, used: ${budgetReport.used}, pressure: ${currentPressureScale})`);
        return { prependContext: full };
      } catch (e) { log.warn?.(`lily-memory: recall failed: ${String(e)}`); }
    });
  }

  // --- Hook: agent_end (capture + runtime health check) ---
  if (autoCapture) {
    api.on("agent_end", async (event) => {
      turnCounter++;

      // Runtime context pressure check (every HEALTH_CHECK_INTERVAL turns)
      if (turnCounter % HEALTH_CHECK_INTERVAL === 0) {
        const messageCount = event.messages?.length || 0;
        const pressure = getContextPressure({
          messageCount,
          contextCap,
          log: (m) => log.info?.(m),
        });
        currentPressureScale = pressure.scale;
        if (pressure.level === "critical") {
          log.warn?.(`lily-memory: context pressure CRITICAL — injection disabled until session resets`);
        }
      }

      if (!event.success || !event.messages?.length) return;
      try {
        const { stored, newDecisionIds, blocked } = captureFromMessages(dbPath, event.messages, maxCapturePerTurn, runtimeEntities, (m) => log.info(m), securityOpts);
        if (stored > 0) log.info?.(`lily-memory: auto-captured ${stored} facts this turn`);
        if (blocked > 0) log.warn?.(`lily-memory: SECURITY — blocked ${blocked} suspicious fact(s) this turn`);
        if (vectorsAvailable && newDecisionIds.length > 0) {
          (async () => { for (const { id, text } of newDecisionIds) await storeEmbedding(dbPath, ollamaUrl, embModel, id, text); })().catch((e) => log.warn?.(`lily-memory: batch embedding failed: ${e.message}`));
        }
        if (stuckEnabled) {
          const last = [...event.messages].reverse().find((m) => m?.role === "assistant");
          if (last) {
            const txt = typeof last.content === "string" ? last.content : Array.isArray(last.content) ? last.content.filter((b) => b?.type === "text").map((b) => b.text).join(" ") : "";
            const sig = extractTopicSignature(txt);
            if (sig) { stuckNudge = checkStuck(dbPath, histPath, sig); log.info?.(`lily-memory: topic sig: ${sig}`); }
          }
        }
      } catch (e) { log.warn?.(`lily-memory: capture failed: ${String(e)}`); }
    });
  } else {
    // Even without auto-capture, run health checks
    api.on("agent_end", async (event) => {
      turnCounter++;
      if (turnCounter % HEALTH_CHECK_INTERVAL === 0) {
        const messageCount = event.messages?.length || 0;
        const pressure = getContextPressure({ messageCount, contextCap, log: (m) => log.info?.(m) });
        currentPressureScale = pressure.scale;
      }
    });
  }

  // --- Hook: before_compaction ---
  api.on("before_compaction", async () => {
    try {
      sqliteExec(dbPath,
        `UPDATE decisions SET last_accessed_at = ? WHERE ttl_class = 'permanent'`,
        [Date.now()]
      );
      log.info("lily-memory: compaction — permanent memories touched");
    } catch (e) { log.warn?.(`lily-memory: before_compaction failed: ${String(e)}`); }
  });

  // --- Hook: after_compaction ---
  api.on("after_compaction", async () => {
    try {
      // Reset injection cache — compaction changes context significantly
      recentInjectionHashes.length = 0;
      // Reset pressure scale — compaction frees context
      currentPressureScale = 1.0;
      turnCounter = 0;
      saveTopicHistory(histPath, []);
      log.info("lily-memory: post-compaction reset (injection cache cleared, pressure reset)");
    } catch (e) { log.warn?.(`lily-memory: after_compaction failed: ${String(e)}`); }
  });

  log.info(`lily-memory v5: registered (db: ${dbPath}, recall: ${autoRecall}, capture: ${autoCapture}, stuck: ${stuckEnabled}, vectors: ${vecEnabled}, budget: ${baseBudget} chars)`);
}
