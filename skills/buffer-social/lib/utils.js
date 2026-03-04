import { existsSync } from 'node:fs';
import { resolve } from 'node:path';

import { MAX_POST_TEXT_LENGTH } from './constants.js';

/**
 * Validate and normalize post text.
 * @param {string} text
 * @returns {string}
 */
export function validatePostText(text) {
  const normalized = (text || '').trim();

  if (!normalized) {
    throw new Error('Post text is required. Provide text like: buffer post "Hello world"');
  }

  if (normalized.length > MAX_POST_TEXT_LENGTH) {
    throw new Error(`Post text must be ${MAX_POST_TEXT_LENGTH} characters or less.`);
  }

  return normalized;
}

/**
 * Parse and validate schedule time.
 * @param {string | undefined} time
 * @returns {string | null}
 */
export function parseScheduleTime(time) {
  if (!time) {
    return null;
  }

  const parsed = new Date(time);
  if (Number.isNaN(parsed.getTime())) {
    throw new Error('Invalid schedule time. Use ISO 8601 format, e.g. 2026-03-03T14:00:00Z');
  }

  return parsed.toISOString();
}

/**
 * Parse profile IDs from comma-separated option.
 * @param {string | undefined} profiles
 * @returns {string[]}
 */
export function parseProfilesList(profiles) {
  if (!profiles) {
    return [];
  }

  const items = profiles
    .split(',')
    .map((item) => item.trim())
    .filter(Boolean);

  if (!items.length) {
    throw new Error(
      'No valid profile IDs found in --profiles. Example: --profiles twitter,linkedin'
    );
  }

  return items;
}

/**
 * Validate image file path when attaching media.
 * @param {string | undefined} imagePath
 * @returns {string | null}
 */
export function validateImagePath(imagePath) {
  if (!imagePath) {
    return null;
  }

  const resolvedPath = resolve(imagePath);
  if (!existsSync(resolvedPath)) {
    throw new Error(`Image file not found: ${imagePath}. Check the path and try again.`);
  }

  return resolvedPath;
}

/**
 * Validate post command option combinations.
 * @param {{profile?: string, profiles?: string, all?: boolean, queue?: boolean, time?: string}} options
 */
export function validatePostOptions(options) {
  const selected = [
    Boolean(options.profile),
    Boolean(options.profiles),
    Boolean(options.all),
  ].filter(Boolean).length;
  if (selected > 1) {
    throw new Error('Choose only one target option: --profile, --profiles, or --all.');
  }

  if (options.queue && options.time) {
    throw new Error('Cannot use --queue and --time together. Use one scheduling mode.');
  }
}

/**
 * Parse a positive integer limit option.
 * @param {string | number | undefined} value
 * @param {string} optionName
 * @returns {number}
 */
export function parseLimit(value, optionName = '--limit') {
  const parsed = Number.parseInt(String(value), 10);
  if (Number.isNaN(parsed) || parsed <= 0) {
    throw new Error(`Invalid ${optionName} value. Use a positive integer, e.g. ${optionName} 10`);
  }

  return parsed;
}

export { MAX_POST_TEXT_LENGTH };
