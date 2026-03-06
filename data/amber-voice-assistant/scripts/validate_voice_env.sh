#!/usr/bin/env bash
set -euo pipefail

# Lightweight preflight for Amber Voice Assistant deployments.
# Safe: prints missing values only (never prints secret contents).

required=(
  TWILIO_ACCOUNT_SID
  TWILIO_AUTH_TOKEN
  TWILIO_CALLER_ID
  OPENAI_API_KEY
  OPENAI_PROJECT_ID
  OPENAI_WEBHOOK_SECRET
  PUBLIC_BASE_URL
)

optional=(
  OPENCLAW_GATEWAY_URL
  OPENCLAW_GATEWAY_TOKEN
  REALTIME_MODEL
  TTS_MODEL
)

missing=0

echo "[amber-voice-assistant] Checking required env vars..."
for key in "${required[@]}"; do
  if [[ -z "${!key:-}" ]]; then
    echo "  ✗ missing: $key"
    missing=1
  else
    echo "  ✓ $key"
  fi
done

echo "[amber-voice-assistant] Checking optional env vars..."
for key in "${optional[@]}"; do
  if [[ -z "${!key:-}" ]]; then
    echo "  - not set: $key"
  else
    echo "  ✓ $key"
  fi
done

echo "[amber-voice-assistant] Tool checks..."
if command -v node >/dev/null 2>&1; then
  echo "  ✓ node $(node -v)"
else
  echo "  ✗ node missing"
  missing=1
fi

if command -v openclaw >/dev/null 2>&1; then
  echo "  ✓ openclaw $(openclaw --version | head -n1)"
else
  echo "  - openclaw CLI not found in PATH"
fi

if [[ "$missing" -eq 1 ]]; then
  echo "[amber-voice-assistant] Preflight failed. Set missing required env vars."
  exit 1
fi

echo "[amber-voice-assistant] Preflight passed."
