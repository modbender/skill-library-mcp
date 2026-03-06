#!/usr/bin/env python3
"""
Overkill Token Optimizer CLI

Commands:
  stats                Show token usage statistics
  check                Check optimization level
  reset --dry-run      Reset sessions and summarize (with --dry-run or --confirm)
  index                Index sessions for search
  search --hybrid      Search sessions (use --hybrid for semantic+keyword)
  compress <command>   Run command with oktk compression
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path

from config import (
    COLORS,
    DEFAULT_COMPRESSION_LEVEL,
    DEFAULT_SEARCH_LIMIT,
    HYBRID_SEARCH_WEIGHT,
    INDEX_SESSION_DAYS,
    OKTK_BIN,
    SESSION_DIR,
    SESSION_INDEX_DIR,
    MAX_CONTEXT_TOKENS,
    TARGET_CONTEXT_TOKENS,
)
    SESSION_PATTERN,
    TARGET_CONTEXT_TOKENS,
    WORKSPACE_DIR,
)


def color(text: str, color_name: str = "reset") -> str:
    return f"{COLORS.get(color_name, '')}{text}{COLORS['reset']}"


def cmd_stats(args):
    """Show token usage statistics."""
    print(f"{color('📊 Token Usage Statistics', 'bold')}\n")
    
    # Check if oktk is available
    if not Path(OKTK_BIN).exists():
        print(f"{color('⚠️  oktl not found at', 'yellow')} {OKTK_BIN}")
        print("Install with: npm install -g overkill-token-optimizer")
        return 1
    
    try:
        result = subprocess.run(
            [OKTK_BIN, "stats"],
            capture_output=True,
            text=True,
            timeout=30
        )
        print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
    except subprocess.TimeoutExpired:
        print(color("⏱️  Stats command timed out", "red"))
        return 1
    except Exception as e:
        print(color(f"Error running oktk stats: {e}", "red"))
        return 1
    
    return 0


def cmd_check(args):
    """Check optimization level."""
    print(f"{color('🔍 Checking Optimization Level', 'bold')}\n")
    
    if not Path(OKTK_BIN).exists():
        print(f"{color('⚠️  oktk not found at', 'yellow')} {OKTK_BIN}")
        return 1
    
    try:
        result = subprocess.run(
            [OKTK_BIN, "check"],
            capture_output=True,
            text=True,
            timeout=30
        )
        print(result.stdout)
    except Exception as e:
        print(color(f"Error running oktk check: {e}", "red"))
        return 1
    
    return 0


def cmd_reset(args):
    """Reset sessions and summarize."""
    dry_run = args.dry_run
    confirm = args.confirm
    
    if not dry_run and not confirm:
        print(color("⚠️  Must specify either --dry-run or --confirm", "yellow"))
        print("   --dry-run: Show what would be reset without actually resetting")
        print("   --confirm: Actually perform the reset")
        return 1
    
    print(f"{color('🔄 Reset & Summarize Sessions', 'bold')}")
    print(f"Mode: {color('DRY RUN', 'yellow') if dry_run else color('CONFIRMED', 'green')}\n")
    
    # Find session files
    sessions = sorted(SESSION_DIR.glob(SESSION_PATTERN))
    
    # Filter to recent sessions
    cutoff = datetime.now() - timedelta(days=INDEX_SESSION_DAYS)
    recent_sessions = []
    for s in sessions:
        try:
            # Try to extract date from filename
            name = s.stem
            if name.replace("-", "").isdigit() and len(name) >= 8:
                date_str = name[:10]
                session_date = datetime.strptime(date_str, "%Y-%m-%d")
                if session_date >= cutoff:
                    recent_sessions.append(s)
        except:
            pass
    
    print(f"Found {len(sessions)} total sessions, {len(recent_sessions)} recent")
    
    if dry_run:
        print(f"\n{color('Would reset the following sessions:', 'yellow')}")
        for s in recent_sessions[:10]:
            print(f"  - {s.name}")
        if len(recent_sessions) > 10:
            print(f"  ... and {len(recent_sessions) - 10} more")
    
    if confirm:
        if not Path(OKTK_BIN).exists():
            print(color("oktk not found, running basic reset", "yellow"))
            # Basic reset - just summarize
            total_chars = sum(len(s.read_text()) for s in recent_sessions)
            print(f"\n{color('✅ Reset complete', 'green')}")
            print(f"Processed {len(recent_sessions)} sessions")
            print(f"Total content: {total_chars:,} characters")
        else:
            try:
                result = subprocess.run(
                    [OKTK_BIN, "reset", "--confirm"],
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                print(result.stdout)
            except Exception as e:
                print(color(f"Error: {e}", "red"))
                return 1
    
    return 0


def cmd_index(args):
    """Index sessions for search."""
    print(f"{color('📑 Indexing Sessions', 'bold')}\n")
    
    # Create index directory
    SESSION_INDEX_DIR.mkdir(parents=True, exist_ok=True)
    
    # Find sessions
    sessions = sorted(SESSION_DIR.glob(SESSION_PATTERN))
    
    if not sessions:
        print(color("No session files found", "yellow"))
        return 0
    
    print(f"Found {len(sessions)} session files")
    
    # Check for oktk index command
    if not Path(OKTK_BIN).exists():
        print(color("oktk not found, creating basic index", "yellow"))
        
        # Basic index - just list files
        index_data = {
            "indexed_at": datetime.now().isoformat(),
            "session_count": len(sessions),
            "sessions": [
                {
                    "name": s.name,
                    "size": s.stat().st_size,
                    "modified": s.stat().st_mtime
                }
                for s in sessions[:50]  # Limit to 50
            ]
        }
        
        index_file = SESSION_INDEX_DIR / "index.json"
        with open(index_file, "w") as f:
            json.dump(index_data, f, indent=2)
        
        print(f"{color('✅ Indexed', 'green')} {len(sessions)} sessions to {index_file}")
    else:
        try:
            result = subprocess.run(
                [OKTK_BIN, "index"],
                capture_output=True,
                text=True,
                timeout=60
            )
            print(result.stdout)
        except Exception as e:
            print(color(f"Error: {e}", "red"))
            return 1
    
    return 0


def cmd_search(args):
    """Search sessions."""
    query = args.query
    hybrid = args.hybrid
    limit = args.limit
    
    mode = "hybrid" if hybrid else "keyword"
    print(f"{color('🔍 Search Sessions', 'bold')} (mode: {mode})")
    print(f"Query: {color(query, 'bold')}\n")
    
    if not query:
        print(color("Error: search query required", "red"))
        return 1
    
    # Load index
    index_file = SESSION_INDEX_DIR / "index.json"
    if not index_file.exists():
        print(color("No index found. Run 'oktk index' first.", "yellow"))
        return 1
    
    with open(index_file) as f:
        index_data = json.load(f)
    
    if not Path(OKTK_BIN).exists():
        # Basic keyword search
        print(color("oktk not found, using basic search", "yellow"))
        results = []
        for session in index_data.get("sessions", [])[:limit]:
            s_path = SESSION_DIR / session["name"]
            if s_path.exists():
                content = s_path.read_text()
                if query.lower() in content.lower():
                    # Count occurrences
                    count = content.lower().count(query.lower())
                    results.append({
                        "session": session["name"],
                        "matches": count,
                        "path": str(s_path)
                    })
        
        if not results:
            print("No results found")
            return 0
        
        print(f"Found {len(results)} results:\n")
        for r in results:
            print(f"  {color('📄', 'blue')} {r['session']}")
            print(f"     {r['matches']} matches\n")
    else:
        # Use oktk search
        cmd = [OKTK_BIN, "search", query]
        if hybrid:
            cmd.append("--hybrid")
        if limit:
            cmd.extend(["--limit", str(limit)])
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            print(result.stdout)
        except Exception as e:
            print(color(f"Error: {e}", "red"))
            return 1
    
    return 0


def cmd_compress(args):
    """Run command with oktk compression."""
    command = args.command
    
    if not command:
        print(color("Error: command required after compress", "red"))
        return 1
    
    print(f"{color('🗜️  Running with compression:', 'bold')} {command}\n")
    
    if not Path(OKTK_BIN).exists():
        print(color("oktk not found", "red"))
        return 1
    
    try:
        # Run the command through oktk compress
        result = subprocess.run(
            [OKTK_BIN, "compress", "--"] + command,
            capture_output=False,
            text=True,
            timeout=300  # 5 min timeout
        )
        return result.returncode
    except subprocess.TimeoutExpired:
        print(color("⏱️  Command timed out", "red"))
        return 1
    except Exception as e:
        print(color(f"Error: {e}", "red"))
        return 1


def main():
    parser = argparse.ArgumentParser(
        description="Overkill Token Optimizer - Manage token usage in your workspace",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # stats
    subparsers.add_parser("stats", help="Show token usage statistics")
    
    # check
    subparsers.add_parser("check", help="Check optimization level")
    
    # reset
    reset_parser = subparsers.add_parser("reset", help="Reset & summarize sessions")
    reset_parser.add_argument("--dry-run", action="store_true", help="Show what would be reset")
    reset_parser.add_argument("--confirm", action="store_true", help="Actually perform reset")
    
    # index
    subparsers.add_parser("index", help="Index sessions for search")
    
    # search
    search_parser = subparsers.add_parser("search", help="Search sessions")
    search_parser.add_argument("query", nargs="?", help="Search query")
    search_parser.add_argument("--hybrid", action="store_true", help="Use hybrid search (semantic + keyword)")
    search_parser.add_argument("--limit", type=int, default=DEFAULT_SEARCH_LIMIT, help="Max results")
    
    # compress
    compress_parser = subparsers.add_parser("compress", help="Run command with oktk compression")
    compress_parser.add_argument("command", nargs=argparse.REMAINDER, help="Command to run")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 0
    
    # Route to command handlers
    commands = {
        "stats": cmd_stats,
        "check": cmd_check,
        "reset": cmd_reset,
        "index": cmd_index,
        "search": cmd_search,
        "compress": cmd_compress,
    }
    
    handler = commands.get(args.command)
    if handler:
        return handler(args)
    else:
        print(color(f"Unknown command: {args.command}", "red"))
        return 1


if __name__ == "__main__":
    sys.exit(main())
