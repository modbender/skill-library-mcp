#!/bin/bash
# brew-audit.sh — Audit Homebrew installation for outdated, cleanup, and health issues
# Usage: brew-audit.sh [--json] [--section outdated|cleanup|doctor|all]

set -euo pipefail

JSON=false
SECTION="all"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --json) JSON=true; shift ;;
    --section) SECTION="$2"; shift 2 ;;
    *) echo "Usage: brew-audit.sh [--json] [--section outdated|cleanup|doctor|all]"; exit 1 ;;
  esac
done

if ! command -v brew &>/dev/null; then
  echo "Error: Homebrew not installed" >&2
  exit 1
fi

# Outdated packages
if [[ "$SECTION" == "all" || "$SECTION" == "outdated" ]]; then
  if $JSON; then
    echo '{"section":"outdated","packages":'
    brew outdated --json 2>/dev/null || echo '[]'
    echo '}'
  else
    echo "📦 OUTDATED PACKAGES"
    echo "===================="
    OUTDATED=$(brew outdated --verbose 2>/dev/null)
    if [[ -z "$OUTDATED" ]]; then
      echo "  ✅ All packages up to date"
    else
      echo "$OUTDATED" | while read -r line; do
        echo "  ⚠️  $line"
      done
      echo ""
      COUNT=$(echo "$OUTDATED" | wc -l | tr -d ' ')
      echo "  Total: $COUNT outdated"
    fi
    echo ""
  fi
fi

# Cleanup opportunities
if [[ "$SECTION" == "all" || "$SECTION" == "cleanup" ]]; then
  if ! $JSON; then
    echo "🧹 CLEANUP OPPORTUNITIES"
    echo "========================"
    CLEANUP=$(brew cleanup --dry-run 2>/dev/null)
    if [[ -z "$CLEANUP" ]]; then
      echo "  ✅ Nothing to clean"
    else
      BYTES=$(brew cleanup --dry-run 2>/dev/null | tail -1 | grep -o '[0-9.]*[KMGT]*B' || echo "unknown")
      COUNT=$(echo "$CLEANUP" | grep -c "Would remove" || echo "0")
      echo "  🗑️  $COUNT items removable (~$BYTES)"
      echo "  Run: brew cleanup"
    fi
    echo ""
  fi
fi

# Doctor check
if [[ "$SECTION" == "all" || "$SECTION" == "doctor" ]]; then
  if ! $JSON; then
    echo "🩺 HEALTH CHECK"
    echo "==============="
    DOCTOR=$(brew doctor 2>&1 || true)
    if echo "$DOCTOR" | grep -q "ready to brew"; then
      echo "  ✅ Your system is ready to brew"
    else
      echo "$DOCTOR" | head -20 | while read -r line; do
        echo "  ⚠️  $line"
      done
    fi
    echo ""
  fi
fi

# Summary
if ! $JSON && [[ "$SECTION" == "all" ]]; then
  TOTAL=$(brew list --formula | wc -l | tr -d ' ')
  CASKS=$(brew list --cask | wc -l | tr -d ' ')
  echo "📊 SUMMARY"
  echo "=========="
  echo "  Formulae: $TOTAL"
  echo "  Casks: $CASKS"
  echo "  Prefix: $(brew --prefix)"
fi
