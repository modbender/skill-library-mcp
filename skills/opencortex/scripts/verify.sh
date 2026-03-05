#!/bin/bash
# OpenCortex — Verify installation is working correctly
# Run from your OpenClaw workspace directory: bash skills/opencortex/scripts/verify.sh

set -euo pipefail
WORKSPACE="${CLAWD_WORKSPACE:-$(pwd)}"
PASS=0
FAIL=0
WARN=0

echo "🔍 OpenCortex Installation Verification"
INSTALLED_VER="unknown"
[ -f "$WORKSPACE/.opencortex-version" ] && INSTALLED_VER="v$(cat "$WORKSPACE/.opencortex-version" | tr -d '[:space:]')"
echo "   Workspace: $WORKSPACE"
echo "   Version:   $INSTALLED_VER"
echo ""

check() {
  local label="$1"
  local result="$2"
  if [ "$result" = "ok" ]; then
    echo "   ✅ $label"
    PASS=$((PASS + 1))
  elif [ "$result" = "warn" ]; then
    echo "   ⚠️  $label"
    WARN=$((WARN + 1))
  else
    echo "   ❌ $label"
    FAIL=$((FAIL + 1))
  fi
}

# --- Core files ---
echo "📁 Core files:"
for f in MEMORY.md SOUL.md USER.md TOOLS.md INFRA.md BOOTSTRAP.md AGENTS.md; do
  if [ -f "$WORKSPACE/$f" ]; then
    check "$f exists" "ok"
  else
    check "$f missing" "fail"
  fi
done
echo ""

# --- Directories ---
echo "📂 Directories:"
for d in memory memory/projects memory/runbooks memory/contacts memory/workflows memory/archive; do
  if [ -d "$WORKSPACE/$d" ]; then
    check "$d/ exists" "ok"
  else
    check "$d/ missing" "fail"
  fi
done
echo ""

# --- Voice profile ---
echo "🎙️ Voice profile:"
if [ -f "$WORKSPACE/memory/VOICE.md" ]; then
  check "VOICE.md exists (voice profiling enabled)" "ok"
else
  check "VOICE.md not found (voice profiling not enabled — this is fine if you skipped it)" "warn"
fi
echo ""

# --- Cron jobs ---
echo "⏰ Cron jobs:"
if command -v openclaw &>/dev/null; then
  CRON_LIST=$(openclaw cron list 2>/dev/null || echo "")
  if echo "$CRON_LIST" | grep -qi "distill"; then
    check "Daily Memory Distillation cron found" "ok"
  else
    check "Daily Memory Distillation cron NOT found" "fail"
  fi
  if echo "$CRON_LIST" | grep -qi "synth"; then
    check "Weekly Synthesis cron found" "ok"
  else
    check "Weekly Synthesis cron NOT found" "fail"
  fi
  # Check for problematic model overrides (models that don't exist)
  CRON_JSON=$(openclaw cron list --json 2>/dev/null || echo "")
  if [ -n "$CRON_JSON" ]; then
    BAD_MODELS=$(echo "$CRON_JSON" | grep -o '"model":\s*"[^"]*"' | grep -iE '"(anthropic/default|default)"' || true)
    if [ -n "$BAD_MODELS" ]; then
      check "Cron jobs have invalid model overrides (e.g. 'default' is not a real model)" "warn"
    else
      check "No invalid model overrides in crons" "ok"
    fi
  fi
else
  check "openclaw CLI not found — cannot verify cron jobs" "fail"
fi
echo ""

# --- Principles ---
echo "📜 Principles:"
if [ -f "$WORKSPACE/MEMORY.md" ]; then
  P_COUNT=$(grep -c "^### P[0-9]" "$WORKSPACE/MEMORY.md" 2>/dev/null || true)
  P_COUNT=$(printf '%s' "$P_COUNT" | tr -dc '0-9')
  P_COUNT=${P_COUNT:-0}
  if [ "$P_COUNT" -ge 7 ]; then
    check "$P_COUNT principles found in MEMORY.md" "ok"
  elif [ "$P_COUNT" -ge 1 ]; then
    check "Only $P_COUNT principles found (expected 7+)" "warn"
  else
    check "No principles found in MEMORY.md" "fail"
  fi
  # Context budget: check MEMORY.md size
  MEM_SIZE=$(wc -c < "$WORKSPACE/MEMORY.md" 2>/dev/null | tr -d ' ')
  MEM_KB=$(( MEM_SIZE / 1024 ))
  if [ "$MEM_SIZE" -le 3072 ]; then
    check "MEMORY.md size: ${MEM_KB}KB (within 3KB budget)" "ok"
  elif [ "$MEM_SIZE" -le 5120 ]; then
    check "MEMORY.md size: ${MEM_KB}KB (over 3KB target — consider moving verbose content to project/memory files)" "warn"
  else
    check "MEMORY.md size: ${MEM_KB}KB (well over 3KB — loaded every session, move content to dedicated files)" "warn"
  fi
else
  check "MEMORY.md not found" "fail"
fi
echo ""

# --- Gitignore ---
echo "🔒 Security:"
if [ -f "$WORKSPACE/.gitignore" ]; then
  if grep -q "^\.vault/" "$WORKSPACE/.gitignore" 2>/dev/null; then
    check ".vault/ is gitignored" "ok"
  else
    check ".vault/ is NOT gitignored" "warn"
  fi
  if grep -q "^\.secrets-map" "$WORKSPACE/.gitignore" 2>/dev/null; then
    check ".secrets-map is gitignored" "ok"
  else
    check ".secrets-map is NOT gitignored" "warn"
  fi
else
  check "No .gitignore found" "warn"
fi
echo ""

# --- Memory Search ---
echo "🔍 Memory Search:"
if command -v openclaw >/dev/null 2>&1; then
  # Check if memory_search is functional by looking for the memory index
  MEM_DB=$(find "$HOME/.openclaw" -name "memory*.sqlite" -o -name "memory*.db" 2>/dev/null | head -1)
  if [ -n "$MEM_DB" ]; then
    DB_SIZE=$(du -k "$MEM_DB" 2>/dev/null | cut -f1)
    check "Memory search index exists (${DB_SIZE}KB)" "ok"
  else
    check "No memory search index (optional — see docs.openclaw.ai/concepts/memory)" "ok"
  fi

  # Check if memory files are being indexed (non-empty memory dir)
  MEM_FILES=$(find "$WORKSPACE/memory" -name "*.md" -type f 2>/dev/null | wc -l | tr -d ' ')
  if [ "$MEM_FILES" -gt 0 ]; then
    check "$MEM_FILES memory files available for indexing" "ok"
  else
    check "No memory files found in memory/" "warn"
  fi

  # Check MEMORY.md size (should stay small for boot performance)
  if [ -f "$WORKSPACE/MEMORY.md" ]; then
    MEM_SIZE=$(du -k "$WORKSPACE/MEMORY.md" 2>/dev/null | cut -f1)
    if [ "$MEM_SIZE" -le 5 ]; then
      check "MEMORY.md is ${MEM_SIZE}KB (target: < 5KB)" "ok"
    elif [ "$MEM_SIZE" -le 10 ]; then
      check "MEMORY.md is ${MEM_SIZE}KB — consider trimming (target: < 5KB)" "warn"
    else
      check "MEMORY.md is ${MEM_SIZE}KB — too large, will slow boot (target: < 5KB)" "fail"
    fi
  fi
else
  check "openclaw not in PATH — cannot verify memory search" "warn"
fi
echo ""

# --- Vault ---
echo "🔐 Vault:"
if [ -f "$WORKSPACE/scripts/vault.sh" ]; then
  check "vault.sh installed" "ok"
  BACKEND=$(bash "$WORKSPACE/scripts/vault.sh" backend 2>/dev/null | head -1 || echo "unknown")
  check "Passphrase backend: $BACKEND" "ok"
else
  check "vault.sh not installed (vault feature not enabled — this is fine if you skipped it)" "warn"
fi
echo ""

# --- Summary ---
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "   ✅ Passed: $PASS"
echo "   ⚠️  Warnings: $WARN"
echo "   ❌ Failed: $FAIL"
echo ""

if [ "$FAIL" -eq 0 ]; then
  echo "🎉 OpenCortex is installed and ready!"
  echo "   Work normally — the nightly distillation will start organizing your knowledge automatically."
else
  echo "⚠️  Some checks failed. Re-run the installer:"
  echo "   cd $WORKSPACE && bash skills/opencortex/scripts/install.sh"
fi
