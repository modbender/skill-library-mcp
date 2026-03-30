import { readdir, readFile } from "node:fs/promises";
import { join } from "node:path";
import { parse as parseYaml } from "yaml";
import { tokenize } from "./tokenize.js";
import type { SkillEntry, SkillFrontmatter, SearchIndex, SkillsBundle, SkillsIndex } from "./types.js";
import { buildCategories } from "./categories.js";

export function parseFrontmatter(content: string): SkillFrontmatter | null {
  const match = content.match(/^---\r?\n([\s\S]*?)\r?\n---/);
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
    return { entries, idfScores: new Map(), totalDocs: 0, categories: new Map() };
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

  const categories = buildCategories(entries);

  return { entries, idfScores, totalDocs, categories };
}

export function buildIndexFromBundle(bundle: SkillsBundle | SkillsIndex): SearchIndex {
  const entries: SkillEntry[] = [];

  for (const [dirName, entry] of Object.entries(bundle.skills)) {
    // Support both full bundle entries (with content) and index-only entries
    const frontmatter: SkillFrontmatter = "content" in entry
      ? (parseFrontmatter(entry.content) ?? { name: dirName, description: "" })
      : {
          name: (entry as SkillsIndex["skills"][string]).name,
          description: (entry as SkillsIndex["skills"][string]).description,
          metadata: (entry as SkillsIndex["skills"][string]).metadata,
          allowedTools: (entry as SkillsIndex["skills"][string]).allowedTools,
        };

    const resourceFiles = "resources" in entry && entry.resources
      ? Object.keys(entry.resources).filter((f) => f.endsWith(".md")).sort()
      : ("resourceFiles" in entry ? (entry as SkillsIndex["skills"][string]).resourceFiles : []);

    const searchTokens = new Set(
      [...tokenize(frontmatter.name), ...tokenize(frontmatter.description)],
    );

    entries.push({ dirName, frontmatter, searchTokens, hasResources: resourceFiles.length > 0, resourceFiles });
  }

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

  const categories = buildCategories(entries);
  return { entries, idfScores, totalDocs, categories };
}
