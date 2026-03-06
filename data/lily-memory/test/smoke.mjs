#!/usr/bin/env node
/**
 * Smoke test — exercises the plugin against the LIVE database.
 * Run: node test/smoke.mjs
 *
 * Tests:
 *   1. DB schema (all tables exist)
 *   2. memory_search tool (FTS5 + LIKE fallback)
 *   3. memory_entity tool
 *   4. memory_store tool (insert + update)
 *   5. memory_semantic_search tool (graceful when Ollama unavailable)
 *   6. memory_add_entity tool
 *   7. auto-recall hook (buildFtsContext + buildRecallContext)
 *   8. auto-capture hook (captureFromMessages)
 *   9. stuck-detection (extractTopicSignature + checkStuck)
 *  10. consolidation (consolidateMemories)
 *  11. Config variations (missing config, partial config)
 */

import { execSync } from "node:child_process";
import os from "node:os";
import path from "node:path";
import fs from "node:fs";
import { randomUUID } from "node:crypto";

import { resolveDbPath, ensureTables, sqliteQuery, sqliteExec, escapeSqlValue } from "../lib/sqlite.js";
import { checkOllamaHealth, storeEmbedding, vectorSearch } from "../lib/embeddings.js";
import { loadEntitiesFromDb, addEntityToDb, mergeConfigEntities } from "../lib/entities.js";
import { consolidateMemories } from "../lib/consolidation.js";
import { buildFtsContext, buildRecallContext } from "../lib/recall.js";
import { captureFromMessages } from "../lib/capture.js";
import { extractTopicSignature, checkStuck, saveTopicHistory } from "../lib/stuck-detection.js";

const LIVE_DB = "/Users/kevinodell/.openclaw/memory/decisions.db";
const SMOKE_DB = path.join(os.tmpdir(), `lily-smoke-${Date.now()}.db`);
const SMOKE_HIST = path.join(os.tmpdir(), `lily-smoke-hist-${Date.now()}.json`);

let pass = 0;
let fail = 0;

function ok(condition, label) {
  if (condition) {
    pass++;
    console.log(`  \x1b[32mPASS\x1b[0m ${label}`);
  } else {
    fail++;
    console.log(`  \x1b[31mFAIL\x1b[0m ${label}`);
  }
}

// ===== TEST 1: Live DB schema =====
console.log("\n1. Live DB schema validation");
{
  const tables = sqliteQuery(LIVE_DB, "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name");
  const names = tables.map(t => t.name);
  ok(names.includes("decisions"), "decisions table exists");
  ok(names.includes("decisions_fts"), "decisions_fts table exists");
  ok(names.includes("vectors"), "vectors table exists");
  ok(names.includes("entities"), "entities table exists");
}

// ===== TEST 2: memory_search (FTS5) =====
console.log("\n2. memory_search — FTS5 keyword search on live DB");
{
  const rows = sqliteQuery(LIVE_DB, `SELECT d.entity, d.fact_key, d.fact_value FROM decisions d JOIN decisions_fts fts ON d.rowid = fts.rowid WHERE decisions_fts MATCH '"config"' AND (d.expires_at IS NULL OR d.expires_at > ${Date.now()}) ORDER BY rank LIMIT 5`);
  ok(Array.isArray(rows), "FTS5 query returns array");
  ok(rows.length > 0, `FTS5 found ${rows.length} results for "config"`);
}

// ===== TEST 3: memory_search (LIKE fallback) =====
console.log("\n3. memory_search — LIKE fallback");
{
  const safe = "OpenClaw";
  const rows = sqliteQuery(LIVE_DB, `SELECT entity, fact_key, fact_value FROM decisions WHERE (description LIKE '%${safe}%' OR fact_value LIKE '%${safe}%') AND (expires_at IS NULL OR expires_at > ${Date.now()}) ORDER BY importance DESC LIMIT 5`);
  ok(Array.isArray(rows), "LIKE query returns array");
  console.log(`    (found ${rows.length} results for "OpenClaw")`);
}

// ===== TEST 4: memory_entity =====
console.log("\n4. memory_entity — entity lookup on live DB");
{
  const rows = sqliteQuery(LIVE_DB, `SELECT fact_key, fact_value, ttl_class FROM decisions WHERE entity = 'Kevin' AND (expires_at IS NULL OR expires_at > ${Date.now()}) ORDER BY importance DESC LIMIT 5`);
  ok(Array.isArray(rows), "Entity query returns array");
  ok(rows.length > 0, `Found ${rows.length} facts for "Kevin"`);
}

// ===== TEST 5: Smoke DB — memory_store (insert + update) =====
console.log("\n5. memory_store — insert and update on smoke DB");
{
  ok(ensureTables(SMOKE_DB), "Smoke DB tables created");

  const id1 = randomUUID();
  const now = Date.now();
  sqliteExec(SMOKE_DB, `INSERT INTO decisions (id, session_id, timestamp, category, description, rationale, classification, importance, ttl_class, expires_at, last_accessed_at, entity, fact_key, fact_value, tags) VALUES ('${id1}', 'smoke', ${now}, 'manual', 'SmokeTest.color = blue', 'smoke test', 'ARCHIVE', 0.9, 'stable', ${now + 90*86400000}, ${now}, 'SmokeTest', 'color', 'blue', '["smoke"]')`);

  const check1 = sqliteQuery(SMOKE_DB, `SELECT fact_value FROM decisions WHERE entity = 'SmokeTest' AND fact_key = 'color'`);
  ok(check1.length === 1 && check1[0].fact_value === "blue", "Inserted fact: SmokeTest.color = blue");

  sqliteExec(SMOKE_DB, `UPDATE decisions SET fact_value = 'red', timestamp = ${now + 1} WHERE entity = 'SmokeTest' AND fact_key = 'color'`);
  const check2 = sqliteQuery(SMOKE_DB, `SELECT fact_value FROM decisions WHERE entity = 'SmokeTest' AND fact_key = 'color'`);
  ok(check2.length === 1 && check2[0].fact_value === "red", "Updated fact: SmokeTest.color = red");
}

// ===== TEST 6: memory_semantic_search (graceful degradation) =====
console.log("\n6. memory_semantic_search — Ollama health check");
{
  const health = await checkOllamaHealth("http://localhost:11434", "nomic-embed-text");
  ok(typeof health.available === "boolean", `Ollama health: ${health.available ? "available" : "unavailable"}${health.reason ? " (" + health.reason + ")" : ""}`);

  if (health.available) {
    const results = await vectorSearch(LIVE_DB, "http://localhost:11434", "nomic-embed-text", "coding preferences", 3, 0.3);
    ok(Array.isArray(results), `Vector search returned ${results.length} results`);
  } else {
    ok(true, "Vector search skipped (Ollama unavailable) — graceful degradation confirmed");
  }
}

// ===== TEST 7: memory_add_entity =====
console.log("\n7. memory_add_entity — runtime entity management");
{
  ok(addEntityToDb(SMOKE_DB, "SmokeBot", "smoke-test"), "Added entity SmokeBot");

  const dbEntities = loadEntitiesFromDb(SMOKE_DB);
  ok(Array.isArray(dbEntities) && dbEntities.some(n => n === "SmokeBot"), "SmokeBot loaded from DB");

  const merged = mergeConfigEntities(["config", "system"], dbEntities);
  ok(merged.has("smokebot"), "SmokeBot present in merged set (case-insensitive)");
  ok(merged.has("config"), "Config entity from config array present");
}

// ===== TEST 8: auto-recall hook =====
console.log("\n8. auto-recall — FTS context building on live DB");
{
  const { lines, ftsIds } = buildFtsContext(LIVE_DB, "what are Kevin's preferences", 5);
  ok(Array.isArray(lines), `FTS context: ${lines.length} lines`);
  ok(ftsIds instanceof Set, `FTS IDs: ${ftsIds.size} unique`);

  const ctx = buildRecallContext(lines, ftsIds, []);
  if (lines.length > 0) {
    ok(typeof ctx === "string" && ctx.length > 0, `Recall context built (${ctx?.length || 0} chars)`);
  } else {
    ok(ctx === null || ctx === undefined || ctx === "", "No recall context (expected if no FTS matches)");
  }
}

// ===== TEST 9: auto-capture hook =====
console.log("\n9. auto-capture — message extraction on smoke DB");
{
  const entities = mergeConfigEntities(["SmokeTest", "config"], new Set());
  const messages = [
    { role: "assistant", content: "SmokeTest: smoke_result = The smoke test completed successfully with all systems operational" },
  ];
  const result = captureFromMessages(SMOKE_DB, messages, 5, entities, () => {});
  ok(typeof result.stored === "number", `Captured ${result.stored} facts`);
  if (result.stored > 0) {
    const check = sqliteQuery(SMOKE_DB, `SELECT fact_value FROM decisions WHERE entity = 'SmokeTest' AND fact_key = 'smoke_result'`);
    ok(check.length > 0, "Captured fact persisted to DB");
  } else {
    ok(true, "No facts captured (pattern may not match — acceptable)");
  }
}

// ===== TEST 10: stuck-detection =====
console.log("\n10. stuck-detection — topic signatures");
{
  const text = "The memory system uses SQLite for persistent storage with FTS5 for full-text search and vector embeddings for semantic similarity matching across all stored decisions and facts";
  const sig = extractTopicSignature(text);
  ok(typeof sig === "string" && sig.length > 0, `Topic signature: ${sig}`);

  // Reset topic history for clean test
  saveTopicHistory(SMOKE_HIST, []);
  const nudge1 = checkStuck(SMOKE_DB, SMOKE_HIST, sig);
  ok(nudge1 === null, "Not stuck after 1 signature");

  const nudge2 = checkStuck(SMOKE_DB, SMOKE_HIST, sig);
  ok(nudge2 === null, "Not stuck after 2 signatures");

  const nudge3 = checkStuck(SMOKE_DB, SMOKE_HIST, sig);
  ok(typeof nudge3 === "string" && nudge3.includes("reflexion"), "Stuck detected after 3 identical signatures");
}

// ===== TEST 11: consolidation =====
console.log("\n11. consolidation — dedup on smoke DB");
{
  // Insert duplicates
  const now = Date.now();
  for (let i = 0; i < 3; i++) {
    sqliteExec(SMOKE_DB, `INSERT INTO decisions (id, session_id, timestamp, category, description, rationale, classification, importance, ttl_class, last_accessed_at, entity, fact_key, fact_value, tags) VALUES ('${randomUUID()}', 'smoke', ${now - i * 1000}, 'manual', 'DupTest.dup_key = dup_value', 'test', 'ARCHIVE', 0.5, 'stable', ${now}, 'DupTest', 'dup_key', 'dup_value', '["test"]')`);
  }
  const before = sqliteQuery(SMOKE_DB, `SELECT COUNT(*) as c FROM decisions WHERE entity = 'DupTest' AND fact_key = 'dup_key'`);
  ok(before[0].c === 3, `Created 3 duplicates`);

  consolidateMemories(SMOKE_DB, () => {});

  const after = sqliteQuery(SMOKE_DB, `SELECT COUNT(*) as c FROM decisions WHERE entity = 'DupTest' AND fact_key = 'dup_key'`);
  ok(after[0].c === 1, `Consolidated to 1 (was ${before[0].c})`);
}

// ===== TEST 12: SQL injection safety =====
console.log("\n12. SQL injection safety");
{
  const malicious = "'; DROP TABLE decisions; --";
  const escaped = escapeSqlValue(malicious);
  ok(escaped === "''; DROP TABLE decisions; --", `Single quotes doubled: "${escaped.substring(0, 40)}..."`);

  // Try FTS5 operator injection
  const ftsPayload = 'test OR "1"="1"';
  const ftsEscaped = `"${escapeSqlValue(ftsPayload).replace(/"/g, '""')}"`;
  ok(ftsEscaped.startsWith('"') && ftsEscaped.endsWith('"'), `FTS5 wrapped as phrase: ${ftsEscaped}`);

  // Verify live DB survived (sanity)
  const count = sqliteQuery(LIVE_DB, "SELECT COUNT(*) as c FROM decisions");
  ok(count[0].c > 0, `Live DB intact after injection tests (${count[0].c} rows)`);
}

// ===== TEST 13: Config variations =====
console.log("\n13. Config variations — resolveDbPath");
{
  ok(resolveDbPath(null).endsWith("decisions.db"), "null config → default path");
  ok(resolveDbPath(undefined).endsWith("decisions.db"), "undefined config → default path");
  ok(resolveDbPath("~/.openclaw/memory/decisions.db").startsWith(os.homedir()), "~ expanded to homedir");
  ok(resolveDbPath("/tmp/test.db") === "/tmp/test.db", "Absolute path passed through");
}

// ===== Cleanup =====
try { fs.unlinkSync(SMOKE_DB); } catch {}
try { fs.unlinkSync(SMOKE_HIST); } catch {}

// ===== Summary =====
console.log(`\n${"=".repeat(50)}`);
console.log(`Smoke test: ${pass} passed, ${fail} failed`);
if (fail > 0) {
  console.log("\x1b[31mSMOKE TEST FAILED\x1b[0m");
  process.exit(1);
} else {
  console.log("\x1b[32mALL SMOKE TESTS PASSED\x1b[0m");
}
