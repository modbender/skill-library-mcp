import { describe, it, before, after } from "node:test";
import assert from "node:assert/strict";
import { mkdtempSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import path from "node:path";
import {
  resolveDbPath,
  escapeSqlValue,
  sqliteQuery,
  sqliteExec,
  ensureTables
} from "../lib/sqlite.js";

describe("SQLite utilities", () => {
  let tempDir;
  let testDbPath;

  before(() => {
    tempDir = mkdtempSync(path.join(tmpdir(), "lily-test-"));
    testDbPath = path.join(tempDir, "test.db");
  });

  after(() => {
    rmSync(tempDir, { recursive: true, force: true });
  });

  describe("resolveDbPath", () => {
    it("expands tilde to home directory", () => {
      const result = resolveDbPath("~/.openclaw/memory/decisions.db");
      assert.ok(result.startsWith("/"));
      assert.ok(!result.includes("~"));
      assert.ok(result.endsWith("/.openclaw/memory/decisions.db"));
    });

    it("passes through absolute paths unchanged", () => {
      const absolutePath = "/tmp/test.db";
      const result = resolveDbPath(absolutePath);
      assert.equal(result, absolutePath);
    });

    it("returns default path when null or undefined", () => {
      const resultNull = resolveDbPath(null);
      const resultUndef = resolveDbPath(undefined);
      assert.ok(resultNull.includes(".openclaw/memory/decisions.db"));
      assert.ok(resultUndef.includes(".openclaw/memory/decisions.db"));
      assert.equal(resultNull, resultUndef);
    });
  });

  describe("escapeSqlValue", () => {
    it("returns normal string unchanged when no special chars", () => {
      const result = escapeSqlValue("hello world");
      assert.equal(result, "hello world");
    });

    it("escapes single quotes", () => {
      const result = escapeSqlValue("it's a test");
      assert.equal(result, "it''s a test");
    });

    it("removes null bytes", () => {
      const result = escapeSqlValue("hello\0world");
      assert.equal(result, "helloworld");
    });

    it("returns empty string for null", () => {
      const resultNull = escapeSqlValue(null);
      const resultUndef = escapeSqlValue(undefined);
      assert.equal(resultNull, "");
      assert.equal(resultUndef, "");
    });

    it("truncates at 10000 chars", () => {
      const longString = "a".repeat(15000);
      const result = escapeSqlValue(longString);
      assert.equal(result.length, 10000);
    });

    it("returns empty string for empty input", () => {
      const result = escapeSqlValue("");
      assert.equal(result, "");
    });
  });

  describe("sqliteQuery", () => {
    it("returns rows for valid SELECT", () => {
      ensureTables(testDbPath);
      sqliteExec(testDbPath, "INSERT INTO entities (name, display_name) VALUES ('test', 'Test Entity')");
      const rows = sqliteQuery(testDbPath, "SELECT * FROM entities WHERE name='test'");
      assert.ok(Array.isArray(rows));
      assert.equal(rows.length, 1);
      assert.equal(rows[0].name, "test");
      assert.equal(rows[0].display_name, "Test Entity");
    });

    it("returns empty array for no results", () => {
      ensureTables(testDbPath);
      const rows = sqliteQuery(testDbPath, "SELECT * FROM entities WHERE name='nonexistent'");
      assert.ok(Array.isArray(rows));
      assert.equal(rows.length, 0);
    });

    it("returns empty array for invalid SQL", () => {
      const rows = sqliteQuery(testDbPath, "SELECT * FROM nonexistent_table");
      assert.ok(Array.isArray(rows));
      assert.equal(rows.length, 0);
    });
  });

  describe("sqliteExec", () => {
    it("returns true for successful INSERT", () => {
      ensureTables(testDbPath);
      const result = sqliteExec(testDbPath, "INSERT INTO entities (name, display_name) VALUES ('exec-test', 'Exec Test')");
      assert.equal(result, true);
      const rows = sqliteQuery(testDbPath, "SELECT * FROM entities WHERE name='exec-test'");
      assert.equal(rows.length, 1);
    });

    it("returns false for invalid SQL", () => {
      const result = sqliteExec(testDbPath, "INSERT INTO nonexistent_table (col) VALUES ('val')");
      assert.equal(result, false);
    });
  });

  describe("ensureTables", () => {
    it("creates all required tables", () => {
      const result = ensureTables(testDbPath);
      assert.equal(result, true);

      // Verify decisions table
      const decisionsInfo = sqliteQuery(testDbPath, "PRAGMA table_info(decisions)");
      assert.ok(decisionsInfo.length > 0);
      const columnNames = decisionsInfo.map(col => col.name);
      assert.ok(columnNames.includes("id"));
      assert.ok(columnNames.includes("session_id"));
      assert.ok(columnNames.includes("timestamp"));
      assert.ok(columnNames.includes("category"));
      assert.ok(columnNames.includes("description"));
      assert.ok(columnNames.includes("rationale"));
      assert.ok(columnNames.includes("classification"));
      assert.ok(columnNames.includes("importance"));
      assert.ok(columnNames.includes("entity"));
      assert.ok(columnNames.includes("fact_key"));
      assert.ok(columnNames.includes("fact_value"));

      // Verify vectors table
      const vectorsInfo = sqliteQuery(testDbPath, "PRAGMA table_info(vectors)");
      assert.ok(vectorsInfo.length > 0);
      const vectorColumns = vectorsInfo.map(col => col.name);
      assert.ok(vectorColumns.includes("id"));
      assert.ok(vectorColumns.includes("decision_id"));
      assert.ok(vectorColumns.includes("embedding"));

      // Verify entities table
      const entitiesInfo = sqliteQuery(testDbPath, "PRAGMA table_info(entities)");
      assert.ok(entitiesInfo.length > 0);
      const entityColumns = entitiesInfo.map(col => col.name);
      assert.ok(entityColumns.includes("name"));
      assert.ok(entityColumns.includes("display_name"));

      // Verify FTS table exists
      const ftsCheck = sqliteQuery(testDbPath, "SELECT name FROM sqlite_master WHERE type='table' AND name='decisions_fts'");
      assert.equal(ftsCheck.length, 1);
    });

    it("is idempotent on second call", () => {
      const result1 = ensureTables(testDbPath);
      const result2 = ensureTables(testDbPath);
      assert.equal(result1, true);
      assert.equal(result2, true);

      // Verify tables still exist and have correct structure
      const decisionsInfo = sqliteQuery(testDbPath, "PRAGMA table_info(decisions)");
      assert.ok(decisionsInfo.length > 0);
    });
  });
});
