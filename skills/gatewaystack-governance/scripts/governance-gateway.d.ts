#!/usr/bin/env node
/**
 * GatewayStack Governance Gateway for OpenClaw
 *
 * Barrel module — re-exports the public API and serves as the CLI entry point.
 * Implementation lives in ./governance/*.ts modules.
 */
export type { Policy, GovernanceCheckResult } from "./governance/types.js";
export { loadPolicy } from "./governance/policy.js";
export { validatePolicy } from "./governance/validate-policy.js";
export { checkGovernance } from "./governance/check.js";
export { scanOutput } from "./governance/dlp.js";
export { detectAnomalies, buildBaseline } from "./governance/behavioral.js";
