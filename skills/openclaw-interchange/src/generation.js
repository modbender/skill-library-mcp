import crypto from 'node:crypto';
import { readMd } from './io.js';

/**
 * Compute SHA-256 hash of content body.
 * @param {string} content - Content to hash
 * @returns {string} Hash prefixed with "sha256:"
 */
export function contentHash(content) {
  const hash = crypto.createHash('sha256').update(content, 'utf8').digest('hex');
  return `sha256:${hash}`;
}

/**
 * Read the current generation_id from an existing file and return the next one.
 * If file doesn't exist, returns 1.
 * @param {string} filePath - Path to the .md file
 * @returns {number} Next generation ID
 */
export function nextGenerationId(filePath) {
  try {
    const { meta } = readMd(filePath);
    return (meta.generation_id || 0) + 1;
  } catch {
    return 1;
  }
}
