/**
 * /policy slash command — shows current policy engine state.
 */

import type {
  OpenClawPluginCommandDefinition,
  PluginCommandContext,
  PluginCommandResult,
} from "openclaw/plugin-sdk";
import type { PolicyConfig } from "../config.js";
import type { StateManager } from "../state.js";

export function createPolicyCommand(deps: {
  config: PolicyConfig;
  state: StateManager;
}): OpenClawPluginCommandDefinition {
  return {
    name: "policy",
    description: "Show current policy engine status, config, and session stats",
    acceptsArgs: false,
    requireAuth: true,
    handler: (_ctx: PluginCommandContext): PluginCommandResult => {
      const { config, state } = deps;

      const lines: string[] = [
        "## Policy Engine Status",
        "",
        `- **Enabled:** ${config.enabled}`,
        `- **Dry-run:** ${config.dryRun}`,
        `- **Dry-run allow T0:** ${config.dryRunAllowT0}`,
        `- **Max blocked retries:** ${config.maxBlockedRetries}`,
        "",
      ];

      // Allowlists
      const allowlistKeys = Object.keys(config.allowlists);
      if (allowlistKeys.length > 0) {
        lines.push("### Allowlists");
        for (const key of allowlistKeys) {
          const tools = config.allowlists[key];
          lines.push(`- **${key}:** ${tools.join(", ")}`);
        }
        lines.push("");
      }

      // Risk tier overrides
      const tierKeys = Object.keys(config.riskTiers);
      if (tierKeys.length > 0) {
        lines.push("### Risk Tier Overrides");
        for (const key of tierKeys) {
          lines.push(`- ${key}: ${config.riskTiers[key]}`);
        }
        lines.push("");
      }

      // Routing rules
      const routingKeys = Object.keys(config.routing);
      if (routingKeys.length > 0) {
        lines.push("### Routing Rules");
        for (const key of routingKeys) {
          const rule = config.routing[key];
          const parts: string[] = [];
          if (rule.model) parts.push(`model=${rule.model}`);
          if (rule.toolProfile) parts.push(`toolProfile=${rule.toolProfile}`);
          lines.push(`- **${key}:** ${parts.join(", ")}`);
        }
        lines.push("");
      }

      // Session stats
      lines.push("### Session Stats");
      lines.push(`- **Tracked sessions:** ${state.size}`);

      return { text: lines.join("\n") };
    },
  };
}
