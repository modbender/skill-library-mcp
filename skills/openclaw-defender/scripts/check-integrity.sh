#!/bin/bash
# File Integrity Monitoring for OpenClaw Workspace
# Checks critical files for unauthorized modifications
# Set OPENCLAW_WORKSPACE to override default (e.g. for multi-agent).

WORKSPACE="${OPENCLAW_WORKSPACE:-$HOME/.openclaw/workspace}"
cd "$WORKSPACE" || exit 1

CRITICAL_FILES=(
  "SOUL.md"
  "MEMORY.md"
  "IDENTITY.md"
  "USER.md"
  ".agent-private-key-SECURE"
  "AGENTS.md"
  "HEARTBEAT.md"
  ".defender-network-whitelist"
  ".defender-safe-commands"
  ".defender-rag-allowlist"
)

VIOLATIONS=0
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

echo "=== File Integrity Check: $TIMESTAMP ==="

# Verify integrity-of-integrity: .integrity/ must match stored manifest
if [ -f ".integrity-manifest.sha256" ]; then
  CURRENT_MANIFEST=$(find .integrity -type f -name '*.sha256' 2>/dev/null | sort | xargs cat 2>/dev/null | sha256sum | cut -d' ' -f1)
  STORED_MANIFEST=$(cat .integrity-manifest.sha256 2>/dev/null | tr -d '[:space:]')
  if [ -n "$STORED_MANIFEST" ] && [ "$CURRENT_MANIFEST" != "$STORED_MANIFEST" ]; then
    echo "🚨 VIOLATION: Integrity baselines tampered (.integrity/ does not match manifest)!"
    VIOLATIONS=$((VIOLATIONS + 1))
    echo "## Integrity baseline tampering" >> memory/security-incidents.md
    echo "**Date:** $TIMESTAMP" >> memory/security-incidents.md
    echo "**Action:** Re-run generate-baseline.sh from a known-good state; investigate who changed .integrity/" >> memory/security-incidents.md
    echo "" >> memory/security-incidents.md
  fi
elif [ -d ".integrity" ] && [ -n "$(find .integrity -type f -name '*.sha256' 2>/dev/null)" ]; then
  echo "⚠️  WARNING: No .integrity-manifest.sha256 (run generate-baseline.sh to create it)"
  VIOLATIONS=$((VIOLATIONS + 1))
fi

# Check core files
for file in "${CRITICAL_FILES[@]}"; do
  if [ -f "$file" ]; then
    CURRENT=$(sha256sum "$file" | cut -d' ' -f1)
    BASELINE=$(cat ".integrity/$file.sha256" 2>/dev/null | cut -d' ' -f1)
    
    if [ -z "$BASELINE" ]; then
      echo "⚠️  WARNING: No baseline for $file (run initial hash generation)"
      VIOLATIONS=$((VIOLATIONS + 1))
    elif [ "$CURRENT" != "$BASELINE" ]; then
      echo "🚨 VIOLATION: $file modified without authorization!"
      echo "   Current:  $CURRENT"
      echo "   Baseline: $BASELINE"
      VIOLATIONS=$((VIOLATIONS + 1))
      
      # Log to security incidents
      echo "## File Integrity Violation: $file" >> memory/security-incidents.md
      echo "**Date:** $TIMESTAMP" >> memory/security-incidents.md
      echo "**File:** $file" >> memory/security-incidents.md
      echo "**Current Hash:** $CURRENT" >> memory/security-incidents.md
      echo "**Baseline Hash:** $BASELINE" >> memory/security-incidents.md
      echo "**Action Required:** Review changes and update baseline if legitimate" >> memory/security-incidents.md
      echo "" >> memory/security-incidents.md
    fi
  fi
done

# Check skill files
find skills/ -name "SKILL.md" -type f | while read -r skill; do
  HASH_FILE=".integrity/$(echo "$skill" | tr / _).sha256"
  if [ -f "$HASH_FILE" ]; then
    CURRENT=$(sha256sum "$skill" | cut -d' ' -f1)
    BASELINE=$(cat "$HASH_FILE" | cut -d' ' -f1)
    
    if [ "$CURRENT" != "$BASELINE" ]; then
      echo "🚨 VIOLATION: $skill modified!"
      echo "   Current:  $CURRENT"
      echo "   Baseline: $BASELINE"
      VIOLATIONS=$((VIOLATIONS + 1))
      
      # Log to security incidents
      echo "## Skill Modification: $skill" >> memory/security-incidents.md
      echo "**Date:** $TIMESTAMP" >> memory/security-incidents.md
      echo "**Skill:** $skill" >> memory/security-incidents.md
      echo "**Current Hash:** $CURRENT" >> memory/security-incidents.md
      echo "**Baseline Hash:** $BASELINE" >> memory/security-incidents.md
      echo "**Risk:** CRITICAL - Skill may be poisoned" >> memory/security-incidents.md
      echo "**Action:** Quarantine skill and investigate" >> memory/security-incidents.md
      echo "" >> memory/security-incidents.md
    fi
  fi
done

if [ $VIOLATIONS -gt 0 ]; then
  echo ""
  echo "⚠️  $VIOLATIONS file(s) modified without authorization"
  echo "Review changes and update baseline if legitimate:"
  echo "  sha256sum [file] > .integrity/[file].sha256"
  exit 1
fi

echo "✅ All files integrity verified ($(($(ls -1 .integrity/*.sha256 | wc -l))) files checked)"
exit 0
