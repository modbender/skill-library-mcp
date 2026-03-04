/**
 * before_agent_start hook — static routing.
 *
 * Injects system prompt constraints based on agent ID or session context.
 * No content-based heuristics in v1 — purely static routing rules.
 */

import type {
  PluginHookBeforeAgentStartEvent,
  PluginHookBeforeAgentStartResult,
  PluginHookAgentContext,
  PluginLogger,
} from "openclaw/plugin-sdk";
import type { PolicyConfig, RoutingRule } from "../config.js";

export function createBeforeAgentStartHandler(deps: {
  config: PolicyConfig;
  logger: PluginLogger;
}) {
  const { logger } = deps;

  return (
    event: PluginHookBeforeAgentStartEvent,
    ctx: PluginHookAgentContext,
  ): PluginHookBeforeAgentStartResult | void => {
    try {
      if (!ctx.agentId) {
        return undefined;
      }

      const rule = deps.config.routing[ctx.agentId];
      if (!rule) {
        return undefined;
      }

      const constraints = buildConstraints(rule, ctx.agentId);
      if (!constraints) {
        return undefined;
      }

      logger.info(
        `policy:routing agentId=${ctx.agentId} toolProfile=${rule.toolProfile ?? "none"} model=${rule.model ?? "none"}`,
      );

      return { prependContext: constraints };
    } catch (err) {
      logger.error(
        `policy-engine before_agent_start error: ${err instanceof Error ? err.message : String(err)}`,
      );
      return undefined;
    }
  };
}

function buildConstraints(rule: RoutingRule, agentId: string): string | undefined {
  const parts: string[] = [];

  if (rule.toolProfile) {
    parts.push(
      `[Policy Engine] Agent "${agentId}" is restricted to tool profile "${rule.toolProfile}". ` +
      `Only tools in that profile are permitted.`,
    );
  }

  if (rule.model) {
    parts.push(
      `[Policy Engine] Agent "${agentId}" is assigned model "${rule.model}".`,
    );
  }

  return parts.length > 0 ? parts.join("\n") : undefined;
}
