import { readFile, readdir } from "node:fs/promises";
import { join, resolve } from "node:path";
import type { SkillEntry } from "./types.js";

export async function loadSkill(
  entry: SkillEntry,
  skillsDir: string,
  includeResources: boolean = false,
): Promise<string> {
  const skillDir = join(skillsDir, entry.dirName);
  const skillPath = join(skillDir, "SKILL.md");
  const absoluteSkillDir = resolve(skillDir);
  let content = `> **Skill directory**: ${absoluteSkillDir}\n> Resolve relative paths (scripts/, resources/, etc.) against this directory.\n\n`;
  content += await readFile(skillPath, "utf-8");

  if (includeResources && entry.hasResources) {
    const resourceDir = join(skillsDir, entry.dirName, "resources");

    try {
      const files = await readdir(resourceDir);
      const mdFiles = files.filter((f) => f.endsWith(".md")).sort();

      for (const file of mdFiles) {
        const resourceContent = await readFile(join(resourceDir, file), "utf-8");
        content += `\n\n---\n\n# Resource: ${file}\n\n${resourceContent}`;
      }
    } catch {
      // Resources directory not accessible
    }
  }

  return content;
}
