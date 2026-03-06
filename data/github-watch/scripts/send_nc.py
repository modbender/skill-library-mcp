#!/usr/bin/env python3
"""
send_nc.py - Publie le digest GitHub Watch sur Nextcloud (Markdown).
Lit le JSON de l'agent (stdin) et ecrit via nextcloud-files skill.

Usage: echo '{...}' | python3 send_nc.py [--dry-run]
"""

import json
import sys
import argparse
import os
import subprocess
from datetime import datetime
from pathlib import Path

SKILL_BASE = Path(os.path.expanduser("~/.openclaw/workspace/skills"))
NC_SCRIPT  = SKILL_BASE / "nextcloud-files" / "scripts" / "nextcloud.py"
NC_PATH    = "/Jarvis/github-watch.md"

JOURS_FR = ["lundi","mardi","mercredi","jeudi","vendredi","samedi","dimanche"]
MOIS_FR  = ["janvier","fevrier","mars","avril","mai","juin",
             "juillet","aout","septembre","octobre","novembre","decembre"]

SECTION_EMOJI = ["En vogue", "SysOps / DevOps", "Topics", "Autres"]


def date_fr(dt=None):
    d = dt or datetime.now()
    return f"{JOURS_FR[d.weekday()]} {d.day} {MOIS_FR[d.month-1]} {d.year}"


def repos_table(repos):
    if not repos:
        return "_Aucun repo._\n"
    rows = [
        "| Repo | Lang | Stars | +Semaine | Description | Raison |",
        "|------|------|-------|----------|-------------|--------|",
    ]
    for r in repos:
        name   = r.get("name", "").replace("|", "\\|")
        url    = r.get("url", "")
        lang   = r.get("language", "") or ""
        stars  = str(r.get("stars_total", "") or "")
        gained = str(r.get("stars_gained", "") or "")
        desc   = (r.get("description", "") or "").replace("|", "\\|")[:80]
        reason = (r.get("reason", "") or "").replace("|", "\\|")
        linked = f"[{name}]({url})" if url else name
        gained_fmt = f"+{gained}" if gained and gained != "None" else ""
        rows.append(f"| {linked} | {lang} | {stars} | {gained_fmt} | {desc} | {reason} |")
    return "\n".join(rows) + "\n"


def highlights_section(highlights):
    if not highlights:
        return ""
    rows = [
        "| Repo | Pourquoi |",
        "|------|---------|",
    ]
    for r in highlights:
        name   = r.get("name", "").replace("|", "\\|")
        url    = r.get("url", "#")
        reason = (r.get("reason", "") or "").replace("|", "\\|")
        linked = f"[{name}]({url})" if url else name
        rows.append(f"| {linked} | {reason} |")
    return "## Highlights\n\n" + "\n".join(rows) + "\n\n"


def build_markdown(sections, highlights):
    today = date_fr()
    week  = datetime.now().strftime("S%V %Y")
    total = sum(len(s.get("repos", [])) for s in sections)

    lines = [
        f"# GitHub Watch - {week}",
        f"_{today} - {total} repos selectionnes_\n",
    ]

    lines.append(highlights_section(highlights))

    for sec in sections:
        name  = sec.get("name", "Section")
        repos = sec.get("repos", [])
        lines.append(f"## {name}\n")
        lines.append(repos_table(repos))

    lines.append(f"\n---\n_Genere par Jarvis le {datetime.now().strftime('%Y-%m-%d %H:%M')}_\n")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--nc-path", default=NC_PATH)
    args = parser.parse_args()

    try:
        raw = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f"[ERR] JSON stdin invalide: {e}", file=sys.stderr)
        sys.exit(1)

    sections   = raw.get("sections", [])
    highlights = raw.get("highlights", [])
    total = sum(len(s.get("repos", [])) for s in sections)

    if total == 0 and not highlights:
        print("[SKIP] Aucun repo - digest non publie.", file=sys.stderr)
        sys.exit(0)

    content = build_markdown(sections, highlights)

    if args.dry_run:
        print(content)
        return

    if not NC_SCRIPT.exists():
        print(f"[ERR] nextcloud-files skill non trouve: {NC_SCRIPT}", file=sys.stderr)
        sys.exit(1)

    # Pass content via stdin to avoid exposing it in process listings (ps)
    result = subprocess.run(
        [sys.executable, str(NC_SCRIPT), "write", args.nc_path],
        input=content, capture_output=True, text=True
    )
    if result.returncode == 0:
        print(f"[OK] Publie sur Nextcloud: {args.nc_path}")
    else:
        print(f"[ERR] Nextcloud: {result.stderr}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
