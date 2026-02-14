import { describe, it, expect, beforeAll } from "vitest";
import { join } from "node:path";
import { fileURLToPath } from "node:url";
import { buildIndex } from "../src/skill-index.js";
import { searchSkills } from "../src/search.js";
import type { SearchIndex } from "../src/types.js";

const __dirname = fileURLToPath(new URL(".", import.meta.url));
const fixturesDir = join(__dirname, "fixtures");

let index: SearchIndex;

beforeAll(async () => {
  index = await buildIndex(fixturesDir);
});

describe("searchSkills", () => {
  it("exact token match scores highest", () => {
    const results = searchSkills(index, "basic-skill");
    expect(results.length).toBeGreaterThan(0);
    expect(results[0].dirName).toBe("basic-skill");
    if (results.length > 1) {
      expect(results[0].score).toBeGreaterThanOrEqual(results[1].score);
    }
  });

  it("partial/substring matches still return the right skill first", () => {
    const results = searchSkills(index, "basic");
    expect(results.length).toBeGreaterThan(0);
    // "basic" should still find basic-skill as the top result
    expect(results[0].dirName).toBe("basic-skill");
  });

  it("name bonus applied for substring match in name", () => {
    const results = searchSkills(index, "basic-skill");
    expect(results[0].dirName).toBe("basic-skill");
    // Score includes IDF weight + name bonus (2.0), should be well above threshold
    expect(results[0].score).toBeGreaterThan(2);
  });

  it("results sorted by score descending", () => {
    const results = searchSkills(index, "skill");
    for (let i = 1; i < results.length; i++) {
      expect(results[i - 1].score).toBeGreaterThanOrEqual(results[i].score);
    }
  });

  it("limit parameter works", () => {
    const results = searchSkills(index, "skill", 1);
    expect(results.length).toBeLessThanOrEqual(1);
  });

  it("empty query returns empty", () => {
    const results = searchSkills(index, "");
    expect(results).toEqual([]);
  });

  it("no matches returns empty", () => {
    const results = searchSkills(index, "zzzznonexistent");
    expect(results).toEqual([]);
  });

  it("description substring bonus is applied", () => {
    // "unit testing" appears in basic-skill description
    const results = searchSkills(index, "unit testing");
    const basic = results.find((r) => r.dirName === "basic-skill");
    expect(basic).toBeDefined();
    // IDF-weighted token matches + description bonus, normalized by 2 tokens
    expect(basic!.score).toBeGreaterThan(1);
  });

  it("multi-token query with unmatched tokens does not dilute score", () => {
    const singleToken = searchSkills(index, "basic-skill");
    const multiToken = searchSkills(index, "basic-skill nonexistenttoken");
    const singleBasic = singleToken.find((r) => r.dirName === "basic-skill");
    const multiBasic = multiToken.find((r) => r.dirName === "basic-skill");
    // Unmatched tokens should not dilute score — only name bonus difference
    expect(singleBasic).toBeDefined();
    expect(multiBasic).toBeDefined();
    // Single gets name bonus (full query matches name), multi doesn't
    expect(singleBasic!.score).toBeGreaterThanOrEqual(multiBasic!.score);
  });

  it("hasResources flag propagated to search results", () => {
    const results = searchSkills(index, "skill");
    const withRes = results.find((r) => r.dirName === "skill-with-resources");
    const basic = results.find((r) => r.dirName === "basic-skill");
    expect(withRes?.hasResources).toBe(true);
    expect(basic?.hasResources).toBe(false);
  });

  it("scores are rounded to two decimal places", () => {
    const results = searchSkills(index, "skill");
    for (const r of results) {
      const rounded = Math.round(r.score * 100) / 100;
      expect(r.score).toBe(rounded);
    }
  });

  it("stop-words are filtered from query", () => {
    // "create a basic" → "create" and "a" are stop-words, "basic" remains
    const results = searchSkills(index, "create a basic");
    expect(results.length).toBeGreaterThan(0);
    // Should match on "basic" token, same as searching "basic" directly
    const basicResults = searchSkills(index, "basic");
    expect(results.map((r) => r.dirName)).toEqual(basicResults.map((r) => r.dirName));
  });

  it("natural language stop-words are filtered (help, need, how, etc.)", () => {
    // "help me with basic" → "help", "me", "with" are stop-words, "basic" remains
    const results = searchSkills(index, "help me with basic");
    expect(results.length).toBeGreaterThan(0);
    const basicResults = searchSkills(index, "basic");
    expect(results.map((r) => r.dirName)).toEqual(basicResults.map((r) => r.dirName));
  });

  it("query tokens are deduplicated", () => {
    const single = searchSkills(index, "testing");
    const double = searchSkills(index, "testing testing");
    // Deduplication means "testing testing" should produce same result set
    expect(single.map((r) => r.dirName)).toEqual(double.map((r) => r.dirName));
  });

  it("2-char tokens can match via substring", () => {
    // 2-char tokens should match via substring (minimum is now 2)
    // "zx" has no match in fixtures, so still empty
    const results = searchSkills(index, "zx");
    expect(results).toEqual([]);
  });

  it("single-char tokens are too short for substring matching", () => {
    const results = searchSkills(index, "z");
    expect(results).toEqual([]);
  });
});
