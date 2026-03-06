#!/bin/bash
# Gather OpenClaw configuration for security analysis
# Outputs sanitized JSON (removes sensitive tokens)

CONFIG_FILE="${OPENCLAW_CONFIG:-$HOME/.openclaw/openclaw.json}"

if [ ! -f "$CONFIG_FILE" ]; then
    echo '{"error": "Config file not found", "path": "'"$CONFIG_FILE"'"}'
    exit 1
fi

# Read config and redact sensitive fields
cat "$CONFIG_FILE" | jq '
  # Redact tokens and passwords
  walk(
    if type == "object" then
      with_entries(
        if (.key | test("token|password|secret|apiKey|appToken|botToken"; "i")) then
          .value = "[REDACTED]"
        else
          .
        end
      )
    else
      .
    end
  )
'
