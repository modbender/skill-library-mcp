#!/bin/bash
# =============================================================================
# Zero Trust Hardening Script — clawd-zero-trust skill
# Guides and applies: plugin allowlist, PLP toolset config, SSH lockdown,
# SecureClaw install if missing, and gateway bind check.
#
# MODES:
#   --dry-run (default): Show what would change, apply nothing
#   --apply:             Actually apply all changes
#
# Idempotent: each change is checked before applying.
# =============================================================================

OPENCLAW="${OPENCLAW_BIN:-$(which openclaw 2>/dev/null || echo '/home/claw/.npm-global/bin/openclaw')}"
CONFIG="${OPENCLAW_CONFIG:-$HOME/.openclaw/openclaw.json}"
SCRIPT_PATH="$(readlink -f "$0")"
SCRIPT_DIR="$(cd "$(dirname "$SCRIPT_PATH")" && pwd)"
SKILL_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
HARDENING_FILE="${HARDENING_FILE:-$SKILL_DIR/hardening.json}"
DRY_RUN=1

# Color output
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; CYAN='\033[0;36m'; NC='\033[0m'

# Parse args
for arg in "$@"; do
  case $arg in
    --apply)   DRY_RUN=0 ;;
    --dry-run) DRY_RUN=1 ;;
  esac
done

info()  { echo -e "${CYAN}[INFO]${NC}  $*"; }
ok()    { echo -e "${GREEN}[OK]${NC}    $*"; }
warn()  { echo -e "${YELLOW}[WARN]${NC}  $*"; }
fail()  { echo -e "${RED}[FAIL]${NC}  $*"; }
apply() {
  if [ "$DRY_RUN" -eq 1 ]; then
    echo -e "${YELLOW}[DRY-RUN]${NC} Would apply: $*"
  else
    info "Applying: $*"
    "$@"
  fi
}
apply_jq() {
  # apply_jq <description> <jq_filter> <file>
  local desc="$1" filter="$2" file="$3"
  
  # Validate jq filter syntax before applying
  if ! jq "$filter" "$file" >/dev/null 2>&1; then
    fail "Invalid jq filter: $filter (syntax check failed)"
    return 1
  fi
  
  if [ "$DRY_RUN" -eq 1 ]; then
    local result
    result=$(jq "$filter" "$file" 2>/dev/null)
    echo -e "${YELLOW}[DRY-RUN]${NC} $desc"
    echo -e "  Would produce:\n$(echo "$result" | head -20)"
  else
    local tmp
    tmp=$(mktemp)
    if jq "$filter" "$file" > "$tmp" 2>/dev/null; then
      mv "$tmp" "$file"
      ok "$desc — applied"
    else
      rm -f "$tmp"
      fail "$desc — jq filter failed"
      return 1
    fi
  fi
}

merge_hardening_overrides() {
  if [ ! -f "$HARDENING_FILE" ]; then
    fail "hardening.json not found at: $HARDENING_FILE"
    return 1
  fi

  if ! jq -e . "$HARDENING_FILE" >/dev/null 2>&1; then
    fail "hardening.json is not valid JSON: $HARDENING_FILE"
    return 1
  fi

  local merged backup tmp
  merged=$(jq -s '.[0] * .[1]' "$CONFIG" "$HARDENING_FILE" 2>/dev/null) || {
    fail "Failed to merge openclaw.json with hardening.json"
    return 1
  }

  if ! echo "$merged" | jq -e . >/dev/null 2>&1; then
    fail "Merged config failed jq validation"
    return 1
  fi

  if [ "$DRY_RUN" -eq 1 ]; then
    echo -e "${YELLOW}[DRY-RUN]${NC} Would shallow-merge overrides from $HARDENING_FILE into $CONFIG"
    echo "$merged" | jq '{plugins: .plugins, tools: .tools, gateway: .gateway, plp: .plp}'
    return 0
  fi

  backup="$CONFIG.bak.hardening.$(date -u +%Y%m%d%H%M%S)"
  cp "$CONFIG" "$backup" || {
    fail "Failed to create backup: $backup"
    return 1
  }
  info "Backup created: $backup"

  tmp=$(mktemp)
  echo "$merged" > "$tmp"
  mv "$tmp" "$CONFIG"
  ok "Merged hardening overrides from hardening.json"
  return 0
}

echo ""
echo "🔧 clawd-zero-trust Hardening — $(date -u '+%Y-%m-%d %H:%M UTC')"
echo "=================================================="
if [ "$DRY_RUN" -eq 1 ]; then
  echo -e "${YELLOW}Mode: DRY-RUN (no changes applied). Pass --apply to execute.${NC}"
else
  echo -e "${RED}Mode: APPLY — changes will be written to disk.${NC}"
fi
echo ""

# Validate dependencies
if ! command -v jq &>/dev/null; then
  fail "jq is required but not installed. Run: sudo apt install jq"
  exit 1
fi
if [ ! -f "$CONFIG" ]; then
  fail "openclaw.json not found at: $CONFIG"
  exit 1
fi

# =============================================================================
# 1. SecureClaw
# =============================================================================
echo "1️⃣  SecureClaw:"
if "$OPENCLAW" plugins list 2>/dev/null | grep -q "secureclaw.*loaded"; then
  ok "SecureClaw loaded"
else
  warn "SecureClaw not loaded."
  echo "  Install via ClawHub: openclaw skills install secureclaw"
  echo "  Or see: https://docs.openclaw.ai/skills/secureclaw"
fi

# =============================================================================
# 2. Hardening overrides (externalized)
# =============================================================================
echo ""
echo "2️⃣  Hardening Overrides (hardening.json):"
merge_hardening_overrides || exit 1

# =============================================================================
# 3. SSH Perimeter (check only — modifying sshd_config requires sudo)
# =============================================================================
echo ""
echo "3️⃣  SSH Perimeter:"
if ss -ltnp 2>/dev/null | grep ':22' | grep -qE '0\.0\.0\.0|\[::\]'; then
  warn "SSH exposed to 0.0.0.0 or [::] (all interfaces)."
  echo "  Add to /etc/ssh/sshd_config:"
  echo "    ListenAddress 127.0.0.1"
  echo "    ListenAddress <YOUR_TAILSCALE_IP>"
  echo "  Then: sudo systemctl restart ssh"
  if [ "$DRY_RUN" -eq 0 ]; then
    warn "SSH config requires manual edit — skipping auto-apply for safety."
  fi
else
  ok "SSH restricted (not bound to all interfaces)"
fi

# Gateway bind now managed via hardening.json merge.

# =============================================================================
# Summary diff (apply mode only)
# =============================================================================
echo ""
echo "=================================================="
if [ "$DRY_RUN" -eq 1 ]; then
  echo -e "${YELLOW}Dry-run complete. No changes applied.${NC}"
  echo -e "To apply: ${GREEN}bash $0 --apply${NC}"
else
  echo -e "${GREEN}Hardening applied.${NC}"
  echo "Next: bash egress-filter.sh --dry-run"
fi
