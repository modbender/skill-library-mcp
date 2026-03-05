/**
 * Risk tier definitions and default mappings.
 *
 * T0 = Safe / read-only
 * T1 = Moderate / writes
 * T2 = Dangerous / exec + delete
 */

import type { RiskTier } from "./config.js";

const DEFAULT_TIER_MAP: Record<string, RiskTier> = {
  // T0 — Safe / read-only
  read: "T0",
  memory_search: "T0",
  memory_get: "T0",
  web_fetch: "T0",
  image: "T0",
  session_status: "T0",
  sessions_list: "T0",
  agents_list: "T0",

  // T1 — Moderate / writes
  write: "T1",
  edit: "T1",
  apply_patch: "T1",
  message: "T1",
  tts: "T1",
  cron: "T1",
  sessions_send: "T1",
  sessions_spawn: "T1",
  browser: "T1",
  canvas: "T1",
  nodes: "T1",

  // T2 — Dangerous / exec + delete
  exec: "T2",
  process: "T2",
  gateway: "T2",
};

/**
 * Resolve the risk tier for a tool, consulting user overrides first,
 * then falling back to defaults. Unknown tools default to T1.
 */
export function getToolTier(
  toolName: string,
  overrides: Record<string, RiskTier>,
): RiskTier {
  const name = toolName.toLowerCase();
  if (overrides[name]) {
    return overrides[name];
  }
  return DEFAULT_TIER_MAP[name] ?? "T1";
}

export function isT0(toolName: string, overrides: Record<string, RiskTier>): boolean {
  return getToolTier(toolName, overrides) === "T0";
}
