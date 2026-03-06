import { readMd } from './io.js';

/**
 * Check if a file's data is stale based on its TTL frontmatter field.
 * @param {string} filePath - Path to the .md file
 * @returns {boolean} True if stale or unreadable
 */
export function isStale(filePath) {
  try {
    const { meta } = readMd(filePath);
    if (!meta.ttl || !meta.updated) return false;
    const updatedMs = new Date(meta.updated).getTime();
    const ttlMs = meta.ttl * 1000;
    return Date.now() > updatedMs + ttlMs;
  } catch {
    return true;
  }
}
