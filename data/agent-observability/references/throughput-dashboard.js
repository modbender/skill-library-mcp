'use strict';
/**
 * throughput-dashboard.js
 *
 * Weekly productivity dashboard for OpenClaw agents.
 * Aggregates: session volume, cost, quality ratio, routing distribution, drift score.
 *
 * Installation: copy to $OPENCLAW_WORKSPACE/scripts/throughput-dashboard.js
 *
 * Usage (CLI):
 *   node scripts/throughput-dashboard.js [workspaceRoot]
 *
 * Usage (cron/heartbeat):
 *   node "$WORKSPACE/scripts/throughput-dashboard.js" "$WORKSPACE"
 *
 * Output: memory/dashboards/YYYY-MM-DD.md
 *
 * Node.js stdlib only. Degrades gracefully if data sources are missing.
 * @module scripts/throughput-dashboard
 */

const fs   = require('fs');
const path = require('path');

// ── Helpers ───────────────────────────────────────────────────────────────────

function todayDate()       { return new Date().toISOString().slice(0, 10); }
function usd(n)            { return '$' + (typeof n === 'number' ? n.toFixed(2) : '0.00'); }
function pct(n)            { return (typeof n !== 'number' || isNaN(n)) ? 'N/A' : (n * 100).toFixed(1) + '%'; }
function safeRequire(p)    { try { return require(p); } catch (_) { return null; } }

function readJsonl(filePath) {
  try {
    return fs.readFileSync(filePath, 'utf8')
      .split('\n')
      .filter(l => l.trim().length > 0)
      .map(l => { try { return JSON.parse(l); } catch (_) { return null; } })
      .filter(Boolean);
  } catch (_) { return []; }
}

function atomicWrite(targetPath, content) {
  const tmp = targetPath + '.tmp.' + process.pid;
  fs.writeFileSync(tmp, content, 'utf8');
  fs.renameSync(tmp, targetPath);
}

function daysAgoDate(n) {
  const d = new Date();
  d.setDate(d.getDate() - n);
  return d.toISOString().slice(0, 10);
}

// ── Data collectors ───────────────────────────────────────────────────────────

function collectSessionSummary(workspaceRoot) {
  const metricsPath = path.join(workspaceRoot, 'scripts', 'session-metrics.js');
  const mod = safeRequire(metricsPath);
  if (!mod || typeof mod.getWeeklySummary !== 'function') {
    return { total_tasks: 0, total_cost: 0, avg_cost_per_task: 0, total_subagents: 0, quality_ratio: 1.0, sessions: 0 };
  }
  try { return mod.getWeeklySummary(workspaceRoot); }
  catch (_) { return { total_tasks: 0, total_cost: 0, avg_cost_per_task: 0, total_subagents: 0, quality_ratio: 1.0, sessions: 0 }; }
}

function collectRoutingStats(workspaceRoot) {
  const metricsPath = path.join(workspaceRoot, 'scripts', 'session-metrics.js');
  const mod = safeRequire(metricsPath);
  if (!mod || typeof mod.getRoutingStats !== 'function') {
    return { total_decisions: 0, by_target: { core: 0, specialist: 0, escalate: 0 }, by_type: {} };
  }
  try { return mod.getRoutingStats(workspaceRoot); }
  catch (_) { return { total_decisions: 0, by_target: { core: 0, specialist: 0, escalate: 0 }, by_type: {} }; }
}

function collectDriftReport(workspaceRoot) {
  const driftPath = path.join(workspaceRoot, 'scripts', 'drift-guard-auto.js');
  const mod = safeRequire(driftPath);
  if (!mod || typeof mod.getLatestReport !== 'function') return null;
  try { return mod.getLatestReport(workspaceRoot); } catch (_) { return null; }
}

function parseDriftSummary(reportContent) {
  if (!reportContent) return { pass_rate: 'N/A', common_flags: [] };

  const passMatch  = reportContent.match(/\*\*Pass rate:\*\*\s*([\d.]+%)/);
  const pass_rate  = passMatch ? passMatch[1] : 'N/A';

  const flagSection = reportContent.match(/## Flag Frequency\n([\s\S]*?)(?:\n##|$)/);
  const common_flags = [];
  if (flagSection) {
    const lines = flagSection[1].trim().split('\n');
    for (const line of lines.slice(0, 3)) {
      const clean = line.replace(/^-\s*/, '').trim();
      if (clean && clean !== 'No flags — clean audit.') common_flags.push(clean);
    }
  }
  return { pass_rate, common_flags };
}

function collectPublishStats(workspaceRoot) {
  const analyticsPath = path.join(workspaceRoot, 'memory', 'clawhub-analytics.jsonl');
  try { fs.accessSync(analyticsPath, fs.constants.R_OK); } catch (_) { return null; }

  const cutoff  = daysAgoDate(7);
  const entries = readJsonl(analyticsPath).filter(e => (e.date || e.ts || '').slice(0, 10) >= cutoff);
  if (entries.length === 0) return null;

  let skills_live = 0, downloads_7d = 0;
  for (const e of entries) {
    if (typeof e.downloads === 'number')   downloads_7d += e.downloads;
    if (typeof e.skills_live === 'number') skills_live   = Math.max(skills_live, e.skills_live);
    if (e.status === 'live')               skills_live   = Math.max(skills_live, 1);
  }
  return { skills_live, downloads_7d };
}

// ── Primary export ─────────────────────────────────────────────────────────────

/**
 * Generate the weekly throughput dashboard as a markdown string.
 *
 * @param {string} workspaceRoot - Absolute path to workspace root
 * @returns {string} Formatted markdown
 */
function generateDashboard(workspaceRoot) {
  const today   = todayDate();
  const summary = collectSessionSummary(workspaceRoot);
  const routing = collectRoutingStats(workspaceRoot);
  const drift   = parseDriftSummary(collectDriftReport(workspaceRoot));
  const publish = collectPublishStats(workspaceRoot);

  const total_r = routing.total_decisions || 0;
  const core_n  = routing.by_target.core       || 0;
  const spec_n  = routing.by_target.specialist || 0;
  const esc_n   = routing.by_target.escalate   || 0;
  const pctOf   = n => total_r > 0 ? (n / total_r * 100).toFixed(0) + '%' : 'N/A';
  const retryR  = typeof summary.quality_ratio === 'number'
    ? ((1 - summary.quality_ratio) * 100).toFixed(1) + '%'
    : 'N/A';

  const lines = [
    `## Weekly Throughput Dashboard — ${today}`,
    '',
    '### Volume',
    `- Tasks routed: ${summary.total_tasks}`,
    `- Subagents spawned: ${summary.total_subagents}`,
    `- Estimated cost: ${usd(summary.total_cost)}`,
    `- Cost per task: ${usd(summary.avg_cost_per_task)}`,
    '',
    '### Quality',
    `- Drift pass rate: ${drift.pass_rate}`,
    `- Common flags: ${drift.common_flags.length > 0 ? drift.common_flags.join(', ') : 'none'}`,
    `- Subagent retry rate: ${retryR}`,
    '',
    '### Routing Distribution',
    `- Core: ${core_n} (${pctOf(core_n)})`,
    `- Specialist: ${spec_n} (${pctOf(spec_n)})`,
    `- Escalated: ${esc_n} (${pctOf(esc_n)})`
  ];

  if (publish) {
    lines.push('', '### Publishing');
    lines.push(`- Skills live: ${publish.skills_live}`);
    lines.push(`- Downloads (7d): ${publish.downloads_7d}`);
  }

  lines.push('', `_Generated by throughput-dashboard.js at ${new Date().toISOString()}_`);
  return lines.join('\n');
}

/**
 * Generate and write dashboard to memory/dashboards/YYYY-MM-DD.md.
 *
 * @param {string} workspaceRoot
 * @returns {string} Absolute path to the written file
 */
function saveDashboard(workspaceRoot) {
  const dashDir = path.join(workspaceRoot, 'memory', 'dashboards');
  const outPath = path.join(dashDir, `${todayDate()}.md`);
  fs.mkdirSync(dashDir, { recursive: true });
  atomicWrite(outPath, generateDashboard(workspaceRoot));
  return outPath;
}

module.exports = { generateDashboard, saveDashboard };

// ── CLI ───────────────────────────────────────────────────────────────────────
if (require.main === module) {
  const WS     = process.argv[2] || process.env.OPENCLAW_WORKSPACE || process.cwd();
  const saved  = saveDashboard(WS);
  const content = generateDashboard(WS);
  console.log(content);
  console.log('\nSaved to:', saved);
}
