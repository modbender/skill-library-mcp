import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import yaml from 'js-yaml';
import { acquireLock, releaseLock } from './lock.js';
import { serializeFrontmatter } from './serialize.js';
import { contentHash } from './generation.js';
import { validateFrontmatter } from './validate.js';

/**
 * Atomic write: write to tmp file, fsync, rename to target.
 * @param {string} filePath - Target file path
 * @param {string} data - File content
 */
export function atomicWrite(filePath, data) {
  fs.mkdirSync(path.dirname(filePath), { recursive: true });
  const tmp = `${filePath}.tmp.${process.pid}.${Date.now()}`;
  const fd = fs.openSync(tmp, 'w');
  try {
    fs.writeSync(fd, data);
    fs.fsyncSync(fd);
    fs.closeSync(fd);
    fs.renameSync(tmp, filePath);
  } catch (err) {
    try { fs.closeSync(fd); } catch {}
    try { fs.unlinkSync(tmp); } catch {}
    throw err;
  }
}

/**
 * Read and parse a .md file with YAML frontmatter.
 * @param {string} filePath - Path to the .md file
 * @returns {{ meta: Record<string, any>, content: string, raw: string }}
 */
export function readMd(filePath) {
  const raw = fs.readFileSync(filePath, 'utf8');
  // Normalize CRLF → LF for cross-platform safety
  const normalized = raw.replace(/\r\n/g, '\n');
  const match = normalized.match(/^---[ \t]*\n([\s\S]*?)\n---[ \t]*\n?([\s\S]*)$/);
  if (!match) {
    return { meta: {}, content: normalized, raw };
  }
  const meta = yaml.load(match[1]) || {};
  const content = match[2];
  return { meta, content, raw };
}

/**
 * Write a .md file atomically with frontmatter.
 * Handles locking, generation_id auto-increment, and content_hash.
 *
 * If content hasn't changed (same content_hash), the file is NOT rewritten
 * and generation_id stays the same (idempotency contract).
 *
 * @param {string} filePath - Target file path
 * @param {Record<string, any>} frontmatter - Frontmatter fields
 * @param {string} content - Markdown body content
 * @param {{ force?: boolean, skipValidation?: boolean }} [opts] - Options; force=true skips idempotency check, skipValidation=true skips frontmatter validation
 */
export async function writeMd(filePath, frontmatter, content, opts = {}) {
  const lock = await acquireLock(filePath);
  try {
    const hash = contentHash(content);

    // Read existing file for idempotency check
    let currentGen = 0;
    try {
      const existing = readMd(filePath);
      currentGen = existing.meta.generation_id || 0;
      if (!opts.force && existing.meta.content_hash === hash) {
        return; // No change — idempotent skip
      }
    } catch {
      // File doesn't exist yet
    }

    const meta = {
      ...frontmatter,
      content_hash: hash,
      generation_id: currentGen + 1,
      updated: new Date().toISOString(),
    };

    // Validate frontmatter unless explicitly skipped (e.g., internal/test use)
    if (!opts.skipValidation) {
      const validation = validateFrontmatter(meta);
      if (!validation.valid) {
        throw new Error(`Invalid frontmatter: ${validation.errors.join('; ')}`);
      }
    }

    const yamlStr = serializeFrontmatter(meta);
    const data = `---\n${yamlStr}\n---\n${content}`;
    atomicWrite(filePath, data);
  } finally {
    releaseLock(lock);
  }
}
