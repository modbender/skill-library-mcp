#!/usr/bin/env node

/**
 * PROPRIOCEPTION ENGINE
 * Self-Spatial Awareness for AI Agents
 *
 * The sixth sense every AI agent is missing.
 * Zero external API calls. Zero databases. Pure local computation.
 *
 * Runs five proprioceptive analyses on each conversation turn:
 *   1. Goal Proximity Radar (GPR)
 *   2. Confidence Topography (CT)
 *   3. Drift Detection (DD)
 *   4. Capability Boundary Sensing (CBS)
 *   5. Session Quality Pulse (SQP)
 */

const { parseArgs } = require("node:util");
const {
  computeGoalProximity,
} = require("./sensors/goal-proximity-radar");
const {
  computeConfidenceTopography,
} = require("./sensors/confidence-topography");
const {
  computeDriftDetection,
} = require("./sensors/drift-detection");
const {
  computeCapabilityBoundary,
} = require("./sensors/capability-boundary");
const {
  computeSessionQuality,
} = require("./sensors/session-quality-pulse");
const { generateAlerts } = require("./alerts");
const { renderDashboard } = require("./dashboard");

// ---------------------------------------------------------------------------
// CLI argument parsing
// ---------------------------------------------------------------------------

const options = {
  "root-intent": { type: "string" },
  "current-response": { type: "string" },
  "turn-number": { type: "string" },
  "prior-signals": { type: "string" },
  dashboard: { type: "boolean", default: false },
};

let args;
try {
  args = parseArgs({ options, allowPositionals: false }).values;
} catch {
  console.error(
    "Usage: proprioception-engine.js --root-intent <text> --current-response <text> --turn-number <n> [--prior-signals <json>] [--dashboard]"
  );
  process.exit(1);
}

const rootIntent = args["root-intent"] || "";
const currentResponse = args["current-response"] || "";
const turnNumber = parseInt(args["turn-number"] || "1", 10);
const priorSignals = args["prior-signals"]
  ? JSON.parse(args["prior-signals"])
  : [];
const showDashboard = args.dashboard || false;

// ---------------------------------------------------------------------------
// Run all five proprioceptive sensors
// ---------------------------------------------------------------------------

const gpr = computeGoalProximity(rootIntent, currentResponse, priorSignals);
const ct = computeConfidenceTopography(currentResponse);
const dd = computeDriftDetection(currentResponse, priorSignals, turnNumber);
const cbs = computeCapabilityBoundary(currentResponse, priorSignals);
const sqp = computeSessionQuality(currentResponse, priorSignals, turnNumber);

// ---------------------------------------------------------------------------
// Compute the overall Proprioceptive Index (PI)
// Weighted average — CBS gets extra weight because hallucination is the
// highest-stakes failure mode for AI agents.
// ---------------------------------------------------------------------------

const weights = { gpr: 0.20, ct: 0.20, dd: 0.15, cbs: 0.25, sqp: 0.20 };

const overallIndex =
  gpr.score * weights.gpr +
  ct.score * weights.ct +
  dd.score * weights.dd +
  cbs.score * weights.cbs +
  sqp.score * weights.sqp;

const status =
  overallIndex >= 0.8
    ? "HEALTHY"
    : overallIndex >= 0.6
      ? "CAUTION"
      : overallIndex >= 0.4
        ? "WARNING"
        : "CRITICAL";

// ---------------------------------------------------------------------------
// Generate alerts for any threshold breaches
// ---------------------------------------------------------------------------

const alerts = generateAlerts({ gpr, ct, dd, cbs, sqp, overallIndex });

// ---------------------------------------------------------------------------
// Assemble output
// ---------------------------------------------------------------------------

const output = {
  turn: turnNumber,
  timestamp: new Date().toISOString(),
  sensors: {
    goalProximityRadar: gpr,
    confidenceTopography: ct,
    driftDetection: dd,
    capabilityBoundary: cbs,
    sessionQualityPulse: sqp,
  },
  overallIndex: Math.round(overallIndex * 100) / 100,
  status,
  alerts,
  annotation: `[P: GPR=${gpr.score.toFixed(2)} | CT=${ct.score.toFixed(2)} | DD=${dd.score.toFixed(2)} | CBS=${cbs.score.toFixed(2)} | SQP=${sqp.score.toFixed(2)}]`,
};

if (showDashboard) {
  console.log(renderDashboard(output));
} else {
  console.log(JSON.stringify(output, null, 2));
}
