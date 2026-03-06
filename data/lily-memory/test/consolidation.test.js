import { test } from 'node:test';
import assert from 'node:assert/strict';
import { mkdtempSync, rmSync } from 'node:fs';
import { join } from 'node:path';
import { tmpdir } from 'node:os';
import { ensureTables, sqliteExec, sqliteQuery } from '../lib/sqlite.js';
import { consolidateMemories } from '../lib/consolidation.js';

function makeTempDb() {
  const dir = mkdtempSync(join(tmpdir(), 'consolidation-test-'));
  const dbPath = join(dir, 'test.db');
  ensureTables(dbPath);
  return { dbPath, dir };
}

function insertDecision(dbPath, { id, timestamp, entity, fact_key, importance = 0.6, last_accessed_at = null }) {
  const laa = last_accessed_at !== null ? last_accessed_at : 'NULL';
  sqliteExec(dbPath,
    `INSERT INTO decisions (id, session_id, timestamp, category, description, rationale, classification, importance, ttl_class, entity, fact_key, fact_value, last_accessed_at) ` +
    `VALUES ('${id}', 'test', ${timestamp}, 'auto', 'desc', 'rat', 'ARCHIVE', ${importance}, 'active', '${entity}', '${fact_key}', 'value long enough here', ${laa})`
  );
}

function insertVector(dbPath, { id, decision_id }) {
  sqliteExec(dbPath,
    `INSERT INTO vectors (id, decision_id, text_content, embedding, model, created_at) ` +
    `VALUES ('${id}', '${decision_id}', 'text', '[]', 'test', ${Date.now()})`
  );
}

// Test 1: No duplicates — returns 0
test('no duplicates returns 0 merged count', () => {
  const { dbPath, dir } = makeTempDb();
  try {
    insertDecision(dbPath, { id: 'a1', timestamp: 1000, entity: 'config', fact_key: 'key1' });
    insertDecision(dbPath, { id: 'a2', timestamp: 2000, entity: 'config', fact_key: 'key2' });
    const result = consolidateMemories(dbPath);
    assert.equal(result, 0);
  } finally {
    rmSync(dir, { recursive: true });
  }
});

// Test 2: One duplicate pair — deletes older, keeps newer, returns 1
test('one duplicate pair deletes older and keeps newer', () => {
  const { dbPath, dir } = makeTempDb();
  try {
    // dup-1: older (timestamp 1000, no last_accessed_at)
    insertDecision(dbPath, { id: 'dup-1', timestamp: 1000, entity: 'config', fact_key: 'test_key' });
    // dup-2: newer (timestamp 2000, last_accessed_at 2000)
    insertDecision(dbPath, { id: 'dup-2', timestamp: 2000, entity: 'config', fact_key: 'test_key', last_accessed_at: 2000 });

    const result = consolidateMemories(dbPath);
    assert.equal(result, 1);

    const remaining = sqliteQuery(dbPath, `SELECT id FROM decisions WHERE entity = 'config' AND fact_key = 'test_key'`);
    assert.equal(remaining.length, 1);
    assert.equal(remaining[0].id, 'dup-2');
  } finally {
    rmSync(dir, { recursive: true });
  }
});

// Test 3: Importance boost — survivor gets +0.05
test('survivor importance is boosted by 0.05', () => {
  const { dbPath, dir } = makeTempDb();
  try {
    insertDecision(dbPath, { id: 'b1', timestamp: 1000, entity: 'config', fact_key: 'boost_key', importance: 0.5 });
    insertDecision(dbPath, { id: 'b2', timestamp: 2000, entity: 'config', fact_key: 'boost_key', importance: 0.6, last_accessed_at: 2000 });

    consolidateMemories(dbPath);

    const rows = sqliteQuery(dbPath, `SELECT importance FROM decisions WHERE id = 'b2'`);
    assert.equal(rows.length, 1);
    // max importance is 0.6, boosted by 0.05 = 0.65
    assert.ok(Math.abs(rows[0].importance - 0.65) < 0.001, `Expected ~0.65 but got ${rows[0].importance}`);
  } finally {
    rmSync(dir, { recursive: true });
  }
});

// Test 4: Importance cap — capped at 0.95
test('importance boost is capped at 0.95', () => {
  const { dbPath, dir } = makeTempDb();
  try {
    insertDecision(dbPath, { id: 'c1', timestamp: 1000, entity: 'config', fact_key: 'cap_key', importance: 0.90 });
    insertDecision(dbPath, { id: 'c2', timestamp: 2000, entity: 'config', fact_key: 'cap_key', importance: 0.92, last_accessed_at: 2000 });

    consolidateMemories(dbPath);

    const rows = sqliteQuery(dbPath, `SELECT importance FROM decisions WHERE id = 'c2'`);
    assert.equal(rows.length, 1);
    // 0.92 + 0.05 = 0.97, capped at 0.95
    assert.ok(Math.abs(rows[0].importance - 0.95) < 0.001, `Expected 0.95 but got ${rows[0].importance}`);
  } finally {
    rmSync(dir, { recursive: true });
  }
});

// Test 5: Three duplicates of same fact — deletes 2, keeps 1
test('three duplicates keeps only newest and returns 2', () => {
  const { dbPath, dir } = makeTempDb();
  try {
    insertDecision(dbPath, { id: 'tri-1', timestamp: 1000, entity: 'config', fact_key: 'tri_key' });
    insertDecision(dbPath, { id: 'tri-2', timestamp: 2000, entity: 'config', fact_key: 'tri_key', last_accessed_at: 2000 });
    insertDecision(dbPath, { id: 'tri-3', timestamp: 3000, entity: 'config', fact_key: 'tri_key', last_accessed_at: 3000 });

    const result = consolidateMemories(dbPath);
    assert.equal(result, 2);

    const remaining = sqliteQuery(dbPath, `SELECT id FROM decisions WHERE entity = 'config' AND fact_key = 'tri_key'`);
    assert.equal(remaining.length, 1);
    assert.equal(remaining[0].id, 'tri-3');
  } finally {
    rmSync(dir, { recursive: true });
  }
});

// Test 6: Multiple duplicate groups processed independently
test('multiple duplicate groups each processed independently', () => {
  const { dbPath, dir } = makeTempDb();
  try {
    // Group 1: entity=config, fact_key=key_a
    insertDecision(dbPath, { id: 'g1a-old', timestamp: 1000, entity: 'config', fact_key: 'key_a' });
    insertDecision(dbPath, { id: 'g1a-new', timestamp: 2000, entity: 'config', fact_key: 'key_a', last_accessed_at: 2000 });
    // Group 2: entity=config, fact_key=key_b
    insertDecision(dbPath, { id: 'g1b-old', timestamp: 1000, entity: 'config', fact_key: 'key_b' });
    insertDecision(dbPath, { id: 'g1b-new', timestamp: 2000, entity: 'config', fact_key: 'key_b', last_accessed_at: 2000 });

    const result = consolidateMemories(dbPath);
    assert.equal(result, 2);

    const remaining = sqliteQuery(dbPath, `SELECT id FROM decisions ORDER BY id`);
    const ids = remaining.map(r => r.id);
    assert.deepEqual(ids, ['g1a-new', 'g1b-new']);
  } finally {
    rmSync(dir, { recursive: true });
  }
});

// Test 7: Orphaned vectors are cleaned up
test('orphaned vectors are deleted', () => {
  const { dbPath, dir } = makeTempDb();
  try {
    insertDecision(dbPath, { id: 'orphan-decision', timestamp: 1000, entity: 'e', fact_key: 'k' });
    insertVector(dbPath, { id: 'orphan-vec', decision_id: 'nonexistent-decision' });

    consolidateMemories(dbPath);

    const vectors = sqliteQuery(dbPath, `SELECT id FROM vectors WHERE id = 'orphan-vec'`);
    assert.equal(vectors.length, 0);
  } finally {
    rmSync(dir, { recursive: true });
  }
});

// Test 8: Non-orphaned vectors are preserved
test('non-orphaned vectors are preserved', () => {
  const { dbPath, dir } = makeTempDb();
  try {
    insertDecision(dbPath, { id: 'live-decision', timestamp: 1000, entity: 'e', fact_key: 'k' });
    insertVector(dbPath, { id: 'live-vec', decision_id: 'live-decision' });

    consolidateMemories(dbPath);

    const vectors = sqliteQuery(dbPath, `SELECT id FROM vectors WHERE id = 'live-vec'`);
    assert.equal(vectors.length, 1);
  } finally {
    rmSync(dir, { recursive: true });
  }
});
