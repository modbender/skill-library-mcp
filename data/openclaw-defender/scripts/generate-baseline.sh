#!/bin/bash
# Generate initial integrity baselines for openclaw-defender
# Run once after a known-good state, then use check-integrity.sh to monitor.

WORKSPACE="${OPENCLAW_WORKSPACE:-$HOME/.openclaw/workspace}"
cd "$WORKSPACE" || { echo "Error: Workspace not found: $WORKSPACE"; exit 1; }

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

mkdir -p .integrity
mkdir -p memory

echo "=== OpenClaw Defender: Generate Integrity Baseline ==="
echo "Workspace: $WORKSPACE"
echo ""

# Core files
for file in "${CRITICAL_FILES[@]}"; do
  if [ -f "$file" ]; then
    sha256sum "$file" > ".integrity/$file.sha256"
    echo "  ✓ $file"
  else
    echo "  - $file (missing, skipped)"
  fi
done

# All SKILL.md under skills/
if [ -d "skills" ]; then
  find skills/ -name "SKILL.md" -type f | while read -r skill; do
    HASH_FILE=".integrity/$(echo "$skill" | tr / _).sha256"
    sha256sum "$skill" > "$HASH_FILE"
    echo "  ✓ $skill"
  done
fi

# Manifest of .integrity/ so we can detect tampering with baselines
MANIFEST=$(find .integrity -type f -name '*.sha256' 2>/dev/null | sort | xargs cat 2>/dev/null | sha256sum | cut -d' ' -f1)
echo "$MANIFEST" > .integrity-manifest.sha256
echo "  ✓ .integrity-manifest.sha256 (integrity-of-integrity)"

echo ""
echo "✅ Baseline generated in .integrity/"
echo "Next: run check-integrity.sh (or add to cron) to monitor for changes."
