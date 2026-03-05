#!/usr/bin/env python3
"""Water tracking core utilities - EXECUTED, not interpreted."""
import json, csv, os, re
from datetime import date, datetime
from pathlib import Path

# ============================================================================
# FLEXIBLE PATHS
# Priority: env var > relative to this file > sensible default
# ============================================================================

SCRIPT_DIR = Path(__file__).parent.resolve()  # .../water-coach/scripts
WORKSPACE_DIR = Path(os.environ.get("PWD", "/home/oriel/.openclaw/workspace"))

# Skill directory: SCRIPT_DIR parent = .../water-coach
SKILL_DIR = SCRIPT_DIR.parent

# Data directory: Use memory/data (outside skill folder)
# This keeps user data separate from skill code
DATA_DIR = WORKSPACE_DIR / "memory" / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

CONFIG_FILE = DATA_DIR / "water_config.json"
LOG_FILE = DATA_DIR / "water_log.csv"

# Session directory: /home/oriel/.openclaw/agents/main/sessions
# Derived from workspace: workspace/.openclaw/agents → workspace.parent/.openclaw/agents
OPENCLAW_BASE = WORKSPACE_DIR.parent  # /home/oriel/.openclaw
AGENTS_DIR = OPENCLAW_BASE / "agents"
SESSION_DIR = AGENTS_DIR / "main" / "sessions"


# ============================================================================
# HELPERS
# ============================================================================

import random
import string

def generate_entry_id(length: int = 6) -> str:
    """Generate a short unique ID for water entries.
    
    Args:
        length: Length of the ID (default 6)
    
    Returns:
        Short unique ID string
    """
    chars = string.ascii_lowercase + string.digits
    return ''.join(random.choices(chars, k=length))

def get_current_message_id() -> str:
    """Get the current user message ID from session transcript for audit trail.
    
    Searches recursively through recent sessions if no user message found in latest.
    Returns message_id from the most recent user message.
    
    Returns:
        Message ID string or empty string if not found
    """
    if not SESSION_DIR.exists():
        return ""
    
    try:
        # Find session files sorted by modification time (newest first)
        files = [f for f in SESSION_DIR.iterdir() if f.suffix == '.jsonl' and not f.name.endswith('.lock')]
        if not files:
            return ""
        
        # Sort by modification time (newest first)
        files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
        
        # Search through recent sessions (newest first)
        for session_file in files[:5]:  # Check up to 5 most recent sessions
            try:
                with open(session_file) as f:
                    lines = f.readlines()
                
                # Search from end (most recent) to start
                for line in reversed(lines):
                    d = json.loads(line)
                    if d.get('type') == 'message' and d.get('message', {}).get('role') == 'user':
                        msg_id = d.get('id', '')
                        if msg_id:
                            return msg_id
            except Exception:
                continue
        
        return ""
    except Exception:
        return ""


# ============================================================================
# CONFIGURATION
# ============================================================================

# Unit conversions (for config/tools only - NOT for user input parsing)
KG_TO_LB = 2.20462
LB_TO_KG = 0.453592
ML_TO_OZ = 0.033814
OZ_TO_ML = 29.5735

# ============================================================================
# CONFIGURATION FUNCTIONS
# ============================================================================

def load_config():
    """Load config or create default."""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE) as f:
            return json.load(f)
    return create_default_config()

def is_user_setup() -> dict:
    """Check if user has completed first-time setup.
    
    Returns:
        Dict with setup status and details
    """
    config = load_config()
    weight = config.get("user", {}).get("weight_kg")
    manual_goal = config.get("settings", {}).get("default_goal_ml")
    
    # Calculate goal: manual goal OR weight-based OR default
    calculated_goal = get_daily_goal()
    
    # User is set up if they have any goal (manual OR from weight OR default)
    is_setup = calculated_goal is not None and calculated_goal > 0
    
    return {
        "is_setup": is_setup,
        "weight_kg": weight,
        "goal_ml": calculated_goal,
        "has_manual_goal": manual_goal is not None and manual_goal > 0,
        "config_exists": CONFIG_FILE.exists()
    }

def create_default_config():
    """Create default configuration."""
    return {
        "version": "3.0",
        "units": {"system": "metric", "weight": "kg", "height": "m", "volume": "ml"},
        "user": {"weight_kg": None, "height_m": None, "body_fat_pct": None, "muscle_pct": None, "water_pct": None},
        "settings": {
            "goal_multiplier": 35,
            "default_goal_ml": None,
            "cutoff_hour": 22,
            "audit_auto_capture": False,
            "reminder_slots": [
                {"name": "morning", "hour": 9},
                {"name": "lunch", "hour": 12},
                {"name": "afternoon", "hour": 15},
                {"name": "predinner", "hour": 18},
                {"name": "evening", "hour": 21}
            ]
        },
        "dynamic_scheduling": {
            "enabled": True,
            "formula": {
                "type": "linear_time_based",
                "margin_percent": 25,
                "start_hour": 9,
                "cutoff_hour": 22
            },
            "extra_notifications": {
                "max_per_day": 4,
                "interval_minutes": 30,
                "reduce_if_catching_up": True,
                "healthy_threshold_percent": 80
            }
        },
        "status": {
            "snoozed_until": None,
            "skip_dates": [],
            "extra_notifications_today": 0,
            "last_extra_notification": None
        },
        "reports": {"weekly_enabled": False, "monthly_enabled": False}
    }

def save_config(config):
    """Save config to file."""
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)

def update_user_weight(weight_kg: float, update_goal: bool = False):
    """Update user's weight.
    
    Args:
        weight_kg: New weight
        update_goal: If True, recalculate goal from weight × 35
    
    Note: Goal is USER'S CHOICE. The agent should ask:
    - At setup: "Your suggested goal is X ml. Is that OK?"
    - On weight update: "Want to update your goal to the new suggested amount?"
    """
    config = load_config()
    old_weight = config.get("user", {}).get("weight_kg")
    config["user"]["weight_kg"] = weight_kg
    
    # Log to body_metrics.csv
    log_body_metrics(weight_kg=weight_kg)
    
    # Calculate suggested goal
    suggested_goal = int(weight_kg * 35)
    current_goal = config.get("settings", {}).get("default_goal_ml")
    
    response = {
        "weight_kg": weight_kg,
        "old_weight": old_weight,
        "suggested_goal_ml": suggested_goal,
        "current_goal_ml": current_goal,
        "goal_updated": False,
        "body_metrics_logged": True,
        "message": "Weight updated. Goal unchanged unless you confirm update."
    }
    
    # If user confirms, update goal
    if update_goal:
        config["settings"]["default_goal_ml"] = suggested_goal
        response["goal_updated"] = True
        response["message"] = f"Weight {weight_kg}kg → Goal updated to {suggested_goal}ml"
    
    save_config(config)
    return response

# ============================================================================
# GOAL & DATE FUNCTIONS
# ============================================================================

def get_daily_goal():
    """Calculate goal: weight_kg × 35ml."""
    config = load_config()
    if config.get("settings", {}).get("default_goal_ml"):
        return config["settings"]["default_goal_ml"]
    weight = config.get("user", {}).get("weight_kg", 95)
    multiplier = config.get("settings", {}).get("goal_multiplier", 35)
    return weight * multiplier if weight else 3325

def get_today_date():
    """Get today's date as YYYY-MM-DD."""
    return date.today().strftime("%Y-%m-%d")

# ============================================================================
# CORE: STATUS & LOGGING (DETERMINISTIC - NO LLM INTERPRETATION)
# ============================================================================

def get_today_status():
    """Get today's water intake status.
    
    IMPORTANT: Uses drank_at to determine which day the water belongs to.
    Calculates cumulative at query time by SUMming ml_drank.
    
    Returns dict with:
    - current_ml: Total ml logged today (SUM of ml_drank WHERE drank_at date = today)
    - goal_ml: Daily goal
    - percentage: Progress percentage
    - remaining_ml: ml left to reach goal
    - is_under_goal: Boolean
    - is_under_threshold: Based on dynamic formula
    - last_entry_time: When user last logged (logged_at)
    """
    goal = get_daily_goal()
    today = get_today_date()
    entries = []
    current_ml = 0
    last_logged_at = None
    
    if LOG_FILE.exists():
        with open(LOG_FILE) as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Use drank_at to determine the day
                drank_at = row.get("drank_at", "")
                entry_date = drank_at[:10] if drank_at else row.get("date", "")[:10]
                
                if entry_date == today:
                    entries.append(row)
                    current_ml += int(row.get("ml_drank", 0))
                    last_logged_at = row.get("logged_at")
    
    percentage = (current_ml / goal * 100) if goal > 0 else 0
    
    # Check if under dynamic threshold
    threshold_info = get_dynamic_threshold()
    
    return {
        "current_ml": current_ml,
        "goal_ml": goal,
        "percentage": round(percentage, 1),
        "remaining_ml": max(0, goal - current_ml),
        "is_under_goal": current_ml < goal,
        "is_under_threshold": percentage < threshold_info["threshold"],
        "last_entry_time": last_logged_at,
        "entries": entries
    }

def remove_entry_by_id(entry_id: str) -> dict:
    """Remove a water entry by its unique entry_id.
    
    Args:
        entry_id: The unique entry ID to remove
    
    Returns:
        Dict with success status and removed entry
    """
    if not LOG_FILE.exists():
        return {"error": "Log file not found", "success": False}
    
    with open(LOG_FILE) as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    # Find entry with matching entry_id
    for i, row in enumerate(rows):
        if row.get("entry_id") == entry_id:
            removed = rows.pop(i)
            with open(LOG_FILE, "w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=["entry_id", "logged_at", "drank_at", "date", "slot", "ml_drank", "goal_at_time", "message_id"])
                writer.writeheader()
                writer.writerows(rows)
            return {"success": True, "removed": removed, "remaining_entries": len(rows)}
    
    return {"error": f"Entry not found: {entry_id}", "success": False}

def log_water(amount_ml: int, slot: str = "manual", drank_at: str = None, message_id: str = None) -> dict:
    """Log water intake.
    
    IMPORTANT: 
    - Uses drank_at to determine which day the water counts toward
    - Uses logged_at to track when the entry was recorded
    - Calculates cumulative at query time (not stored)
    
    Args:
        amount_ml: Integer of ml to log (LLM converts "2 glasses" → 500)
        slot: Optional slot name for tracking
        drank_at: When user drank (ISO timestamp). If None, uses logged_at
        message_id: For audit trail - link to conversation message. If None, auto-fetches from session.
    
    Returns:
        Updated status dict
    """
    # Auto-populate message_id if not provided
    if message_id is None or message_id == "":
        message_id = get_current_message_id()
    
    if amount_ml <= 0:
        return {"error": "Amount must be positive", "current_status": get_today_status()}
    
    now = datetime.now().isoformat() + "Z"
    
    # drank_at is mandatory - if not provided, assume equal to logged_at
    if drank_at is None:
        drank_at = now
    
    # Extract date from drank_at
    drank_date = drank_at[:10]
    
    # Get goal at that time (use current goal for now - could be historical later)
    goal = get_daily_goal()
    
    # Generate unique entry ID
    entry_id = generate_entry_id()
    
    # Append to CSV with new format
    file_exists = LOG_FILE.exists()
    with open(LOG_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["entry_id", "logged_at", "drank_at", "date", "slot", "ml_drank", "goal_at_time", "message_id"])
        writer.writerow([entry_id, now, drank_at, drank_date, slot, amount_ml, goal, message_id])
    
    return get_today_status()

def get_entry_by_message_id(message_id: str) -> dict:
    """Get water entry by message_id for audit trail.
    
    Args:
        message_id: The message ID from conversation
    
    Returns:
        Entry dict or None if not found
    """
    if not message_id or not LOG_FILE.exists():
        return None
    
    with open(LOG_FILE) as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("message_id") == message_id:
                return row
    
    return None

def get_message_context(message_id: str, context_lines: int = 2) -> dict:
    """Get message context from session transcript for audit trail.
    
    Args:
        message_id: The message ID to look up
        context_lines: Number of messages before/after to include
    
    Returns:
        Dict with message and context, or None if not found
    """
    if not message_id or not SESSION_DIR.exists():
        return None
    
    try:
        # Find most recent session
        files = [f for f in SESSION_DIR.iterdir() if f.suffix == '.jsonl' and not f.name.endswith('.lock')]
        if not files:
            return None
        
        latest_session = max(files, key=lambda f: f.stat().st_mtime)
        
        # Read all messages
        with open(latest_session) as f:
            lines = f.readlines()
        
        # Find the message and its position
        messages = []
        for line in lines:
            d = json.loads(line)
            if d.get('type') == 'message':
                msg = d.get('message', {})
                messages.append({
                    'id': d.get('id'),
                    'role': msg.get('role'),
                    'timestamp': msg.get('timestamp'),
                    'content': msg.get('content', [])
                })
        
        # Find target message index
        target_idx = None
        for i, m in enumerate(messages):
            if m['id'] == message_id:
                target_idx = i
                break
        
        if target_idx is None:
            return None
        
        # Get context (before and after)
        start_idx = max(0, target_idx - context_lines)
        end_idx = min(len(messages), target_idx + context_lines + 1)
        
        context_messages = []
        for m in messages[start_idx:end_idx]:
            # Extract text content
            text = ''
            for c in m['content']:
                if c.get('type') == 'text':
                    text += c.get('text', '')
            
            context_messages.append({
                'id': m['id'],
                'role': m['role'],
                'timestamp': m['timestamp'],
                'text': text[:500]  # Limit text length
            })
        
        # Extract target message text
        target_text = ''
        for c in messages[target_idx]['content']:
            if c.get('type') == 'text':
                target_text += c.get('text', '')
        
        return {
            'found': True,
            'message_id': message_id,
            'target_message': {
                'id': messages[target_idx]['id'],
                'role': messages[target_idx]['role'],
                'timestamp': messages[target_idx]['timestamp'],
                'text': target_text[:500]
            },
            'context': context_messages
        }
        
    except Exception as e:
        return {"error": str(e)}


def get_entries_by_date(date: str) -> list:
    """Get all entries for a specific date.
    
    Args:
        date: YYYY-MM-DD format
    
    Returns:
        List of entry dicts
    """
    entries = []
    if not LOG_FILE.exists():
        return entries
    
    with open(LOG_FILE) as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Use drank_at to determine date
            drank_at = row.get("drank_at", "")
            entry_date = drank_at[:10] if drank_at else ""
            if entry_date == date:
                entries.append(row)
    
    return entries

def calculate_cumulative_for_date(date: str) -> int:
    """Calculate cumulative ml for a specific date.
    
    Args:
        date: YYYY-MM-DD format
    
    Returns:
        Total ml for that date
    """
    entries = get_entries_by_date(date)
    return sum(int(e.get("ml_drank", 0)) for e in entries)

# ============================================================================
# DYNAMIC SCHEDULING (DETERMINISTIC FORMULA)
# ============================================================================

def calculate_expected_percent(current_hour: int = None, start_hour: int = 9, cutoff_hour: int = 22) -> float:
    """Calculate expected progress based on time of day.
    
    Formula: ((hours_passed + 1) / total_hours) × 100
    
    At hour 9 (9am): we've had 1 hour of the day
    At hour 22 (10pm): we've had 13 hours
    
    Example:
        9am: (1/13) × 100 = 7.7%
        4pm (16): (8/13) × 100 = 61.5%
        10pm (22): (13/13) × 100 = 100%
    """
    if current_hour is None:
        current_hour = datetime.now().hour
    
    total_hours = cutoff_hour - start_hour  # 13 hours (9 to 22)
    hours_passed = max(0, current_hour - start_hour)  # 0 at 9am
    
    # +1 because at 9am we've completed 1 hour (9-10)
    return min(100, ((hours_passed + 1) / total_hours) * 100)

def get_dynamic_threshold() -> dict:
    """Get the dynamic threshold for triggering extras.
    
    Returns dict with:
    - expected_percent: What user should have at current time
    - threshold: expected - margin = when to trigger
    - margin_percent: Configured margin
    """
    config = load_config()
    formula = config.get("dynamic_scheduling", {}).get("formula", {})
    
    margin = formula.get("margin_percent", 25)
    start = formula.get("start_hour", 9)
    cutoff = formula.get("cutoff_hour", 22)
    
    current_hour = datetime.now().hour
    expected = calculate_expected_percent(current_hour, start, cutoff)
    threshold = max(0, expected - margin)
    
    return {
        "expected_percent": round(expected, 1),
        "threshold": round(threshold, 1),
        "margin_percent": margin,
        "current_hour": current_hour,
        "start_hour": start,
        "cutoff_hour": cutoff
    }

def get_aggressiveness_adjustment(current_hour: int, config: dict) -> int:
    """Get threshold adjustment based on time of day.
    
    Configurable aggressiveness curve:
    - Early day: easier to trigger (less adjustment)
    - Late day: more aggressive (more adjustment = easier to trigger)
    
    This helps the "coach" be more persistent near cutoff time.
    """
    extra_config = config.get("dynamic_scheduling", {}).get("extra_notifications", {})
    curve = extra_config.get("aggressiveness_curve", {})
    
    if not curve.get("enabled", False):
        return 0
    
    schedule = curve.get("schedule", [])
    
    for period in schedule:
        start = period.get("start", 0)
        end = period.get("end", 24)
        adjustment = period.get("adjustment", 0)
        
        if start <= current_hour < end:
            return adjustment
    
    return 0

def should_send_extra_notification() -> dict:
    """Check if extra notification should be sent (Coach Mode).
    
    This is the CORE function for dynamic scheduling.
    Called by heartbeat to decide whether to send extra notification.
    
    COACH MODE LOGIC:
    - Every check is independent
    - If behind → send notification
    - If doing well → skip
    - If falls behind again later → send again (no locking)
    - Max per hour prevents spam
    
    Returns:
        dict with:
        - should_send: Boolean
        - reason: Explanation
        - current_status: Full status
        - threshold_info: Dynamic threshold data
    """
    config = load_config()
    ds_config = config.get("dynamic_scheduling", {})
    now = datetime.now()
    current_hour = now.hour
    
    # Check if dynamic scheduling is enabled
    if not ds_config.get("enabled", False):
        return {
            "should_send": False,
            "reason": "dynamic_scheduling_disabled",
            "current_status": get_today_status(),
            "threshold_info": get_dynamic_threshold()
        }
    
    # Get working hours from config (NOT HARDCODED)
    formula = ds_config.get("formula", {})
    start_hour = formula.get("start_hour", 9)
    cutoff_hour = formula.get("cutoff_hour", 22)
    
    # Check if in working hours
    if current_hour < start_hour or current_hour >= cutoff_hour:
        return {
            "should_send": False,
            "reason": "outside_working_hours",
            "current_status": get_today_status(),
            "threshold_info": get_dynamic_threshold()
        }
    
    # Get extra notification config (NOT HARDCODED)
    extra_config = ds_config.get("extra_notifications", {})
    interval_minutes = extra_config.get("interval_minutes", 30)
    max_per_hour = extra_config.get("max_per_hour", 2)
    max_per_day = extra_config.get("max_per_day", None)  # Optional
    healthy_threshold = extra_config.get("healthy_threshold_percent", 80)
    
    # Get current status
    status = get_today_status()
    
    # Check if user has logged anything today
    if status["current_ml"] == 0:
        return {
            "should_send": False,
            "reason": "no_water_logged_today",
            "current_status": status,
            "threshold_info": get_dynamic_threshold()
        }
    
    # Check if already at healthy threshold
    if status["percentage"] >= healthy_threshold:
        return {
            "should_send": False,
            "reason": "healthy_progress",
            "current_status": status,
            "threshold_info": get_dynamic_threshold(),
            "message": f"At {status['percentage']}% - doing great! No extra notification needed."
        }
    
    # Check max per hour - FIRST reset counter if hour changed
    current_hour = now.hour
    last_extra_hour = config.get("status", {}).get("last_extra_hour", None)
    if last_extra_hour is not None and last_extra_hour != current_hour:
        # Hour changed - reset the hourly counter
        config.setdefault("status", {})["extras_this_hour"] = 0
    
    extras_this_hour = config.get("status", {}).get("extras_this_hour", 0)
    if extras_this_hour >= max_per_hour:
        return {
            "should_send": False,
            "reason": "max_per_hour_reached",
            "extras_this_hour": extras_this_hour,
            "max_per_hour": max_per_hour,
            "current_status": status,
            "threshold_info": get_dynamic_threshold()
        }
    
    # Check max per day (if configured)
    if max_per_day:
        extra_used = config.get("status", {}).get("extra_notifications_today", 0)
        if extra_used >= max_per_day:
            return {
                "should_send": False,
                "reason": "max_per_day_reached",
                "extra_used_today": extra_used,
                "max_per_day": max_per_day,
                "current_status": status,
                "threshold_info": get_dynamic_threshold()
            }
    
    # Check if enough time since last extra notification
    last_extra = config.get("status", {}).get("last_extra_notification")
    if last_extra:
        try:
            last_time = datetime.fromisoformat(last_extra.replace("Z", "+00:00"))
            minutes_since = (now - last_time).total_seconds() / 60
            if minutes_since < interval_minutes:
                return {
                    "should_send": False,
                    "reason": "too_soon_since_last",
                    "minutes_since_last": round(minutes_since),
                    "interval_required": interval_minutes,
                    "current_status": status,
                    "threshold_info": get_dynamic_threshold()
                }
        except:
            pass  # If parsing fails, continue
    
    # Calculate threshold with aggressiveness curve
    threshold_info = get_dynamic_threshold()
    adjustment = get_aggressiveness_adjustment(current_hour, config)
    effective_threshold = threshold_info["threshold"] + adjustment
    
    # Check if under effective threshold
    if status["percentage"] < effective_threshold:
        return {
            "should_send": True,
            "reason": "under_threshold",
            "current_percent": status["percentage"],
            "effective_threshold": effective_threshold,
            "base_threshold": threshold_info["threshold"],
            "aggressiveness_adjustment": adjustment,
            "extras_this_hour": extras_this_hour,
            "max_per_hour": max_per_hour,
            "current_status": status,
            "threshold_info": threshold_info
        }
    
    return {
        "should_send": False,
        "reason": "on_track",
        "current_status": status,
        "threshold_info": threshold_info
    }

def increment_extra_notifications() -> dict:
    """Increment the counter for extra notifications used today and this hour."""
    config = load_config()
    now = datetime.now()
    current_hour = now.hour
    
    if "status" not in config:
        config["status"] = {}
    
    # Track daily extras
    config["status"]["extra_notifications_today"] = config["status"].get("extra_notifications_today", 0) + 1
    
    # Track hourly extras (with hour reset)
    last_hour = config["status"].get("last_extra_hour", None)
    if last_hour != current_hour:
        config["status"]["extras_this_hour"] = 0  # Reset on new hour
    
    config["status"]["extras_this_hour"] = config["status"].get("extras_this_hour", 0) + 1
    config["status"]["last_extra_hour"] = current_hour
    config["status"]["last_extra_notification"] = now.isoformat() + "Z"
    
    save_config(config)
    return {
        "extra_notifications_today": config["status"]["extra_notifications_today"],
        "extras_this_hour": config["status"]["extras_this_hour"],
        "last_extra_notification": config["status"]["last_extra_notification"]
    }

def reset_daily_counters() -> dict:
    """Reset daily counters. Called at start of new day."""
    config = load_config()
    if "status" not in config:
        config["status"] = {}
    config["status"]["extra_notifications_today"] = 0
    config["status"]["extras_this_hour"] = 0
    config["status"]["last_extra_notification"] = None
    config["status"]["last_extra_hour"] = None
    save_config(config)
    return {"extra_notifications_today": 0, "extras_this_hour": 0}

# ============================================================================
# ANALYTICS
# ============================================================================

def get_week_stats(days: int = 7) -> dict:
    """Get stats for last N days."""
    stats = {"days": [], "total_ml": 0, "avg_ml": 0, "goal_hits": 0, "days_tracked": 0}
    
    if not LOG_FILE.exists():
        return stats
    
    with open(LOG_FILE) as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    # Group by date - sum ml_drank for each day
    by_date = {}
    for row in rows:
        d = row.get("date")
        if d:
            if d not in by_date:
                by_date[d] = {"ml": 0, "goal": 3325}
            by_date[d]["ml"] += int(row.get("ml_drank", 0))
            by_date[d]["goal"] = int(float(row.get("goal_at_time", 3325)))
    
    # Last N days - include ALL days, even with 0ml
    import datetime as dt
    daily_goal = 3325  # Default goal
    for i in range(days):
        d = (dt.date.today() - dt.timedelta(days=i)).strftime("%Y-%m-%d")
        ml = by_date.get(d, {}).get("ml", 0)
        goal = by_date.get(d, {}).get("goal", daily_goal)
        
        stats["days"].append({
            "date": d, 
            "ml": ml, 
            "goal": goal,
            "percentage": round(ml / goal * 100, 1) if goal > 0 else 0
        })
        stats["total_ml"] += ml
        stats["days_tracked"] += 1
        if ml >= goal:
            stats["goal_hits"] += 1
    
    stats["avg_ml"] = stats["total_ml"] // stats["days_tracked"] if stats["days_tracked"] else 0
    return stats

# ============================================================================
# BODY METRICS FUNCTIONS
# ============================================================================

BODY_METRICS_FILE = DATA_DIR / "body_metrics.csv"

def load_body_metrics():
    """Load all body metrics entries."""
    if not BODY_METRICS_FILE.exists():
        return []
    with open(BODY_METRICS_FILE) as f:
        return list(csv.DictReader(f))

def log_body_metrics(weight_kg: float = None, height_m: float = None, 
                    body_fat_pct: float = None, muscle_pct: float = None,
                    water_pct: float = None) -> dict:
    """Log body metrics for today.
    
    Args:
        weight_kg: Weight in kg
        height_m: Height in meters
        body_fat_pct: Body fat percentage
        muscle_pct: Muscle percentage
        water_pct: Body water percentage
    
    Returns:
        Latest metrics and calculated BMI if height provided
    """
    today = date.today().strftime("%Y-%m-%d")
    now = datetime.now().isoformat() + "Z"
    
    # Calculate BMI if height and weight available
    bmi = None
    if weight_kg and height_m:
        bmi = round(weight_kg / (height_m ** 2), 1)
    
    # Get existing entry for today or create new
    existing = load_body_metrics()
    today_entry = None
    for entry in existing:
        if entry.get("date") == today:
            today_entry = entry
            break
    
    # Update fields
    if today_entry:
        data = dict(today_entry)
    else:
        data = {"date": today, "weight_kg": "", "height_m": "", "bmi": "", 
                "body_fat_pct": "", "muscle_pct": "", "water_pct": ""}
    
    if weight_kg is not None:
        data["weight_kg"] = weight_kg
    if height_m is not None:
        data["height_m"] = height_m
    if bmi is not None:
        data["bmi"] = bmi
    if body_fat_pct is not None:
        data["body_fat_pct"] = body_fat_pct
    if muscle_pct is not None:
        data["muscle_pct"] = muscle_pct
    if water_pct is not None:
        data["water_pct"] = water_pct
    
    # Write to CSV
    file_exists = BODY_METRICS_FILE.exists()
    with open(BODY_METRICS_FILE, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["date", "weight_kg", "height_m", "bmi", "body_fat_pct", "muscle_pct", "water_pct"])
        if not file_exists:
            writer.writeheader()
        writer.writerow(data)
    
    return {"logged": data, "bmi_calculated": bmi}

def get_latest_body_metrics() -> dict:
    """Get the most recent body metrics entry."""
    entries = load_body_metrics()
    if not entries:
        return {"error": "No body metrics logged yet"}
    
    # Get most recent (by date)
    latest = sorted(entries, key=lambda x: x.get("date", ""), reverse=True)[0]
    return latest

def get_body_metrics_history(days: int = 30) -> dict:
    """Get body metrics history for last N days."""
    entries = load_body_metrics()
    import datetime
    cutoff = (datetime.date.today() - datetime.timedelta(days=days)).strftime("%Y-%m-%d")
    
    recent = [e for e in entries if e.get("date", "") >= cutoff]
    return {
        "entries": recent,
        "count": len(recent)
    }

# ============================================================================
# CLI ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    import sys
    
    # Handle "status" as default
    if len(sys.argv) == 1:
        cmd = "status"
    else:
        cmd = sys.argv[1]
    
    if cmd == "status":
        print(json.dumps(get_today_status()))
    
    elif cmd == "log":
        # Usage: water.py log <amount_ml>
        # NOTE: LLM interprets user input first, then calls this with integer ml
        if len(sys.argv) > 2:
            try:
                amount_ml = int(sys.argv[2])
                print(json.dumps(log_water(amount_ml, message_id=get_current_message_id())))
            except ValueError:
                print(json.dumps({"error": "Amount must be integer ml. LLM should convert first."}))
        else:
            print(json.dumps({"error": "Usage: water.py log <amount_ml>"}))
    
    elif cmd == "week":
        print(json.dumps(get_week_stats()))
    
    elif cmd == "config":
        print(json.dumps(load_config()))
    
    elif cmd == "setup":
        # Check if user has completed first-time setup
        print(json.dumps(is_user_setup()))
    
    elif cmd == "threshold":
        print(json.dumps(get_dynamic_threshold()))
    
    elif cmd == "dynamic":
        print(json.dumps(should_send_extra_notification()))
    
    elif cmd == "dynamic_increment":
        print(json.dumps(increment_extra_notifications()))
    
    elif cmd == "dynamic_reset":
        print(json.dumps(reset_daily_counters()))
    
    elif cmd == "goal":
        print(json.dumps({"goal_ml": get_daily_goal()}))
    
    elif cmd == "remove":
        # Usage: water.py remove <entry_id>
        if len(sys.argv) > 2:
            entry_id = sys.argv[2]
            print(json.dumps(remove_entry_by_id(entry_id)))
        else:
            print(json.dumps({"error": "Usage: water.py remove <entry_id>"}))
    
    elif cmd == "set_body_weight":
        if len(sys.argv) > 2:
            weight = float(sys.argv[2])
            update_goal = len(sys.argv) > 3 and sys.argv[3] == "--update-goal"
            print(json.dumps(update_user_weight(weight, update_goal)))
        else:
            print(json.dumps({"error": "Usage: water.py set_body_weight <kg> [--update-goal]"}))
    
    elif cmd == "body":
        # Usage: water.py body [--weight 80] [--height 1.75] [--body-fat 18] [--muscle 40] [--water 55]
        args = sys.argv[2:]
        kwargs = {}
        for arg in args:
            if arg.startswith("--weight"):
                kwargs["weight_kg"] = float(arg.split("=")[1]) if "=" in arg else None
            elif arg.startswith("--height"):
                kwargs["height_m"] = float(arg.split("=")[1]) if "=" in arg else None
            elif arg.startswith("--body-fat"):
                kwargs["body_fat_pct"] = float(arg.split("=")[1]) if "=" in arg else None
            elif arg.startswith("--muscle"):
                kwargs["muscle_pct"] = float(arg.split("=")[1]) if "=" in arg else None
            elif arg.startswith("--water"):
                kwargs["water_pct"] = float(arg.split("=")[1]) if "=" in arg else None
        print(json.dumps(log_body_metrics(**kwargs)))
    
    elif cmd == "body_latest":
        print(json.dumps(get_latest_body_metrics()))
    
    elif cmd == "body_history":
        days = 30
        if len(sys.argv) > 2:
            days = int(sys.argv[2])
        print(json.dumps(get_body_metrics_history(days)))
    
    else:
        print(json.dumps({"error": f"Unknown command: {cmd}"}))
