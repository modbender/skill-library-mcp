#!/usr/bin/env bash
# ipeaky v5 — detect_test_config.sh
# Usage: bash detect_test_config.sh <SERVICE_NAME>
# Prints the test config JSON for the given service.
# If a saved config exists in ~/.ipeaky/test-configs/, uses it.
# Otherwise generates a best-guess config and saves it.
# If the service is unknown, writes a stub (url='') and exits 0.

set -euo pipefail

SERVICE="${1:?Usage: detect_test_config.sh <SERVICE_NAME>}"
CONFIG_DIR="$HOME/.ipeaky/test-configs"
CONFIG_FILE="$CONFIG_DIR/${SERVICE}.json"

mkdir -p "$CONFIG_DIR"

# If a saved config exists, print it and exit
if [ -f "$CONFIG_FILE" ]; then
  cat "$CONFIG_FILE"
  exit 0
fi

# Generate best-guess config based on service name
_PYEOF_TMP=$(mktemp /tmp/ipeaky_detect_XXXXXX.py)
cat > "$_PYEOF_TMP" <<'PYEOF'
import sys
import json
import os

service = sys.argv[1].upper()
config_file = sys.argv[2]

# Known provider patterns
def make_config(service_raw):
    s = service_raw.upper()

    if "OPENAI" in s:
        return {
            "service": service_raw,
            "url": "https://api.openai.com/v1/models",
            "method": "GET",
            "headers": ["Authorization: Bearer {{KEY}}"],
            "body": None,
            "expected_status": 200
        }

    if "ANTHROPIC" in s:
        return {
            "service": service_raw,
            "url": "https://api.anthropic.com/v1/messages",
            "method": "POST",
            "headers": [
                "x-api-key: {{KEY}}",
                "anthropic-version: 2023-06-01",
                "Content-Type: application/json"
            ],
            "body": json.dumps({
                "model": "claude-3-haiku-20240307",
                "max_tokens": 1,
                "messages": [{"role": "user", "content": "hi"}]
            }),
            "expected_status": 200
        }

    if "ELEVENLABS" in s or "ELEVEN_LABS" in s:
        return {
            "service": service_raw,
            "url": "https://api.elevenlabs.io/v1/user",
            "method": "GET",
            "headers": ["xi-api-key: {{KEY}}"],
            "body": None,
            "expected_status": 200
        }

    if "BRAVE" in s:
        return {
            "service": service_raw,
            "url": "https://api.search.brave.com/res/v1/web/search?q=test&count=1",
            "method": "GET",
            "headers": ["X-Subscription-Token: {{KEY}}"],
            "body": None,
            "expected_status": 200
        }

    if "GEMINI" in s:
        return {
            "service": service_raw,
            "url": "https://generativelanguage.googleapis.com/v1/models",
            "method": "GET",
            "headers": ["x-goog-api-key: {{KEY}}"],
            "body": None,
            "expected_status": 200
        }

    # Unknown service — stub
    return {
        "service": service_raw,
        "url": "",
        "method": "GET",
        "headers": ["Authorization: Bearer {{KEY}}"],
        "body": None,
        "expected_status": 200
    }

config = make_config(service)

os.makedirs(os.path.dirname(config_file), exist_ok=True)
with open(config_file, "w") as f:
    json.dump(config, f, indent=2)

print(json.dumps(config, indent=2))
PYEOF
python3 "$_PYEOF_TMP" "$SERVICE" "$CONFIG_FILE"
rm -f "$_PYEOF_TMP"
