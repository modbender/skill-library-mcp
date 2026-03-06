/**
 * before_tool_call hook — the main firewall.
 *
 * Runs on every tool call. Evaluates the call against the policy engine
 * and returns a block/allow/dry-run decision.
 */

import type {
  PluginHookBeforeToolCallEvent,
  PluginHookBeforeToolCallResult,
  PluginHookToolContext,
  PluginLogger,
} from "openclaw/plugin-sdk";
import type { PolicyEngine } from "../engine.js";
import type { StateManager } from "../state.js";

export function createBeforeToolCallHandler(deps: {
  engine: PolicyEngine;
  state: StateManager;
  logger: PluginLogger;
}) {
  const { engine, state, logger } = deps;

  return (
    event: PluginHookBeforeToolCallEvent,
    ctx: PluginHookToolContext,
  ): PluginHookBeforeToolCallResult | void => {
    try {
      // Break-glass bypass: OPENCLAW_POLICY_BYPASS=1
      // Allows operators to escape a locked system without editing config.
      // NEVER enable this by default in production.
      if (process.env.OPENCLAW_POLICY_BYPASS === "1") {
        logger.warn(
          `policy:bypass OPENCLAW_POLICY_BYPASS active — all tools allowed (tool=${event.toolName})`,
        );
        return undefined;
      }

      const sessionKey = ctx.sessionKey ?? "unknown";
      const sessionState = state.get(sessionKey);

      const decision = engine.evaluate({
        toolName: event.toolName,
        params: event.params,
        agentId: ctx.agentId,
        sessionKey,
        blockedCount: sessionState.blockedCount,
      });

      // Dry-run: block with a stub response
      if (decision.action === "dryrun") {
        const stub = engine.buildDryRunStub(event.toolName, event.params);
        logger.info(
          `policy:dryrun tool=${event.toolName} tier=${decision.tier} session=${sessionKey}`,
        );
        state.recordToolCall(sessionKey, event.toolName, false);
        return {
          block: true,
          blockReason: JSON.stringify(stub),
        };
      }

      // Block: record and return reason
      if (decision.action === "block") {
        state.recordToolCall(sessionKey, event.toolName, false);

        // Check if we should escalate
        const currentState = state.get(sessionKey);
        if (currentState.blockedCount >= (deps.engine as any).config.maxBlockedRetries) {
          const level = state.escalate(sessionKey);
          logger.info(
            `policy:escalate session=${sessionKey} level=${level} blockedCount=${currentState.blockedCount}`,
          );
        }

        logger.info(
          `policy:block tool=${event.toolName} tier=${decision.tier} reason="${decision.reason}" session=${sessionKey}`,
        );

        const blockMessage = decision.remediation
          ? `${decision.reason}\n\nRemediation: ${decision.remediation}`
          : decision.reason ?? "Blocked by policy engine";

        return {
          block: true,
          blockReason: blockMessage,
        };
      }

      // Allow
      state.recordToolCall(sessionKey, event.toolName, true);

      // T2 tools always logged at info level
      if (decision.tier === "T2") {
        logger.info(
          `policy:allow tool=${event.toolName} tier=T2 session=${sessionKey}`,
        );
      } else {
        logger.debug?.(
          `policy:allow tool=${event.toolName} tier=${decision.tier} session=${sessionKey}`,
        );
      }

      return undefined; // allow — no modification
    } catch (err) {
      // Defensive: never crash the agent
      logger.error(
        `policy-engine before_tool_call error: ${err instanceof Error ? err.message : String(err)}`,
      );
      return undefined; // fail-open
    }
  };
}
