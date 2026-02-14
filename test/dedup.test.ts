import { describe, it, expect } from "vitest";
import { join } from "node:path";
import { fileURLToPath } from "node:url";
import { findDuplicates, jaccardSimilarity } from "../src/dedup.js";

const __dirname = fileURLToPath(new URL(".", import.meta.url));
const dedupFixturesDir = join(__dirname, "fixtures-dedup");
const skillsDir = join(__dirname, "..", "skills");

describe("jaccardSimilarity", () => {
  it("returns 1 for identical strings", () => {
    expect(jaccardSimilarity("hello world", "hello world")).toBe(1);
  });

  it("returns 0 for completely different strings", () => {
    expect(jaccardSimilarity("hello world", "foo bar")).toBe(0);
  });

  it("returns 1 for two empty strings", () => {
    expect(jaccardSimilarity("", "")).toBe(1);
  });

  it("returns 0 when one string is empty", () => {
    expect(jaccardSimilarity("hello", "")).toBe(0);
    expect(jaccardSimilarity("", "hello")).toBe(0);
  });

  it("computes correct similarity for partial overlap", () => {
    // {"a", "b", "c"} vs {"b", "c", "d"} → intersection=2, union=4 → 0.5
    expect(jaccardSimilarity("a b c", "b c d")).toBe(0.5);
  });

  it("is case-insensitive", () => {
    expect(jaccardSimilarity("Hello World", "hello world")).toBe(1);
  });

  it("handles boundary around 0.8 threshold", () => {
    // {"a", "b", "c", "d", "e"} vs {"a", "b", "c", "d", "f"} → intersection=4, union=6 → 0.666...
    const below = jaccardSimilarity("a b c d e", "a b c d f");
    expect(below).toBeLessThan(0.8);

    // {"a", "b", "c", "d"} vs {"a", "b", "c", "d", "e"} → intersection=4, union=5 → 0.8
    const atBoundary = jaccardSimilarity("a b c d", "a b c d e");
    expect(atBoundary).toBe(0.8);
  });
});

describe("findDuplicates: fixtures", () => {
  it("detects exact duplicates (same name + description)", async () => {
    const report = await findDuplicates(dedupFixturesDir);
    expect(report.exactDuplicates.length).toBe(1);

    const group = report.exactDuplicates[0];
    const dirNames = group.map((s) => s.dirName).sort();
    expect(dirNames).toEqual(["skill-a", "skill-a-copy"]);
  });

  it("detects near-duplicates above 0.8 threshold", async () => {
    const report = await findDuplicates(dedupFixturesDir);
    expect(report.nearDuplicates.length).toBe(1);

    const { pair, similarity } = report.nearDuplicates[0];
    const dirNames = [pair[0].dirName, pair[1].dirName].sort();
    expect(dirNames).toEqual(["skill-b", "skill-c"]);
    expect(similarity).toBeGreaterThan(0.8);
  });

  it("handles skills with empty descriptions without crashing", async () => {
    const report = await findDuplicates(dedupFixturesDir);
    // empty-desc fixture has no description — should not appear in near-duplicates
    const hasEmpty = report.nearDuplicates.some(
      ({ pair }) => pair[0].dirName === "empty-desc" || pair[1].dirName === "empty-desc",
    );
    expect(hasEmpty).toBe(false);
  });

  it("returns empty report for nonexistent directory", async () => {
    const report = await findDuplicates("/tmp/nonexistent-skills-dir");
    expect(report.exactDuplicates).toEqual([]);
    expect(report.nearDuplicates).toEqual([]);
  });
});

describe("dedup: real skills/ directory", () => {
  it("has zero exact duplicates", async () => {
    const report = await findDuplicates(skillsDir);
    if (report.exactDuplicates.length > 0) {
      const details = report.exactDuplicates
        .map((g) => `  "${g[0].name}": ${g.map((s) => s.dirName).join(", ")}`)
        .join("\n");
      expect.fail(`Found exact duplicates:\n${details}`);
    }
  });

  it("reports near-duplicates without failing", async () => {
    const report = await findDuplicates(skillsDir);
    if (report.nearDuplicates.length > 0) {
      console.warn(
        `⚠️  ${report.nearDuplicates.length} near-duplicate pair(s) found:`,
        report.nearDuplicates.map(
          ({ pair, similarity }) => `${pair[0].dirName} ↔ ${pair[1].dirName} (${(similarity * 100).toFixed(0)}%)`,
        ),
      );
    }
    // This is a warning, not a failure
    expect(true).toBe(true);
  });
});
