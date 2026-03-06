/**
 * OpenCode CLI Provider implementation.
 *
 * OpenCode CLI docs: https://open-code.ai/en/docs/cli
 * - Command: `opencode run "<prompt>"`
 * - Headless: `opencode run "message" --format json`
 * - Auth: Credentials in ~/.local/share/opencode/auth.json or via `opencode auth list`
 * - Output: JSON format (schema TBD). For v1, we treat full stdout as finalText if JSON parsing fails.
 */

import fs from "node:fs";
import path from "node:path";
import os from "node:os";
import { spawn, spawnSync } from "node:child_process";
import { createInterface } from "node:readline";
import type {
  CLIProvider,
  ProviderId,
  VerifyResult,
  RunResult,
  RunOptions,
  ParseResult,
  JsonValue,
} from "./types.js";
import { sanitizePrompt } from "../sanitize.js";

/**
 * Safe CLI executable path for OpenCode subprocess calls.
 * Same validation as KIMI_CLI_PATH.
 */
// eslint-disable-next-line no-control-regex
const SAFE_CLI_PATH_REGEX = /^[^\s;|&$`"'<>\x00-\x1f]+$/;
const MAX_LEN = 512;

function getSafeOpenCodeCliPath(): string {
  const raw = process.env.OPENCODE_CLI_PATH;
  if (raw == null || raw === "") return "opencode";
  if (raw.length > MAX_LEN) return "opencode";
  if (!SAFE_CLI_PATH_REGEX.test(raw)) return "opencode";
  return raw;
}

/**
 * Get OpenCode config directory.
 * Uses ~/.local/share/opencode by default (XDG compliant).
 */
function getOpenCodeConfigDir(): string {
  const xdgDataHome = process.env.XDG_DATA_HOME;
  if (xdgDataHome) {
    return path.join(xdgDataHome, "opencode");
  }
  return path.join(os.homedir(), ".local", "share", "opencode");
}

/**
 * Parse OpenCode output.
 * Tries to parse JSON events first; if that fails, treats full stdout as finalText.
 *
 * OpenCode's --format json output format is not fully documented.
 * Strategy:
 * 1. Try to parse as NDJSON with text deltas (similar to Claude)
 * 2. Try to extract a final "result" or "message" field
 * 3. Fallback: join all lines as finalText
 */
export function parseOpenCodeOutput(lines: string[]): ParseResult {
  const raw: JsonValue[] = [];
  const textParts: string[] = [];

  for (const line of lines) {
    const trimmed = line.trim();
    if (!trimmed) continue;

    try {
      const obj = JSON.parse(trimmed) as JsonValue;
      raw.push(obj);

      // Try to extract text from common JSON response patterns
      if (typeof obj === "object" && obj !== null) {
        // Pattern 1: delta.text (event stream like Claude)
        if (obj.delta?.text) {
          textParts.push(String(obj.delta.text));
        }
        // Pattern 2: content field
        else if (typeof obj.content === "string") {
          textParts.push(obj.content);
        }
        // Pattern 3: message.content
        else if (obj.message?.content) {
          textParts.push(String(obj.message.content));
        }
        // Pattern 4: result field
        else if (typeof obj.result === "string") {
          textParts.push(obj.result);
        }
        // Pattern 5: text field
        else if (typeof obj.text === "string") {
          textParts.push(obj.text);
        }
      }
    } catch {
      // Not JSON - treat as plain text line
      textParts.push(line);
    }
  }

  // If we couldn't extract structured text, join all lines
  const finalText =
    textParts.length > 0 ? textParts.join("") : lines.join("\n");

  return { finalText, raw };
}

export class OpenCodeProvider implements CLIProvider {
  readonly id: ProviderId = "opencode";
  readonly displayName = "OpenCode";

  /**
   * Verify OpenCode CLI is installed and authenticated.
   * Checks for auth.json file and optionally runs `opencode auth list`.
   */
  verify(): VerifyResult {
    // Check if auth.json exists
    const configDir = getOpenCodeConfigDir();
    const authFile = path.join(configDir, "auth.json");

    const hasAuthFile = fs.existsSync(authFile);

    // Try to run opencode auth list to verify CLI works
    const opencodeCmd = getSafeOpenCodeCliPath();
    const result = spawnSync(opencodeCmd, ["auth", "list"], {
      encoding: "utf-8",
      timeout: 10_000,
      stdio: ["pipe", "pipe", "pipe"],
      shell: false,
    });

    if (result.status === 0) {
      return { ok: true };
    }

    // If auth list failed, provide helpful error
    const msg =
      result.error?.message ?? result.stderr?.trim() ?? `exit ${result.status}`;

    if (!hasAuthFile) {
      return {
        ok: false,
        reason: "auth_missing",
        detail: `OpenCode auth file not found at ${authFile}. Run 'opencode auth login' to authenticate.`,
      };
    }

    return {
      ok: false,
      reason: "run_failed",
      detail: `OpenCode CLI verification failed: ${msg}. Ensure 'opencode' is on PATH and authenticated.`,
    };
  }

  /**
   * Run OpenCode CLI with a prompt.
   * Uses spawn() with an argument array (no shell).
   * Prompt is sanitized before passing.
   *
   * Command: opencode run "<prompt>" --format json
   */
  run(
    prompt: string,
    cwd: string,
    options: RunOptions = {}
  ): Promise<RunResult> {
    const safePrompt = sanitizePrompt(prompt);
    return new Promise((resolve, reject) => {
      const opencodeCmd = getSafeOpenCodeCliPath();
      // opencode uses 'run' subcommand, not '-p' flag
      const args = ["run", safePrompt, "--format", "json"];

      const child = spawn(opencodeCmd, args, {
        cwd,
        env: process.env,
        stdio: ["pipe", "pipe", "pipe"],
      });

      const stdoutLines: string[] = [];
      const rl = createInterface({ input: child.stdout, crlfDelay: Infinity });
      rl.on("line", (line) => stdoutLines.push(line));

      let stderr = "";
      child.stderr?.on("data", (chunk: Buffer) => {
        stderr += chunk.toString();
      });

      let timeoutId: ReturnType<typeof setTimeout> | undefined;
      if (options.timeoutMs && options.timeoutMs > 0) {
        timeoutId = setTimeout(() => {
          child.kill("SIGTERM");
          timeoutId = setTimeout(() => child.kill("SIGKILL"), 2000);
        }, options.timeoutMs);
      }

      child.on("error", (err) => {
        if (timeoutId) clearTimeout(timeoutId);
        reject(err);
      });

      child.on("close", (code, signal) => {
        if (timeoutId) clearTimeout(timeoutId);
        resolve({
          exitCode: code,
          signal: signal,
          stdoutLines,
          stderr,
        });
      });
    });
  }

  /**
   * Parse OpenCode output.
   * Handles JSON format if available, otherwise treats as plain text.
   */
  parseStdout(lines: string[]): ParseResult {
    return parseOpenCodeOutput(lines);
  }

  /**
   * Get the report subdirectory name.
   */
  reportSubdir(): string {
    return "opencode-reports";
  }

  /**
   * Get the AGENTS.md title.
   */
  agentsMdTitle(): string {
    return "OpenClaw OpenCode Worker - Task Instructions";
  }
}

/** Singleton instance */
export const opencodeProvider = new OpenCodeProvider();
