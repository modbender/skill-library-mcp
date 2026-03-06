import { readdir, rm, stat } from "node:fs/promises";
import { join } from "node:path";

const SKILLS_DIR = process.argv[2] || join(process.cwd(), "data");
const DRY_RUN = !process.argv.includes("--no-dry-run");

async function isDirectory(path: string): Promise<boolean> {
  try {
    return (await stat(path)).isDirectory();
  } catch {
    return false;
  }
}

async function hasSkillMd(skillPath: string): Promise<boolean> {
  try {
    await stat(join(skillPath, "SKILL.md"));
    return true;
  } catch {
    return false;
  }
}

async function main() {
  console.log(`\nCleaning skills in: ${SKILLS_DIR}`);
  console.log(`Mode: ${DRY_RUN ? "DRY RUN" : "LIVE"}\n`);

  const entries = await readdir(SKILLS_DIR);
  let totalRemoved = 0;
  let totalValid = 0;

  for (const name of entries) {
    const skillPath = join(SKILLS_DIR, name);
    if (!(await isDirectory(skillPath))) continue;

    if (!(await hasSkillMd(skillPath))) {
      console.log(`  REMOVE ${name} (no SKILL.md)`);
      if (!DRY_RUN) await rm(skillPath, { recursive: true, force: true });
      totalRemoved++;
    } else {
      totalValid++;
    }
  }

  console.log(`\n${"=".repeat(50)}`);
  console.log(`Results:`);
  console.log(`  Valid skills:           ${totalValid}`);
  console.log(`  Removed (no SKILL.md):  ${totalRemoved}`);
  console.log(`${"=".repeat(50)}`);

  if (DRY_RUN) {
    console.log(`\nThis was a dry run. Re-run with --no-dry-run to apply changes.`);
  }
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
