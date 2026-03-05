#!/usr/bin/env python3
"""MoltbotDen den monitor - scan dens for activity and engagement opportunities."""
import json, sys, argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from importlib.machinery import SourceFileLoader
client = SourceFileLoader("mbd_client", str(Path(__file__).parent / "moltbotden-client.py")).load_module()

DENS = ["the-den", "introductions", "philosophy", "technical", "collaboration"]

def cmd_scan(args):
    """Scan all dens for recent activity."""
    print("MoltbotDen Activity Scan\n")
    for den_slug in DENS:
        try:
            data = client.api_request("GET", f"/dens/{den_slug}/messages", params={"limit": 5})
            msgs = data if isinstance(data, list) else data.get("messages", data.get("items", []))
            if msgs:
                print(f"=== {den_slug} ({len(msgs)} recent) ===")
                for m in msgs[:3]:
                    agent = m.get("agent_id", "?")
                    content = m.get("content", "")[:120]
                    print(f"  {agent}: {content}")
                print()
        except SystemExit:
            print(f"  {den_slug}: (error reading)")

def cmd_mentions(args):
    """Find messages mentioning our agent."""
    agent_id = args.agent_id or "yoder"
    print(f"Scanning for mentions of @{agent_id}...\n")
    found = 0
    for den_slug in DENS:
        try:
            data = client.api_request("GET", f"/dens/{den_slug}/messages", params={"limit": 30})
            msgs = data if isinstance(data, list) else data.get("messages", data.get("items", []))
            for m in msgs:
                content = m.get("content", "")
                if f"@{agent_id}" in content or agent_id.lower() in content.lower():
                    author = m.get("agent_id", "?")
                    if author != agent_id:
                        ts = m.get("created_at", m.get("timestamp", "?"))[:19]
                        print(f"[{den_slug}] [{ts}] {author}: {content[:200]}")
                        print()
                        found += 1
        except SystemExit:
            pass
    if found == 0:
        print("No mentions found.")

def cmd_threads(args):
    """Track conversation threads in a den."""
    data = client.api_request("GET", f"/dens/{args.den}/messages", params={"limit": 30})
    msgs = data if isinstance(data, list) else data.get("messages", data.get("items", []))
    
    threads = {}
    for m in msgs:
        reply_to = m.get("reply_to")
        mid = m.get("id", "?")
        if reply_to:
            if reply_to not in threads:
                threads[reply_to] = []
            threads[reply_to].append(m)
    
    print(f"Threads in {args.den}: {len(threads)} active\n")
    for root_id, replies in threads.items():
        print(f"Thread {root_id[:12]}... ({len(replies)} replies)")
        for r in replies[:5]:
            agent = r.get("agent_id", "?")
            content = r.get("content", "")[:100]
            print(f"  {agent}: {content}")
        print()

def main():
    parser = argparse.ArgumentParser(description="MoltbotDen Den Monitor")
    sub = parser.add_subparsers(dest="command", required=True)
    
    sub.add_parser("scan", help="Scan all dens")
    p = sub.add_parser("mentions", help="Find mentions of you")
    p.add_argument("--agent-id", default="yoder")
    p = sub.add_parser("threads", help="Track threads in a den")
    p.add_argument("--den", required=True)
    
    args = parser.parse_args()
    cmds = {"scan": cmd_scan, "mentions": cmd_mentions, "threads": cmd_threads}
    cmds[args.command](args)

if __name__ == "__main__":
    main()
