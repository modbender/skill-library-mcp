#!/usr/bin/env python3
"""
cross_skill.py — Event prep context fetcher (GitHub PRs + Notion pages).

Fetches read-only context to enrich meeting prep check-ins. This file does NOT
read other skills' credentials, config files, tokens, or stored data. It only:
  1. Checks if a SKILL.md file exists for "github" or "notion" (presence check only,
     file is NOT read — used to decide whether to attempt the integration).
  2. Calls the `gh` CLI for open PRs/issues (your existing gh auth, read-only).
  3. Searches Notion via NOTION_API_KEY env var (read-only page titles + URLs).
All integrations are opt-in (feature_cross_skill=false by default in config.json).

COMPLETE NETWORK CALL AUDIT — every outbound call in this file:
  1. get_github_context(): subprocess ["gh", "pr", "list", ...] and ["gh", "issue", "list", ...]
     READ-ONLY. Auth handled by gh CLI (never by this script).
     Receives: PR/issue titles, states, URLs only. No data written back.
     Gated by: gh CLI installed + authenticated AND github SKILL.md present locally.

  2. get_notion_context(): POST https://api.notion.com/v1/search
     READ-ONLY. Sends: NOTION_API_KEY env var (Bearer token) + event title (first 50 chars).
     Receives: matching page titles and URLs only. No data written back.
     Gated by: NOTION_API_KEY env var set AND notion SKILL.md present locally.

  3. NO other network calls. No telemetry, no analytics, no calls home.
     pending_nudges.json is read/written locally under skill dir only — never transmitted.
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

if sys.version_info < (3, 8):
    print(json.dumps({"error": "python_version_too_old", "detail": f"Python 3.8+ required."}))
    sys.exit(1)

SKILL_DIR = Path.home() / ".openclaw/workspace/skills/proactive-claw"
SKILLS_ROOT = Path.home() / ".openclaw/workspace/skills"


def _integration_installed(name: str) -> bool:
    """Presence-only check: returns True if a SKILL.md file exists for the named skill.
    The file is NOT opened or read — this only checks whether the skill directory exists
    so we know whether to attempt the GitHub/Notion integration below."""
    return (SKILLS_ROOT / name / "SKILL.md").exists()


def available_integrations() -> list:
    """Return which optional integrations (github, notion) are locally installed.
    Only checks for SKILL.md file presence — does NOT read any other skill's data."""
    integrable = ["github", "notion", "slack", "discord", "apple-notes", "summarize"]
    return [s for s in integrable if _integration_installed(s)]


def get_github_context(event_title: str) -> dict:
    """Pull recent GitHub activity relevant to the event."""
    try:
        # Recent PRs
        result = subprocess.run(
            ["gh", "pr", "list", "--limit", "5", "--json",
             "title,state,updatedAt,url,reviewDecision"],
            capture_output=True, text=True, timeout=10
        )
        prs = json.loads(result.stdout) if result.returncode == 0 else []

        # Recent issues assigned to me
        result2 = subprocess.run(
            ["gh", "issue", "list", "--assignee", "@me", "--limit", "5",
             "--json", "title,state,updatedAt,url"],
            capture_output=True, text=True, timeout=10
        )
        issues = json.loads(result2.stdout) if result2.returncode == 0 else []

        # Filter to items updated in last 3 days
        cutoff = (datetime.now(timezone.utc) - timedelta(days=3)).isoformat()
        recent_prs = [p for p in prs if p.get("updatedAt", "") >= cutoff]
        recent_issues = [i for i in issues if i.get("updatedAt", "") >= cutoff]

        if not recent_prs and not recent_issues:
            return {}

        context_lines = []
        if recent_prs:
            context_lines.append(f"**Open PRs ({len(recent_prs)}):** " +
                                  ", ".join(p["title"] for p in recent_prs[:3]))
        if recent_issues:
            context_lines.append(f"**Open Issues ({len(recent_issues)}):** " +
                                  ", ".join(i["title"] for i in recent_issues[:3]))

        return {
            "skill": "github",
            "context": "\n".join(context_lines),
            "prs": recent_prs[:3],
            "issues": recent_issues[:3],
        }
    except Exception:
        return {}


def get_notion_context(event_title: str) -> dict:
    """Search Notion for pages related to the event title."""
    notion_key = os.environ.get("NOTION_API_KEY", "")
    if not notion_key:
        return {}
    try:
        import urllib.request
        query = event_title[:50]
        payload = json.dumps({"query": query, "page_size": 3}).encode()
        req = urllib.request.Request(
            "https://api.notion.com/v1/search",
            data=payload,
            headers={
                "Authorization": f"Bearer {notion_key}",
                "Content-Type": "application/json",
                "Notion-Version": "2022-06-28",
            }
        )
        resp = json.loads(urllib.request.urlopen(req, timeout=8).read())
        results = resp.get("results", [])
        if not results:
            return {}
        pages = []
        for r in results[:3]:
            title = ""
            props = r.get("properties", {})
            for v in props.values():
                if v.get("type") == "title":
                    texts = v.get("title", [])
                    title = "".join(t.get("plain_text", "") for t in texts)
                    break
            if title:
                pages.append({"title": title, "url": r.get("url", "")})
        if not pages:
            return {}
        return {
            "skill": "notion",
            "context": "**Notion pages:** " + ", ".join(p["title"] for p in pages),
            "pages": pages,
        }
    except Exception:
        return {}


def get_pending_nudges() -> list:
    """Return unshown nudges from daemon — consumed by OpenClaw on conversation open."""
    nudges_file = SKILL_DIR / "pending_nudges.json"
    if not nudges_file.exists():
        return []
    try:
        nudges = json.loads(nudges_file.read_text())
        unshown = [n for n in nudges if not n.get("shown")]
        if unshown:
            # Mark all as shown
            for n in nudges:
                n["shown"] = True
            nudges_file.write_text(json.dumps(nudges, indent=2))
        return unshown
    except Exception:
        return []


def enrich_event(event_title: str, event_type: str) -> dict:
    """Fetch GitHub PR/issue and Notion page context for an event title.
    Only calls GitHub CLI and/or Notion API — does not access any other skill's data."""
    enrichments = []
    available = available_integrations()

    if "github" in available:
        ctx = get_github_context(event_title)
        if ctx:
            enrichments.append(ctx)

    if "notion" in available:
        ctx = get_notion_context(event_title)
        if ctx:
            enrichments.append(ctx)

    # Build combined context block
    if not enrichments:
        return {"event_title": event_title, "enrichments": [], "context_block": ""}

    context_block = "\n\n".join(e["context"] for e in enrichments if e.get("context"))

    return {
        "event_title": event_title,
        "event_type": event_type,
        "enrichments": enrichments,
        "context_block": context_block,
        "skills_used": [e["skill"] for e in enrichments],
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--event-title", default="")
    parser.add_argument("--event-type", default="one_off_standard")
    parser.add_argument("--list-available", action="store_true")
    parser.add_argument("--pending-nudges", action="store_true")
    args = parser.parse_args()

    if args.list_available:
        print(json.dumps({"available_integrations": available_integrations()}, indent=2))
    elif args.pending_nudges:
        print(json.dumps({"pending_nudges": get_pending_nudges()}, indent=2))
    elif args.event_title:
        print(json.dumps(enrich_event(args.event_title, args.event_type), indent=2))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
