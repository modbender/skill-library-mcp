import { readdir, readFile, copyFile, mkdir, stat } from "node:fs/promises";
import { join, basename, extname } from "node:path";
import { findDuplicates, jaccardSimilarity } from "../src/dedup.js";
import { parseFrontmatter } from "../src/skill-index.js";

const NEAR_DUPE_THRESHOLD = 0.8;
const CONCURRENCY = 64;

interface SourceSkill {
  skillName: string;
  author: string;
  srcPath: string;
  description: string;
}

async function isDirectory(path: string): Promise<boolean> {
  try {
    return (await stat(path)).isDirectory();
  } catch {
    return false;
  }
}

/** Run async tasks with bounded concurrency */
async function parallel<T, R>(items: T[], concurrency: number, fn: (item: T) => Promise<R>): Promise<R[]> {
  const results: R[] = [];
  let index = 0;

  async function worker() {
    while (index < items.length) {
      const i = index++;
      results[i] = await fn(items[i]);
    }
  }

  await Promise.all(Array.from({ length: Math.min(concurrency, items.length) }, worker));
  return results;
}

/**
 * Fast discovery: two-level dir scan, only reads SKILL.md for colliding names.
 * Pass 1: enumerate author/skill-name dirs (no file reads)
 * Pass 2: read SKILL.md content only for skills that collide on name
 */
async function discoverSourceSkills(sourceDir: string): Promise<SourceSkill[]> {
  const topEntries = await readdir(sourceDir);
  console.log(`  Scanning ${topEntries.length} author directories...`);

  // Pass 1: collect all skill paths without reading content
  interface SkillRef { skillName: string; author: string; srcPath: string }
  const allRefs: SkillRef[] = [];

  await parallel(topEntries, CONCURRENCY, async (author) => {
    const authorPath = join(sourceDir, author);
    if (!(await isDirectory(authorPath))) return;

    let subEntries: string[];
    try {
      subEntries = await readdir(authorPath);
    } catch {
      return;
    }

    for (const sub of subEntries) {
      const subPath = join(authorPath, sub);
      // Quick check: does SKILL.md exist? Use stat instead of access+stat
      try {
        await stat(join(subPath, "SKILL.md"));
      } catch {
        continue;
      }
      allRefs.push({ skillName: sub, author, srcPath: subPath });
    }
  });

  console.log(`  Found ${allRefs.length} skills across ${topEntries.length} authors`);

  // Find which names collide (appear more than once)
  const nameCounts = new Map<string, number>();
  for (const ref of allRefs) {
    nameCounts.set(ref.skillName, (nameCounts.get(ref.skillName) ?? 0) + 1);
  }
  const collidingNames = new Set([...nameCounts.entries()].filter(([, c]) => c > 1).map(([n]) => n));
  console.log(`  ${collidingNames.size} name collision(s) to resolve via content comparison`);

  // Pass 2: read descriptions only for colliding skills
  const needsContent = allRefs.filter((r) => collidingNames.has(r.skillName));
  const descriptionMap = new Map<string, string>(); // srcPath -> description

  if (needsContent.length > 0) {
    console.log(`  Reading ${needsContent.length} SKILL.md files for collision resolution...`);
    await parallel(needsContent, CONCURRENCY, async (ref) => {
      try {
        const content = await readFile(join(ref.srcPath, "SKILL.md"), "utf-8");
        const fm = parseFrontmatter(content);
        descriptionMap.set(ref.srcPath, fm?.description ?? "");
      } catch {
        descriptionMap.set(ref.srcPath, "");
      }
    });
  }

  return allRefs.map((ref) => ({
    ...ref,
    description: descriptionMap.get(ref.srcPath) ?? "",
  }));
}

/**
 * Resolve source-level name collisions using content dedup.
 *   - Near-duplicates (Jaccard > threshold): keep first, skip rest
 *   - Meaningfully different: prefix with author name
 */
function resolveSourceCollisions(skills: SourceSkill[]): Map<string, SourceSkill> {
  const groups = new Map<string, SourceSkill[]>();
  for (const skill of skills) {
    const group = groups.get(skill.skillName) ?? [];
    group.push(skill);
    groups.set(skill.skillName, group);
  }

  const resolved = new Map<string, SourceSkill>();
  let dedupedCount = 0;
  let prefixedCount = 0;

  for (const [name, group] of groups) {
    if (group.length === 1) {
      resolved.set(name, group[0]);
      continue;
    }

    // Multiple skills with same name — content dedup
    const kept: SourceSkill[] = [];
    for (const skill of group) {
      const isDupe = kept.some(
        (existing) => jaccardSimilarity(existing.description, skill.description) > NEAR_DUPE_THRESHOLD,
      );
      if (isDupe) {
        dedupedCount++;
        continue;
      }
      kept.push(skill);
    }

    if (kept.length === 1) {
      resolved.set(name, kept[0]);
    } else {
      // Meaningfully different — prefix all with author
      for (const skill of kept) {
        const prefixed = skill.author ? `${skill.author}-${name}` : name;
        resolved.set(prefixed, skill);
        prefixedCount++;
      }
    }
  }

  if (dedupedCount > 0) {
    console.log(`  Deduped ${dedupedCount} source collision(s) (near-duplicate content skipped)`);
  }
  if (prefixedCount > 0) {
    console.log(`  Prefixed ${prefixedCount} skill(s) with author name (different content, same name)`);
  }

  return resolved;
}

async function getExistingDescriptions(
  skillsDir: string,
): Promise<Map<string, string>> {
  const dirs = await readdir(skillsDir);
  const existing = new Map<string, string>();

  await parallel(dirs, CONCURRENCY, async (dirName) => {
    try {
      const content = await readFile(join(skillsDir, dirName, "SKILL.md"), "utf-8");
      const fm = parseFrontmatter(content);
      existing.set(dirName, fm?.description ?? "");
    } catch {
      existing.set(dirName, "");
    }
  });

  return existing;
}

/**
 * Copy a skill directory selectively:
 *   - SKILL.md → target root
 *   - Other .md files → target/resources/
 *   - Everything else is dropped
 */
async function copySkillDir(srcPath: string, destPath: string): Promise<void> {
  await mkdir(destPath, { recursive: true });

  const entries = await readdir(srcPath, { withFileTypes: true });
  const extraMdFiles: string[] = [];

  for (const entry of entries) {
    if (entry.isDirectory()) {
      // Check for .md files in subdirectories (e.g. existing resources/)
      const subEntries = await readdir(join(srcPath, entry.name)).catch(() => []);
      for (const sub of subEntries) {
        if (typeof sub === "string" && extname(sub) === ".md") {
          extraMdFiles.push(join(entry.name, sub));
        }
      }
      continue;
    }

    if (!entry.isFile()) continue;

    if (entry.name === "SKILL.md") {
      await copyFile(join(srcPath, entry.name), join(destPath, entry.name));
    } else if (extname(entry.name) === ".md") {
      extraMdFiles.push(entry.name);
    }
    // Drop everything else (_meta.json, .js, .py, .json, .sh, etc.)
  }

  // Move extra .md files into resources/
  if (extraMdFiles.length > 0) {
    const resourcesDir = join(destPath, "resources");
    await mkdir(resourcesDir, { recursive: true });
    for (const mdFile of extraMdFiles) {
      const srcFile = join(srcPath, mdFile);
      // Flatten nested paths: "subdir/file.md" → "subdir-file.md"
      const destName = mdFile.includes("/") ? mdFile.replace(/\//g, "-") : mdFile;
      await copyFile(srcFile, join(resourcesDir, destName));
    }
  }
}

async function importSkills(
  sourceDir: string,
  targetDir: string,
  sourceName: string,
  dryRun: boolean,
): Promise<void> {
  console.log(`\nImporting skills from: ${sourceDir}`);
  console.log(`Target: ${targetDir}`);
  console.log(`Source: ${sourceName}`);
  console.log(`Mode: ${dryRun ? "DRY RUN" : "LIVE"}\n`);

  const t0 = Date.now();

  console.log("Step 1: Discovering source skills...");
  let sourceSkills: SourceSkill[];
  try {
    sourceSkills = await discoverSourceSkills(sourceDir);
  } catch (err) {
    console.error(`Failed to read source directory: ${err}`);
    process.exit(1);
  }
  console.log(`  Done in ${((Date.now() - t0) / 1000).toFixed(1)}s\n`);

  const t1 = Date.now();
  console.log("Step 2: Resolving source-level name collisions...");
  const resolved = resolveSourceCollisions(sourceSkills);
  console.log(`  ${resolved.size} unique skills after resolution`);
  console.log(`  Done in ${((Date.now() - t1) / 1000).toFixed(1)}s\n`);

  const t2 = Date.now();
  console.log("Step 3: Loading existing target skills...");
  const existing = await getExistingDescriptions(targetDir);
  console.log(`  ${existing.size} skills already in target`);
  console.log(`  Done in ${((Date.now() - t2) / 1000).toFixed(1)}s\n`);

  // Read descriptions for resolved skills that collide with existing target names
  // (we only read descriptions for source-level collisions earlier)
  const targetCollisions = [...resolved.entries()].filter(([name]) => existing.has(name));
  if (targetCollisions.length > 0) {
    const needsDesc = targetCollisions.filter(([, s]) => !s.description);
    if (needsDesc.length > 0) {
      console.log(`  Reading ${needsDesc.length} more SKILL.md files for target collision checks...`);
      await parallel(needsDesc, CONCURRENCY, async ([, skill]) => {
        try {
          const content = await readFile(join(skill.srcPath, "SKILL.md"), "utf-8");
          const fm = parseFrontmatter(content);
          skill.description = fm?.description ?? "";
        } catch {
          // leave empty
        }
      });
    }
  }

  let added = 0;
  let skippedSimilar = 0;
  let skippedConflict = 0;
  const conflicts: string[] = [];

  console.log("Step 4: Comparing against target...");
  for (const [targetName, skill] of resolved) {
    if (existing.has(targetName)) {
      const existingDesc = existing.get(targetName)!;
      const sim = jaccardSimilarity(existingDesc, skill.description);
      if (sim > NEAR_DUPE_THRESHOLD) {
        skippedSimilar++;
      } else {
        conflicts.push(`${targetName} (from ${skill.author}/${skill.skillName}, similarity: ${(sim * 100).toFixed(0)}%)`);
        skippedConflict++;
      }
      continue;
    }

    if (!dryRun) {
      await copySkillDir(skill.srcPath, join(targetDir, targetName));
    }
    added++;
  }

  const totalTime = ((Date.now() - t0) / 1000).toFixed(1);
  console.log(`\n${"=".repeat(50)}`);
  console.log(`Results (${totalTime}s):`);
  console.log(`  Source skills discovered: ${sourceSkills.length}`);
  console.log(`  After source dedup:      ${resolved.size}`);
  console.log(`  Would add:               ${added}`);
  console.log(`  Skipped (similar to existing): ${skippedSimilar}`);
  console.log(`  Skipped (name conflict, different content): ${skippedConflict}`);
  console.log(`${"=".repeat(50)}`);

  if (conflicts.length > 0) {
    console.log(`\nConflicts (name exists, content differs — review manually):`);
    for (const c of conflicts) {
      console.log(`  - ${c}`);
    }
  }

  if (!dryRun && added > 0) {
    console.log(`\nRunning post-import dedup check...`);
    const report = await findDuplicates(targetDir);
    if (report.exactDuplicates.length > 0) {
      console.log(`❌ ${report.exactDuplicates.length} exact duplicate group(s) found:`);
      for (const group of report.exactDuplicates) {
        console.log(`  "${group[0].name}": ${group.map((s) => s.dirName).join(", ")}`);
      }
    } else {
      console.log(`✅ No exact duplicates.`);
    }
    if (report.nearDuplicates.length > 0) {
      console.log(`⚠️  ${report.nearDuplicates.length} near-duplicate pair(s) — review with: pnpm dedup`);
    }
  }
}

// CLI
const args = process.argv.slice(2);
const sourceDir = args.find((a) => !a.startsWith("--"));
const sourceName = args.find((a) => a.startsWith("--source="))?.split("=")[1] ?? basename(sourceDir ?? "");
const dryRun = !args.includes("--no-dry-run");
const targetDir = args.find((a) => a.startsWith("--target="))?.split("=")[1] ?? join(process.cwd(), "skills");

if (!sourceDir) {
  console.error("Usage: tsx scripts/import-skills.ts <source-dir> [--source=name] [--target=dir] [--no-dry-run]");
  console.error("\nOptions:");
  console.error("  --source=name     Name of the source (for logging)");
  console.error("  --target=dir      Target skills directory (default: ./skills)");
  console.error("  --no-dry-run      Actually copy files (default is dry-run)");
  process.exit(1);
}

importSkills(sourceDir, targetDir, sourceName, dryRun);
