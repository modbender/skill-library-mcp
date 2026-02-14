import { readdir, readFile, access } from "node:fs/promises";
import { join } from "node:path";
import { createHash } from "node:crypto";
import { parse as parseYaml } from "yaml";

interface SkillMeta {
  dirName: string;
  name: string;
  description: string;
}

export interface DuplicateReport {
  exactDuplicates: SkillMeta[][];
  nearDuplicates: { pair: [SkillMeta, SkillMeta]; similarity: number }[];
}

function parseFrontmatter(content: string): { name: string; description: string } | null {
  const match = content.match(/^---\n([\s\S]*?)\n---/);
  if (!match) return null;
  try {
    const parsed = parseYaml(match[1]);
    if (!parsed || typeof parsed.name !== "string") return null;
    return {
      name: parsed.name,
      description: typeof parsed.description === "string" ? parsed.description.trim() : "",
    };
  } catch {
    return null;
  }
}

function jaccardSimilarity(a: string, b: string): number {
  const wordsA = new Set(a.toLowerCase().split(/\s+/).filter(Boolean));
  const wordsB = new Set(b.toLowerCase().split(/\s+/).filter(Boolean));
  if (wordsA.size === 0 && wordsB.size === 0) return 1;
  if (wordsA.size === 0 || wordsB.size === 0) return 0;

  let intersection = 0;
  for (const w of wordsA) {
    if (wordsB.has(w)) intersection++;
  }
  const union = wordsA.size + wordsB.size - intersection;
  return union === 0 ? 0 : intersection / union;
}

export async function findDuplicates(skillsDir: string): Promise<DuplicateReport> {
  const skills: SkillMeta[] = [];
  let dirs: string[];

  try {
    dirs = await readdir(skillsDir);
  } catch {
    return { exactDuplicates: [], nearDuplicates: [] };
  }

  for (const dirName of dirs) {
    const skillPath = join(skillsDir, dirName, "SKILL.md");
    try {
      await access(skillPath);
    } catch {
      continue;
    }

    const content = await readFile(skillPath, "utf-8");
    const fm = parseFrontmatter(content);
    if (!fm) continue;

    skills.push({ dirName, name: fm.name, description: fm.description });
  }

  // Find exact duplicates: identical name + description hash
  const hashMap = new Map<string, SkillMeta[]>();
  for (const skill of skills) {
    const hash = createHash("sha256")
      .update(`${skill.name}\n${skill.description}`)
      .digest("hex");
    const group = hashMap.get(hash) ?? [];
    group.push(skill);
    hashMap.set(hash, group);
  }

  const exactDuplicates = [...hashMap.values()].filter((group) => group.length > 1);

  // Find near duplicates: Jaccard word similarity > 0.8 on descriptions
  const nearDuplicates: DuplicateReport["nearDuplicates"] = [];
  for (let i = 0; i < skills.length; i++) {
    for (let j = i + 1; j < skills.length; j++) {
      const a = skills[i];
      const b = skills[j];
      // Skip exact dupes (already reported)
      if (a.name === b.name && a.description === b.description) continue;
      // Only check if descriptions are non-empty
      if (!a.description || !b.description) continue;

      const sim = jaccardSimilarity(a.description, b.description);
      if (sim > 0.8) {
        nearDuplicates.push({ pair: [a, b], similarity: Math.round(sim * 100) / 100 });
      }
    }
  }

  return { exactDuplicates, nearDuplicates };
}

// CLI entrypoint
if (process.argv[1] && (process.argv[1].endsWith("dedup.ts") || process.argv[1].endsWith("dedup.js"))) {
  const dir = process.argv[2] || join(process.cwd(), "skills");

  findDuplicates(dir).then((report) => {
    if (report.exactDuplicates.length > 0) {
      console.log(`\n❌ Found ${report.exactDuplicates.length} exact duplicate group(s):\n`);
      for (const group of report.exactDuplicates) {
        console.log(`  Name: "${group[0].name}"`);
        console.log(`  Dirs: ${group.map((s) => s.dirName).join(", ")}\n`);
      }
    } else {
      console.log("\n✅ No exact duplicates found.\n");
    }

    if (report.nearDuplicates.length > 0) {
      console.log(`⚠️  Found ${report.nearDuplicates.length} near-duplicate pair(s):\n`);
      for (const { pair, similarity } of report.nearDuplicates) {
        console.log(`  ${pair[0].dirName} ↔ ${pair[1].dirName} (${(similarity * 100).toFixed(0)}% similar)`);
      }
      console.log();
    } else {
      console.log("✅ No near-duplicates found.\n");
    }

    process.exit(report.exactDuplicates.length > 0 ? 1 : 0);
  });
}
