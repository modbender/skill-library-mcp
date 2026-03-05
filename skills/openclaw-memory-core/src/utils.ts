import path from "node:path";
import os from "node:os";

/** Expand leading `~` to the user's home directory. */
export function expandHome(p: string): string {
  if (!p) return p;
  if (p === "~") return os.homedir();
  if (p.startsWith("~/") || p.startsWith("~\\")) return path.join(os.homedir(), p.slice(2));
  return p;
}

/**
 * Resolve a path and ensure it stays inside the user's home directory.
 * Throws if the resolved path would escape home (path traversal guard).
 * Uses case-insensitive comparison on Windows.
 *
 * Also rejects Windows-style absolute paths (e.g. C:\...) on non-Windows
 * platforms. On Linux, path.resolve would treat "C:\Windows\..." as a
 * relative segment appended to cwd, silently placing it inside home - which
 * is misleading and a potential security issue.
 */
export function safePath(p: string, label = "storePath"): string {
  // Reject Windows absolute paths on non-Windows platforms.
  // Match drive letters like C:\ or C:/ (case-insensitive).
  if (process.platform !== "win32" && /^[A-Za-z]:[/\\]/.test(p)) {
    throw new Error(
      `[openclaw] ${label} must be inside the home directory. Got: ${p} (Windows-style absolute path on non-Windows platform)`,
    );
  }

  const resolved = path.resolve(p);
  const home = os.homedir();
  // On Windows paths are case-insensitive; normalise both sides before comparing.
  const normalize = (s: string) => process.platform === "win32" ? s.toLowerCase() : s;
  const rn = normalize(resolved);
  const hn = normalize(home);
  if (!rn.startsWith(hn + path.sep) && rn !== hn) {
    throw new Error(`[openclaw] ${label} must be inside the home directory. Got: ${resolved}`);
  }
  return resolved;
}

/** Clamp an untrusted number to [1, max], returning dflt when invalid. */
export function safeLimit(val: unknown, dflt: number, max: number): number {
  const n = Math.trunc(Number(val));
  return isNaN(n) || n < 1 ? dflt : Math.min(n, max);
}

/** Return an ISO 8601 timestamp `ms` milliseconds from now. Useful for setting MemoryItem.expiresAt. */
export function ttlMs(ms: number): string {
  return new Date(Date.now() + ms).toISOString();
}
