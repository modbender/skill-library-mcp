#!/usr/bin/env bash
set -euo pipefail

command -v jq >/dev/null || { echo '{"status":"error","message":"jq required"}'; exit 1; }

WORKSPACE="${1:-$HOME/clawd}"
DATA_DIR="$WORKSPACE/memory/life-architect"
STATE_FILE="$DATA_DIR/state.json"
OUT="$DATA_DIR/final-document.md"

[[ ! -f "$STATE_FILE" ]] && echo '{"status":"error","message":"Not initialized"}' && exit 1

LANG=$(jq -r '.lang // "en"' "$STATE_FILE")
DONE=$(jq '[.sessions[] | select(.status=="completed")] | length' "$STATE_FILE")

# Generate header based on language
if [[ "$LANG" == "ru" ]]; then
    cat > "$OUT" << EOF
# 🧠 Life Architect — Финальный Документ

Этот документ содержит все инсайты и ответы из 10 сессий психологической проработки.

**Сессий завершено:** $DONE/10

---

EOF
else
    cat > "$OUT" << EOF
# 🧠 Life Architect — Final Document

This document contains all insights and responses from 10 sessions of psychological work.

**Sessions completed:** $DONE/10

---

EOF
fi

# Append each session file
for i in {1..10}; do
    f="$DATA_DIR/session-$(printf "%02d" $i).md"
    if [[ -f "$f" ]]; then
        cat "$f" >> "$OUT"
        echo -e "\n---\n" >> "$OUT"
    fi
done

# Append insights if exists
INSIGHTS_FILE="$DATA_DIR/insights.md"
if [[ -f "$INSIGHTS_FILE" && -s "$INSIGHTS_FILE" ]]; then
    echo "" >> "$OUT"
    if [[ "$LANG" == "ru" ]]; then
        echo "# Ключевые Инсайты" >> "$OUT"
    else
        echo "# Key Insights" >> "$OUT"
    fi
    echo "" >> "$OUT"
    cat "$INSIGHTS_FILE" >> "$OUT"
fi

# Add timestamp
echo "" >> "$OUT"
echo "---" >> "$OUT"
if [[ "$LANG" == "ru" ]]; then
    echo "*Сгенерировано: $(date '+%Y-%m-%d %H:%M')*" >> "$OUT"
else
    echo "*Generated: $(date '+%Y-%m-%d %H:%M')*" >> "$OUT"
fi

jq -n --arg path "$OUT" --argjson done "$DONE" --arg lang "$LANG" \
    '{status:"ok",path:$path,completedSessions:$done,lang:$lang}'
