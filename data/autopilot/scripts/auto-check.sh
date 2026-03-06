#!/usr/bin/env bash
# auto-check.sh — Layer 1: Zero-LLM-cost automated checks
# Run after commits detected. Returns findings or empty if clean.
# Usage: auto-check.sh <project_dir> [--nudge]

set -euo pipefail

PROJECT_DIR="${1:?Usage: auto-check.sh <project_dir> [--nudge] [--issues-only]}"
shift || true
NUDGE=false
ISSUES_ONLY=false
while [ $# -gt 0 ]; do
    case "$1" in
        --nudge)
            NUDGE=true
            ;;
        --issues-only)
            ISSUES_ONLY=true
            ;;
        *)
            echo "Usage: auto-check.sh <project_dir> [--nudge] [--issues-only]" >&2
            exit 2
            ;;
    esac
    shift
done
TMUX="/opt/homebrew/bin/tmux"
FINDINGS=""

cd "$PROJECT_DIR" || exit 1

PROJECT_NAME=$(basename "$PROJECT_DIR")

add_finding() {
    if [ -n "$FINDINGS" ]; then
        FINDINGS="$FINDINGS\n$1"
    else
        FINDINGS="$1"
    fi
}

# --- TypeScript checks ---
if [ -f "tsconfig.json" ]; then
    # Type errors
    TSC_OUT=$(npx tsc --noEmit 2>&1 | tail -10) || true
    if echo "$TSC_OUT" | grep -q "error TS"; then
        ERR_COUNT=$(echo "$TSC_OUT" | grep -c "error TS" || echo "0")
        add_finding "🔴 TypeScript: ${ERR_COUNT} type errors"
    fi

    # ESLint (if configured)
    if [ -f ".eslintrc.js" ] || [ -f ".eslintrc.json" ] || [ -f "eslint.config.js" ] || [ -f ".eslintrc.cjs" ]; then
        LINT_OUT=$(npx eslint src/ --quiet --max-warnings=0 2>&1 | tail -10) || true
        if echo "$LINT_OUT" | grep -q "problem"; then
            add_finding "🟡 ESLint: $(echo "$LINT_OUT" | grep 'problem' | head -1)"
        fi
    fi
fi

# --- Swift checks ---
if [ -d "ios" ] || [ -f "Package.swift" ]; then
    if command -v swiftlint &>/dev/null; then
        SWIFT_OUT=$(swiftlint lint --quiet 2>&1 | tail -10) || true
        if [ -n "$SWIFT_OUT" ]; then
            SWIFT_COUNT=$(echo "$SWIFT_OUT" | wc -l | tr -d ' ')
            add_finding "🟡 SwiftLint: ${SWIFT_COUNT} warnings"
        fi
    fi
fi

# --- Dangerous patterns ---
DANGEROUS=$(grep -rn 'eval(\|\.innerHTML\s*=\|dangerouslySetInnerHTML\|child_process' src/ --include="*.ts" --include="*.tsx" 2>/dev/null | grep -v 'node_modules\|__tests__\|\.test\.\|\.spec\.' | head -5) || true
if [ -n "$DANGEROUS" ]; then
    add_finding "🔴 Dangerous pattern found:\n$DANGEROUS"
fi

# --- Hardcoded secrets ---
SECRETS=$(grep -rn 'api_key\s*=\s*["'"'"']\|apiKey\s*=\s*["'"'"']\|secret\s*=\s*["'"'"'].*[A-Za-z0-9]' src/ --include="*.ts" --include="*.tsx" 2>/dev/null | grep -vi 'test\|mock\|example\|type\|interface\|process\.env' | head -5) || true
if [ -n "$SECRETS" ]; then
    add_finding "🔴 Possible hardcoded secret:\n$SECRETS"
fi

# --- SRP violations (>500 lines) ---
BIG_FILES=$(find src/ -name "*.ts" -o -name "*.tsx" 2>/dev/null | xargs wc -l 2>/dev/null | awk '$1 > 500 && !/total/' | sort -rn | head -5) || true
if [ -n "$BIG_FILES" ]; then
    add_finding "🟡 Large files (SRP signal):\n$BIG_FILES"
fi

# --- Output ---
if [ -n "$FINDINGS" ]; then
    if [ "$ISSUES_ONLY" = "true" ]; then
        printf '%b\n' "$FINDINGS"
    else
        echo -e "⚠️ [$PROJECT_NAME] Auto-check findings:\n$FINDINGS"
    fi

    # Optionally nudge Codex to fix
    if [ "$NUDGE" = "true" ]; then
        SAFE_NAME=$(echo "$PROJECT_NAME" | tr -c 'a-zA-Z0-9_-' '_')
        WINDOW="autopilot:${SAFE_NAME}"

        # Only nudge if Codex is idle (has › prompt)
        PANE_CONTENT=$($TMUX capture-pane -t "$WINDOW" -p 2>/dev/null | tail -5) || true
        if echo "$PANE_CONTENT" | grep -q '›'; then
            MSG="修复以下自动检查发现的问题，然后继续当前任务：\n$(echo -e "$FINDINGS" | head -20)"
            bash ~/.autopilot/scripts/tmux-send.sh "$SAFE_NAME" "$MSG"
            echo "✅ Nudge sent to $WINDOW"
        fi
    fi
    exit 1
else
    if [ "$ISSUES_ONLY" != "true" ]; then
        echo "✅ [$PROJECT_NAME] Auto-check clean"
    fi
    exit 0
fi
