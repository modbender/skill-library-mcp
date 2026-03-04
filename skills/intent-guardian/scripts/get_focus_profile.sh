#!/bin/bash
# Read the user's focus profile (long-term pattern data).

LOG_DIR="${INTENT_GUARDIAN_DATA_DIR:-$HOME/.openclaw/memory/skills/intent-guardian}"
PROFILE_FILE="$LOG_DIR/focus_profile.json"

if [ ! -f "$PROFILE_FILE" ]; then
    cat <<'EOF'
{
  "user_id": "default",
  "updated_at": "",
  "patterns": {
    "avg_focus_duration_minutes": 0,
    "interruption_sources": {},
    "peak_focus_hours": [],
    "high_risk_transitions": [],
    "reminder_effectiveness": {
      "accepted": 0,
      "dismissed": 0,
      "ignored": 0
    }
  }
}
EOF
    exit 0
fi

cat "$PROFILE_FILE"
