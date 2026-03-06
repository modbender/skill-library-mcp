/**
 * GatewayStack Governance — OpenClaw Plugin
 *
 * Registers a `before_tool_call` hook that automatically runs governance
 * checks on every tool invocation. The agent cannot bypass this — it runs
 * at the process level before any tool executes.
 *
 * Identity mapping uses OpenClaw agent IDs (e.g. "main", "ops", "dev")
 * rather than human users, since OpenClaw is a single-user personal AI.
 */

import * as path from "path";
import * as os from "os";
import { checkGovernance } from "../scripts/governance-gateway.js";
import { loadPolicy } from "../scripts/governance/policy.js";
import { scanOutput, redactOutput, logDlpScan } from "../scripts/governance/dlp.js";

// Resolve policy path: check plugin directory first, then ~/.openclaw default
function resolvePolicyPath(): string {
  const pluginDir = path.resolve(__dirname, "..");
  const localPolicy = path.join(pluginDir, "policy.json");

  // Also check OpenClaw skills directory (for backward compat with skill installs)
  const openclawSkillPolicy = path.join(
    os.homedir(),
    ".openclaw",
    "skills",
    "gatewaystack-governance",
    "policy.json"
  );

  // Prefer local plugin directory policy
  try {
    require("fs").accessSync(localPolicy);
    return localPolicy;
  } catch {
    // Fall through
  }

  // Try OpenClaw skills directory
  try {
    require("fs").accessSync(openclawSkillPolicy);
    return openclawSkillPolicy;
  } catch {
    // Fall through
  }

  // Default to local — will produce a clear error from checkGovernance
  return localPolicy;
}

const plugin = {
  id: "gatewaystack-governance",
  name: "GatewayStack Governance",
  description:
    "Automatic governance for every tool call — identity, scope, rate limiting, injection detection, audit logging, plus opt-in output DLP, escalation, and behavioral monitoring",

  register(api: any) {
    const policyPath = resolvePolicyPath();

    api.on(
      "before_tool_call",
      async (
        event: { toolName: string; params: Record<string, unknown> },
        ctx: { agentId?: string; sessionKey?: string }
      ) => {
        const result = await checkGovernance({
          toolName: event.toolName,
          args: JSON.stringify(event.params),
          userId: ctx.agentId ?? "unknown",
          session: ctx.sessionKey,
          policyPath,
        });

        if (!result.allowed) {
          return { block: true, blockReason: result.reason };
        }

        // Review verdict is already handled above (allowed: false, block: true)
        // but we set blockReason with the review instructions from formatReviewBlock

        return {};
      },
      { priority: 0 }
    );

    // --- Output DLP hooks ---
    // Cache policy at registration time for DLP hooks (avoids re-reading JSON on every call)
    let cachedPolicy: ReturnType<typeof loadPolicy> | null = null;
    try {
      cachedPolicy = loadPolicy(policyPath);
    } catch {
      // Policy load failure is already handled by before_tool_call
    }

    if (cachedPolicy?.outputDlp?.enabled) {
      const dlpMode = cachedPolicy.outputDlp.mode;

      if (dlpMode === "log") {
        // Log mode: observe output via after_tool_call (cannot modify)
        api.on(
          "after_tool_call",
          async (event: { toolName: string; output?: string }) => {
            if (!event.output || !cachedPolicy) return;
            try {
              const result = scanOutput(event.output, cachedPolicy);
              logDlpScan(result, event.toolName, cachedPolicy);
            } catch {
              // DLP scan failure should not break the agent
            }
          },
          { priority: 100 }
        );
      }

      if (dlpMode === "block") {
        // Block mode: redact output via tool_result_persist
        api.on(
          "tool_result_persist",
          async (event: { toolName: string; output: string }) => {
            if (!event.output || !cachedPolicy) return {};
            try {
              const scanResult = scanOutput(event.output, cachedPolicy);
              logDlpScan(scanResult, event.toolName, cachedPolicy);

              if (scanResult.hasMatches) {
                const redacted = redactOutput(event.output, cachedPolicy);
                return { output: redacted };
              }
            } catch {
              // DLP failure should not break the agent
            }
            return {};
          },
          { priority: 0 }
        );
      }
    }

    if (api.logger) {
      api.logger.info(
        `GatewayStack Governance loaded (policy: ${policyPath})`
      );
    }
  },
};

export default plugin;
