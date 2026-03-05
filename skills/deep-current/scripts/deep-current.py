#!/usr/bin/env python3
"""
Deep Current — Autonomous research thread manager.

A CLI for maintaining long-running research threads across sessions.
Uses only Python stdlib. Data lives in ../deep-current/currents.json.

Usage:
    python deep-current.py <command> [args...]

Commands:
    list                          Show all threads with status
    show <id>                     Display full thread details
    add <title>                   Create a new research thread
    note <id> <text>              Add a dated research note
    source <id> <url> [desc]      Add a source/reference
    finding <id> <text>           Add a key finding
    status <id> <status>          Set status (active/paused/resolved)
    digest                        Summary of all active threads
"""

import json
import sys
import os
import re
from datetime import date
from pathlib import Path

# Resolve data file: check workspace first, fall back to skill-relative path
_WORKSPACE = Path.home() / ".openclaw" / "workspace" / "deep-current" / "currents.json"
_SKILL_RELATIVE = Path(__file__).resolve().parent.parent / "deep-current" / "currents.json"
DATA_FILE = _WORKSPACE if _WORKSPACE.exists() else _SKILL_RELATIVE


def load():
    """Load currents.json, returning the full data dict."""
    with open(DATA_FILE, "r") as f:
        return json.load(f)


def save(data):
    """Write data back to currents.json."""
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)
        f.write("\n")


def find_thread(data, thread_id):
    """Find a thread by id (exact or prefix match)."""
    for t in data["threads"]:
        if t["id"] == thread_id:
            return t
    # Try prefix match
    matches = [t for t in data["threads"] if t["id"].startswith(thread_id)]
    if len(matches) == 1:
        return matches[0]
    if len(matches) > 1:
        print(f"Ambiguous id '{thread_id}'. Matches: {', '.join(t['id'] for t in matches)}")
        sys.exit(1)
    print(f"No thread found with id '{thread_id}'")
    sys.exit(1)


def slugify(title):
    """Turn a title into a URL-safe id slug."""
    s = title.lower().strip()
    s = re.sub(r"[^a-z0-9\s-]", "", s)
    s = re.sub(r"[\s-]+", "-", s)
    return s[:60].strip("-")


def today():
    return date.today().isoformat()


# ── Commands ──────────────────────────────────────────────────────

def cmd_list(data, args):
    """Show all threads with status."""
    if not data["threads"]:
        print("No research threads yet.")
        return
    status_icons = {"active": "🌊", "paused": "⏸️ ", "resolved": "✅"}
    for t in data["threads"]:
        icon = status_icons.get(t["status"], "?")
        notes_count = len(t.get("notes", []))
        print(f"  {icon} [{t['id']}] {t['title']}  ({notes_count} notes, {t['status']})")


def cmd_show(data, args):
    """Display full thread details."""
    if not args:
        print("Usage: show <id>")
        return
    t = find_thread(data, args[0])
    print(f"\n{'=' * 60}")
    print(f"  {t['title']}")
    print(f"  id: {t['id']}  |  status: {t['status']}")
    print(f"  created: {t['created']}  |  updated: {t['last_updated']}")
    print(f"{'=' * 60}")

    if t.get("key_findings"):
        print("\n  ⚡ Key Findings:")
        for f in t["key_findings"]:
            print(f"    • {f}")

    if t.get("notes"):
        print(f"\n  📝 Notes ({len(t['notes'])}):")
        for n in t["notes"]:
            print(f"\n    [{n['date']}]")
            for line in n["text"].split("\n"):
                print(f"    {line}")

    if t.get("sources"):
        print(f"\n  📚 Sources ({len(t['sources'])}):")
        for s in t["sources"]:
            desc = f" — {s['description']}" if s.get("description") else ""
            print(f"    • {s['url']}{desc}")

    print()


def cmd_add(data, args):
    """Create a new research thread."""
    if not args:
        print("Usage: add <title>")
        return
    title = " ".join(args)
    tid = slugify(title)
    # Check for duplicate
    if any(t["id"] == tid for t in data["threads"]):
        print(f"Thread '{tid}' already exists.")
        return
    thread = {
        "id": tid,
        "title": title,
        "status": "active",
        "created": today(),
        "last_updated": today(),
        "notes": [],
        "sources": [],
        "key_findings": [],
    }
    data["threads"].append(thread)
    save(data)
    print(f"🌊 Created thread: [{tid}] {title}")


def cmd_note(data, args):
    """Add a research note to a thread."""
    if len(args) < 2:
        print("Usage: note <id> <text>")
        return
    t = find_thread(data, args[0])
    text = " ".join(args[1:])
    t["notes"].append({"date": today(), "text": text})
    t["last_updated"] = today()
    save(data)
    print(f"📝 Note added to [{t['id']}]")


def cmd_source(data, args):
    """Add a source to a thread."""
    if len(args) < 2:
        print("Usage: source <id> <url> [description]")
        return
    t = find_thread(data, args[0])
    url = args[1]
    desc = " ".join(args[2:]) if len(args) > 2 else ""
    entry = {"url": url}
    if desc:
        entry["description"] = desc
    t["sources"].append(entry)
    t["last_updated"] = today()
    save(data)
    print(f"📚 Source added to [{t['id']}]")


def cmd_finding(data, args):
    """Add a key finding to a thread."""
    if len(args) < 2:
        print("Usage: finding <id> <text>")
        return
    t = find_thread(data, args[0])
    text = " ".join(args[1:])
    t["key_findings"].append(text)
    t["last_updated"] = today()
    save(data)
    print(f"⚡ Finding added to [{t['id']}]")


def cmd_status(data, args):
    """Change thread status."""
    if len(args) < 2 or args[1] not in ("active", "paused", "resolved"):
        print("Usage: status <id> <active|paused|resolved>")
        return
    t = find_thread(data, args[0])
    old = t["status"]
    t["status"] = args[1]
    t["last_updated"] = today()
    save(data)
    print(f"Status [{t['id']}]: {old} → {args[1]}")


def cmd_digest(data, args):
    """Generate a brief summary of all active threads."""
    active = [t for t in data["threads"] if t["status"] == "active"]
    if not active:
        print("No active research threads.")
        return
    print(f"\nDeep Current Digest — {today()}")
    print(f"{'─' * 40}")
    for t in active:
        print(f"\n  🌊 {t['title']}")
        if t.get("key_findings"):
            print(f"     Latest finding: {t['key_findings'][-1][:120]}")
        if t.get("notes"):
            last = t["notes"][-1]
            snippet = last["text"][:100].replace("\n", " ")
            print(f"     Last note ({last['date']}): {snippet}...")
        print(f"     {len(t.get('notes', []))} notes, {len(t.get('sources', []))} sources")
    print()


def cmd_decay(data, args):
    """Prune stale threads (>90 days inactive, no recent notes)."""
    from datetime import datetime, timedelta
    cutoff = (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d")
    pruned = []
    kept = []
    for t in data["threads"]:
        if t["status"] == "active" and t["last_updated"] < cutoff:
            recent_notes = [n for n in t.get("notes", []) if n["date"] >= cutoff]
            if not recent_notes:
                t["status"] = "paused"
                pruned.append(t["id"])
        kept.append(t)
    data["threads"] = kept
    save(data)
    if pruned:
        print(f"Paused {len(pruned)} stale threads: {', '.join(pruned)}")
    else:
        print("No stale threads to prune.")


def cmd_covered(data, args):
    """Show topics/URLs covered in recent reports to avoid duplication."""
    from datetime import datetime, timedelta
    days = int(args[0]) if args else 14
    cutoff = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    reports_dir = DATA_FILE.parent.parent / "deep-current-reports"
    if not reports_dir.exists():
        print("No reports directory found.")
        return

    covered_titles = []
    covered_urls = set()
    for f in sorted(reports_dir.glob("*.md")):
        # Extract date from filename (YYYY-MM-DD.md or other formats)
        fname = f.stem
        # Try to find a YYYY-MM-DD pattern in filename
        date_match = re.search(r"(\d{4}-\d{2}-\d{2})", fname)
        if date_match:
            fdate = date_match.group(1)
        else:
            # Try to parse "Deep Current — Month DD, YYYY"
            try:
                from datetime import datetime as dt
                cleaned = fname.replace("Deep Current — ", "").strip()
                fdate = dt.strptime(cleaned, "%B %d, %Y").strftime("%Y-%m-%d")
            except (ValueError, KeyError):
                continue
        if fdate < cutoff:
            continue

        content = f.read_text(encoding="utf-8", errors="replace")
        # Extract h2 titles
        for line in content.split("\n"):
            if line.startswith("## "):
                covered_titles.append(f"  [{fdate}] {line[3:].strip()}")
            # Extract URLs
            for url_match in re.finditer(r"https?://[^\s\)>\]]+", line):
                covered_urls.add(url_match.group(0))

    print(f"\n📋 Topics covered in last {days} days:")
    if covered_titles:
        for t in covered_titles:
            print(t)
    else:
        print("  (none)")

    if covered_urls:
        print(f"\n🔗 {len(covered_urls)} unique URLs cited (showing up to 20):")
        for url in sorted(covered_urls)[:20]:
            print(f"  {url}")
    else:
        print("\n🔗 No URLs cited.")
    print()


COMMANDS = {
    "list": cmd_list,
    "show": cmd_show,
    "add": cmd_add,
    "note": cmd_note,
    "source": cmd_source,
    "finding": cmd_finding,
    "status": cmd_status,
    "digest": cmd_digest,
    "decay": cmd_decay,
    "covered": cmd_covered,
}


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help", "help"):
        print(__doc__)
        return

    cmd = sys.argv[1]
    if cmd not in COMMANDS:
        print(f"Unknown command: {cmd}")
        print(f"Available: {', '.join(COMMANDS)}")
        sys.exit(1)

    data = load()
    COMMANDS[cmd](data, sys.argv[2:])


if __name__ == "__main__":
    main()
