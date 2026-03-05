import { describe, it, before, after } from "node:test";
import assert from "node:assert/strict";
import { mkdtempSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import path from "node:path";
import { randomUUID } from "node:crypto";
import { ensureTables, sqliteExec } from "../lib/sqlite.js";
import { buildFtsContext, buildRecallContext } from "../lib/recall.js";

// Helper: insert a decision row directly
function insertDecision(dbPath, fields) {
  const id = fields.id || randomUUID();
  const sessionId = escapeLiteral(fields.session_id || "test-session");
  const timestamp = fields.timestamp || Date.now();
  const category = escapeLiteral(fields.category || "general");
  const description = escapeLiteral(fields.description || "");
  const rationale = escapeLiteral(fields.rationale || "");
  const classification = escapeLiteral(fields.classification || "ARCHIVE");
  const importance = fields.importance ?? 0.5;
  const ttlClass = escapeLiteral(fields.ttl_class || "active");
  const expiresAt = fields.expires_at === undefined ? "NULL" : fields.expires_at;
  const entity = fields.entity ? `'${escapeLiteral(fields.entity)}'` : "NULL";
  const factKey = fields.fact_key ? `'${escapeLiteral(fields.fact_key)}'` : "NULL";
  const factValue = fields.fact_value ? `'${escapeLiteral(fields.fact_value)}'` : "NULL";

  sqliteExec(dbPath, `
    INSERT INTO decisions
      (id, session_id, timestamp, category, description, rationale, classification,
       importance, ttl_class, expires_at, entity, fact_key, fact_value)
    VALUES
      ('${id}', '${sessionId}', ${timestamp}, '${category}', '${description}',
       '${rationale}', '${classification}', ${importance}, '${ttlClass}',
       ${expiresAt}, ${entity}, ${factKey}, ${factValue})
  `);
  return id;
}

function escapeLiteral(v) {
  return String(v || "").replace(/'/g, "''");
}

describe("recall utilities", () => {
  let tempDir;
  let dbPath;

  before(() => {
    tempDir = mkdtempSync(path.join(tmpdir(), "lily-recall-test-"));
    dbPath = path.join(tempDir, "test.db");
    ensureTables(dbPath);

    // Seed: 2 permanent facts
    insertDecision(dbPath, {
      id: "perm-1",
      ttl_class: "permanent",
      entity: "project",
      fact_key: "language",
      fact_value: "JavaScript",
      description: "Project language is JavaScript",
      rationale: "chosen at start",
      importance: 0.9,
    });
    insertDecision(dbPath, {
      id: "perm-2",
      ttl_class: "permanent",
      entity: "project",
      fact_key: "framework",
      fact_value: "Node.js",
      description: "Project framework is Node.js",
      rationale: "chosen at start",
      importance: 0.85,
    });

    // Seed: 3 active facts with keywords matching test prompts
    insertDecision(dbPath, {
      id: "active-1",
      ttl_class: "active",
      description: "database migration completed successfully",
      rationale: "ran migration scripts",
      category: "engineering",
      importance: 0.6,
    });
    insertDecision(dbPath, {
      id: "active-2",
      ttl_class: "active",
      description: "authentication module refactored",
      rationale: "improved security",
      category: "engineering",
      importance: 0.65,
    });
    insertDecision(dbPath, {
      id: "active-3",
      ttl_class: "active",
      entity: "user",
      fact_key: "preference",
      fact_value: "dark mode",
      description: "User prefers dark mode interface",
      rationale: "user stated preference",
      category: "preference",
      importance: 0.55,
    });

    // Seed: 1 high-importance recent entry
    insertDecision(dbPath, {
      id: "high-imp-1",
      ttl_class: "stable",
      description: "critical security patch applied",
      rationale: "vulnerability fix",
      category: "security",
      importance: 0.95,
    });
  });

  after(() => {
    rmSync(tempDir, { recursive: true, force: true });
  });

  // -------------------------------------------------------------------------
  // buildFtsContext tests
  // -------------------------------------------------------------------------

  describe("buildFtsContext", () => {
    it("returns permanent facts from DB", () => {
      const { lines } = buildFtsContext(dbPath, "hello world test", 10);
      assert.ok(lines.includes("## Permanent Knowledge"), "should have Permanent Knowledge section");
      const hasPerm1 = lines.some((l) => l.includes("project") && l.includes("language") && l.includes("JavaScript"));
      assert.ok(hasPerm1, "should include permanent fact project.language = JavaScript");
    });

    it("FTS5 matches keywords in prompt", () => {
      const { lines, ftsIds } = buildFtsContext(dbPath, "database migration completed", 10);
      const hasKeywordSection = lines.includes("## Relevant Memories (keyword)");
      assert.ok(hasKeywordSection, "should have Relevant Memories (keyword) section");
      const hasMatch = lines.some((l) => l.includes("database migration") || l.includes("migration"));
      assert.ok(hasMatch, "should include FTS-matched memory about database migration");
      assert.ok(ftsIds.size > 0, "ftsIds should be non-empty after FTS match");
    });

    it("returns empty lines for no matches on short prompt", () => {
      // Prompt shorter than 5 chars skips FTS
      const { lines, ftsIds } = buildFtsContext(dbPath, "hi", 10);
      assert.ok(!lines.includes("## Relevant Memories (keyword)"), "should not have keyword section for short prompt");
      assert.equal(ftsIds.size, 0, "ftsIds should be empty when FTS is skipped");
    });

    it("returns high-importance recent entries", () => {
      const { lines } = buildFtsContext(dbPath, "something unrelated prompt text", 10);
      const hasRecentSection = lines.includes("## Recent Important Context");
      assert.ok(hasRecentSection, "should have Recent Important Context section for high-importance entries");
      const hasSecurityPatch = lines.some((l) => l.includes("critical security patch"));
      assert.ok(hasSecurityPatch, "should include the high-importance security patch entry");
    });

    it("ftsIds Set contains matched IDs", () => {
      const { ftsIds } = buildFtsContext(dbPath, "authentication module refactored security", 10);
      // The FTS search should have found active-2
      assert.ok(ftsIds instanceof Set, "ftsIds should be a Set");
      assert.ok(ftsIds.has("active-2"), "ftsIds should contain ID of matched row");
    });

    it("respects maxResults limit", () => {
      // Insert extra rows to exceed limit
      for (let i = 0; i < 5; i++) {
        insertDecision(dbPath, {
          id: `limit-test-${i}`,
          ttl_class: "active",
          description: `migration test entry number ${i}`,
          rationale: "limit test",
          category: "test",
          importance: 0.5,
        });
      }
      const { ftsIds } = buildFtsContext(dbPath, "migration test entry number", 3);
      assert.ok(ftsIds.size <= 3, `ftsIds.size (${ftsIds.size}) should be <= maxResults (3)`);
    });

    it("returns empty lines and empty ftsIds when DB has no matching data", () => {
      // Use a fresh empty DB
      const emptyDir = mkdtempSync(path.join(tmpdir(), "lily-recall-empty-"));
      const emptyDb = path.join(emptyDir, "empty.db");
      try {
        ensureTables(emptyDb);
        const { lines, ftsIds } = buildFtsContext(emptyDb, "something interesting to find here", 10);
        assert.equal(lines.length, 0, "lines should be empty for empty DB");
        assert.equal(ftsIds.size, 0, "ftsIds should be empty for empty DB");
      } finally {
        rmSync(emptyDir, { recursive: true, force: true });
      }
    });
  });

  // -------------------------------------------------------------------------
  // buildRecallContext tests
  // -------------------------------------------------------------------------

  describe("buildRecallContext", () => {
    it("formats XML correctly with <lily-memory> tags", () => {
      const lines = ["## Permanent Knowledge", "- **project**.language = JavaScript", ""];
      const result = buildRecallContext(lines, new Set(), null);
      assert.ok(result !== null, "result should not be null");
      assert.ok(result.startsWith("<lily-memory>"), "should start with <lily-memory>");
      assert.ok(result.endsWith("</lily-memory>"), "should end with </lily-memory>");
      assert.ok(result.includes("## Permanent Knowledge"), "should include the FTS lines");
    });

    it("returns null when no lines and no vector results", () => {
      const result = buildRecallContext([], new Set(), null);
      assert.equal(result, null, "should return null for empty input");
    });

    it("returns null when no lines and empty vector results array", () => {
      const result = buildRecallContext([], new Set(), []);
      assert.equal(result, null, "should return null for empty lines and empty vector array");
    });

    it("includes vector results section when provided", () => {
      const ftsLines = ["## Permanent Knowledge", "- **project**.language = JavaScript", ""];
      const vectorResults = [
        {
          decision_id: "vec-1",
          entity: "user",
          fact_key: "name",
          fact_value: "Alice",
          description: null,
          category: "profile",
          similarity: 0.87,
        },
      ];
      const result = buildRecallContext(ftsLines, new Set(), vectorResults);
      assert.ok(result !== null, "result should not be null");
      assert.ok(result.includes("## Semantically Related Memories"), "should include semantic section header");
      assert.ok(result.includes("87% match"), "should include formatted similarity score");
      assert.ok(result.includes("user"), "should include entity from vector result");
    });

    it("deduplicates vector results against ftsIds", () => {
      const ftsIds = new Set(["vec-already-in-fts"]);
      const ftsLines = ["## Relevant Memories (keyword)", "- some line", ""];
      const vectorResults = [
        {
          decision_id: "vec-already-in-fts",
          entity: "duplicate",
          fact_key: "key",
          fact_value: "value",
          description: null,
          category: "test",
          similarity: 0.95,
        },
        {
          decision_id: "vec-new",
          entity: "newentity",
          fact_key: "uniquekey",
          fact_value: "uniquevalue",
          description: null,
          category: "test",
          similarity: 0.75,
        },
      ];
      const result = buildRecallContext(ftsLines, ftsIds, vectorResults);
      assert.ok(result !== null, "result should not be null");
      assert.ok(!result.includes("duplicate"), "should not include the duplicated vector result");
      assert.ok(result.includes("newentity"), "should include the non-duplicate vector result");
    });

    it("includes preamble text in output", () => {
      const lines = ["## Permanent Knowledge", "- **project**.language = JavaScript", ""];
      const result = buildRecallContext(lines, new Set(), null);
      assert.ok(
        result.includes("_Persistent memory context (auto-injected)"),
        "should include the preamble/description line"
      );
    });
  });
});
