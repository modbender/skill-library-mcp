#!/usr/bin/env python3
"""Generate a static HTML trust center page from the GRC compliance database.

Produces a professional, public-facing trust center page showing compliance
framework status, active policies, evidence freshness, and security posture.

Usage:
    python3 generate_trust_center.py [--db-path PATH] [--output-dir DIR] [--org-name NAME]

Examples:
    python3 generate_trust_center.py
    python3 generate_trust_center.py --org-name "Acme Corp" --output-dir ./public
    python3 generate_trust_center.py --db-path /path/to/compliance.sqlite
"""

import argparse
import json
import os
import sqlite3
import sys
from datetime import datetime, timedelta, timezone
from html import escape

DEFAULT_DB_PATH = os.path.expanduser("~/.openclaw/grc/compliance.sqlite")


# ---------------------------------------------------------------------------
# Data access helpers
# ---------------------------------------------------------------------------

def _dict_factory(cursor, row):
    """SQLite row factory that returns dicts."""
    return {col[0]: row[idx] for idx, col in enumerate(cursor.description)}


def _safe_query(conn, sql, params=()):
    """Execute a query and return all rows; return [] on any error."""
    try:
        cur = conn.execute(sql, params)
        return cur.fetchall()
    except sqlite3.OperationalError:
        return []


def _safe_scalar(conn, sql, params=(), default=0):
    """Execute a query returning a single scalar value."""
    try:
        cur = conn.execute(sql, params)
        row = cur.fetchone()
        if row is None:
            return default
        val = list(row.values())[0]
        return val if val is not None else default
    except sqlite3.OperationalError:
        return default


# ---------------------------------------------------------------------------
# Data collection
# ---------------------------------------------------------------------------

def collect_data(conn):
    """Query all data needed for the trust center page."""

    data = {}

    # --- Frameworks ---------------------------------------------------------
    frameworks = _safe_query(conn, """
        SELECT f.id, f.name, f.slug, f.version, f.status, f.activated_at,
               COUNT(c.id)                                        AS total_controls,
               SUM(CASE WHEN c.status = 'complete' THEN 1 ELSE 0 END) AS complete_controls
        FROM frameworks f
        LEFT JOIN controls c ON c.framework_id = f.id
        WHERE f.status = 'active'
        GROUP BY f.id
        ORDER BY f.priority ASC, f.name ASC
    """)
    for fw in frameworks:
        total = fw["total_controls"] or 0
        complete = fw["complete_controls"] or 0
        fw["completion_pct"] = round((complete / total) * 100, 1) if total > 0 else 0.0
    data["frameworks"] = frameworks

    # --- Policies -----------------------------------------------------------
    policies = _safe_query(conn, """
        SELECT id, title, type, version, status, approved_by, approved_at,
               last_reviewed, next_review
        FROM policies
        WHERE status IN ('active', 'draft', 'under_review')
        ORDER BY
            CASE status WHEN 'active' THEN 0 WHEN 'under_review' THEN 1 ELSE 2 END,
            title ASC
    """)
    data["policies"] = policies

    # --- Evidence freshness -------------------------------------------------
    now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    thirty_days = (datetime.now(timezone.utc) + timedelta(days=30)).strftime("%Y-%m-%d")

    total_evidence = _safe_scalar(conn, "SELECT COUNT(*) FROM evidence")
    current_evidence = _safe_scalar(conn, """
        SELECT COUNT(*) FROM evidence
        WHERE status = 'active'
          AND (valid_until IS NULL OR valid_until >= ?)
    """, (now_iso,))
    expiring_evidence = _safe_scalar(conn, """
        SELECT COUNT(*) FROM evidence
        WHERE status = 'active'
          AND valid_until IS NOT NULL
          AND valid_until >= ?
          AND valid_until < ?
    """, (now_iso, thirty_days))
    expired_evidence = _safe_scalar(conn, """
        SELECT COUNT(*) FROM evidence
        WHERE (status = 'expired')
           OR (status = 'active' AND valid_until IS NOT NULL AND valid_until < ?)
    """, (now_iso,))
    data["evidence"] = {
        "total": total_evidence,
        "current": current_evidence,
        "expiring_soon": expiring_evidence,
        "expired": expired_evidence,
        "freshness_pct": round((current_evidence / total_evidence) * 100, 1) if total_evidence > 0 else 0.0,
    }

    # --- Latest compliance score date ---------------------------------------
    latest_score_row = _safe_query(conn, """
        SELECT calculated_at FROM compliance_scores
        ORDER BY calculated_at DESC LIMIT 1
    """)
    data["last_score_date"] = latest_score_row[0]["calculated_at"] if latest_score_row else None

    # --- Last security scan (browser_checks) --------------------------------
    last_scan_row = _safe_query(conn, """
        SELECT last_run FROM browser_checks
        WHERE last_run IS NOT NULL
        ORDER BY last_run DESC LIMIT 1
    """)
    data["last_scan_date"] = last_scan_row[0]["last_run"] if last_scan_row else None

    # --- Compliance test summary --------------------------------------------
    tests_total = _safe_scalar(conn, "SELECT COUNT(*) FROM compliance_tests WHERE status = 'active'")
    tests_passing = _safe_scalar(conn, """
        SELECT COUNT(*) FROM compliance_tests
        WHERE status = 'active' AND last_result = 'pass'
    """)
    data["tests"] = {
        "total": tests_total,
        "passing": tests_passing,
        "pass_rate": round((tests_passing / tests_total) * 100, 1) if tests_total > 0 else 0.0,
    }

    # --- Controls summary ---------------------------------------------------
    controls_total = _safe_scalar(conn, "SELECT COUNT(*) FROM controls")
    controls_complete = _safe_scalar(conn, "SELECT COUNT(*) FROM controls WHERE status = 'complete'")
    controls_in_progress = _safe_scalar(conn, "SELECT COUNT(*) FROM controls WHERE status = 'in_progress'")
    data["controls"] = {
        "total": controls_total,
        "complete": controls_complete,
        "in_progress": controls_in_progress,
    }

    # --- Open risks summary -------------------------------------------------
    open_risks = _safe_scalar(conn, "SELECT COUNT(*) FROM risks WHERE status = 'open'")
    mitigated_risks = _safe_scalar(conn, "SELECT COUNT(*) FROM risks WHERE status = 'mitigated'")
    data["risks"] = {
        "open": open_risks,
        "mitigated": mitigated_risks,
    }

    return data


# ---------------------------------------------------------------------------
# HTML rendering helpers
# ---------------------------------------------------------------------------

def _completion_color(pct):
    """Return CSS color class based on completion percentage."""
    if pct >= 80:
        return "badge-green"
    elif pct >= 40:
        return "badge-yellow"
    else:
        return "badge-red"


def _completion_bar_color(pct):
    """Return hex color for progress bar fill."""
    if pct >= 80:
        return "#16a34a"
    elif pct >= 40:
        return "#ca8a04"
    else:
        return "#dc2626"


def _framework_icon(slug):
    """Return an SVG icon string for known frameworks, generic shield otherwise."""
    shield = (
        '<svg width="32" height="32" viewBox="0 0 24 24" fill="none" '
        'stroke="currentColor" stroke-width="1.5" stroke-linecap="round" '
        'stroke-linejoin="round">'
        '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>'
        '</svg>'
    )
    check_shield = (
        '<svg width="32" height="32" viewBox="0 0 24 24" fill="none" '
        'stroke="currentColor" stroke-width="1.5" stroke-linecap="round" '
        'stroke-linejoin="round">'
        '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>'
        '<path d="M9 12l2 2 4-4"/>'
        '</svg>'
    )
    lock = (
        '<svg width="32" height="32" viewBox="0 0 24 24" fill="none" '
        'stroke="currentColor" stroke-width="1.5" stroke-linecap="round" '
        'stroke-linejoin="round">'
        '<rect x="3" y="11" width="18" height="11" rx="2" ry="2"/>'
        '<path d="M7 11V7a5 5 0 0110 0v4"/>'
        '</svg>'
    )
    icons = {
        "soc2": check_shield,
        "iso27001": shield,
        "hipaa": lock,
        "gdpr": lock,
        "nist-csf": shield,
        "nist_csf": shield,
        "pci-dss": lock,
        "pci_dss": lock,
    }
    return icons.get(slug, shield)


def _policy_status_badge(status):
    """Return styled HTML badge for policy status."""
    colors = {
        "active": ("#dcfce7", "#166534"),
        "draft": ("#fef9c3", "#854d0e"),
        "under_review": ("#dbeafe", "#1e40af"),
        "archived": ("#f3f4f6", "#6b7280"),
    }
    bg, fg = colors.get(status, ("#f3f4f6", "#6b7280"))
    label = status.replace("_", " ").title()
    return (
        f'<span style="display:inline-block;padding:2px 10px;border-radius:9999px;'
        f'font-size:0.75rem;font-weight:600;background:{bg};color:{fg};">'
        f'{escape(label)}</span>'
    )


def _format_date(iso_str):
    """Format an ISO date/datetime string for display, or return 'N/A'."""
    if not iso_str:
        return "N/A"
    try:
        for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M",
                     "%Y-%m-%dT%H:%M", "%Y-%m-%d"):
            try:
                dt = datetime.strptime(iso_str.split(".")[0], fmt)
                return dt.strftime("%b %d, %Y")
            except ValueError:
                continue
        return escape(iso_str)
    except Exception:
        return escape(str(iso_str))


# ---------------------------------------------------------------------------
# CSS styles (extracted for readability)
# ---------------------------------------------------------------------------

_CSS = """
/* ---- Reset and Base ---- */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
html { font-size: 16px; -webkit-font-smoothing: antialiased; }
body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto,
                 'Helvetica Neue', Arial, sans-serif;
    color: #1e293b;
    background: #f8fafc;
    line-height: 1.6;
}
.hero {
    background: linear-gradient(135deg, #0f172a 0%, #1e3a5f 50%, #1e40af 100%);
    color: #fff;
    padding: 60px 24px 48px;
    text-align: center;
}
.hero h1 { font-size: 2.25rem; font-weight: 700; letter-spacing: -0.02em; margin-bottom: 8px; }
.hero .subtitle { font-size: 1.1rem; color: #cbd5e1; max-width: 600px; margin: 0 auto 16px; }
.hero .updated { font-size: 0.8rem; color: #94a3b8; margin-top: 18px; }
.hero .shield-row { display: flex; justify-content: center; gap: 12px; margin-top: 20px; flex-wrap: wrap; }
.hero .shield-pill {
    display: inline-flex; align-items: center; gap: 6px;
    background: rgba(255,255,255,0.12); border: 1px solid rgba(255,255,255,0.18);
    border-radius: 9999px; padding: 6px 16px; font-size: 0.82rem; font-weight: 500; color: #e2e8f0;
}
.hero .shield-pill svg { width: 16px; height: 16px; stroke: #60a5fa; }
.section { margin: 48px auto; max-width: 1080px; padding: 0 24px; }
.section-title { font-size: 1.35rem; font-weight: 700; color: #0f172a; margin-bottom: 6px; }
.section-desc { font-size: 0.92rem; color: #64748b; margin-bottom: 24px; }
.fw-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 20px; }
.fw-card {
    background: #fff; border: 1px solid #e2e8f0; border-radius: 12px;
    padding: 24px 20px 20px; text-align: center; transition: box-shadow 0.2s, transform 0.2s;
}
.fw-card:hover { box-shadow: 0 4px 24px rgba(0,0,0,0.07); transform: translateY(-2px); }
.fw-card.badge-green  { border-top: 4px solid #16a34a; }
.fw-card.badge-yellow { border-top: 4px solid #ca8a04; }
.fw-card.badge-red    { border-top: 4px solid #dc2626; }
.fw-icon { display: flex; justify-content: center; margin-bottom: 12px; color: #475569; }
.fw-card.badge-green  .fw-icon { color: #16a34a; }
.fw-card.badge-yellow .fw-icon { color: #ca8a04; }
.fw-card.badge-red    .fw-icon { color: #dc2626; }
.fw-name { font-weight: 600; font-size: 0.95rem; color: #1e293b; margin-bottom: 8px; }
.fw-pct { font-size: 1.75rem; font-weight: 700; color: #0f172a; margin-bottom: 8px; }
.fw-bar-track { height: 6px; background: #e2e8f0; border-radius: 3px; overflow: hidden; margin-bottom: 10px; }
.fw-bar-fill { height: 100%; border-radius: 3px; transition: width 0.4s ease; }
.fw-stats { font-size: 0.8rem; color: #94a3b8; }
.stats-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 20px; }
.stat-card { background: #fff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 24px 20px; text-align: center; }
.stat-card .stat-label { font-size: 0.78rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; color: #64748b; margin-bottom: 6px; }
.stat-card .stat-value { font-size: 2rem; font-weight: 700; color: #0f172a; }
.stat-card .stat-sub { font-size: 0.8rem; color: #94a3b8; margin-top: 4px; }
.stat-green  { color: #16a34a !important; }
.stat-yellow { color: #ca8a04 !important; }
.stat-red    { color: #dc2626 !important; }
.donut-wrapper { display: flex; align-items: center; justify-content: center; gap: 32px; flex-wrap: wrap; margin-bottom: 20px; }
.donut { width: 120px; height: 120px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 1.5rem; font-weight: 700; color: #0f172a; }
.donut-legend { display: flex; flex-direction: column; gap: 8px; }
.donut-legend-item { display: flex; align-items: center; gap: 8px; font-size: 0.85rem; color: #475569; }
.donut-legend-dot { width: 12px; height: 12px; border-radius: 3px; flex-shrink: 0; }
.policy-table-wrap { overflow-x: auto; -webkit-overflow-scrolling: touch; }
.policy-table { width: 100%; border-collapse: collapse; background: #fff; border-radius: 12px; overflow: hidden; border: 1px solid #e2e8f0; }
.policy-table thead th { background: #f1f5f9; padding: 12px 16px; font-size: 0.78rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; color: #64748b; text-align: left; border-bottom: 1px solid #e2e8f0; }
.policy-table tbody td { padding: 12px 16px; font-size: 0.9rem; color: #334155; border-bottom: 1px solid #f1f5f9; }
.policy-table tbody tr:last-child td { border-bottom: none; }
.policy-table tbody tr:hover { background: #f8fafc; }
.date-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 20px; }
.date-card { background: #fff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 20px 24px; display: flex; align-items: center; gap: 16px; }
.date-card .date-icon { flex-shrink: 0; width: 44px; height: 44px; border-radius: 10px; background: #eff6ff; display: flex; align-items: center; justify-content: center; color: #3b82f6; }
.date-card .date-icon svg { width: 22px; height: 22px; }
.date-card .date-info .date-label { font-size: 0.78rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.04em; color: #64748b; }
.date-card .date-info .date-value { font-size: 1rem; font-weight: 600; color: #0f172a; }
.empty-state { color: #94a3b8; font-style: italic; padding: 24px 0; text-align: center; }
.footer { text-align: center; padding: 40px 24px; color: #94a3b8; font-size: 0.8rem; border-top: 1px solid #e2e8f0; margin-top: 48px; }
.footer a { color: #64748b; text-decoration: none; }
@media (max-width: 640px) {
    .hero { padding: 40px 16px 32px; }
    .hero h1 { font-size: 1.6rem; }
    .section { padding: 0 16px; margin: 32px auto; }
    .fw-grid { grid-template-columns: 1fr; }
    .stats-grid { grid-template-columns: 1fr 1fr; }
    .date-grid { grid-template-columns: 1fr; }
    .donut-wrapper { flex-direction: column; }
}
"""


# ---------------------------------------------------------------------------
# HTML generation
# ---------------------------------------------------------------------------

def build_html(data, org_name):
    """Construct the full trust center HTML document."""

    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    frameworks = data["frameworks"]
    policies = data["policies"]
    evidence = data["evidence"]
    tests = data["tests"]
    controls = data["controls"]
    risks = data["risks"]

    # --- Framework badge cards ---
    framework_cards = ""
    if frameworks:
        for fw in frameworks:
            pct = fw["completion_pct"]
            color_cls = _completion_color(pct)
            bar_color = _completion_bar_color(pct)
            icon = _framework_icon(fw["slug"])
            version_str = f' v{escape(fw["version"])}' if fw.get("version") else ""
            framework_cards += (
                f'<div class="fw-card {color_cls}">'
                f'<div class="fw-icon">{icon}</div>'
                f'<div class="fw-name">{escape(fw["name"])}{version_str}</div>'
                f'<div class="fw-pct">{pct:.0f}%</div>'
                f'<div class="fw-bar-track">'
                f'<div class="fw-bar-fill" style="width:{pct}%;background:{bar_color};"></div>'
                f'</div>'
                f'<div class="fw-stats">{fw["complete_controls"]}/{fw["total_controls"]} controls</div>'
                f'</div>\n'
            )
    else:
        framework_cards = '<p class="empty-state">No compliance frameworks activated yet.</p>'

    # --- Policy table rows ---
    policy_rows = ""
    if policies:
        for p in policies:
            p_type = (p.get("type") or "\u2014").replace("_", " ").title()
            p_version = p.get("version") or "\u2014"
            policy_rows += (
                f'<tr>'
                f'<td>{escape(p["title"])}</td>'
                f'<td>{escape(p_type)}</td>'
                f'<td>{escape(p_version)}</td>'
                f'<td>{_policy_status_badge(p["status"])}</td>'
                f'<td>{_format_date(p.get("approved_at"))}</td>'
                f'<td>{_format_date(p.get("next_review"))}</td>'
                f'</tr>\n'
            )
    else:
        policy_rows = '<tr><td colspan="6" class="empty-state">No policies published yet.</td></tr>'

    # --- Evidence donut values ---
    ev_pct = evidence["freshness_pct"]
    ev_color = _completion_bar_color(ev_pct)
    ev_expiring_pct = (evidence["expiring_soon"] / evidence["total"] * 100) if evidence["total"] > 0 else 0
    ev_seg2_end = ev_pct + ev_expiring_pct

    # --- Controls completion ---
    controls_completion = round(
        (controls["complete"] / controls["total"]) * 100, 1
    ) if controls["total"] > 0 else 0.0

    # --- Risks color class ---
    if risks["open"] == 0:
        risk_cls = "stat-green"
    elif risks["open"] < 5:
        risk_cls = "stat-yellow"
    else:
        risk_cls = "stat-red"

    # --- Hero shield pills ---
    shield_pills = ""
    for fw in frameworks:
        small_icon = _framework_icon(fw["slug"]).replace(
            'width="32"', 'width="16"'
        ).replace('height="32"', 'height="16"')
        shield_pills += (
            f'<span class="shield-pill">{small_icon} {escape(fw["name"])}</span>\n'
        )

    year = datetime.now(timezone.utc).year
    today_display = datetime.now(timezone.utc).strftime("%b %d, %Y")

    # --- SVG icons for date cards ---
    svg_calendar = (
        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        'stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">'
        '<rect x="3" y="4" width="18" height="18" rx="2" ry="2"/>'
        '<line x1="16" y1="2" x2="16" y2="6"/>'
        '<line x1="8" y1="2" x2="8" y2="6"/>'
        '<line x1="3" y1="10" x2="21" y2="10"/>'
        '</svg>'
    )
    svg_clock = (
        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        'stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">'
        '<circle cx="12" cy="12" r="10"/>'
        '<polyline points="12 6 12 12 16 14"/>'
        '</svg>'
    )
    svg_check_shield = (
        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        'stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">'
        '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>'
        '<path d="M9 12l2 2 4-4"/>'
        '</svg>'
    )

    html = f'<!DOCTYPE html>\n'
    html += f'<html lang="en">\n'
    html += f'<head>\n'
    html += f'    <meta charset="UTF-8">\n'
    html += f'    <meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
    html += f'    <title>Trust Center \u2014 {escape(org_name)}</title>\n'
    html += f'    <style>{_CSS}</style>\n'
    html += f'</head>\n'
    html += f'<body>\n'
    html += f'\n'
    html += f'<header class="hero">\n'
    html += f'    <h1>{escape(org_name)} Trust Center</h1>\n'
    html += f'    <p class="subtitle">\n'
    html += f'        We are committed to protecting your data. This page provides an overview\n'
    html += f'        of our compliance posture and the security measures we have in place.\n'
    html += f'    </p>\n'
    html += f'    <div class="shield-row">\n'
    html += f'{shield_pills}'
    html += f'    </div>\n'
    html += f'    <p class="updated">Last updated {escape(generated_at)}</p>\n'
    html += f'</header>\n'
    html += f'\n'
    html += f'<section class="section">\n'
    html += f'    <h2 class="section-title">Compliance Frameworks</h2>\n'
    html += f'    <p class="section-desc">\n'
    html += f'        Frameworks we are actively pursuing or maintaining. Completion percentage\n'
    html += f'        reflects the ratio of fully implemented controls to total controls.\n'
    html += f'    </p>\n'
    html += f'    <div class="fw-grid">\n'
    html += f'{framework_cards}\n'
    html += f'    </div>\n'
    html += f'</section>\n'
    html += f'\n'
    html += f'<section class="section">\n'
    html += f'    <h2 class="section-title">Security Measures</h2>\n'
    html += f'    <p class="section-desc">\n'
    html += f'        A high-level overview of our security controls, evidence collection,\n'
    html += f'        and automated testing posture.\n'
    html += f'    </p>\n'
    html += f'    <div class="stats-grid">\n'
    html += f'        <div class="stat-card">\n'
    html += f'            <div class="stat-label">Controls Implemented</div>\n'
    html += f'            <div class="stat-value">{controls["complete"]}<span style="font-size:1rem;color:#94a3b8;">/{controls["total"]}</span></div>\n'
    html += f'            <div class="stat-sub">{controls_completion:.0f}% complete</div>\n'
    html += f'        </div>\n'
    html += f'        <div class="stat-card">\n'
    html += f'            <div class="stat-label">Evidence Items</div>\n'
    html += f'            <div class="stat-value">{evidence["total"]}</div>\n'
    html += f'            <div class="stat-sub">{evidence["current"]} current</div>\n'
    html += f'        </div>\n'
    html += f'        <div class="stat-card">\n'
    html += f'            <div class="stat-label">Automated Tests</div>\n'
    html += f'            <div class="stat-value">{tests["passing"]}<span style="font-size:1rem;color:#94a3b8;">/{tests["total"]}</span></div>\n'
    html += f'            <div class="stat-sub">{tests["pass_rate"]:.0f}% passing</div>\n'
    html += f'        </div>\n'
    html += f'        <div class="stat-card">\n'
    html += f'            <div class="stat-label">Open Risks</div>\n'
    html += f'            <div class="stat-value {risk_cls}">{risks["open"]}</div>\n'
    html += f'            <div class="stat-sub">{risks["mitigated"]} mitigated</div>\n'
    html += f'        </div>\n'
    html += f'    </div>\n'
    html += f'</section>\n'
    html += f'\n'
    html += f'<section class="section">\n'
    html += f'    <h2 class="section-title">Evidence Freshness</h2>\n'
    html += f'    <p class="section-desc">\n'
    html += f'        Evidence items are documents, screenshots, and automated outputs that\n'
    html += f'        demonstrate compliance. We track their validity to ensure nothing goes stale.\n'
    html += f'    </p>\n'
    html += f'    <div class="donut-wrapper">\n'
    html += f'        <div class="donut" style="background: conic-gradient('
    html += f'{ev_color} 0% {ev_pct}%, '
    html += f'#fbbf24 {ev_pct}% {ev_seg2_end:.1f}%, '
    html += f'#e2e8f0 {ev_seg2_end:.1f}% 100%'
    html += f');">\n'
    html += f'            <span style="background:#f8fafc;width:80px;height:80px;border-radius:50%;display:flex;align-items:center;justify-content:center;">\n'
    html += f'                {ev_pct:.0f}%\n'
    html += f'            </span>\n'
    html += f'        </div>\n'
    html += f'        <div class="donut-legend">\n'
    html += f'            <div class="donut-legend-item">\n'
    html += f'                <span class="donut-legend-dot" style="background:{ev_color};"></span>\n'
    html += f'                Current \u2014 {evidence["current"]} items\n'
    html += f'            </div>\n'
    html += f'            <div class="donut-legend-item">\n'
    html += f'                <span class="donut-legend-dot" style="background:#fbbf24;"></span>\n'
    html += f'                Expiring within 30 days \u2014 {evidence["expiring_soon"]} items\n'
    html += f'            </div>\n'
    html += f'            <div class="donut-legend-item">\n'
    html += f'                <span class="donut-legend-dot" style="background:#e2e8f0;"></span>\n'
    html += f'                Expired \u2014 {evidence["expired"]} items\n'
    html += f'            </div>\n'
    html += f'        </div>\n'
    html += f'    </div>\n'
    html += f'</section>\n'

    html += f'\n'
    html += f'<section class="section">\n'
    html += f'    <h2 class="section-title">Security Policies</h2>\n'
    html += f'    <p class="section-desc">\n'
    html += f'        Our documented policies define the rules and procedures we follow\n'
    html += f'        to keep your data safe.\n'
    html += f'    </p>\n'
    html += f'    <div class="policy-table-wrap">\n'
    html += f'        <table class="policy-table">\n'
    html += f'            <thead>\n'
    html += f'                <tr>\n'
    html += f'                    <th>Policy</th>\n'
    html += f'                    <th>Category</th>\n'
    html += f'                    <th>Version</th>\n'
    html += f'                    <th>Status</th>\n'
    html += f'                    <th>Approved</th>\n'
    html += f'                    <th>Next Review</th>\n'
    html += f'                </tr>\n'
    html += f'            </thead>\n'
    html += f'            <tbody>\n'
    html += f'{policy_rows}\n'
    html += f'            </tbody>\n'
    html += f'        </table>\n'
    html += f'    </div>\n'
    html += f'</section>\n'
    html += f'\n'
    html += f'<section class="section">\n'
    html += f'    <h2 class="section-title">Last Assessment</h2>\n'
    html += f'    <p class="section-desc">\n'
    html += f'        Key dates for our most recent compliance activities.\n'
    html += f'    </p>\n'
    html += f'    <div class="date-grid">\n'
    html += f'        <div class="date-card">\n'
    html += f'            <div class="date-icon">{svg_calendar}</div>\n'
    html += f'            <div class="date-info">\n'
    html += f'                <div class="date-label">Last Compliance Score</div>\n'
    html += f'                <div class="date-value">{_format_date(data["last_score_date"])}</div>\n'
    html += f'            </div>\n'
    html += f'        </div>\n'
    html += f'        <div class="date-card">\n'
    html += f'            <div class="date-icon">{svg_clock}</div>\n'
    html += f'            <div class="date-info">\n'
    html += f'                <div class="date-label">Last Security Scan</div>\n'
    html += f'                <div class="date-value">{_format_date(data["last_scan_date"])}</div>\n'
    html += f'            </div>\n'
    html += f'        </div>\n'
    html += f'        <div class="date-card">\n'
    html += f'            <div class="date-icon">{svg_check_shield}</div>\n'
    html += f'            <div class="date-info">\n'
    html += f'                <div class="date-label">Trust Center Generated</div>\n'
    html += f'                <div class="date-value">{today_display}</div>\n'
    html += f'            </div>\n'
    html += f'        </div>\n'
    html += f'    </div>\n'
    html += f'</section>\n'
    html += f'\n'
    html += f'<footer class="footer">\n'
    html += f'    <p>Generated by GRC Compliance Suite | OpenClaw</p>\n'
    html += f'    <p style="margin-top:4px;">\u00a9 {year} {escape(org_name)}. All rights reserved.</p>\n'
    html += f'</footer>\n'
    html += f'\n'
    html += f'</body>\n'
    html += f'</html>'

    return html

# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def generate_trust_center(db_path, output_dir, org_name):
    if not os.path.isfile(db_path):
        return {"status": "error", "error": "Database not found at " + db_path}

    os.makedirs(output_dir, exist_ok=True)

    conn = sqlite3.connect(db_path)
    conn.row_factory = _dict_factory

    try:
        data = collect_data(conn)
        html = build_html(data, org_name)

        output_path = os.path.join(output_dir, "trust-center.html")
        with open(output_path, "w", encoding="utf-8") as fh:
            fh.write(html)

        result = {
            "status": "generated",
            "path": os.path.abspath(output_path),
            "frameworks": len(data["frameworks"]),
            "policies": len(data["policies"]),
        }

    finally:
        conn.close()

    return result


def main():
    parser = argparse.ArgumentParser(
        description="Generate a static HTML trust center page."
    )
    parser.add_argument(
        "--db-path",
        default=DEFAULT_DB_PATH,
        help="Path to the compliance SQLite database",
    )
    parser.add_argument(
        "--output-dir",
        default=".",
        help="Directory to write trust-center.html into",
    )
    parser.add_argument(
        "--org-name",
        default="Our Organization",
        help="Organization name for the page title",
    )
    args = parser.parse_args()

    result = generate_trust_center(args.db_path, args.output_dir, args.org_name)
    print(json.dumps(result, indent=2))

    if result.get("status") == "error":
        sys.exit(1)


if __name__ == "__main__":
    main()
