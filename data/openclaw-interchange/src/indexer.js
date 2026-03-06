import fs from 'node:fs';
import path from 'node:path';
import { atomicWrite, readMd } from './io.js';
import { acquireLock, releaseLock } from './lock.js';
import { serializeFrontmatter, serializeTable } from './serialize.js';
import { contentHash } from './generation.js';

const INTERCHANGE_ROOT = path.resolve(process.env.INTERCHANGE_ROOT || path.join(process.env.HOME || '/tmp', '.openclaw', 'workspace', 'interchange'));

/**
 * Update the _index.md for a skill atomically.
 * @param {string} skillName
 * @param {{ path: string, type: string, layer: string, updated: string }[]} files
 */
export async function updateIndex(skillName, files) {
  const headers = ['File', 'Type', 'Layer', 'Updated'];
  const rows = files
    .sort((a, b) => a.path.localeCompare(b.path))
    .map(f => [f.path, f.type, f.layer, f.updated]);
  const table = serializeTable(headers, rows);
  const content = `# ${skillName} Index\n\n${table}\n`;
  const hash = contentHash(content);

  const indexPath = path.join(INTERCHANGE_ROOT, skillName, '_index.md');
  const lock = await acquireLock(indexPath);
  try {
    let gen = 1;
    try {
      const existing = readMd(indexPath);
      gen = (existing.meta.generation_id || 0);
      if (existing.meta.content_hash === hash) return; // idempotent
      gen++;
    } catch {}

    const meta = {
      skill: skillName,
      type: 'summary',
      layer: 'ops',
      updated: new Date().toISOString(),
      version: 1,
      generation_id: gen,
      content_hash: hash,
      generator: '@openclaw/interchange',
      tags: ['index'],
    };

    const yamlStr = serializeFrontmatter(meta);
    const data = `---\n${yamlStr}\n---\n${content}`;
    atomicWrite(indexPath, data);
  } finally {
    releaseLock(lock);
  }
}

/**
 * List interchange files, optionally filtered by skill and/or layer.
 * @param {string} [skill] - Filter by skill name
 * @param {'ops'|'state'} [layer] - Filter by layer
 * @returns {string[]} Array of file paths
 */
export function listInterchange(skill, layer) {
  const root = skill ? path.join(INTERCHANGE_ROOT, skill) : INTERCHANGE_ROOT;
  if (!fs.existsSync(root)) return [];
  return walkDir(root).filter(f => {
    if (!f.endsWith('.md')) return false;
    if (layer) {
      const normalized = f.replace(/\\/g, '/');
      if (!normalized.includes(`/${layer}/`)) return false;
    }
    return true;
  });
}

/**
 * Rebuild the master _index.md from disk scan.
 * @param {string} [skill] - If provided, only rebuild that skill's index
 */
export function rebuildIndex(skill) {
  const skills = skill
    ? [skill]
    : fs.existsSync(INTERCHANGE_ROOT)
      ? fs.readdirSync(INTERCHANGE_ROOT, { withFileTypes: true })
          .filter(d => d.isDirectory())
          .map(d => d.name)
      : [];

  for (const s of skills) {
    const files = listInterchange(s).map(f => {
      try {
        const { meta } = readMd(f);
        return { path: path.relative(INTERCHANGE_ROOT, f), type: meta.type || 'unknown', layer: meta.layer || 'unknown', updated: meta.updated || 'unknown' };
      } catch {
        return { path: path.relative(INTERCHANGE_ROOT, f), type: 'unknown', layer: 'unknown', updated: 'unknown' };
      }
    });
    if (files.length > 0) updateIndex(s, files);
  }

  // Master index
  if (!skill) {
    const allSkills = skills.filter(s => fs.existsSync(path.join(INTERCHANGE_ROOT, s, '_index.md')));
    const headers = ['Skill', 'Files', 'Last Updated'];
    const rows = allSkills.sort().map(s => {
      const count = listInterchange(s).length;
      let lastUpdated = 'unknown';
      try {
        const { meta } = readMd(path.join(INTERCHANGE_ROOT, s, '_index.md'));
        lastUpdated = meta.updated || 'unknown';
      } catch {}
      return [s, String(count), lastUpdated];
    });
    const table = serializeTable(headers, rows);
    const content = `# Interchange Master Index\n\n${table}\n`;
    const hash = contentHash(content);

    const masterPath = path.join(INTERCHANGE_ROOT, '_index.md');
    let gen = 1;
    try {
      const existing = readMd(masterPath);
      gen = (existing.meta.generation_id || 0);
      if (existing.meta.content_hash === hash) return;
      gen++;
    } catch {}

    const meta = {
      skill: '_master',
      type: 'summary',
      layer: 'ops',
      updated: new Date().toISOString(),
      version: 1,
      generation_id: gen,
      content_hash: hash,
      generator: '@openclaw/interchange',
      tags: ['index', 'master'],
    };
    const yamlStr = serializeFrontmatter(meta);
    const data = `---\n${yamlStr}\n---\n${content}`;
    atomicWrite(masterPath, data);
  }
}

/**
 * Recursively walk a directory.
 * @param {string} dir
 * @returns {string[]}
 */
function walkDir(dir) {
  const results = [];
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) results.push(...walkDir(full));
    else results.push(full);
  }
  return results;
}
