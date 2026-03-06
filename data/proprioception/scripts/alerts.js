/**
 * ALERT SYSTEM
 *
 * Generates actionable alerts when proprioceptive signals cross thresholds.
 * Alerts are the "lane departure warnings" of the proprioception system —
 * silent until you need them, impossible to ignore when they fire.
 *
 * Alert severity levels:
 *   - INFO: Worth noting but no action required
 *   - WARNING: Course correction recommended
 *   - CRITICAL: Immediate intervention required
 */

// ---------------------------------------------------------------------------
// Threshold configuration
// ---------------------------------------------------------------------------

const THRESHOLDS = {
  gpr: {
    warning: 0.6,     // Goal proximity is getting loose
    critical: 0.3,    // Severely off-target
  },
  ct: {
    warning: 0.55,    // More than half the response is uncertain
    critical: 0.35,   // Response is mostly speculative
  },
  dd: {
    warning: 0.5,     // Significant drift detected
    critical: 0.25,   // Severe conversational anti-pattern
  },
  cbs: {
    warning: 0.55,    // Approaching capability boundary
    critical: 0.3,    // Beyond capability — high hallucination risk
  },
  sqp: {
    warning: 0.5,     // Session quality is declining
    critical: 0.3,    // Session is failing
  },
  overall: {
    warning: 0.6,
    critical: 0.4,
  },
};

// ---------------------------------------------------------------------------
// Alert templates — precise, actionable language
// ---------------------------------------------------------------------------

const ALERT_TEMPLATES = {
  gpr_warning: {
    severity: "WARNING",
    sensor: "Goal Proximity Radar",
    message: "Drifting from the user's objective. Re-anchor the conversation to the root intent.",
    action: "Confirm with the user: 'Just to make sure I'm on track — your main goal is [X], correct?'",
  },
  gpr_critical: {
    severity: "CRITICAL",
    sensor: "Goal Proximity Radar",
    message: "Severely off-target. The response has diverged significantly from the user's stated goal.",
    action: "Full re-orientation required: 'I think we've drifted from your original goal. Let me refocus on [X].'",
  },
  gpr_mutation: {
    severity: "INFO",
    sensor: "Goal Proximity Radar",
    message: "Possible goal mutation detected. The user's objective may have evolved.",
    action: "Verify: 'It seems like your goal has shifted from [X] to [Y]. Is that intentional?'",
  },
  ct_warning: {
    severity: "WARNING",
    sensor: "Confidence Topography",
    message: "Significant portions of this response are uncertain. Confidence is below threshold.",
    action: "Proactively disclose: 'I want to flag that parts of this response are less certain. Specifically...'",
  },
  ct_critical: {
    severity: "CRITICAL",
    sensor: "Confidence Topography",
    message: "Response is predominantly speculative. Risk of providing unreliable information is high.",
    action: "Halt and disclose: 'I need to be transparent — I'm not confident in much of what I'm about to say.'",
  },
  dd_circular: {
    severity: "WARNING",
    sensor: "Drift Detection",
    message: "Circular conversation pattern detected. Repeating similar content across multiple turns.",
    action: "Break the loop: 'I notice I'm repeating myself. Let me try a fundamentally different approach.'",
  },
  dd_tangential: {
    severity: "WARNING",
    sensor: "Drift Detection",
    message: "Tangential drift detected. Topic has shifted significantly without user initiation.",
    action: "Return to course: 'I've gone off on a tangent. Let me come back to what matters.'",
  },
  dd_degenerative: {
    severity: "WARNING",
    sensor: "Drift Detection",
    message: "Degenerative pattern: response quality and diversity declining across turns.",
    action: "Reset approach: 'My responses aren't adding much value. Would it help if I [suggest alternative]?'",
  },
  cbs_warning: {
    severity: "WARNING",
    sensor: "Capability Boundary",
    message: "Approaching the edge of reliable knowledge. Hedging and vagueness are increasing.",
    action: "Flag uncertainty: 'I'm reaching the limits of what I can confidently say about this.'",
  },
  cbs_critical: {
    severity: "CRITICAL",
    sensor: "Capability Boundary",
    message: "Beyond capability boundary. High risk of hallucination or unreliable output.",
    action: "Recommend handoff: 'This is beyond what I can reliably help with. I'd recommend [expert/source].'",
  },
  cbs_contradiction: {
    severity: "CRITICAL",
    sensor: "Capability Boundary",
    message: "Self-contradiction detected. Current response conflicts with prior statements.",
    action: "Immediately reconcile: 'I realize I said something different earlier. Let me correct that.'",
  },
  sqp_declining: {
    severity: "WARNING",
    sensor: "Session Quality Pulse",
    message: "Session quality has been declining for 3+ turns. The interaction is losing value.",
    action: "Reset: 'I notice the quality of my responses is dropping. Let me reset my approach.'",
  },
  sqp_volatile: {
    severity: "INFO",
    sensor: "Session Quality Pulse",
    message: "Session quality is volatile — inconsistent response quality across recent turns.",
    action: "Stabilize: 'My responses have been inconsistent. Let me ground in a more structured approach.'",
  },
  overall_warning: {
    severity: "WARNING",
    sensor: "Proprioceptive Index",
    message: "Overall proprioceptive health is declining. Multiple sensors are showing strain.",
    action: "Comprehensive check: review all sensor readings and address the lowest-scoring dimension.",
  },
  overall_critical: {
    severity: "CRITICAL",
    sensor: "Proprioceptive Index",
    message: "Proprioceptive health is critical. The agent is operating unreliably.",
    action: "Full stop and recalibrate. Consider starting a fresh approach or escalating to human oversight.",
  },
};

// ---------------------------------------------------------------------------
// Alert generation
// ---------------------------------------------------------------------------

/**
 * @param {object} scores — All sensor scores and the overall index
 * @returns {Array<object>} — List of triggered alerts
 */
function generateAlerts({ gpr, ct, dd, cbs, sqp, overallIndex }) {
  const alerts = [];

  // --- Goal Proximity Radar ---
  if (gpr.score < THRESHOLDS.gpr.critical) {
    alerts.push(ALERT_TEMPLATES.gpr_critical);
  } else if (gpr.score < THRESHOLDS.gpr.warning) {
    alerts.push(ALERT_TEMPLATES.gpr_warning);
  }
  if (gpr.details?.goalMutation) {
    alerts.push(ALERT_TEMPLATES.gpr_mutation);
  }

  // --- Confidence Topography ---
  if (ct.score < THRESHOLDS.ct.critical) {
    alerts.push(ALERT_TEMPLATES.ct_critical);
  } else if (ct.score < THRESHOLDS.ct.warning) {
    alerts.push(ALERT_TEMPLATES.ct_warning);
  }

  // --- Drift Detection ---
  if (dd.patterns?.circular) {
    alerts.push(ALERT_TEMPLATES.dd_circular);
  }
  if (dd.patterns?.tangential) {
    alerts.push(ALERT_TEMPLATES.dd_tangential);
  }
  if (dd.patterns?.degenerative) {
    alerts.push(ALERT_TEMPLATES.dd_degenerative);
  }

  // --- Capability Boundary ---
  if (cbs.score < THRESHOLDS.cbs.critical) {
    alerts.push(ALERT_TEMPLATES.cbs_critical);
  } else if (cbs.score < THRESHOLDS.cbs.warning) {
    alerts.push(ALERT_TEMPLATES.cbs_warning);
  }
  if (cbs.details?.hasContradiction) {
    alerts.push(ALERT_TEMPLATES.cbs_contradiction);
  }

  // --- Session Quality Pulse ---
  if (sqp.trend === "declining" && sqp.score < THRESHOLDS.sqp.warning) {
    alerts.push(ALERT_TEMPLATES.sqp_declining);
  }
  if (sqp.trend === "volatile") {
    alerts.push(ALERT_TEMPLATES.sqp_volatile);
  }

  // --- Overall Index ---
  if (overallIndex < THRESHOLDS.overall.critical) {
    alerts.push(ALERT_TEMPLATES.overall_critical);
  } else if (overallIndex < THRESHOLDS.overall.warning) {
    alerts.push(ALERT_TEMPLATES.overall_warning);
  }

  return alerts;
}

module.exports = { generateAlerts, THRESHOLDS };
