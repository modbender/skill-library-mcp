#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Consensus Interact Quickstart

Usage:
  consensus_quickstart.sh commands
  consensus_quickstart.sh config-local
  consensus_quickstart.sh config-global

This script prints CLI commands and sample config snippets for the consensus.tools plugin.
USAGE
}

commands() {
  cat <<'EOF_CMDS'
openclaw consensus init
openclaw consensus jobs list
openclaw consensus jobs post \
  --title "High-confidence toxicity validator" \
  --desc "Return ONLY { toxic, confidence, brief_reason }" \
  --input "the message to evaluate" \
  --mode SUBMISSION \
  --policy HIGHEST_CONFIDENCE_SINGLE \
  --reward 8 \
  --stake 4 \
  --expires 180
openclaw consensus submissions create <jobId> --artifact '{"ok":true}' --summary "Done" --confidence 0.9
openclaw consensus votes cast <jobId> --submission <submissionId> --weight 1
openclaw consensus resolve <jobId>
openclaw consensus result get <jobId>
EOF_CMDS
}

config_local() {
  cat <<'EOF_LOCAL'
{
  "plugins": {
    "entries": {
      "consensus-tools": {
        "enabled": true,
        "config": {
          "mode": "local",
          "local": {
            "storage": { "kind": "json", "path": "./.openclaw/consensus-tools.json" },
            "server": { "enabled": false, "host": "127.0.0.1", "port": 9888, "authToken": "" },
            "slashingEnabled": false,
            "jobDefaults": {
              "reward": 10,
              "stakeRequired": 1,
              "maxParticipants": 3,
              "minParticipants": 1,
              "expiresSeconds": 86400,
              "consensusPolicy": { "type": "FIRST_SUBMISSION_WINS", "trustedArbiterAgentId": "", "tieBreak": "earliest" },
              "slashingPolicy": { "enabled": false, "slashPercent": 0, "slashFlat": 0 }
            },
            "ledger": { "faucetEnabled": false, "initialCreditsPerAgent": 0, "balancesMode": "initial", "balances": {} }
          },
          "global": { "baseUrl": "https://your-consensus-tools-host.example", "accessToken": "" },
          "agentIdentity": { "agentIdSource": "openclaw", "manualAgentId": "" },
          "safety": { "requireOptionalToolsOptIn": true, "allowNetworkSideEffects": false }
        }
      }
    }
  }
}
EOF_LOCAL
}

config_global() {
  cat <<'EOF_GLOBAL'
{
  "plugins": {
    "entries": {
      "consensus-tools": {
        "enabled": true,
        "config": {
          "mode": "global",
          "global": { "baseUrl": "https://your-consensus-tools-host.example", "accessToken": "YOUR_ACCESS_TOKEN" },
          "agentIdentity": { "agentIdSource": "openclaw", "manualAgentId": "" },
          "safety": { "requireOptionalToolsOptIn": true, "allowNetworkSideEffects": false }
        }
      }
    }
  }
}
EOF_GLOBAL
}

case "${1:-}" in
  commands)
    commands
    ;;
  config-local)
    config_local
    ;;
  config-global)
    config_global
    ;;
  ""|help|-h|--help)
    usage
    ;;
  *)
    echo "Unknown option: ${1}" >&2
    usage
    exit 1
    ;;
esac
