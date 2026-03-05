#!/bin/bash
set -e

SKILL_DIR="$HOME/.openclaw/skills/xhs"

echo ""
echo "========================================"
echo "  OpenClaw XHS Skill — Uninstaller"
echo "========================================"
echo ""

if [[ ! -d "$SKILL_DIR" ]]; then
    echo "XHS skill not found at $SKILL_DIR. Nothing to do."
    exit 0
fi

echo "This will remove:"
echo "  - $SKILL_DIR (skill files, scripts, toolkit)"
echo ""
echo "This will NOT remove:"
echo "  - ~/.openclaw/credentials/xhs_cookies.json"
echo "  - openclaw.json config (remove manually if needed)"
echo ""
read -p "Continue? [y/N] " confirm

if [[ "$confirm" != "y" && "$confirm" != "Y" ]]; then
    echo "Cancelled."
    exit 0
fi

rm -rf "$SKILL_DIR"
echo "Removed $SKILL_DIR"

echo ""
echo "To also remove the config from openclaw.json, run:"
echo "  python3 -c \""
echo "import json; p='$HOME/.openclaw/openclaw.json'; c=json.load(open(p));"
echo "c.get('skills',{}).get('entries',{}).pop('xhs',None);"
echo "open(p,'w').write(json.dumps(c,indent=2,ensure_ascii=False))"
echo "\""
echo ""
echo "Done. Restart the gateway: openclaw gateway --force"
