/**
 * Safe CLI executable path for subprocess calls. Prevents abuse when
 * KIMI_CLI_PATH (or similar) is set by an untrusted environment.
 * Must not contain shell metacharacters or spaces; used with spawn(..., { shell: false }).
 */
// eslint-disable-next-line no-control-regex
const SAFE_CLI_PATH_REGEX = /^[^\s;|&$`"'<>\x00-\x1f]+$/;
const MAX_LEN = 512;

export function getSafeKimiCliPath(): string {
  const raw = process.env.KIMI_CLI_PATH;
  if (raw == null || raw === "") return "kimi";
  if (raw.length > MAX_LEN) return "kimi";
  if (!SAFE_CLI_PATH_REGEX.test(raw)) return "kimi";
  return raw;
}
