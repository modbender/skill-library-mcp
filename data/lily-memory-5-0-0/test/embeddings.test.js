import { test } from "node:test";
import assert from "node:assert/strict";
import os from "node:os";
import path from "node:path";
import fs from "node:fs";
import { execSync } from "node:child_process";

import {
  cosineSimilarity,
  generateEmbedding,
  checkOllamaHealth,
  ensureVectorsTable,
  storeEmbedding,
  vectorSearch,
} from "../lib/embeddings.js";

import { ensureTables, sqliteQuery } from "../lib/sqlite.js";

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function makeTempDb() {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), "lily-embed-test-"));
  const dbPath = path.join(dir, "test.db");
  ensureTables(dbPath);
  return dbPath;
}

let ollamaAvailable = false;
let ollamaModel = "nomic-embed-text";

try {
  const res = execSync("curl -s --max-time 2 http://localhost:11434/api/version", {
    encoding: "utf-8",
    timeout: 3000,
  });
  const json = JSON.parse(res);
  if (json.version) ollamaAvailable = true;
} catch {
  // Ollama not running — skip dependent tests
}

// ---------------------------------------------------------------------------
// cosineSimilarity
// ---------------------------------------------------------------------------

test("cosineSimilarity: identical vectors return 1.0", () => {
  const v = [1, 2, 3];
  const result = cosineSimilarity(v, v);
  assert.ok(Math.abs(result - 1.0) < 1e-10, `expected ~1.0, got ${result}`);
});

test("cosineSimilarity: orthogonal vectors return 0.0", () => {
  const a = [1, 0, 0];
  const b = [0, 1, 0];
  const result = cosineSimilarity(a, b);
  assert.ok(Math.abs(result) < 1e-10, `expected ~0.0, got ${result}`);
});

test("cosineSimilarity: opposite vectors return -1.0", () => {
  const a = [1, 0, 0];
  const b = [-1, 0, 0];
  const result = cosineSimilarity(a, b);
  assert.ok(Math.abs(result - (-1.0)) < 1e-10, `expected ~-1.0, got ${result}`);
});

test("cosineSimilarity: null input returns 0", () => {
  assert.equal(cosineSimilarity(null, [1, 2, 3]), 0);
  assert.equal(cosineSimilarity([1, 2, 3], null), 0);
  assert.equal(cosineSimilarity(null, null), 0);
});

test("cosineSimilarity: undefined input returns 0", () => {
  assert.equal(cosineSimilarity(undefined, [1, 2, 3]), 0);
  assert.equal(cosineSimilarity([1, 2, 3], undefined), 0);
});

test("cosineSimilarity: mismatched lengths returns 0", () => {
  assert.equal(cosineSimilarity([1, 2, 3], [1, 2]), 0);
});

test("cosineSimilarity: empty arrays returns 0", () => {
  assert.equal(cosineSimilarity([], []), 0);
});

// ---------------------------------------------------------------------------
// generateEmbedding — bad URL
// ---------------------------------------------------------------------------

test("generateEmbedding: bad URL returns null", async () => {
  // Port 99999 is invalid and should fail fast
  const result = await generateEmbedding("http://localhost:99999", "any-model", "hello");
  assert.equal(result, null);
});

// ---------------------------------------------------------------------------
// checkOllamaHealth — bad URL
// ---------------------------------------------------------------------------

test("checkOllamaHealth: bad URL returns { available: false }", async () => {
  const result = await checkOllamaHealth("http://localhost:99999", "any-model");
  assert.equal(result.available, false);
  assert.ok(typeof result.reason === "string", "should include a reason string");
});

// ---------------------------------------------------------------------------
// vectorSearch — empty DB returns []
// ---------------------------------------------------------------------------

test("vectorSearch: returns empty array for empty DB", async () => {
  const dbPath = makeTempDb();
  // Use a bad URL so no network call succeeds — should still return []
  const results = await vectorSearch(
    dbPath,
    "http://localhost:99999",
    "any-model",
    "test query",
    10,
    0.5
  );
  assert.deepEqual(results, []);
});

// ---------------------------------------------------------------------------
// Ollama-dependent tests
// ---------------------------------------------------------------------------

test("generateEmbedding: returns float array when Ollama available", { skip: !ollamaAvailable }, async () => {
  const emb = await generateEmbedding("http://localhost:11434", ollamaModel, "hello world");
  assert.ok(Array.isArray(emb), "should return an array");
  assert.ok(emb.length > 0, "array should be non-empty");
  assert.ok(typeof emb[0] === "number", "elements should be numbers");
});

test("checkOllamaHealth: returns available=true when Ollama available", { skip: !ollamaAvailable }, async () => {
  const result = await checkOllamaHealth("http://localhost:11434", ollamaModel);
  assert.equal(result.available, true);
  assert.ok(typeof result.dimensions === "number" && result.dimensions > 0);
});

test("storeEmbedding: stores and retrieves from temp DB", { skip: !ollamaAvailable }, async () => {
  const dbPath = makeTempDb();

  // Insert a minimal decision row so the FK join in vectorSearch works
  const { sqliteExec } = await import("../lib/sqlite.js");
  const decisionId = "test-decision-001";
  sqliteExec(dbPath, `
    INSERT INTO decisions (id, session_id, timestamp, category, description, rationale, classification, importance)
    VALUES ('${decisionId}', 'sess-1', ${Date.now()}, 'test', 'test description', 'test rationale', 'ACTIVE', 0.9)
  `);

  const ok = await storeEmbedding(
    dbPath,
    "http://localhost:11434",
    ollamaModel,
    decisionId,
    "test description"
  );
  assert.equal(ok, true, "storeEmbedding should return true");

  const rows = sqliteQuery(dbPath, `SELECT * FROM vectors WHERE decision_id = '${decisionId}'`);
  assert.equal(rows.length, 1, "should have one vector row");
  assert.equal(rows[0].decision_id, decisionId);

  // Parse stored embedding
  const emb = JSON.parse(rows[0].embedding);
  assert.ok(Array.isArray(emb) && emb.length > 0, "stored embedding should be a non-empty array");
});
