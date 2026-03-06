#!/usr/bin/env python3
"""
web-monitor: Track web pages for changes and get alerts.
Stores snapshots, computes diffs, supports CSS selectors for targeted monitoring.
"""

import argparse
import hashlib
import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError
from difflib import unified_diff

# Optional dependencies (graceful fallback)
try:
    from bs4 import BeautifulSoup
    HAS_BS4 = True
except ImportError:
    HAS_BS4 = False

DATA_DIR = Path(os.environ.get("WEB_MONITOR_DIR", Path.home() / ".web-monitor"))
WATCHES_FILE = DATA_DIR / "watches.json"
SNAPSHOTS_DIR = DATA_DIR / "snapshots"

def ensure_dirs():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    SNAPSHOTS_DIR.mkdir(parents=True, exist_ok=True)

def load_watches() -> dict:
    if WATCHES_FILE.exists():
        return json.loads(WATCHES_FILE.read_text())
    return {"watches": []}

def save_watches(data: dict):
    WATCHES_FILE.write_text(json.dumps(data, indent=2))

def slug(url: str) -> str:
    """Create a filesystem-safe slug from a URL."""
    return hashlib.md5(url.encode()).hexdigest()[:12]

def fetch_content(url: str, selector: str = None, headers: dict = None) -> str:
    """Fetch URL content, optionally extracting a CSS selector."""
    req_headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) web-monitor/1.0"
    }
    if headers:
        req_headers.update(headers)
    
    req = Request(url, headers=req_headers)
    try:
        with urlopen(req, timeout=30) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
    except HTTPError as e:
        raise RuntimeError(f"HTTP {e.code}: {e.reason}")
    except URLError as e:
        raise RuntimeError(f"Connection error: {e.reason}")
    
    if selector and HAS_BS4:
        soup = BeautifulSoup(raw, "html.parser")
        elements = soup.select(selector)
        if not elements:
            return f"[No elements matched selector: {selector}]"
        return "\n".join(el.get_text(strip=True, separator="\n") for el in elements)
    elif selector and not HAS_BS4:
        print("Warning: beautifulsoup4 not installed, ignoring selector", file=sys.stderr)
    
    # Basic text extraction without bs4
    if HAS_BS4:
        soup = BeautifulSoup(raw, "html.parser")
        # Remove script, style, nav, footer
        for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
            tag.decompose()
        return soup.get_text(strip=True, separator="\n")
    else:
        # Crude fallback: strip HTML tags
        text = re.sub(r'<[^>]+>', ' ', raw)
        text = re.sub(r'\s+', ' ', text).strip()
        return text

def normalize_text(text: str) -> str:
    """Normalize text to reduce noise from timestamps, ads, etc."""
    lines = text.split("\n")
    # Remove empty lines and normalize whitespace
    lines = [re.sub(r'\s+', ' ', line.strip()) for line in lines if line.strip()]
    return "\n".join(lines)

def cmd_add(args):
    """Add a URL to watch."""
    ensure_dirs()
    data = load_watches()
    
    # Check for duplicate
    for w in data["watches"]:
        if w["url"] == args.url:
            print(f"Already watching: {args.url}")
            return
    
    watch = {
        "url": args.url,
        "name": args.name or args.url[:60],
        "selector": args.selector,
        "added": datetime.now(timezone.utc).isoformat(),
        "last_check": None,
        "last_change": None,
        "check_count": 0,
        "change_count": 0,
    }
    data["watches"].append(watch)
    save_watches(data)
    
    # Take initial snapshot
    try:
        content = fetch_content(args.url, args.selector)
        content = normalize_text(content)
        snap_path = SNAPSHOTS_DIR / f"{slug(args.url)}.txt"
        snap_path.write_text(content)
        print(f"✅ Added and snapshotted: {watch['name']}")
    except Exception as e:
        print(f"⚠️  Added but initial fetch failed: {e}")

def cmd_remove(args):
    """Remove a URL from watch list."""
    ensure_dirs()
    data = load_watches()
    original = len(data["watches"])
    data["watches"] = [w for w in data["watches"] if w["url"] != args.url and w["name"] != args.url]
    if len(data["watches"]) < original:
        save_watches(data)
        print(f"✅ Removed: {args.url}")
    else:
        print(f"Not found: {args.url}")

def cmd_list(args):
    """List all watched URLs."""
    ensure_dirs()
    data = load_watches()
    if not data["watches"]:
        print("No URLs being watched. Use 'add' to start.")
        return
    
    fmt = getattr(args, 'format', 'text')
    if fmt == 'json':
        print(json.dumps(data["watches"], indent=2))
        return
    
    for i, w in enumerate(data["watches"], 1):
        status = "never checked" if not w["last_check"] else f"checked {w['check_count']}x, {w['change_count']} changes"
        sel = f" [selector: {w['selector']}]" if w.get("selector") else ""
        print(f"{i}. {w['name']}")
        print(f"   URL: {w['url']}{sel}")
        print(f"   Status: {status}")
        if w.get("last_change"):
            print(f"   Last change: {w['last_change']}")
        print()

def cmd_check(args):
    """Check all (or one) watched URLs for changes."""
    ensure_dirs()
    data = load_watches()
    
    if not data["watches"]:
        print("No URLs being watched.")
        return
    
    results = []
    watches_to_check = data["watches"]
    if args.url:
        watches_to_check = [w for w in data["watches"] if w["url"] == args.url or w["name"] == args.url]
        if not watches_to_check:
            print(f"Not found: {args.url}")
            return
    
    for watch in watches_to_check:
        url = watch["url"]
        s = slug(url)
        snap_path = SNAPSHOTS_DIR / f"{s}.txt"
        
        try:
            new_content = fetch_content(url, watch.get("selector"))
            new_content = normalize_text(new_content)
        except Exception as e:
            results.append({"name": watch["name"], "url": url, "error": str(e)})
            continue
        
        watch["last_check"] = datetime.now(timezone.utc).isoformat()
        watch["check_count"] = watch.get("check_count", 0) + 1
        
        if snap_path.exists():
            old_content = snap_path.read_text()
            if old_content == new_content:
                results.append({"name": watch["name"], "url": url, "changed": False})
            else:
                # Compute diff
                old_lines = old_content.split("\n")
                new_lines = new_content.split("\n")
                diff = list(unified_diff(old_lines, new_lines, n=2, lineterm=""))
                
                # Count meaningful changes
                added = [l for l in diff if l.startswith("+") and not l.startswith("+++")]
                removed = [l for l in diff if l.startswith("-") and not l.startswith("---")]
                
                watch["last_change"] = datetime.now(timezone.utc).isoformat()
                watch["change_count"] = watch.get("change_count", 0) + 1
                
                # Save new snapshot
                snap_path.write_text(new_content)
                
                # Save diff
                diff_path = SNAPSHOTS_DIR / f"{s}_diff_{int(time.time())}.txt"
                diff_path.write_text("\n".join(diff))
                
                result = {
                    "name": watch["name"],
                    "url": url,
                    "changed": True,
                    "added_lines": len(added),
                    "removed_lines": len(removed),
                    "diff_preview": "\n".join(diff[:30]),
                }
                results.append(result)
        else:
            # First snapshot
            snap_path.write_text(new_content)
            results.append({"name": watch["name"], "url": url, "changed": False, "note": "initial snapshot"})
    
    save_watches(data)
    
    # Output
    fmt = getattr(args, 'format', 'text')
    if fmt == 'json':
        print(json.dumps(results, indent=2))
        return
    
    changes_found = False
    for r in results:
        if r.get("error"):
            print(f"❌ {r['name']}: {r['error']}")
        elif r.get("changed"):
            changes_found = True
            print(f"🔔 CHANGED: {r['name']}")
            print(f"   URL: {r['url']}")
            print(f"   +{r['added_lines']} lines / -{r['removed_lines']} lines")
            if r.get("diff_preview"):
                print(f"   Preview:")
                for line in r["diff_preview"].split("\n")[:10]:
                    print(f"     {line}")
            print()
        elif r.get("note"):
            print(f"📸 {r['name']}: {r['note']}")
        else:
            print(f"✅ {r['name']}: no changes")
    
    if not changes_found and not any(r.get("error") for r in results):
        print("\nNo changes detected across all watched URLs.")

def cmd_diff(args):
    """Show the last diff for a URL."""
    ensure_dirs()
    data = load_watches()
    
    watch = None
    for w in data["watches"]:
        if w["url"] == args.url or w["name"] == args.url:
            watch = w
            break
    
    if not watch:
        print(f"Not found: {args.url}")
        return
    
    s = slug(watch["url"])
    # Find latest diff file
    diffs = sorted(SNAPSHOTS_DIR.glob(f"{s}_diff_*.txt"), reverse=True)
    if not diffs:
        print(f"No diffs recorded for: {watch['name']}")
        return
    
    print(f"Last diff for: {watch['name']}")
    print(f"URL: {watch['url']}")
    print("-" * 60)
    print(diffs[0].read_text())

def cmd_snapshot(args):
    """Show the current snapshot for a URL."""
    ensure_dirs()
    data = load_watches()
    
    watch = None
    for w in data["watches"]:
        if w["url"] == args.url or w["name"] == args.url:
            watch = w
            break
    
    if not watch:
        print(f"Not found: {args.url}")
        return
    
    snap_path = SNAPSHOTS_DIR / f"{slug(watch['url'])}.txt"
    if not snap_path.exists():
        print(f"No snapshot for: {watch['name']}")
        return
    
    content = snap_path.read_text()
    if args.lines:
        lines = content.split("\n")[:args.lines]
        print("\n".join(lines))
    else:
        print(content[:5000])
    

def main():
    parser = argparse.ArgumentParser(
        prog="web-monitor",
        description="Monitor web pages for changes"
    )
    sub = parser.add_subparsers(dest="command", required=True)
    
    # add
    p_add = sub.add_parser("add", help="Add a URL to watch")
    p_add.add_argument("url", help="URL to monitor")
    p_add.add_argument("--name", "-n", help="Friendly name")
    p_add.add_argument("--selector", "-s", help="CSS selector to monitor (requires beautifulsoup4)")
    p_add.set_defaults(func=cmd_add)
    
    # remove
    p_rm = sub.add_parser("remove", help="Remove a URL")
    p_rm.add_argument("url", help="URL or name to remove")
    p_rm.set_defaults(func=cmd_remove)
    
    # list
    p_ls = sub.add_parser("list", help="List watched URLs")
    p_ls.add_argument("--format", "-f", choices=["text", "json"], default="text")
    p_ls.set_defaults(func=cmd_list)
    
    # check
    p_chk = sub.add_parser("check", help="Check for changes")
    p_chk.add_argument("url", nargs="?", help="URL/name to check (all if omitted)")
    p_chk.add_argument("--format", "-f", choices=["text", "json"], default="text")
    p_chk.set_defaults(func=cmd_check)
    
    # diff
    p_diff = sub.add_parser("diff", help="Show last diff for a URL")
    p_diff.add_argument("url", help="URL or name")
    p_diff.set_defaults(func=cmd_diff)
    
    # snapshot
    p_snap = sub.add_parser("snapshot", help="Show current snapshot")
    p_snap.add_argument("url", help="URL or name")
    p_snap.add_argument("--lines", "-l", type=int, help="Limit output lines")
    p_snap.set_defaults(func=cmd_snapshot)
    
    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()
