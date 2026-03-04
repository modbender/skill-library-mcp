import yaml from 'js-yaml';

/**
 * Serialize frontmatter to deterministic YAML string.
 * Keys are sorted alphabetically; output is stable across runs.
 * @param {Record<string, any>} meta - Frontmatter object
 * @returns {string} YAML string (without --- delimiters)
 */
export function serializeFrontmatter(meta) {
  const sorted = sortObject(coerceDates(meta));
  return yaml.dump(sorted, {
    sortKeys: true,
    lineWidth: -1,
    noRefs: true,
    quotingType: '"',
    forceQuotes: false,
  }).trimEnd();
}

/**
 * Coerce Date objects to ISO strings for deterministic serialization.
 * @param {any} obj
 * @returns {any}
 */
function coerceDates(obj) {
  if (obj instanceof Date) return obj.toISOString();
  if (Array.isArray(obj)) return obj.map(coerceDates);
  if (obj !== null && typeof obj === 'object') {
    const result = {};
    for (const [k, v] of Object.entries(obj)) {
      result[k] = coerceDates(v);
    }
    return result;
  }
  return obj;
}

/**
 * Deep-sort object keys alphabetically for deterministic output.
 * @param {any} obj
 * @returns {any}
 */
function sortObject(obj) {
  if (Array.isArray(obj)) return obj.map(sortObject);
  if (obj !== null && typeof obj === 'object' && !(obj instanceof Date)) {
    const sorted = {};
    for (const key of Object.keys(obj).sort()) {
      sorted[key] = sortObject(obj[key]);
    }
    return sorted;
  }
  return obj;
}

/**
 * Serialize a markdown table deterministically.
 * @param {string[]} headers - Column headers
 * @param {string[][]} rows - Table rows
 * @returns {string} Markdown table string
 */
export function serializeTable(headers, rows) {
  const cols = headers.length;
  // Calculate column widths
  const widths = headers.map((h, i) => {
    const cellWidths = rows.map(r => String(r[i] ?? '').length);
    return Math.max(String(h).length, ...cellWidths, 3);
  });

  const escape = (s) => String(s).replace(/\|/g, '\\|');
  const pad = (s, w) => escape(s).padEnd(w);
  const headerLine = '| ' + headers.map((h, i) => pad(h, widths[i])).join(' | ') + ' |';
  const sepLine = '| ' + widths.map(w => '-'.repeat(w)).join(' | ') + ' |';
  const dataLines = rows.map(
    row => '| ' + headers.map((_, i) => pad(row[i] ?? '', widths[i])).join(' | ') + ' |'
  );

  return [headerLine, sepLine, ...dataLines].join('\n');
}
