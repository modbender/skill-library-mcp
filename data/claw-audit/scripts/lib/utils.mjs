/**
 * Shared utilities for ClawAudit scripts
 */

import { homedir } from "os";
import { join } from "path";

// ANSI Color Codes
export const COLORS = {
  BOLD: "\x1b[1m",
  GREEN: "\x1b[32m",
  YELLOW: "\x1b[33m",
  RED: "\x1b[31m",
  GRAY: "\x1b[90m",
  CYAN: "\x1b[36m",
  RESET: "\x1b[0m",
};

// Config Paths (centralized, consistent)
const HOME = homedir();
export const CONFIG_PATHS = [
  join(HOME, ".openclaw", "openclaw.json"),
  join(HOME, ".openclaw", "config.json"),
  join(HOME, ".clawdbot", "clawdbot.json"),
  join(HOME, ".clawdbot", "config.json"),
];

export const STATE_DIRS = [
  join(HOME, ".openclaw"),
  join(HOME, ".clawdbot"),
];

// CLI Helpers
export function parseFlag(flag) {
  return process.argv.includes(flag);
}

export function outputJSON(data) {
  if (parseFlag("--json")) {
    console.log(JSON.stringify(data, null, 2));
    return true;
  }
  return false;
}

// Finding Utilities
export function createFindingCollector() {
  const findings = [];
  let totalChecks = 0;

  return {
    // mitigated=true: finding exists but a compensating control reduces the real-world risk.
    // calculate-score will apply a reduced point deduction instead of the full weight.
    add(severity, code, title, detail, fix = null, mitigated = false) {
      findings.push({ severity, code, title, detail, fix, ...(mitigated && { mitigated: true }) });
    },
    /** Call once per distinct check/rule that was evaluated (pass or fail). */
    check(n = 1) {
      totalChecks += n;
    },
    getAll() {
      return findings;
    },
    getTotalChecks() {
      return totalChecks;
    },
    getPassed() {
      return Math.max(0, totalChecks - findings.length);
    },
    countBySeverity() {
      return {
        critical: findings.filter(f => f.severity === "critical").length,
        warnings: findings.filter(f => f.severity === "warning").length,
        info: findings.filter(f => f.severity === "info").length,
      };
    },
    sort() {
      const order = { critical: 0, warning: 1, info: 2 };
      findings.sort((a, b) => order[a.severity] - order[b.severity]);
    },
  };
}
