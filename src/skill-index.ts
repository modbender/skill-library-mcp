import { readdir, readFile, access } from "node:fs/promises";
import { join } from "node:path";
import { parse as parseYaml } from "yaml";
import type { SkillEntry, SkillFrontmatter, SearchIndex } from "./types.js";

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
  const tokens = new Set<string>();
  for (const word of words) {
    tokens.add(word);
    // Split hyphenated tokens into sub-tokens
    if (word.includes("-")) {
      for (const part of word.split("-")) {
        if (part) tokens.add(part);
      }
    }
  }
  return tokens;
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
