import path from "node:path";
import { randomUUID } from "node:crypto";
import { resolveDbPath, ensureTables, sqliteQuery, sqliteExec, escapeSqlValue } from "./lib/sqlite.js";
import { checkOllamaHealth, storeEmbedding, vectorSearch, backfillEmbeddings } from "./lib/embeddings.js";
import { loadEntitiesFromDb, addEntityToDb, mergeConfigEntities } from "./lib/entities.js";
import { consolidateMemories } from "./lib/consolidation.js";
import { buildFtsContext, buildRecallContext } from "./lib/recall.js";
import { captureFromMessages } from "./lib/capture.js";
import { extractTopicSignature, saveTopicHistory, checkStuck } from "./lib/stuck-detection.js";

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
  const log = api.logger || { info: (m) => console.log("[lily-memory]", m), warn: (m) => console.warn("[lily-memory]", m) };

  let vectorsAvailable = false;
  let runtimeEntities = new Set();
  let stuckNudge = null;

  // --- Service lifecycle ---
  api.registerService({ id: "lily-memory", name: "lily-memory",
    async start() {
      if (!ensureTables(dbPath)) { log.warn("lily-memory: FATAL — failed to create database tables"); return; }
      runtimeEntities = mergeConfigEntities(cfg.entities || [], loadEntitiesFromDb(dbPath));
      log.info(`Entities loaded: ${runtimeEntities.size} total`);
      sqliteExec(dbPath, `DELETE FROM decisions WHERE expires_at IS NOT NULL AND expires_at <= ${Date.now()}`);
      if (cfg.consolidation !== false) consolidateMemories(dbPath, (m) => log.info(m));
      if (vecEnabled) {
        (async () => {
          const h = await checkOllamaHealth(ollamaUrl, embModel);
          vectorsAvailable = h.available;
          log.info(`Vectors: ${vectorsAvailable ? "available" : "unavailable"}${h.reason ? " (" + h.reason + ")" : ""}`);
          if (vectorsAvailable) await backfillEmbeddings(dbPath, ollamaUrl, embModel, log);
        })().catch((e) => log.warn?.(`Vector init error: ${e.message}`));
      }
    },
    stop() { log.info("lily-memory stopped"); },
  });

  // --- Tool: memory_search ---
  api.registerTool({ name: "memory_search", label: "Memory Search",
    description: "Search persistent memory using full-text search. Use to recall facts, decisions, preferences, or past context.",
    parameters: { type: "object", properties: {
      query: { type: "string", description: "Search query (keywords)" },
      limit: { type: "number", description: "Max results (default: 10)" },
    }, required: ["query"] },
    async execute(_id, { query, limit = 10 }) {
      const now = Date.now(), safe = escapeSqlValue(query);
      const safeLimit = Math.max(1, Math.min(100, parseInt(limit, 10) || 10));
      const ftsPhrase = `"${safe.replace(/"/g, '""')}"`;
      const likeSafe = safe.replace(/%/g, '\\%').replace(/_/g, '\\_');
      let rows = sqliteQuery(dbPath, `SELECT d.entity, d.fact_key, d.fact_value, d.description, d.category, d.importance FROM decisions d JOIN decisions_fts fts ON d.rowid = fts.rowid WHERE decisions_fts MATCH '${ftsPhrase}' AND (d.expires_at IS NULL OR d.expires_at > ${now}) ORDER BY rank LIMIT ${safeLimit}`);
      if (!rows.length) rows = sqliteQuery(dbPath, `SELECT entity, fact_key, fact_value, description, category, importance FROM decisions WHERE (description LIKE '%${likeSafe}%' ESCAPE '\\' OR fact_value LIKE '%${likeSafe}%' ESCAPE '\\' OR rationale LIKE '%${likeSafe}%' ESCAPE '\\') AND (expires_at IS NULL OR expires_at > ${now}) ORDER BY importance DESC LIMIT ${safeLimit}`);
      if (!rows.length) return { content: [{ type: "text", text: "No matching memories found." }], details: { count: 0 } };
      const lines = rows.map((r, i) => r.entity && r.fact_key ? `${i+1}. **${r.entity}**.${r.fact_key} = ${r.fact_value}` : `${i+1}. [${r.category}] ${r.description}`);
      return { content: [{ type: "text", text: `Found ${rows.length} memories:\n\n${lines.join("\n")}` }], details: { count: rows.length, results: rows } };
    },
  }, { name: "memory_search" });

  // --- Tool: memory_entity ---
  api.registerTool({ name: "memory_entity", label: "Memory Entity Lookup",
    description: "Look up all known facts about a specific entity (person, config, system). Use for targeted knowledge retrieval.",
    parameters: { type: "object", properties: { entity: { type: "string", description: "Entity name" } }, required: ["entity"] },
    async execute(_id, { entity }) {
      const rows = sqliteQuery(dbPath, `SELECT fact_key, fact_value, category, importance, ttl_class FROM decisions WHERE entity = '${escapeSqlValue(entity)}' AND (expires_at IS NULL OR expires_at > ${Date.now()}) ORDER BY importance DESC, timestamp DESC LIMIT 20`);
      if (!rows.length) return { content: [{ type: "text", text: `No facts found for entity "${entity}".` }], details: { count: 0 } };
      const lines = rows.map((r) => `- **${r.fact_key}** = ${r.fact_value} _(${r.ttl_class})_`);
      return { content: [{ type: "text", text: `Facts about **${entity}** (${rows.length}):\n\n${lines.join("\n")}` }], details: { count: rows.length, results: rows } };
    },
  }, { name: "memory_entity" });

  // --- Tool: memory_store ---
  api.registerTool({ name: "memory_store", label: "Memory Store",
    description: "Save a fact to persistent memory. Use for preferences, decisions, and important information that should survive session resets.",
    parameters: { type: "object", properties: {
      entity: { type: "string", description: "Entity name" },
      key: { type: "string", description: "Fact key" },
      value: { type: "string", description: "Fact value" },
      ttl: { type: "string", description: "TTL: permanent, stable (90d), active (14d), session (24h). Default: stable" },
    }, required: ["entity", "key", "value"] },
    async execute(_id, { entity, key, value, ttl = "stable" }) {
      const now = Date.now(), se = escapeSqlValue(entity), sk = escapeSqlValue(key), sv = escapeSqlValue(value);
      const ttlMs = { permanent: null, stable: 90*86400000, active: 14*86400000, session: 86400000 };
      const tc = ttlMs[ttl] !== undefined ? ttl : "stable";
      const exp = ttlMs[tc] === null ? "NULL" : now + ttlMs[tc];
      const existing = sqliteQuery(dbPath, `SELECT id FROM decisions WHERE entity = '${se}' AND fact_key = '${sk}' AND (expires_at IS NULL OR expires_at > ${now}) LIMIT 1`);
      let aid;
      if (existing.length > 0) {
        aid = existing[0].id;
        sqliteExec(dbPath, `UPDATE decisions SET fact_value = '${sv}', timestamp = ${now}, last_accessed_at = ${now}, ttl_class = '${tc}', expires_at = ${exp} WHERE id = '${escapeSqlValue(aid)}'`);
      } else {
        aid = randomUUID();
        sqliteExec(dbPath, `INSERT INTO decisions (id, session_id, timestamp, category, description, rationale, classification, importance, ttl_class, expires_at, last_accessed_at, entity, fact_key, fact_value, tags) VALUES ('${escapeSqlValue(aid)}', 'tool', ${now}, 'manual', '${se}.${sk} = ${sv}', 'Stored via memory_store tool', 'ARCHIVE', 0.9, '${tc}', ${exp}, ${now}, '${se}', '${sk}', '${sv}', '["tool"]')`);
      }
      if (vectorsAvailable) storeEmbedding(dbPath, ollamaUrl, embModel, aid, `${entity}.${key} = ${value}`).catch((e) => log.warn?.(`lily-memory: embedding failed: ${e.message}`));
      const verb = existing.length > 0 ? "Updated" : "Stored";
      return { content: [{ type: "text", text: `${verb}: ${entity}.${key} = ${value} (${tc})` }], details: { action: verb.toLowerCase(), id: aid } };
    },
  }, { name: "memory_store" });

  // --- Tool: memory_semantic_search ---
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
      return { content: [{ type: "text", text: `Found ${rows.length} semantically similar memories:\n\n${lines.join("\n")}` }], details: { count: rows.length, results: rows } };
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

  // --- Hook: before_agent_start (recall) ---
  if (autoRecall) {
    api.on("before_agent_start", async (event) => {
      try {
        const prompt = event.prompt || "", parts = [];
        const { lines: ftsLines, ftsIds } = buildFtsContext(dbPath, prompt, maxRecallResults);
        let vec = [];
        if (vectorsAvailable && prompt.length >= 10) { try { vec = await vectorSearch(dbPath, ollamaUrl, embModel, prompt, 5, vecThreshold); } catch {} }
        const ctx = buildRecallContext(ftsLines, ftsIds, vec);
        if (ctx) parts.push(ctx);
        if (stuckEnabled && stuckNudge) { parts.push("\n" + stuckNudge); stuckNudge = null; }
        if (!parts.length) return;
        const full = parts.join("\n");
        log.info?.(`lily-memory: injecting ${full.length} chars of context`);
        return { prependContext: full };
      } catch (e) { log.warn?.(`lily-memory: recall failed: ${String(e)}`); }
    });
  }

  // --- Hook: agent_end (capture) ---
  if (autoCapture) {
    api.on("agent_end", async (event) => {
      if (!event.success || !event.messages?.length) return;
      try {
        const { stored, newDecisionIds } = captureFromMessages(dbPath, event.messages, maxCapturePerTurn, runtimeEntities, (m) => log.info(m));
        if (stored > 0) log.info?.(`lily-memory: auto-captured ${stored} facts this turn`);
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
  }

  // --- Hook: before_compaction ---
  api.on("before_compaction", async () => {
    try {
      sqliteExec(dbPath, `UPDATE decisions SET last_accessed_at = ${Date.now()} WHERE ttl_class = 'permanent'`);
      log.info("lily-memory: compaction — permanent memories touched");
    } catch (e) { log.warn?.(`lily-memory: before_compaction failed: ${String(e)}`); }
  });

  // --- Hook: after_compaction ---
  api.on("after_compaction", async () => {
    try { saveTopicHistory(histPath, []); log.info("lily-memory: topic history reset after compaction"); }
    catch (e) { log.warn?.(`lily-memory: after_compaction failed: ${String(e)}`); }
  });

  log.info(`lily-memory v5: registered (db: ${dbPath}, recall: ${autoRecall}, capture: ${autoCapture}, stuck: ${stuckEnabled}, vectors: ${vecEnabled})`);
}
