/**
 * Failover status inspection and management.
 *
 * Standalone CLI usage:
 *   npx tsx status.ts                  # pretty-print current status
 *   npx tsx status.ts --json           # machine-readable JSON output
 *   npx tsx status.ts clear <model-id> # clear a single model's rate limit
 *   npx tsx status.ts clear --all      # clear all rate limits
 *
 * Programmatic usage:
 *   import { getFailoverStatus, clearModel, clearAllModels } from "./status.js";
 */

import {
  expandHome,
  loadState,
  saveState,
  nowSec,
  firstAvailableModel,
  DEFAULT_MODEL_ORDER,
  DEFAULT_STATE_FILE,
  type LimitState,
} from "./index.js";

// -------------------------------------------------------------------------
// Types
// -------------------------------------------------------------------------

export interface ModelStatus {
  model: string;
  available: boolean;
  reason?: string;
  lastHitAt?: number;
  nextAvailableAt?: number;
  remainingSeconds?: number;
}

export interface FailoverStatus {
  timestamp: number;
  statePath: string;
  models: ModelStatus[];
  activeModel: string | undefined;
  blockedCount: number;
  availableCount: number;
}

// -------------------------------------------------------------------------
// Core functions
// -------------------------------------------------------------------------

/**
 * Build a structured snapshot of the current failover state.
 */
export function getFailoverStatus(opts?: {
  statePath?: string;
  modelOrder?: string[];
}): FailoverStatus {
  const resolvedPath = expandHome(opts?.statePath ?? DEFAULT_STATE_FILE);
  const modelOrder = opts?.modelOrder ?? DEFAULT_MODEL_ORDER;
  const state = loadState(resolvedPath);
  const now = nowSec();

  const seen = new Set<string>();
  const models: ModelStatus[] = [];

  // Models in the configured order first.
  for (const model of modelOrder) {
    seen.add(model);
    const lim = state.limited[model];
    const isLimited = !!lim && lim.nextAvailableAt > now;
    models.push({
      model,
      available: !isLimited,
      reason: isLimited ? lim.reason : undefined,
      lastHitAt: lim?.lastHitAt,
      nextAvailableAt: isLimited ? lim.nextAvailableAt : undefined,
      remainingSeconds: isLimited ? lim.nextAvailableAt - now : undefined,
    });
  }

  // Models in the state file that are not in the configured order (stale entries).
  for (const [model, lim] of Object.entries(state.limited)) {
    if (seen.has(model)) continue;
    const isLimited = lim.nextAvailableAt > now;
    models.push({
      model,
      available: !isLimited,
      reason: isLimited ? lim.reason : undefined,
      lastHitAt: lim.lastHitAt,
      nextAvailableAt: isLimited ? lim.nextAvailableAt : undefined,
      remainingSeconds: isLimited ? lim.nextAvailableAt - now : undefined,
    });
  }

  const activeModel = firstAvailableModel(modelOrder, state);
  const blockedCount = models.filter((m) => !m.available).length;
  const availableCount = models.filter((m) => m.available).length;

  return {
    timestamp: now,
    statePath: resolvedPath,
    models,
    activeModel,
    blockedCount,
    availableCount,
  };
}

/**
 * Remove the rate-limit entry for a single model. Returns true if an entry existed.
 */
export function clearModel(
  model: string,
  statePath?: string,
): boolean {
  const resolved = expandHome(statePath ?? DEFAULT_STATE_FILE);
  const state = loadState(resolved);
  if (!(model in state.limited)) return false;
  delete state.limited[model];
  saveState(resolved, state);
  return true;
}

/**
 * Remove all rate-limit entries. Returns the number of entries cleared.
 */
export function clearAllModels(statePath?: string): number {
  const resolved = expandHome(statePath ?? DEFAULT_STATE_FILE);
  const state = loadState(resolved);
  const count = Object.keys(state.limited).length;
  if (count === 0) return 0;
  state.limited = {};
  saveState(resolved, state);
  return count;
}

// -------------------------------------------------------------------------
// Formatting helpers
// -------------------------------------------------------------------------

/**
 * Format seconds into a compact human-readable string (e.g. "2h 15m").
 */
export function formatDuration(seconds: number): string {
  if (seconds <= 0) return "now";
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  const s = seconds % 60;
  const parts: string[] = [];
  if (h > 0) parts.push(`${h}h`);
  if (m > 0) parts.push(`${m}m`);
  if (s > 0 && h === 0) parts.push(`${s}s`);
  return parts.join(" ") || "now";
}

/**
 * Pretty-print a FailoverStatus object for terminal output.
 */
export function formatStatus(status: FailoverStatus): string {
  const lines: string[] = [];

  lines.push("=== OpenClaw Model Failover Status ===");
  lines.push("");
  lines.push(`Active model : ${status.activeModel ?? "(none)"}`);
  lines.push(`Models       : ${status.availableCount} available, ${status.blockedCount} blocked`);
  lines.push(`State file   : ${status.statePath}`);

  if (status.blockedCount > 0) {
    lines.push("");
    lines.push("Blocked models:");
    for (const m of status.models) {
      if (!m.available) {
        const remaining = formatDuration(m.remainingSeconds ?? 0);
        const availAt = new Date((m.nextAvailableAt ?? 0) * 1000).toISOString();
        lines.push(`  - ${m.model}`);
        lines.push(`    Reason      : ${m.reason ?? "unknown"}`);
        lines.push(`    Available in: ${remaining} (${availAt})`);
      }
    }
  }

  lines.push("");
  lines.push("Model order:");
  for (const m of status.models) {
    const marker = m.available ? "OK" : "BLOCKED";
    lines.push(`  [${marker.padEnd(7)}] ${m.model}`);
  }

  return lines.join("\n");
}

// -------------------------------------------------------------------------
// CLI entry point
// -------------------------------------------------------------------------

const isDirectRun =
  typeof process !== "undefined" &&
  process.argv[1] &&
  (process.argv[1].endsWith("status.ts") || process.argv[1].endsWith("status.js"));

if (isDirectRun) {
  const args = process.argv.slice(2);

  if (args[0] === "clear") {
    const target = args[1];
    if (target === "--all") {
      const count = clearAllModels();
      console.log(`Cleared ${count} rate-limit ${count === 1 ? "entry" : "entries"}.`);
    } else if (target) {
      const ok = clearModel(target);
      console.log(
        ok
          ? `Cleared rate limit for ${target}.`
          : `No rate-limit entry found for ${target}.`,
      );
    } else {
      console.log("Usage: npx tsx status.ts clear <model-id> | --all");
      process.exit(1);
    }
  } else if (args[0] === "--json") {
    const status = getFailoverStatus();
    console.log(JSON.stringify(status, null, 2));
  } else if (args[0] === "--help" || args[0] === "-h") {
    console.log(
      [
        "Usage: npx tsx status.ts [command] [options]",
        "",
        "Commands:",
        "  (default)             Pretty-print current failover status",
        "  --json                Output status as JSON",
        "  clear <model-id>     Clear rate limit for a specific model",
        "  clear --all           Clear all rate-limit entries",
        "  --help, -h            Show this help message",
      ].join("\n"),
    );
  } else {
    const status = getFailoverStatus();
    console.log(formatStatus(status));
  }
}
