#!/usr/bin/env bash
# redact-secrets.sh — Detect and redact secrets from file content before sending to model
#
# Usage:
#   redact-secrets.sh <file>              # prints redacted content to stdout, map to fd 3
#   redact-secrets.sh --check <file>      # exits 0 if secrets found, 1 if clean
#   redact-secrets.sh --restore           # reads redacted file from stdin, map from --map-file,
#                                         # outputs restored content to stdout
#
# Security model:
#   - The redaction map is ONLY emitted to fd 3 when explicitly opened by the caller.
#   - If fd 3 is not open, the script aborts with an error rather than falling back to stderr.
#     This prevents the map from leaking into logs or shell output.
#   - No map data is written to disk, stdout, or any other stream.
#   - Caller must open fd 3 before invoking: exec 3>map_holder; ./redact-secrets.sh file
#
# Patterns detected:
#   - API keys (sk-, pk-, ghp_, ghs_, xoxb-, xoxp-, AKIA, etc.)
#   - Bearer/Basic auth tokens
#   - Private keys (RSA, EC, etc.)
#   - Connection strings with passwords
#   - Config values for password/secret/token/apiKey fields

set -euo pipefail

MODE="${1:---redact}"

# Secret patterns (PCRE-style, used with grep -P)
SECRET_PATTERNS=(
  'sk-[a-zA-Z0-9]{20,}'
  'sk-ant-[a-zA-Z0-9_-]{20,}'
  'sk-proj-[a-zA-Z0-9_-]{20,}'
  'pk-[a-zA-Z0-9]{20,}'
  'ghp_[a-zA-Z0-9]{36,}'
  'ghs_[a-zA-Z0-9]{36,}'
  'github_pat_[a-zA-Z0-9_]{20,}'
  'xoxb-[a-zA-Z0-9-]+'
  'xoxp-[a-zA-Z0-9-]+'
  'AKIA[0-9A-Z]{16}'
  'glpat-[a-zA-Z0-9_-]{20,}'
  'npm_[a-zA-Z0-9]{36,}'
  'Bearer [a-zA-Z0-9._\-]{20,}'
  'Basic [a-zA-Z0-9+/=]{20,}'
  '-----BEGIN (RSA |EC |OPENSSH |)PRIVATE KEY-----'
  '(mysql|postgres|mongodb|redis)://[^:]+:[^@]+@'
  'password\s*[:=]\s*"[^"]{8,}"'
  'secret\s*[:=]\s*"[^"]{8,}"'
  'token\s*[:=]\s*"[^"]{20,}"'
  'apiKey\s*[:=]\s*"[^"]{20,}"'
  'api_key\s*[:=]\s*"[^"]{20,}"'
)

if [[ "$MODE" == "--check" ]]; then
  FILE="$2"
  if [[ ! -f "$FILE" ]]; then
    echo "Error: File not found: $FILE" >&2
    exit 2
  fi
  for pattern in "${SECRET_PATTERNS[@]}"; do
    if grep -qP "$pattern" "$FILE" 2>/dev/null; then
      echo "SECRET DETECTED: $pattern"
      exit 0
    fi
  done
  exit 1
fi

if [[ "$MODE" == "--restore" ]]; then
  # --restore --map-file <path>
  # Reads redacted content from stdin, restores using plaintext map file (caller manages lifecycle)
  MAP_FILE=""
  shift
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --map-file) MAP_FILE="$2"; shift 2 ;;
      *) echo "Error: unknown arg: $1" >&2; exit 2 ;;
    esac
  done
  if [[ -z "$MAP_FILE" || ! -f "$MAP_FILE" ]]; then
    echo "Error: --map-file required and must exist" >&2
    exit 2
  fi
  content=$(cat)
  while IFS=$'\t' read -r placeholder original; do
    [[ -z "$placeholder" ]] && continue
    content="${content//$placeholder/$original}"
  done < "$MAP_FILE"
  echo "$content"
  exit 0
fi

# Default: redact mode
FILE="$1"
if [[ ! -f "$FILE" ]]; then
  echo "Error: File not found: $FILE" >&2
  exit 2
fi

# SECURITY: Verify fd 3 is open before proceeding. If not, abort.
# This prevents the redaction map from leaking to stderr/logs.
if ! { true >&3; } 2>/dev/null; then
  echo "Error: fd 3 is not open. The caller must open fd 3 to receive the redaction map." >&2
  echo "Example: exec 3>\"\$map_tmpfile\"; ./redact-secrets.sh file; exec 3>&-" >&2
  exit 2
fi

content=$(cat "$FILE")
counter=0
map_lines=""

for pattern in "${SECRET_PATTERNS[@]}"; do
  while IFS= read -r match; do
    if [[ -n "$match" ]]; then
      counter=$((counter + 1))
      placeholder="[REDACTED_${counter}]"
      map_lines+="${placeholder}"$'\t'"${match}"$'\n'
      content="${content//$match/$placeholder}"
    fi
  done < <(grep -oP "$pattern" <<< "$content" 2>/dev/null || true)
done

# Redacted content to stdout
printf '%s\n' "$content"

# Map to fd 3 ONLY — never to stderr
printf '%s' "$map_lines" >&3

if [[ $counter -gt 0 ]]; then
  echo "--- Redacted $counter secret(s)" >&2
fi
