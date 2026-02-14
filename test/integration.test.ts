import { describe, it, expect, beforeAll } from "vitest";
import { join } from "node:path";
import { fileURLToPath } from "node:url";
import { buildIndex } from "../src/skill-index.js";
import { searchSkills } from "../src/search.js";
import { loadSkill } from "../src/loader.js";
import type { SkillEntry } from "../src/types.js";

const __dirname = fileURLToPath(new URL(".", import.meta.url));
const skillsDir = join(__dirname, "..", "skills");

let index: SkillEntry[];

beforeAll(async () => {
  index = await buildIndex(skillsDir);
});

describe("integration: real skills/ directory", () => {
  it("indexes all skills (expect ≥700)", () => {
    expect(index.length).toBeGreaterThanOrEqual(700);
  });

  it("every entry has non-empty name", () => {
    for (const entry of index) {
      expect(entry.frontmatter.name).toBeTruthy();
    }
  });

  it("every entry has searchTokens", () => {
    for (const entry of index) {
      expect(entry.searchTokens.size).toBeGreaterThan(0);
    }
  });

  it("multiline description parsed correctly (brainstorming skill)", () => {
    const brainstorming = index.find((e) => e.dirName === "brainstorming");
    expect(brainstorming).toBeDefined();
    // Folded scalar should produce a single-line string
    expect(brainstorming!.frontmatter.description).not.toContain("\n");
    expect(brainstorming!.frontmatter.description).toContain("creative or constructive work");
  });

  it("skills with resources detected (expect ≥90)", () => {
    const withResources = index.filter((e) => e.hasResources);
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
    const entry = index.find((e) => e.dirName === "brainstorming")!;
    const content = await loadSkill(entry, skillsDir);
    expect(content).toContain("# Brainstorming");
    expect(content).toContain("name: brainstorming");
  });

  it("loadSkill with resources loads hyphenated filenames (stride-analysis-patterns)", async () => {
    const entry = index.find((e) => e.dirName === "stride-analysis-patterns")!;
    expect(entry.hasResources).toBe(true);
    const content = await loadSkill(entry, skillsDir, true);
    expect(content).toContain("# Resource: implementation-playbook.md");
  });
});
