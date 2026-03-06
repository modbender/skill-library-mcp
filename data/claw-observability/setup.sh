#!/bin/bash
# CLAW Observability — Hooks Installer
# Installs Claude Code hooks for automatic agent reporting to CLAW.
#
# Usage: bash setup.sh
# Run once after installing the CLAW skill.

set -euo pipefail

echo ""
echo "  CLAW Observability — Hooks Setup"
echo "  =================================="
echo ""

# ─── Prerequisites ───
if ! command -v python3 &>/dev/null; then
  echo "  [ERROR] python3 is required but not found."
  exit 1
fi
if ! command -v curl &>/dev/null; then
  echo "  [ERROR] curl is required but not found."
  exit 1
fi

# ─── Check env vars ───
MISSING_ENV=0
if [ -z "${CLAW_API_KEY:-}" ]; then
  echo "  [WARN] CLAW_API_KEY is not set."
  echo "         Add to your shell profile (~/.zshrc or ~/.bashrc):"
  echo "         export CLAW_API_KEY=\"your-api-key\""
  echo ""
  MISSING_ENV=1
fi
if [ -z "${CLAW_BASE_URL:-}" ]; then
  echo "  [WARN] CLAW_BASE_URL is not set."
  echo "         Add to your shell profile (~/.zshrc or ~/.bashrc):"
  echo "         export CLAW_BASE_URL=\"https://claw.ia.br\""
  echo ""
  MISSING_ENV=1
fi

# ─── Locate hook script ───
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
HOOKS_SRC="$SCRIPT_DIR/hooks/claw-hooks.sh"

if [ ! -f "$HOOKS_SRC" ]; then
  echo "  [ERROR] hooks/claw-hooks.sh not found at: $HOOKS_SRC"
  echo "         Make sure you run this from the skill directory."
  exit 1
fi

# ─── Install hook script ───
HOOKS_DIR="$HOME/.claude/hooks/claw"
mkdir -p "$HOOKS_DIR"
cp "$HOOKS_SRC" "$HOOKS_DIR/claw-hooks.sh"
chmod +x "$HOOKS_DIR/claw-hooks.sh"
echo "  [OK] Hook script installed: $HOOKS_DIR/claw-hooks.sh"

# ─── Configure Claude Code settings ───
SETTINGS_FILE="$HOME/.claude/settings.json"

python3 << 'PYEOF'
import json
import os
import sys

settings_file = os.path.expanduser("~/.claude/settings.json")
hooks_script = os.path.expanduser("~/.claude/hooks/claw/claw-hooks.sh")
hooks_cmd = f"bash {hooks_script}"

# CLAW hook definitions
claw_hooks = {
    "UserPromptSubmit": [
        {
            "hooks": [
                {
                    "type": "command",
                    "command": hooks_cmd,
                    "timeout": 10
                }
            ]
        }
    ],
    "PreToolUse": [
        {
            "matcher": "Task",
            "hooks": [
                {
                    "type": "command",
                    "command": hooks_cmd,
                    "timeout": 10
                }
            ]
        }
    ],
    "PostToolUse": [
        {
            "matcher": "Task",
            "hooks": [
                {
                    "type": "command",
                    "command": hooks_cmd,
                    "timeout": 10
                }
            ]
        }
    ],
    "PostToolUseFailure": [
        {
            "matcher": "Task",
            "hooks": [
                {
                    "type": "command",
                    "command": hooks_cmd,
                    "timeout": 10
                }
            ]
        }
    ],
    "Stop": [
        {
            "hooks": [
                {
                    "type": "command",
                    "command": hooks_cmd,
                    "timeout": 10
                }
            ]
        }
    ]
}

# Load existing settings
settings = {}
if os.path.exists(settings_file):
    try:
        with open(settings_file) as f:
            settings = json.load(f)
    except json.JSONDecodeError:
        print(f"  [WARN] Could not parse {settings_file}, creating new config")
        settings = {}

# Merge hooks (preserve existing, add CLAW)
existing_hooks = settings.get("hooks", {})
added = 0

for event, hook_list in claw_hooks.items():
    if event not in existing_hooks:
        existing_hooks[event] = []

    # Check if CLAW hook already installed
    has_claw = any(
        any("claw-hooks.sh" in h.get("command", "") for h in entry.get("hooks", []))
        for entry in existing_hooks[event]
    )

    if has_claw:
        # Update existing CLAW hook entry
        for entry in existing_hooks[event]:
            for h in entry.get("hooks", []):
                if "claw-hooks.sh" in h.get("command", ""):
                    h["command"] = hooks_cmd
                    h["timeout"] = 10
    else:
        existing_hooks[event].extend(hook_list)
        added += 1

settings["hooks"] = existing_hooks

# Ensure .claude directory exists
os.makedirs(os.path.dirname(settings_file), exist_ok=True)

# Write settings
with open(settings_file, "w") as f:
    json.dump(settings, f, indent=2)
    f.write("\n")

if added > 0:
    print(f"  [OK] Added {added} hook events to {settings_file}")
else:
    print(f"  [OK] Hooks already configured in {settings_file} (updated)")
PYEOF

# ─── Test connection ───
if [ "$MISSING_ENV" -eq 0 ]; then
  echo ""
  echo "  Testing connection to CLAW..."
  HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" \
    -X POST "${CLAW_BASE_URL}/api/v1/events" \
    -H "Content-Type: application/json" \
    -H "x-api-key: ${CLAW_API_KEY}" \
    -d '{"agent_id":"sheev-palpatine","agent_name":"Sheev Palpatine","agent_type":"orchestrator","status":"idle","message":"CLAW hooks installed and verified"}' \
    2>/dev/null || echo "000")

  if [ "$HTTP_CODE" = "201" ]; then
    echo "  [OK] Connection verified! CLAW is receiving events."
  else
    echo "  [WARN] Connection returned HTTP $HTTP_CODE"
    echo "         Check CLAW_API_KEY and CLAW_BASE_URL values."
  fi
fi

echo ""
echo "  ============================================"
echo "  Setup complete!"
echo ""
echo "  Required env vars (add to ~/.zshrc):"
echo "    export CLAW_API_KEY=\"your-api-key\""
echo "    export CLAW_BASE_URL=\"https://claw.ia.br\""
echo ""
echo "  Restart Claude Code to activate hooks."
echo "  ============================================"
echo ""
