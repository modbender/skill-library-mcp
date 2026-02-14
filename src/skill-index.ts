import { readdir, readFile } from "node:fs/promises";
import { join } from "node:path";
import { parse as parseYaml } from "yaml";
import { tokenize } from "./tokenize.js";
import type { SkillEntry, SkillFrontmatter, SearchIndex } from "./types.js";

export function parseFrontmatter(content: string): SkillFrontmatter | null {
  const match = content.match(/^---\n([\s\S]*?)\n---/);
  if (!match) return null;

  try {
    const parsed = parseYaml(match[1]);
    if (!parsed || typeof parsed.name !== "string") return null;

    const metadata =
      parsed.metadata && typeof parsed.metadata === "object" && !Array.isArray(parsed.metadata)
        ? (parsed.metadata as Record<string, unknown>)
        : undefined;

    const allowedTools =
      Array.isArray(parsed.allowedTools) && parsed.allowedTools.every((t: unknown) => typeof t === "string")
        ? (parsed.allowedTools as string[])
        : undefined;

    return {
      name: parsed.name,
      description: typeof parsed.description === "string" ? parsed.description.trim() : "",
      metadata,
      allowedTools,
    };
  } catch {
    return null;
  }
}

export async function buildIndex(skillsDir: string): Promise<SearchIndex> {
  const entries: SkillEntry[] = [];
  let dirs: string[];

  try {
    dirs = await readdir(skillsDir);
  } catch {
    return { entries, idfScores: new Map(), totalDocs: 0 };
  }

  for (const dirName of dirs) {
    const skillPath = join(skillsDir, dirName, "SKILL.md");

    let content: string;
    try {
      content = await readFile(skillPath, "utf-8");
    } catch {
      continue;
    }

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

    const searchTokens = new Set(
      [...tokenize(frontmatter.name), ...tokenize(frontmatter.description)],
    );

    entries.push({
      dirName,
      frontmatter,
      searchTokens,
      hasResources,
      resourceFiles,
    });
  }

  // Compute IDF scores
  const totalDocs = entries.length;
  const docFrequency = new Map<string, number>();

  for (const entry of entries) {
    for (const token of entry.searchTokens) {
      docFrequency.set(token, (docFrequency.get(token) ?? 0) + 1);
    }
  }

  const idfScores = new Map<string, number>();
  for (const [token, df] of docFrequency) {
    idfScores.set(token, Math.log(totalDocs / df));
  }

  return { entries, idfScores, totalDocs };
}
