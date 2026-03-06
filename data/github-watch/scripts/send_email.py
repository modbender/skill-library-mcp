#!/usr/bin/env python3
"""
send_email.py - Envoie le digest GitHub Watch par email via mail-client skill.
Lit le JSON de l'agent (stdin).

Usage: echo '{...}' | python3 send_email.py [--to addr] [--dry-run]
"""

import json
import sys
import argparse
import os
import importlib.util
import html
from datetime import datetime, date
from pathlib import Path

SKILL_BASE  = Path(os.path.expanduser("~/.openclaw/workspace/skills"))
MAIL_SCRIPT = SKILL_BASE / "mail-client" / "scripts" / "mail.py"
RECIPIENT   = "romain@rwx-g.fr"

JOURS_FR = ["lundi","mardi","mercredi","jeudi","vendredi","samedi","dimanche"]
MOIS_FR  = ["janvier","fevrier","mars","avril","mai","juin",
             "juillet","aout","septembre","octobre","novembre","decembre"]
SECTION_COLORS = ["#6366f1", "#0ea5e9", "#10b981", "#f59e0b"]


def date_fr(dt=None):
    d = dt or datetime.now()
    return f"{JOURS_FR[d.weekday()]} {d.day} {MOIS_FR[d.month-1]} {d.year}"


def format_repo_rows(repos, accent):
    rows = ""
    for r in repos:
        name         = html.escape(r.get("name", ""))
        url          = html.escape(r.get("url", "#"), quote=True)
        description  = html.escape((r.get("description", "") or ""))
        language     = html.escape((r.get("language", "") or ""))
        stars_total  = html.escape(str(r.get("stars_total", "") or ""))
        stars_gained = r.get("stars_gained")
        reason       = html.escape((r.get("reason", "") or ""))

        meta_parts = []
        if language:
            meta_parts.append(language)
        if stars_total:
            meta_parts.append(f"⭐ {stars_total}")
        if stars_gained and str(stars_gained) not in ("None", "?", ""):
            meta_parts.append(f"+{stars_gained} cette semaine")
        meta = " &nbsp;·&nbsp; ".join(meta_parts)

        rows += f"""
          <tr>
            <td style="padding:8px 0 16px 0;border-bottom:1px solid #f3f4f6;">
              <a href="{url}" style="font-size:14px;font-weight:600;color:{accent};text-decoration:none;">{name}</a>
              <div style="font-size:11px;color:#9ca3af;margin-top:2px;">{meta}</div>
              {f'<div style="font-size:13px;color:#4b5563;margin-top:4px;">{description}</div>' if description else ''}
              {f'<div style="font-size:12px;color:#6b7280;margin-top:6px;font-style:italic;">{reason}</div>' if reason else ''}
            </td>
          </tr>"""
    return rows


def format_highlights(highlights):
    if not highlights:
        return ""
    rows = ""
    for r in highlights:
        name   = html.escape(r.get("name", ""))
        url    = html.escape(r.get("url", "#"), quote=True)
        reason = html.escape((r.get("reason", "") or ""))
        rows += f"""
          <tr>
            <td style="padding:0 0 14px 14px;border-left:3px solid #f59e0b;">
              <a href="{url}" style="font-size:14px;font-weight:600;color:#111827;text-decoration:none;display:block;">{name}</a>
              <div style="font-size:13px;color:#92400e;margin-top:4px;">{reason}</div>
            </td>
          </tr>"""
    return f"""
      <tr><td style="padding:20px 0 12px 0;border-bottom:2px solid #f59e0b;">
        <span style="font-size:12px;font-weight:700;color:#92400e;text-transform:uppercase;">Highlights</span>
      </td></tr>
      <tr><td style="background:#fffbeb;border-radius:6px;padding:4px 0;">
        <table width="100%" cellpadding="0" cellspacing="0">{rows}</table>
      </td></tr>"""


def format_html(sections, highlights):
    today = date_fr()
    total = sum(len(s.get("repos", [])) for s in sections)
    body  = format_highlights(highlights)

    for i, sec in enumerate(sections):
        accent = SECTION_COLORS[i % len(SECTION_COLORS)]
        name   = html.escape(sec.get("name", f"Section {i+1}"))
        repos  = sec.get("repos", [])
        rows   = format_repo_rows(repos, accent)
        body += f"""
      <tr><td style="padding:20px 0 12px 0;">
        <span style="font-size:12px;font-weight:700;color:#374151;text-transform:uppercase;">{name}</span>
        <span style="font-size:11px;color:#9ca3af;"> ({len(repos)})</span>
      </td></tr>
      <tr><td><table width="100%" cellpadding="0" cellspacing="0">{rows}</table></td></tr>"""

    return f"""<!DOCTYPE html><html lang="fr"><head><meta charset="utf-8"></head>
<body style="margin:0;padding:0;background:#f3f4f6;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;">
<table width="100%" cellpadding="0" cellspacing="0"><tr><td style="padding:24px 16px;">
<table width="100%" cellpadding="0" cellspacing="0" style="max-width:800px;margin:0 auto;background:#fff;border-radius:10px;border:1px solid #e5e7eb;">
  <tr><td style="padding:24px 32px 16px 32px;border-bottom:1px solid #f3f4f6;">
    <div style="font-size:11px;color:#9ca3af;text-transform:uppercase;">{today}</div>
    <div style="font-size:22px;font-weight:800;color:#111827;">GitHub Watch</div>
    <div style="font-size:13px;color:#6b7280;margin-top:4px;">{total} repos selectionnes</div>
  </td></tr>
  <tr><td style="padding:8px 32px 24px 32px;">
    <table width="100%" cellpadding="0" cellspacing="0">{body}</table>
  </td></tr>
  <tr><td style="padding:14px 32px;background:#f9fafb;border-top:1px solid #f3f4f6;">
    <div style="font-size:11px;color:#9ca3af;">Jarvis - GitHub Watch hebdomadaire - {datetime.now().strftime('%H:%M')}</div>
  </td></tr>
</table></td></tr></table></body></html>"""


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--to", default=RECIPIENT)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    try:
        raw = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f"[ERR] JSON stdin: {e}", file=sys.stderr)
        sys.exit(1)

    sections   = raw.get("sections", [])
    highlights = raw.get("highlights", [])
    total = sum(len(s.get("repos", [])) for s in sections)

    if total == 0 and not highlights:
        print("[SKIP] Aucun repo - email non envoye.", file=sys.stderr)
        sys.exit(0)

    body = format_html(sections, highlights)
    week = datetime.now().strftime("S%V %Y")

    if args.dry_run:
        print(f"[DRY-RUN] Email vers {args.to} - {total} repos, {len(highlights)} highlights")
        return

    if not MAIL_SCRIPT.exists():
        print(f"[ERR] mail-client skill non trouve: {MAIL_SCRIPT}", file=sys.stderr)
        sys.exit(1)

    # Ecrire le HTML dans un fichier temporaire pour --attachment
    # Import mail-client module directly to avoid exposing content in process listings (ps)
    spec = importlib.util.spec_from_file_location("mail", str(MAIL_SCRIPT))
    mail_mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mail_mod)
    client = mail_mod.MailClient()
    result_data = client.send(
        to=args.to,
        subject=f"GitHub Watch - {week}",
        body=f"GitHub Watch {week} - {total} repos selectionnes.",
        html=body,
    )
    class _Result:
        returncode = 0 if result_data.get("status") == "ok" else 1
        stderr = result_data.get("error", "")
    result = _Result()

    if result.returncode == 0:
        print(f"[OK] Email envoye a {args.to}")
    else:
        print(f"[ERR] mail-client: {result.stderr}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
