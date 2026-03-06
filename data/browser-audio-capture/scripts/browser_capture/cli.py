"""CLI interface for browser audio capture."""

import asyncio
import argparse
import sys
import json

from .cdp_client import CDP_URL, get_tabs, find_meeting_tabs
from .audio_capture import capture_tab, stop_capture, capture_status, watch_meetings


def cmd_tabs(args):
    """List open browser tabs."""
    tabs = asyncio.run(get_tabs(args.cdp_url))
    meetings = asyncio.run(find_meeting_tabs(args.cdp_url))
    meeting_ids = {t["id"] for t in meetings}
    
    print(f"📑 {len(tabs)} tabs open ({len(meetings)} meetings detected)\n")
    for tab in tabs:
        is_meeting = "🎙️" if tab["id"] in meeting_ids else "  "
        title = tab.get("title", "Untitled")[:50]
        url = tab.get("url", "")[:60]
        tid = tab['id'][:12]
        print(f"{is_meeting} [{tid}] {title}")
        print(f"     {url}")
        print(f"     ID: {tab['id']}")


def cmd_capture(args):
    """Start capturing a tab."""
    result = asyncio.run(capture_tab(args.tab, args.cdp_url))
    
    if result.get("status") == "ok":
        capture = result.get("capture", {})
        tab = result.get("tab", {})
        if capture.get("status") == "capturing":
            print(f"✅ Capturing audio from: {tab.get('title')}")
            print(f"   Session: {capture.get('sessionId')}")
            print(f"   URL: {tab.get('url')}")
            print(f"\n   Audio streaming to Percept receiver...")
            print(f"   Run 'percept capture-browser stop' to end")
        elif capture.get("status") == "already_capturing":
            print(f"⚠️ Already capturing (session: {capture.get('sessionId')})")
        else:
            print(f"❌ {capture.get('error', 'Unknown error')}")
    else:
        print(f"❌ {result.get('error', 'Failed')}")


def cmd_stop(args):
    """Stop capturing."""
    result = asyncio.run(stop_capture(args.tab, args.cdp_url))
    if result.get("stopped"):
        for s in result["stopped"]:
            print(f"🛑 Stopped: {s['tab']}")
    else:
        print("No active captures found.")


def cmd_status(args):
    """Check capture status."""
    result = asyncio.run(capture_status(args.cdp_url))
    active = result.get("active_captures", [])
    
    if active:
        print(f"🎙️ {len(active)} active capture(s):\n")
        for cap in active:
            print(f"  Tab: {cap['title']}")
            print(f"  URL: {cap['url']}")
            print(f"  Session: {cap['sessionId']}")
            print()
    else:
        print(f"No active captures. ({result.get('total_tabs', 0)} tabs open)")


def cmd_watch(args):
    """Auto-detect and capture meetings."""
    print("👀 Meeting auto-detect mode")
    print(f"   Checking every {args.interval}s for: Zoom, Google Meet, Teams, Webex, etc.")
    print(f"   CDP: {args.cdp_url}")
    print(f"   Press Ctrl+C to stop\n")
    
    try:
        asyncio.run(watch_meetings(args.cdp_url, args.interval))
    except KeyboardInterrupt:
        print("\n🛑 Stopped watching.")


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="percept capture-browser",
        description="Capture audio from browser tabs via Chrome CDP"
    )
    parser.add_argument("--cdp-url", default=CDP_URL, help="Chrome CDP URL")
    
    sub = parser.add_subparsers(dest="command")
    
    # tabs
    sub.add_parser("tabs", help="List open browser tabs")
    
    # capture
    p_cap = sub.add_parser("capture", help="Start capturing a tab")
    p_cap.add_argument("--tab", help="Tab ID (auto-detects meeting if omitted)")
    
    # stop
    p_stop = sub.add_parser("stop", help="Stop capturing")
    p_stop.add_argument("--tab", help="Tab ID (stops all if omitted)")
    
    # status
    sub.add_parser("status", help="Check capture status")
    
    # watch
    p_watch = sub.add_parser("watch", help="Auto-detect and capture meetings")
    p_watch.add_argument("--interval", type=int, default=15, help="Check interval (seconds)")
    
    args = parser.parse_args(argv)
    
    if args.command == "tabs":
        cmd_tabs(args)
    elif args.command == "capture":
        cmd_capture(args)
    elif args.command == "stop":
        cmd_stop(args)
    elif args.command == "status":
        cmd_status(args)
    elif args.command == "watch":
        cmd_watch(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
