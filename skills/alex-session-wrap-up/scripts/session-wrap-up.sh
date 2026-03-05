#!/usr/bin/env bash
# session-wrap-up.sh - End-of-session automation (lightweight)
# Phase 1: Ship It | Phase 2: Extract | Phase 3: Pattern Detect | Phase 4: Persist
set -euo pipefail

WORKSPACE="/home/xbill/.openclaw/workspace"
MEMORY_DIR="$WORKSPACE/memory"
TODAY=$(date +%Y-%m-%d)
MEMORY_FILE="$MEMORY_DIR/${TODAY}.md"
MODEL="gpt-4o-mini"

# Load env
if [[ -f "$WORKSPACE/../.env" ]]; then
  set -a
  source "$WORKSPACE/../.env"
  set +a
fi

echo "=== Session Wrap-Up ==="
echo "Date: $TODAY"
echo ""

# ============================================================
# Phase 1: Ship It (selective - text/config files only)
# ============================================================
echo "📦 Phase 1: Ship It"
echo "-------------------"

cd "$WORKSPACE"

# Only commit text/config files, skip binaries and media
if git rev-parse --git-dir >/dev/null 2>&1; then
  # Add only text/config files
  git add *.md *.txt *.json *.sh *.yaml *.yml *.env 2>/dev/null || true
  git add docs/* scripts/* skills/* memory/* 2>/dev/null || true
  git add AGENTS.md USER.md SOUL.md MEMORY.md TOOLS.md 2>/dev/null || true
  git add projects/*/README.md projects/*/notes/* 2>/dev/null || true
  
  if [[ -n "$(git status --porcelain 2>/dev/null)" ]]; then
    echo "Committing text/config changes..."
    git commit -m "Auto-wrap-up: $(date -Iseconds)" 2>/dev/null || true
    if git remote get-url origin >/dev/null 2>&1; then
      git push origin HEAD 2>/dev/null && echo "  ✓ Pushed to origin" || echo "  ⚠ Push failed"
    fi
  else
    echo "  ✓ No text/config changes to commit"
  fi
else
  echo "  ⚠ Not a git repo"
fi
echo ""

# ============================================================
# Phase 2: Extract Learnings
# ============================================================
echo "📝 Phase 2: Extract Learnings"
echo "-------------------------------"

LEARNINGS=""
if [[ -f "$MEMORY_FILE" ]]; then
  LEARNINGS=$(grep -E '^- ' "$MEMORY_FILE" 2>/dev/null | head -20 || true)
  echo "Found memory entries:"
  echo "$LEARNINGS"
else
  echo "  No memory file for today"
fi
echo ""

# ============================================================
# Phase 3: Pattern Detect (gpt-4o-mini) - with timeout
# ============================================================
echo "🔍 Phase 3: Pattern Detect (gpt-4o-mini)"
echo "-----------------------------------------"

PROMPT="You are a pattern detection assistant. Analyze the following memory entries from today and find:

1. Repeated questions or requests
2. Things the user had to ask about repeatedly
3. Automation opportunities

Memory entries:
$LEARNINGS

Respond in this format:
PATTERNS:
- [pattern or 'No significant patterns']

AUTOMATION_SUGGESTIONS:
- [suggestion or 'None']"

PATTERN_RESULT=""

if [[ -n "$LEARNINGS" && -n "${OPENAI_API_KEY:-}" ]]; then
  PATTERN_RESULT=$(curl -sS --max-time 30 "https://api.openai.com/v1/chat/completions" \
    -H "Authorization: Bearer $OPENAI_API_KEY" \
    -H "Content-Type: application/json" \
    -d "{\"model\": \"$MODEL\", \"messages\": [{\"role\": \"user\", \"content\": \"$PROMPT\"}], \"max_tokens\": 300}" \
    2>/dev/null | python3 -c 'import sys,json; d=json.load(sys.stdin); print(d.get("choices",[{}])[0].get("message",{}).get("content","Error"))') \
    || PATTERN_RESULT="API error"
elif [[ -n "$LEARNINGS" && -n "${OPENROUTER_API_KEY:-}" ]]; then
  PATTERN_RESULT=$(curl -sS --max-time 30 "https://openrouter.ai/api/chat/v1/chat/completions" \
    -H "Authorization: Bearer $OPENROUTER_API_KEY" \
    -H "Content-Type: application/json" \
    -d "{\"model\": \"openai/gpt-4o-mini\", \"messages\": [{\"role\": \"user\", \"content\": \"$PROMPT\"}], \"max_tokens\": 300}" \
    2>/dev/null | python3 -c 'import sys,json; d=json.load(sys.stdin); print(d.get("choices",[{}])[0].get("message",{}).get("content","Error"))') \
    || PATTERN_RESULT="API error"
elif [[ -n "$LEARNINGS" ]]; then
  echo "  ⚠ No API key found, skipping pattern detection"
else
  echo "  ℹ No learnings to analyze"
fi

if [[ -n "$PATTERN_RESULT" && "$PATTERN_RESULT" != "API error" && "$PATTERN_RESULT" != "Error" ]]; then
  echo "$PATTERN_RESULT"
fi
echo ""

# ============================================================
# Phase 4: Persist & Evolve
# ============================================================
echo "💾 Phase 4: Persist & Evolve"
echo "-----------------------------"

if [[ -n "$PATTERN_RESULT" && "$PATTERN_RESULT" != "API error" && "$PATTERN_RESULT" != "Error" && "$PATTERN_RESULT" != "No significant patterns" ]]; then
  echo "Patterns detected, logging..."
  echo "" >> "$MEMORY_FILE"
  echo "### Wrap-up Patterns ($TODAY)" >> "$MEMORY_FILE"
  echo "$PATTERN_RESULT" >> "$MEMORY_FILE"
  echo "  ✓ Patterns saved"
else
  echo "  ✓ No new patterns to persist"
fi

echo ""
echo "=== Wrap-Up Complete ==="
