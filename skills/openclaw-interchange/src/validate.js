/**
 * Required frontmatter fields.
 */
const REQUIRED_FIELDS = [
  'skill', 'type', 'layer', 'updated', 'version',
  'generation_id', 'content_hash', 'generator', 'tags',
];

const VALID_LAYERS = ['ops', 'state'];
const VALID_TYPES = ['summary', 'detail', 'alert'];

/**
 * Validate frontmatter has all required fields with correct types.
 * @param {Record<string, any>} meta
 * @returns {{ valid: boolean, errors: string[] }}
 */
export function validateFrontmatter(meta) {
  const errors = [];

  for (const field of REQUIRED_FIELDS) {
    if (meta[field] === undefined || meta[field] === null) {
      errors.push(`Missing required field: ${field}`);
    }
  }

  if (meta.layer && !VALID_LAYERS.includes(meta.layer)) {
    errors.push(`Invalid layer: ${meta.layer} (must be ops or state)`);
  }
  if (meta.type && !VALID_TYPES.includes(meta.type)) {
    errors.push(`Invalid type: ${meta.type} (must be summary, detail, or alert)`);
  }
  if (meta.tags && !Array.isArray(meta.tags)) {
    errors.push('tags must be an array');
  }
  if (meta.generation_id !== undefined && (typeof meta.generation_id !== 'number' || meta.generation_id < 1)) {
    errors.push('generation_id must be a positive number');
  }
  if (meta.content_hash && !String(meta.content_hash).startsWith('sha256:')) {
    errors.push('content_hash must start with sha256:');
  }

  return { valid: errors.length === 0, errors };
}

/**
 * Validate that a file's path matches its layer field.
 * @param {string} filePath - File path
 * @param {Record<string, any>} meta - Frontmatter
 * @returns {{ valid: boolean, errors: string[] }}
 */
export function validateLayer(filePath, meta) {
  const errors = [];
  if (!meta.layer) {
    errors.push('No layer field in frontmatter');
    return { valid: false, errors };
  }
  const normalized = filePath.replace(/\\/g, '/');
  if (!normalized.includes(`/${meta.layer}/`)) {
    errors.push(`File path "${filePath}" does not contain /${meta.layer}/ but layer is "${meta.layer}"`);
  }
  return { valid: errors.length === 0, errors };
}
