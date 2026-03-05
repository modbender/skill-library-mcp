#!/usr/bin/env bash

fund_request_line() {
  local amount="${1:-}"
  local reason="${2:-}"
  local info_json addr

  if [[ -z "$amount" ]]; then
    amount="0.05"
  fi
  if [[ -z "$reason" ]]; then
    reason="DID + storage init"
  fi

  info_json="$(safe_core_info_json)"
  addr="$(python3 - <<'PY' "$info_json"
import json, sys
info = json.loads(sys.argv[1])
print(info.get("wallet_address", ""))
PY
)"
  [[ -n "$addr" ]] || fatal "fund-request requires core node running (could not read wallet address)"
  echo "peaq-robotics fund-request: address=$addr amount=$amount PEAQ reason=\"$reason\""
}
