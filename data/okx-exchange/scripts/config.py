"""OKX Exchange Skill — Unified configuration, state, and journal management"""
import json
import os

MEMORY_DIR = os.path.expanduser("~/.openclaw/workspace/memory")
PREFS_PATH = os.path.join(MEMORY_DIR, "okx-trading-preferences.json")
STATE_PATH = os.path.join(MEMORY_DIR, "okx-trading-state.json")
JOURNAL_PATH = os.path.join(MEMORY_DIR, "okx-trading-journal.json")

# Merged defaults from execute.py and monitor.py
DEFAULT_PREFS: dict = {
    # Order safety
    "max_order_usd": 100,
    "max_leverage": 10,
    "price_impact_warn": 0.005,
    "price_impact_abort": 0.01,
    "require_confirm": True,
    # Position management
    "stop_loss_pct": 5.0,
    "take_profit_pct": 10.0,
    "auto_trade": False,
    "max_position_usd": 100,
    "max_daily_trades": 10,
    # Strategy
    "strategies": ["trend"],
    "watchlist": ["BTC-USDT-SWAP", "ETH-USDT-SWAP"],
    "default_sz": "0.01",
}


def load_prefs() -> dict:
    """Load user preferences, merged over defaults so new keys are always present."""
    if os.path.exists(PREFS_PATH):
        with open(PREFS_PATH) as f:
            data = json.load(f)
        return {**DEFAULT_PREFS, **data}
    return dict(DEFAULT_PREFS)


def save_prefs(prefs: dict) -> None:
    os.makedirs(MEMORY_DIR, exist_ok=True)
    with open(PREFS_PATH, "w") as f:
        json.dump(prefs, f, indent=2)


def load_state() -> dict:
    if os.path.exists(STATE_PATH):
        with open(STATE_PATH) as f:
            return json.load(f)
    return {"last_scan": None, "daily_trades": 0, "last_reset": None}


def save_state(state: dict) -> None:
    os.makedirs(MEMORY_DIR, exist_ok=True)
    with open(STATE_PATH, "w") as f:
        json.dump(state, f, indent=2)


def log_trade(entry: dict) -> None:
    os.makedirs(MEMORY_DIR, exist_ok=True)
    journal: dict = {"trades": []}
    if os.path.exists(JOURNAL_PATH):
        with open(JOURNAL_PATH) as f:
            journal = json.load(f)
    journal["trades"].append(entry)
    with open(JOURNAL_PATH, "w") as f:
        json.dump(journal, f, indent=2)


def grid_state_path(inst_id: str) -> str:
    """Return path for the grid state file of a given instrument."""
    return os.path.join(MEMORY_DIR, f"okx-grid-{inst_id.replace('/', '-')}.json")


SNAPSHOTS_PATH = os.path.join(MEMORY_DIR, "okx-monitor-snapshots.json")
_MAX_SNAPSHOTS = 48  # keep last 48 entries


def load_snapshots() -> dict:
    """Load persisted monitor snapshots."""
    if os.path.exists(SNAPSHOTS_PATH):
        with open(SNAPSHOTS_PATH) as f:
            return json.load(f)
    return {"initial_equity": None, "snapshots": []}


def save_snapshot(snapshot: dict) -> None:
    """Append a snapshot and persist. Sets initial_equity on first write."""
    os.makedirs(MEMORY_DIR, exist_ok=True)
    data = load_snapshots()
    if data["initial_equity"] is None:
        data["initial_equity"] = snapshot.get("equity_usd")
    data["snapshots"].append(snapshot)
    data["snapshots"] = data["snapshots"][-_MAX_SNAPSHOTS:]
    with open(SNAPSHOTS_PATH, "w") as f:
        json.dump(data, f, indent=2)
