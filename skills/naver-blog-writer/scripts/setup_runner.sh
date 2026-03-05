#!/usr/bin/env bash
set -euo pipefail

SETUP_URL="${SETUP_URL:-}"
PROOF_TOKEN="${PROOF_TOKEN:-}"
SETUP_ISSUE_URL="${SETUP_ISSUE_URL:-}"
DEVICE_FINGERPRINT="${DEVICE_FINGERPRINT:-$(hostname)-$(uname -s)-$(uname -m)}"
AUTO_SERVICE="${AUTO_SERVICE:-both}"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --setup-url)
      SETUP_URL="$2"
      shift 2
      ;;
    --proof-token)
      PROOF_TOKEN="$2"
      shift 2
      ;;
    --setup-issue-url)
      SETUP_ISSUE_URL="$2"
      shift 2
      ;;
    --device-fingerprint)
      DEVICE_FINGERPRINT="$2"
      shift 2
      ;;
    --auto-service)
      AUTO_SERVICE="$2"
      shift 2
      ;;
    *)
      echo "unknown arg: $1" >&2
      exit 1
      ;;
  esac
done

if [[ -z "$SETUP_URL" && ( -z "$PROOF_TOKEN" || -z "$SETUP_ISSUE_URL" ) ]]; then
  echo '{"error":"setup_url required or proof_token+setup_issue_url required"}'
  exit 1
fi

runner_cmd=(npx @y80163442/naver-thin-runner setup)

if [[ -n "$SETUP_URL" ]]; then
  runner_cmd+=(--setup-url "$SETUP_URL")
else
  runner_cmd+=(--proof-token "$PROOF_TOKEN" --setup-issue-url "$SETUP_ISSUE_URL" --device-fingerprint "$DEVICE_FINGERPRINT")
fi

runner_cmd+=(--auto-service "$AUTO_SERVICE")
"${runner_cmd[@]}"

echo '{"ok":true,"next_action":"RUN_LOGIN_ONCE","hint":"npx @y80163442/naver-thin-runner login"}'
