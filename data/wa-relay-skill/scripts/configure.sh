#!/usr/bin/env bash
set -euo pipefail

# ─── wa-relay configure v0.2.1 ───
# Generates the JSON config for multi-agent WhatsApp routing.
# Usage: bash configure.sh <owner-phone-number> [direct-numbers]
# Example: bash configure.sh +573001234567 +573009999999,+573008888888
#
# direct-numbers: comma-separated list of additional numbers that go
#                 directly to the main agent (bypassing the relay).

OWNER="${1:?Usage: configure.sh <owner-phone-number> [direct-numbers-comma-separated]}"
DIRECT="${2:-}"

# Build bindings array - owner goes to main
JSON_BINDINGS="    {
      \"agentId\": \"main\",
      \"match\": { \"channel\": \"whatsapp\", \"peer\": { \"kind\": \"direct\", \"id\": \"${OWNER}\" } }
    }"

# Add direct numbers if provided
if [[ -n "$DIRECT" ]]; then
  IFS=',' read -ra NUMS <<< "$DIRECT"
  for NUM in "${NUMS[@]}"; do
    NUM="$(echo "$NUM" | xargs)"  # trim whitespace
    JSON_BINDINGS+=",
    {
      \"agentId\": \"main\",
      \"match\": { \"channel\": \"whatsapp\", \"peer\": { \"kind\": \"direct\", \"id\": \"${NUM}\" } }
    }"
  done
fi

# Add catch-all for relay
JSON_BINDINGS+=",
    {
      \"agentId\": \"wa-relay\",
      \"match\": { \"channel\": \"whatsapp\" }
    }"

CONFIG_JSON="{
  \"agents\": {
    \"list\": [
      {
        \"id\": \"wa-relay\",
        \"workspace\": \"~/.openclaw/workspace-relay\",
        \"model\": { \"primary\": \"openai-codex/gpt-5.3-codex\" },
        \"heartbeat\": { \"every\": \"0m\" },
        \"identity\": { \"name\": \"WA Relay\" }
      }
    ]
  },
  \"bindings\": [
${JSON_BINDINGS}
  ]
}"

cat << EOF

═══════════════════════════════════════════════════════
  wa-relay — Configuration Output (v0.2.1)
═══════════════════════════════════════════════════════

Apply the following config using gateway config.patch:

${CONFIG_JSON}

── How to apply ────────────────────────────────────

Your agent can apply this directly:

  gateway config.patch with the JSON above

Or manually:

  1. Copy the JSON above
  2. Run: openclaw gateway config.patch '<paste JSON here>'
  3. Or edit ~/.openclaw/openclaw.json manually and restart

── Important notes ─────────────────────────────────

- The "list" array MERGES with existing agents (won't overwrite your main agent)
- The "bindings" array REPLACES any existing bindings
- Make sure your existing agents in agents.list are preserved
- After applying, restart: openclaw gateway restart

═══════════════════════════════════════════════════════

EOF

if [[ -n "$DIRECT" ]]; then
  echo "ℹ️  Direct numbers (bypass relay): $DIRECT"
  echo ""
fi

echo "📋 Config JSON also saved to /tmp/wa-relay-config.json"
echo "$CONFIG_JSON" > /tmp/wa-relay-config.json
