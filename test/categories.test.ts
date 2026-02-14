import { describe, it, expect } from "vitest";
import { buildCategories } from "../src/categories.js";
import type { SkillEntry } from "../src/types.js";

function makeEntry(dirName: string, description = ""): SkillEntry {
  return {
    dirName,
    frontmatter: { name: dirName, description },
    searchTokens: new Set(),
    hasResources: false,
    resourceFiles: [],
  };
}

describe("buildCategories", () => {
  it("classifies skills by keyword in dirName", () => {
    const entries = [
      makeEntry("react-hooks"),
      makeEntry("docker-setup"),
      makeEntry("python-basics"),
    ];
    const categories = buildCategories(entries);

    expect(categories.get("Frontend")).toContain("react-hooks");
    expect(categories.get("DevOps & Infra")).toContain("docker-setup");
    expect(categories.get("Python")).toContain("python-basics");
  });

  it("classifies skills by keyword in description", () => {
    const entries = [
      makeEntry("my-skill", "How to do tdd well"),
      makeEntry("another-skill", "Deploy with kubernetes"),
    ];
    const categories = buildCategories(entries);

    expect(categories.get("Testing")).toContain("my-skill");
    expect(categories.get("DevOps & Infra")).toContain("another-skill");
  });

  it("puts unmatched skills in Other", () => {
    const entries = [makeEntry("random-stuff", "No matching keywords here")];
    const categories = buildCategories(entries);

    expect(categories.get("Other")).toContain("random-stuff");
  });

  it("assigns each skill to exactly one category", () => {
    const entries = [
      makeEntry("react-testing", "Testing react components"),
      makeEntry("docker-setup"),
      makeEntry("random-thing"),
    ];
    const categories = buildCategories(entries);

    const allAssigned = [...categories.values()].flat();
    expect(allAssigned).toHaveLength(entries.length);
    // No duplicates
    expect(new Set(allAssigned).size).toBe(entries.length);
  });

  it("first matching category wins", () => {
    // "react-testing" has both frontend (react) and testing keywords
    // Frontend comes first in the keyword list
    const entries = [makeEntry("react-testing", "Testing react components")];
    const categories = buildCategories(entries);

    expect(categories.get("Frontend")).toContain("react-testing");
    expect(categories.has("Testing") && categories.get("Testing")!.includes("react-testing")).toBe(false);
  });

  it("returns empty map for empty entries", () => {
    const categories = buildCategories([]);
    expect(categories.size).toBe(0);
  });

  it("matches keywords case-insensitively", () => {
    const entries = [makeEntry("MY-REACT-APP", "A DOCKER deployment")];
    const categories = buildCategories(entries);

    // Should match "react" from Frontend even though dirName is uppercase
    expect(categories.get("Frontend")).toContain("MY-REACT-APP");
  });
});
