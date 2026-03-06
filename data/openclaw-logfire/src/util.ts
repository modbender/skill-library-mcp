// SPDX-License-Identifier: MIT
/**
 * Shared utilities: safe JSON serialization, truncation, secret redaction.
 */

/** Patterns that likely indicate secret values. */
const SECRET_PATTERNS = [
  /(?:api[_-]?key|token|secret|password|auth|credential|bearer)\s*[:=]\s*["']?[^\s"',}{]{8,}/gi,
  /(?:sk|pk|rk|pat|ghp|gho|glpat|xox[bpras])[_-][A-Za-z0-9_-]{10,}/g,
  /eyJ[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}/g, // JWT
];

/**
 * Serialize a value to JSON, handling circular refs and BigInts.
 * Returns an empty string on failure rather than throwing.
 */
export function safeJsonStringify(value: unknown): string {
  const seen = new WeakSet();
  try {
    return JSON.stringify(value, (_key, val) => {
      if (typeof val === 'bigint') return val.toString();
      if (typeof val === 'object' && val !== null) {
        if (seen.has(val)) return '[Circular]';
        seen.add(val);
      }
      return val;
    });
  } catch {
    return String(value);
  }
}

/** Truncate a string to maxLength, appending "...[truncated]" if needed. */
export function truncate(value: string, maxLength: number): string {
  if (value.length <= maxLength) return value;
  return value.slice(0, maxLength) + '...[truncated]';
}

/** Redact likely secrets from a string. */
export function redactSecrets(value: string): string {
  let result = value;
  for (const pattern of SECRET_PATTERNS) {
    // Reset lastIndex for global regexes
    pattern.lastIndex = 0;
    result = result.replace(pattern, (match) => {
      // Keep the key name, redact the value portion
      const eqIdx = match.search(/[:=]/);
      if (eqIdx !== -1) {
        return match.slice(0, eqIdx + 1) + ' [REDACTED]';
      }
      return '[REDACTED]';
    });
  }
  return result;
}

/**
 * Prepare a tool input/output value for recording as a span attribute.
 * Serializes to JSON, optionally redacts secrets, and truncates.
 */
export function prepareForCapture(
  value: unknown,
  maxLength: number,
  redact: boolean,
): string {
  let str = typeof value === 'string' ? value : safeJsonStringify(value);
  if (redact) {
    str = redactSecrets(str);
  }
  return truncate(str, maxLength);
}

/**
 * Extract workspace name from a workspace directory path.
 * e.g., "/path/to/workspaces/chief-of-staff" -> "chief-of-staff"
 */
export function extractWorkspaceName(workspaceDir: string | undefined): string {
  if (!workspaceDir) return 'unknown';
  const parts = workspaceDir.replace(/\/$/, '').split('/');
  return parts[parts.length - 1] || 'unknown';
}

/**
 * Generate a short unique ID for tool call correlation.
 * Uses timestamp + random suffix to avoid collisions without
 * pulling in a uuid dependency.
 */
export function generateCallId(): string {
  const ts = Date.now().toString(36);
  const rand = Math.random().toString(36).slice(2, 8);
  return `${ts}-${rand}`;
}

/**
 * Extract error details in a structured format suitable for OTEL
 * exception semantic conventions.
 */
export function extractErrorDetails(error: unknown): {
  type: string;
  message: string;
  stacktrace: string;
} {
  if (error instanceof Error) {
    return {
      type: error.constructor.name || 'Error',
      message: error.message,
      stacktrace: error.stack ?? '',
    };
  }
  if (typeof error === 'string') {
    return { type: 'Error', message: error, stacktrace: '' };
  }
  return {
    type: 'Error',
    message: safeJsonStringify(error),
    stacktrace: '',
  };
}
