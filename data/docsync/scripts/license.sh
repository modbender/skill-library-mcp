#!/usr/bin/env bash
# DocSync — License Validation Module
# Validates JWT license keys offline (no network calls)
# License keys encode: tier (free/pro/team/enterprise), seats, expiry

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
DIM='\033[2m'
NC='\033[0m'

# ─── Config paths ──────────────────────────────────────────────────────────

OPENCLAW_CONFIG="${HOME}/.openclaw/openclaw.json"
DOCSYNC_LICENSE_KEY="${DOCSYNC_LICENSE_KEY:-}"

# Tier hierarchy
declare -A TIER_LEVELS=(
  [free]=0
  [pro]=1
  [team]=2
  [enterprise]=3
)

# ─── License key extraction ────────────────────────────────────────────────

get_license_key() {
  # Priority: env var > openclaw config
  if [[ -n "$DOCSYNC_LICENSE_KEY" ]]; then
    echo "$DOCSYNC_LICENSE_KEY"
    return 0
  fi

  # Try openclaw config
  if [[ -f "$OPENCLAW_CONFIG" ]]; then
    local key
    # Extract apiKey from skills.entries.docsync.apiKey
    # Using python for JSON parsing (widely available)
    if command -v python3 &>/dev/null; then
      key=$(python3 -c "
import json, sys
try:
    with open('$OPENCLAW_CONFIG') as f:
        cfg = json.load(f)
    print(cfg.get('skills', {}).get('entries', {}).get('docsync', {}).get('apiKey', ''))
except:
    pass
" 2>/dev/null)
    elif command -v python &>/dev/null; then
      key=$(python -c "
import json, sys
try:
    with open('$OPENCLAW_CONFIG') as f:
        cfg = json.load(f)
    print(cfg.get('skills', {}).get('entries', {}).get('docsync', {}).get('apiKey', ''))
except:
    pass
" 2>/dev/null)
    elif command -v node &>/dev/null; then
      key=$(node -e "
try {
  const cfg = require('$OPENCLAW_CONFIG');
  console.log(cfg?.skills?.entries?.docsync?.apiKey || '');
} catch(e) {}
" 2>/dev/null)
    elif command -v jq &>/dev/null; then
      key=$(jq -r '.skills.entries.docsync.apiKey // ""' "$OPENCLAW_CONFIG" 2>/dev/null)
    fi

    if [[ -n "${key:-}" ]]; then
      echo "$key"
      return 0
    fi
  fi

  return 1
}

# ─── JWT decoding (base64 only — no crypto verification for offline use) ─

decode_jwt_payload() {
  local token="$1"
  # JWT format: header.payload.signature
  local payload
  payload=$(echo "$token" | cut -d. -f2)

  # Add padding if needed
  local padded="$payload"
  local mod=$((${#payload} % 4))
  if [[ $mod -eq 2 ]]; then
    padded="${payload}=="
  elif [[ $mod -eq 3 ]]; then
    padded="${payload}="
  fi

  # Decode base64url (replace - with + and _ with /)
  echo "$padded" | tr '_-' '/+' | base64 -d 2>/dev/null || \
  echo "$padded" | tr '_-' '/+' | base64 -D 2>/dev/null || \
  echo "$padded" | tr '_-' '/+' | openssl base64 -d 2>/dev/null || \
  return 1
}

extract_field() {
  local json="$1"
  local field="$2"

  if command -v python3 &>/dev/null; then
    python3 -c "import json; print(json.loads('$json').get('$field', ''))" 2>/dev/null
  elif command -v node &>/dev/null; then
    node -e "console.log(JSON.parse('$json')['$field'] || '')" 2>/dev/null
  elif command -v jq &>/dev/null; then
    echo "$json" | jq -r ".$field // \"\"" 2>/dev/null
  else
    # Crude regex fallback
    echo "$json" | grep -oP "\"$field\"\s*:\s*\"?\K[^\",$}]+" 2>/dev/null || echo ""
  fi
}

# ─── License validation ────────────────────────────────────────────────────

check_license() {
  local required_tier="${1:-pro}"
  local required_level="${TIER_LEVELS[$required_tier]:-1}"

  # Get the license key
  local key
  if ! key=$(get_license_key) || [[ -z "$key" ]]; then
    echo -e "${RED}${BOLD}━━━ DocSync License Required ━━━${NC}"
    echo ""
    echo -e "This feature requires a ${BOLD}${required_tier}${NC} license."
    echo ""
    echo -e "Get your license at: ${CYAN}${BOLD}https://docsync.pages.dev/pricing${NC}"
    echo ""
    echo "Then add it to your config:"
    echo ""
    echo -e "  ${DIM}# In ~/.openclaw/openclaw.json:${NC}"
    echo -e "  ${CYAN}\"skills\": { \"entries\": { \"docsync\": { \"apiKey\": \"YOUR_KEY\" } } }${NC}"
    echo ""
    echo -e "  ${DIM}# Or set the environment variable:${NC}"
    echo -e "  ${CYAN}export DOCSYNC_LICENSE_KEY=\"YOUR_KEY\"${NC}"
    echo ""
    return 1
  fi

  # Decode the JWT payload
  local payload
  if ! payload=$(decode_jwt_payload "$key"); then
    echo -e "${RED}[DocSync]${NC} Invalid license key format."
    echo -e "Get a valid license at: ${CYAN}https://docsync.pages.dev/pricing${NC}"
    return 1
  fi

  # Extract fields
  local tier expiry seats
  tier=$(extract_field "$payload" "tier")
  expiry=$(extract_field "$payload" "exp")
  seats=$(extract_field "$payload" "seats")

  # Validate tier
  local actual_level="${TIER_LEVELS[$tier]:-0}"
  if [[ "$actual_level" -lt "$required_level" ]]; then
    echo -e "${RED}[DocSync]${NC} This feature requires ${BOLD}$required_tier${NC} tier."
    echo -e "Your current tier: ${BOLD}$tier${NC}"
    echo ""
    echo -e "Upgrade at: ${CYAN}https://docsync.pages.dev/upgrade${NC}"
    return 1
  fi

  # Validate expiry
  if [[ -n "$expiry" ]]; then
    local now
    now=$(date +%s)
    if [[ "$now" -gt "$expiry" ]]; then
      local expiry_date
      expiry_date=$(date -d "@$expiry" +%Y-%m-%d 2>/dev/null || date -r "$expiry" +%Y-%m-%d 2>/dev/null || echo "unknown")
      echo -e "${RED}[DocSync]${NC} License expired on ${BOLD}$expiry_date${NC}."
      echo -e "Renew at: ${CYAN}https://docsync.pages.dev/renew${NC}"
      return 1
    fi
  fi

  # License valid
  return 0
}

# ─── Status display ────────────────────────────────────────────────────────

show_license_status() {
  local key
  if ! key=$(get_license_key) || [[ -z "$key" ]]; then
    echo -e "License: ${YELLOW}Free tier${NC}"
    echo -e "  Available commands: generate"
    echo -e "  Upgrade at: ${CYAN}https://docsync.pages.dev/pricing${NC}"
    return
  fi

  local payload
  if ! payload=$(decode_jwt_payload "$key"); then
    echo -e "License: ${RED}Invalid key${NC}"
    return
  fi

  local tier expiry seats
  tier=$(extract_field "$payload" "tier")
  expiry=$(extract_field "$payload" "exp")
  seats=$(extract_field "$payload" "seats")

  # Check if expired
  local now
  now=$(date +%s)
  local status_color="$GREEN"
  local status_text="Active"
  if [[ -n "$expiry" && "$now" -gt "$expiry" ]]; then
    status_color="$RED"
    status_text="Expired"
  fi

  local expiry_date="Never"
  if [[ -n "$expiry" ]]; then
    expiry_date=$(date -d "@$expiry" +%Y-%m-%d 2>/dev/null || date -r "$expiry" +%Y-%m-%d 2>/dev/null || echo "unknown")
  fi

  echo -e "License: ${status_color}${BOLD}${tier^^}${NC} (${status_color}${status_text}${NC})"
  echo -e "  Seats: ${seats:-unlimited}"
  echo -e "  Expires: $expiry_date"
  echo ""

  case "$tier" in
    pro)
      echo -e "  Available: generate, drift, hooks, auto-fix"
      echo -e "  Upgrade to Team for: onboarding, architecture"
      ;;
    team)
      echo -e "  Available: generate, drift, hooks, auto-fix, onboarding, architecture"
      ;;
    enterprise)
      echo -e "  Available: All features + priority support"
      ;;
  esac
}
