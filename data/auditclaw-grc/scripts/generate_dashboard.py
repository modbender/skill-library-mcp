#!/usr/bin/env python3
"""Generate GRC Compliance Dashboard — self-contained HTML.

Reads data from the compliance database and generates a dark-mode,
mobile-responsive HTML dashboard with inline CSS/SVG charts.

Usage:
    python3 generate_dashboard.py --db-path ~/.openclaw/grc/compliance.sqlite
    python3 generate_dashboard.py --db-path ~/.openclaw/grc/compliance.sqlite --output ~/clawd/canvas/grc/index.html
"""

import argparse
import json
import os
import sqlite3
import sys
from datetime import datetime, timedelta
from html import escape


def get_dashboard_data(db_path):
    """Collect all data needed for the dashboard."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    data = {}

    # Overall scores
    scores = conn.execute(
        "SELECT framework_slug, score, calculated_at FROM compliance_scores ORDER BY calculated_at DESC"
    ).fetchall()
    latest_scores = {}
    for s in scores:
        d = dict(s)
        if d["framework_slug"] not in latest_scores:
            latest_scores[d["framework_slug"]] = d

    data["scores"] = latest_scores
    all_scores = [v["score"] for v in latest_scores.values()]
    data["overall_score"] = round(sum(all_scores) / len(all_scores), 1) if all_scores else 0
    data["frameworks_count"] = len(latest_scores)

    # Framework status
    frameworks = conn.execute("SELECT * FROM frameworks ORDER BY priority, name").fetchall()
    data["frameworks"] = [dict(f) for f in frameworks]

    # Risk heat map
    risks = conn.execute("SELECT likelihood, impact, COUNT(*) as count FROM risks GROUP BY likelihood, impact").fetchall()
    data["risk_matrix"] = [dict(r) for r in risks]
    data["total_risks"] = conn.execute("SELECT COUNT(*) FROM risks").fetchone()[0]

    # Evidence freshness
    now_str = datetime.now().isoformat(timespec="seconds")
    fresh = conn.execute(
        "SELECT COUNT(*) FROM evidence WHERE status = 'active' AND (valid_until IS NULL OR valid_until > ?)",
        (now_str,)
    ).fetchone()[0]
    expiring_cutoff = (datetime.now() + timedelta(days=30)).isoformat(timespec="seconds")
    expiring = conn.execute(
        "SELECT COUNT(*) FROM evidence WHERE status = 'active' AND valid_until IS NOT NULL AND valid_until <= ? AND valid_until > ?",
        (expiring_cutoff, now_str)
    ).fetchone()[0]
    expired = conn.execute(
        "SELECT COUNT(*) FROM evidence WHERE status = 'active' AND valid_until IS NOT NULL AND valid_until <= ?",
        (now_str,)
    ).fetchone()[0]
    data["evidence"] = {"fresh": fresh, "expiring": expiring, "expired": expired, "total": fresh + expiring + expired}

    # Recent alerts (last 10 unresolved)
    alerts = conn.execute(
        "SELECT * FROM alerts WHERE resolved_at IS NULL ORDER BY triggered_at DESC LIMIT 10"
    ).fetchall()
    data["alerts"] = [dict(a) for a in alerts]
    data["unresolved_alerts"] = conn.execute("SELECT COUNT(*) FROM alerts WHERE resolved_at IS NULL").fetchone()[0]

    # Integration health
    integrations = conn.execute("SELECT * FROM integrations ORDER BY provider").fetchall()
    data["integrations"] = [dict(i) for i in integrations]

    # Control maturity distribution
    maturity = conn.execute(
        "SELECT maturity_level, COUNT(*) as count FROM controls WHERE maturity_level IS NOT NULL GROUP BY maturity_level"
    ).fetchall()
    data["maturity"] = {dict(m)["maturity_level"]: dict(m)["count"] for m in maturity}

    # Active incidents
    data["active_incidents"] = conn.execute(
        "SELECT COUNT(*) FROM incidents WHERE status IN ('open', 'investigating')"
    ).fetchone()[0]

    data["generated_at"] = datetime.now().isoformat(timespec="seconds")

    conn.close()
    return data


def generate_html(data):
    """Generate the dashboard HTML."""
    overall = data["overall_score"]
    score_color = "#22c55e" if overall >= 80 else "#eab308" if overall >= 60 else "#ef4444"

    # Framework cards
    fw_cards = ""
    for slug, score_data in data["scores"].items():
        if not slug:
            continue
        score = score_data["score"]
        color = "#22c55e" if score >= 80 else "#eab308" if score >= 60 else "#ef4444"
        calc_at = score_data.get('calculated_at') or ''
        fw_cards += f"""
        <div class="card framework-card">
            <div class="fw-name">{escape(slug.upper())}</div>
            <div class="fw-score" style="color:{color}">{score}%</div>
            <div class="fw-date">{escape(calc_at[:10])}</div>
        </div>"""

    # Risk heat map cells (5x5)
    risk_data = {}
    for r in data["risk_matrix"]:
        key = (r.get("likelihood", 1), r.get("impact", 1))
        risk_data[key] = r.get("count", 0)

    risk_cells = ""
    for impact in range(5, 0, -1):
        for likelihood in range(1, 6):
            count = risk_data.get((likelihood, impact), 0)
            if count > 0:
                bg = "#ef4444" if likelihood >= 4 and impact >= 4 else "#eab308" if likelihood + impact >= 6 else "#22c55e"
                risk_cells += f'<div class="risk-cell" style="background:{bg}40;border:1px solid {bg}">{count}</div>'
            else:
                risk_cells += '<div class="risk-cell"></div>'

    # Evidence bar
    ev = data["evidence"]
    ev_total = ev["total"] or 1
    fresh_pct = round(ev["fresh"] / ev_total * 100)
    expiring_pct = round(ev["expiring"] / ev_total * 100)
    expired_pct = round(ev["expired"] / ev_total * 100)

    # Alerts list
    alert_rows = ""
    for a in data["alerts"][:8]:
        sev_color = "#ef4444" if a["severity"] == "critical" else "#eab308" if a["severity"] == "warning" else "#60a5fa"
        alert_rows += f"""
        <div class="alert-row">
            <span class="alert-badge" style="background:{sev_color}">{escape(a['severity'][:4].upper())}</span>
            <span class="alert-title">{escape(a.get('title', 'Untitled')[:60])}</span>
        </div>"""

    # Integration health
    int_rows = ""
    for i in data["integrations"]:
        st = i.get("status", "unknown")
        st_color = "#22c55e" if st in ("active", "configured") else "#ef4444" if st == "error" else "#eab308"
        last_sync = (i.get("last_sync") or "never")[:16]
        int_rows += f"""
        <div class="int-row">
            <span class="int-provider">{escape(i['provider'] or '')}</span>
            <span class="int-name">{escape(i['name'] or '')}</span>
            <span class="int-status" style="color:{st_color}">{escape(st)}</span>
            <span class="int-sync">{escape(last_sync)}</span>
        </div>"""

    # Maturity pie data
    maturity_levels = ["initial", "developing", "defined", "managed", "optimizing"]
    mat_colors = ["#ef4444", "#f97316", "#eab308", "#22c55e", "#06b6d4"]
    mat_data = data.get("maturity", {})
    mat_total = sum(mat_data.values()) or 1

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>GRC Compliance Dashboard</title>
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ background: #0f172a; color: #e2e8f0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; padding: 16px; }}
.header {{ text-align: center; margin-bottom: 24px; }}
.header h1 {{ font-size: 24px; color: #f1f5f9; }}
.header .subtitle {{ color: #94a3b8; font-size: 13px; margin-top: 4px; }}
.score-gauge {{ text-align: center; margin: 16px 0; }}
.score-value {{ font-size: 64px; font-weight: bold; }}
.score-label {{ color: #94a3b8; font-size: 14px; }}
.grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 16px; }}
.section {{ background: #1e293b; border-radius: 12px; padding: 16px; margin-bottom: 16px; }}
.section h2 {{ font-size: 16px; color: #94a3b8; margin-bottom: 12px; text-transform: uppercase; letter-spacing: 1px; }}
.card {{ background: #334155; border-radius: 8px; padding: 12px; }}
.fw-cards {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(120px, 1fr)); gap: 8px; }}
.framework-card {{ text-align: center; }}
.fw-name {{ font-size: 12px; color: #94a3b8; font-weight: 600; }}
.fw-score {{ font-size: 28px; font-weight: bold; }}
.fw-date {{ font-size: 11px; color: #64748b; }}
.risk-grid {{ display: grid; grid-template-columns: repeat(5, 1fr); gap: 4px; }}
.risk-cell {{ width: 100%; aspect-ratio: 1; display: flex; align-items: center; justify-content: center; border-radius: 4px; font-size: 14px; font-weight: bold; background: #334155; }}
.evidence-bar {{ display: flex; height: 24px; border-radius: 6px; overflow: hidden; margin: 8px 0; }}
.ev-fresh {{ background: #22c55e; }}
.ev-expiring {{ background: #eab308; }}
.ev-expired {{ background: #ef4444; }}
.ev-legend {{ display: flex; gap: 16px; font-size: 12px; color: #94a3b8; }}
.ev-legend span {{ display: flex; align-items: center; gap: 4px; }}
.ev-dot {{ width: 10px; height: 10px; border-radius: 50%; display: inline-block; }}
.alert-row {{ display: flex; align-items: center; gap: 8px; padding: 6px 0; border-bottom: 1px solid #334155; }}
.alert-badge {{ font-size: 10px; padding: 2px 6px; border-radius: 4px; color: #fff; font-weight: 600; flex-shrink: 0; }}
.alert-title {{ font-size: 13px; color: #cbd5e1; }}
.int-row {{ display: grid; grid-template-columns: 80px 1fr 80px 120px; gap: 8px; padding: 6px 0; border-bottom: 1px solid #334155; font-size: 13px; }}
.int-provider {{ font-weight: 600; color: #60a5fa; }}
.int-name {{ color: #cbd5e1; }}
.int-status {{ font-weight: 600; text-align: center; }}
.int-sync {{ color: #64748b; text-align: right; }}
.stat-row {{ display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #334155; }}
.stat-label {{ color: #94a3b8; }}
.stat-value {{ font-weight: 600; }}
.maturity-bar {{ display: flex; height: 20px; border-radius: 4px; overflow: hidden; margin: 4px 0; }}
.quick-actions {{ display: flex; flex-wrap: wrap; gap: 8px; }}
.action-btn {{ background: #3b82f6; color: #fff; padding: 8px 16px; border-radius: 6px; text-decoration: none; font-size: 13px; font-weight: 500; }}
.action-btn:hover {{ background: #2563eb; }}
</style>
</head>
<body>
<div class="header">
    <h1>GRC Compliance Dashboard</h1>
    <div class="subtitle">Last updated: {data['generated_at']}</div>
</div>

<div class="score-gauge">
    <div class="score-value" style="color:{score_color}">{overall}%</div>
    <div class="score-label">Overall Compliance Score ({data['frameworks_count']} frameworks)</div>
</div>

<div class="grid">
    <div class="section">
        <h2>Framework Scores</h2>
        <div class="fw-cards">{fw_cards}</div>
    </div>

    <div class="section">
        <h2>Risk Heat Map ({data['total_risks']} risks)</h2>
        <div style="display:flex;gap:8px;align-items:center;margin-bottom:8px">
            <span style="font-size:11px;color:#64748b;writing-mode:vertical-lr;transform:rotate(180deg)">Impact</span>
            <div style="flex:1">
                <div class="risk-grid">{risk_cells}</div>
                <div style="text-align:center;font-size:11px;color:#64748b;margin-top:4px">Likelihood →</div>
            </div>
        </div>
    </div>

    <div class="section">
        <h2>Evidence Freshness ({ev['total']} items)</h2>
        <div class="evidence-bar">
            <div class="ev-fresh" style="width:{fresh_pct}%"></div>
            <div class="ev-expiring" style="width:{expiring_pct}%"></div>
            <div class="ev-expired" style="width:{expired_pct}%"></div>
        </div>
        <div class="ev-legend">
            <span><span class="ev-dot" style="background:#22c55e"></span> Fresh ({ev['fresh']})</span>
            <span><span class="ev-dot" style="background:#eab308"></span> Expiring ({ev['expiring']})</span>
            <span><span class="ev-dot" style="background:#ef4444"></span> Expired ({ev['expired']})</span>
        </div>
    </div>

    <div class="section">
        <h2>Unresolved Alerts ({data['unresolved_alerts']})</h2>
        {alert_rows if alert_rows else '<div style="color:#64748b;font-size:13px">No unresolved alerts</div>'}
    </div>

    <div class="section">
        <h2>Integration Health ({len(data['integrations'])} providers)</h2>
        {int_rows if int_rows else '<div style="color:#64748b;font-size:13px">No integrations configured</div>'}
    </div>

    <div class="section">
        <h2>Control Maturity</h2>
        <div class="maturity-bar">
            {''.join(f'<div style="background:{mat_colors[i]};width:{mat_data.get(level, 0) / mat_total * 100}%"></div>' for i, level in enumerate(maturity_levels))}
        </div>
        <div class="ev-legend" style="flex-wrap:wrap">
            {''.join(f'<span><span class="ev-dot" style="background:{mat_colors[i]}"></span> {level.title()} ({mat_data.get(level, 0)})</span>' for i, level in enumerate(maturity_levels))}
        </div>
    </div>

    <div class="section">
        <h2>Quick Stats</h2>
        <div class="stat-row"><span class="stat-label">Active Incidents</span><span class="stat-value">{data['active_incidents']}</span></div>
        <div class="stat-row"><span class="stat-label">Total Risks</span><span class="stat-value">{data['total_risks']}</span></div>
        <div class="stat-row"><span class="stat-label">Unresolved Alerts</span><span class="stat-value">{data['unresolved_alerts']}</span></div>
        <div class="stat-row"><span class="stat-label">Evidence Items</span><span class="stat-value">{ev['total']}</span></div>
        <div class="stat-row"><span class="stat-label">Integrations</span><span class="stat-value">{len(data['integrations'])}</span></div>
    </div>

    <div class="section">
        <h2>Quick Actions</h2>
        <div class="quick-actions">
            <a class="action-btn" href="openclaw://agent?message=show%20compliance%20score">Score</a>
            <a class="action-btn" href="openclaw://agent?message=list%20alerts">Alerts</a>
            <a class="action-btn" href="openclaw://agent?message=run%20gap%20analysis">Gaps</a>
            <a class="action-btn" href="openclaw://agent?message=compliance%20calendar">Calendar</a>
            <a class="action-btn" href="openclaw://agent?message=compliance%20digest">Digest</a>
            <a class="action-btn" href="openclaw://agent?message=integration%20health">Health</a>
        </div>
    </div>
</div>

<script>
// Auto-reload every 5 minutes
setTimeout(() => location.reload(), 300000);
</script>
</body>
</html>"""

    return html


def generate_text_summary(data):
    """Generate a text summary of the dashboard suitable for chat display."""
    overall = data["overall_score"]
    if overall >= 80:
        indicator = "GREEN"
    elif overall >= 60:
        indicator = "YELLOW"
    else:
        indicator = "RED"

    lines = []
    lines.append("=== GRC COMPLIANCE DASHBOARD ===")
    lines.append(f"Generated: {data['generated_at'][:16]}")
    lines.append("")
    lines.append(f"OVERALL SCORE: {overall}% [{indicator}]")
    lines.append(f"Frameworks tracked: {data['frameworks_count']}")
    lines.append("")

    if data["scores"]:
        lines.append("FRAMEWORK SCORES:")
        for slug, score_data in sorted(((k or "", v) for k, v in data["scores"].items())):
            if not slug:
                continue
            sc = score_data["score"]
            mark = "+" if sc >= 80 else "~" if sc >= 60 else "-"
            calc_date = (score_data.get("calculated_at") or "")[:10]
            lines.append(f"  [{mark}] {slug.upper()}: {sc}% (scored {calc_date})")
        lines.append("")

    ev = data["evidence"]
    lines.append("RISK OVERVIEW:")
    lines.append(f"  Total risks: {data['total_risks']}")
    lines.append("")

    lines.append(f"EVIDENCE ({ev['total']} items):")
    lines.append(f"  Fresh: {ev['fresh']}")
    lines.append(f"  Expiring (30d): {ev['expiring']}")
    lines.append(f"  Expired: {ev['expired']}")
    lines.append("")

    lines.append("ALERTS & INCIDENTS:")
    lines.append(f"  Unresolved alerts: {data['unresolved_alerts']}")
    lines.append(f"  Active incidents: {data['active_incidents']}")
    lines.append("")

    # Control maturity
    if data.get("maturity"):
        total_m = sum(data["maturity"].values())
        lines.append(f"CONTROL MATURITY ({total_m} controls):")
        for level in ["initial", "developing", "defined", "managed", "optimizing"]:
            count = data["maturity"].get(level, 0)
            if count > 0:
                lines.append(f"  {level.title()}: {count}")
        lines.append("")

    if data.get("integrations"):
        lines.append(f"INTEGRATIONS: {len(data['integrations'])} configured")
        lines.append("")

    dashboard_url = os.environ.get("DASHBOARD_URL", "http://localhost:8080/grc/")
    lines.append(f"Full dashboard: {dashboard_url}")

    return "\n".join(lines)



def main():
    parser = argparse.ArgumentParser(description="Generate GRC Dashboard")
    parser.add_argument("--db-path", required=True, help="Path to compliance.sqlite")
    parser.add_argument("--output", default=None, help="Output HTML path (default: ~/clawd/canvas/grc/index.html)")

    args = parser.parse_args()

    output = args.output or os.path.expanduser("~/clawd/canvas/grc/index.html")
    os.makedirs(os.path.dirname(output), exist_ok=True)

    data = get_dashboard_data(args.db_path)
    html = generate_html(data)

    with open(output, "w") as f:
        f.write(html)

    text_summary = generate_text_summary(data)
    dashboard_url = os.environ.get("DASHBOARD_URL", "http://localhost:8080/grc/")

    result = {
        "status": "ok",
        "output": output,
        "overall_score": data["overall_score"],
        "frameworks": data["frameworks_count"],
        "alerts": data["unresolved_alerts"],
        "evidence_items": data["evidence"]["total"],
        "generated_at": data["generated_at"],
        "dashboard_url": dashboard_url,
        "text_summary": text_summary,
    }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
