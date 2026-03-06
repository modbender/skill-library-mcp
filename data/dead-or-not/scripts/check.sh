#!/bin/bash

# DeadOrNot - Check if user is still alive
# Runs once per day via cron

CONFIG_DIR="$HOME/.openclaw/apps/deadornot"
LAST_SEEN_FILE="$CONFIG_DIR/last_seen"
LAST_ASKED_FILE="$CONFIG_DIR/last_asked"
CONFIG_FILE="$CONFIG_DIR/config"
SCRIPT_DIR="$(dirname "$0")"

# Load config
if [ ! -f "$CONFIG_FILE" ]; then
    mkdir -p "$CONFIG_DIR"
    echo "# DeadOrNot Configuration" > "$CONFIG_FILE"
    echo "TIMEOUT_HOURS=24" >> "$CONFIG_FILE"
    echo "NOTIFY_EMAIL=" >> "$CONFIG_FILE"
    echo "MESSAGE=User is unresponsive!" >> "$CONFIG_FILE"
    echo "ASK_HOUR=10" >> "$CONFIG_FILE"
    echo "SMTP_SERVER=smtp.qq.com" >> "$CONFIG_FILE"
    echo "SMTP_PORT=465" >> "$CONFIG_FILE"
    echo "SMTP_EMAIL=" >> "$CONFIG_FILE"
    echo "SMTP_PASSWORD=" >> "$CONFIG_FILE"
fi

source "$CONFIG_FILE"

NOW=$(date +%s)
CURRENT_HOUR=$(date +%H)

if [ -f "$LAST_SEEN_FILE" ]; then
    LAST_SEEN=$(cat "$LAST_SEEN_FILE")
else
    LAST_SEEN=$NOW
fi

DIFF=$((NOW - LAST_SEEN))
TIMEOUT_SECONDS=$((TIMEOUT_HOURS * 3600))

echo "[$(date)] Diff: ${DIFF}s, Timeout: ${TIMEOUT_SECONDS}s"

if [ $DIFF -ge $TIMEOUT_SECONDS ]; then
    if [ -f "$LAST_ASKED_FILE" ]; then
        LAST_ASKED=$(cat "$LAST_ASKED_FILE")
        ASKED_DIFF=$((NOW - LAST_ASKED))
        if [ $ASKED_DIFF -lt 7200 ]; then
            echo "Already asked within 2 hours, waiting..."
            exit 0
        fi
    fi
    
    if [ "$CURRENT_HOUR" -ge "$ASK_HOUR" ] && [ "$CURRENT_HOUR" -lt "$((ASK_HOUR + 2))" ]; then
        echo "TIME_TO_ASK=true" > "$CONFIG_DIR/check_flag"
        echo "Setting ask flag - agent will check on user"
        echo "$NOW" > "$LAST_ASKED_FILE"
    else
        echo "Outside ask hours ($ASK_HOUR-$((ASK_HOUR+2))), skipping"
    fi
else
    rm -f "$CONFIG_DIR/check_flag"
    echo "All good! User is still alive."
fi
