#!/usr/bin/env bash
# safe-merge-update: Post-merge validation
set -euo pipefail

REPO_DIR="${REPO_DIR:?REPO_DIR must be set to your OpenClaw repo path}"
MANIFEST="${MANIFEST:-$(dirname "$0")/../MERGE_MANIFEST.json}"
REPORT_DIR="/tmp/safe-merge"
REPORT="$REPORT_DIR/validation-report.json"
ERRORS=()
WARNINGS=()

mkdir -p "$REPORT_DIR"
cd "$REPO_DIR"

echo "=== Post-Merge Validation ==="
echo ""

# ─── Check 1: pnpm install ───
echo ">>> Check 1: pnpm install (--ignore-scripts for safety)..."
if pnpm install --frozen-lockfile --ignore-scripts 2>&1 | tail -5; then
  echo "✅ pnpm install succeeded"
elif pnpm install --ignore-scripts 2>&1 | tail -5; then
  echo "⚠️  pnpm install succeeded (lockfile updated)"
  WARNINGS+=("pnpm lockfile was updated during install")
else
  echo "❌ pnpm install failed"
  ERRORS+=("pnpm install failed")
fi

# ─── Check 2: pnpm build ───
echo ""
echo ">>> Check 2: pnpm build..."
if pnpm build 2>&1 | tail -10; then
  echo "✅ Build succeeded"
else
  echo "❌ Build FAILED"
  ERRORS+=("pnpm build failed — TypeScript compilation errors")
fi

# ─── Check 3: pnpm ui:build ───
echo ""
echo ">>> Check 3: pnpm ui:build..."
if pnpm ui:build 2>&1 | tail -5; then
  echo "✅ UI build succeeded"
else
  echo "❌ UI build FAILED"
  ERRORS+=("pnpm ui:build failed")
fi

# ─── Check 4: Protected tabs in navigation.ts ───
echo ""
echo ">>> Check 4: Protected tabs in navigation.ts..."
NAV_FILE="ui/src/ui/navigation.ts"
REQUIRED_TABS=("jarvis" "mode" "usage" "memory" "agents" "sessions" "discord" "1password" "pipedream" "zapier")
for tab in "${REQUIRED_TABS[@]}"; do
  if grep -q "\"$tab\"" "$NAV_FILE" 2>/dev/null; then
    echo "  ✅ Tab '$tab' present"
  else
    echo "  ❌ Tab '$tab' MISSING"
    ERRORS+=("Tab '$tab' missing from navigation.ts")
  fi
done

# ─── Check 5: Protected files exist ───
echo ""
echo ">>> Check 5: Protected files from manifest..."
if [[ -f "$MANIFEST" ]]; then
  while IFS= read -r pf; do
    [[ -z "$pf" ]] && continue
    if [[ -f "$pf" ]]; then
      echo "  ✅ $pf"
    else
      echo "  ❌ MISSING: $pf"
      ERRORS+=("Protected file missing: $pf")
    fi
  done < <(python3 -c "
import json, sys
with open('$MANIFEST') as f:
    m = json.load(f)
for path in m.get('protectedFiles', {}):
    print(path)
" 2>/dev/null)
fi

# ─── Check 6: Custom new files still exist ───
echo ""
echo ">>> Check 6: Custom new files..."
NEW_FILES=(
  "ui/src/ui/views/jarvis-view.ts"
  "ui/src/ui/views/memory.ts"
  "ui/src/ui/views/mode.ts"
  "ui/src/ui/views/sessions-history-modal.ts"
  "ui/src/ui/plugins/registry.ts"
  "ui/src/ui/controllers/mode.ts"
)
for nf in "${NEW_FILES[@]}"; do
  if [[ -f "$nf" ]]; then
    echo "  ✅ $nf"
  else
    echo "  ❌ MISSING: $nf"
    ERRORS+=("Custom file deleted: $nf")
  fi
done

# ─── Check 7: Must-preserve patterns ───
echo ""
echo ">>> Check 7: Must-preserve patterns..."
declare -A CRITICAL_PATTERNS
CRITICAL_PATTERNS=(
  ["uiPluginRegistry"]="ui/src/ui/plugins/registry.ts"
  ["BackgroundJobToast"]="ui/src/ui/app-view-state.ts"
  ["backgroundJobToasts"]="ui/src/ui/app-view-state.ts"
  ["compactionStatus"]="ui/src/ui/app-view-state.ts"
  ["renderMemory"]="ui/src/ui/app-render.ts"
  ["renderMode"]="ui/src/ui/app-render.ts"
  ["jarvis-view"]="ui/src/ui/app-render.ts"
  ["loadModeStatus"]="ui/src/ui/app-settings.ts"
  ["loadArchivedSessions"]="ui/src/ui/app-settings.ts"
)
for pattern in "${!CRITICAL_PATTERNS[@]}"; do
  file="${CRITICAL_PATTERNS[$pattern]}"
  if grep -q "$pattern" "$file" 2>/dev/null; then
    echo "  ✅ '$pattern' in $file"
  else
    echo "  ❌ '$pattern' NOT FOUND in $file"
    ERRORS+=("Pattern '$pattern' missing from $file")
  fi
done

# ─── Check 8: Plugin registry export ───
echo ""
echo ">>> Check 8: Plugin registry export..."
if grep -q "export const uiPluginRegistry" "ui/src/ui/plugins/registry.ts" 2>/dev/null; then
  echo "  ✅ uiPluginRegistry exported"
else
  echo "  ❌ uiPluginRegistry export missing"
  ERRORS+=("uiPluginRegistry export missing from plugins/registry.ts")
fi

# ─── Summary ───
echo ""
echo "=== Validation Summary ==="
ERROR_COUNT=${#ERRORS[@]}
WARN_COUNT=${#WARNINGS[@]}

if [[ "$ERROR_COUNT" -eq 0 ]]; then
  echo "✅ ALL CHECKS PASSED ($WARN_COUNT warnings)"
  STATUS="pass"
else
  echo "❌ $ERROR_COUNT ERRORS, $WARN_COUNT WARNINGS"
  STATUS="fail"
  echo ""
  echo "Errors:"
  for e in "${ERRORS[@]}"; do
    echo "  ❌ $e"
  done
fi

if [[ "$WARN_COUNT" -gt 0 ]]; then
  echo ""
  echo "Warnings:"
  for w in "${WARNINGS[@]}"; do
    echo "  ⚠️  $w"
  done
fi

# ─── Write JSON report ───
python3 - <<PYEOF
import json
errors = ${ERRORS[@]+"$(printf '"%s",' "${ERRORS[@]}" | sed 's/,$//; s/,/","/g')"}
warnings = ${WARNINGS[@]+"$(printf '"%s",' "${WARNINGS[@]}" | sed 's/,$//; s/,/","/g')"}
report = {
    "status": "$STATUS",
    "errorCount": $ERROR_COUNT,
    "warningCount": $WARN_COUNT,
    "errors": [e for e in """${ERRORS[*]:-}""".split("\n") if e] if $ERROR_COUNT > 0 else [],
    "warnings": [w for w in """${WARNINGS[*]:-}""".split("\n") if w] if $WARN_COUNT > 0 else [],
}
with open("$REPORT", "w") as f:
    json.dump(report, f, indent=2)
print(f"Report written to $REPORT")
PYEOF

echo ""
echo "=== Validation Complete ==="
exit "$ERROR_COUNT"
