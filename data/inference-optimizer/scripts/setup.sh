#!/usr/bin/env bash
# Setup inference-optimizer: make scripts executable; optionally wire commands into workspace.
# Default: preview only. Use --apply to modify AGENTS.md and TOOLS.md.
# Run after install. Targets ~/clawd and ~/.openclaw/workspace-whatsapp.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
WORKSPACE_MAIN="${WORKSPACE_MAIN:-$HOME/clawd}"
WORKSPACE_WHATSAPP="${WORKSPACE_WHATSAPP:-$HOME/.openclaw/workspace-whatsapp}"

chmod +x "$SKILL_DIR/scripts/openclaw-audit.sh"
chmod +x "$SKILL_DIR/scripts/purge-stale-sessions.sh"
echo "[OK] Scripts executable"

APPLY=false
[[ "${1:-}" = "--apply" ]] && APPLY=true

AUDIT_PATH="$SKILL_DIR/scripts/openclaw-audit.sh"
PURGE_PATH="$SKILL_DIR/scripts/purge-stale-sessions.sh"

SNIPPET_AGENTS="

## Chat commands (exact match, run immediately)

| Command | Action |
| \`/optimize\` or \`/audit\` | Exec \`bash $AUDIT_PATH\`; include script output. |"

SNIPPET_TOOLS="

## inference-optimizer

| App | Use | Example |
| \`/optimize\` | Run audit script | exec \`bash $AUDIT_PATH\`; include output. |
| purge sessions | After /optimize if user approves | exec \`bash $PURGE_PATH\` (archives by default). |"

if [[ "$APPLY" = false ]]; then
  echo ""
  echo "Preview (no changes made). Run with --apply to modify workspace files."
  echo ""
  echo "Would add to AGENTS.md:"
  echo "$SNIPPET_AGENTS"
  echo ""
  echo "Would add to TOOLS.md:"
  echo "$SNIPPET_TOOLS"
  echo ""
  echo "Workspaces: $WORKSPACE_MAIN, $WORKSPACE_WHATSAPP"
  echo "Usage: bash $0 --apply"
  exit 0
fi

for ws in "$WORKSPACE_MAIN" "$WORKSPACE_WHATSAPP"; do
  [[ -d "$ws" ]] || continue
  if [[ -f "$ws/AGENTS.md" ]]; then
    if ! grep -q "/optimize" "$ws/AGENTS.md" 2>/dev/null; then
      echo "$SNIPPET_AGENTS" >> "$ws/AGENTS.md"
      echo "[OK] Added /optimize to $ws/AGENTS.md"
    else
      echo "[SKIP] $ws/AGENTS.md already has /optimize"
    fi
  else
    echo "[WARN] $ws/AGENTS.md not found"
  fi
  if [[ -f "$ws/TOOLS.md" ]]; then
    if ! grep -q "inference-optimizer" "$ws/TOOLS.md" 2>/dev/null; then
      echo "$SNIPPET_TOOLS" >> "$ws/TOOLS.md"
      echo "[OK] Added /optimize to $ws/TOOLS.md"
    else
      echo "[SKIP] $ws/TOOLS.md already has inference-optimizer"
    fi
  else
    echo "[WARN] $ws/TOOLS.md not found"
  fi
done

echo ""
echo "Done. Prefer manual purge: bash $PURGE_PATH (archives by default)."
echo "Verify: bash $SKILL_DIR/scripts/verify.sh"
