#!/usr/bin/env bash
set -euo pipefail

BASE_DIR="${TPM_DIR:-$HOME/.openclaw/workspace/tpm}"

echo "Initializing TPM Copilot workspace at: $BASE_DIR"
mkdir -p "$BASE_DIR"/{programs,templates,meetings}

if [ ! -f "$BASE_DIR/config.json" ]; then
  cat > "$BASE_DIR/config.json" << 'EOF'
{
  "tracker": "jira",
  "jira": {
    "base_url": "",
    "email": "",
    "api_token": ""
  },
  "linear": {
    "api_key": ""
  },
  "github": {
    "token": "",
    "method": "gh_cli"
  },
  "slack": {
    "webhook_url": ""
  },
  "email": {
    "provider": "resend",
    "api_key": "",
    "from": ""
  },
  "defaults": {
    "stale_ticket_days": 5,
    "pr_review_threshold_hours": 48,
    "sprint_length_weeks": 2
  }
}
EOF
  echo "Created config.json"
fi

if [ ! -f "$BASE_DIR/state.json" ]; then
  echo '{"last_risk_scan": null, "last_status_report": null, "last_action_check": null}' > "$BASE_DIR/state.json"
  echo "Created state.json"
fi

echo "✅ TPM Copilot workspace initialized"
echo ""
echo "Next: scripts/add-program.sh --name my-program --tracker jira --project PHX"
