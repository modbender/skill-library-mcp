import { readdir, readFile, writeFile, rm, stat } from "node:fs/promises";
import { join, basename } from "node:path";
import { createHash } from "node:crypto";
import { stringify as yamlStringify, parse as parseYaml } from "yaml";
import { parseFrontmatter } from "../src/skill-index.js";

const CONCURRENCY = 64;

// ── Types ──────────────────────────────────────────────────────────────

type Issue =
  | "valid"
  | "no-frontmatter"
  | "broken-frontmatter"
  | "missing-description"
  | "missing-skillmd";

interface ScannedSkill {
  dirName: string;
  issue: Issue;
  content?: string; // raw SKILL.md content (undefined when missing-skillmd)
  name?: string;
  description?: string;
  contentHash?: string; // sha256(name.lower()::description.lower())
}

interface FixAction {
  dirName: string;
  action: "rewrite" | "delete";
  reason: string;
  newContent?: string; // for rewrite
}

// ── Helpers ────────────────────────────────────────────────────────────

async function parallel<T, R>(
  items: T[],
  concurrency: number,
  fn: (item: T) => Promise<R>,
): Promise<R[]> {
  const results: R[] = [];
  let index = 0;

  async function worker() {
    while (index < items.length) {
      const i = index++;
      results[i] = await fn(items[i]);
    }
  }

  await Promise.all(
    Array.from({ length: Math.min(concurrency, items.length) }, worker),
  );
  return results;
}

function contentHash(name: string, description: string): string {
  const key = `${name.toLowerCase().trim()}::${description.toLowerCase().trim()}`;
  return createHash("sha256").update(key).digest("hex");
}

/** Turn a dirName like "my-cool-skill" into "my cool skill" */
function dirNameToTitle(dirName: string): string {
  return dirName.replace(/[-_]+/g, " ").replace(/\s+/g, " ").trim();
}

/** Extract the first # heading from markdown body */
function extractHeading(body: string): string | null {
  const match = body.match(/^#\s+(.+)/m);
  return match ? match[1].trim() : null;
}

/**
 * Extract first meaningful paragraph from markdown body.
 * Skips headings, blank lines, tables, code blocks, and list items.
 */
function extractDescription(body: string): string {
  const lines = body.split("\n");
  let inCodeBlock = false;
  const paragraphLines: string[] = [];

  for (const line of lines) {
    if (line.trim().startsWith("```")) {
      inCodeBlock = !inCodeBlock;
      continue;
    }
    if (inCodeBlock) continue;

    const trimmed = line.trim();
    // Skip empty lines, headings, tables, list items, horizontal rules
    if (!trimmed) {
      if (paragraphLines.length > 0) break; // end of first paragraph
      continue;
    }
    if (/^#{1,6}\s/.test(trimmed)) {
      if (paragraphLines.length > 0) break;
      continue;
    }
    if (trimmed.startsWith("|") || trimmed.startsWith("-") || trimmed.startsWith("*") || trimmed.startsWith(">")) {
      if (paragraphLines.length > 0) break;
      continue;
    }

    paragraphLines.push(trimmed);
  }

  let desc = paragraphLines.join(" ");
  // Strip markdown formatting
  desc = desc
    .replace(/\[([^\]]+)\]\([^)]+\)/g, "$1") // links
    .replace(/[*_`~]+/g, "") // bold/italic/code
    .replace(/\s+/g, " ")
    .trim();

  if (desc.length > 200) {
    desc = desc.slice(0, 197) + "...";
  }
  return desc;
}

/** Build valid frontmatter + body content */
function buildSkillMd(
  name: string,
  description: string,
  body: string,
): string {
  const fm = yamlStringify({ name, description }).trim();
  return `---\n${fm}\n---\n${body}`;
}

/**
 * Regex-based extraction of name/description from YAML frontmatter lines.
 * Used as fallback when YAML parsing fails (e.g. unquoted colons in values).
 */
function extractFieldByRegex(
  yamlBlock: string,
  field: string,
): string | null {
  // Match field: "value" or field: 'value' (quoted)
  const quotedMatch = yamlBlock.match(
    new RegExp(`^${field}:\\s*["'](.+?)["']\\s*$`, "m"),
  );
  if (quotedMatch) return quotedMatch[1].trim();

  // Match field: value (unquoted, rest of line)
  const unquotedMatch = yamlBlock.match(
    new RegExp(`^${field}:\\s*(.+)$`, "m"),
  );
  if (unquotedMatch) return unquotedMatch[1].trim();

  return null;
}

/**
 * Try to extract name and description from raw YAML block that failed parsing,
 * handling common issues like numeric names, unquoted colons, missing fields.
 */
function extractFromBrokenYaml(
  yamlBlock: string,
  dirName: string,
  body: string,
): { name: string; description: string } | null {
  // First try normal YAML parsing
  let parsed: Record<string, unknown> | null = null;
  try {
    const result = parseYaml(yamlBlock);
    if (result && typeof result === "object") {
      parsed = result as Record<string, unknown>;
    }
  } catch {
    // YAML parse failed — fall through to regex extraction
  }

  let name: string | null = null;
  let description: string | null = null;

  if (parsed) {
    // YAML parsed but maybe name isn't a string (numeric) or description missing
    if (typeof parsed.name === "string" && parsed.name.trim()) {
      name = parsed.name.trim();
    } else if (parsed.name != null) {
      name = String(parsed.name);
    }

    if (typeof parsed.description === "string" && parsed.description.trim()) {
      description = parsed.description.trim();
    } else if (typeof parsed.summary === "string" && (parsed.summary as string).trim()) {
      description = (parsed.summary as string).trim();
    }
  }

  // Regex fallback for fields not extracted via YAML
  if (!name) {
    name = extractFieldByRegex(yamlBlock, "name") || dirName;
  }
  if (!description) {
    description =
      extractFieldByRegex(yamlBlock, "description") ||
      extractFieldByRegex(yamlBlock, "summary") ||
      extractDescription(body) ||
      dirNameToTitle(dirName);
  }

  if (!name || !description) return null;
  return { name, description };
}

// ── Phase 1: Scan ──────────────────────────────────────────────────────

async function scanSkill(
  skillsDir: string,
  dirName: string,
): Promise<ScannedSkill> {
  const skillMdPath = join(skillsDir, dirName, "SKILL.md");

  let content: string;
  try {
    content = await readFile(skillMdPath, "utf-8");
  } catch {
    return { dirName, issue: "missing-skillmd" };
  }

  const fm = parseFrontmatter(content);
  if (fm) {
    const hash = contentHash(fm.name, fm.description);
    if (!fm.description) {
      return {
        dirName,
        issue: "missing-description",
        content,
        name: fm.name,
        contentHash: hash,
      };
    }
    return {
      dirName,
      issue: "valid",
      content,
      name: fm.name,
      description: fm.description,
      contentHash: hash,
    };
  }

  // parseFrontmatter failed — determine why
  const hasFrontmatterBlock = /^---\r?\n/.test(content);
  if (!hasFrontmatterBlock) {
    return { dirName, issue: "no-frontmatter", content };
  }

  return { dirName, issue: "broken-frontmatter", content };
}

// ── Phase 2: Plan Fixes ────────────────────────────────────────────────

function planFixForNoFrontmatter(skill: ScannedSkill): FixAction | null {
  const body = skill.content!;
  const heading = extractHeading(body);
  const name = heading || skill.dirName;
  const description = extractDescription(body) || dirNameToTitle(skill.dirName);

  const newContent = buildSkillMd(name, description, body.startsWith("\n") ? body : "\n" + body);

  // Validate the fix produces valid output
  const check = parseFrontmatter(newContent);
  if (!check || !check.description) return null;

  return {
    dirName: skill.dirName,
    action: "rewrite",
    reason: "no-frontmatter: prepended generated frontmatter",
    newContent,
  };
}

function planFixForBrokenFrontmatter(skill: ScannedSkill): FixAction | null {
  const content = skill.content!;

  // Try closed frontmatter block first, then unclosed (opening --- but no closing ---)
  let yamlBlock: string;
  let body: string;
  const fmMatch = content.match(/^---\r?\n([\s\S]*?)\r?\n---/);
  if (fmMatch) {
    yamlBlock = fmMatch[1];
    body = content.slice(fmMatch[0].length);
  } else {
    // Unclosed frontmatter: take lines after opening --- until first blank line or # heading
    const lines = content.split(/\r?\n/);
    if (lines[0].replace(/\r$/, "") !== "---") return null;
    const yamlLines: string[] = [];
    let bodyStart = 1;
    for (let i = 1; i < lines.length; i++) {
      const trimmed = lines[i].replace(/\r$/, "").trim();
      if (!trimmed || trimmed.startsWith("#")) {
        bodyStart = i;
        break;
      }
      yamlLines.push(lines[i].replace(/\r$/, ""));
      bodyStart = i + 1;
    }
    if (yamlLines.length === 0) return null;
    yamlBlock = yamlLines.join("\n");
    body = "\n" + lines.slice(bodyStart).map(l => l.replace(/\r$/, "")).join("\n");
  }

  const extracted = extractFromBrokenYaml(yamlBlock, skill.dirName, body);
  if (!extracted) return null;

  const newContent = buildSkillMd(extracted.name, extracted.description, body);

  // Validate
  const check = parseFrontmatter(newContent);
  if (!check || !check.description) return null;

  return {
    dirName: skill.dirName,
    action: "rewrite",
    reason: `broken-frontmatter: rebuilt frontmatter (name="${extracted.name}")`,
    newContent,
  };
}

function planFixForMissingDescription(skill: ScannedSkill): FixAction | null {
  const content = skill.content!;
  const fmMatch = content.match(/^---\r?\n([\s\S]*?)\r?\n---/);
  if (!fmMatch) return null;

  const yamlBlock = fmMatch[1];
  const body = content.slice(fmMatch[0].length);

  let parsed: Record<string, unknown>;
  try {
    parsed = parseYaml(yamlBlock);
  } catch {
    return null;
  }

  const name = typeof parsed.name === "string" ? parsed.name : String(parsed.name ?? skill.dirName);

  // Try summary field, then extract from body
  let description = "";
  if (typeof parsed.summary === "string" && parsed.summary.trim()) {
    description = parsed.summary.trim();
  } else {
    description = extractDescription(body) || dirNameToTitle(skill.dirName);
  }

  if (!description) return null;

  const newContent = buildSkillMd(name, description, body);

  const check = parseFrontmatter(newContent);
  if (!check || !check.description) return null;

  return {
    dirName: skill.dirName,
    action: "rewrite",
    reason: `missing-description: added description "${description.slice(0, 60)}..."`,
    newContent,
  };
}

function planDuplicateRemovals(
  skills: ScannedSkill[],
): FixAction[] {
  // Group valid skills by content hash
  const hashGroups = new Map<string, ScannedSkill[]>();
  for (const skill of skills) {
    if (skill.issue !== "valid" || !skill.contentHash) continue;
    const group = hashGroups.get(skill.contentHash) ?? [];
    group.push(skill);
    hashGroups.set(skill.contentHash, group);
  }

  const actions: FixAction[] = [];
  for (const [, group] of hashGroups) {
    if (group.length < 2) continue;

    // Keep shortest dirName, alphabetical tiebreaker
    group.sort((a, b) => {
      if (a.dirName.length !== b.dirName.length)
        return a.dirName.length - b.dirName.length;
      return a.dirName.localeCompare(b.dirName);
    });

    const kept = group[0];
    for (let i = 1; i < group.length; i++) {
      actions.push({
        dirName: group[i].dirName,
        action: "delete",
        reason: `exact-duplicate: same as "${kept.dirName}"`,
      });
    }
  }

  return actions;
}

// ── Phase 3: Apply ─────────────────────────────────────────────────────

async function applyFix(
  skillsDir: string,
  fix: FixAction,
  dryRun: boolean,
): Promise<void> {
  if (fix.action === "delete") {
    if (!dryRun) {
      await rm(join(skillsDir, fix.dirName), { recursive: true, force: true });
    }
  } else if (fix.action === "rewrite" && fix.newContent) {
    if (!dryRun) {
      await writeFile(
        join(skillsDir, fix.dirName, "SKILL.md"),
        fix.newContent,
        "utf-8",
      );
    }
  }
}

// ── Main ───────────────────────────────────────────────────────────────

async function main() {
  const args = process.argv.slice(2);
  const skillsDir = args.find((a) => !a.startsWith("--")) || join(process.cwd(), "data");
  const dryRun = !args.includes("--no-dry-run");

  console.log(`\nFix broken skills in: ${skillsDir}`);
  console.log(`Mode: ${dryRun ? "DRY RUN" : "LIVE"}\n`);

  // ── Phase 1: Scan ──────────────────────────────────────────────────

  const t0 = Date.now();
  console.log("Phase 1: Scanning all skills...");

  let dirs: string[];
  try {
    const entries = await readdir(skillsDir);
    // Filter to directories only
    const dirChecks = await parallel(entries, CONCURRENCY, async (name) => {
      try {
        return (await stat(join(skillsDir, name))).isDirectory();
      } catch {
        return false;
      }
    });
    dirs = entries.filter((_, i) => dirChecks[i]);
  } catch (err) {
    console.error(`Failed to read skills directory: ${err}`);
    process.exit(1);
  }

  const skills = await parallel(dirs, CONCURRENCY, (dirName) =>
    scanSkill(skillsDir, dirName),
  );

  const counts = { valid: 0, "no-frontmatter": 0, "broken-frontmatter": 0, "missing-description": 0, "missing-skillmd": 0 };
  for (const skill of skills) {
    counts[skill.issue]++;
  }

  console.log(`  Total directories: ${dirs.length}`);
  console.log(`  Valid:             ${counts.valid}`);
  console.log(`  No frontmatter:    ${counts["no-frontmatter"]}`);
  console.log(`  Broken frontmatter:${counts["broken-frontmatter"]}`);
  console.log(`  Missing description:${counts["missing-description"]}`);
  console.log(`  Missing SKILL.md:  ${counts["missing-skillmd"]}`);
  console.log(`  Scanned in ${((Date.now() - t0) / 1000).toFixed(1)}s\n`);

  // ── Phase 2: Plan fixes ────────────────────────────────────────────

  const t1 = Date.now();
  console.log("Phase 2: Planning fixes...");

  const fixes: FixAction[] = [];
  let unfixable = 0;

  for (const skill of skills) {
    let fix: FixAction | null = null;

    switch (skill.issue) {
      case "valid":
        break; // handled in duplicate pass
      case "missing-skillmd":
        fix = {
          dirName: skill.dirName,
          action: "delete",
          reason: "missing-skillmd: no SKILL.md found",
        };
        break;
      case "no-frontmatter":
        fix = planFixForNoFrontmatter(skill);
        break;
      case "broken-frontmatter":
        fix = planFixForBrokenFrontmatter(skill);
        break;
      case "missing-description":
        fix = planFixForMissingDescription(skill);
        break;
    }

    if (fix) {
      fixes.push(fix);
    } else if (skill.issue !== "valid") {
      unfixable++;
      console.log(`  UNFIXABLE: ${skill.dirName} (${skill.issue})`);
    }
  }

  // Duplicate removal
  const dupFixes = planDuplicateRemovals(skills);
  fixes.push(...dupFixes);

  const rewrites = fixes.filter((f) => f.action === "rewrite").length;
  const deletes = fixes.filter((f) => f.action === "delete").length;

  console.log(`  Planned rewrites: ${rewrites}`);
  console.log(`  Planned deletes:  ${deletes}`);
  console.log(`  Unfixable:        ${unfixable}`);
  console.log(`  Planned in ${((Date.now() - t1) / 1000).toFixed(1)}s\n`);

  // ── Phase 3: Apply ────────────────────────────────────────────────

  const t2 = Date.now();
  console.log(`Phase 3: ${dryRun ? "Previewing" : "Applying"} fixes...`);

  // Log all actions
  for (const fix of fixes) {
    const prefix = fix.action === "delete" ? "DELETE" : "REWRITE";
    console.log(`  ${prefix} ${fix.dirName} — ${fix.reason}`);
  }

  if (!dryRun) {
    await parallel(fixes, CONCURRENCY, (fix) => applyFix(skillsDir, fix, false));
  }

  console.log(`  ${dryRun ? "Previewed" : "Applied"} in ${((Date.now() - t2) / 1000).toFixed(1)}s\n`);

  // ── Summary ────────────────────────────────────────────────────────

  const totalTime = ((Date.now() - t0) / 1000).toFixed(1);
  console.log(`${"=".repeat(50)}`);
  console.log(`Results (${totalTime}s):`);
  console.log(`  Skills scanned:    ${dirs.length}`);
  console.log(`  Already valid:     ${counts.valid - dupFixes.length}`);
  console.log(`  Rewrites:          ${rewrites}`);
  console.log(`  Deletes:           ${deletes} (${dupFixes.length} dupes + ${deletes - dupFixes.length} missing)`);
  console.log(`  Unfixable:         ${unfixable}`);
  console.log(`${"=".repeat(50)}`);

  if (dryRun) {
    console.log(`\nThis was a dry run. Re-run with --no-dry-run to apply changes.`);
  }
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
