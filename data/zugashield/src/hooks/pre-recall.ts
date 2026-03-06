import type { ShieldClient, ScanResult } from "../shield-client.js";
import type { PluginConfig } from "../config.js";
import { ShieldBlockedError, ShieldUnavailableError } from "../errors.js";

/**
 * Scans memory content before it's recalled into the LLM context.
 * Blocks poisoned memories — content that was stored earlier by an attacker
 * and contains embedded instructions, prompt injections, or manipulation.
 *
 * Hook phase: preRecall (runs before memory content enters the prompt)
 * Fail behavior: respects config.fail_closed
 *
 * Note: The `request.content` field carries the memory text being recalled,
 * not the user's original message (which was already scanned in preRequest).
 */
export function createPreRecallHook(client: ShieldClient, config: PluginConfig) {
  return async (ctx: {
    request: { content: string; channel: string };
    sessionKey: string;
  }): Promise<void> => {
    if (!config.scan.memory) return;
    if (config.excluded_channels.includes(ctx.request.channel)) return;

    let result: ScanResult;
    try {
      result = await client.scanMemory(ctx.request.content, "memory-recall");
    } catch (err) {
      if (err instanceof ShieldUnavailableError) {
        if (config.fail_closed) throw err;
        return;
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
        phase: "preRecall",
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
