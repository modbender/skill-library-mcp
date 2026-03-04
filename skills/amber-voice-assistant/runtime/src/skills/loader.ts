/**
 * Amber Skills — Loader
 * 
 * Scans amber-skills/ directory at startup, parses SKILL.md frontmatter,
 * loads handler.js for each valid skill.
 */

import * as fs from 'fs';
import * as path from 'path';
import { createRequire } from 'module';
import { AmberSkillManifest, AmberSkillConfig, LoadedSkill, SkillHandler } from './types.js';

const require = createRequire(import.meta.url);

/**
 * Parse YAML-ish frontmatter from a SKILL.md file.
 * Handles the OpenClaw pattern: simple YAML fields + inline JSON for metadata.
 */
function parseFrontmatter(content: string): Record<string, any> {
  const match = content.match(/^---\s*\n([\s\S]*?)\n---/);
  if (!match) return {};

  const yaml = match[1];
  const result: Record<string, any> = {};

  // Parse line by line — handles simple key: value and key: {json}
  for (const line of yaml.split('\n')) {
    const kvMatch = line.match(/^(\w[\w-]*)\s*:\s*(.+)$/);
    if (!kvMatch) continue;

    const key = kvMatch[1].trim();
    let value: any = kvMatch[2].trim();

    // Strip surrounding quotes
    if ((value.startsWith('"') && value.endsWith('"')) || (value.startsWith("'") && value.endsWith("'"))) {
      value = value.slice(1, -1);
    }

    // Try to parse as JSON (for metadata field)
    if (value.startsWith('{') || value.startsWith('[')) {
      try {
        value = JSON.parse(value);
      } catch {
        // keep as string
      }
    }

    result[key] = value;
  }

  return result;
}

/**
 * Validate that a parsed manifest has all required Amber skill fields.
 */
function validateManifest(data: Record<string, any>, skillDir: string): AmberSkillManifest | null {
  const name = data.name;
  const version = data.version || '0.0.0';
  const description = data.description || '';

  // Extract amber config from metadata
  const metadata = data.metadata;
  if (!metadata || !metadata.amber) {
    console.warn(`[skills] Skipping ${skillDir}: no metadata.amber in SKILL.md`);
    return null;
  }

  const amber: AmberSkillConfig = metadata.amber;

  if (!amber.function_schema || !amber.function_schema.name) {
    console.warn(`[skills] Skipping ${skillDir}: missing function_schema.name`);
    return null;
  }

  if (!amber.capabilities || !Array.isArray(amber.capabilities)) {
    console.warn(`[skills] Skipping ${skillDir}: missing capabilities array`);
    return null;
  }

  // Defaults
  if (typeof amber.timeout_ms !== 'number') amber.timeout_ms = 5000;
  if (typeof amber.confirmation_required !== 'boolean') amber.confirmation_required = false;
  if (!amber.permissions) amber.permissions = {};

  return { name, version, description, amber };
}

/**
 * Load the approved skill list from SKILL_MANIFEST.json.
 *
 * SECURITY: This function MUST be called before any handler.js is loaded.
 * The returned Set is used as an explicit allowlist — only skill directories
 * whose names appear in approvedSkills will have their handler.js required().
 * Any directory in amber-skills/ that is NOT in this allowlist is skipped
 * unconditionally, even if it has a valid SKILL.md and handler.js.
 *
 * To add a new skill: add its directory name to the approvedSkills array
 * in amber-skills/SKILL_MANIFEST.json and restart the runtime.
 */
function loadApprovedSkills(skillsDir: string): Set<string> {
  const manifestPath = path.join(skillsDir, 'SKILL_MANIFEST.json');
  if (!fs.existsSync(manifestPath)) {
    console.warn('[skills] No SKILL_MANIFEST.json found — no skills will be loaded');
    return new Set();
  }
  try {
    const raw = fs.readFileSync(manifestPath, 'utf8');
    const data = JSON.parse(raw);
    const approved: string[] = Array.isArray(data.approvedSkills) ? data.approvedSkills : [];
    console.log(`[skills] Approved skill allowlist: [${approved.join(', ')}]`);
    return new Set(approved);
  } catch (e) {
    console.error('[skills] Failed to parse SKILL_MANIFEST.json — no skills loaded:', e);
    return new Set();
  }
}

/**
 * Load all skills from the amber-skills/ directory.
 * Only skills listed in amber-skills/SKILL_MANIFEST.json are loaded.
 * Returns array of loaded skills ready for registration.
 */
export function loadSkills(skillsDir: string): LoadedSkill[] {
  const loaded: LoadedSkill[] = [];

  if (!fs.existsSync(skillsDir)) {
    console.log(`[skills] Skills directory not found: ${skillsDir} — no skills loaded`);
    return loaded;
  }

  // Enforce allowlist — only load skills explicitly approved in SKILL_MANIFEST.json
  const approvedSkills = loadApprovedSkills(skillsDir);
  if (approvedSkills.size === 0) return loaded;

  const entries = fs.readdirSync(skillsDir, { withFileTypes: true });

  for (const entry of entries) {
    if (!entry.isDirectory()) continue;

    // Skip any skill not in the approved allowlist
    if (!approvedSkills.has(entry.name)) {
      console.log(`[skills] Skipping ${entry.name}: not in SKILL_MANIFEST.json allowlist`);
      continue;
    }

    const skillDir = path.join(skillsDir, entry.name);
    const skillMd = path.join(skillDir, 'SKILL.md');
    const handlerJs = path.join(skillDir, 'handler.js');

    // Check required files exist
    if (!fs.existsSync(skillMd)) {
      console.warn(`[skills] Skipping ${entry.name}: no SKILL.md`);
      continue;
    }
    if (!fs.existsSync(handlerJs)) {
      console.warn(`[skills] Skipping ${entry.name}: no handler.js`);
      continue;
    }

    try {
      // Parse SKILL.md
      const content = fs.readFileSync(skillMd, 'utf8');
      const data = parseFrontmatter(content);
      const manifest = validateManifest(data, entry.name);

      if (!manifest) continue;

      // Load handler — only reaches here if skill is in the approved allowlist
      // eslint-disable-next-line @typescript-eslint/no-var-requires
      const handler: SkillHandler = require(handlerJs);

      if (typeof handler !== 'function') {
        console.warn(`[skills] Skipping ${entry.name}: handler.js does not export a function`);
        continue;
      }

      loaded.push({ manifest, handler, path: skillDir });
      console.log(`[skills] Loaded: ${manifest.name} v${manifest.version} [${manifest.amber.capabilities.join('+')}] → ${manifest.amber.function_schema.name}()`);

    } catch (e) {
      console.error(`[skills] Error loading ${entry.name}:`, e);
    }
  }

  console.log(`[skills] ${loaded.length} skill(s) loaded from ${skillsDir}`);
  return loaded;
}
