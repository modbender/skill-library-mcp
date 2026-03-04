/**
 * Convert a name to a URL/filesystem-safe slug.
 * @param {string} name
 * @returns {string}
 */
export function slugify(name) {
  return String(name)
    .toLowerCase()
    .trim()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-|-$/g, '');
}

/**
 * Format a markdown table. Re-exports serializeTable for convenience.
 * @param {string[]} headers
 * @param {string[][]} rows
 * @returns {string}
 */
export { serializeTable as formatTable } from './serialize.js';

/**
 * Format a number as USD currency.
 * @param {number} amount
 * @returns {string}
 */
export function formatCurrency(amount) {
  return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(amount);
}

/**
 * Return a human-readable relative time string.
 * @param {Date|string|number} date
 * @returns {string}
 */
export function relativeTime(date) {
  const now = Date.now();
  const then = new Date(date).getTime();
  const diffMs = now - then;
  const absDiff = Math.abs(diffMs);
  const future = diffMs < 0;

  const seconds = Math.floor(absDiff / 1000);
  const minutes = Math.floor(seconds / 60);
  const hours = Math.floor(minutes / 60);
  const days = Math.floor(hours / 24);

  let str;
  if (seconds < 60) str = `${seconds} seconds`;
  else if (minutes < 60) str = `${minutes} minute${minutes !== 1 ? 's' : ''}`;
  else if (hours < 24) str = `${hours} hour${hours !== 1 ? 's' : ''}`;
  else str = `${days} day${days !== 1 ? 's' : ''}`;

  return future ? `in ${str}` : `${str} ago`;
}
