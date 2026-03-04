import { readdir, readFile, stat } from "node:fs/promises";
import { join } from "node:path";
import { parseFrontmatter } from "../src/skill-index.js";

const SKILLS_DIR = process.argv[2] || join(process.cwd(), "skills");

interface Violation {
  skill: string;
  issue: string;
}

async function isDirectory(path: string): Promise<boolean> {
  try {
    return (await stat(path)).isDirectory();
  } catch {
    return false;
  }
}

async function validateSkill(skillPath: string, name: string): Promise<Violation[]> {
  const violations: Violation[] = [];

  // Must have SKILL.md
  let skillMdPath = join(skillPath, "SKILL.md");
  try {
    await stat(skillMdPath);
  } catch {
    violations.push({ skill: name, issue: "missing SKILL.md" });
    return violations;
  }

  // SKILL.md must have valid frontmatter with name and description
  try {
    const content = await readFile(skillMdPath, "utf-8");
    const fm = parseFrontmatter(content);
    if (!fm) {
      violations.push({ skill: name, issue: "SKILL.md has no valid YAML frontmatter" });
    } else {
      if (!fm.name) violations.push({ skill: name, issue: "frontmatter missing 'name'" });
      if (!fm.description) violations.push({ skill: name, issue: "frontmatter missing 'description'" });
    }
  } catch (err) {
    violations.push({ skill: name, issue: `cannot read SKILL.md: ${err}` });
  }

  return violations;
}

async function main() {
  const entries = await readdir(SKILLS_DIR);
  const allViolations: Violation[] = [];
  let skillCount = 0;

  for (const name of entries) {
    const skillPath = join(SKILLS_DIR, name);
    if (!(await isDirectory(skillPath))) continue;
    skillCount++;

    const violations = await validateSkill(skillPath, name);
    allViolations.push(...violations);
  }

  if (allViolations.length === 0) {
    console.log(`✅ All ${skillCount} skills are valid.`);
    process.exit(0);
  }

  // Group by skill
  const grouped = new Map<string, string[]>();
  for (const v of allViolations) {
    const issues = grouped.get(v.skill) ?? [];
    issues.push(v.issue);
    grouped.set(v.skill, issues);
  }

  console.log(`❌ ${grouped.size} skill(s) with ${allViolations.length} violation(s):\n`);
  for (const [skill, issues] of grouped) {
    console.log(`  ${skill}:`);
    for (const issue of issues) {
      console.log(`    - ${issue}`);
    }
  }

  process.exit(1);
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
