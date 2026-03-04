export interface VettrignoreResult {
  /** Parsed glob patterns (non-empty, non-comment lines, trimmed) */
  patterns: string[];
  /** Warning messages for malformed lines (if any) */
  warnings: string[];
}

/**
 * Parse a .vettrignore file content into glob patterns.
 * Lines starting with # are comments, empty lines are skipped.
 */
export function parseVettrignore(content: string): VettrignoreResult {
  const patterns: string[] = [];
  const warnings: string[] = [];

  for (const raw of content.split('\n')) {
    const line = raw.trim();
    if (line === '' || line.startsWith('#')) continue;
    patterns.push(line);
  }

  return { patterns, warnings };
}

/**
 * Serialize a list of glob patterns back to .vettrignore format.
 * One pattern per line, trailing newline.
 */
export function serializeVettrignore(patterns: string[]): string {
  return patterns.join('\n') + '\n';
}

/**
 * Convert a vettrignore glob pattern to a RegExp.
 *
 * Supported globs:
 *  - `**` matches any sequence of characters including path separators
 *  - `*`  matches any sequence of non-separator characters
 *  - `?`  matches a single non-separator character
 *  - Patterns ending with `/` match directories (and all contents)
 *  - Patterns without `/` match filenames anywhere in the tree
 *  - Patterns with `/` (not only trailing) match from the scan root
 */
function patternToRegex(pattern: string): RegExp {
  // Directory pattern: match the directory and everything inside it
  if (pattern.endsWith('/')) {
    const dir = pattern.slice(0, -1);
    const escaped = globToRegexStr(dir);
    return new RegExp(`(^|/)${escaped}(/|$)`);
  }

  // Pattern contains a slash (not trailing) — anchored to root
  if (pattern.includes('/')) {
    const escaped = globToRegexStr(pattern);
    return new RegExp(`^${escaped}$`);
  }

  // Bare filename pattern — matches anywhere in the tree
  const escaped = globToRegexStr(pattern);
  return new RegExp(`(^|/)${escaped}$`);
}

/**
 * Convert glob characters to regex string.
 * Handles **, *, and ? while escaping everything else.
 */
function globToRegexStr(glob: string): string {
  let result = '';
  let i = 0;

  while (i < glob.length) {
    if (glob[i] === '*' && glob[i + 1] === '*') {
      result += '.*';
      i += 2;
      // Skip optional trailing slash after **
      if (glob[i] === '/') i++;
    } else if (glob[i] === '*') {
      result += '[^/]*';
      i++;
    } else if (glob[i] === '?') {
      result += '[^/]';
      i++;
    } else {
      result += escapeRegex(glob[i]!);
      i++;
    }
  }

  return result;
}

function escapeRegex(char: string): string {
  return char.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

/**
 * Check if a relative file path matches any of the vettrignore patterns.
 */
export function isExcluded(filePath: string, patterns: string[]): boolean {
  // Normalise to forward slashes for consistent matching
  const normalized = filePath.replace(/\\/g, '/');

  for (const pattern of patterns) {
    const regex = patternToRegex(pattern);
    if (regex.test(normalized)) return true;
  }

  return false;
}
