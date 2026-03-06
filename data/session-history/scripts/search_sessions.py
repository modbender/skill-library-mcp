#!/usr/bin/env python3
"""Search through OpenClaw session transcripts for relevant conversations.

Usage:
    python3 search_sessions.py <query> [--days N] [--max-results N] [--agent AGENT]
    python3 search_sessions.py --list [--days N] [--agent AGENT]

Examples:
    python3 search_sessions.py "error blog patches"
    python3 search_sessions.py "flight monitor" --days 7
    python3 search_sessions.py --list --days 3
    python3 search_sessions.py "gclid pipeline" --agent main --max-results 5
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path


def find_session_dirs():
    """Find all agent session directories."""
    base = Path.home() / ".openclaw" / "agents"
    dirs = {}
    if base.exists():
        for agent_dir in base.iterdir():
            sessions_dir = agent_dir / "sessions"
            if sessions_dir.is_dir():
                dirs[agent_dir.name] = sessions_dir
    return dirs


def parse_session(path: Path):
    """Parse a JSONL session file into metadata + messages."""
    meta = {}
    messages = []
    try:
        with open(path) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                obj = json.loads(line)
                t = obj.get("type")
                if t == "session":
                    meta = obj
                elif t == "message":
                    msg = obj.get("message", {})
                    role = msg.get("role", "")
                    content = msg.get("content", "")
                    # Extract text from content array
                    if isinstance(content, list):
                        texts = []
                        for block in content:
                            if isinstance(block, dict) and block.get("type") == "text":
                                texts.append(block.get("text", ""))
                        text = "\n".join(texts)
                    elif isinstance(content, str):
                        text = content
                    else:
                        text = ""
                    if text.strip():
                        messages.append({
                            "role": role,
                            "text": text,
                            "timestamp": obj.get("timestamp", ""),
                        })
    except (json.JSONDecodeError, OSError):
        pass
    return meta, messages


def session_timestamp(meta):
    """Get session start time as datetime."""
    ts = meta.get("timestamp", "")
    if ts:
        try:
            return datetime.fromisoformat(ts.replace("Z", "+00:00"))
        except ValueError:
            pass
    return None


def search_text(query_terms, text):
    """Score text against query terms. Returns (score, matched_terms)."""
    text_lower = text.lower()
    matched = []
    score = 0
    for term in query_terms:
        count = text_lower.count(term.lower())
        if count > 0:
            matched.append(term)
            score += count
    return score, matched


def excerpt_around_match(text, term, context_chars=150):
    """Get an excerpt around the first match of a term."""
    idx = text.lower().find(term.lower())
    if idx == -1:
        return text[:300]
    start = max(0, idx - context_chars)
    end = min(len(text), idx + len(term) + context_chars)
    excerpt = text[start:end]
    if start > 0:
        excerpt = "..." + excerpt
    if end < len(text):
        excerpt = excerpt + "..."
    return excerpt


def main():
    parser = argparse.ArgumentParser(description="Search OpenClaw session history")
    parser.add_argument("query", nargs="*", help="Search terms")
    parser.add_argument("--list", action="store_true", help="List recent sessions")
    parser.add_argument("--days", type=int, default=14, help="Look back N days (default: 14)")
    parser.add_argument("--max-results", type=int, default=10, help="Max results (default: 10)")
    parser.add_argument("--agent", default=None, help="Filter by agent id (main, chai, nori)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show message excerpts")
    args = parser.parse_args()

    if not args.list and not args.query:
        parser.print_help()
        sys.exit(1)

    session_dirs = find_session_dirs()
    if not session_dirs:
        print("No session directories found.")
        sys.exit(1)

    cutoff = datetime.now(timezone.utc) - timedelta(days=args.days)
    query_str = " ".join(args.query) if args.query else ""
    query_terms = query_str.split() if query_str else []

    results = []

    agents = [args.agent] if args.agent else list(session_dirs.keys())

    for agent_id in agents:
        if agent_id not in session_dirs:
            continue
        sessions_dir = session_dirs[agent_id]
        for jsonl_path in sessions_dir.glob("*.jsonl"):
            # Quick file age check
            stat = jsonl_path.stat()
            file_mtime = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc)
            if file_mtime < cutoff:
                continue

            meta, messages = parse_session(jsonl_path)
            ts = session_timestamp(meta)
            if ts and ts < cutoff:
                continue

            if args.list:
                # List mode — show session summaries
                msg_count = len(messages)
                user_msgs = [m for m in messages if m["role"] == "user"]
                first_user = user_msgs[0]["text"][:120] if user_msgs else "(no user messages)"
                results.append({
                    "agent": agent_id,
                    "session_id": meta.get("id", jsonl_path.stem),
                    "timestamp": ts.isoformat() if ts else "unknown",
                    "messages": msg_count,
                    "preview": first_user.replace("\n", " "),
                    "path": str(jsonl_path),
                })
            else:
                # Search mode
                all_text = "\n".join(m["text"] for m in messages)
                score, matched = search_text(query_terms, all_text)
                if score > 0:
                    # Find best excerpt
                    best_excerpt = ""
                    for term in matched:
                        for m in messages:
                            if term.lower() in m["text"].lower():
                                best_excerpt = excerpt_around_match(m["text"], term)
                                break
                        if best_excerpt:
                            break

                    user_msgs = [m for m in messages if m["role"] == "user"]
                    first_user = user_msgs[0]["text"][:120] if user_msgs else ""

                    results.append({
                        "agent": agent_id,
                        "session_id": meta.get("id", jsonl_path.stem),
                        "timestamp": ts.isoformat() if ts else "unknown",
                        "score": score,
                        "matched_terms": matched,
                        "messages": len(messages),
                        "preview": first_user.replace("\n", " "),
                        "excerpt": best_excerpt.replace("\n", " "),
                        "path": str(jsonl_path),
                    })

    # Sort
    if args.list:
        results.sort(key=lambda r: r["timestamp"], reverse=True)
    else:
        results.sort(key=lambda r: r["score"], reverse=True)

    results = results[:args.max_results]

    if not results:
        if args.list:
            print(f"No sessions found in the last {args.days} days.")
        else:
            print(f"No sessions matching '{query_str}' in the last {args.days} days.")
        sys.exit(0)

    # Output
    if args.list:
        print(f"📋 Recent sessions (last {args.days} days):\n")
        for r in results:
            ts_short = r["timestamp"][:16].replace("T", " ") if r["timestamp"] != "unknown" else "?"
            print(f"  [{r['agent']}] {ts_short} ({r['messages']} msgs) — {r['preview'][:80]}")
            if args.verbose:
                print(f"    Path: {r['path']}")
            print()
    else:
        print(f"🔍 Found {len(results)} sessions matching '{query_str}':\n")
        for i, r in enumerate(results, 1):
            ts_short = r["timestamp"][:16].replace("T", " ") if r["timestamp"] != "unknown" else "?"
            print(f"  {i}. [{r['agent']}] {ts_short} (score: {r['score']}, {r['messages']} msgs)")
            print(f"     Matched: {', '.join(r['matched_terms'])}")
            if r.get("excerpt"):
                print(f"     Excerpt: {r['excerpt'][:200]}")
            print(f"     Path: {r['path']}")
            print()


if __name__ == "__main__":
    main()
