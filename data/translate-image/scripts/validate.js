#!/usr/bin/env node
/**
 * validate.js — Validates SKILL.md against ClawHub publishing requirements.
 *
 * Rules enforced:
 *   - Frontmatter block (--- ... ---) must be present
 *   - Required fields: name, version, description, tags
 *   - name must be lowercase letters, numbers, and hyphens only
 *   - version must be valid semver (MAJOR.MINOR.PATCH)
 *   - description must be a non-empty string
 *   - tags must be a non-empty array
 *   - metadata.openclaw.requires.env must list at least one env var
 *   - Body content must be present and substantive (> 200 chars)
 */

import { readFileSync, existsSync } from "fs";
import { join, dirname } from "path";
import { fileURLToPath } from "url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const skillPath = join(__dirname, "..", "SKILL.md");

// ── Helpers ──────────────────────────────────────────────────────────────────

function pass(msg) {
  console.log(`  ✅ ${msg}`);
}

function warn(msg) {
  console.warn(`  ⚠️  ${msg}`);
}

function fail(msg) {
  console.error(`  ❌ ${msg}`);
  process.exitCode = 1;
}

function extract(frontmatter, key) {
  const match = frontmatter.match(new RegExp(`^${key}:\\s*"?([^"\\n]+)"?`, "m"));
  return match ? match[1].trim() : null;
}

// ── Read file ─────────────────────────────────────────────────────────────────

if (!existsSync(skillPath)) {
  console.error("❌ SKILL.md not found at:", skillPath);
  process.exit(1);
}

const raw = readFileSync(skillPath, "utf-8");
console.log("\n🔍 Validating SKILL.md...\n");

// ── Parse frontmatter ─────────────────────────────────────────────────────────

const fmMatch = raw.match(/^---\r?\n([\s\S]+?)\r?\n---/);
if (!fmMatch) {
  fail("Missing YAML frontmatter block (--- ... ---)");
  process.exit(1);
}

const frontmatter = fmMatch[1];
const body = raw.slice(fmMatch[0].length).trim();

// ── Required string fields ────────────────────────────────────────────────────

const name = extract(frontmatter, "name");
if (!name) {
  fail('Missing required field: name (e.g. name: "my-skill")');
} else if (!/^[a-z0-9][a-z0-9-]*[a-z0-9]$/.test(name)) {
  fail(`name "${name}" must be lowercase letters, numbers, and hyphens only`);
} else {
  pass(`name: ${name}`);
}

const version = extract(frontmatter, "version");
if (!version) {
  fail('Missing required field: version (e.g. version: "1.0.0")');
} else if (!/^\d+\.\d+\.\d+/.test(version)) {
  fail(`version "${version}" must be semver format (e.g. 1.0.0)`);
} else {
  pass(`version: ${version}`);
}

const description = extract(frontmatter, "description");
if (!description) {
  fail("Missing required field: description");
} else if (description.length < 20) {
  fail(`description is too short (${description.length} chars) — be more descriptive`);
} else {
  pass(`description: ${description.slice(0, 60)}${description.length > 60 ? "…" : ""}`);
}

// ── tags ──────────────────────────────────────────────────────────────────────

const tagsMatch = frontmatter.match(/^tags:\s*\[([^\]]+)\]/m);
if (!tagsMatch) {
  fail('Missing required field: tags (e.g. tags: ["image", "translation"])');
} else {
  const tags = tagsMatch[1]
    .split(",")
    .map((t) => t.trim().replace(/^"|"$/g, "").trim())
    .filter(Boolean);
  if (tags.length === 0) {
    fail("tags array must not be empty");
  } else {
    pass(`tags: [${tags.join(", ")}]`);
  }
}

// ── metadata ──────────────────────────────────────────────────────────────────

if (!frontmatter.includes("metadata:")) {
  warn("No metadata section — consider declaring env requirements for user clarity");
} else if (!frontmatter.includes("primaryEnv:")) {
  warn("metadata.openclaw.primaryEnv not set — recommended for ClawHub UI display");
} else {
  const primaryEnvMatch = frontmatter.match(/primaryEnv:\s*(\S+)/);
  if (primaryEnvMatch) {
    pass(`metadata.primaryEnv: ${primaryEnvMatch[1]}`);
  }
}

if (frontmatter.includes("requires:") && frontmatter.includes("env:")) {
  const envBlockMatch = frontmatter.match(/env:\s*\n((?:\s+-\s+\S+\n?)+)/);
  const envVars = envBlockMatch
    ? envBlockMatch[1].match(/- (\S+)/g)?.map((e) => e.replace("- ", "")) ?? []
    : [];
  if (envVars.length === 0) {
    warn("requires.env is declared but lists no env vars");
  } else {
    pass(`requires.env: [${envVars.join(", ")}]`);
  }
}

// ── bins vs body cross-check ──────────────────────────────────────────────────

const binsBlockMatch = frontmatter.match(/bins:\s*\n((?:\s+-\s+\S+\n?)+)/);
const declaredBins = binsBlockMatch
  ? binsBlockMatch[1].match(/- (\S+)/g)?.map((b) => b.replace("- ", "")) ?? []
  : [];

if (declaredBins.length > 0) {
  pass(`requires.bins: [${declaredBins.join(", ")}]`);
}

// Warn if body uses a tool not declared in bins
const commonBins = ["python3", "python", "jq", "node", "npx", "git", "ffmpeg", "magick", "convert"];
for (const bin of commonBins) {
  const usedInBody = new RegExp(`\\b${bin}\\b`).test(body);
  const declared = declaredBins.includes(bin);
  if (usedInBody && !declared) {
    warn(`body uses "${bin}" but it is not listed in requires.bins`);
  }
}

// ── Body content ──────────────────────────────────────────────────────────────

if (body.length === 0) {
  fail("SKILL.md body is empty — add usage instructions for the AI agent");
} else if (body.length < 200) {
  fail(`SKILL.md body is too short (${body.length} chars) — needs substantive instructions`);
} else {
  pass(`body: ${body.length.toLocaleString()} chars`);
}

// Check for at least one tool section
if (!body.includes("###") && !body.includes("##")) {
  warn("No tool sections found in body — consider structuring with ## or ### headings");
} else {
  const toolSections = (body.match(/^#{2,3}\s+`?\w/gm) ?? []).length;
  pass(`sections: ${toolSections} headings`);
}

// ── Summary ───────────────────────────────────────────────────────────────────

console.log();
if (process.exitCode === 1) {
  console.error("❌ Validation failed — fix errors above before publishing\n");
  process.exit(1);
} else {
  console.log(`✅ SKILL.md is valid and ready to publish\n`);
  console.log(`   Run "pnpm publish:skill" to push to ClawHub\n`);
}
