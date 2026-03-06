#!/bin/bash
# Audit all installed OpenClaw skills
# Usage: bash audit-all.sh [skills-directory] [--json] [--allowlist /path/to/allowlist.json]

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
AUDIT="$SCRIPT_DIR/audit.sh"
DEFAULT_ALLOWLIST="$SCRIPT_DIR/allowlist.json"

SKILLS_DIR=""
JSON_MODE=false
ALLOWLIST_FILE=""

# Parse args
while [[ $# -gt 0 ]]; do
    case $1 in
        --json) JSON_MODE=true; shift ;;
        --allowlist) ALLOWLIST_FILE="$2"; shift 2 ;;
        *) SKILLS_DIR="$1"; shift ;;
    esac
done

SKILLS_DIR="${SKILLS_DIR:-/opt/homebrew/lib/node_modules/openclaw/skills}"

# Use default allowlist if none specified and default exists
if [ -z "$ALLOWLIST_FILE" ] && [ -f "$DEFAULT_ALLOWLIST" ]; then
    ALLOWLIST_FILE="$DEFAULT_ALLOWLIST"
fi

AUDIT_ARGS=""
if $JSON_MODE; then AUDIT_ARGS="$AUDIT_ARGS --json"; fi
if [ -n "$ALLOWLIST_FILE" ]; then AUDIT_ARGS="$AUDIT_ARGS --allowlist $ALLOWLIST_FILE"; fi

if ! $JSON_MODE; then
    echo "========================================="
    echo "  Skill Auditor - Batch Scan v3.0.0"
    echo "  Directory: $SKILLS_DIR"
    if [ -n "$ALLOWLIST_FILE" ]; then echo "  Allowlist: $ALLOWLIST_FILE"; fi
    echo "========================================="
    echo ""
fi

TOTAL=0
PASS=0
REVIEW=0
FAIL=0
JSON_RESULTS=""

for skill_dir in "$SKILLS_DIR"/*/; do
    if [ -d "$skill_dir" ]; then
        SKILL_NAME=$(basename "$skill_dir")
        ((TOTAL++))

        if $JSON_MODE; then
            RESULT=$(bash "$AUDIT" "$skill_dir" $AUDIT_ARGS 2>/dev/null)
            code=$?
            if [ -n "$JSON_RESULTS" ]; then JSON_RESULTS="$JSON_RESULTS,"; fi
            JSON_RESULTS="$JSON_RESULTS$RESULT"
        else
            echo "--- Auditing: $SKILL_NAME ---"
            bash "$AUDIT" "$skill_dir" $AUDIT_ARGS 2>/dev/null
            code=$?
            echo ""
        fi

        if [ $code -eq 0 ]; then
            ((PASS++))
        elif [ $code -eq 1 ]; then
            ((REVIEW++))
        elif [ $code -eq 2 ]; then
            ((FAIL++))
        fi
    fi
done

if $JSON_MODE; then
    echo "{\"total\":$TOTAL,\"pass\":$PASS,\"review\":$REVIEW,\"fail\":$FAIL,\"results\":[$JSON_RESULTS]}"
else
    echo "========================================="
    echo "  BATCH AUDIT COMPLETE"
    echo "========================================="
    echo "  Total skills: $TOTAL"
    echo -e "  Pass:         \033[0;32m$PASS\033[0m"
    echo -e "  Review:       \033[1;33m$REVIEW\033[0m"
    echo -e "  FAIL:         \033[0;31m$FAIL\033[0m"
    echo "========================================="
fi
