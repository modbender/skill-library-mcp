#!/usr/bin/env python3
"""
Rate Limiter — Self-Throttling for AI Agents

Tracks usage within a rolling window and returns tier-based recommendations.
Works with Claude Max, OpenAI ChatGPT Plus/Pro, or any custom rate limit.

Commands:
  gate                  Check tier (exit 0=ok/cautious, 1=throttled, 2=critical/paused)
  record [tokens]       Log a request with optional token count
  status                Full status JSON
  pause [minutes]       Enter paused state (auto exponential backoff if no minutes)
  resume                Clear pause, reset backoff
  set-limit <n>         Override estimated request limit per window
  reset                 Reset all state

Environment variables (all optional):
  RATE_LIMIT_PROVIDER   claude | openai | custom (default: claude)
  RATE_LIMIT_PLAN       max-5x | max-20x | plus | pro | custom (default: max-5x)
  RATE_LIMIT_STATE      Path to state file (default: ./rate-limit-state.json)
  RATE_LIMIT_WINDOW_HOURS  Rolling window in hours (default: from preset)
  RATE_LIMIT_ESTIMATE   Estimated request limit per window (default: from preset)

Built by The Agent Wire — https://theagentwire.ai
"""

import json
import sys
import os
import fcntl
import random
from contextlib import contextmanager
from datetime import datetime, timezone, timedelta
from pathlib import Path

# --- Provider Presets ---

PRESETS = {
    ("claude", "max-5x"):  {"window_hours": 5, "limit": 200},
    ("claude", "max-20x"): {"window_hours": 5, "limit": 540},
    ("openai", "plus"):    {"window_hours": 3, "limit": 80},
    ("openai", "pro"):     {"window_hours": 3, "limit": 200},
}

# --- Config ---

PROVIDER = os.environ.get("RATE_LIMIT_PROVIDER", "claude").lower()
PLAN = os.environ.get("RATE_LIMIT_PLAN", "max-5x").lower()

preset = PRESETS.get((PROVIDER, PLAN), {"window_hours": 5, "limit": 200})

WINDOW_HOURS = float(os.environ.get("RATE_LIMIT_WINDOW_HOURS", preset["window_hours"]))
WINDOW_MS = int(WINDOW_HOURS * 3_600_000)
DEFAULT_LIMIT = int(os.environ.get("RATE_LIMIT_ESTIMATE", preset["limit"]))


def _validate_state_path(raw_path):
    """Validate and resolve state file path."""
    resolved = Path(raw_path).resolve()
    if not str(resolved).endswith(".json"):
        print(f"Error: RATE_LIMIT_STATE must end with .json, got: {resolved}", file=sys.stderr)
        sys.exit(1)
    # Check for .. after resolution (shouldn't survive resolve(), but belt-and-suspenders)
    if ".." in resolved.parts:
        print(f"Error: RATE_LIMIT_STATE contains '..' components: {resolved}", file=sys.stderr)
        sys.exit(1)
    return resolved


STATE_PATH = _validate_state_path(os.environ.get(
    "RATE_LIMIT_STATE",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "rate-limit-state.json")
))

# --- Tier Thresholds ---

TIERS = [
    (98, "critical"),
    (95, "throttled"),
    (90, "cautious"),
    (0,  "ok"),
]


# --- File Locking ---

@contextmanager
def locked_file(path, mode="r"):
    """Context manager that acquires an exclusive flock on a file."""
    lock_path = str(path) + ".lock"
    fd = os.open(lock_path, os.O_CREAT | os.O_RDWR, 0o600)
    lock_file = os.fdopen(fd, "r+")
    try:
        fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)
        yield
    finally:
        fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)
        lock_file.close()


# --- Datetime Helper ---

def parse_iso_datetime(s):
    """Parse ISO datetime string, handling Z suffix and various formats."""
    if s is None:
        return None
    try:
        # Try direct parse first (Python 3.11+ handles Z)
        return datetime.fromisoformat(s)
    except ValueError:
        pass
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00"))
    except (ValueError, AttributeError) as e:
        print(f"Warning: failed to parse datetime '{s}': {e}", file=sys.stderr)
        return None


# --- State Management ---

def default_state():
    return {
        "provider": PROVIDER,
        "plan": PLAN,
        "tier": "ok",
        "estimatedPct": 0,
        "lastUpdated": None,
        "pausedUntil": None,
        "window": {
            "durationMs": WINDOW_MS,
            "requests": [],
            "estimatedLimit": DEFAULT_LIMIT,
        },
        "backoff": {
            "consecutive429s": 0,
            "lastBackoffMs": 0,
        },
    }


def _validate_state_types(state):
    """Validate state field types, warn and fix any corrupted fields."""
    defaults = default_state()
    window = state.get("window", {})

    # Validate requests is a list
    if not isinstance(window.get("requests"), list):
        print(f"Warning: state 'requests' is not a list (got {type(window.get('requests')).__name__}), resetting to []", file=sys.stderr)
        window["requests"] = []

    # Validate estimatedLimit is a positive number
    limit = window.get("estimatedLimit")
    if not isinstance(limit, (int, float)) or limit <= 0:
        print(f"Warning: state 'estimatedLimit' invalid (got {limit!r}), resetting to {DEFAULT_LIMIT}", file=sys.stderr)
        window["estimatedLimit"] = DEFAULT_LIMIT

    # Validate backoff fields
    backoff = state.get("backoff", {})
    if not isinstance(backoff.get("consecutive429s"), (int, float)) or backoff["consecutive429s"] < 0:
        print(f"Warning: state 'consecutive429s' invalid, resetting to 0", file=sys.stderr)
        backoff["consecutive429s"] = 0
    if not isinstance(backoff.get("lastBackoffMs"), (int, float)) or backoff["lastBackoffMs"] < 0:
        backoff["lastBackoffMs"] = 0

    state["window"] = window
    state["backoff"] = backoff


def load_state():
    if STATE_PATH.exists():
        try:
            raw = STATE_PATH.read_text()
            state = json.loads(raw)
            if not isinstance(state, dict):
                print(f"Warning: state file is not a JSON object, using defaults", file=sys.stderr)
                return default_state()
            # Ensure all keys exist (migration-safe)
            defaults = default_state()
            for key in defaults:
                if key not in state:
                    state[key] = defaults[key]
            for key in defaults["window"]:
                if key not in state.get("window", {}):
                    state.setdefault("window", {})[key] = defaults["window"][key]
            for key in defaults["backoff"]:
                if key not in state.get("backoff", {}):
                    state.setdefault("backoff", {})[key] = defaults["backoff"][key]
            _validate_state_types(state)
            return state
        except json.JSONDecodeError as e:
            print(f"Warning: corrupted state file ({e}), using defaults", file=sys.stderr)
        except PermissionError as e:
            print(f"Warning: cannot read state file ({e}), using defaults", file=sys.stderr)
        except OSError as e:
            print(f"Warning: error reading state file ({e}), using defaults", file=sys.stderr)
    return default_state()


def save_state(state):
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    tmp = STATE_PATH.with_suffix(".tmp")
    # Write with restricted permissions (0o600)
    fd = os.open(str(tmp), os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w") as f:
        f.write(json.dumps(state, indent=2) + "\n")
    tmp.rename(STATE_PATH)


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def now_ms():
    return int(datetime.now(timezone.utc).timestamp() * 1000)


# --- Core Logic ---

def prune_requests(state):
    current = now_ms()
    cutoff = current - state["window"]["durationMs"]
    state["window"]["requests"] = [
        r for r in state["window"]["requests"]
        if r["ts"] > cutoff and r["ts"] <= current  # exclude future timestamps (clock skew)
    ]


def calculate_pct(state):
    count = len(state["window"]["requests"])
    limit = state["window"].get("estimatedLimit", DEFAULT_LIMIT)
    if limit <= 0:
        return 0  # Don't falsely trigger critical tier
    return min(round(count / limit * 100), 100)


def determine_tier(pct):
    for threshold, tier in TIERS:
        if pct >= threshold:
            return tier
    return "ok"


def check_pause_expired(state):
    pu = state.get("pausedUntil")
    if pu:
        pause_dt = parse_iso_datetime(pu)
        if pause_dt is None:
            # Unparseable, clear it
            state["pausedUntil"] = None
        elif pause_dt <= datetime.now(timezone.utc):
            state["pausedUntil"] = None
            state["tier"] = "cautious"
            state["backoff"]["consecutive429s"] = 0
            state["backoff"]["lastBackoffMs"] = 0


def update_tier(state):
    prune_requests(state)
    check_pause_expired(state)

    if state.get("pausedUntil"):
        state["tier"] = "paused"
    else:
        pct = calculate_pct(state)
        state["estimatedPct"] = pct
        state["tier"] = determine_tier(pct)

    state["lastUpdated"] = now_iso()


# --- Input Validation ---

def validate_non_negative_int(value, name):
    """Validate value is a non-negative integer. Exit 1 on failure."""
    try:
        n = int(value)
        if n < 0:
            raise ValueError("must be non-negative")
        return n
    except (ValueError, TypeError):
        print(f"Error: {name} must be a non-negative integer, got: {value!r}", file=sys.stderr)
        sys.exit(1)


def validate_positive_int(value, name):
    """Validate value is a positive integer. Exit 1 on failure."""
    try:
        n = int(value)
        if n <= 0:
            raise ValueError("must be positive")
        return n
    except (ValueError, TypeError):
        print(f"Error: {name} must be a positive integer, got: {value!r}", file=sys.stderr)
        sys.exit(1)


def validate_positive_number(value, name):
    """Validate value is a positive number. Exit 1 on failure."""
    try:
        n = float(value)
        if n <= 0:
            raise ValueError("must be positive")
        return n
    except (ValueError, TypeError):
        print(f"Error: {name} must be a positive number, got: {value!r}", file=sys.stderr)
        sys.exit(1)


# --- Commands ---

def cmd_gate():
    with locked_file(STATE_PATH):
        state = load_state()
        update_tier(state)
        save_state(state)

    tier = state["tier"]
    paused = state.get("pausedUntil") is not None

    print(json.dumps({
        "tier": tier,
        "pct": state["estimatedPct"],
        "paused": paused,
        "provider": state.get("provider", PROVIDER),
        "plan": state.get("plan", PLAN),
    }))

    if tier in ("ok", "cautious"):
        sys.exit(0)
    elif tier == "throttled":
        sys.exit(1)
    else:  # critical, paused
        sys.exit(2)


def cmd_record(tokens=0):
    tokens = validate_non_negative_int(tokens, "tokens")
    with locked_file(STATE_PATH):
        state = load_state()
        state["window"]["requests"].append({
            "ts": now_ms(),
            "tokens": tokens,
        })
        update_tier(state)
        save_state(state)
    print(json.dumps({
        "tier": state["tier"],
        "pct": state["estimatedPct"],
        "requests": len(state["window"]["requests"]),
    }))


def cmd_status():
    with locked_file(STATE_PATH):
        state = load_state()
        update_tier(state)
        save_state(state)
    reqs = len(state["window"]["requests"])
    limit = state["window"].get("estimatedLimit", DEFAULT_LIMIT)
    total_tokens = sum(r.get("tokens", 0) for r in state["window"]["requests"])

    print(json.dumps({
        "provider": state.get("provider", PROVIDER),
        "plan": state.get("plan", PLAN),
        "tier": state["tier"],
        "pct": state["estimatedPct"],
        "requests": reqs,
        "limit": limit,
        "totalTokens": total_tokens,
        "windowHours": state["window"]["durationMs"] / 3_600_000,
        "pausedUntil": state.get("pausedUntil"),
        "consecutive429s": state["backoff"]["consecutive429s"],
        "lastUpdated": state.get("lastUpdated"),
    }, indent=2))


def cmd_pause(minutes=None):
    if minutes is not None:
        minutes = validate_positive_number(minutes, "minutes")
    with locked_file(STATE_PATH):
        state = load_state()
        if minutes is None:
            base_min = random.uniform(3, 8)
            consecutive = state["backoff"]["consecutive429s"]
            multiplier = 1.5 ** consecutive
            wait_min = min(base_min * multiplier, 30)
            state["backoff"]["consecutive429s"] = consecutive + 1
            state["backoff"]["lastBackoffMs"] = int(wait_min * 60 * 1000)
        else:
            wait_min = minutes
            state["backoff"]["consecutive429s"] += 1
            state["backoff"]["lastBackoffMs"] = int(wait_min * 60 * 1000)

        resume_at = datetime.now(timezone.utc) + timedelta(minutes=wait_min)
        state["pausedUntil"] = resume_at.isoformat()
        state["tier"] = "paused"
        state["lastUpdated"] = now_iso()
        save_state(state)
    print(json.dumps({
        "tier": "paused",
        "pausedUntil": state["pausedUntil"],
        "waitMinutes": round(wait_min, 1),
        "consecutive429s": state["backoff"]["consecutive429s"],
    }, indent=2))


def cmd_resume():
    with locked_file(STATE_PATH):
        state = load_state()
        state["pausedUntil"] = None
        state["backoff"]["consecutive429s"] = 0
        state["backoff"]["lastBackoffMs"] = 0
        update_tier(state)
        save_state(state)
    print(json.dumps({"tier": state["tier"], "pct": state["estimatedPct"]}))


def cmd_set_limit(n):
    n = validate_positive_int(n, "limit")
    with locked_file(STATE_PATH):
        state = load_state()
        state["window"]["estimatedLimit"] = n
        update_tier(state)
        save_state(state)
    print(json.dumps({"limit": n, "tier": state["tier"], "pct": state["estimatedPct"]}))


def cmd_reset():
    with locked_file(STATE_PATH):
        state = default_state()
        save_state(state)
    print(json.dumps({"status": "reset", "tier": "ok", "provider": PROVIDER, "plan": PLAN}))


# --- Main ---

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    cmd = sys.argv[1]
    args = sys.argv[2:]

    commands = {
        "gate": cmd_gate,
        "record": lambda: cmd_record(args[0] if args else 0),
        "status": cmd_status,
        "pause": lambda: cmd_pause(args[0] if args else None),
        "resume": cmd_resume,
        "set-limit": lambda: cmd_set_limit(args[0] if len(args) > 0 else None),
        "reset": cmd_reset,
    }

    if cmd in commands:
        commands[cmd]()
    else:
        print(f"Unknown command: {cmd}")
        print(__doc__)
        sys.exit(1)
