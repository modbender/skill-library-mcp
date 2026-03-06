#!/usr/bin/env bash
# ipeaky - Test an API key by calling the provider's API
# Usage: echo "KEY_VALUE" | ./test_key.sh <SERVICE>
# Reads key from stdin. Never prints the full key.
# Keys are passed via temp header files (NOT as CLI args) to avoid ps-aux exposure.

set -euo pipefail

SERVICE="${1:?Usage: echo KEY | test_key.sh <SERVICE>}"
KEY=$(cat)

if [ -z "$KEY" ]; then
  echo "ERROR: No key provided on stdin"
  exit 1
fi

MASKED="${KEY:0:4}****"

# --- Secure header file helper ---
# Writes curl header(s) to a chmod-600 temp file; caller must rm it.
make_header_file() {
  local hfile
  hfile=$(mktemp)
  chmod 600 "$hfile"
  printf '%s\n' "$@" > "$hfile"
  echo "$hfile"
}

case "$SERVICE" in
  OPENAI_API_KEY|openai)
    HFILE=$(make_header_file "Authorization: Bearer $KEY")
    RESP=$(curl -s -w "\n%{http_code}" -H @"$HFILE" "https://api.openai.com/v1/models" 2>/dev/null)
    rm -f "$HFILE"
    CODE=$(echo "$RESP" | tail -1)
    if [ "$CODE" = "200" ]; then
      echo "OK: OpenAI key ($MASKED) is valid."
    else
      echo "FAIL: OpenAI key ($MASKED) returned HTTP $CODE."
      exit 1
    fi
    ;;
  ELEVENLABS_API_KEY|elevenlabs)
    HFILE=$(make_header_file "xi-api-key: $KEY")
    RESP=$(curl -s -w "\n%{http_code}" -H @"$HFILE" "https://api.elevenlabs.io/v1/user" 2>/dev/null)
    rm -f "$HFILE"
    CODE=$(echo "$RESP" | tail -1)
    if [ "$CODE" = "200" ]; then
      echo "OK: ElevenLabs key ($MASKED) is valid."
    else
      echo "FAIL: ElevenLabs key ($MASKED) returned HTTP $CODE."
      exit 1
    fi
    ;;
  ANTHROPIC_API_KEY|anthropic)
    HFILE=$(make_header_file "x-api-key: $KEY" "anthropic-version: 2023-06-01" "Content-Type: application/json")
    RESP=$(curl -s -w "\n%{http_code}" -H @"$HFILE" \
      "https://api.anthropic.com/v1/messages" \
      -d '{"model":"claude-3-haiku-20240307","max_tokens":1,"messages":[{"role":"user","content":"hi"}]}' 2>/dev/null)
    rm -f "$HFILE"
    CODE=$(echo "$RESP" | tail -1)
    if [ "$CODE" = "200" ]; then
      echo "OK: Anthropic key ($MASKED) is valid."
    else
      echo "FAIL: Anthropic key ($MASKED) returned HTTP $CODE."
      exit 1
    fi
    ;;
  BRAVE_API_KEY|brave)
    HFILE=$(make_header_file "X-Subscription-Token: $KEY")
    RESP=$(curl -s -w "\n%{http_code}" -H @"$HFILE" "https://api.search.brave.com/res/v1/web/search?q=test&count=1" 2>/dev/null)
    rm -f "$HFILE"
    CODE=$(echo "$RESP" | tail -1)
    if [ "$CODE" = "200" ]; then
      echo "OK: Brave Search key ($MASKED) is valid."
    else
      echo "FAIL: Brave Search key ($MASKED) returned HTTP $CODE."
      exit 1
    fi
    ;;
  GEMINI_API_KEY|gemini)
    # Use header auth instead of query param to avoid key exposure in URLs/logs
    HFILE=$(make_header_file "x-goog-api-key: $KEY")
    RESP=$(curl -s -w "\n%{http_code}" -H @"$HFILE" "https://generativelanguage.googleapis.com/v1/models" 2>/dev/null)
    rm -f "$HFILE"
    CODE=$(echo "$RESP" | tail -1)
    if [ "$CODE" = "200" ]; then
      echo "OK: Gemini key ($MASKED) is valid."
    else
      echo "FAIL: Gemini key ($MASKED) returned HTTP $CODE."
      exit 1
    fi
    ;;
  *)
    echo "OK: Key ($MASKED) stored. No built-in test for '$SERVICE'."
    ;;
esac
