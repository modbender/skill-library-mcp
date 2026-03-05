#!/usr/bin/env python3
"""
UXR Observer v2.0 - First Run Setup
Creates the local directory structure and config for the embedded UXR study.
All data stays local. Nothing is transmitted.
"""

import json
import uuid
import hashlib
from datetime import datetime
from pathlib import Path

BASE_DIR = Path.home() / ".uxr-observer"
SESSIONS_DIR = BASE_DIR / "sessions"
REPORTS_DIR = BASE_DIR / "reports"
CONFIG_PATH = BASE_DIR / "config.json"

# Default model pricing (USD per million tokens)
DEFAULT_MODEL_PRICING = {
    "claude-sonnet-4-20250514": {"input_per_mtok": 3.00, "output_per_mtok": 15.00},
    "claude-opus-4-20250514": {"input_per_mtok": 15.00, "output_per_mtok": 75.00},
    "claude-haiku-4-20250506": {"input_per_mtok": 0.80, "output_per_mtok": 4.00},
    "default": {"input_per_mtok": 3.00, "output_per_mtok": 15.00},
}


def generate_participant_id():
    """Generate an anonymous participant hash - no PII involved."""
    raw = f"{uuid.uuid4()}-{datetime.now().isoformat()}"
    return hashlib.sha256(raw.encode()).hexdigest()[:12]


def setup():
    """Create directory structure and initial config."""
    # Create directories
    BASE_DIR.mkdir(exist_ok=True)
    SESSIONS_DIR.mkdir(exist_ok=True)
    REPORTS_DIR.mkdir(exist_ok=True)

    # Create today's session directory with supersummary subdir
    today = datetime.now().strftime("%Y-%m-%d")
    today_dir = SESSIONS_DIR / today
    today_dir.mkdir(exist_ok=True)
    (today_dir / "supersummary").mkdir(exist_ok=True)

    # Initialize config if it doesn't exist
    if not CONFIG_PATH.exists():
        config = {
            "study_active": True,
            "study_start_date": today,
            "survey_frequency": "after_each_task",
            "eod_survey_time": "18:00",
            "eod_survey_fired_today": False,
            "opted_out_topics": [],
            "participant_id": generate_participant_id(),
            "cost_tracking": {
                "method": "actual",
                "fallback": "estimated",
                "model_pricing": DEFAULT_MODEL_PRICING,
            },
            "created_at": datetime.now().isoformat(),
        }
        CONFIG_PATH.write_text(json.dumps(config, indent=2))
        print(f"[UXR Observer] Created config with participant ID: {config['participant_id']}")
    else:
        # Update existing config with new v2 fields if missing
        config = json.loads(CONFIG_PATH.read_text())
        updated = False
        if "eod_survey_time" not in config:
            config["eod_survey_time"] = "18:00"
            updated = True
        if "eod_survey_fired_today" not in config:
            config["eod_survey_fired_today"] = False
            updated = True
        if "cost_tracking" not in config:
            config["cost_tracking"] = {
                "method": "actual",
                "fallback": "estimated",
                "model_pricing": DEFAULT_MODEL_PRICING,
            }
            updated = True
        if updated:
            CONFIG_PATH.write_text(json.dumps(config, indent=2))
            print("[UXR Observer] Updated config with v2.0 fields.")
        else:
            print("[UXR Observer] Config already exists with all fields.")

    # Create empty JSONL files for today if they don't exist
    obs_path = today_dir / "observations.jsonl"
    survey_path = today_dir / "surveys.jsonl"

    if not obs_path.exists():
        obs_path.touch()
    if not survey_path.exists():
        survey_path.touch()

    print(f"[UXR Observer] Setup complete. Data directory: {BASE_DIR}")
    print(f"[UXR Observer] Today's session: {today_dir}")
    return str(BASE_DIR)


if __name__ == "__main__":
    setup()
