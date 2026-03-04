#!/bin/bash
# quota_watcher.sh — Retry apply_feedback until quota clears, then notify Master

SKILL_DIR="$HOME/.openclaw/workspace/skills/video-production"
STORYBOARD="$HOME/Desktop/Muffin/Media/MMM-Ad/storyboard.json"
FEEDBACK="$HOME/Desktop/Muffin/Media/MMM-Ad/feedback.json"
MASTER="+13106509695"

source ~/.zshenv 2>/dev/null

OUTPUT=$("$SKILL_DIR/.venv/bin/python3" "$SKILL_DIR/scripts/apply_feedback.py" \
  --storyboard "$STORYBOARD" \
  --feedback "$FEEDBACK" 2>&1)

EXIT_CODE=$?

# Still rate-limited — exit 1, cron will retry in 30 min
if echo "$OUTPUT" | grep -q "RESOURCE_EXHAUSTED\|429"; then
    echo "[$(date)] Quota still exhausted. Retrying later."
    exit 1
fi

# Success — notify, rebuild preview, disable self
if [ $EXIT_CODE -eq 0 ]; then
    echo "[$(date)] Generation complete."

    # Rebuild preview
    "$SKILL_DIR/.venv/bin/python3" "$SKILL_DIR/scripts/generate_preview.py" \
      --storyboard "$STORYBOARD" --no-open

    # Notify Master via iMessage
    imsg send --to "$MASTER" \
      --text "🎬 MMM clips ready. scene_02 + scene_04 regenerated. Preview rebuilt — open ~/Desktop/Muffin/Media/MMM-Ad/preview.html to review and send next feedback." \
      --service imessage

    # Remove the cron job (self-destruct)
    crontab -l | grep -v "quota_watcher" | crontab -
    echo "[$(date)] Cron removed. Done."
    exit 0
fi

# Other error — log but don't retry forever
echo "[$(date)] Unexpected error: $OUTPUT"
exit 1
