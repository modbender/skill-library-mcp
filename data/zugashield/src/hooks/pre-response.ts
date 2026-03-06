import type { ShieldClient, ScanResult } from "../shield-client.js";
import type { PluginConfig } from "../config.js";
import { ShieldBlockedError, ShieldUnavailableError } from "../errors.js";

/**
 * Scans every LLM response before it's sent to the user. Catches:
 * - Leaked API keys, secrets, and credentials
 * - PII exposure (SSNs, credit cards, etc.)
 * - DNS exfiltration patterns (high-entropy subdomains)
 * - Encoded data exfiltration (base64 blobs, hex streams)
 *
 * Hook phase: preResponse (runs after LLM generates, before delivery)
 * Fail behavior: respects config.fail_closed
 */
export function createPreResponseHook(client: ShieldClient, config: PluginConfig) {
  return async (ctx: {
    response: { content: string };
    request: { channel: string };
    sessionKey: string;
  }): Promise<void> => {
    if (!config.scan.outputs) return;
    if (config.excluded_channels.includes(ctx.request.channel)) return;

    let result: ScanResult;
    try {
      result = await client.scanOutput(ctx.response.content, ctx.sessionKey);
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
        phase: "preResponse",
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
