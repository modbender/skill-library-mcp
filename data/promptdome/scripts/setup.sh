#!/usr/bin/env bash
# PromptDome OpenClaw Integration Setup
# Usage: bash setup.sh [--api-key sk_shield_live_...]
# One-shot: sets up the hook, plugin, API key, and tests the connection.
set -euo pipefail

CYAN='\033[0;36m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; NC='\033[0m'
BOLD='\033[1m'

info()  { echo -e "${CYAN}▶${NC} $*"; }
ok()    { echo -e "${GREEN}✅${NC} $*"; }
warn()  { echo -e "${YELLOW}⚠️ ${NC} $*"; }
die()   { echo -e "${RED}✗${NC} $*" >&2; exit 1; }
title() { echo -e "\n${BOLD}$*${NC}"; }

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
HOOKS_DIR="${HOME}/.openclaw/hooks/promptdome-gate"
EXTS_DIR="${HOME}/.openclaw/extensions/promptdome"
LOGS_DIR="${HOME}/.openclaw/logs"
CONFIG_FILE="${HOME}/.openclaw/openclaw.json"
API_URL="${PROMPTDOME_API_URL:-https://promptdome.cyberforge.one/api/v1/shield}"

title "═══════════════════════════════════════════"
title "  🛡️  PromptDome × OpenClaw Setup"
title "═══════════════════════════════════════════"
echo ""

# ── 1. Resolve API key ───────────────────────────────────────────────────────
API_KEY="${PROMPTDOME_API_KEY:-}"

# Accept --api-key flag
while [[ $# -gt 0 ]]; do
  case "$1" in
    --api-key) API_KEY="$2"; shift 2 ;;
    *) shift ;;
  esac
done

if [[ -z "$API_KEY" ]]; then
  echo -e "Enter your PromptDome API key (from ${CYAN}https://promptdome.cyberforge.one/dashboard/api-keys${NC}):"
  read -rsp "  API key: " API_KEY
  echo ""
fi

[[ -z "$API_KEY" ]] && die "No API key provided. Aborting."

# ── 2. Test the API key ──────────────────────────────────────────────────────
title "Step 1 / 4 — Testing API connection..."

TEST_RESPONSE=$(curl -sf -X POST "$API_URL" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${API_KEY}" \
  -d '{"text":"Hello, world!","mode":"user_prompt"}' 2>&1) || {
  die "Could not reach PromptDome API at ${API_URL}. Check your API key and network."
}

SCORE=$(echo "$TEST_RESPONSE" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('score','?'))" 2>/dev/null || echo "?")
ENGINE=$(echo "$TEST_RESPONSE" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('engineVersion','?'))" 2>/dev/null || echo "?")
ok "API connection verified (engine v${ENGINE}, test score: ${SCORE}/100)"

# ── 3. Install hook ──────────────────────────────────────────────────────────
title "Step 2 / 4 — Installing promptdome-gate hook..."

mkdir -p "$HOOKS_DIR" "$LOGS_DIR"
cp "${SKILL_DIR}/hook/HOOK.md"   "${HOOKS_DIR}/HOOK.md"
cp "${SKILL_DIR}/hook/handler.ts" "${HOOKS_DIR}/handler.ts"
ok "Hook files installed → ${HOOKS_DIR}"

# Enable the hook via CLI
openclaw hooks enable promptdome-gate 2>/dev/null && ok "Hook enabled" || warn "Could not auto-enable hook — run: openclaw hooks enable promptdome-gate"

# ── 4. Install plugin ────────────────────────────────────────────────────────
title "Step 3 / 4 — Installing promptdome plugin..."

mkdir -p "$EXTS_DIR"
cp "${SKILL_DIR}/plugin/index.ts"                "${EXTS_DIR}/index.ts"
cp "${SKILL_DIR}/plugin/openclaw.plugin.json"    "${EXTS_DIR}/openclaw.plugin.json"
ok "Plugin installed → ${EXTS_DIR}"

# ── 5. Persist API key in openclaw.json ─────────────────────────────────────
title "Step 4 / 4 — Saving API key to OpenClaw config..."

if [[ -f "$CONFIG_FILE" ]]; then
  # Use python3 to safely merge the env key without stomping other config
  python3 - <<PYEOF
import json, sys, os

config_file = os.path.expanduser("${CONFIG_FILE}")
api_key     = "${API_KEY}"

with open(config_file) as f:
    cfg = json.load(f)

cfg.setdefault("env", {})["PROMPTDOME_API_KEY"] = api_key

with open(config_file, "w") as f:
    json.dump(cfg, f, indent=2)

print("  API key written to openclaw.json")
PYEOF
  ok "API key saved to ${CONFIG_FILE}"
else
  warn "openclaw.json not found at ${CONFIG_FILE}"
  warn "Add this to your shell profile instead:"
  echo "  export PROMPTDOME_API_KEY=\"${API_KEY}\""
fi

# ── 6. Summary ───────────────────────────────────────────────────────────────
echo ""
echo -e "${BOLD}═══════════════════════════════════════════${NC}"
echo -e "${GREEN}${BOLD}  ✅ PromptDome integration complete!${NC}"
echo -e "${BOLD}═══════════════════════════════════════════${NC}"
echo ""
echo -e "  ${CYAN}Hook:${NC}   promptdome-gate (message:received)"
echo -e "  ${CYAN}Plugin:${NC} promptdome_scan (agent tool)"
echo -e "  ${CYAN}Logs:${NC}   ~/.openclaw/logs/promptdome-gate.log"
echo ""
echo -e "  ${YELLOW}Restart your OpenClaw gateway to activate:${NC}"
echo -e "  ${BOLD}  openclaw gateway restart${NC}"
echo ""
echo -e "  All incoming messages will now be automatically"
echo -e "  scanned before your agent processes them."
echo ""
