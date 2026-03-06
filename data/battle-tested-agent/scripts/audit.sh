#!/usr/bin/env bash
set -uo pipefail

WORKSPACE="${1:-$HOME/workspace}"
SCORE=0
TOTAL=16
MISSING=()

found() {
  grep -rql "$1" "${@:2}" 2>/dev/null
}

check() {
  local name="$1" result="$2"
  if [ "$result" = "yes" ]; then
    printf "  ✅ %-28s" "$name"
    ((SCORE++)) || true
  else
    printf "  ❌ %-28s" "$name"
    MISSING+=("$name")
  fi
}

echo ""
echo "⚔️ Battle-Tested Agent — Workspace Audit"
echo "   Workspace: $WORKSPACE"
echo ""

# --- Starter ---
echo "🟢 Starter"

r="no"; found 'WAL Protocol' "$WORKSPACE/SOUL.md" "$WORKSPACE/AGENTS.md" && r="yes"
check "WAL Protocol" "$r"

r="no"; found 'Anti-Hallucination' "$WORKSPACE/HEARTBEAT.md" "$WORKSPACE/SOUL.md" "$WORKSPACE/AGENTS.md" && r="yes"
check "Anti-Hallucination" "$r"
echo ""

r="no"; grep -qi 'Ambiguity Gate\|multiple reasonable interpretations' "$WORKSPACE/SOUL.md" "$WORKSPACE/AGENTS.md" 2>/dev/null && r="yes"
check "Ambiguity Gate" "$r"

r="no"; grep -qi 'simple path first\|simplest.*approach' "$WORKSPACE/SOUL.md" 2>/dev/null && r="yes"
check "Simple Path First" "$r"

r="no"; grep -qi 'unblock.*shelve' "$WORKSPACE/SOUL.md" "$WORKSPACE/AGENTS.md" 2>/dev/null && r="yes"
check "Unblock Before Shelve" "$r"
echo ""

# --- Intermediate ---
echo "🟡 Intermediate"

r="no"; found 'No command.*no number\|Verification Rule' "$WORKSPACE/SOUL.md" "$WORKSPACE/AGENTS.md" && r="yes"
[ "$r" = "no" ] && found 'No command.*no number\|Verification Rule' "$WORKSPACE"/memory/agents/*.md 2>/dev/null && r="yes"
check "Agent Verification" "$r"

r="no"; [ -f "$WORKSPACE/memory/working-buffer.md" ] && r="yes"
check "Working Buffer" "$r"
echo ""

r="no"; [ -f "$WORKSPACE/QA.md" ] && r="yes"
check "QA Gates" "$r"

r="no"; found 'Decision.*Reasoning\|Decision.*Log' "$WORKSPACE/SOUL.md" "$WORKSPACE/AGENTS.md" && r="yes"
check "Decision Logs" "$r"
echo ""

r="no"; found 'Verify Implementation' "$WORKSPACE/SOUL.md" "$WORKSPACE/AGENTS.md" "$WORKSPACE/QA.md" && r="yes"
check "Verify Implementation" "$r"
echo ""

# --- Advanced ---
echo "🔴 Advanced"

r="no"; found 'Delegation' "$WORKSPACE/AGENTS.md" && r="yes"
check "Delegation Rules" "$r"

r="no"; found 'Handoff Template\|5-Point' "$WORKSPACE/AGENTS.md" && r="yes"
check "Handoff Template" "$r"
echo ""

r="no"; found 'Orchestrator.*build\|orchestrator.*build' "$WORKSPACE/SOUL.md" "$WORKSPACE/AGENTS.md" && r="yes"
check "Orchestrator Rule" "$r"

r="no"; found 'Task State Tracking\|Spawned.*In Progress' "$WORKSPACE/AGENTS.md" && r="yes"
check "Task State Tracking" "$r"
echo ""

r="no"; found 'Compaction.*Injection\|INERT DATA' "$WORKSPACE/SOUL.md" && r="yes"
check "Compaction Hardening" "$r"

r="no"; [ -d "$WORKSPACE/.learnings" ] && r="yes"
check "Self-Improvement" "$r"
echo ""

# --- Summary ---
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Score: $SCORE/$TOTAL patterns"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ ${#MISSING[@]} -gt 0 ]; then
  echo ""
  echo "  Missing:"
  for m in "${MISSING[@]}"; do
    echo "    → $m"
  done
  echo ""
  echo "  Start with: ${MISSING[0]}"
fi

echo ""
