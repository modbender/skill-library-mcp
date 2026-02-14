import { describe, it, expect, beforeAll } from "vitest";
import { join } from "node:path";
import { fileURLToPath } from "node:url";
import { buildIndex } from "../src/skill-index.js";
import { loadSkill } from "../src/loader.js";
import type { SkillEntry } from "../src/types.js";

const __dirname = fileURLToPath(new URL(".", import.meta.url));
const fixturesDir = join(__dirname, "fixtures");

let index: SkillEntry[];

beforeAll(async () => {
  index = await buildIndex(fixturesDir);
});

describe("loadSkill", () => {
  it("loads SKILL.md content", async () => {
    const entry = index.find((e) => e.dirName === "basic-skill")!;
    const content = await loadSkill(entry, fixturesDir);
    expect(content).toContain("# Basic Skill");
    expect(content).toContain("basic skill used for testing");
  });

  it("appends resources when includeResources=true", async () => {
    const entry = index.find((e) => e.dirName === "skill-with-resources")!;
    const content = await loadSkill(entry, fixturesDir, true);
    expect(content).toContain("# Skill With Resources");
    expect(content).toContain("# Resource: examples.md");
    expect(content).toContain("# Resource: guide.md");
  });

  it("resources sorted alphabetically", async () => {
    const entry = index.find((e) => e.dirName === "skill-with-resources")!;
    const content = await loadSkill(entry, fixturesDir, true);
    const examplesIdx = content.indexOf("# Resource: examples.md");
    const guideIdx = content.indexOf("# Resource: guide.md");
    // examples.md comes before guide.md alphabetically
    expect(examplesIdx).toBeLessThan(guideIdx);
  });

  it("without resources flag, only SKILL.md returned", async () => {
    const entry = index.find((e) => e.dirName === "skill-with-resources")!;
    const content = await loadSkill(entry, fixturesDir, false);
    expect(content).toContain("# Skill With Resources");
    expect(content).not.toContain("# Resource:");
  });

  it("resource sections have '# Resource: filename.md' headers", async () => {
    const entry = index.find((e) => e.dirName === "skill-with-resources")!;
    const content = await loadSkill(entry, fixturesDir, true);
    const resourceHeaders = content.match(/# Resource: [\w-]+\.md/g);
    expect(resourceHeaders).toHaveLength(2);
    expect(resourceHeaders).toContain("# Resource: examples.md");
    expect(resourceHeaders).toContain("# Resource: guide.md");
  });

  it("loads hyphenated resource filenames correctly", async () => {
    const entry = index.find((e) => e.dirName === "skill-with-hyphenated-resources")!;
    const content = await loadSkill(entry, fixturesDir, true);
    expect(content).toContain("# Resource: implementation-playbook.md");
    expect(content).toContain("# Resource: quick-start-guide.md");
  });

  it("resource sections separated by --- dividers", async () => {
    const entry = index.find((e) => e.dirName === "skill-with-hyphenated-resources")!;
    const content = await loadSkill(entry, fixturesDir, true);
    const dividers = content.match(/\n\n---\n\n# Resource:/g);
    expect(dividers).toHaveLength(2);
  });
});
