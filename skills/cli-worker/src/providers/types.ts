/**
 * Provider abstraction for CLI worker.
 * Supports Kimi, Claude Code, and OpenCode CLIs.
 */

export type ProviderId = "kimi" | "claude" | "opencode";

export interface VerifyResult {
  ok: boolean;
  reason?: string;
  detail?: string;
}

export interface RunResult {
  exitCode: number | null;
  signal: string | null;
  stdoutLines: string[];
  stderr: string;
}

export interface RunOptions {
  timeoutMs?: number;
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export type JsonValue = any;

export interface ParseResult {
  finalText: string;
  raw: JsonValue[];
}

/**
 * Interface that all CLI providers must implement.
 */
export interface CLIProvider {
  /** Provider identifier */
  readonly id: ProviderId;

  /** Display name for the provider */
  readonly displayName: string;

  /**
   * Verify that the CLI is installed and authenticated.
   * @returns VerifyResult with ok=true if ready to use
   */
  verify(): VerifyResult | Promise<VerifyResult>;

  /**
   * Run the CLI with a prompt.
   * Must call sanitizePrompt() on the prompt before passing to spawn.
   * Must use spawn(cmd, args, options) with an argument array (no shell).
   *
   * @param prompt - The task prompt to send to the CLI
   * @param cwd - Working directory for the subprocess
   * @param options - Optional timeout and other settings
   * @returns RunResult with exit code, signal, stdout lines, and stderr
   */
  run(prompt: string, cwd: string, options?: RunOptions): Promise<RunResult>;

  /**
   * Parse the stdout lines from the CLI run.
   * @param lines - Array of lines from stdout
   * @returns ParseResult with finalText and raw parsed data
   */
  parseStdout(lines: string[]): ParseResult;

  /**
   * Get the report subdirectory name for this provider.
   * @returns Subdirectory name under .openclaw/ (e.g., "kimi-reports")
   */
  reportSubdir(): string;

  /**
   * Get the AGENTS.md title for this provider.
   * @returns Title string (e.g., "OpenClaw Kimi Worker - Task Instructions")
   */
  agentsMdTitle(): string;
}
