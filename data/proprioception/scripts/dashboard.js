/**
 * PROPRIOCEPTION DASHBOARD
 *
 * Renders a visual dashboard showing all five proprioceptive senses
 * and any active alerts. ASCII art that works in any terminal.
 */

// ---------------------------------------------------------------------------
// Bar rendering
// ---------------------------------------------------------------------------

function renderBar(score, width = 10) {
  const filled = Math.round(score * width);
  const empty = width - filled;
  return "\u2588".repeat(filled) + "\u2591".repeat(empty);
}

function statusColor(score) {
  if (score >= 0.8) return "OK";
  if (score >= 0.6) return "~~";
  if (score >= 0.4) return "!!";
  return "XX";
}

// ---------------------------------------------------------------------------
// Main dashboard renderer
// ---------------------------------------------------------------------------

/**
 * @param {object} output — Full proprioception engine output
 * @returns {string} — Formatted dashboard string
 */
function renderDashboard(output) {
  const { sensors, overallIndex, status, alerts, turn } = output;

  const gpr = sensors.goalProximityRadar;
  const ct = sensors.confidenceTopography;
  const dd = sensors.driftDetection;
  const cbs = sensors.capabilityBoundary;
  const sqp = sensors.sessionQualityPulse;

  const w = 55;
  const hr = "\u2500".repeat(w);
  const dhr = "\u2550".repeat(w);

  let lines = [];

  // Header
  lines.push("\u250C" + hr + "\u2510");
  lines.push("\u2502" + centerText("PROPRIOCEPTION DASHBOARD", w) + "\u2502");
  lines.push("\u2502" + centerText(`Turn ${turn} | ${output.timestamp}`, w) + "\u2502");
  lines.push("\u251C" + hr + "\u2524");

  // Sensor readings
  lines.push(sensorLine("Goal Proximity Radar", gpr.score, gpr.drift, w));
  lines.push(sensorLine("Confidence Topography", ct.score, topZone(ct.zones), w));
  lines.push(sensorLine("Drift Detection", dd.score, dd.arcPhase, w));
  lines.push(sensorLine("Capability Boundary", cbs.score, cbs.boundaryDistance, w));
  lines.push(sensorLine("Session Quality Pulse", sqp.score, sqp.trend, w));

  // Overall
  lines.push("\u251C" + hr + "\u2524");
  lines.push(
    "\u2502" +
      padRight(
        `  Overall Proprioceptive Index:  ${renderBar(overallIndex)}  ${overallIndex.toFixed(2)}`,
        w
      ) +
      "\u2502"
  );
  lines.push(
    "\u2502" +
      padRight(`  Status: ${status}`, w) +
      "\u2502"
  );

  // Alerts
  if (alerts.length > 0) {
    lines.push("\u251C" + hr + "\u2524");
    lines.push("\u2502" + centerText("ALERTS", w) + "\u2502");
    lines.push("\u251C" + hr + "\u2524");

    for (const alert of alerts) {
      const prefix = alert.severity === "CRITICAL" ? "[!!]" : alert.severity === "WARNING" ? "[~~]" : "[ii]";
      const line = `  ${prefix} ${alert.sensor}: ${alert.message}`;
      // Wrap long lines
      const wrapped = wrapText(line, w - 2);
      for (const wl of wrapped) {
        lines.push("\u2502" + padRight("  " + wl, w) + "\u2502");
      }
      // Action
      const actionWrapped = wrapText(`     -> ${alert.action}`, w - 2);
      for (const al of actionWrapped) {
        lines.push("\u2502" + padRight("  " + al, w) + "\u2502");
      }
    }
  } else {
    lines.push("\u251C" + hr + "\u2524");
    lines.push("\u2502" + padRight("  Alerts: None", w) + "\u2502");
  }

  // Annotation shorthand
  lines.push("\u251C" + hr + "\u2524");
  lines.push("\u2502" + padRight(`  ${output.annotation}`, w) + "\u2502");

  // Footer
  lines.push("\u2514" + hr + "\u2518");

  return lines.join("\n");
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function sensorLine(name, score, detail, w) {
  const bar = renderBar(score);
  const scoreStr = score.toFixed(2);
  const content = `  ${padRight(name, 26)} ${bar}  ${scoreStr}  ${detail}`;
  return "\u2502" + padRight(content, w) + "\u2502";
}

function centerText(text, width) {
  const padding = Math.max(0, width - text.length);
  const left = Math.floor(padding / 2);
  const right = padding - left;
  return " ".repeat(left) + text + " ".repeat(right);
}

function padRight(text, width) {
  if (text.length >= width) return text.slice(0, width);
  return text + " ".repeat(width - text.length);
}

function topZone(zones) {
  if (!zones) return "";
  const entries = Object.entries(zones).sort((a, b) => b[1] - a[1]);
  if (entries.length === 0) return "";
  return entries[0][0].replace("_", " ");
}

function wrapText(text, maxWidth) {
  if (text.length <= maxWidth) return [text];
  const words = text.split(" ");
  const lines = [];
  let current = "";
  for (const word of words) {
    if (current.length + word.length + 1 > maxWidth) {
      lines.push(current);
      current = word;
    } else {
      current = current ? current + " " + word : word;
    }
  }
  if (current) lines.push(current);
  return lines;
}

module.exports = { renderDashboard };
