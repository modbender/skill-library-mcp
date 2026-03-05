#!/usr/bin/env bash
set -euo pipefail

# Standalone trigger script for OpenClaw Phone Receipt skill.
#
# Required env vars:
# - ELEVENLABS_API_KEY
# - ELEVENLABS_AGENT_ID
# - ELEVENLABS_OUTBOUND_PHONE_ID
# - TO_NUMBER (E.164, e.g. +639178688896)
#
# Optional:
# - ENV_FILE (default: workspace/.env.elevenlabs-call)

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../" && pwd)"
ENV_FILE="${ENV_FILE:-$ROOT/.env.elevenlabs-call}"

if [[ -f "$ENV_FILE" ]]; then
  # shellcheck disable=SC1090
  set -a; source "$ENV_FILE"; set +a
fi

: "${ELEVENLABS_API_KEY:?Missing ELEVENLABS_API_KEY}"
: "${ELEVENLABS_AGENT_ID:?Missing ELEVENLABS_AGENT_ID}"
: "${ELEVENLABS_OUTBOUND_PHONE_ID:?Missing ELEVENLABS_OUTBOUND_PHONE_ID}"
: "${TO_NUMBER:?Missing TO_NUMBER}"

payload=$(python3 - <<'PY'
import json, os
print(json.dumps({
  "agent_id": os.environ["ELEVENLABS_AGENT_ID"],
  "agent_phone_number_id": os.environ["ELEVENLABS_OUTBOUND_PHONE_ID"],
  "to_number": os.environ["TO_NUMBER"],
}))
PY
)

resp=$(curl -sS -X POST "https://api.elevenlabs.io/v1/convai/twilio/outbound-call" \
  -H "xi-api-key: ${ELEVENLABS_API_KEY}" \
  -H "Content-Type: application/json" \
  -d "$payload")

python3 - <<'PY' "$resp"
import json, sys
raw = sys.argv[1]
try:
    data = json.loads(raw)
except Exception:
    print(raw)
    raise SystemExit(0)

cid = data.get("conversation_id") or data.get("conversationId")
if cid:
    print(f"[OK] outbound call initiated, conversation_id={cid}")
    raise SystemExit(0)

print(json.dumps(data, ensure_ascii=False, indent=2))
if data.get("success") is False or data.get("error") or data.get("detail"):
    raise SystemExit(1)
PY
