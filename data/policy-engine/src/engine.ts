/**
 * PolicyEngine — pure-logic decision engine for tool call governance.
 *
 * Evaluates a tool call against the configured policy rules and returns
 * an allow/block/dry-run decision. Stateless per call; session state is
 * managed externally by the StateManager.
 */

import type { PolicyConfig, RiskTier } from "./config.js";
import { getToolTier, isT0 } from "./tiers.js";
import { matchDenyPatterns, checkPathAllowlist } from "./patterns.js";

export type PolicyDecision = {
  action: "allow" | "block" | "dryrun";
  reason?: string;
  tier: RiskTier;
  remediation?: string;
};

export type EvaluateInput = {
  toolName: string;
  params: Record<string, unknown>;
  agentId?: string;
  sessionKey?: string;
  /** Current blocked count for this session (for escalation check). */
  blockedCount?: number;
};

export class PolicyEngine {
  constructor(private config: PolicyConfig) {}

  /**
   * Update the engine's config at runtime (e.g. after hot-reload).
   */
  updateConfig(config: PolicyConfig): void {
    this.config = config;
  }

  /**
   * Evaluate a tool call against the full policy chain.
   *
   * Order of evaluation:
   * 1. Global kill-switch (enabled=false → allow everything)
   * 2. Dry-run mode
   * 3. Denylist / deny patterns
   * 4. Allowlist enforcement
   * 5. Retry escalation check
   * 6. Allow
   */
  evaluate(input: EvaluateInput): PolicyDecision {
    const { toolName, params, agentId, blockedCount } = input;
    const name = toolName.toLowerCase();
    const tier = getToolTier(name, this.config.riskTiers);

    // 1. Global kill-switch: disabled → pass everything through
    if (!this.config.enabled) {
      return { action: "allow", tier };
    }

    // 2. Dry-run mode
    if (this.config.dryRun) {
      // Essential tools ALWAYS pass — control plane must never be blocked.
      // Without this, dry-run creates an unrecoverable deadlock: the agent
      // cannot communicate, patch config, or disable dry-run.
      if (this.isEssentialTool(name)) {
        return { action: "allow", tier, reason: "Essential tool allowed in dry-run mode" };
      }
      if (this.config.dryRunAllowT0 && isT0(name, this.config.riskTiers)) {
        return { action: "allow", tier, reason: "T0 tool allowed in dry-run mode" };
      }
      return {
        action: "dryrun",
        tier,
        reason: "Blocked by policy engine dry-run mode",
      };
    }

    // 3. Deny patterns — check before anything else so dangerous calls
    //    are always caught, even for essential tools.
    const patternResult = matchDenyPatterns(name, params, this.config.denyPatterns);
    if (patternResult.matched) {
      return {
        action: "block",
        tier,
        reason: `Blocked: argument matches deny pattern "${patternResult.pattern}"`,
        remediation: "Remove the dangerous argument pattern and try again.",
      };
    }

    // 3b. Path allowlist enforcement — canonicalize + check write targets
    const pathResult = checkPathAllowlist(name, params, this.config.pathAllowlists);
    if (pathResult.blocked) {
      return {
        action: "block",
        tier,
        reason: pathResult.reason,
        remediation: "The target path is outside allowed directories. Use an allowed path instead.",
      };
    }

    // 4. Essential tool + T0 early exit — bypass allowlist and escalation.
    //    Control-plane tools (message, gateway, session_status, etc.) and
    //    read-only T0 tools must NEVER be blocked by allowlists or escalation
    //    counters. Without this, the agent bricks itself when it hits
    //    maxBlockedRetries — same deadlock class as the dry-run issue.
    //    Deny patterns (step 3) still apply to prevent abuse.
    if (this.isEssentialTool(name) || isT0(name, this.config.riskTiers)) {
      return { action: "allow", tier, reason: "Essential/T0 tool — always allowed" };
    }

    // 5. Allowlist enforcement
    const allowlistResult = this.checkAllowlist(name, agentId);
    if (allowlistResult) {
      return { ...allowlistResult, tier };
    }

    // 6. Retry escalation check
    if (
      typeof blockedCount === "number" &&
      blockedCount >= this.config.maxBlockedRetries
    ) {
      return {
        action: "block",
        tier,
        reason: `Session has exceeded the maximum blocked retries (${this.config.maxBlockedRetries}). Escalation required.`,
        remediation:
          "Too many blocked attempts in this session. Ask the user for explicit authorization or change your approach.",
      };
    }

    // 6. Default: allow
    return { action: "allow", tier };
  }

  /**
   * Check if a tool is in the essential tools list.
   * Essential tools are control-plane tools that must always work,
   * even in dry-run mode, to prevent system deadlocks.
   */
  private isEssentialTool(toolName: string): boolean {
    const essentials = new Set(
      this.config.dryRunEssentialTools.map((t) => t.toLowerCase()),
    );
    return essentials.has(toolName);
  }

  /**
   * Check if a tool is permitted by allowlist rules.
   * Returns a block decision if denied, or undefined if allowed.
   */
  private checkAllowlist(
    toolName: string,
    agentId?: string,
  ): Omit<PolicyDecision, "tier"> | undefined {
    // Find the applicable allowlist profile
    const profileName = this.resolveAllowlistProfile(agentId);
    if (!profileName) {
      return undefined; // no allowlist configured → allow all
    }

    const allowedTools = this.config.allowlists[profileName];
    if (!allowedTools || allowedTools.length === 0) {
      return undefined; // empty allowlist → allow all
    }

    const normalizedAllowed = new Set(allowedTools.map((t) => t.toLowerCase()));
    if (!normalizedAllowed.has(toolName)) {
      return {
        action: "block",
        reason: `Tool "${toolName}" is not in the "${profileName}" allowlist.`,
        remediation: `Only these tools are allowed: ${allowedTools.join(", ")}. Use one of those instead.`,
      };
    }

    return undefined;
  }

  /**
   * Determine which allowlist profile applies for a given agent.
   * Checks routing rules first, then falls back to a "default" allowlist if one exists.
   */
  private resolveAllowlistProfile(agentId?: string): string | undefined {
    if (agentId) {
      const rule = this.config.routing[agentId];
      if (rule?.toolProfile && this.config.allowlists[rule.toolProfile]) {
        return rule.toolProfile;
      }
    }

    // Fall back to "default" allowlist if one is configured
    if (this.config.allowlists["default"]) {
      return "default";
    }

    return undefined;
  }

  /**
   * Build a dry-run stub result for a blocked tool call.
   */
  buildDryRunStub(
    toolName: string,
    params: Record<string, unknown>,
  ): Record<string, unknown> {
    const paramSummary = Object.keys(params).length > 0
      ? Object.keys(params).join(", ")
      : "(none)";

    return {
      dryRun: true,
      tool: toolName,
      params: paramSummary,
      note: "Blocked by policy engine dry-run mode",
    };
  }
}
