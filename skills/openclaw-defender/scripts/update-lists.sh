#!/bin/bash
# Fetch blocklist (and optional allowlist examples) from official openclaw-defender repo
# Part of openclaw-defender

DEFENDER_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BLOCKLIST_FILE="$DEFENDER_ROOT/references/blocklist.conf"
BACKUP_DIR="$DEFENDER_ROOT/references/.backup"

# Resolve base URL for raw content: env override, else git remote, else default
if [ -n "$OPENCLAW_DEFENDER_LISTS_URL" ]; then
  BASE_URL="$OPENCLAW_DEFENDER_LISTS_URL"
else
  BRANCH="$(cd "$DEFENDER_ROOT" && git rev-parse --abbrev-ref HEAD 2>/dev/null)" || BRANCH="main"
  REMOTE="$(cd "$DEFENDER_ROOT" && git remote get-url origin 2>/dev/null)"
  if echo "$REMOTE" | grep -q 'github\.com'; then
    REPO=$(echo "$REMOTE" | sed -E 's|.*github\.com[:/]([^/]+/[^/]+)(\.git)?$|\1|')
    BASE_URL="https://raw.githubusercontent.com/$REPO/${BRANCH}"
  else
    BASE_URL="https://raw.githubusercontent.com/nightfullstar/openclaw-defender/main"
  fi
fi

echo "=== OpenClaw Defender: Update lists ==="
echo "Source: $BASE_URL"
echo ""

# Blocklist
if [ -f "$BLOCKLIST_FILE" ]; then
  mkdir -p "$BACKUP_DIR"
  cp "$BLOCKLIST_FILE" "$BACKUP_DIR/blocklist.conf.$(date +%Y%m%d%H%M%S)"
  echo "  Backed up blocklist to $BACKUP_DIR/"
fi

BLOCKLIST_URL="$BASE_URL/references/blocklist.conf"
if command -v curl >/dev/null 2>&1; then
  if curl -sSfL -o "$BLOCKLIST_FILE.new" "$BLOCKLIST_URL"; then
    mv "$BLOCKLIST_FILE.new" "$BLOCKLIST_FILE"
    echo "  ✓ blocklist.conf updated from $BLOCKLIST_URL"
  else
    echo "  ✗ Failed to fetch blocklist (curl failed or 404)"
    rm -f "$BLOCKLIST_FILE.new"
    exit 1
  fi
elif command -v wget >/dev/null 2>&1; then
  if wget -q -O "$BLOCKLIST_FILE.new" "$BLOCKLIST_URL"; then
    mv "$BLOCKLIST_FILE.new" "$BLOCKLIST_FILE"
    echo "  ✓ blocklist.conf updated from $BLOCKLIST_URL"
  else
    echo "  ✗ Failed to fetch blocklist (wget failed or 404)"
    rm -f "$BLOCKLIST_FILE.new"
    exit 1
  fi
else
  echo "  ✗ Need curl or wget to fetch lists"
  exit 1
fi

# Optional: mention example allowlists if repo has them
for name in network-whitelist.example safe-commands.example rag-allowlist.example; do
  URL="$BASE_URL/references/$name"
  if command -v curl >/dev/null 2>&1; then
    curl -sSfL -o /dev/null "$URL" 2>/dev/null && echo "  ℹ  Optional: $name available at $URL (copy to workspace root as .defender-* if needed)"
  fi
done

echo ""
echo "✅ Lists updated. Re-audit skills to use new blocklist: audit-skills.sh /path/to/skill"
echo "   To use a different source next time: OPENCLAW_DEFENDER_LISTS_URL=<base_url> $0"
