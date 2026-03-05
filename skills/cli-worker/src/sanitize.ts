/**
 * Shared prompt sanitization for all CLI providers.
 * Prevents argument injection and control sequence attacks.
 *
 * Security:
 * - Strips null bytes (can truncate argv in C-style parsers).
 * - Replaces other C0 control chars (except tab, newline, CR) with space
 *   so downstream cannot be confused by control sequences.
 *
 * All providers must use this before passing prompts to spawn().
 */

/**
 * Sanitize prompt before passing to subprocess.
 * - Strips null bytes (\0).
 * - Replaces other C0 control characters (except tab \t, newline \n, carriage return \r) with space.
 *
 * Used with spawn() with an array of args (no shell), so the prompt is a single
 * argument; this is defense-in-depth.
 */
export function sanitizePrompt(prompt: string): string {
  return (
    prompt
      .replace(/\0/g, "")
      // eslint-disable-next-line no-control-regex
      .replace(/[\x01-\x08\x0b\x0c\x0e-\x1f]/g, " ")
  );
}
