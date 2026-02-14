import { readFile, readdir } from "node:fs/promises";
import { join } from "node:path";
import type { SkillEntry } from "./types.js";

export async function loadSkill(
  entry: SkillEntry,
  skillsDir: string,
  includeResources: boolean = false,
): Promise<string> {
  const skillPath = join(skillsDir, entry.dirName, "SKILL.md");
  let content = await readFile(skillPath, "utf-8");

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
