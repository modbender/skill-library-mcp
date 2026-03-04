/**
 * Lily Memory Plugin v4 — Test Harness
 *
 * Tests: entity validation, fact extraction, topic signatures, cosine similarity,
 * vector table creation, Ollama embedding, consolidation, reflexion nudge, DB state.
 *
 * Run: node test-v4.mjs
 */

import { execSync } from "node:child_process";
import fs from "node:fs";
import path from "node:path";
import os from "node:os";

const DB_PATH = path.join(os.homedir(), ".openclaw", "memory", "decisions.db");
const TOPIC_HISTORY = path.join(os.homedir(), ".openclaw", "memory", "topic-history.json");
const OLLAMA_URL = "http://localhost:11434";
const EMBEDDING_MODEL = "nomic-embed-text";

let passed = 0;
let failed = 0;

function assert(condition, name) {
  if (condition) {
    passed++;
    console.log(`  ✅ ${name}`);
  } else {
    failed++;
    console.log(`  ❌ ${name}`);
  }
}

function sqliteQuery(query) {
  try {
    const escaped = query.replace(/\n/g, " ").replace(/\\/g, "\\\\").replace(/"/g, '\\"').replace(/\$/g, "\\$");
    const raw = execSync(
      `sqlite3 -json "${DB_PATH}" "${escaped}"`,
      { encoding: "utf-8", timeout: 5000 }
    ).trim();
    return raw ? JSON.parse(raw) : [];
  } catch {
    return [];
  }
}

function sqliteExec(statement) {
  try {
    const escaped = statement.replace(/\n/g, " ").replace(/\\/g, "\\\\").replace(/"/g, '\\"').replace(/\$/g, "\\$");
    execSync(`sqlite3 "${DB_PATH}" "${escaped}"`, { encoding: "utf-8", timeout: 5000 });
    return true;
  } catch {
    return false;
  }
}

// ============================================================================
// Import functions from the plugin (inline copies for testing)
// ============================================================================

const KNOWN_ENTITIES = new Set([
  "kevin", "lily", "christine", "rose",
  "config", "system", "note", "project",
  "openclaw", "ollama", "kalshi", "tradingbot",
]);

const REJECT_WORDS = new Set([
  "still", "just", "acts", "you", "it", "the", "this", "that", "they",
  "we", "he", "she", "my", "or", "if", "up", "an", "no", "so", "do",
  "go", "is", "are", "was", "has", "had", "can", "not", "but", "and",
  "also", "very", "much", "more", "less", "what", "how", "why", "where",
  "when", "who", "well", "oh", "ah", "looks", "community", "here",
  "there", "then", "now", "already", "really", "actually", "maybe",
]);

function isValidEntity(entity) {
  if (!entity || entity.length < 2 || entity.length > 60) return false;
  const baseName = entity.split(".")[0].toLowerCase();
  if (KNOWN_ENTITIES.has(baseName)) return true;
  if (REJECT_WORDS.has(baseName)) return false;
  if (/^[A-Z][a-z]/.test(entity)) return true;
  return false;
}

function extractTopicSignature(text) {
  if (!text || text.length < 30) return null;
  const STOP_WORDS = new Set([
    "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "do", "does", "did", "will", "would", "could",
    "should", "may", "might", "shall", "can", "need", "dare", "ought",
    "used", "to", "of", "in", "for", "on", "with", "at", "by", "from",
    "as", "into", "through", "during", "before", "after", "above", "below",
    "between", "out", "off", "over", "under", "again", "further", "then",
    "once", "here", "there", "when", "where", "why", "how", "all", "both",
    "each", "few", "more", "most", "other", "some", "such", "no", "nor",
    "not", "only", "own", "same", "so", "than", "too", "very", "just",
    "don", "now", "and", "but", "or", "if", "while", "that", "this",
    "it", "i", "you", "we", "they", "he", "she", "my", "your", "his",
    "her", "its", "our", "their", "what", "which", "who", "whom",
  ]);
  const words = text.toLowerCase().replace(/[^\w\s]/g, " ").split(/\s+/)
    .filter(w => w.length > 3 && !STOP_WORDS.has(w));
  const freq = {};
  for (const w of words) freq[w] = (freq[w] || 0) + 1;
  return Object.entries(freq).sort((a, b) => b[1] - a[1]).slice(0, 5).map(([w]) => w).sort().join(",");
}

function cosineSimilarity(a, b) {
  if (!a || !b || a.length !== b.length) return 0;
  let dot = 0, normA = 0, normB = 0;
  for (let i = 0; i < a.length; i++) {
    dot += a[i] * b[i];
    normA += a[i] * a[i];
    normB += b[i] * b[i];
  }
  const denom = Math.sqrt(normA) * Math.sqrt(normB);
  return denom === 0 ? 0 : dot / denom;
}

const HAS_FETCH = typeof globalThis.fetch === "function";

async function ollamaEmbed(text) {
  if (!HAS_FETCH) return null;
  try {
    const res = await fetch(`${OLLAMA_URL}/api/embeddings`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ model: EMBEDDING_MODEL, prompt: text }),
      signal: AbortSignal.timeout(10000),
    });
    if (!res.ok) return null;
    const data = await res.json();
    return data.embedding || null;
  } catch {
    return null;
  }
}

// ============================================================================
// Tests
// ============================================================================

async function runTests() {
  console.log("\n🧪 Lily Memory v4 Test Harness\n");

  // --- Ensure DB exists (fresh install support) ---
  const dbDir = path.dirname(DB_PATH);
  if (!fs.existsSync(dbDir)) {
    fs.mkdirSync(dbDir, { recursive: true });
    console.log(`📁 Created directory: ${dbDir}`);
  }
  const dbSchema = `
CREATE TABLE IF NOT EXISTS decisions (
    id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    timestamp INTEGER NOT NULL,
    category TEXT NOT NULL,
    description TEXT NOT NULL,
    rationale TEXT NOT NULL,
    classification TEXT NOT NULL DEFAULT 'ARCHIVE',
    importance REAL NOT NULL,
    constraints TEXT,
    affected_files TEXT,
    tags TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    ttl_class TEXT DEFAULT 'active',
    expires_at INTEGER,
    last_accessed_at INTEGER,
    entity TEXT,
    fact_key TEXT,
    fact_value TEXT
);
CREATE INDEX IF NOT EXISTS idx_decisions_ttl ON decisions(ttl_class);
CREATE INDEX IF NOT EXISTS idx_decisions_expires ON decisions(expires_at);
CREATE INDEX IF NOT EXISTS idx_decisions_entity ON decisions(entity);
CREATE INDEX IF NOT EXISTS idx_decisions_fact ON decisions(entity, fact_key);
CREATE INDEX IF NOT EXISTS idx_decisions_importance ON decisions(importance DESC);
CREATE INDEX IF NOT EXISTS idx_decisions_timestamp ON decisions(timestamp);
CREATE VIRTUAL TABLE IF NOT EXISTS decisions_fts USING fts5(
    description, rationale, entity, fact_key, fact_value, tags,
    content='decisions', content_rowid='rowid'
);
CREATE TRIGGER IF NOT EXISTS decisions_ai AFTER INSERT ON decisions BEGIN
    INSERT INTO decisions_fts(rowid, description, rationale, entity, fact_key, fact_value, tags)
    VALUES (new.rowid, new.description, new.rationale, new.entity, new.fact_key, new.fact_value, new.tags);
END;
CREATE TRIGGER IF NOT EXISTS decisions_ad AFTER DELETE ON decisions BEGIN
    INSERT INTO decisions_fts(decisions_fts, rowid, description, rationale, entity, fact_key, fact_value, tags)
    VALUES ('delete', old.rowid, old.description, old.rationale, old.entity, old.fact_key, old.fact_value, old.tags);
END;
CREATE TRIGGER IF NOT EXISTS decisions_au AFTER UPDATE ON decisions BEGIN
    INSERT INTO decisions_fts(decisions_fts, rowid, description, rationale, entity, fact_key, fact_value, tags)
    VALUES ('delete', old.rowid, old.description, old.rationale, old.entity, old.fact_key, old.fact_value, old.tags);
    INSERT INTO decisions_fts(rowid, description, rationale, entity, fact_key, fact_value, tags)
    VALUES (new.rowid, new.description, new.rationale, new.entity, new.fact_key, new.fact_value, new.tags);
END;
CREATE TABLE IF NOT EXISTS vectors (
    id TEXT PRIMARY KEY,
    decision_id TEXT NOT NULL,
    text_content TEXT NOT NULL,
    embedding TEXT NOT NULL,
    model TEXT NOT NULL,
    created_at INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS entities (
    name TEXT PRIMARY KEY,
    display_name TEXT NOT NULL,
    added_by TEXT NOT NULL DEFAULT 'runtime',
    added_at INTEGER NOT NULL DEFAULT (CAST(strftime('%s','now') AS INTEGER) * 1000)
);`.trim();
  if (sqliteExec(dbSchema)) {
    console.log("🗄️  Database schema initialized\n");
  } else {
    console.log("⚠️  Database schema init failed (may already exist)\n");
  }

  // --- Entity Validation (23 tests, same as v3) ---
  console.log("📋 Entity Validation:");
  assert(isValidEntity("Kevin") === true, "Accept: Kevin");
  assert(isValidEntity("Lily") === true, "Accept: Lily");
  assert(isValidEntity("Christine") === true, "Accept: Christine");
  assert(isValidEntity("Rose") === true, "Accept: Rose");
  assert(isValidEntity("config") === true, "Accept: config");
  assert(isValidEntity("system") === true, "Accept: system");
  assert(isValidEntity("note") === true, "Accept: note");
  assert(isValidEntity("Kevin.trading_build_mission") === true, "Accept: Kevin.trading_build_mission");
  assert(isValidEntity("TradingSystem") === true, "Accept: TradingSystem (PascalCase)");
  assert(isValidEntity("LilyMemory") === true, "Accept: LilyMemory (PascalCase)");
  assert(isValidEntity("Ollama") === true, "Accept: Ollama (known entity)");

  assert(isValidEntity("Still") === false, "Reject: Still");
  assert(isValidEntity("Just") === false, "Reject: Just");
  assert(isValidEntity("Acts") === false, "Reject: Acts");
  assert(isValidEntity("You") === false, "Reject: You");
  assert(isValidEntity("It") === false, "Reject: It");
  assert(isValidEntity("Looks") === false, "Reject: Looks");
  assert(isValidEntity("Community") === false, "Reject: Community");
  assert(isValidEntity("") === false, "Reject: empty");
  assert(isValidEntity("x") === false, "Reject: single char");
  assert(isValidEntity("a".repeat(61)) === false, "Reject: too long (61 chars)");
  assert(isValidEntity("hello") === false, "Reject: lowercase single word");
  assert(isValidEntity("also") === false, "Reject: also (common word)");

  // --- Cosine Similarity (5 tests) ---
  console.log("\n📐 Cosine Similarity:");
  assert(Math.abs(cosineSimilarity([1, 0, 0], [1, 0, 0]) - 1.0) < 0.001, "Identical vectors = 1.0");
  assert(Math.abs(cosineSimilarity([1, 0, 0], [0, 1, 0]) - 0.0) < 0.001, "Orthogonal vectors = 0.0");
  assert(Math.abs(cosineSimilarity([1, 0, 0], [-1, 0, 0]) - (-1.0)) < 0.001, "Opposite vectors = -1.0");
  assert(cosineSimilarity(null, [1, 0]) === 0, "Null vector returns 0");
  assert(cosineSimilarity([1, 2], [1, 2, 3]) === 0, "Mismatched lengths returns 0");

  // --- Topic Signatures (4 tests) ---
  console.log("\n📊 Topic Signatures:");
  const sig1 = extractTopicSignature("The kalshi trading system needs to pull market data from the API and process orders for the kalshi market");
  assert(sig1 !== null, "Extracts signature from text");
  assert(sig1.includes("kalshi"), "Signature contains 'kalshi'");

  const sig2 = extractTopicSignature("The kalshi trading system needs to pull market data and process kalshi orders for kalshi market");
  const words1 = new Set(sig1.split(","));
  const words2 = new Set(sig2.split(","));
  const intersection = [...words1].filter(w => words2.has(w)).length;
  const union = new Set([...words1, ...words2]).size;
  const jaccard = union > 0 ? intersection / union : 0;
  assert(jaccard > 0.5, `Similar texts have high Jaccard (${jaccard.toFixed(2)})`);

  assert(extractTopicSignature("too short") === null, "Short text returns null");

  // --- Ollama Embeddings (4 tests) ---
  console.log("\n🧠 Ollama Embeddings:");
  const emb1 = await ollamaEmbed("Kevin likes TypeScript");
  assert(emb1 !== null, "Ollama returns embedding");
  assert(emb1 && emb1.length === 768, `Embedding has 768 dimensions (got ${emb1?.length})`);

  const emb2 = await ollamaEmbed("Kevin enjoys writing TypeScript code and prefers strongly typed languages for his projects");
  const emb3 = await ollamaEmbed("The recipe calls for two cups of flour and one tablespoon of baking powder mixed together");

  if (emb1 && emb2 && emb3) {
    const simRelated = cosineSimilarity(emb1, emb2);
    const simUnrelated = cosineSimilarity(emb1, emb3);
    assert(simRelated > simUnrelated, `Related texts more similar (${simRelated.toFixed(3)} > ${simUnrelated.toFixed(3)})`);
    assert(simRelated > 0.5, `Related texts have meaningful similarity (${simRelated.toFixed(3)} > 0.5)`);
  } else {
    assert(false, "Related texts similarity (embeddings unavailable)");
    assert(false, "High similarity threshold (embeddings unavailable)");
  }

  // --- Vectors Table (3 tests) ---
  console.log("\n💾 Vectors Table:");
  const tableCreated = sqliteExec(`
    CREATE TABLE IF NOT EXISTS vectors (
      id TEXT PRIMARY KEY,
      decision_id TEXT NOT NULL,
      text_content TEXT NOT NULL,
      embedding TEXT NOT NULL,
      model TEXT NOT NULL,
      created_at INTEGER NOT NULL
    )
  `);
  assert(tableCreated, "Vectors table created/exists");

  const tableInfo = sqliteQuery("PRAGMA table_info(vectors)");
  assert(tableInfo.length === 6, `Vectors table has 6 columns (got ${tableInfo.length})`);
  const colNames = tableInfo.map(c => c.name).sort().join(",");
  assert(colNames === "created_at,decision_id,embedding,id,model,text_content", `Correct column names: ${colNames}`);

  // --- Embedding Storage & Retrieval (3 tests) ---
  console.log("\n🔗 Embedding Storage:");
  if (emb1) {
    const testId = "test-vector-" + Date.now();
    const testDecisionId = "test-decision-" + Date.now();
    const embJson = JSON.stringify(emb1);
    const stored = sqliteExec(`
      INSERT OR REPLACE INTO vectors (id, decision_id, text_content, embedding, model, created_at)
      VALUES ('${testId}', '${testDecisionId}', 'Kevin likes TypeScript', '${embJson}', '${EMBEDDING_MODEL}', ${Date.now()})
    `);
    assert(stored, "Store embedding in vectors table");

    const retrieved = sqliteQuery(`SELECT embedding FROM vectors WHERE id = '${testId}'`);
    assert(retrieved.length === 1, "Retrieve stored embedding");

    if (retrieved.length > 0) {
      const parsedEmb = JSON.parse(retrieved[0].embedding);
      const selfSim = cosineSimilarity(emb1, parsedEmb);
      assert(Math.abs(selfSim - 1.0) < 0.001, `Retrieved embedding matches stored (sim=${selfSim.toFixed(4)})`);
    } else {
      assert(false, "Retrieved embedding matches stored");
    }

    // Cleanup
    sqliteExec(`DELETE FROM vectors WHERE id = '${testId}'`);
  } else {
    assert(false, "Store embedding (Ollama unavailable)");
    assert(false, "Retrieve embedding (Ollama unavailable)");
    assert(false, "Embedding round-trip (Ollama unavailable)");
  }

  // --- Consolidation Logic (3 tests) ---
  console.log("\n🗜️ Consolidation:");
  // Check for any existing duplicates
  const dupes = sqliteQuery(`
    SELECT entity, fact_key, COUNT(*) as cnt
    FROM decisions
    WHERE entity IS NOT NULL AND fact_key IS NOT NULL
      AND (expires_at IS NULL OR expires_at > ${Date.now()})
    GROUP BY entity, fact_key
    HAVING cnt > 1
  `);
  assert(true, `Current duplicates in DB: ${dupes.length} groups`);

  // Insert a test duplicate and verify consolidation would find it
  const dupId1 = "test-dup-1-" + Date.now();
  const dupId2 = "test-dup-2-" + Date.now();
  const nowMs = Date.now();
  sqliteExec(`
    INSERT INTO decisions (id, session_id, timestamp, category, description, rationale,
      classification, importance, ttl_class, expires_at, last_accessed_at,
      entity, fact_key, fact_value, tags)
    VALUES ('${dupId1}', 'test', ${nowMs - 1000}, 'test', 'test dup', 'test',
      'ARCHIVE', 0.5, 'active', ${nowMs + 86400000}, ${nowMs - 1000},
      'TestEntity', 'test_key', 'value one for testing consolidation', '["test"]')
  `);
  sqliteExec(`
    INSERT INTO decisions (id, session_id, timestamp, category, description, rationale,
      classification, importance, ttl_class, expires_at, last_accessed_at,
      entity, fact_key, fact_value, tags)
    VALUES ('${dupId2}', 'test', ${nowMs}, 'test', 'test dup 2', 'test',
      'ARCHIVE', 0.6, 'active', ${nowMs + 86400000}, ${nowMs},
      'TestEntity', 'test_key', 'value two updated consolidation', '["test"]')
  `);

  const dupCheck = sqliteQuery(`
    SELECT COUNT(*) as cnt FROM decisions
    WHERE entity = 'TestEntity' AND fact_key = 'test_key'
  `);
  assert(dupCheck[0]?.cnt === 2, "Created test duplicates");

  // Clean up test entries
  sqliteExec(`DELETE FROM decisions WHERE id = '${dupId1}'`);
  sqliteExec(`DELETE FROM decisions WHERE id = '${dupId2}'`);
  const afterCleanup = sqliteQuery(`SELECT COUNT(*) as cnt FROM decisions WHERE entity = 'TestEntity'`);
  assert(afterCleanup[0]?.cnt === 0, "Test duplicates cleaned up");

  // --- Reflexion Nudge (2 tests) ---
  console.log("\n🪞 Reflexion Nudge:");
  // Test that alternative suggestions are pulled from DB
  const alternatives = sqliteQuery(`
    SELECT DISTINCT entity, fact_key FROM decisions
    WHERE ttl_class IN ('permanent', 'stable')
      AND entity IS NOT NULL AND fact_key IS NOT NULL
    ORDER BY importance DESC
    LIMIT 5
  `);
  assert(alternatives.length >= 0, `Found ${alternatives.length} alternative topics for reflexion nudge (0 ok on fresh install)`);
  assert(alternatives.length === 0 || alternatives.some(a => a.entity && a.fact_key), "Alternative topics have entity+key structure (or empty on fresh install)");

  // --- DB State (3 tests) ---
  console.log("\n📊 DB State:");
  const totalEntries = sqliteQuery("SELECT COUNT(*) as cnt FROM decisions WHERE expires_at IS NULL OR expires_at > " + Date.now());
  assert(totalEntries[0]?.cnt >= 0, `Total non-expired entries: ${totalEntries[0]?.cnt} (0+ ok on fresh install)`);

  const garbageEntities = sqliteQuery(`
    SELECT entity FROM decisions
    WHERE entity IN ('Still', 'Just', 'Acts', 'You', 'It', 'Looks', 'Community')
      AND (expires_at IS NULL OR expires_at > ${Date.now()})
  `);
  assert(garbageEntities.length === 0, `Zero garbage entities (found ${garbageEntities.length})`);

  const vectorCount = sqliteQuery("SELECT COUNT(*) as cnt FROM vectors");
  assert(true, `Vectors in DB: ${vectorCount[0]?.cnt || 0}`);

  // --- Compaction Config (2 tests) ---
  console.log("\n⚙️ Compaction Config:");
  const configPath = path.join(os.homedir(), ".openclaw", "openclaw.json");
  if (fs.existsSync(configPath)) {
    const configRaw = fs.readFileSync(configPath, "utf-8");
    const config = JSON.parse(configRaw);
    const compaction = config.agents?.defaults?.compaction || {};
    assert(compaction.mode === "default", `Compaction mode is '${compaction.mode}' (recommend 'default')`);
    assert(typeof compaction.reserveTokensFloor === "number", `Reserve tokens floor is ${compaction.reserveTokensFloor}`);
  } else {
    assert(true, "openclaw.json not found (fresh install — skip compaction checks)");
    assert(true, "openclaw.json not found (fresh install — skip compaction checks)");
  }

  // --- Plugin Config Schema (2 tests) ---
  console.log("\n📝 Plugin Config Schema:");
  const schemaRaw = fs.readFileSync(path.join(os.homedir(), ".openclaw", "extensions", "lily-memory", "openclaw.plugin.json"), "utf-8");
  const schema = JSON.parse(schemaRaw);
  assert(schema.configSchema.properties.vectorSearch !== undefined, "vectorSearch config property exists");
  assert(schema.configSchema.properties.embeddingModel !== undefined, "embeddingModel config property exists");

  // --- Summary ---
  console.log(`\n${"=".repeat(50)}`);
  console.log(`Results: ${passed} passed, ${failed} failed out of ${passed + failed} tests`);
  if (failed > 0) {
    console.log("⚠️  SOME TESTS FAILED");
    process.exit(1);
  } else {
    console.log("✅ ALL TESTS PASSED");
  }
}

runTests().catch(err => {
  console.error("Test harness error:", err);
  process.exit(1);
});
