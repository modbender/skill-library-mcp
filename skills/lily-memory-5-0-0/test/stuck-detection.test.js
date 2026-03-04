import { describe, it, before, after } from "node:test";
import assert from "node:assert/strict";
import { mkdtempSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import path from "node:path";
import {
  MAX_TOPIC_HISTORY,
  STUCK_THRESHOLD,
  STOP_WORDS,
  extractTopicSignature,
  loadTopicHistory,
  saveTopicHistory,
  checkStuck,
  buildReflexionNudge,
} from "../lib/stuck-detection.js";

describe("stuck-detection", () => {
  let tempDir;
  let historyPath;
  let dbPath;

  before(() => {
    tempDir = mkdtempSync(path.join(tmpdir(), "lily-stuck-test-"));
    historyPath = path.join(tempDir, "topic-history.json");
    dbPath = path.join(tempDir, "test.db");
  });

  after(() => {
    rmSync(tempDir, { recursive: true, force: true });
  });

  describe("extractTopicSignature", () => {
    it("returns comma-separated top 5 words for long text", () => {
      const text = "machine learning algorithms neural network training data science python tensorflow keras";
      const result = extractTopicSignature(text);
      assert.ok(typeof result === "string");
      const parts = result.split(",");
      assert.ok(parts.length <= 5);
      assert.ok(parts.length >= 2);
    });

    it("returns null for very short text", () => {
      const result = extractTopicSignature("hello world");
      assert.equal(result, null);
    });

    it("excludes stop words", () => {
      const text = "the quick brown fox jumps over the lazy dog running through fields";
      const result = extractTopicSignature(text);
      assert.ok(result !== null);
      const parts = result.split(",");
      for (const word of parts) {
        assert.ok(!STOP_WORDS.has(word), `stop word found in signature: ${word}`);
      }
    });

    it("sorts words alphabetically", () => {
      const text = "zebra apple mango banana cherry dragon elephant falcon guitar hammer instrument";
      const result = extractTopicSignature(text);
      assert.ok(result !== null);
      const parts = result.split(",");
      const sorted = [...parts].sort();
      assert.deepEqual(parts, sorted);
    });

    it("similar texts produce high Jaccard overlap (> 0.5)", () => {
      const text1 = "javascript programming language functions closures async await promises callbacks modules";
      const text2 = "javascript programming language closures functions promises async modules patterns";
      const sig1 = extractTopicSignature(text1);
      const sig2 = extractTopicSignature(text2);
      assert.ok(sig1 !== null);
      assert.ok(sig2 !== null);
      const set1 = new Set(sig1.split(","));
      const set2 = new Set(sig2.split(","));
      const intersection = [...set1].filter(w => set2.has(w)).length;
      const union = new Set([...set1, ...set2]).size;
      const jaccard = intersection / union;
      assert.ok(jaccard > 0.5, `expected jaccard > 0.5, got ${jaccard}`);
    });

    it("different texts produce low Jaccard overlap (< 0.3)", () => {
      const text1 = "cooking recipes baking bread flour yeast oven temperature ingredients kitchen";
      const text2 = "software programming computers algorithms databases networks servers cloud storage";
      const sig1 = extractTopicSignature(text1);
      const sig2 = extractTopicSignature(text2);
      assert.ok(sig1 !== null);
      assert.ok(sig2 !== null);
      const set1 = new Set(sig1.split(","));
      const set2 = new Set(sig2.split(","));
      const intersection = [...set1].filter(w => set2.has(w)).length;
      const union = new Set([...set1, ...set2]).size;
      const jaccard = intersection / union;
      assert.ok(jaccard < 0.3, `expected jaccard < 0.3, got ${jaccard}`);
    });
  });

  describe("loadTopicHistory", () => {
    it("returns [] for missing file", () => {
      const result = loadTopicHistory(path.join(tempDir, "nonexistent.json"));
      assert.deepEqual(result, []);
    });

    it("returns parsed array for valid file", () => {
      const data = ["alpha,beta,gamma", "delta,epsilon,zeta"];
      const filePath = path.join(tempDir, "valid-history.json");
      writeFileSync(filePath, JSON.stringify(data), "utf-8");
      const result = loadTopicHistory(filePath);
      assert.deepEqual(result, data);
    });

    it("returns [] for corrupt/invalid JSON", () => {
      const filePath = path.join(tempDir, "corrupt-history.json");
      writeFileSync(filePath, "{ not valid json [[[", "utf-8");
      const result = loadTopicHistory(filePath);
      assert.deepEqual(result, []);
    });
  });

  describe("saveTopicHistory", () => {
    it("writes and reads back correctly", () => {
      const filePath = path.join(tempDir, "save-test.json");
      const data = ["aardvark,bear,cat", "deer,eagle,fox"];
      saveTopicHistory(filePath, data);
      const result = loadTopicHistory(filePath);
      assert.deepEqual(result, data);
    });

    it("trims to MAX_TOPIC_HISTORY entries", () => {
      const filePath = path.join(tempDir, "trim-test.json");
      const data = Array.from({ length: MAX_TOPIC_HISTORY + 5 }, (_, i) => `word${i},word${i + 1}`);
      saveTopicHistory(filePath, data);
      const result = loadTopicHistory(filePath);
      assert.equal(result.length, MAX_TOPIC_HISTORY);
      // Should keep the last MAX_TOPIC_HISTORY entries
      assert.deepEqual(result, data.slice(-MAX_TOPIC_HISTORY));
    });
  });

  describe("checkStuck", () => {
    it("returns null when fewer than STUCK_THRESHOLD entries", () => {
      const filePath = path.join(tempDir, "check-few.json");
      const sig = "alpha,beta,gamma,delta,epsilon";
      // Push STUCK_THRESHOLD - 1 entries
      for (let i = 0; i < STUCK_THRESHOLD - 1; i++) {
        checkStuck(dbPath, filePath, sig);
      }
      const result = checkStuck(dbPath, filePath, sig);
      // At STUCK_THRESHOLD entries, the history has exactly STUCK_THRESHOLD items now
      // That means it should trigger — so let's test with fewer
      const filePath2 = path.join(tempDir, "check-few2.json");
      const result2 = checkStuck(dbPath, filePath2, sig);
      assert.equal(result2, null);
    });

    it("returns nudge string when STUCK_THRESHOLD identical signatures in a row", () => {
      const filePath = path.join(tempDir, "check-stuck.json");
      const sig = "project,status,update,review,summary";
      let result = null;
      for (let i = 0; i < STUCK_THRESHOLD; i++) {
        result = checkStuck(dbPath, filePath, sig, { userName: "Alice" });
      }
      assert.ok(typeof result === "string", "expected a nudge string");
      assert.ok(result.includes("lily-memory-nudge"));
    });
  });

  describe("buildReflexionNudge", () => {
    it("output contains userName (not 'Kevin')", () => {
      const result = buildReflexionNudge(dbPath, "project,status,update", "TestUser");
      assert.ok(result.includes("TestUser"), "expected userName in output");
      assert.ok(!result.includes("Kevin"), "should not contain hardcoded 'Kevin'");
    });

    it("output contains repeating words", () => {
      const sig = "project,status,update";
      const result = buildReflexionNudge(dbPath, sig, "the user");
      assert.ok(result.includes("project"), "expected repeating word 'project'");
      assert.ok(result.includes("status"), "expected repeating word 'status'");
      assert.ok(result.includes("update"), "expected repeating word 'update'");
    });

    it("uses default userName when not provided", () => {
      const result = buildReflexionNudge(dbPath, "alpha,beta,gamma");
      assert.ok(result.includes("the user"));
    });

    it("output is properly structured with nudge wrapper", () => {
      const result = buildReflexionNudge(dbPath, "alpha,beta,gamma", "Bob");
      assert.ok(result.startsWith('<lily-memory-nudge type="reflexion">'));
      assert.ok(result.endsWith("</lily-memory-nudge>"));
      assert.ok(result.includes("SELF-REFLECTION"));
      assert.ok(result.includes("BREAK THE LOOP"));
    });
  });
});
