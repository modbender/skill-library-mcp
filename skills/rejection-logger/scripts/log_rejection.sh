#!/usr/bin/env bash
# Usage: ./log_rejection.sh "Target Task" "Reason for Rejection" "Alternative"

TARGET=$1
REASON=$2
ALT=$3
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
ID="REJ-$(date +%Y%m%d)-$((RANDOM%900+100))"

LEARNINGS_DIR=".learnings"
FILE="$LEARNINGS_DIR/REJECTIONS.md"

mkdir -p "$LEARNINGS_DIR"

if [ ! -f "$FILE" ]; then
  echo "# Rejection Logs" > "$FILE"
fi

echo -e "\n## [$ID] $TARGET\n\n**Timestamp**: $TIMESTAMP\n**Decision**: REJECTED\n**Reason**: $REASON\n**Alternative**: $ALT" >> "$FILE"
echo "✅ Logged rejection: $ID"
