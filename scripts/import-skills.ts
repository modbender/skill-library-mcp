import { readdir, access, cp } from "node:fs/promises";
import { join, basename } from "node:path";
import { findDuplicates } from "../src/dedup.js";

async function hasSkillMd(dir: string): Promise<boolean> {
  try {
    await access(join(dir, "SKILL.md"));
    return true;
  } catch {
    return false;
  }
}

async function getExistingSkillDirs(skillsDir: string): Promise<Set<string>> {
  const dirs = await readdir(skillsDir);
  return new Set(dirs);
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

  const existing = await getExistingSkillDirs(targetDir);
  let sourceDirs: string[];

  try {
    sourceDirs = await readdir(sourceDir);
  } catch (err) {
    console.error(`Failed to read source directory: ${err}`);
    process.exit(1);
  }

  let added = 0;
  let skipped = 0;
  const conflicts: string[] = [];

  for (const dirName of sourceDirs) {
    const srcPath = join(sourceDir, dirName);
    if (!(await hasSkillMd(srcPath))) continue;

    if (existing.has(dirName)) {
      conflicts.push(dirName);
      skipped++;
      continue;
    }

    if (!dryRun) {
      await cp(srcPath, join(targetDir, dirName), { recursive: true });
    }
    console.log(`  + ${dirName}`);
    added++;
  }

  console.log(`\nResults:`);
  console.log(`  Added: ${added}`);
  console.log(`  Skipped (already exists): ${skipped}`);

  if (conflicts.length > 0) {
    console.log(`\nConflicts (skipped):`);
    for (const c of conflicts) {
      console.log(`  - ${c}`);
    }
  }

  // Run dedup check
  if (!dryRun && added > 0) {
    console.log(`\nRunning dedup check...`);
    const report = await findDuplicates(targetDir);
    if (report.exactDuplicates.length > 0) {
      console.log(`\n❌ ${report.exactDuplicates.length} exact duplicate group(s) created:`);
      for (const group of report.exactDuplicates) {
        console.log(`  "${group[0].name}": ${group.map((s) => s.dirName).join(", ")}`);
      }
    } else {
      console.log(`✅ No new exact duplicates.`);
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
