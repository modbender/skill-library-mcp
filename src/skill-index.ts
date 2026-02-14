import { readdir, readFile, access } from "node:fs/promises";
import { join } from "node:path";
import { parse as parseYaml } from "yaml";
import type { SkillEntry, SkillFrontmatter } from "./types.js";

function parseFrontmatter(content: string): SkillFrontmatter | null {
  const match = content.match(/^---\n([\s\S]*?)\n---/);
  if (!match) return null;

  try {
    const parsed = parseYaml(match[1]);
    if (!parsed || typeof parsed.name !== "string") return null;
    return {
      name: parsed.name,
      description: typeof parsed.description === "string" ? parsed.description.trim() : "",
      metadata: parsed.metadata,
      allowedTools: parsed.allowedTools,
    };
  } catch {
    return null;
  }
}

function tokenize(text: string): Set<string> {
  const words = text.toLowerCase().replace(/[^a-z0-9\-]/g, " ").split(/\s+/).filter(Boolean);
  return new Set(words);
}

export async function buildIndex(skillsDir: string): Promise<SkillEntry[]> {
  const entries: SkillEntry[] = [];
  let dirs: string[];

  try {
    dirs = await readdir(skillsDir);
  } catch {
    return entries;
  }

  for (const dirName of dirs) {
    const skillPath = join(skillsDir, dirName, "SKILL.md");

    try {
      await access(skillPath);
    } catch {
      continue;
    }

    const content = await readFile(skillPath, "utf-8");
    const frontmatter = parseFrontmatter(content);
    if (!frontmatter) continue;

    // Check for resources
    const resourceDir = join(skillsDir, dirName, "resources");
    let hasResources = false;
    let resourceFiles: string[] = [];

    try {
      const files = await readdir(resourceDir);
      resourceFiles = files.filter((f) => f.endsWith(".md"));
      hasResources = resourceFiles.length > 0;
    } catch {
      // No resources directory
    }

    const searchTokens = new Set([
      ...tokenize(frontmatter.name),
      ...tokenize(frontmatter.description),
    ]);

    entries.push({
      dirName,
      frontmatter,
      searchTokens,
      hasResources,
      resourceFiles,
    });
  }

  return entries;
}
