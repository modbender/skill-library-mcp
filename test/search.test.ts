import { describe, it, expect, beforeAll } from "vitest";
import { join } from "node:path";
import { fileURLToPath } from "node:url";
import { buildIndex } from "../src/skill-index.js";
import { searchSkills } from "../src/search.js";
import type { SkillEntry } from "../src/types.js";

const __dirname = fileURLToPath(new URL(".", import.meta.url));
const fixturesDir = join(__dirname, "fixtures");

let index: SkillEntry[];

beforeAll(async () => {
  index = await buildIndex(fixturesDir);
});

describe("searchSkills", () => {
  it("exact token match scores highest", () => {
    const results = searchSkills(index, "basic-skill");
    expect(results.length).toBeGreaterThan(0);
    expect(results[0].dirName).toBe("basic-skill");
    // basic-skill should score higher than skill-with-resources
    if (results.length > 1) {
      expect(results[0].score).toBeGreaterThanOrEqual(results[1].score);
    }
  });

  it("partial/substring matches score lower than exact", () => {
    // "basic" is a substring of "basic-skill" token
    const results = searchSkills(index, "basic");
    expect(results.length).toBeGreaterThan(0);

    const exactResults = searchSkills(index, "basic-skill");
    // Exact match on name should score >= partial
    expect(exactResults[0].score).toBeGreaterThanOrEqual(results[0].score);
  });

  it("name substring bonus (+0.5) applied", () => {
    // Searching "basic-skill" matches the name exactly as substring
    const results = searchSkills(index, "basic-skill");
    expect(results[0].dirName).toBe("basic-skill");
    // Score includes the +0.5 name bonus
    expect(results[0].score).toBeGreaterThan(1);
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

  it("description substring bonus (+0.3) is applied", () => {
    // "unit testing" appears in basic-skill description
    const results = searchSkills(index, "unit testing");
    const basic = results.find((r) => r.dirName === "basic-skill");
    expect(basic).toBeDefined();
    // Score should include the +0.3 description bonus
    // Token matches: "unit" exact +1, "testing" exact +1 = 2
    // Description contains "unit testing" → +0.3
    // Normalized by 2 tokens → (2 + 0.3) / 2 = 1.15
    expect(basic!.score).toBeGreaterThan(1);
  });

  it("multi-token query normalizes score by token count", () => {
    const singleToken = searchSkills(index, "basic-skill");
    const multiToken = searchSkills(index, "basic-skill nonexistenttoken");
    const singleBasic = singleToken.find((r) => r.dirName === "basic-skill");
    const multiBasic = multiToken.find((r) => r.dirName === "basic-skill");
    // Multi-token query divides by more tokens, so score should be lower
    if (singleBasic && multiBasic) {
      expect(singleBasic.score).toBeGreaterThan(multiBasic.score);
    }
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
});
