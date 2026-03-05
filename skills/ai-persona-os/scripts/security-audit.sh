#!/usr/bin/env bash
# security-audit.sh — Local workspace credential scanner
# Part of AI Persona OS by Jeff J Hunter
#
# This script scans your workspace for accidentally leaked credentials.
# It runs ONLY local grep checks. No network calls. No file modifications.
# Safe to run anytime. Run monthly as part of your security routine.
#
# Usage: bash scripts/security-audit.sh
# Or:    ./scripts/security-audit.sh (if executable)

set -euo pipefail

WORKSPACE="${1:-$HOME/workspace}"
ISSUES=0

echo "━━━ AI Persona OS — Security Audit ━━━"
echo "Scanning: $WORKSPACE"
echo "Date:     $(date '+%Y-%m-%d %H:%M')"
echo ""

# 1. Check for leaked credentials in workspace files
echo "🔍 Checking for leaked credentials..."
CRED_PATTERNS='api_key|secret_key|access_token|private_key|password=|passwd=|auth_token|bearer [a-zA-Z0-9]|sk-[a-zA-Z0-9]{20,}|ghp_[a-zA-Z0-9]{36}|xoxb-|xoxp-'

MATCHES=$(grep -rniE "$CRED_PATTERNS" "$WORKSPACE" \
  --include="*.md" --include="*.json" --include="*.yaml" --include="*.yml" --include="*.txt" \
  --exclude-dir=".git" --exclude-dir="node_modules" \
  2>/dev/null | grep -v "SECURITY" | grep -v "KNOWLEDGE" | grep -v "template" | grep -v "example" || true)

if [ -n "$MATCHES" ]; then
  echo "⚠️  Potential credentials found:"
  echo "$MATCHES" | head -20
  ISSUES=$((ISSUES + 1))
else
  echo "✅ No leaked credentials detected"
fi
echo ""

# 2. Check for overly permissive file permissions
echo "🔍 Checking file permissions..."
WORLD_READABLE=$(find "$WORKSPACE" -type f \( -name "*.json" -o -name "*.env" \) -perm -o=r 2>/dev/null || true)

if [ -n "$WORLD_READABLE" ]; then
  COUNT=$(echo "$WORLD_READABLE" | wc -l | tr -d ' ')
  echo "⚠️  $COUNT config/env files are world-readable"
  ISSUES=$((ISSUES + 1))
else
  echo "✅ File permissions look good"
fi
echo ""

# 3. Check SOUL.md for injection patterns
echo "🔍 Checking SOUL.md for injection patterns..."
if [ -f "$WORKSPACE/SOUL.md" ]; then
  INJECTION=$(grep -niE 'ignore previous|ignore all|system prompt|disregard|new instructions' "$WORKSPACE/SOUL.md" 2>/dev/null || true)
  if [ -n "$INJECTION" ]; then
    echo "⚠️  Suspicious patterns in SOUL.md:"
    echo "$INJECTION"
    ISSUES=$((ISSUES + 1))
  else
    echo "✅ SOUL.md looks clean"
  fi
else
  echo "ℹ️  No SOUL.md found (OK if not yet set up)"
fi
echo ""

# 4. Check MEMORY.md size (bloat = context risk)
echo "🔍 Checking MEMORY.md size..."
if [ -f "$WORKSPACE/MEMORY.md" ]; then
  SIZE=$(wc -c < "$WORKSPACE/MEMORY.md")
  if [ "$SIZE" -gt 8192 ]; then
    echo "⚠️  MEMORY.md is $(( SIZE / 1024 ))KB — consider pruning (recommended: under 4KB)"
    ISSUES=$((ISSUES + 1))
  else
    echo "✅ MEMORY.md size is healthy ($(( SIZE / 1024 ))KB)"
  fi
else
  echo "ℹ️  No MEMORY.md found"
fi
echo ""

# Summary
echo "━━━ Audit Complete ━━━━━━━━━━━━━━━━━━"
if [ "$ISSUES" -eq 0 ]; then
  echo "✅ No issues found. Workspace looks secure."
else
  echo "⚠️  $ISSUES issue(s) found. Review above and address."
fi
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
