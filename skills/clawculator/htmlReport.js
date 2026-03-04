'use strict';

const fs = require('fs');
const path = require('path');
const os = require('os');

function severityColor(severity) {
  return { critical: '#ef4444', high: '#f97316', medium: '#eab308', low: '#06b6d4', info: '#22c55e' }[severity] || '#6b7280';
}

function severityBg(severity) {
  return { critical: '#fef2f2', high: '#fff7ed', medium: '#fefce8', low: '#ecfeff', info: '#f0fdf4' }[severity] || '#f9fafb';
}

function severityIcon(severity) {
  return { critical: '🔴', high: '🟠', medium: '🟡', low: '🔵', info: '✅' }[severity] || '⚪';
}

function relativeAge(ageMs) {
  if (!ageMs) return 'unknown';
  const s = Math.floor(ageMs / 1000);
  if (s < 60)        return `${s}s ago`;
  const m = Math.floor(s / 60);
  if (m < 60)        return `${m}m ago`;
  const h = Math.floor(m / 60);
  if (h < 24)        return `${h}h ago`;
  const d = Math.floor(h / 24);
  if (d < 30)        return `${d}d ago`;
  return `${Math.floor(d / 30)}mo ago`;
}

const SOURCE_LABELS = {
  heartbeat: '💓 Heartbeat', hooks: '🪝 Hooks', whatsapp: '📱 WhatsApp',
  subagents: '🤖 Subagents', skills: '🔧 Skills', memory: '🧠 Memory',
  primary_model: '⚙️ Primary Model', sessions: '💬 Sessions',
  workspace: '📁 Workspace', config: '📄 Config',
};

async function generateHTMLReport(analysis, outPath) {
  const { summary, findings, sessions } = analysis;
  const bleed = summary.estimatedMonthlyBleed;

  // Burn summary calculation
  const activeSessions = (sessions || []).filter(s => s.dailyCost);
  const totalDaily = activeSessions.reduce((sum, s) => sum + (s.dailyCost || 0), 0);
  const totalMonthly = totalDaily * 30;
  const burnSummary = totalDaily > 0 ? `
    <div class="section">
      <div class="section-title">Session Burn Rate</div>
      <div style="display:flex; gap:32px; flex-wrap:wrap;">
        <div>
          <div style="font-size:24px; font-weight:800; color:#f59e0b;">$${totalDaily.toFixed(4)}/day</div>
          <div style="font-size:13px; color:#94a3b8; margin-top:4px;">Combined daily burn rate across ${activeSessions.length} active session${activeSessions.length !== 1 ? 's' : ''}</div>
        </div>
        <div>
          <div style="font-size:24px; font-weight:800; color:#f97316;">$${totalMonthly.toFixed(2)}/month</div>
          <div style="font-size:13px; color:#94a3b8; margin-top:4px;">Projected monthly from active sessions</div>
        </div>
      </div>
    </div>` : '';

  const findingCards = findings.map(f => `
    <div class="finding" style="border-left: 4px solid ${severityColor(f.severity)}; background: ${severityBg(f.severity)}; padding: 16px; margin-bottom: 12px; border-radius: 0 8px 8px 0;">
      <div style="display:flex; align-items:center; gap:8px; margin-bottom:6px;">
        <span style="font-size:18px">${severityIcon(f.severity)}</span>
        <strong style="color:${severityColor(f.severity)}">${f.severity.toUpperCase()}</strong>
        <span style="color:#6b7280; font-size:14px">${SOURCE_LABELS[f.source] || f.source}</span>
        ${f.monthlyCost ? `<span style="margin-left:auto; color:${severityColor(f.severity)}; font-weight:bold">$${f.monthlyCost.toFixed(2)}/mo</span>` : ''}
      </div>
      <div style="font-weight:600; color:#111; margin-bottom:4px">${f.message}</div>
      ${f.detail ? `<div style="color:#555; font-size:14px; margin-bottom:6px; white-space:pre-line">${f.detail}</div>` : ''}
      ${f.recommendation ? `<div style="color:#16a34a; font-size:14px; margin-top:8px">→ Fix: ${f.recommendation}</div>` : ''}
    </div>
  `).join('');

  const sessionRows = (sessions || [])
    .sort((a, b) => (b.inputTokens + b.outputTokens) - (a.inputTokens + a.outputTokens))
    .slice(0, 20)
    .map(s => {
      const keyDisplay = s.key.length > 12 ? s.key.slice(0, 8) + '…' : s.key;
      const flag = s.isOrphaned ? ' ⚠️' : '';
      const age = s.ageMs ? relativeAge(s.ageMs) : 'unknown';
      const absDate = s.updatedAt ? new Date(s.updatedAt).toLocaleString() : '';
      const daily = s.dailyCost ? `$${s.dailyCost.toFixed(4)}/day` : '—';
      return `
      <tr style="${s.isOrphaned ? 'background:#fff7ed' : ''}">
        <td style="padding:8px 12px; font-family:monospace; font-size:13px">${keyDisplay}${flag}</td>
        <td style="padding:8px 12px">${s.modelLabel || s.model}</td>
        <td style="padding:8px 12px; text-align:right">${(s.inputTokens + s.outputTokens).toLocaleString()}</td>
        <td style="padding:8px 12px; text-align:right; color:${s.cost > 0.01 ? '#ef4444' : '#22c55e'}">$${s.cost.toFixed(6)}</td>
        <td style="padding:8px 12px; text-align:right; color:#f59e0b">${daily}</td>
        <td style="padding:8px 12px; color:#6b7280; font-size:13px" title="${absDate}">${age}</td>
      </tr>
    `}).join('');

  const html = `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Clawculator Report — ${new Date(analysis.scannedAt).toLocaleString()}</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #0f172a; color: #e2e8f0; min-height: 100vh; }
    .header { background: linear-gradient(135deg, #0f172a 0%, #1e3a5f 100%); padding: 48px 32px; text-align: center; border-bottom: 1px solid #1e40af; }
    .logo { font-size: 42px; font-weight: 900; letter-spacing: -2px; background: linear-gradient(90deg, #38bdf8, #818cf8); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    .tagline { color: #94a3b8; margin-top: 8px; font-size: 16px; }
    .container { max-width: 1000px; margin: 0 auto; padding: 32px 24px; }
    .cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 16px; margin-bottom: 32px; }
    .card { background: #1e293b; border-radius: 12px; padding: 20px; border: 1px solid #334155; }
    .card-value { font-size: 32px; font-weight: 800; }
    .card-label { font-size: 13px; color: #94a3b8; margin-top: 4px; }
    .section { background: #1e293b; border-radius: 12px; padding: 24px; margin-bottom: 24px; border: 1px solid #334155; }
    .section-title { font-size: 18px; font-weight: 700; margin-bottom: 16px; color: #f1f5f9; }
    table { width: 100%; border-collapse: collapse; }
    th { background: #0f172a; padding: 10px 12px; text-align: left; font-size: 13px; color: #94a3b8; }
    tr:nth-child(even) { background: #0f172a33; }
    .footer { text-align: center; color: #475569; font-size: 13px; padding: 32px; }
    .bleed { background: linear-gradient(135deg, #7f1d1d, #991b1b); border-radius: 12px; padding: 20px 24px; margin-bottom: 24px; border: 1px solid #ef4444; }
    .bleed-amount { font-size: 36px; font-weight: 900; color: #fca5a5; }
  </style>
</head>
<body>
  <div class="header">
    <div class="logo">CLAWCULATOR</div>
    <div class="tagline">Your friendly penny pincher. · 100% offline · Zero AI · Pure deterministic logic</div>
    <div style="color:#64748b; font-size:13px; margin-top:12px">Report generated: ${new Date(analysis.scannedAt).toLocaleString()}</div>
  </div>

  <div class="container">
    ${bleed > 0 ? `
    <div class="bleed">
      <div style="color:#fca5a5; font-size:14px; font-weight:600; margin-bottom:4px">⚠️ ESTIMATED MONTHLY COST EXPOSURE</div>
      <div class="bleed-amount">$${bleed.toFixed(2)}/month</div>
      <div style="color:#fca5a5; font-size:14px; margin-top:4px">Based on current config — fix the critical issues below to stop the bleed</div>
    </div>` : `
    <div style="background:#14532d; border-radius:12px; padding:20px 24px; margin-bottom:24px; border:1px solid #22c55e">
      <div style="color:#86efac; font-size:18px; font-weight:700">✅ No significant cost bleed detected</div>
    </div>`}

    <div class="cards">
      <div class="card">
        <div class="card-value" style="color:#ef4444">${summary.critical}</div>
        <div class="card-label">🔴 Critical</div>
      </div>
      <div class="card">
        <div class="card-value" style="color:#f97316">${summary.high}</div>
        <div class="card-label">🟠 High</div>
      </div>
      <div class="card">
        <div class="card-value" style="color:#eab308">${summary.medium}</div>
        <div class="card-label">🟡 Medium</div>
      </div>
      <div class="card">
        <div class="card-value" style="color:#06b6d4">${summary.low || 0}</div>
        <div class="card-label">🔵 Low</div>
      </div>
      <div class="card">
        <div class="card-value" style="color:#22c55e">${summary.info}</div>
        <div class="card-label">✅ OK</div>
      </div>
      <div class="card">
        <div class="card-value" style="color:#38bdf8">${summary.sessionsAnalyzed}</div>
        <div class="card-label">Sessions Analyzed</div>
      </div>
      <div class="card">
        <div class="card-value" style="color:#818cf8">${(summary.totalTokensFound || 0).toLocaleString()}</div>
        <div class="card-label">Total Tokens Found</div>
      </div>
    </div>

    <div class="section">
      <div class="section-title">Findings</div>
      <div style="color:#0f172a">
        ${findingCards}
      </div>
    </div>

    ${sessionRows ? `
    <div class="section">
      <div class="section-title">Session Breakdown</div>
      <div style="overflow-x:auto">
        <table>
          <thead><tr><th>Session</th><th>Model</th><th style="text-align:right">Tokens</th><th style="text-align:right">Total Cost</th><th style="text-align:right">$/day</th><th>Last Active</th></tr></thead>
          <tbody>${sessionRows}</tbody>
        </table>
      </div>
    </div>
    ${burnSummary}` : ''}

  </div>
  <div class="footer">
    Clawculator · github.com/echoudhry/clawculator · Your friendly penny pincher.
  </div>
</body>
</html>`;

  if (!outPath) {
    outPath = path.join(process.cwd(), `clawculator-report-${Date.now()}.html`);
  }
  fs.writeFileSync(outPath, html, 'utf8');
  return outPath;
}

module.exports = { generateHTMLReport };
