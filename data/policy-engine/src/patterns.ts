/**
 * Deny pattern matching for tool arguments.
 *
 * Checks tool parameters against dangerous argument patterns
 * (fork bombs, disk wipes, system path writes, etc.).
 *
 * IMPORTANT: Pattern matching is scoped to RELEVANT params only.
 * - exec: checks "command" param (not env vars, workdir, etc.)
 * - write/edit: checks path params only (NOT file content)
 * - This prevents false positives when content merely *discusses*
 *   system paths or dangerous commands.
 */

const DEFAULT_EXEC_DENY_PATTERNS: string[] = [
  "rm -rf",
  "mkfs",
  ":(){ :|:& };:",
  "dd if=",
  "> /dev/sd",
  "chmod -R 777 /",
  "mv /* ",
  "wget -O- | sh",
  "curl | sh",
];

const DEFAULT_WRITE_DENY_PATTERNS: string[] = [
  "/etc/",
  "/boot/",
  "/sys/",
  "/proc/",
  "/dev/",
  "/sbin/",
  "/usr/sbin/",
];

const BUILT_IN_DENY_PATTERNS: Record<string, string[]> = {
  exec: DEFAULT_EXEC_DENY_PATTERNS,
  write: DEFAULT_WRITE_DENY_PATTERNS,
  edit: DEFAULT_WRITE_DENY_PATTERNS,
  apply_patch: DEFAULT_WRITE_DENY_PATTERNS,
};

/**
 * Tool-specific parameter keys that should be checked for deny patterns.
 * Only these params are scanned — content/body params are excluded to
 * prevent false positives when writing documentation or code that
 * mentions system paths or dangerous commands in prose.
 */
const TOOL_RELEVANT_PARAMS: Record<string, string[]> = {
  exec: ["command"],
  write: ["file_path", "path"],
  edit: ["file_path", "path"],
  apply_patch: ["file_path", "path"],
  browser: ["path", "outPath", "file_path"],
};

/**
 * Get the combined deny patterns for a tool: built-in + user-configured.
 */
function getDenyPatterns(
  toolName: string,
  userPatterns: Record<string, string[]>,
): string[] {
  const name = toolName.toLowerCase();
  const builtIn = BUILT_IN_DENY_PATTERNS[name] ?? [];
  const user = userPatterns[name] ?? [];
  if (builtIn.length === 0 && user.length === 0) {
    return [];
  }
  return [...builtIn, ...user];
}

/**
 * Extract only the relevant parameter values for pattern matching.
 * If a tool has specific relevant params defined, only those are checked.
 * Otherwise, falls back to checking all string params (for user-configured tools).
 */
function extractRelevantValues(
  toolName: string,
  params: Record<string, unknown>,
): string {
  const name = toolName.toLowerCase();
  const relevantKeys = TOOL_RELEVANT_PARAMS[name];

  if (relevantKeys) {
    // Scoped matching: only check specified params
    const parts: string[] = [];
    for (const key of relevantKeys) {
      for (const [paramKey, paramValue] of Object.entries(params)) {
        if (paramKey.toLowerCase() === key.toLowerCase() && typeof paramValue === "string") {
          parts.push(paramValue);
        }
      }
    }
    return parts.join(" ");
  }

  // Fallback for unknown tools: check all string params
  return flattenAllParams(params);
}

/**
 * Flatten all parameter values into a single string (fallback for unknown tools).
 */
function flattenAllParams(params: Record<string, unknown>): string {
  const parts: string[] = [];
  for (const value of Object.values(params)) {
    if (typeof value === "string") {
      parts.push(value);
    } else if (typeof value === "number" || typeof value === "boolean") {
      parts.push(String(value));
    } else if (Array.isArray(value)) {
      for (const item of value) {
        if (typeof item === "string") {
          parts.push(item);
        }
      }
    }
  }
  return parts.join(" ");
}

export type PatternMatchResult = {
  matched: boolean;
  pattern?: string;
};

/**
 * Check whether tool params contain any denied patterns.
 * Only checks RELEVANT params for known tools to prevent false positives.
 */
export function matchDenyPatterns(
  toolName: string,
  params: Record<string, unknown>,
  userPatterns: Record<string, string[]>,
): PatternMatchResult {
  const patterns = getDenyPatterns(toolName, userPatterns);
  if (patterns.length === 0) {
    return { matched: false };
  }

  const relevant = extractRelevantValues(toolName, params).toLowerCase();
  if (relevant.length === 0) {
    return { matched: false };
  }

  for (const pattern of patterns) {
    if (relevant.includes(pattern.toLowerCase())) {
      return { matched: true, pattern };
    }
  }

  return { matched: false };
}

// ---------------------------------------------------------------------------
// Path allowlist enforcement
// ---------------------------------------------------------------------------

import nodePath from "node:path";

export type PathAllowlistResult = {
  blocked: boolean;
  resolvedPath?: string;
  reason?: string;
};

/**
 * Extract path-like parameter values from tool params.
 * Uses TOOL_RELEVANT_PARAMS for known tools; for unknown tools returns empty
 * (no path enforcement unless explicitly configured).
 */
function extractPathValues(
  toolName: string,
  params: Record<string, unknown>,
): string[] {
  const name = toolName.toLowerCase();
  const relevantKeys = TOOL_RELEVANT_PARAMS[name];
  if (!relevantKeys) {
    return [];
  }

  const paths: string[] = [];
  for (const key of relevantKeys) {
    for (const [paramKey, paramValue] of Object.entries(params)) {
      if (paramKey.toLowerCase() === key.toLowerCase() && typeof paramValue === "string" && paramValue.length > 0) {
        paths.push(paramValue);
      }
    }
  }
  return paths;
}

/**
 * Check whether tool params target paths within the configured allowlist.
 *
 * Canonicalizes paths using path.resolve() (handles ../ without filesystem
 * access) and checks that the resolved path starts with at least one
 * allowed prefix. This prevents path traversal bypasses.
 *
 * Opt-in: if no pathAllowlists entry exists for a tool, all paths are allowed.
 */
export function checkPathAllowlist(
  toolName: string,
  params: Record<string, unknown>,
  pathAllowlists: Record<string, string[]>,
): PathAllowlistResult {
  const name = toolName.toLowerCase();

  // Find allowlist — check exact name first, then lowercase
  const allowedPrefixes = pathAllowlists[name] ?? pathAllowlists[toolName];
  if (!allowedPrefixes || allowedPrefixes.length === 0) {
    return { blocked: false };
  }

  const pathValues = extractPathValues(name, params);
  if (pathValues.length === 0) {
    // Tool has an allowlist but no path params found — allow (e.g. browser snapshot)
    return { blocked: false };
  }

  for (const rawPath of pathValues) {
    let resolved: string;
    try {
      resolved = nodePath.resolve(rawPath);
    } catch {
      // Fail closed: if resolution fails, block
      return {
        blocked: true,
        resolvedPath: rawPath,
        reason: `Blocked: could not resolve path "${rawPath}"`,
      };
    }

    // Check if resolved path starts with any allowed prefix
    const allowed = allowedPrefixes.some((prefix) => {
      // Normalize prefix: ensure it ends with separator for directory matching
      const normalizedPrefix = prefix.endsWith(nodePath.sep) ? prefix : prefix + nodePath.sep;
      // Allow exact match to the prefix directory itself, or anything under it
      return resolved === prefix.replace(/\/$/, "") || resolved.startsWith(normalizedPrefix);
    });

    if (!allowed) {
      return {
        blocked: true,
        resolvedPath: resolved,
        reason: `Blocked: path "${resolved}" is outside allowed directories [${allowedPrefixes.join(", ")}]`,
      };
    }
  }

  return { blocked: false };
}
