#!/usr/bin/env bash
set -euo pipefail

echo "[amber-voice-assistant] Quickstart setup"
echo "1) Copy references/env.example to your own .env and replace placeholders."

env_example_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/references"
if [[ -f "$env_example_dir/env.example" ]]; then
  echo "   Example file: $env_example_dir/env.example"
fi

echo "2) Export required vars (TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_CALLER_ID, OPENAI_API_KEY, OPENAI_PROJECT_ID, OPENAI_WEBHOOK_SECRET, PUBLIC_BASE_URL)."
echo "3) Run preflight validator..."
"$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/validate_voice_env.sh"

echo "4) Personalize voice assistant values (name/greeting/safety policy)."
echo "5) Run one inbound/outbound smoke call before production use."

echo "[amber-voice-assistant] Quickstart complete."
