#!/bin/bash
#
# Daily Model Optimization Script
# 
# Add this to your crontab to automatically optimize model selection
# based on the latest AI capability intelligence.
#

SKILL_DIR="skills/model-benchmarks"
LOG_FILE="$HOME/.openclaw/logs/model-optimization.log"

echo "[$(date)] Starting daily model optimization..." >> "$LOG_FILE"

# Fetch latest benchmark data
python3 "$SKILL_DIR/scripts/run.py" fetch >> "$LOG_FILE" 2>&1
if [ $? -ne 0 ]; then
    echo "[$(date)] ERROR: Failed to fetch benchmark data" >> "$LOG_FILE"
    exit 1
fi

# Get recommendations for common tasks
echo "[$(date)] Getting task recommendations..." >> "$LOG_FILE"

for task in coding writing analysis translation; do
    echo "=== $task recommendations ===" >> "$LOG_FILE"
    python3 "$SKILL_DIR/scripts/run.py" recommend --task "$task" >> "$LOG_FILE" 2>&1
done

# Check for significant cost efficiency changes
python3 "$SKILL_DIR/scripts/run.py" analyze --alert-threshold 20 >> "$LOG_FILE" 2>&1

echo "[$(date)] Daily optimization complete" >> "$LOG_FILE"