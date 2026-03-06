import type { ShieldClient, ScanResult } from "../shield-client.js";
import type { PluginConfig } from "../config.js";
import { ShieldBlockedError, ShieldUnavailableError } from "../errors.js";

/**
 * Scans every incoming user message for prompt injection, unicode smuggling,
 * and other input-layer attacks.
 *
 * Hook phase: preRequest (runs before LLM sees the message)
 * Fail behavior: respects config.fail_closed
 */
export function createPreRequestHook(client: ShieldClient, config: PluginConfig) {
  return async (ctx: {
    request: { content: string; channel: string; messageId: string };
    sessionKey: string;
  }): Promise<void> => {
    if (!config.scan.inputs) return;
    if (config.excluded_channels.includes(ctx.request.channel)) return;

    let result: ScanResult;
    try {
      result = await client.scanInput(ctx.request.content, ctx.sessionKey);
    } catch (err) {
      if (err instanceof ShieldUnavailableError) {
        if (config.fail_closed) throw err;
        return; // fail-open: allow through
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
        phase: "preRequest",
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
