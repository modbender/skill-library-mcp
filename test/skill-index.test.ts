import { describe, it, expect } from "vitest";
import { join } from "node:path";
import { fileURLToPath } from "node:url";
import { buildIndex } from "../src/skill-index.js";

const __dirname = fileURLToPath(new URL(".", import.meta.url));
const fixturesDir = join(__dirname, "fixtures");

describe("buildIndex", () => {
  it("parses valid skills and counts entries correctly", async () => {
    const entries = await buildIndex(fixturesDir);
    // basic-skill, skill-with-resources, multiline-description,
    // skill-with-hyphenated-resources, empty-description, allowed-tools
    expect(entries.length).toBe(6);
  });

  it("extracts frontmatter fields (name, description)", async () => {
    const entries = await buildIndex(fixturesDir);
    const basic = entries.find((e) => e.dirName === "basic-skill");
    expect(basic).toBeDefined();
    expect(basic!.frontmatter.name).toBe("basic-skill");
    expect(basic!.frontmatter.description).toBe(
      "A basic test skill for unit testing",
    );
  });

  it("extracts metadata from frontmatter", async () => {
    const entries = await buildIndex(fixturesDir);
    const basic = entries.find((e) => e.dirName === "basic-skill");
    expect(basic!.frontmatter.metadata).toEqual({
      category: "testing",
      difficulty: "easy",
    });
  });

  it("populates searchTokens from name and description", async () => {
    const entries = await buildIndex(fixturesDir);
    const basic = entries.find((e) => e.dirName === "basic-skill");
    expect(basic!.searchTokens).toBeInstanceOf(Set);
    expect(basic!.searchTokens.has("basic-skill")).toBe(true);
    expect(basic!.searchTokens.has("testing")).toBe(true);
    expect(basic!.searchTokens.has("unit")).toBe(true);
  });

  it("detects hasResources and resourceFiles", async () => {
    const entries = await buildIndex(fixturesDir);
    const withResources = entries.find(
      (e) => e.dirName === "skill-with-resources",
    );
    expect(withResources!.hasResources).toBe(true);
    expect(withResources!.resourceFiles).toContain("guide.md");
    expect(withResources!.resourceFiles).toContain("examples.md");

    const basic = entries.find((e) => e.dirName === "basic-skill");
    expect(basic!.hasResources).toBe(false);
    expect(basic!.resourceFiles).toEqual([]);
  });

  it("skips invalid frontmatter", async () => {
    const entries = await buildIndex(fixturesDir);
    const invalid = entries.find((e) => e.dirName === "invalid-frontmatter");
    expect(invalid).toBeUndefined();
  });

  it("skips missing frontmatter", async () => {
    const entries = await buildIndex(fixturesDir);
    const noFm = entries.find((e) => e.dirName === "no-frontmatter");
    expect(noFm).toBeUndefined();
  });

  it("handles missing directory", async () => {
    const entries = await buildIndex("/nonexistent/path");
    expect(entries).toEqual([]);
  });

  it("parses multiline YAML description", async () => {
    const entries = await buildIndex(fixturesDir);
    const ml = entries.find((e) => e.dirName === "multiline-description");
    expect(ml).toBeDefined();
    expect(ml!.frontmatter.description).toContain("multiline description");
    expect(ml!.frontmatter.description).toContain("YAML folded scalar");
    // Folded scalar collapses newlines into spaces
    expect(ml!.frontmatter.description).not.toContain("\n");
  });

  it("handles missing description field gracefully", async () => {
    const entries = await buildIndex(fixturesDir);
    const empty = entries.find((e) => e.dirName === "empty-description");
    expect(empty).toBeDefined();
    expect(empty!.frontmatter.description).toBe("");
  });

  it("extracts allowedTools array from frontmatter", async () => {
    const entries = await buildIndex(fixturesDir);
    const at = entries.find((e) => e.dirName === "allowed-tools");
    expect(at).toBeDefined();
    expect(at!.frontmatter.allowedTools).toEqual(["Bash", "Read"]);
  });

  it("detects hyphenated resource filenames", async () => {
    const entries = await buildIndex(fixturesDir);
    const hyph = entries.find((e) => e.dirName === "skill-with-hyphenated-resources");
    expect(hyph).toBeDefined();
    expect(hyph!.hasResources).toBe(true);
    expect(hyph!.resourceFiles).toContain("implementation-playbook.md");
    expect(hyph!.resourceFiles).toContain("quick-start-guide.md");
  });

  it("tokenize preserves hyphens within tokens", async () => {
    const entries = await buildIndex(fixturesDir);
    const basic = entries.find((e) => e.dirName === "basic-skill");
    // "basic-skill" should be a single token, not split on hyphen
    expect(basic!.searchTokens.has("basic-skill")).toBe(true);
  });
});
