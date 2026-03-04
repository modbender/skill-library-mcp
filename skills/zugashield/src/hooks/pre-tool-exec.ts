import type { ShieldClient, ScanResult } from "../shield-client.js";
import type { PluginConfig } from "../config.js";
import { ShieldBlockedError, ShieldUnavailableError } from "../errors.js";

/**
 * Scans every tool call before execution for SSRF, command injection,
 * path traversal, and other tool-layer attacks.
 *
 * Hook phase: preToolExecution
 *
 * ALWAYS FAIL-CLOSED: Even when config.fail_closed is false, this hook
 * blocks when the scanner is unavailable. Tool execution is too dangerous
 * to allow blindly — a single unscanned `bash` or `http_request` call
 * could compromise the host.
 */
export function createPreToolExecHook(client: ShieldClient, config: PluginConfig) {
  return async (ctx: {
    tool: { name: string; args: Record<string, unknown> };
    request: { channel: string };
    sessionKey: string;
  }): Promise<void> => {
    if (!config.scan.tool_calls) return;
    // No channel exclusion for tool calls — too dangerous to skip

    let result: ScanResult;
    try {
      result = await client.scanToolCall(ctx.tool.name, ctx.tool.args, ctx.sessionKey);
    } catch (err) {
      if (err instanceof ShieldUnavailableError) {
        // ALWAYS fail-closed for tool execution, regardless of config
        throw new ShieldUnavailableError(
          "Scanner unavailable — tool execution blocked for safety",
        );
      }
      throw err;
    }

    if (shouldBlock(result, config.strict_mode)) {
      throw new ShieldBlockedError({
        verdict: result.verdict,
        threatLevel: result.max_threat_level,
        threats: result.threats.map(t => ({
          category: t.category,
          description: t.description,
        })),
        phase: "preToolExecution",
      });
    }
  };
}

function shouldBlock(result: ScanResult, strictMode: boolean): boolean {
  if (result.is_blocked) return true;
  if (strictMode && isMediumOrAbove(result.max_threat_level)) return true;
  return false;
}

function isMediumOrAbove(level: string): boolean {
  return level === "medium" || level === "high" || level === "critical";
}
