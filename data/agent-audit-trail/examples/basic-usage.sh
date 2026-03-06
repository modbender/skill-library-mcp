#!/bin/bash
# Basic usage examples for agent-audit-trail

SCRIPT="../scripts/auditlog.py"

echo "=== Agent Audit Trail Examples ==="
echo

# Create audit directory
mkdir -p audit

# Example 1: Simple file operation log
echo "1. Logging a file write..."
$SCRIPT append \
  --kind "file-write" \
  --summary "Created configuration file" \
  --target "config.yaml" \
  --domain "personal"

echo

# Example 2: Command execution with details
echo "2. Logging a command execution..."
$SCRIPT append \
  --kind "exec" \
  --summary "Ran git status" \
  --target "git status" \
  --domain "dev" \
  --details '{"exit_code": 0, "duration_ms": 150}'

echo

# Example 3: API call with provenance
echo "3. Logging an API call..."
$SCRIPT append \
  --kind "api-call" \
  --summary "Fetched weather data" \
  --target "https://api.weather.example/v1/current" \
  --domain "personal" \
  --provenance '{"source": "telegram", "message_id": "12345", "user": "roosch"}'

echo

# Example 4: Gated action (requires approval)
echo "4. Logging a gated action..."
$SCRIPT append \
  --kind "external-write" \
  --summary "Posted tweet about project launch" \
  --target "https://x.com/status/987654321" \
  --domain "agirails" \
  --gate "approval-2026-02-05-001" \
  --provenance '{"channel": "telegram", "approved_by": "roosch"}'

echo

# Example 5: Verify the chain
echo "5. Verifying audit log integrity..."
$SCRIPT verify

echo
echo "=== Log contents ==="
cat audit/agent-actions.ndjson | python3 -m json.tool --compact 2>/dev/null || cat audit/agent-actions.ndjson
