#!/usr/bin/env python3
"""
clawdscan — Clawdbot Session Health Analyzer

Scans Clawdbot session JSONL files and provides actionable diagnostics:
- Session size, age, message count analysis
- Bloat detection (large sessions, high message count)
- Stale/zombie session identification
- Disk usage breakdown per agent
- Tool usage patterns and model switching
- Cleanup recommendations with safe archive/delete

Addresses: https://github.com/clawdbot/clawdbot/issues/1808
"""

import argparse
import glob
import json
import os
import platform
import re
import subprocess
import sys
import shutil
from collections import Counter, defaultdict
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Optional

try:
    import yaml as _yaml
except ImportError:
    _yaml = None

__version__ = "0.3.0"

# ─── Defaults ────────────────────────────────────────────────────────────────

DEFAULT_CLAWDBOT_DIR = Path.home() / ".clawdbot"
OPENCLAW_DIR = Path.home() / ".openclaw"
RC_FILE = Path.home() / ".clawdscanrc"

# Thresholds (overridable via ~/.clawdscanrc)
BLOAT_SIZE_BYTES = 1 * 1024 * 1024       # 1 MB
BLOAT_MSG_COUNT = 300                     # messages
STALE_DAYS = 7                            # days without activity
ZOMBIE_HOURS = 48                         # hours: created but never got messages
LARGE_SESSION_TOP_N = 15                  # top N in reports


def load_rc_config() -> dict:
    """Load thresholds from ~/.clawdscanrc (JSON) if it exists.

    Supported keys:
      bloat_size_bytes, bloat_size (human e.g. "2M"),
      bloat_msg_count, stale_days, zombie_hours, top_n,
      clawdbot_dir
    """
    rc = {}
    for candidate in (RC_FILE, Path(".clawdscanrc")):
        if candidate.exists():
            try:
                with open(candidate) as f:
                    rc = json.load(f)
            except (json.JSONDecodeError, OSError):
                pass
            break
    return rc


def apply_rc_config():
    """Apply ~/.clawdscanrc overrides to module-level thresholds."""
    global BLOAT_SIZE_BYTES, BLOAT_MSG_COUNT, STALE_DAYS, ZOMBIE_HOURS, LARGE_SESSION_TOP_N
    rc = load_rc_config()
    if not rc:
        return
    if "bloat_size" in rc:
        BLOAT_SIZE_BYTES = parse_size(str(rc["bloat_size"]))
    if "bloat_size_bytes" in rc:
        BLOAT_SIZE_BYTES = int(rc["bloat_size_bytes"])
    if "bloat_msg_count" in rc:
        BLOAT_MSG_COUNT = int(rc["bloat_msg_count"])
    if "stale_days" in rc:
        STALE_DAYS = int(rc["stale_days"])
    if "zombie_hours" in rc:
        ZOMBIE_HOURS = int(rc["zombie_hours"])
    if "top_n" in rc:
        LARGE_SESSION_TOP_N = int(rc["top_n"])

# Colors
class C:
    """ANSI color codes (disabled if NO_COLOR or not a TTY)."""
    _enabled = sys.stdout.isatty() and not os.environ.get("NO_COLOR")

    @classmethod
    def _w(cls, code: str, text: str) -> str:
        return f"\033[{code}m{text}\033[0m" if cls._enabled else text

    @classmethod
    def red(cls, t): return cls._w("31", t)
    @classmethod
    def green(cls, t): return cls._w("32", t)
    @classmethod
    def yellow(cls, t): return cls._w("33", t)
    @classmethod
    def blue(cls, t): return cls._w("34", t)
    @classmethod
    def magenta(cls, t): return cls._w("35", t)
    @classmethod
    def cyan(cls, t): return cls._w("36", t)
    @classmethod
    def bold(cls, t): return cls._w("1", t)
    @classmethod
    def dim(cls, t): return cls._w("2", t)


# ─── Session Analysis ────────────────────────────────────────────────────────

def analyze_session(filepath: Path) -> dict:
    """Parse a session JSONL file and extract health metrics."""
    stats = {
        "path": str(filepath),
        "filename": filepath.name,
        "session_id": filepath.stem.replace(".jsonl", ""),
        "size_bytes": filepath.stat().st_size,
        "mtime": datetime.fromtimestamp(filepath.stat().st_mtime, tz=timezone.utc),
        "messages": 0,
        "user_messages": 0,
        "assistant_messages": 0,
        "tool_calls": 0,
        "compactions": 0,
        "model_changes": 0,
        "models_used": set(),
        "tools_used": Counter(),
        "first_timestamp": None,
        "last_timestamp": None,
        "created": None,
        "label": None,
        "cwd": None,
        "errors": 0,
        "custom_types": Counter(),
    }

    try:
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            for line_num, line in enumerate(f):
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                except json.JSONDecodeError:
                    stats["errors"] += 1
                    continue

                entry_type = entry.get("type", "unknown")
                ts_str = entry.get("timestamp")
                ts = None
                if ts_str:
                    try:
                        ts = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
                    except (ValueError, AttributeError):
                        pass

                if ts:
                    if stats["first_timestamp"] is None or ts < stats["first_timestamp"]:
                        stats["first_timestamp"] = ts
                    if stats["last_timestamp"] is None or ts > stats["last_timestamp"]:
                        stats["last_timestamp"] = ts

                if entry_type == "session":
                    stats["created"] = ts
                    stats["cwd"] = entry.get("cwd")
                    stats["label"] = entry.get("label") or entry.get("name")
                    stats["session_id"] = entry.get("id", stats["session_id"])

                elif entry_type == "message":
                    stats["messages"] += 1
                    msg = entry.get("message", {})
                    role = msg.get("role", "")
                    if role == "user":
                        stats["user_messages"] += 1
                    elif role == "assistant":
                        stats["assistant_messages"] += 1
                        # Count tool calls in assistant content blocks
                        content = msg.get("content", [])
                        if isinstance(content, list):
                            for block in content:
                                if isinstance(block, dict):
                                    if block.get("type") == "tool_use":
                                        stats["tool_calls"] += 1
                                        tool_name = block.get("name", "unknown")
                                        stats["tools_used"][tool_name] += 1
                    elif role == "toolResult":
                        # Clawdbot stores tool results as separate message entries
                        stats["tool_calls"] += 1
                        tool_name = msg.get("toolName", "unknown")
                        stats["tools_used"][tool_name] += 1

                elif entry_type == "compaction":
                    stats["compactions"] += 1

                elif entry_type == "model_change":
                    stats["model_changes"] += 1
                    model_id = entry.get("modelId") or entry.get("model")
                    if model_id:
                        stats["models_used"].add(model_id)

                elif entry_type == "custom":
                    custom_type = entry.get("customType", "unknown")
                    stats["custom_types"][custom_type] += 1
                    # Extract model from model-snapshot
                    if custom_type == "model-snapshot":
                        data = entry.get("data", {})
                        model_id = data.get("modelId")
                        if model_id:
                            stats["models_used"].add(model_id)

                elif entry_type == "thinking_level_change":
                    pass  # Tracked but not counted specially

                else:
                    pass  # Unknown type

    except Exception as e:
        stats["errors"] += 1
        stats["error_detail"] = str(e)

    # Convert sets to lists for JSON serialization
    stats["models_used"] = list(stats["models_used"])

    return stats


def classify_session(stats: dict, now: datetime) -> list[str]:
    """Classify a session with health labels."""
    labels = []

    # Size-based
    if stats["size_bytes"] > BLOAT_SIZE_BYTES * 5:
        labels.append("🔴 mega-bloat")
    elif stats["size_bytes"] > BLOAT_SIZE_BYTES:
        labels.append("🟡 bloated")

    # Message count
    if stats["messages"] > BLOAT_MSG_COUNT * 3:
        labels.append("🔴 msg-overflow")
    elif stats["messages"] > BLOAT_MSG_COUNT:
        labels.append("🟡 msg-heavy")

    # Staleness
    last_activity = stats["last_timestamp"] or stats["mtime"]
    if last_activity:
        age = now - last_activity
        if age > timedelta(days=STALE_DAYS * 4):
            labels.append("🔴 ancient")
        elif age > timedelta(days=STALE_DAYS):
            labels.append("🟡 stale")

    # Zombie: created but <3 messages and old
    if stats["messages"] <= 2:
        created = stats["created"] or stats["first_timestamp"]
        if created and (now - created) > timedelta(hours=ZOMBIE_HOURS):
            labels.append("👻 zombie")

    # High compaction = session has been compacted many times
    if stats["compactions"] > 10:
        labels.append("📦 over-compacted")
    elif stats["compactions"] > 3:
        labels.append("📦 compacted")

    # Errors
    if stats["errors"] > 5:
        labels.append("⚠️ parse-errors")

    if not labels:
        labels.append("✅ healthy")

    return labels


# ─── Formatting ───────────────────────────────────────────────────────────────

def fmt_size(n: int) -> str:
    """Human-readable file size."""
    for unit in ("B", "KB", "MB", "GB"):
        if abs(n) < 1024:
            return f"{n:.1f} {unit}" if unit != "B" else f"{n} B"
        n /= 1024
    return f"{n:.1f} TB"


def fmt_age(dt: Optional[datetime], now: datetime) -> str:
    """Human-readable age string."""
    if not dt:
        return "unknown"
    delta = now - dt
    if delta.days > 30:
        return f"{delta.days // 30}mo ago"
    elif delta.days > 0:
        return f"{delta.days}d ago"
    elif delta.seconds > 3600:
        return f"{delta.seconds // 3600}h ago"
    elif delta.seconds > 60:
        return f"{delta.seconds // 60}m ago"
    else:
        return "just now"


def fmt_compaction_efficiency(size_bytes: int, compactions: int) -> str:
    """Show size-per-compaction ratio to indicate compaction effectiveness."""
    if compactions <= 0:
        return "no compactions"
    ratio = size_bytes / compactions
    verdict = ""
    if size_bytes > BLOAT_SIZE_BYTES and compactions > 5:
        verdict = C.red(" (compaction not helping)")
    elif size_bytes > BLOAT_SIZE_BYTES and compactions > 2:
        verdict = C.yellow(" (consider restart)")
    return f"{fmt_size(int(ratio))}/compaction{verdict}"


def fmt_duration(dt_start: Optional[datetime], dt_end: Optional[datetime]) -> str:
    """Human-readable session duration."""
    if not dt_start or not dt_end:
        return "unknown"
    delta = dt_end - dt_start
    if delta.days > 0:
        return f"{delta.days}d {delta.seconds // 3600}h"
    elif delta.seconds > 3600:
        return f"{delta.seconds // 3600}h {(delta.seconds % 3600) // 60}m"
    elif delta.seconds > 60:
        return f"{delta.seconds // 60}m"
    else:
        return f"{delta.seconds}s"


# ─── Commands ─────────────────────────────────────────────────────────────────

def find_clawdbot_dir() -> Path:
    """Find the Clawdbot config directory."""
    if DEFAULT_CLAWDBOT_DIR.exists():
        return DEFAULT_CLAWDBOT_DIR
    if OPENCLAW_DIR.exists():
        return OPENCLAW_DIR
    return DEFAULT_CLAWDBOT_DIR


def discover_agents(base_dir: Path) -> list[dict]:
    """Discover all agents and their session directories."""
    agents_dir = base_dir / "agents"
    if not agents_dir.exists():
        return []

    agents = []
    for agent_dir in sorted(agents_dir.iterdir()):
        if not agent_dir.is_dir():
            continue
        sessions_dir = agent_dir / "sessions"
        if sessions_dir.exists():
            agents.append({
                "name": agent_dir.name,
                "path": str(agent_dir),
                "sessions_dir": sessions_dir,
            })
    return agents


def scan_sessions(sessions_dir: Path, include_deleted: bool = False) -> list[Path]:
    """Find all session JSONL files."""
    files = []
    for f in sessions_dir.iterdir():
        if not f.name.endswith(".jsonl"):
            continue
        if ".deleted." in f.name and not include_deleted:
            continue
        files.append(f)
    return sorted(files, key=lambda f: f.stat().st_size, reverse=True)


def cmd_scan(args):
    """Full scan of all sessions across all agents."""
    base_dir = Path(args.dir) if args.dir else find_clawdbot_dir()
    now = datetime.now(timezone.utc)

    if not base_dir.exists():
        print(C.red(f"Error: Clawdbot directory not found at {base_dir}"))
        print("Try: clawdscan scan --dir ~/.clawdbot")
        sys.exit(1)

    agents = discover_agents(base_dir)
    if not agents:
        print(C.red(f"No agents found in {base_dir / 'agents'}"))
        sys.exit(1)

    total_sessions = 0
    total_size = 0
    all_issues = []
    all_stats = []

    print(C.bold(f"\n🔍 clawdscan v{__version__} — Session Health Report"))
    print(C.dim(f"   Scanning: {base_dir}"))
    print(C.dim(f"   Time: {now.strftime('%Y-%m-%d %H:%M:%S UTC')}\n"))

    for agent in agents:
        sessions = scan_sessions(agent["sessions_dir"], include_deleted=args.include_deleted)
        deleted_count = len(list(agent["sessions_dir"].glob("*.deleted.*")))
        agent_size = sum(f.stat().st_size for f in sessions)

        print(C.bold(f"📁 Agent: {agent['name']}"))
        print(f"   Sessions: {len(sessions)} active, {deleted_count} deleted")
        print(f"   Disk: {fmt_size(agent_size)}")

        agent_issues = []
        for session_file in sessions:
            stats = analyze_session(session_file)
            labels = classify_session(stats, now)
            stats["labels"] = labels
            stats["agent"] = agent["name"]
            all_stats.append(stats)

            if not all(l.startswith("✅") for l in labels):
                agent_issues.append(stats)

        total_sessions += len(sessions)
        total_size += agent_size
        all_issues.extend(agent_issues)

        # Show top issues for this agent
        if agent_issues:
            # Sort by size descending
            agent_issues.sort(key=lambda s: s["size_bytes"], reverse=True)
            shown = min(args.top, len(agent_issues))
            print(f"   ⚠️  {len(agent_issues)} sessions with issues (showing top {shown}):\n")

            for s in agent_issues[:shown]:
                sid = s["session_id"][:12]
                label_str = " ".join(s["labels"])
                size = fmt_size(s["size_bytes"])
                msgs = s["messages"]
                age = fmt_age(s["last_timestamp"], now)
                duration = fmt_duration(s["first_timestamp"], s["last_timestamp"])
                models = ", ".join(s["models_used"][:2]) if s["models_used"] else "unknown"

                # Use session label as primary identifier when available
                display_name = C.cyan(s["label"]) if s.get("label") else C.dim(sid)

                # Color the size
                if s["size_bytes"] > BLOAT_SIZE_BYTES * 5:
                    size = C.red(size)
                elif s["size_bytes"] > BLOAT_SIZE_BYTES:
                    size = C.yellow(size)

                print(f"   {display_name:>20}  {size:>12}  {msgs:>5} msgs  {age:>10}  {label_str}")
                if s.get("label"):
                    print(f"   {'':20}  id: {C.dim(sid)}")
                if s["compactions"] > 0:
                    eff = fmt_compaction_efficiency(s["size_bytes"], s["compactions"])
                    print(f"   {'':20}  compactions: {s['compactions']}, {eff}, duration: {duration}, models: {models}")
        else:
            print(f"   ✅ All sessions healthy\n")

        print()

    # ─── Summary ──────────────────────────────────────────────────────────

    print(C.bold("═══ Summary ═══════════════════════════════════════════════"))
    print(f"  Total sessions: {total_sessions}")
    print(f"  Total disk:     {fmt_size(total_size)}")
    print(f"  Issues found:   {len(all_issues)}")

    # Classify by severity
    red_issues = [s for s in all_issues if any("🔴" in l for l in s["labels"])]
    yellow_issues = [s for s in all_issues if any("🟡" in l for l in s["labels"]) and s not in red_issues]
    zombie_issues = [s for s in all_issues if any("👻" in l for l in s["labels"])]

    if red_issues:
        print(C.red(f"  🔴 Critical:    {len(red_issues)} sessions"))
    if yellow_issues:
        print(C.yellow(f"  🟡 Warning:     {len(yellow_issues)} sessions"))
    if zombie_issues:
        print(f"  👻 Zombies:     {len(zombie_issues)} sessions")

    # Reclaimable space
    reclaimable = sum(s["size_bytes"] for s in zombie_issues)
    stale_reclaimable = sum(s["size_bytes"] for s in all_issues
                           if any("stale" in l or "ancient" in l for l in s["labels"]))

    if reclaimable > 0 or stale_reclaimable > 0:
        print()
        print(C.bold("  Cleanup potential:"))
        if zombie_issues:
            print(f"    Zombie cleanup:  {fmt_size(reclaimable)} ({len(zombie_issues)} sessions)")
        if stale_reclaimable > 0:
            stale_count = len([s for s in all_issues if any("stale" in l or "ancient" in l for l in s["labels"])])
            print(f"    Stale cleanup:   {fmt_size(stale_reclaimable)} ({stale_count} sessions)")

    print()

    # ─── Recommendations ─────────────────────────────────────────────────
    if all_issues:
        print(C.bold("═══ Recommendations ═══════════════════════════════════════"))

        if red_issues:
            print(C.red("\n  🔴 CRITICAL — Action recommended:"))
            for s in red_issues[:5]:
                sid = s["session_id"][:12]
                print(f"     • {sid} ({fmt_size(s['size_bytes'])}, {s['messages']} msgs)")
            if len(red_issues) > 5:
                print(f"     ... and {len(red_issues) - 5} more")
            print(f"\n     Fix: clawdscan clean --min-size 5M --agent {red_issues[0]['agent']}")

        if zombie_issues:
            print(f"\n  👻 ZOMBIES — Safe to remove:")
            print(f"     {len(zombie_issues)} sessions with ≤2 messages, older than {ZOMBIE_HOURS}h")
            print(f"     Fix: clawdscan clean --zombies --agent <name>")

        stale_sessions = [s for s in all_issues if any("ancient" in l for l in s["labels"])]
        if stale_sessions:
            print(f"\n  🟡 ANCIENT — Consider archiving:")
            print(f"     {len(stale_sessions)} sessions with no activity for {STALE_DAYS * 4}+ days")
            print(f"     Fix: clawdscan clean --stale-days {STALE_DAYS * 4}")

        print()

    # JSON output
    if args.json:
        output = {
            "scan_time": now.isoformat(),
            "base_dir": str(base_dir),
            "total_sessions": total_sessions,
            "total_size_bytes": total_size,
            "issues_count": len(all_issues),
            "critical_count": len(red_issues),
            "warning_count": len(yellow_issues),
            "zombie_count": len(zombie_issues),
            "sessions": [{
                k: (v.isoformat() if isinstance(v, datetime) else
                    dict(v) if isinstance(v, Counter) else v)
                for k, v in s.items()
            } for s in all_stats] if args.verbose else None,
        }
        json_path = Path(args.json)
        with open(json_path, "w") as f:
            json.dump(output, f, indent=2, default=str)
        print(f"📄 JSON report saved to: {json_path}")


def cmd_top(args):
    """Show top sessions by size or message count."""
    base_dir = Path(args.dir) if args.dir else find_clawdbot_dir()
    now = datetime.now(timezone.utc)

    agents = discover_agents(base_dir)
    all_stats = []

    for agent in agents:
        if args.agent and agent["name"] != args.agent:
            continue
        sessions = scan_sessions(agent["sessions_dir"])
        for session_file in sessions:
            stats = analyze_session(session_file)
            stats["labels"] = classify_session(stats, now)
            stats["agent"] = agent["name"]
            all_stats.append(stats)

    if not all_stats:
        print("No sessions found.")
        return

    # Sort
    sort_key = "size_bytes" if args.sort == "size" else "messages"
    all_stats.sort(key=lambda s: s[sort_key], reverse=True)

    n = args.count
    print(C.bold(f"\n🏆 Top {n} sessions by {args.sort}\n"))
    print(f"  {'#':>3}  {'Agent':8}  {'Label/Session':20}  {'Size':>10}  {'Msgs':>6}  {'User':>5}  "
          f"{'Tools':>5}  {'Compact':>7}  {'Last Active':>12}  Labels")
    print(f"  {'─' * 3}  {'─' * 8}  {'─' * 20}  {'─' * 10}  {'─' * 6}  {'─' * 5}  "
          f"{'─' * 5}  {'─' * 7}  {'─' * 12}  {'─' * 20}")

    for i, s in enumerate(all_stats[:n], 1):
        sid = s["session_id"][:12]
        display_name = s.get("label", sid) or sid
        if len(display_name) > 20:
            display_name = display_name[:17] + "..."
        size = fmt_size(s["size_bytes"])
        labels = " ".join(s["labels"])

        if s["size_bytes"] > BLOAT_SIZE_BYTES * 5:
            size = C.red(size)
        elif s["size_bytes"] > BLOAT_SIZE_BYTES:
            size = C.yellow(size)

        print(f"  {i:>3}  {s['agent']:8}  {display_name:20}  {size:>10}  {s['messages']:>6}  "
              f"{s['user_messages']:>5}  {s['tool_calls']:>5}  {s['compactions']:>7}  "
              f"{fmt_age(s['last_timestamp'], now):>12}  {labels}")

    print()


def cmd_inspect(args):
    """Deep-inspect a single session."""
    base_dir = Path(args.dir) if args.dir else find_clawdbot_dir()
    now = datetime.now(timezone.utc)

    # Find the session file
    session_file = None
    for agent in discover_agents(base_dir):
        for f in agent["sessions_dir"].iterdir():
            if args.session_id in f.name:
                session_file = f
                break
        if session_file:
            break

    if not session_file:
        print(C.red(f"Session not found: {args.session_id}"))
        print("Tip: use the first 8+ chars of the session ID")
        sys.exit(1)

    stats = analyze_session(session_file)
    labels = classify_session(stats, now)

    print(C.bold(f"\n🔬 Session Inspection: {stats['session_id'][:16]}"))
    print(f"   File: {stats['path']}")
    print(f"   Size: {fmt_size(stats['size_bytes'])}")
    print(f"   Health: {' '.join(labels)}")
    print()

    print(C.bold("  Messages"))
    print(f"    Total:     {stats['messages']}")
    print(f"    User:      {stats['user_messages']}")
    print(f"    Assistant: {stats['assistant_messages']}")
    print(f"    Tool calls: {stats['tool_calls']}")
    print()

    print(C.bold("  Timeline"))
    print(f"    Created:      {stats['created'] or 'unknown'}")
    print(f"    First msg:    {stats['first_timestamp'] or 'unknown'}")
    print(f"    Last msg:     {stats['last_timestamp'] or 'unknown'}")
    print(f"    Duration:     {fmt_duration(stats['first_timestamp'], stats['last_timestamp'])}")
    print(f"    Last active:  {fmt_age(stats['last_timestamp'], now)}")
    print()

    print(C.bold("  Models"))
    for m in stats["models_used"]:
        print(f"    • {m}")
    print(f"    Model switches: {stats['model_changes']}")
    print()

    if stats["compactions"]:
        print(C.bold("  Compaction"))
        print(f"    Count: {stats['compactions']}")
        eff = fmt_compaction_efficiency(stats["size_bytes"], stats["compactions"])
        print(f"    Efficiency: {eff}")
        print()

    if stats["tools_used"]:
        print(C.bold("  Tool Usage (top 10)"))
        top_tools = stats["tools_used"].most_common(10)
        max_tool_count = top_tools[0][1] if top_tools else 1
        for tool, count in top_tools:
            bar_len = max(1, int(40 * count / max_tool_count))
            bar = "█" * bar_len
            print(f"    {tool:30s} {count:>5}  {C.cyan(bar)}")
        print()

    if stats["custom_types"]:
        print(C.bold("  Custom Event Types"))
        for ct, count in stats["custom_types"].most_common():
            print(f"    {ct:30s} {count:>5}")
        print()

    if stats.get("cwd"):
        print(f"  Working Dir: {stats['cwd']}")
    if stats.get("label"):
        print(f"  Label: {stats['label']}")
    if stats["errors"]:
        print(C.yellow(f"  Parse Errors: {stats['errors']}"))

    print()


def cmd_clean(args):
    """Clean up zombie and stale sessions (with dry-run by default)."""
    base_dir = Path(args.dir) if args.dir else find_clawdbot_dir()
    now = datetime.now(timezone.utc)

    agents = discover_agents(base_dir)
    targets = []

    for agent in agents:
        if args.agent and agent["name"] != args.agent:
            continue
        sessions = scan_sessions(agent["sessions_dir"])
        for session_file in sessions:
            stats = analyze_session(session_file)
            labels = classify_session(stats, now)

            should_clean = False
            reason = ""

            if args.zombies and any("👻" in l for l in labels):
                should_clean = True
                reason = "zombie (≤2 msgs, >48h old)"

            if args.stale_days:
                last = stats["last_timestamp"] or stats["mtime"]
                if last and (now - last) > timedelta(days=args.stale_days):
                    should_clean = True
                    reason = f"stale (>{args.stale_days} days)"

            if args.min_size:
                size_threshold = parse_size(args.min_size)
                if stats["size_bytes"] > size_threshold:
                    should_clean = True
                    reason = f"oversized (>{args.min_size})"

            if should_clean:
                targets.append({
                    "stats": stats,
                    "agent": agent["name"],
                    "reason": reason,
                    "file": session_file,
                })

    if not targets:
        print("✅ No sessions match cleanup criteria.")
        return

    total_size = sum(t["stats"]["size_bytes"] for t in targets)

    print(C.bold(f"\n🧹 Cleanup Plan — {len(targets)} sessions ({fmt_size(total_size)})\n"))

    for t in targets:
        s = t["stats"]
        sid = s["session_id"][:12]
        print(f"  {t['agent']:8}  {sid}  {fmt_size(s['size_bytes']):>10}  {s['messages']:>5} msgs  "
              f"reason: {t['reason']}")

    print()

    if args.dry_run:
        print(C.yellow("  ⚡ DRY RUN — no files modified"))
        print(f"  To execute: add --execute")
        print(f"  Reclaimable: {fmt_size(total_size)}")
    else:
        confirm = input(f"\n  Delete {len(targets)} sessions ({fmt_size(total_size)})? [y/N] ").strip().lower()
        if confirm != "y":
            print("  Cancelled.")
            return

        archive_dir = base_dir / "archived-sessions" / now.strftime("%Y%m%d-%H%M%S")
        archive_dir.mkdir(parents=True, exist_ok=True)

        for t in targets:
            dest = archive_dir / f"{t['agent']}_{t['file'].name}"
            shutil.move(str(t["file"]), str(dest))

        print(C.green(f"\n  ✅ Moved {len(targets)} sessions to {archive_dir}"))
        print(f"  Freed: {fmt_size(total_size)}")
        print(f"  To undo: move files back from {archive_dir}")

    print()


def cmd_tools(args):
    """Aggregate tool usage across all sessions."""
    base_dir = Path(args.dir) if args.dir else find_clawdbot_dir()
    agents = discover_agents(base_dir)

    tool_totals = Counter()
    session_count = 0

    for agent in agents:
        if args.agent and agent["name"] != args.agent:
            continue
        sessions = scan_sessions(agent["sessions_dir"])
        for session_file in sessions:
            stats = analyze_session(session_file)
            tool_totals += stats["tools_used"]
            session_count += 1

    if not tool_totals:
        print("No tool usage found.")
        return

    print(C.bold(f"\n🔧 Tool Usage Across {session_count} Sessions\n"))

    max_count = max(tool_totals.values())
    for tool, count in tool_totals.most_common(args.count):
        bar_len = int(40 * count / max_count)
        bar = "█" * bar_len
        print(f"  {tool:35s} {count:>6}  {C.cyan(bar)}")

    print()


def cmd_models(args):
    """Show model usage patterns across sessions."""
    base_dir = Path(args.dir) if args.dir else find_clawdbot_dir()
    agents = discover_agents(base_dir)

    model_sessions = defaultdict(int)
    model_messages = defaultdict(int)
    session_count = 0

    for agent in agents:
        if args.agent and agent["name"] != args.agent:
            continue
        sessions = scan_sessions(agent["sessions_dir"])
        for session_file in sessions:
            stats = analyze_session(session_file)
            session_count += 1
            for model in stats["models_used"]:
                model_sessions[model] += 1
                model_messages[model] += stats["messages"]

    if not model_sessions:
        print("No model usage found.")
        return

    print(C.bold(f"\n🤖 Model Usage Across {session_count} Sessions\n"))
    print(f"  {'Model':40}  {'Sessions':>10}  {'Messages':>10}")
    print(f"  {'─' * 40}  {'─' * 10}  {'─' * 10}")

    for model in sorted(model_sessions.keys(), key=lambda m: model_sessions[m], reverse=True):
        print(f"  {model:40}  {model_sessions[model]:>10}  {model_messages[model]:>10}")

    print()


def cmd_disk(args):
    """Show disk usage breakdown."""
    base_dir = Path(args.dir) if args.dir else find_clawdbot_dir()
    agents = discover_agents(base_dir)

    print(C.bold(f"\n💾 Disk Usage — {base_dir}\n"))

    total = 0
    for agent in agents:
        sessions = scan_sessions(agent["sessions_dir"], include_deleted=True)
        active = [f for f in sessions if ".deleted." not in f.name]
        deleted = [f for f in sessions if ".deleted." in f.name]

        active_size = sum(f.stat().st_size for f in active)
        deleted_size = sum(f.stat().st_size for f in deleted)
        agent_total = active_size + deleted_size

        print(f"  {C.bold(agent['name']):20}")
        print(f"    Active:  {len(active):>5} sessions  {fmt_size(active_size):>10}")
        print(f"    Deleted: {len(deleted):>5} sessions  {fmt_size(deleted_size):>10}")
        print(f"    Total:   {len(sessions):>5} sessions  {fmt_size(agent_total):>10}")

        # Size distribution
        if active:
            sizes = sorted([f.stat().st_size for f in active])
            p50 = sizes[len(sizes) // 2]
            p90 = sizes[int(len(sizes) * 0.9)]
            p99 = sizes[int(len(sizes) * 0.99)]
            print(f"    Median:  {fmt_size(p50):>10}  P90: {fmt_size(p90):>10}  P99: {fmt_size(p99):>10}")

        total += agent_total
        print()

    print(f"  {C.bold('TOTAL'):20}  {fmt_size(total):>30}")

    # Check other dirs
    other_dirs = ["extensions", "plugins", "cache", "logs"]
    other_total = 0
    for d in other_dirs:
        p = base_dir / d
        if p.exists():
            size = sum(f.stat().st_size for f in p.rglob("*") if f.is_file())
            if size > 0:
                print(f"  {d:20}  {fmt_size(size):>30}")
                other_total += size

    if other_total > 0:
        print(f"  {'OTHER':20}  {fmt_size(other_total):>30}")
        print(f"  {'GRAND TOTAL':20}  {fmt_size(total + other_total):>30}")

    print()


def cmd_history(args):
    """Display session health trends over time."""
    base_dir = Path(args.dir) if args.dir else find_clawdbot_dir()
    agents = discover_agents(base_dir)
    
    days = args.days
    now = datetime.now(timezone.utc)
    start_date = now - timedelta(days=days)

    print(C.bold(f"\n📈 Session Health Trends (Last {days} Days)\n"))
    
    # Collect all sessions across agents
    all_sessions = []
    for agent in agents:
        sessions = scan_sessions(agent["sessions_dir"])
        for session_file in sessions:
            if ".deleted." in session_file.name:
                continue
            try:
                created = datetime.fromtimestamp(session_file.stat().st_mtime, timezone.utc)
                if created >= start_date:
                    size = session_file.stat().st_size
                    # Count messages by reading file
                    message_count = 0
                    try:
                        with open(session_file, 'r') as f:
                            for line in f:
                                if line.strip():
                                    message_count += 1
                    except:
                        message_count = 0
                    
                    all_sessions.append({
                        'file': session_file,
                        'created': created,
                        'size': size,
                        'messages': message_count,
                        'agent': agent['name']
                    })
            except Exception:
                continue
    
    if not all_sessions:
        print("No sessions found in the specified time range.")
        return
    
    # Group sessions by week
    history_data = {}
    
    for session in all_sessions:
        created_date = session['created']
        days_from_start = (created_date - start_date).days
        week_num = days_from_start // 7
        week_key = f"Week {week_num + 1}"
        
        if week_key not in history_data:
            history_data[week_key] = {
                'sessions': [],
                'total_size': 0,
                'bloated': 0,
                'zombies': 0,
                'date_range': None
            }
        
        history_data[week_key]['sessions'].append(session)
        history_data[week_key]['total_size'] += session['size']
        
        # Check for bloated sessions
        if session['size'] > BLOAT_SIZE_BYTES or session['messages'] > BLOAT_MSG_COUNT:
            history_data[week_key]['bloated'] += 1
        
        # Check for zombie sessions (very few messages)
        if session['messages'] <= 2:
            history_data[week_key]['zombies'] += 1

    # Calculate date ranges for each week
    for week_key, data in history_data.items():
        week_num = int(week_key.split()[1]) - 1
        week_start = start_date + timedelta(days=week_num * 7)
        week_end = min(week_start + timedelta(days=6), now)
        data['date_range'] = f"{week_start.strftime('%b %d')}-{week_end.strftime('%d')}"

    prev_sessions = 0
    prev_size = 0

    for week_key in sorted(history_data.keys(), key=lambda x: int(x.split()[1])):
        data = history_data[week_key]
        session_count = len(data['sessions'])
        total_size = data['total_size']
        
        # Calculate growth
        if prev_sessions > 0:
            session_growth = ((session_count - prev_sessions) / prev_sessions) * 100
            size_growth = ((total_size - prev_size) / prev_size) * 100 if prev_size > 0 else 0
            growth_indicator = "📈" if session_growth > 10 else "📊" if session_growth > 0 else "📉"
            print(f"{week_key} ({data['date_range']}): {session_count:3d} sessions, {fmt_size(total_size):>8s} "
                  f"{growth_indicator} {session_growth:+.0f}% sessions, {size_growth:+.0f}% size")
        else:
            print(f"{week_key} ({data['date_range']}): {session_count:3d} sessions, {fmt_size(total_size):>8s}")
        
        prev_sessions = session_count
        prev_size = total_size

    # Show issue trends
    print(f"\n{C.bold('🔥 Issue Trends:')}")
    bloat_counts = []
    zombie_counts = []
    
    for week_key in sorted(history_data.keys(), key=lambda x: int(x.split()[1])):
        data = history_data[week_key]
        bloat_counts.append(str(data['bloated']))
        zombie_counts.append(str(data['zombies']))
    
    print(f"Bloated Sessions: {' → '.join(bloat_counts)}")
    print(f"Zombie Sessions:  {' → '.join(zombie_counts)}")

    # Calculate overall growth rate
    if len(history_data) > 1:
        first_week = list(history_data.values())[0]
        last_week = list(history_data.values())[-1]
        
        weeks = len(history_data)
        if len(first_week['sessions']) > 0:
            session_growth_rate = ((len(last_week['sessions']) / len(first_week['sessions'])) ** (1/weeks) - 1) * 100
        else:
            session_growth_rate = 0
            
        if first_week['total_size'] > 0:
            size_growth_rate = ((last_week['total_size'] / first_week['total_size']) ** (1/weeks) - 1) * 100
        else:
            size_growth_rate = 0
        
        print(f"\n{C.bold('💡 Growth Rate:')} {session_growth_rate:+.0f}% sessions/week, {size_growth_rate:+.0f}% storage/week")

    print()


def cmd_watch(args):
    """Watch sessions directory and alert when thresholds are crossed."""
    import time

    base_dir = Path(args.dir) if args.dir else find_clawdbot_dir()
    interval = args.interval

    print(C.bold(f"\n👁️  clawdscan watch — monitoring {base_dir}"))
    print(C.dim(f"   Interval: {interval}s | Ctrl+C to stop"))
    print(C.dim(f"   Thresholds: size>{fmt_size(BLOAT_SIZE_BYTES)}, msgs>{BLOAT_MSG_COUNT}\n"))

    prev_issues = set()

    try:
        while True:
            now = datetime.now(timezone.utc)
            agents = discover_agents(base_dir)
            current_issues = set()
            new_alerts = []

            for agent in agents:
                sessions = scan_sessions(agent["sessions_dir"])
                for session_file in sessions:
                    stats = analyze_session(session_file)
                    labels = classify_session(stats, now)

                    if not all(l.startswith("✅") for l in labels):
                        issue_key = stats["session_id"]
                        current_issues.add(issue_key)

                        if issue_key not in prev_issues:
                            display = stats.get("label") or stats["session_id"][:12]
                            new_alerts.append(
                                f"  ⚡ NEW: {display} ({agent['name']}) — "
                                f"{fmt_size(stats['size_bytes'])}, {stats['messages']} msgs — "
                                f"{' '.join(labels)}"
                            )

            if new_alerts:
                ts = now.strftime("%H:%M:%S")
                print(f"\n[{ts}] {C.yellow(f'{len(new_alerts)} new issue(s)')}")
                for a in new_alerts:
                    print(a)
            else:
                # Quiet tick
                ts = now.strftime("%H:%M:%S")
                total_issues = len(current_issues)
                print(f"[{ts}] ✅ {total_issues} tracked issues, 0 new", end="\r")

            prev_issues = current_issues
            time.sleep(interval)

    except KeyboardInterrupt:
        print(f"\n\n👋 Watch stopped.")


def parse_size(s: str) -> int:
    """Parse size string like '5M', '100K', '1G'."""
    s = s.strip().upper()
    multipliers = {"B": 1, "K": 1024, "KB": 1024, "M": 1024**2, "MB": 1024**2,
                   "G": 1024**3, "GB": 1024**3}
    for suffix, mult in sorted(multipliers.items(), key=lambda x: -len(x[0])):
        if s.endswith(suffix):
            return int(float(s[:-len(suffix)]) * mult)
    return int(s)


# ─── Skill Health Check ──────────────────────────────────────────────────────

DEFAULT_SKILL_DIRS = [
    os.path.expanduser("/opt/homebrew/lib/node_modules/openclaw/skills"),
    os.path.expanduser("~/workspace/skills"),
]


def _get_skill_dirs(extra_dirs=None):
    """Build skill directory list from OpenClaw config + defaults + extra dirs."""
    dirs = list(DEFAULT_SKILL_DIRS)
    for config_path in [
        os.path.expanduser("~/.openclaw/openclaw.json"),
        os.path.expanduser("~/.clawdbot/clawdbot.json"),
    ]:
        try:
            with open(config_path) as f:
                config = json.load(f)
            agents_cfg = config.get("agents", {}).get("defaults", {})
            skill_dirs_cfg = agents_cfg.get("skillDirs", [])
            if isinstance(skill_dirs_cfg, list):
                dirs.extend([os.path.expanduser(p) for p in skill_dirs_cfg])
            elif isinstance(skill_dirs_cfg, str):
                dirs.append(os.path.expanduser(skill_dirs_cfg))
            skills_cfg = config.get("skills", {})
            if isinstance(skills_cfg, dict):
                for key in ("dirs", "paths", "directories"):
                    paths = skills_cfg.get(key, [])
                    if isinstance(paths, list):
                        dirs.extend([os.path.expanduser(p) for p in paths])
                    elif isinstance(paths, str):
                        dirs.append(os.path.expanduser(paths))
            break
        except (FileNotFoundError, json.JSONDecodeError, KeyError):
            continue
    if extra_dirs:
        dirs.extend([os.path.expanduser(d) for d in extra_dirs])
    seen = set()
    unique = []
    for d in dirs:
        real = os.path.realpath(d)
        if real not in seen:
            seen.add(real)
            unique.append(d)
    return unique


def _parse_skill_frontmatter(path):
    """Extract YAML frontmatter from SKILL.md."""
    try:
        with open(path) as f:
            content = f.read()
    except Exception:
        return None
    if not content.startswith("---"):
        return None
    end = content.find("---", 3)
    if end == -1:
        return None
    fm_text = content[3:end].strip()
    try:
        if _yaml:
            return _yaml.safe_load(fm_text)
        return _parse_simple_fm(fm_text)
    except Exception:
        return _parse_simple_fm(fm_text)


def _parse_simple_fm(text):
    """Minimal frontmatter parser without PyYAML."""
    result = {}
    for line in text.split("\n"):
        m = re.match(r'^(\w[\w-]*)\s*:\s*(.+)$', line)
        if m:
            key, val = m.group(1), m.group(2).strip()
            if val.startswith('"') and val.endswith('"'):
                val = val[1:-1]
            result[key] = val
    json_match = re.search(r'"openclaw"\s*:\s*(\{[^}]*(?:\{[^}]*\}[^}]*)*\})', text)
    if json_match:
        try:
            oc = json.loads(json_match.group(1))
            if "metadata" not in result or not isinstance(result.get("metadata"), dict):
                result["metadata"] = {}
            result["metadata"]["openclaw"] = oc
        except json.JSONDecodeError:
            pass
    meta_match = re.search(r'metadata\s*:\s*\n\s*(\{[\s\S]*?\})\s*\n---', text + "\n---")
    if meta_match and not isinstance(result.get("metadata"), dict):
        try:
            result["metadata"] = json.loads(meta_match.group(1))
        except json.JSONDecodeError:
            pass
    return result if result else None


def _scan_skills(skill_dirs):
    """Scan skill directories and return skill info list."""
    skills = []
    current_os = platform.system().lower()
    for skill_dir in skill_dirs:
        if not os.path.isdir(skill_dir):
            continue
        for skill_path in sorted(glob.glob(os.path.join(skill_dir, "*/SKILL.md"))):
            skill_name = os.path.basename(os.path.dirname(skill_path))
            source = "builtin" if "node_modules" in skill_path else "custom"
            fm = _parse_skill_frontmatter(skill_path)
            meta = {}
            if fm and isinstance(fm, dict):
                m = fm.get("metadata", {})
                if isinstance(m, dict):
                    meta = m.get("openclaw", {})
            requires = meta.get("requires", {}) if meta else {}
            skill = {
                "name": skill_name,
                "path": os.path.dirname(skill_path),
                "skill_md_path": skill_path,
                "source": source,
                "description": fm.get("description", "") if fm else "",
                "os_req": meta.get("os", []),
                "required_bins": requires.get("bins", []),
                "optional_bins": requires.get("optional_bins", []),
                "bin_versions": requires.get("bin_versions", {}),
                "install_info": meta.get("install", []) if meta else [],
                "bins_status": {},
                "optional_bins_status": {},
                "version_issues": [],
                "os_ok": True,
                "healthy": True,
                "warnings": [],
                "issues": [],
                "inferred_bins": [],
                "inferred_bins_status": {},
            }
            if skill["os_req"]:
                os_map = {"darwin": "darwin", "linux": "linux", "win32": "windows"}
                if current_os not in [os_map.get(o, o) for o in skill["os_req"]]:
                    skill["os_ok"] = False
                    skill["healthy"] = False
                    skill["issues"].append(f"OS mismatch: needs {skill['os_req']}, have {current_os}")
            for bin_name in skill["required_bins"]:
                found = shutil.which(bin_name) is not None
                skill["bins_status"][bin_name] = found
                if not found:
                    skill["healthy"] = False
                    skill["issues"].append(f"Missing binary: {bin_name}")
            for bin_name in skill["optional_bins"]:
                found = shutil.which(bin_name) is not None
                skill["optional_bins_status"][bin_name] = found
                if not found:
                    skill["warnings"].append(f"Optional missing: {bin_name}")
            skills.append(skill)
    return skills


def _infer_deps_from_body(skill_md_path):
    """Scan SKILL.md body text for CLI tool references when no deps are declared."""
    try:
        with open(skill_md_path) as f:
            content = f.read()
    except Exception:
        return []
    # Strip frontmatter
    if content.startswith("---"):
        end = content.find("---", 3)
        if end != -1:
            content = content[end + 3:]
    inferred = set()
    # Pattern: "requires `tool`", "uses `tool`", "install `tool`", "needs `tool`",
    # "depends on `tool`", "`tool` must be installed"
    for m in re.finditer(r'(?:requires|uses|install|needs|depends\s+on)\s+`([a-zA-Z0-9_-]+)`', content, re.IGNORECASE):
        inferred.add(m.group(1))
    for m in re.finditer(r'`([a-zA-Z0-9_-]+)`\s+must\s+be\s+installed', content, re.IGNORECASE):
        inferred.add(m.group(1))
    # Code block patterns: brew install X, npm install -g X, pip install X, apt install X
    # Skip brew tap patterns like "steipete/tap/camsnap" — only take the last segment
    for m in re.finditer(r'(?:brew|apt|apt-get)\s+install\s+(?:-\S+\s+)*([a-zA-Z0-9_/-]+)', content):
        pkg = m.group(1).split("/")[-1]  # handle tap paths like user/tap/formula
        inferred.add(pkg)
    for m in re.finditer(r'npm\s+install\s+(?:-g\s+)?([a-zA-Z0-9_@/-]+)', content):
        pkg = m.group(1).split("/")[-1]  # handle scoped packages
        inferred.add(pkg)
    for m in re.finditer(r'pip\s+install\s+([a-zA-Z0-9_-]+)', content):
        inferred.add(m.group(1))
    # Filter out common non-tool words and false positives
    noise = {"the", "a", "an", "and", "or", "for", "to", "in", "on", "it", "is", "be", "this", "that",
             "your", "you", "with", "from", "not", "can", "will", "all", "use", "run", "set", "get",
             "add", "new", "see", "e", "g", "i", "s", "t", "v", "commands", "export", "requests",
             "install", "update", "config", "setup", "build", "test", "check", "start", "stop",
             "init", "create", "delete", "list", "show", "help", "version", "status", "enable",
             "disable", "reset", "clean", "clear", "remove", "search", "find", "open", "close",
             "file", "path", "name", "key", "value", "type", "mode", "level", "output", "input",
             "server", "client", "source", "target", "local", "remote", "global", "default"}
    filtered = set()
    for item in inferred - noise:
        # Skip ALL_CAPS (env vars like GOOGLE_PLACES_API_KEY)
        if item.isupper() and len(item) > 1:
            continue
        # Skip items starting with - (flags like -e, -g)
        if item.startswith("-"):
            continue
        # Skip date-like patterns (2025-09-03)
        if re.match(r'^\d{4}(-\d{2}){0,2}$', item):
            continue
        # Skip pure numbers
        if item.isdigit():
            continue
        # Skip very short items (likely noise)
        if len(item) <= 1:
            continue
        # Skip items with underscores (likely env vars or internal names)
        if "_" in item and item == item.upper():
            continue
        filtered.add(item)
    return sorted(filtered)


def _check_bin_version(bin_name, version_spec):
    """Run `tool --version` and compare against a minimum version spec like '>=6.0'."""
    try:
        result = subprocess.run(
            [bin_name, "--version"], capture_output=True, text=True, timeout=5
        )
        output = result.stdout.strip() or result.stderr.strip()
    except Exception:
        return None, "could not run --version"
    # Parse version from output
    ver_match = re.search(r'(\d+(?:\.\d+)+)', output)
    if not ver_match:
        return None, f"could not parse version from: {output[:80]}"
    actual_ver = ver_match.group(1)
    # Parse spec
    spec_match = re.match(r'(>=|>|==|<=|<)\s*(.+)', version_spec.strip())
    if not spec_match:
        return actual_ver, f"invalid version spec: {version_spec}"
    op, required_ver = spec_match.group(1), spec_match.group(2)
    # Compare versions
    actual_parts = [int(x) for x in actual_ver.split(".")]
    required_parts = [int(x) for x in required_ver.split(".")]
    # Pad to same length
    max_len = max(len(actual_parts), len(required_parts))
    actual_parts.extend([0] * (max_len - len(actual_parts)))
    required_parts.extend([0] * (max_len - len(required_parts)))
    if op == ">=" and actual_parts >= required_parts:
        return actual_ver, None
    elif op == ">" and actual_parts > required_parts:
        return actual_ver, None
    elif op == "==" and actual_parts == required_parts:
        return actual_ver, None
    elif op == "<=" and actual_parts <= required_parts:
        return actual_ver, None
    elif op == "<" and actual_parts < required_parts:
        return actual_ver, None
    return actual_ver, f"have {actual_ver}, need {version_spec}"


def _skill_install_hint(skill):
    """Get install hints for a broken skill."""
    hints = []
    for inst in skill.get("install_info", []):
        if isinstance(inst, dict):
            kind = inst.get("kind", "")
            if kind == "brew":
                hints.append(f"brew install {inst.get('formula', '')}")
            elif kind == "npm":
                hints.append(f"npm install -g {inst.get('package', '')}")
            elif kind == "pip":
                hints.append(f"pip install {inst.get('package', '')}")
            elif kind == "shell":
                hints.append(inst.get("cmd", ""))
    return [h for h in hints if h.strip()]


def cmd_skills(args):
    """Skill dependency health check."""
    skill_dirs = _get_skill_dirs(extra_dirs=getattr(args, 'dirs', None))
    skills = _scan_skills(skill_dirs)
    do_infer = getattr(args, 'infer', False)
    do_versions = getattr(args, 'check_versions', False)

    # Inference pass: scan SKILL.md body for deps when none declared
    if do_infer:
        for s in skills:
            if not s["required_bins"] and not s["optional_bins"]:
                inferred = _infer_deps_from_body(s["skill_md_path"])
                s["inferred_bins"] = inferred
                for bin_name in inferred:
                    found = shutil.which(bin_name) is not None
                    s["inferred_bins_status"][bin_name] = found
                    if not found:
                        s["warnings"].append(f"Inferred missing: {bin_name}")

    # Version check pass
    if do_versions:
        for s in skills:
            for bin_name, spec in s.get("bin_versions", {}).items():
                if shutil.which(bin_name):
                    actual, err = _check_bin_version(bin_name, spec)
                    if err:
                        s["version_issues"].append(f"{bin_name}: {err}")
                        s["warnings"].append(f"Version mismatch: {bin_name} ({err})")

    if getattr(args, 'skill', None):
        skills = [s for s in skills if s["name"] == args.skill]
        if not skills:
            print(f"Skill '{args.skill}' not found")
            sys.exit(1)

    # Apply filter
    filt = getattr(args, 'filter', None)
    if filt == "broken":
        skills = [s for s in skills if not s["healthy"]]
    elif filt == "healthy":
        skills = [s for s in skills if s["healthy"]]

    healthy = [s for s in skills if s["healthy"]]
    broken = [s for s in skills if not s["healthy"]]
    no_deps = [s for s in skills if not s["required_bins"] and not s["os_req"] and not s["inferred_bins"]]
    with_warnings = [s for s in skills if s["warnings"]]

    # Fix-hints mode: just print install commands
    if getattr(args, 'fix_hints', False):
        any_hints = False
        for s in [sk for sk in skills if not sk["healthy"]]:
            hints = _skill_install_hint(s)
            if hints:
                print(f"# {s['name']}")
                for h in hints:
                    print(h)
                print()
                any_hints = True
            else:
                missing = [b for b, ok in s["bins_status"].items() if not ok]
                if missing:
                    print(f"# {s['name']} — no install info, missing: {', '.join(missing)}")
                    print()
                    any_hints = True
        if not any_hints:
            print("All skills healthy! Nothing to fix.")
        return

    # JSON output
    if getattr(args, 'json_out', None):
        target = sys.stdout if args.json_out == "-" else open(args.json_out, "w")
        json.dump(skills, target, indent=2)
        if args.json_out == "-":
            print()
        return

    print(f"\n🩺 Skill Health Report")
    print(f"{'='*60}")
    print(f"📦 Total skills scanned: {len(skills)}")
    print(f"✅ Healthy: {len(healthy)}")
    print(f"❌ Broken:  {len(broken)}")
    if with_warnings:
        print(f"⚠️  Warnings: {len(with_warnings)}")
    print(f"📝 No deps declared: {len(no_deps)}")
    print(f"📂 Directories: {', '.join(skill_dirs)}")
    print()

    if broken:
        print(f"❌ BROKEN SKILLS ({len(broken)})")
        print(f"{'-'*60}")
        for s in broken:
            print(f"\n  🔴 {s['name']} ({s['source']})")
            for issue in s["issues"]:
                print(f"     ⚠️  {issue}")
            hints = _skill_install_hint(s)
            for h in hints:
                print(f"     💡 Fix: {h}")
        print()

    if with_warnings:
        print(f"⚠️  SKILLS WITH WARNINGS ({len(with_warnings)})")
        print(f"{'-'*60}")
        for s in with_warnings:
            if s in broken:
                continue  # already shown above
            print(f"\n  🟡 {s['name']} ({s['source']})")
            for w in s["warnings"]:
                print(f"     ⚠️  {w}")
        print()

    if do_infer:
        inferred_skills = [s for s in skills if s["inferred_bins"]]
        if inferred_skills:
            print(f"🔍 INFERRED DEPENDENCIES ({len(inferred_skills)} skills)")
            print(f"{'-'*60}")
            for s in inferred_skills:
                found = [b for b, ok in s["inferred_bins_status"].items() if ok]
                missing = [b for b, ok in s["inferred_bins_status"].items() if not ok]
                status_parts = []
                if found:
                    status_parts.append(f"✅ {', '.join(found)}")
                if missing:
                    status_parts.append(f"❌ {', '.join(missing)}")
                print(f"  {s['name']}: {' | '.join(status_parts)}")
            print()

    if getattr(args, 'verbose', False):
        print(f"✅ HEALTHY SKILLS ({len(healthy)})")
        print(f"{'-'*60}")
        for s in healthy:
            bins = ", ".join(s["required_bins"]) if s["required_bins"] else "none"
            print(f"  🟢 {s['name']} ({s['source']}) — bins: {bins}")
        print()


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        prog="clawdscan",
        description="🔍 Clawdbot Session Health Analyzer — diagnose bloat, find zombies, reclaim disk",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  clawdscan scan                    Full health scan of all sessions
  clawdscan scan --json report.json Export full report as JSON
  clawdscan top -n 20               Top 20 largest sessions
  clawdscan top --sort messages     Top sessions by message count
  clawdscan inspect <session-id>    Deep-inspect a specific session
  clawdscan tools                   Aggregate tool usage stats
  clawdscan models                  Model usage patterns
  clawdscan disk                    Disk usage breakdown
  clawdscan clean --zombies         Preview zombie cleanup
  clawdscan clean --zombies --execute  Execute zombie cleanup
  clawdscan clean --stale-days 28   Clean sessions inactive >28 days
  clawdscan history                 View session health trends (last 30 days)
  clawdscan history --days 7        View trends for last week
        """,
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument("--dir", help="Clawdbot config directory (default: ~/.clawdbot or ~/.openclaw)")

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Common --dir argument for all subcommands
    dir_kwargs = {"help": "Clawdbot config directory (default: ~/.clawdbot or ~/.openclaw)"}

    # scan
    p_scan = subparsers.add_parser("scan", help="Full health scan")
    p_scan.add_argument("--dir", **dir_kwargs)
    p_scan.add_argument("--agent", help="Filter to specific agent")
    p_scan.add_argument("--top", type=int, default=LARGE_SESSION_TOP_N, help="Show top N issues per agent")
    p_scan.add_argument("--include-deleted", action="store_true", help="Include soft-deleted sessions")
    p_scan.add_argument("--json", metavar="FILE", help="Export report as JSON")
    p_scan.add_argument("--verbose", action="store_true", help="Include all session details in JSON")
    p_scan.set_defaults(func=cmd_scan)

    # top
    p_top = subparsers.add_parser("top", help="Top sessions by size or messages")
    p_top.add_argument("--dir", **dir_kwargs)
    p_top.add_argument("-n", "--count", type=int, default=LARGE_SESSION_TOP_N, help="Number of sessions")
    p_top.add_argument("--sort", choices=["size", "messages"], default="size", help="Sort by")
    p_top.add_argument("--agent", help="Filter to specific agent")
    p_top.set_defaults(func=cmd_top)

    # inspect
    p_inspect = subparsers.add_parser("inspect", help="Deep-inspect a session")
    p_inspect.add_argument("--dir", **dir_kwargs)
    p_inspect.add_argument("session_id", help="Session ID (first 8+ chars)")
    p_inspect.set_defaults(func=cmd_inspect)

    # tools
    p_tools = subparsers.add_parser("tools", help="Aggregate tool usage")
    p_tools.add_argument("--dir", **dir_kwargs)
    p_tools.add_argument("--agent", help="Filter to specific agent")
    p_tools.add_argument("-n", "--count", type=int, default=30, help="Top N tools")
    p_tools.set_defaults(func=cmd_tools)

    # models
    p_models = subparsers.add_parser("models", help="Model usage patterns")
    p_models.add_argument("--dir", **dir_kwargs)
    p_models.add_argument("--agent", help="Filter to specific agent")
    p_models.set_defaults(func=cmd_models)

    # disk
    p_disk = subparsers.add_parser("disk", help="Disk usage breakdown")
    p_disk.add_argument("--dir", **dir_kwargs)
    p_disk.set_defaults(func=cmd_disk)

    # clean
    p_clean = subparsers.add_parser("clean", help="Clean up sessions")
    p_clean.add_argument("--dir", **dir_kwargs)
    p_clean.add_argument("--agent", help="Filter to specific agent")
    p_clean.add_argument("--zombies", action="store_true", help="Clean zombie sessions (≤2 msgs, >48h)")
    p_clean.add_argument("--stale-days", type=int, help="Clean sessions inactive for N+ days")
    p_clean.add_argument("--min-size", help="Clean sessions larger than size (e.g. 5M, 100K)")
    p_clean.add_argument("--execute", dest="dry_run", action="store_false", default=True,
                         help="Actually move files (default: dry-run)")
    p_clean.set_defaults(func=cmd_clean)

    # history
    p_history = subparsers.add_parser("history", help="View session health trends over time")
    p_history.add_argument("--dir", **dir_kwargs)
    p_history.add_argument("--days", type=int, default=30, help="Number of days of history (default: 30)")
    p_history.set_defaults(func=cmd_history)

    # skills
    p_skills = subparsers.add_parser("skills", help="Skill dependency health check")
    p_skills.add_argument("--dirs", nargs="+", metavar="DIR", help="Additional skill directories to scan")
    p_skills.add_argument("--skill", help="Check a specific skill by name")
    p_skills.add_argument("--json", metavar="FILE", dest="json_out", help="Export as JSON (use - for stdout)")
    p_skills.add_argument("--verbose", action="store_true", help="Show healthy skills too")
    p_skills.add_argument("--fix-hints", action="store_true", help="Show only install commands for broken skills")
    p_skills.add_argument("--filter", choices=["broken", "healthy"], help="Filter by status")
    p_skills.add_argument("--infer", action="store_true", help="Infer deps from SKILL.md body text")
    p_skills.add_argument("--check-versions", action="store_true", help="Check binary versions against requirements")
    p_skills.set_defaults(func=cmd_skills)

    # watch
    p_watch = subparsers.add_parser("watch", help="Watch sessions and alert on threshold crossings")
    p_watch.add_argument("--dir", **dir_kwargs)
    p_watch.add_argument("--interval", type=int, default=60, help="Check interval in seconds (default: 60)")
    p_watch.set_defaults(func=cmd_watch)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    # Load RC config overrides before running any command
    apply_rc_config()

    args.func(args)


if __name__ == "__main__":
    main()
