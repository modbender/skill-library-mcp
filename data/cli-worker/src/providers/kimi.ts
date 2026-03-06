/**
 * Kimi CLI Provider implementation.
 * Delegates to existing auth, spawn, and parser modules.
 */

import type {
  CLIProvider,
  ProviderId,
  VerifyResult,
  RunResult,
  RunOptions,
  ParseResult,
} from "./types.js";
import { verifyAll } from "../auth/verify.js";
import { runKimi } from "../spawn/run.js";
import { parseStreamJson } from "../parser/stream-json.js";

export class KimiProvider implements CLIProvider {
  readonly id: ProviderId = "kimi";
  readonly displayName = "Kimi CLI";

  /**
   * Verify Kimi CLI is installed and authenticated.
   * Delegates to verifyAll() from auth/verify module.
   */
  verify(): VerifyResult {
    return verifyAll();
  }

  /**
   * Run Kimi CLI with a prompt.
   * Delegates to runKimi() from spawn/run module.
   * Sanitization is handled internally by runKimi.
   */
  run(prompt: string, cwd: string, options?: RunOptions): Promise<RunResult> {
    return runKimi(prompt, cwd, options);
  }

  /**
   * Parse Kimi stream-json output.
   * Delegates to parseStreamJson() from parser/stream-json module.
   */
  parseStdout(lines: string[]): ParseResult {
    return parseStreamJson(lines);
  }

  /**
   * Get the report subdirectory name.
   */
  reportSubdir(): string {
    return "kimi-reports";
  }

  /**
   * Get the AGENTS.md title.
   */
  agentsMdTitle(): string {
    return "OpenClaw Kimi Worker - Task Instructions";
  }
}

/** Singleton instance */
export const kimiProvider = new KimiProvider();
