#!/usr/bin/env python3
"""
config_wizard.py — Interactive configuration wizard.

Walks users through initial setup, generating a config.json with
sensible defaults based on their preferences.

Usage:
  python3 config_wizard.py              # interactive setup
  python3 config_wizard.py --defaults   # generate config with all defaults
  python3 config_wizard.py --validate   # validate existing config.json
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

if sys.version_info < (3, 8):
    print(json.dumps({"error": "python_version_too_old", "detail": "Python 3.8+ required."}))
    sys.exit(1)

SKILL_DIR = Path.home() / ".openclaw/workspace/skills/proactive-claw"
CONFIG_FILE = SKILL_DIR / "config.json"

DEFAULT_CONFIG = {
    "calendar_backend": "google",
    "timezone": "UTC",
    "user_email": "",
    "pre_checkin_offset_default": "1 day",
    "pre_checkin_offset_same_day": "1 hour",
    "post_checkin_offset": "30 minutes",
    "conversation_threshold": 5,
    "calendar_threshold": 6,
    "scan_days_ahead": 7,
    "scan_cache_ttl_minutes": 30,
    "daemon_interval_minutes": 15,
    "proactivity_mode": "balanced",
    "max_autonomy_level": "confirm",
    "quiet_hours": {"weekdays": "22:00-07:00", "weekends": "21:00-09:00"},
    "memory_decay_half_life_days": 90,
    "max_nudges_per_day": 12,
    "nudge_cooldown_minutes": 30,
    "openclaw_cal_id": "",
    "default_user_calendar": "",
    "notes_destination": "local",
    "notes_path": str(SKILL_DIR / "outcomes") + "/",
    "feature_conversation": True,
    "feature_calendar": True,
    "feature_daemon": True,
    "feature_memory": True,
    "feature_conflicts": True,
    "feature_rules": True,
    "feature_intelligence_loop": True,
    "feature_policy_engine": True,
    "feature_orchestrator": True,
    "feature_energy": True,
    "feature_cal_editor": True,
    "feature_relationship": True,
    "feature_adaptive_notifications": True,
    "feature_proactivity_engine": True,
    "feature_interrupt_controller": True,
    "feature_explainability": True,
    "feature_health_check": True,
    "feature_simulation": True,
    "feature_export": True,
    "feature_behaviour_report": True,
    "feature_config_wizard": True,
    "feature_policy_conflict_detection": True,
    "feature_cross_skill": False,
    "feature_voice": False,
    "feature_team_awareness": False,
    "feature_llm_rater": False,
    "notification_channels": ["openclaw", "system"],
    "telegram": {"bot_token": "", "chat_id": ""},
    "clawhub_token": "",
    "nextcloud": {"url": "", "username": "", "password": "", "openclaw_calendar_url": ""},
    "llm_rater": {
        "enabled": False,
        "base_url": "http://localhost:11434/v1",
        "model": "qwen2.5:3b",
        "api_key_env": "",
        "timeout": 30,
        "max_tokens": 256,
        "temperature": 0.1,
    },
}


def detect_system_timezone() -> str:
    """Try to detect OS timezone."""
    try:
        import time
        name = time.tzname[0]
        # Common mappings
        tz_map = {
            "CET": "Europe/Berlin", "CEST": "Europe/Berlin",
            "GMT": "Europe/London", "BST": "Europe/London",
            "EST": "America/New_York", "EDT": "America/New_York",
            "CST": "America/Chicago", "CDT": "America/Chicago",
            "MST": "America/Denver", "MDT": "America/Denver",
            "PST": "America/Los_Angeles", "PDT": "America/Los_Angeles",
            "AEST": "Australia/Sydney", "AEDT": "Australia/Sydney",
        }
        return tz_map.get(name, "UTC")
    except Exception:
        return "UTC"


def _ask(prompt: str, default: str = "", options: list = None) -> str:
    """Interactive prompt with optional default and options."""
    if options:
        option_str = "/".join(options)
        full = f"{prompt} [{option_str}] (default: {default}): "
    elif default:
        full = f"{prompt} (default: {default}): "
    else:
        full = f"{prompt}: "

    try:
        answer = input(full).strip()
    except (EOFError, KeyboardInterrupt):
        print()
        return default

    if not answer:
        return default
    if options and answer not in options:
        print(f"  Invalid choice. Using default: {default}")
        return default
    return answer


def run_wizard() -> dict:
    """Interactive setup flow."""
    print("\n🦞 Proactive Claw — Configuration Wizard")
    print("=" * 42)
    print("Answer a few questions to generate your config.json.\n")

    config = dict(DEFAULT_CONFIG)

    # 1. Calendar backend
    backend = _ask("Calendar backend", "google", ["google", "nextcloud"])
    config["calendar_backend"] = backend

    # 2. Timezone
    detected = detect_system_timezone()
    tz = _ask(f"Timezone (detected: {detected})", detected)
    config["timezone"] = tz

    # 3. Email
    email = _ask("Your email (for calendar matching)", "")
    if email:
        config["user_email"] = email

    # 4. Proactivity mode
    print("\nProactivity modes:")
    print("  low       — only nudge for high-stakes events")
    print("  balanced  — default, normal proactivity")
    print("  executive — aggressive prep for everything")
    mode = _ask("Proactivity mode", "balanced", ["low", "balanced", "executive"])
    config["proactivity_mode"] = mode

    # 5. Autonomy level
    print("\nAutonomy levels:")
    print("  advisory   — never auto-act, just suggest")
    print("  confirm    — always ask before acting")
    print("  autonomous — trust policies to auto-execute")
    autonomy = _ask("Max autonomy level", "autonomous", ["advisory", "confirm", "autonomous"])
    config["max_autonomy_level"] = autonomy

    # 6. Notification channels
    print("\nNotification channels (comma-separated):")
    print("  openclaw — in-chat nudges (default)")
    print("  system   — desktop notifications (default)")
    print("  telegram — Telegram bot messages")
    channels_str = _ask("Channels", "openclaw,system")
    config["notification_channels"] = [c.strip() for c in channels_str.split(",") if c.strip()]

    if "telegram" in config["notification_channels"]:
        token = _ask("Telegram bot token", "")
        chat_id = _ask("Telegram chat ID", "")
        config["telegram"] = {"bot_token": token, "chat_id": chat_id}

    # 7. Quiet hours
    use_quiet = _ask("Enable quiet hours?", "yes", ["yes", "no"])
    if use_quiet == "yes":
        weekday = _ask("Weekday quiet hours", "22:00-07:00")
        weekend = _ask("Weekend quiet hours", "21:00-09:00")
        config["quiet_hours"] = {"weekdays": weekday, "weekends": weekend}
    else:
        config["quiet_hours"] = {}

    # 8. Scan horizon
    days = _ask("How many days ahead to scan", "7")
    try:
        config["scan_days_ahead"] = int(days)
    except ValueError:
        config["scan_days_ahead"] = 7

    print("\n✅ Configuration ready!")
    return config


def validate_config() -> dict:
    """Validate existing config.json."""
    if not CONFIG_FILE.exists():
        return {"status": "error", "detail": "config.json not found."}
    try:
        with open(CONFIG_FILE) as f:
            config = json.load(f)
    except json.JSONDecodeError as e:
        return {"status": "error", "detail": f"Invalid JSON: {e}"}

    issues = []
    # Check for missing critical keys
    for key in ("calendar_backend", "timezone"):
        if key not in config:
            issues.append(f"Missing: {key}")

    # Check types
    for key, val in config.items():
        if key.startswith("feature_") and not isinstance(val, bool):
            issues.append(f"{key} should be boolean")
        if key.endswith("_minutes") and not isinstance(val, (int, float)):
            issues.append(f"{key} should be numeric")

    return {
        "status": "ok" if not issues else "warning",
        "issues": issues,
        "keys": len(config),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--defaults",
        action="store_true",
        help="Generate config with safe defaults (non-interactive).",
    )
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Validate existing config.json",
    )
    parser.add_argument(
        "--autonomy",
        choices=["advisory", "confirm", "autonomous"],
        default="confirm",
        help="Set max_autonomy_level when using --defaults (default: confirm).",
    )
    parser.add_argument(
        "--i-accept-risk",
        action="store_true",
        help="Required to set --autonomy autonomous (unsafe).",
    )

    args = parser.parse_args()

    if args.defaults:
        cfg = dict(DEFAULT_CONFIG)
        # Safe by default: unattended config generation must never silently enable autonomy.
        if args.autonomy == "autonomous" and not args.i_accept_risk:
            raise SystemExit(
                "Refusing to set max_autonomy_level=autonomous without --i-accept-risk."
            )
        cfg["max_autonomy_level"] = args.autonomy

        SKILL_DIR.mkdir(parents=True, exist_ok=True)
        with open(CONFIG_FILE, "w") as f:
            json.dump(cfg, f, indent=2)

        print(
            json.dumps(
                {
                    "status": "ok",
                    "path": str(CONFIG_FILE),
                    "message": "Default config.json written.",
                    "max_autonomy_level": cfg.get("max_autonomy_level"),
                }
            )
        )

    elif args.validate:
        print(json.dumps(validate_config(), indent=2))

    else:
        config = run_wizard()
        SKILL_DIR.mkdir(parents=True, exist_ok=True)
        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f, indent=2)
        print(f"
📝 Config written to {CONFIG_FILE}")
        print("   Next: run setup.sh to connect your calendar.")


if __name__ == "__main__":
    main()
