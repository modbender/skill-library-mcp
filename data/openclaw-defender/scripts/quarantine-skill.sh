#!/bin/bash
# Quarantine a suspicious skill
# Part of openclaw-defender

SKILL_NAME="$1"

if [ -z "$SKILL_NAME" ]; then
  echo "Usage: $0 <skill-name>"
  exit 1
fi

WORKSPACE="${OPENCLAW_WORKSPACE:-$HOME/.openclaw/workspace}"
SKILL_PATH="$WORKSPACE/skills/$SKILL_NAME"
QUARANTINE_PATH="$WORKSPACE/skills/$SKILL_NAME.QUARANTINE"

if [ ! -d "$SKILL_PATH" ]; then
  echo "Error: Skill not found: $SKILL_PATH"
  exit 1
fi

echo "=== OpenClaw Defender: Quarantine Skill ==="
echo "Skill: $SKILL_NAME"
echo "Path: $SKILL_PATH"
echo ""

# 1. Move to quarantine
echo "1. Moving skill to quarantine..."
mv "$SKILL_PATH" "$QUARANTINE_PATH"
echo "   ✓ Quarantined: $QUARANTINE_PATH"

# 2. Check for memory poisoning
echo ""
echo "2. Checking for memory poisoning..."
cd "$WORKSPACE" || exit 1

POISONED=0
for file in SOUL.md MEMORY.md IDENTITY.md memory/*.md; do
  if [ -f "$file" ]; then
    if grep -q "$SKILL_NAME" "$file"; then
      echo "   ⚠️  Found references in: $file"
      grep -n "$SKILL_NAME" "$file"
      POISONED=1
    fi
  fi
done

if [ $POISONED -eq 0 ]; then
  echo "   ✓ No memory poisoning detected"
else
  echo "   🚨 Memory poisoning detected - manual review required"
fi

# 3. Log incident
echo ""
echo "3. Logging security incident..."
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

cat >> "$WORKSPACE/memory/security-incidents.md" << EOF

## Skill Quarantine: $SKILL_NAME
**Date:** $TIMESTAMP
**Action:** Skill moved to quarantine
**Path:** $QUARANTINE_PATH
**Memory Poisoning:** $([ $POISONED -eq 1 ] && echo "YES - REVIEW REQUIRED" || echo "No")

**Next Steps:**
1. Review skill SKILL.md for malicious content
2. If poisoned, restore memory files from baseline
3. Rotate credentials (assume compromise):
   - Regenerate .agent-private-key-SECURE
   - Rotate API keys
   - Check for unauthorized transactions
4. Update blocklist to prevent re-installation
5. Report to OpenClaw community (responsible disclosure)

EOF

echo "   ✓ Incident logged to memory/security-incidents.md"

# 4. Recommendations
echo ""
echo "=== Recommended Actions ==="
echo "1. Review quarantined skill: $QUARANTINE_PATH/SKILL.md"
echo "2. Check integrity: ~/.openclaw/workspace/bin/check-integrity.sh"
echo "3. If compromised:"
echo "   - Restore from baseline"
echo "   - Rotate all credentials"
echo "   - Review audit logs"
echo "4. Permanent removal: rm -rf $QUARANTINE_PATH"
echo ""
echo "⚠️  DO NOT re-enable until thoroughly investigated"
