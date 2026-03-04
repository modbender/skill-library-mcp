/**
 * Policy Engine Plugin — Entry Point
 *
 * Deterministic governance layer for OpenClaw tool execution.
 * Registers hooks for before_tool_call (firewall), after_tool_call (audit),
 * and before_agent_start (static routing).
 */

import type { OpenClawPluginApi } from "openclaw/plugin-sdk";
import { resolveConfig } from "./src/config.js";
import { PolicyEngine } from "./src/engine.js";
import { StateManager } from "./src/state.js";
import { createBeforeToolCallHandler } from "./src/hooks/before-tool-call.js";
import { createAfterToolCallHandler } from "./src/hooks/after-tool-call.js";
import { createBeforeAgentStartHandler } from "./src/hooks/before-agent-start.js";
import { createPolicyCommand } from "./src/commands/policy.js";

export default function register(api: OpenClawPluginApi): void {
  const logger = api.logger;

  // Resolve and validate configuration
  const config = resolveConfig(api.pluginConfig);
  const engine = new PolicyEngine(config);
  const state = new StateManager();

  logger.info(
    `policy-engine loaded: enabled=${config.enabled} dryRun=${config.dryRun} ` +
    `allowlists=${Object.keys(config.allowlists).length} ` +
    `routing=${Object.keys(config.routing).length}`,
  );

  // Register the main firewall hook (before_tool_call)
  api.on("before_tool_call", createBeforeToolCallHandler({ engine, state, logger }), {
    priority: 10, // run early — before other plugins
  });

  // Register audit hook (after_tool_call)
  api.on("after_tool_call", createAfterToolCallHandler({ config, logger }));

  // Register static routing hook (before_agent_start)
  api.on("before_agent_start", createBeforeAgentStartHandler({ config, logger }));

  // Register /policy slash command
  api.registerCommand(createPolicyCommand({ config, state }));
}
