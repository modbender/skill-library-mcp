#!/usr/bin/env python3
"""
Solo Leveling System — Player Data Manager
Manages player state: stats, XP, rank, streaks, quests, titles.
Stored as JSON, read/written by the agent.
"""

import json
import sys
import os
from datetime import datetime, timezone, timedelta

# Resolve paths relative to the skill directory
SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.environ.get("SOLO_DATA_DIR", os.path.join(SKILL_DIR, "solo-leveling-data"))
CONFIG_FILE = os.path.join(SKILL_DIR, "references", "config.json")
CONFIG_TEMPLATE = os.path.join(SKILL_DIR, "references", "config-template.json")
PLAYER_FILE = os.path.join(DATA_DIR, "player.json")
QUEST_LOG = os.path.join(DATA_DIR, "quest-log.json")

RANK_TABLE = [
    {"rank": "F", "title": "Unawakened", "min_level": 1, "min_xp": 0},
    {"rank": "E", "title": "Awakened Hunter", "min_level": 6, "min_xp": 500},
    {"rank": "D", "title": "Rising Hunter", "min_level": 16, "min_xp": 2000},
    {"rank": "C", "title": "Proven Hunter", "min_level": 31, "min_xp": 5000},
    {"rank": "B", "title": "Elite Hunter", "min_level": 51, "min_xp": 12000},
    {"rank": "A", "title": "S-Rank Candidate", "min_level": 76, "min_xp": 25000},
    {"rank": "S", "title": "Shadow Monarch", "min_level": 91, "min_xp": 50000},
]

DEFAULT_PLAYER = {
    "name": "Hunter",
    "created": None,
    "timezone": "UTC",
    "stats": {"STR": 10, "INT": 10, "VIT": 5, "AGI": 5, "PER": 5, "CHA": 5},
    "xp": 0,
    "level": 1,
    "rank": "F",
    "rank_title": "Unawakened",
    "streak": 0,
    "best_streak": 0,
    "titles": [],
    "active_dungeon": None,
    "dungeons_completed": [],
    "total_quests_completed": 0,
    "total_quests_failed": 0,
    "honesty_count": 0,
    "lies_caught": 0,
    "last_check_in": None,
    "last_sleep_time": None,
    "last_wake_time": None,
    "quest_counters": {},
}


def get_tz(tz_name="UTC"):
    """Get timezone offset. Supports common timezone names and UTC offsets."""
    tz_offsets = {
        "UTC": 0, "GMT": 0,
        "Asia/Kolkata": 5.5, "IST": 5.5,
        "America/New_York": -5, "EST": -5, "EDT": -4,
        "America/Chicago": -6, "CST": -6, "CDT": -5,
        "America/Denver": -7, "MST": -7, "MDT": -6,
        "America/Los_Angeles": -8, "PST": -8, "PDT": -7,
        "Europe/London": 0, "BST": 1,
        "Europe/Berlin": 1, "CET": 1, "CEST": 2,
        "Europe/Paris": 1,
        "Asia/Tokyo": 9, "JST": 9,
        "Asia/Shanghai": 8,
        "Asia/Dubai": 4,
        "Australia/Sydney": 11, "AEDT": 11, "AEST": 10,
    }
    hours = tz_offsets.get(tz_name, 0)
    return timezone(timedelta(hours=hours))


def load_config():
    """Load config.json if it exists."""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE) as f:
            return json.load(f)
    return None


def ensure_dir():
    os.makedirs(DATA_DIR, exist_ok=True)


def load_player():
    ensure_dir()
    if os.path.exists(PLAYER_FILE):
        with open(PLAYER_FILE) as f:
            return json.load(f)
    return None


def save_player(data):
    ensure_dir()
    with open(PLAYER_FILE, "w") as f:
        json.dump(data, f, indent=2)


def init_player(name=None, config_path=None):
    """Initialize a new player, optionally from a config file."""
    config = None
    if config_path and os.path.exists(config_path):
        with open(config_path) as f:
            config = json.load(f)
    elif os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE) as f:
            config = json.load(f)

    player = DEFAULT_PLAYER.copy()
    player["stats"] = DEFAULT_PLAYER["stats"].copy()
    player["titles"] = []
    player["dungeons_completed"] = []
    player["quest_counters"] = {}

    if config:
        player["name"] = config.get("player_name") or name or "Hunter"
        player["timezone"] = config.get("timezone", "UTC")
    else:
        player["name"] = name or "Hunter"

    tz = get_tz(player["timezone"])
    player["created"] = datetime.now(tz).isoformat()
    save_player(player)
    return player


def calculate_level(xp):
    """Level = 1 + floor(xp / 100), capped at 100."""
    return min(1 + xp // 100, 100)


def calculate_rank(level):
    """Return rank info based on level."""
    current = RANK_TABLE[0]
    for r in RANK_TABLE:
        if level >= r["min_level"]:
            current = r
    return current


def add_xp(player, amount, stat=None, stat_amount=0):
    """Add XP and optional stat points. Returns updated player."""
    player["xp"] = max(0, player["xp"] + amount)
    old_level = player["level"]
    player["level"] = calculate_level(player["xp"])
    rank_info = calculate_rank(player["level"])
    player["rank"] = rank_info["rank"]
    player["rank_title"] = rank_info["title"]
    if stat and stat in player["stats"]:
        player["stats"][stat] = max(0, player["stats"][stat] + stat_amount)
    save_player(player)
    return player, player["level"] > old_level


def load_quest_log():
    ensure_dir()
    if os.path.exists(QUEST_LOG):
        with open(QUEST_LOG) as f:
            return json.load(f)
    return {"days": {}}


def save_quest_log(log):
    ensure_dir()
    with open(QUEST_LOG, "w") as f:
        json.dump(log, f, indent=2)


def log_quest(date_str, quest_name, status, xp_earned, proof=None, notes=None, tz_name="UTC"):
    """Log a quest completion/failure for a given date."""
    log = load_quest_log()
    if date_str not in log["days"]:
        log["days"][date_str] = {"quests": [], "total_xp": 0}
    tz = get_tz(tz_name)
    log["days"][date_str]["quests"].append({
        "quest": quest_name,
        "status": status,
        "xp": xp_earned,
        "proof": proof,
        "notes": notes,
        "timestamp": datetime.now(tz).isoformat(),
    })
    log["days"][date_str]["total_xp"] += xp_earned
    save_quest_log(log)
    return log


def get_stat_bar(value, max_val=100, width=10):
    """Generate a visual stat bar."""
    filled = min(int((value / max_val) * width), width)
    return "█" * filled + "░" * (width - filled)


def format_status_card(player):
    """Generate the Hunter Status card."""
    next_rank = None
    for r in RANK_TABLE:
        if r["min_xp"] > player["xp"]:
            next_rank = r
            break
    next_xp = next_rank["min_xp"] if next_rank else "MAX"

    lines = [
        "📋 HUNTER STATUS",
        "",
        f"Player: {player['name']}",
        f"Rank: {player['rank']}-Rank | Level: {player['level']}",
        f"Title: {player['rank_title']}",
        f"Total XP: {player['xp']} / {next_xp}",
        "",
        "━━━ STATS ━━━",
    ]
    for stat, val in player["stats"].items():
        bar = get_stat_bar(val)
        lines.append(f"{stat} {bar} {val}")
    lines.extend([
        "",
        f"🔥 Streak: {player['streak']} days (Best: {player['best_streak']})",
        f"🏆 Titles: {', '.join(player['titles']) if player['titles'] else 'None yet'}",
        f"⚔️ Active Dungeon: {player['active_dungeon'] or 'None'}",
        "",
        f"📊 Quests: {player['total_quests_completed']} completed / {player['total_quests_failed']} failed",
    ])

    # Show quest counters if any
    counters = player.get("quest_counters", {})
    if counters:
        for label, count in counters.items():
            lines.append(f"  {label}: {count}")

    return "\n".join(lines)


def reset_player():
    """Archive current data and start fresh."""
    ensure_dir()
    now = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    archive_dir = os.path.join(DATA_DIR, "archive")
    os.makedirs(archive_dir, exist_ok=True)

    for fname in ["player.json", "quest-log.json"]:
        src = os.path.join(DATA_DIR, fname)
        if os.path.exists(src):
            dst = os.path.join(archive_dir, f"{now}_{fname}")
            os.rename(src, dst)
            print(f"Archived {fname} → archive/{now}_{fname}")

    print("Player data reset. Run 'init' to create a new player.")


def show_config():
    """Show current config summary."""
    config = load_config()
    if not config:
        print("No config found at references/config.json")
        print("Run onboarding or copy from references/config-template.json")
        return
    print(f"Player: {config.get('player_name', '(not set)')}")
    print(f"Timezone: {config.get('timezone', 'UTC')}")
    print(f"\nDaily quests ({len(config.get('quests', {}).get('daily', []))}):")
    for q in config.get("quests", {}).get("daily", []):
        print(f"  {q.get('icon', '▸')} {q['name']} [{q['stat']} +{q['stat_amount']}]")
    weekend = config.get("quests", {}).get("weekend_bonus", [])
    if weekend:
        print(f"\nWeekend bonus ({len(weekend)}):")
        for q in weekend:
            print(f"  {q.get('icon', '▸')} {q['name']} [{q['stat']} +{q['stat_amount']}]")
    print(f"\nSchedule:")
    print(f"  Morning quests: {config.get('morning_quest_time', '06:30')}")
    print(f"  Evening report: {config.get('evening_report_time', '22:00')}")
    print(f"  Sleep check: {config.get('sleep_check_time', '23:30')}")
    print(f"  Sleep curfew: {config.get('sleep_curfew', '23:00')}")
    print(f"  Wake target: {config.get('wake_target', '07:00')}")
    print(f"  Weekly review: {config.get('weekly_review_day', 'sunday')} {config.get('weekly_review_time', '10:00')}")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"

    if cmd == "init":
        # Support --config flag
        config_path = None
        name = None
        args = sys.argv[2:]
        i = 0
        while i < len(args):
            if args[i] == "--config" and i + 1 < len(args):
                config_path = args[i + 1]
                i += 2
            else:
                name = args[i]
                i += 1

        p = init_player(name=name, config_path=config_path)
        print(f"Player '{p['name']}' initialized. Welcome, Hunter.")
        print(format_status_card(p))

    elif cmd == "status":
        p = load_player()
        if not p:
            print("No player found. Run: python3 player_data.py init")
            sys.exit(1)
        print(format_status_card(p))

    elif cmd == "add_xp":
        p = load_player()
        if not p:
            print("No player found.")
            sys.exit(1)
        amount = int(sys.argv[2])
        stat = sys.argv[3] if len(sys.argv) > 3 else None
        stat_amt = int(sys.argv[4]) if len(sys.argv) > 4 else 0
        p, leveled = add_xp(p, amount, stat, stat_amt)
        print(f"Added {amount} XP." + (" LEVEL UP!" if leveled else ""))
        print(f"Level: {p['level']} | Rank: {p['rank']}")

    elif cmd == "json":
        p = load_player()
        print(json.dumps(p, indent=2))

    elif cmd == "reset":
        confirm = input("Reset all player data? This archives current data. (yes/no): ") if sys.stdin.isatty() else "yes"
        if confirm.lower() in ("yes", "y"):
            reset_player()
        else:
            print("Reset cancelled.")

    elif cmd == "config":
        show_config()

    else:
        print(f"Unknown command: {cmd}")
        print("Usage: player_data.py [init|status|add_xp|json|reset|config]")
        print("  init [name] [--config path]  Initialize player")
        print("  status                       Show hunter status card")
        print("  add_xp <amount> [stat] [amt] Add XP and optional stat")
        print("  json                         Dump player as JSON")
        print("  reset                        Archive data and start fresh")
        print("  config                       Show current config")
