import { describe, it, expect, beforeAll } from "vitest";
import { join } from "node:path";
import { fileURLToPath } from "node:url";
import { buildIndex } from "../src/skill-index.js";
import { searchSkills } from "../src/search.js";
import { loadSkill } from "../src/loader.js";
import type { SearchIndex } from "../src/types.js";

const __dirname = fileURLToPath(new URL(".", import.meta.url));
const skillsDir = join(__dirname, "..", "skills");

let index: SearchIndex;

beforeAll(async () => {
  index = await buildIndex(skillsDir);
});

describe("integration: real skills/ directory", () => {
  it("indexes all skills (expect ≥690)", () => {
    expect(index.entries.length).toBeGreaterThanOrEqual(690);
  });

  it("every entry has non-empty name", () => {
    for (const entry of index.entries) {
      expect(entry.frontmatter.name).toBeTruthy();
    }
  });

  it("every entry has searchTokens", () => {
    for (const entry of index.entries) {
      expect(entry.searchTokens.size).toBeGreaterThan(0);
    }
  });

  it("IDF scores computed for real index", () => {
    expect(index.idfScores.size).toBeGreaterThan(0);
    expect(index.totalDocs).toBeGreaterThanOrEqual(690);
  });

  it("multiline description parsed correctly (brainstorming skill)", () => {
    const brainstorming = index.entries.find((e) => e.dirName === "brainstorming");
    expect(brainstorming).toBeDefined();
    // Folded scalar should produce a single-line string
    expect(brainstorming!.frontmatter.description).not.toContain("\n");
    expect(brainstorming!.frontmatter.description).toContain("creative or constructive work");
  });

  it("skills with resources detected (expect ≥90)", () => {
    const withResources = index.entries.filter((e) => e.hasResources);
    expect(withResources.length).toBeGreaterThanOrEqual(90);
  });

  it("search returns relevant results for 'debugging'", () => {
    const results = searchSkills(index, "debugging");
    expect(results.length).toBeGreaterThan(0);
    // At least one result should have "debug" in name or description
    const hasDebug = results.some(
      (r) => r.name.includes("debug") || r.description.toLowerCase().includes("debug"),
    );
    expect(hasDebug).toBe(true);
  });

  it("loadSkill loads a known skill (brainstorming)", async () => {
    const entry = index.entries.find((e) => e.dirName === "brainstorming")!;
    const content = await loadSkill(entry, skillsDir);
    expect(content).toContain("**Skill directory**:");
    expect(content).toContain("# Brainstorming");
    expect(content).toContain("name: brainstorming");
  });

  it("loadSkill with resources loads hyphenated filenames (stride-analysis-patterns)", async () => {
    const entry = index.entries.find((e) => e.dirName === "stride-analysis-patterns")!;
    expect(entry.hasResources).toBe(true);
    const content = await loadSkill(entry, skillsDir, true);
    expect(content).toContain("# Resource: implementation-playbook.md");
  });
});

describe("integration: search relevance", () => {
  it("'react' returns React skills in top 5, not autonomous-agents first", () => {
    const results = searchSkills(index, "react");
    expect(results.length).toBeGreaterThan(0);
    const top5 = results.slice(0, 5);
    const hasReactSkill = top5.some(
      (r) => r.dirName.includes("react") || r.name.toLowerCase().includes("react"),
    );
    expect(hasReactSkill).toBe(true);
    // autonomous-agents should NOT be #1
    expect(results[0].dirName).not.toBe("autonomous-agents");
  });

  it("'terraform' returns terraform skills in top 3", () => {
    const results = searchSkills(index, "terraform");
    expect(results.length).toBeGreaterThan(0);
    const top3 = results.slice(0, 3);
    const hasTerraform = top3.some(
      (r) => r.dirName.includes("terraform") || r.name.toLowerCase().includes("terraform"),
    );
    expect(hasTerraform).toBe(true);
  });

  it("'build a REST API' returns backend/API skills in top 5", () => {
    const results = searchSkills(index, "build a REST API");
    expect(results.length).toBeGreaterThan(0);
    const top5 = results.slice(0, 5);
    const hasApiSkill = top5.some(
      (r) => r.name.toLowerCase().includes("api") || r.description.toLowerCase().includes("api"),
    );
    expect(hasApiSkill).toBe(true);
  });

  it("'write tests' returns testing skills in top 5", () => {
    const results = searchSkills(index, "write tests");
    expect(results.length).toBeGreaterThan(0);
    const top5 = results.slice(0, 5);
    const hasTestSkill = top5.some(
      (r) => r.name.toLowerCase().includes("test") || r.description.toLowerCase().includes("test"),
    );
    expect(hasTestSkill).toBe(true);
  });

  it("natural language query finds single-token skills (normalization fix)", () => {
    // "help with brainstorming" should still find brainstorming
    const results = searchSkills(index, "help with brainstorming");
    const brainstorming = results.find((r) => r.dirName === "brainstorming");
    expect(brainstorming).toBeDefined();
  });

  it("short acronym queries find matching skills (2-char substring)", () => {
    // "ai" should find ai-engineer, ai-product, etc.
    const results = searchSkills(index, "ai");
    expect(results.length).toBeGreaterThan(0);
    const hasAiSkill = results.some(
      (r) => r.dirName.includes("ai-") || r.name.toLowerCase().includes("ai"),
    );
    expect(hasAiSkill).toBe(true);
  });

  it("every skill is findable by its own name", () => {
    const unfindable: string[] = [];
    for (const entry of index.entries) {
      const results = searchSkills(index, entry.frontmatter.name);
      const found = results.some((r) => r.dirName === entry.dirName);
      if (!found) unfindable.push(entry.dirName);
    }
    expect(unfindable).toEqual([]);
  });
});
