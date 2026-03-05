/**
 * after_tool_call hook — result tracking.
 *
 * Logs tool call outcomes for audit trail. No blocking logic.
 */

import type {
  PluginHookAfterToolCallEvent,
  PluginHookToolContext,
  PluginLogger,
} from "openclaw/plugin-sdk";
import type { PolicyConfig } from "../config.js";
import { getToolTier } from "../tiers.js";

export function createAfterToolCallHandler(deps: {
  config: PolicyConfig;
  logger: PluginLogger;
}) {
  const { logger } = deps;

  return (
    event: PluginHookAfterToolCallEvent,
    ctx: PluginHookToolContext,
  ): void => {
    try {
      const tier = getToolTier(event.toolName, deps.config.riskTiers);
      const sessionKey = ctx.sessionKey ?? "unknown";
      const duration = event.durationMs != null ? ` duration=${event.durationMs}ms` : "";
      const errorSuffix = event.error ? ` error="${event.error}"` : "";

      if (tier === "T2" || event.error) {
        logger.info(
          `policy:after tool=${event.toolName} tier=${tier} session=${sessionKey}${duration}${errorSuffix}`,
        );
      } else {
        logger.debug?.(
          `policy:after tool=${event.toolName} tier=${tier} session=${sessionKey}${duration}`,
        );
      }
    } catch (err) {
      logger.error(
        `policy-engine after_tool_call error: ${err instanceof Error ? err.message : String(err)}`,
      );
    }
  };
}
