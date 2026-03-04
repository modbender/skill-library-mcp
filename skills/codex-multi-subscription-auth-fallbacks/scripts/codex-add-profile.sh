#!/usr/bin/env bash
# codex-add-profile.sh — Run Codex CLI OAuth device-flow login and import
# the tokens into openclaw as a named auth profile, without overwriting
# existing profiles.
#
# Usage: ./codex-add-profile.sh <profile-name>
# Example: ./codex-add-profile.sh myaccount
#
# Requires: codex CLI (`npm i -g @openai/codex`), node
#
# Files read:
#   ~/.codex/auth.json — OAuth tokens after device-flow login
# Files written:
#   ~/.codex/auth.json — Temporarily cleared, then restored from backup
#   ~/.openclaw/agents/main/agent/auth-profiles.json — Imported profile tokens
#
# Safety: Both files are backed up before modification. A trap handler
# restores ~/.codex/auth.json automatically on unexpected exit.

set -euo pipefail

PROFILE_NAME="${1:?Usage: $0 <profile-name>}"
OPENCLAW_AUTH="$HOME/.openclaw/agents/main/agent/auth-profiles.json"
CODEX_AUTH="$HOME/.codex/auth.json"
CODEX_BACKUP="${CODEX_AUTH}.bak-$(date +%s)"
OPENCLAW_BACKUP="${OPENCLAW_AUTH}.bak-$(date +%s)"

# Track whether we need to restore codex auth on unexpected exit
CODEX_AUTH_CLEARED=0

# Trap handler: restore codex auth if script exits unexpectedly after clearing it
cleanup() {
  if [ "$CODEX_AUTH_CLEARED" -eq 1 ] && [ -f "$CODEX_BACKUP" ]; then
    echo ""
    echo "==> Interrupted. Restoring Codex CLI auth from backup..."
    cp "$CODEX_BACKUP" "$CODEX_AUTH"
    echo "    Restored."
  fi
}
trap cleanup EXIT INT TERM

# Check all required dependencies upfront
command -v codex >/dev/null 2>&1 || { echo "Error: codex CLI not found. Install with: npm i -g @openai/codex"; exit 1; }
command -v node >/dev/null 2>&1 || { echo "Error: node not found (required by codex CLI)"; exit 1; }

echo "==> Adding openai-codex:$PROFILE_NAME via Codex CLI device flow"
echo ""

# Step 1: Back up both files
echo "==> Backing up existing auth files"
if [ -f "$CODEX_AUTH" ]; then
  cp "$CODEX_AUTH" "$CODEX_BACKUP"
  # Verify backup succeeded
  if [ ! -f "$CODEX_BACKUP" ]; then
    echo "Error: Failed to create backup at $CODEX_BACKUP"
    exit 1
  fi
  echo "    Codex CLI:  $CODEX_BACKUP"
fi
if [ -f "$OPENCLAW_AUTH" ]; then
  cp "$OPENCLAW_AUTH" "$OPENCLAW_BACKUP"
  if [ ! -f "$OPENCLAW_BACKUP" ]; then
    echo "Error: Failed to create backup at $OPENCLAW_BACKUP"
    exit 1
  fi
  echo "    OpenClaw:   $OPENCLAW_BACKUP"
fi

# Step 2: Confirm before clearing codex auth
echo ""
echo "==> This will temporarily clear ~/.codex/auth.json to force a fresh login."
echo "    Your existing Codex CLI session has been backed up and will be restored afterward."
echo ""
printf "    Continue? [y/N] "
read -r CONFIRM
if [[ ! "$CONFIRM" =~ ^[Yy]$ ]]; then
  echo "    Aborted."
  exit 0
fi

echo ""
echo "==> Clearing Codex CLI auth to force fresh login..."
echo '{}' > "$CODEX_AUTH"
CODEX_AUTH_CLEARED=1

# Step 3: Run codex auth login (device flow — gives a URL + code)
echo ""
echo "==> Starting Codex CLI device-flow login."
echo "    Log in with your '$PROFILE_NAME' OpenAI account when the browser opens."
echo ""

LOGIN_OK=0
codex auth login && LOGIN_OK=1 || true

if [ "$LOGIN_OK" -eq 0 ] || [ ! -s "$CODEX_AUTH" ]; then
  echo ""
  echo "==> Login failed or cancelled. Restoring Codex CLI backup..."
  [ -f "$CODEX_BACKUP" ] && cp "$CODEX_BACKUP" "$CODEX_AUTH"
  echo "    Restored."
  exit 1
fi

# Step 4: Import tokens into openclaw auth-profiles.json
echo ""
echo "==> Importing tokens into openclaw as openai-codex:$PROFILE_NAME..."
PROFILE_NAME="$PROFILE_NAME" OPENCLAW_AUTH="$OPENCLAW_AUTH" node << 'NODEEOF'
const fs = require("fs");
const path = require("path");

const profileName = process.env.PROFILE_NAME;
const openclawAuthPath = process.env.OPENCLAW_AUTH;
const codexAuthPath = path.join(require("os").homedir(), ".codex", "auth.json");

// Read codex auth
const codex = JSON.parse(fs.readFileSync(codexAuthPath, "utf8"));
const tokens = codex.tokens || {};
if (!tokens.access_token && !tokens.refresh_token) {
  console.error("Error: No OAuth tokens found in codex auth.json");
  process.exit(1);
}

// Build openclaw profile entry
const profileKey = `openai-codex:${profileName}`;
const profileEntry = {
  type: "oauth",
  provider: "openai-codex",
  access: tokens.access_token || "",
  refresh: tokens.refresh_token || "",
};
if (tokens.account_id) profileEntry.accountId = tokens.account_id;

// Calculate expiry from access token JWT (exp claim)
try {
  const parts = tokens.access_token.split(".");
  const payload = JSON.parse(Buffer.from(parts[1], "base64url").toString());
  if (payload.exp) {
    profileEntry.expires = payload.exp * 1000; // ms
    console.log(`    Token expires at epoch ${payload.exp}`);
  }
} catch (e) {
  console.log(`    Warning: could not parse token expiry: ${e.message}`);
}

// Read and update openclaw auth (create if missing)
let data;
if (fs.existsSync(openclawAuthPath)) {
  data = JSON.parse(fs.readFileSync(openclawAuthPath, "utf8"));
} else {
  data = { version: 1, profiles: {}, order: {} };
}
if (!data.profiles) data.profiles = {};
if (!data.order) data.order = {};

// Replace placeholder if it exists
const existing = data.profiles[profileKey] || {};
if (existing.needsAuth) {
  console.log(`    Replacing placeholder for ${profileKey}`);
}

data.profiles[profileKey] = profileEntry;

// Update order list for openai-codex provider
const codexOrder = data.order["openai-codex"] || [];
if (!codexOrder.includes(profileKey)) codexOrder.push(profileKey);
data.order["openai-codex"] = codexOrder;

console.log(`    Saved profile: ${profileKey}`);

// Ensure parent directory exists
fs.mkdirSync(path.dirname(openclawAuthPath), { recursive: true });
fs.writeFileSync(openclawAuthPath, JSON.stringify(data, null, 2));

console.log("    Auth profiles updated successfully");
NODEEOF

# Step 5: Restore the original codex CLI auth
echo ""
echo "==> Restoring original Codex CLI auth..."
if [ -f "$CODEX_BACKUP" ]; then
  cp "$CODEX_BACKUP" "$CODEX_AUTH"
  CODEX_AUTH_CLEARED=0  # Clear flag so trap handler doesn't double-restore
  echo "    Restored original Codex CLI session."
fi

echo ""
echo "==> Done! Profile openai-codex:$PROFILE_NAME added."
echo "    OpenClaw backup: $OPENCLAW_BACKUP"
echo "    Codex backup:    $CODEX_BACKUP"
echo ""
echo "Next: Add the profile to openclaw.json auth.profiles and auth.order"
