#!/usr/bin/env python3
"""
Prospect Tracker — deduplication and tracking for SEO prospect lead generation.

Tracks all researched prospects to prevent duplicate research and provide
coverage analytics across industries and clusters.

Usage:
    python3 prospect_tracker.py add --business "Name" --industry "X" --priority HIGH --file report.md
    python3 prospect_tracker.py check --business "Name" [--domain "x.com"]
    python3 prospect_tracker.py stats
    python3 prospect_tracker.py stale --days 30
    python3 prospect_tracker.py list [--industry "X"] [--priority HIGH] [--since 2026-02-01]
    python3 prospect_tracker.py blacklist add --business "Name" --domain "x.com" --reason "Why"
    python3 prospect_tracker.py blacklist check --business "Name"
    python3 prospect_tracker.py blacklist remove --business "Name"
    python3 prospect_tracker.py blacklist list
    python3 prospect_tracker.py outreach set --business "Name" --status draft_ready
    python3 prospect_tracker.py outreach list [--status sent]

Database: ~/.openclaw/workspace/leads/data/prospect-database.json
Blacklist: ~/.openclaw/workspace/leads/data/blacklist.json
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date, datetime, timedelta
from pathlib import Path
from difflib import SequenceMatcher

DB_PATH = Path.home() / ".openclaw" / "workspace" / "leads" / "data" / "prospect-database.json"
BLACKLIST_PATH = Path.home() / ".openclaw" / "workspace" / "leads" / "data" / "blacklist.json"


def load_blacklist() -> dict:
    if BLACKLIST_PATH.exists():
        return json.loads(BLACKLIST_PATH.read_text())
    return {"version": 1, "businesses": [], "domains": []}


def save_blacklist(bl: dict) -> None:
    BLACKLIST_PATH.parent.mkdir(parents=True, exist_ok=True)
    BLACKLIST_PATH.write_text(json.dumps(bl, indent=2, default=str))


def is_blacklisted(business_name: str, domain: str = "") -> dict | None:
    """Check if a business or domain is blacklisted. Returns the entry if found."""
    bl = load_blacklist()
    norm = normalize_name(business_name)
    for entry in bl["businesses"]:
        if fuzzy_match(business_name, entry["name"]) > 0.8:
            return entry
    if domain:
        domain = domain.lower().strip().replace("https://", "").replace("http://", "").rstrip("/")
        for d in bl["domains"]:
            if domain == d.get("domain", "").lower():
                return d
        for entry in bl["businesses"]:
            if entry.get("domain") and domain == entry["domain"].lower():
                return entry
    return None


def load_db() -> dict:
    if DB_PATH.exists():
        return json.loads(DB_PATH.read_text())
    return {"version": 1, "prospects": [], "stats": {"total_added": 0, "duplicates_prevented": 0}}


def save_db(db: dict) -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    DB_PATH.write_text(json.dumps(db, indent=2, default=str))


def normalize_name(name: str) -> str:
    """Normalize business name for fuzzy matching."""
    name = name.lower().strip()
    # Remove common suffixes
    for suffix in ["llc", "inc", "corp", "ltd", "co", "company", "the"]:
        name = name.replace(suffix, "")
    # Remove punctuation and extra whitespace
    name = "".join(c if c.isalnum() or c == " " else " " for c in name)
    return " ".join(name.split())


def fuzzy_match(a: str, b: str) -> float:
    """Return similarity ratio between two business names (0-1)."""
    return SequenceMatcher(None, normalize_name(a), normalize_name(b)).ratio()


def find_existing(db: dict, business_name: str, days: int = 14) -> dict | None:
    """Find an existing prospect researched within `days` days."""
    cutoff = (date.today() - timedelta(days=days)).isoformat()
    for p in db["prospects"]:
        if p.get("date", "") >= cutoff and fuzzy_match(business_name, p["business"]) > 0.8:
            return p
    return None


def cmd_add(args) -> None:
    # Check blacklist first
    domain = args.domain or ""
    blocked = is_blacklisted(args.business, domain)
    if blocked:
        print(json.dumps({
            "status": "blacklisted",
            "message": f"Blocked: {blocked.get('reason', 'blacklisted')}",
            "entry": blocked
        }, indent=2))
        return

    db = load_db()
    existing = find_existing(db, args.business, days=14)
    if existing:
        db["stats"]["duplicates_prevented"] = db["stats"].get("duplicates_prevented", 0) + 1
        save_db(db)
        print(json.dumps({
            "status": "duplicate",
            "message": f"Already researched on {existing['date']}",
            "existing": existing
        }, indent=2))
        return

    prospect = {
        "business": args.business,
        "industry": args.industry or "unknown",
        "priority": (args.priority or "MEDIUM").upper(),
        "date": args.date or date.today().isoformat(),
        "report_file": args.file or "",
        "cluster": args.cluster or "",
        "source": args.source or "klw-directory",
        "domain": args.domain or "",
    }
    db["prospects"].append(prospect)
    db["stats"]["total_added"] = db["stats"].get("total_added", 0) + 1
    save_db(db)
    print(json.dumps({"status": "added", "prospect": prospect}, indent=2))


def cmd_check(args) -> None:
    # Check blacklist first
    domain = args.domain if hasattr(args, "domain") and args.domain else ""
    blocked = is_blacklisted(args.business, domain)
    if blocked:
        print(json.dumps({"found": True, "blacklisted": True, "reason": blocked.get("reason", "blacklisted"), "entry": blocked}, indent=2))
        return

    db = load_db()
    days = args.days if hasattr(args, "days") and args.days else 14
    existing = find_existing(db, args.business, days=days)
    if existing:
        print(json.dumps({"found": True, "blacklisted": False, "prospect": existing}, indent=2))
    else:
        print(json.dumps({"found": False, "blacklisted": False}, indent=2))


def cmd_stats(args) -> None:
    db = load_db()
    prospects = db["prospects"]
    total = len(prospects)

    # Industry coverage
    industries = {}
    for p in prospects:
        ind = p.get("industry", "unknown")
        industries[ind] = industries.get(ind, 0) + 1

    # Priority breakdown
    priorities = {}
    for p in prospects:
        pri = p.get("priority", "MEDIUM")
        priorities[pri] = priorities.get(pri, 0) + 1

    # Cluster coverage
    clusters = {}
    for p in prospects:
        cl = p.get("cluster", "")
        if cl:
            clusters[cl] = clusters.get(cl, 0) + 1

    # Recent activity (last 7 days)
    week_ago = (date.today() - timedelta(days=7)).isoformat()
    recent = [p for p in prospects if p.get("date", "") >= week_ago]

    # Date range
    dates = [p.get("date", "") for p in prospects if p.get("date")]
    date_range = f"{min(dates)} to {max(dates)}" if dates else "none"

    stats = {
        "total_prospects": total,
        "duplicates_prevented": db["stats"].get("duplicates_prevented", 0),
        "industries_covered": len(industries),
        "industry_breakdown": dict(sorted(industries.items(), key=lambda x: -x[1])),
        "priority_breakdown": priorities,
        "clusters_covered": len(clusters),
        "cluster_breakdown": dict(sorted(clusters.items(), key=lambda x: -x[1])) if clusters else {},
        "recent_7_days": len(recent),
        "date_range": date_range,
    }
    print(json.dumps(stats, indent=2))


def cmd_stale(args) -> None:
    db = load_db()
    days = args.days if hasattr(args, "days") and args.days else 30
    cutoff = (date.today() - timedelta(days=days)).isoformat()
    stale = [p for p in db["prospects"] if p.get("date", "") < cutoff]
    stale.sort(key=lambda x: x.get("date", ""))
    print(json.dumps({"stale_count": len(stale), "prospects": stale}, indent=2))


def cmd_list(args) -> None:
    db = load_db()
    prospects = db["prospects"]

    # Filters
    if hasattr(args, "industry") and args.industry:
        prospects = [p for p in prospects if args.industry.lower() in p.get("industry", "").lower()]
    if hasattr(args, "priority") and args.priority:
        prospects = [p for p in prospects if p.get("priority", "").upper() == args.priority.upper()]
    if hasattr(args, "since") and args.since:
        prospects = [p for p in prospects if p.get("date", "") >= args.since]
    if hasattr(args, "cluster") and args.cluster:
        prospects = [p for p in prospects if args.cluster.lower() in p.get("cluster", "").lower()]

    prospects.sort(key=lambda x: x.get("date", ""), reverse=True)
    print(json.dumps({"count": len(prospects), "prospects": prospects}, indent=2))


def cmd_blacklist(args) -> None:
    """Manage the prospect blacklist."""
    action = args.action if hasattr(args, "action") and args.action else "list"

    if action == "add":
        if not args.business and not args.domain:
            print(json.dumps({"error": "Need --business or --domain"}))
            return
        bl = load_blacklist()
        entry = {
            "name": args.business or "",
            "domain": (args.domain or "").lower().strip(),
            "reason": args.reason or "No reason provided",
            "added": date.today().isoformat(),
        }
        bl["businesses"].append(entry)
        save_blacklist(bl)
        print(json.dumps({"status": "added", "entry": entry}, indent=2))

    elif action == "check":
        if not args.business:
            print(json.dumps({"error": "Need --business"}))
            return
        domain = args.domain if hasattr(args, "domain") and args.domain else ""
        blocked = is_blacklisted(args.business, domain)
        if blocked:
            print(json.dumps({"blocked": True, "entry": blocked}, indent=2))
        else:
            print(json.dumps({"blocked": False}, indent=2))

    elif action == "remove":
        if not args.business:
            print(json.dumps({"error": "Need --business"}))
            return
        bl = load_blacklist()
        before = len(bl["businesses"])
        bl["businesses"] = [b for b in bl["businesses"] if fuzzy_match(args.business, b["name"]) <= 0.8]
        removed = before - len(bl["businesses"])
        save_blacklist(bl)
        print(json.dumps({"status": "removed", "count": removed}, indent=2))

    else:  # list
        bl = load_blacklist()
        print(json.dumps({
            "businesses": bl["businesses"],
            "domains": bl.get("domains", []),
            "total": len(bl["businesses"]) + len(bl.get("domains", []))
        }, indent=2))


OUTREACH_STATUSES = [
    "draft_ready", "pending_review", "approved", "sent",
    "followed_up", "responded", "closed",
]


def cmd_outreach(args) -> None:
    """Manage outreach status for prospects."""
    action = args.action if hasattr(args, "action") and args.action else "list"

    db = load_db()

    if action == "set":
        if not args.business:
            print(json.dumps({"error": "Need --business"}))
            return
        if not args.status:
            print(json.dumps({"error": "Need --status", "valid": OUTREACH_STATUSES}))
            return
        if args.status not in OUTREACH_STATUSES:
            print(json.dumps({"error": f"Invalid status: {args.status}", "valid": OUTREACH_STATUSES}))
            return

        found = False
        for p in db["prospects"]:
            if fuzzy_match(args.business, p["business"]) > 0.8:
                p["outreach_status"] = args.status
                p["outreach_updated"] = date.today().isoformat()
                if args.email:
                    p["contact_email"] = args.email
                if args.note:
                    p.setdefault("outreach_notes", []).append({
                        "date": date.today().isoformat(),
                        "note": args.note,
                    })
                found = True
                save_db(db)
                print(json.dumps({"status": "updated", "prospect": p}, indent=2))
                break

        if not found:
            print(json.dumps({"status": "not_found", "business": args.business}))

    else:  # list
        prospects = db["prospects"]

        # Filter by outreach status
        if hasattr(args, "status") and args.status:
            prospects = [p for p in prospects if p.get("outreach_status") == args.status]
        else:
            # Show all prospects that have any outreach status
            prospects = [p for p in prospects if p.get("outreach_status")]

        # Also filter by priority if requested
        if hasattr(args, "priority") and args.priority:
            prospects = [p for p in prospects if p.get("priority", "").upper() == args.priority.upper()]

        prospects.sort(key=lambda x: x.get("outreach_updated", ""), reverse=True)

        summary = {
            "count": len(prospects),
            "by_status": {},
            "prospects": prospects,
        }
        for p in prospects:
            st = p.get("outreach_status", "none")
            summary["by_status"][st] = summary["by_status"].get(st, 0) + 1

        print(json.dumps(summary, indent=2))


def cmd_outreach_ready(args) -> None:
    """List HIGH/MEDIUM-HIGH prospects not yet in outreach pipeline."""
    db = load_db()
    candidates = [
        p for p in db["prospects"]
        if p.get("priority", "").upper() in ("HIGH", "MEDIUM-HIGH", "MEDIUM_HIGH")
        and not p.get("outreach_status")
    ]
    candidates.sort(key=lambda x: x.get("date", ""), reverse=True)
    print(json.dumps({"count": len(candidates), "prospects": candidates}, indent=2))


def cmd_today_clusters(args) -> None:
    """Show which clusters are scheduled for today based on rotation."""
    rotation_path = Path.home() / ".openclaw" / "workspace" / "leads" / "data" / "cluster-rotation.json"
    if not rotation_path.exists():
        print(json.dumps({"error": "cluster-rotation.json not found"}))
        return

    rotation = json.loads(rotation_path.read_text())
    today = date.today()
    weekday = today.strftime("%A").lower()

    # Calculate which week in the 2-week cycle (0 or 1)
    # Use ISO week number mod 2
    cycle_week = today.isocalendar()[1] % 2  # 0 = even week, 1 = odd week

    schedule = rotation.get("schedule", {})
    week_key = f"week_{cycle_week + 1}"
    day_schedule = schedule.get(week_key, {}).get(weekday, {})

    result = {
        "date": today.isoformat(),
        "weekday": weekday,
        "cycle_week": cycle_week + 1,
        "runs": {}
    }

    for run_key, cluster_id in day_schedule.items():
        cluster = None
        for c in rotation.get("clusters", []):
            if c["id"] == cluster_id:
                cluster = c
                break
        if cluster:
            result["runs"][run_key] = {
                "cluster_id": cluster_id,
                "cluster_name": cluster["name"],
                "industries": cluster["industries"],
                "tier": cluster["tier"],
                "serp_first": cluster.get("serp_first", False),
                "klw_filter": cluster.get("klw_filter", []),
                "serp_keywords": cluster.get("serp_keywords", []),
            }

    print(json.dumps(result, indent=2))


def main():
    parser = argparse.ArgumentParser(description="SEO Prospect Tracker")
    sub = parser.add_subparsers(dest="command")

    # add
    p_add = sub.add_parser("add", help="Record a new prospect")
    p_add.add_argument("--business", required=True, help="Business name")
    p_add.add_argument("--industry", help="Industry category")
    p_add.add_argument("--priority", help="HIGH, MEDIUM, or LOW")
    p_add.add_argument("--date", help="Research date (YYYY-MM-DD)")
    p_add.add_argument("--file", help="Path to report file")
    p_add.add_argument("--cluster", help="Cluster name from rotation")
    p_add.add_argument("--source", help="Data source (klw-directory, serp, perplexity)")
    p_add.add_argument("--domain", help="Website domain")

    # check
    p_check = sub.add_parser("check", help="Check if a prospect was recently researched or blacklisted")
    p_check.add_argument("--business", required=True, help="Business name")
    p_check.add_argument("--domain", help="Website domain")
    p_check.add_argument("--days", type=int, default=14, help="Look-back window in days")

    # stats
    sub.add_parser("stats", help="Show coverage statistics")

    # stale
    p_stale = sub.add_parser("stale", help="List prospects ripe for re-research")
    p_stale.add_argument("--days", type=int, default=30, help="Staleness threshold")

    # list
    p_list = sub.add_parser("list", help="List prospects with filters")
    p_list.add_argument("--industry", help="Filter by industry")
    p_list.add_argument("--priority", help="Filter by priority")
    p_list.add_argument("--since", help="Only after this date (YYYY-MM-DD)")
    p_list.add_argument("--cluster", help="Filter by cluster name")

    # blacklist
    p_bl = sub.add_parser("blacklist", help="Manage prospect blacklist")
    p_bl.add_argument("action", nargs="?", default="list", choices=["add", "check", "remove", "list"])
    p_bl.add_argument("--business", help="Business name")
    p_bl.add_argument("--domain", help="Website domain")
    p_bl.add_argument("--reason", help="Why this business is blacklisted")

    # today-clusters
    sub.add_parser("today-clusters", help="Show today's scheduled clusters from rotation")

    # outreach
    p_out = sub.add_parser("outreach", help="Manage outreach status for prospects")
    p_out.add_argument("action", nargs="?", default="list", choices=["set", "list"])
    p_out.add_argument("--business", help="Business name")
    p_out.add_argument("--status", help="Outreach status: draft_ready, pending_review, approved, sent, followed_up, responded, closed")
    p_out.add_argument("--email", help="Contact email address")
    p_out.add_argument("--note", help="Add a note to the outreach history")
    p_out.add_argument("--priority", help="Filter by priority (for list)")

    # outreach-ready
    sub.add_parser("outreach-ready", help="List HIGH/MEDIUM-HIGH prospects not yet in outreach")

    args = parser.parse_args()

    commands = {
        "add": cmd_add,
        "check": cmd_check,
        "stats": cmd_stats,
        "stale": cmd_stale,
        "list": cmd_list,
        "blacklist": cmd_blacklist,
        "today-clusters": cmd_today_clusters,
        "outreach": cmd_outreach,
        "outreach-ready": cmd_outreach_ready,
    }

    if args.command in commands:
        commands[args.command](args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
