#!/bin/bash
# install-proxy.sh — Install the Morpheus-to-OpenAI proxy and Gateway Guardian
#
# Sets up:
# 1. morpheus-proxy.mjs → ~/morpheus/proxy/ (OpenAI-compatible proxy)
# 2. gateway-guardian.sh → ~/.openclaw/workspace/scripts/ (gateway watchdog)
# 3. launchd plists for both (auto-start, auto-restart)
#
# Usage: bash skills/everclaw/scripts/install-proxy.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
MORPHEUS_DIR="${MORPHEUS_DIR:-$HOME/morpheus}"
PROXY_DIR="$MORPHEUS_DIR/proxy"
OPENCLAW_DIR="${OPENCLAW_DIR:-$HOME/.openclaw}"
NODE_PATH="${NODE_PATH_OVERRIDE:-$(which node)}"
LAUNCH_AGENTS="$HOME/Library/LaunchAgents"

echo "╔══════════════════════════════════════════╗"
echo "║  Everclaw — Proxy & Guardian Installer   ║"
echo "╚══════════════════════════════════════════╝"
echo ""

# --- 1. Install Morpheus Proxy ---
echo "📡 Installing Morpheus-to-OpenAI proxy..."
mkdir -p "$PROXY_DIR"

cp "$SCRIPT_DIR/morpheus-proxy.mjs" "$PROXY_DIR/morpheus-proxy.mjs"
echo "   ✓ Copied morpheus-proxy.mjs → $PROXY_DIR/"

# --- 2. Install Router Launch Script ---
echo "🔧 Installing proxy-router headless launcher..."
cp "$SCRIPT_DIR/mor-launch-headless.sh" "$MORPHEUS_DIR/mor-launch-headless.sh"
chmod +x "$MORPHEUS_DIR/mor-launch-headless.sh"
echo "   ✓ Copied mor-launch-headless.sh → $MORPHEUS_DIR/"

# --- 3. Install Gateway Guardian ---
echo "🛡️  Installing Gateway Guardian..."
mkdir -p "$OPENCLAW_DIR/workspace/scripts"
mkdir -p "$OPENCLAW_DIR/logs"

cp "$SCRIPT_DIR/gateway-guardian.sh" "$OPENCLAW_DIR/workspace/scripts/gateway-guardian.sh"
chmod +x "$OPENCLAW_DIR/workspace/scripts/gateway-guardian.sh"
echo "   ✓ Copied gateway-guardian.sh → $OPENCLAW_DIR/workspace/scripts/"

# --- 3. Install launchd plists (macOS only) ---
if [[ "$(uname)" == "Darwin" ]]; then
  echo "🍎 Setting up launchd services..."
  mkdir -p "$LAUNCH_AGENTS"

  # Unload existing if present
  launchctl unload "$LAUNCH_AGENTS/com.morpheus.router.plist" 2>/dev/null || true
  launchctl unload "$LAUNCH_AGENTS/com.morpheus.proxy.plist" 2>/dev/null || true
  launchctl unload "$LAUNCH_AGENTS/ai.openclaw.guardian.plist" 2>/dev/null || true

  # Morpheus router plist (the Go proxy-router binary)
  sed \
    -e "s|__MORPHEUS_DIR__|$MORPHEUS_DIR|g" \
    -e "s|__HOME__|$HOME|g" \
    "$SKILL_DIR/templates/com.morpheus.router.plist" > "$LAUNCH_AGENTS/com.morpheus.router.plist"
  echo "   ✓ Installed com.morpheus.router.plist"

  # Morpheus proxy plist
  sed \
    -e "s|__NODE_PATH__|$NODE_PATH|g" \
    -e "s|__PROXY_SCRIPT_PATH__|$PROXY_DIR/morpheus-proxy.mjs|g" \
    -e "s|__MORPHEUS_DIR__|$MORPHEUS_DIR|g" \
    -e "s|__HOME__|$HOME|g" \
    "$SKILL_DIR/templates/com.morpheus.proxy.plist" > "$LAUNCH_AGENTS/com.morpheus.proxy.plist"
  echo "   ✓ Installed com.morpheus.proxy.plist"

  # Guardian plist
  sed \
    -e "s|__GUARDIAN_SCRIPT_PATH__|$OPENCLAW_DIR/workspace/scripts/gateway-guardian.sh|g" \
    -e "s|__OPENCLAW_DIR__|$OPENCLAW_DIR|g" \
    -e "s|__HOME__|$HOME|g" \
    "$SKILL_DIR/templates/ai.openclaw.guardian.plist" > "$LAUNCH_AGENTS/ai.openclaw.guardian.plist"
  echo "   ✓ Installed ai.openclaw.guardian.plist"

  # Load services (router first — proxy depends on it)
  launchctl load "$LAUNCH_AGENTS/com.morpheus.router.plist" 2>/dev/null
  sleep 3  # Give router time to start before proxy tries to connect
  launchctl load "$LAUNCH_AGENTS/com.morpheus.proxy.plist" 2>/dev/null
  launchctl load "$LAUNCH_AGENTS/ai.openclaw.guardian.plist" 2>/dev/null
  echo "   ✓ Services loaded (router → proxy → guardian)"

  sleep 2

  # Verify router is running
  if curl -s --max-time 5 -u "admin:$(cat "$MORPHEUS_DIR/.cookie" 2>/dev/null | cut -d: -f2)" http://localhost:8082/healthcheck 2>/dev/null | grep -q healthy; then
    echo "   ✓ Proxy-router is healthy (port 8082)"
  else
    echo "   ⚠️  Proxy-router not responding — check ~/morpheus/data/logs/router-stdout.log"
    echo "      (May need wallet key in 1Password or Keychain)"
  fi

  # Verify proxy is running
  if curl -s --max-time 3 http://127.0.0.1:8083/health > /dev/null 2>&1; then
    echo "   ✓ Morpheus proxy is healthy (port 8083)"
  else
    echo "   ⚠️  Morpheus proxy not responding yet — check ~/morpheus/proxy/proxy.log"
  fi

  # Verify guardian
  if launchctl list | grep -q "ai.openclaw.guardian"; then
    echo "   ✓ Gateway Guardian is scheduled (every 2 minutes)"
  else
    echo "   ⚠️  Gateway Guardian not loaded — check manually"
  fi
else
  echo "⚠️  Non-macOS detected. Skipping launchd setup."
  echo "   For Linux, create systemd units or cron jobs manually."
  echo "   Proxy: node $PROXY_DIR/morpheus-proxy.mjs"
  echo "   Guardian: bash $OPENCLAW_DIR/workspace/scripts/gateway-guardian.sh"
fi

# --- Post-Install: Validate OpenClaw Config ---
echo ""
echo "🔍 Validating OpenClaw configuration..."

OPENCLAW_CONFIG="$OPENCLAW_DIR/openclaw.json"
CONFIG_ISSUES=0

if [[ -f "$OPENCLAW_CONFIG" ]]; then
  # Check for invalid provider prefixes in model config
  # "everclaw/" is NOT a valid provider — Everclaw is a skill, not a provider.
  # Valid Morpheus providers: "morpheus", "mor-gateway"
  INVALID_PROVIDERS=$(python3 -c "
import json, sys
try:
    config = json.load(open('$OPENCLAW_CONFIG'))
    issues = []
    # Check primary model
    primary = config.get('agents',{}).get('defaults',{}).get('model',{}).get('primary','')
    if primary.startswith('everclaw/'):
        issues.append(f'primary model: {primary}')
    # Check fallbacks
    for fb in config.get('agents',{}).get('defaults',{}).get('model',{}).get('fallbacks',[]):
        if fb.startswith('everclaw/'):
            issues.append(f'fallback model: {fb}')
    # Check provider names
    for pname in config.get('models',{}).get('providers',{}).keys():
        if pname == 'everclaw':
            issues.append(f'provider named \"everclaw\"')
    if issues:
        print('|'.join(issues))
except:
    pass
" 2>/dev/null)

  if [[ -n "$INVALID_PROVIDERS" ]]; then
    echo ""
    echo "   ⚠️  MISCONFIGURATION DETECTED!"
    echo ""
    echo "   Your config uses 'everclaw/' as a provider prefix."
    echo "   Everclaw is a SKILL, not an inference provider."
    echo "   This will route requests to Venice (billing errors) instead of Morpheus."
    echo ""
    echo "   Issues found:"
    IFS='|' read -ra ISSUES <<< "$INVALID_PROVIDERS"
    for issue in "${ISSUES[@]}"; do
      echo "     ❌ $issue"
    done
    echo ""
    echo "   VALID provider names for Morpheus inference:"
    echo "     • morpheus/kimi-k2.5     — local P2P (needs proxy-router running)"
    echo "     • mor-gateway/kimi-k2.5  — hosted API Gateway (needs API key)"
    echo ""
    echo "   To fix, change your model in openclaw.json:"
    echo "     \"primary\": \"mor-gateway/kimi-k2.5\"    ← Morpheus API Gateway"
    echo "     \"primary\": \"morpheus/kimi-k2.5\"       ← Local Morpheus P2P"
    echo ""
    echo "   Then restart: openclaw gateway restart"
    echo ""
    CONFIG_ISSUES=1
  fi

  # Check if any Morpheus provider is configured
  HAS_MORPHEUS=$(python3 -c "
import json
config = json.load(open('$OPENCLAW_CONFIG'))
providers = config.get('models',{}).get('providers',{})
has = 'morpheus' in providers or 'mor-gateway' in providers
print('yes' if has else 'no')
" 2>/dev/null || echo "no")

  if [[ "$HAS_MORPHEUS" == "no" ]]; then
    echo "   ⚠️  No Morpheus provider configured in openclaw.json"
    echo "   Run: node $SKILL_DIR/scripts/bootstrap-gateway.mjs"
    echo "   This adds mor-gateway as a fallback (no API key needed)."
    CONFIG_ISSUES=1
  fi

  if [[ "$CONFIG_ISSUES" -eq 0 ]]; then
    echo "   ✓ OpenClaw config looks good"
  fi
else
  echo "   ⚠️  openclaw.json not found at $OPENCLAW_CONFIG"
  echo "   Run 'openclaw onboard' first, then re-run this installer."
fi

echo ""
echo "╔══════════════════════════════════════════╗"
echo "║  Installation complete!                  ║"
echo "╠══════════════════════════════════════════╣"
echo "║                                          ║"
echo "║  Router:   http://127.0.0.1:8082         ║"
echo "║  Proxy:    http://127.0.0.1:8083         ║"
echo "║  Health:   curl localhost:8083/health     ║"
echo "║  Guardian: ~/.openclaw/logs/guardian.log  ║"
echo "║                                          ║"
if [[ "$CONFIG_ISSUES" -gt 0 ]]; then
echo "║  ⚠️  Config issues found — see above      ║"
else
echo "║  ✅ Config validated — ready to go!        ║"
fi
echo "║                                          ║"
echo "╚══════════════════════════════════════════╝"
