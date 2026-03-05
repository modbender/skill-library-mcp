#!/usr/bin/env bash
set -euo pipefail

# Inject NotebookLM auth files for headless environments (AWS).
#
# Supported input methods:
# 1) NOTEBOOKLM_AUTH_SECRET_FILE (path to JSON payload file)
# 2) NOTEBOOKLM_AUTH_SECRET_JSON (raw JSON payload in env)
# 3) NOTEBOOKLM_AUTH_SECRET_ID + aws secretsmanager get-secret-value
#
# Expected secret JSON structure:
# {
#   "cookies": { "SID": "...", "HSID": "..." } OR [ { "name":"SID","value":"..." } ],
#   "metadata": {
#     "csrf_token": "",
#     "session_id": "",
#     "email": "user@example.com",
#     "last_validated": "2026-02-10T12:00:00"
#   }
# }
#
# The script writes:
#   $NOTEBOOKLM_MCP_CLI_PATH/profiles/default/cookies.json
#   $NOTEBOOKLM_MCP_CLI_PATH/profiles/default/metadata.json

if ! command -v jq >/dev/null 2>&1; then
  echo "Error: jq is required but not installed." >&2
  exit 1
fi

NOTEBOOKLM_MCP_CLI_PATH="${NOTEBOOKLM_MCP_CLI_PATH:-/opt/openclaw/notebooklm-auth}"
PROFILE_DIR="${NOTEBOOKLM_MCP_CLI_PATH}/profiles/default"
COOKIES_FILE="${PROFILE_DIR}/cookies.json"
METADATA_FILE="${PROFILE_DIR}/metadata.json"

mkdir -p "${PROFILE_DIR}"

SECRET_JSON=""

if [[ -n "${NOTEBOOKLM_AUTH_SECRET_FILE:-}" ]]; then
  if [[ ! -f "${NOTEBOOKLM_AUTH_SECRET_FILE}" ]]; then
    echo "Error: NOTEBOOKLM_AUTH_SECRET_FILE does not exist: ${NOTEBOOKLM_AUTH_SECRET_FILE}" >&2
    exit 1
  fi
  SECRET_JSON="$(cat "${NOTEBOOKLM_AUTH_SECRET_FILE}")"
elif [[ -n "${NOTEBOOKLM_AUTH_SECRET_JSON:-}" ]]; then
  SECRET_JSON="${NOTEBOOKLM_AUTH_SECRET_JSON}"
elif [[ -n "${NOTEBOOKLM_AUTH_SECRET_ID:-}" ]]; then
  if ! command -v aws >/dev/null 2>&1; then
    echo "Error: aws CLI is required when NOTEBOOKLM_AUTH_SECRET_ID is used." >&2
    exit 1
  fi

  AWS_REGION="${AWS_REGION:-${AWS_DEFAULT_REGION:-}}"
  if [[ -z "${AWS_REGION}" ]]; then
    echo "Error: set AWS_REGION or AWS_DEFAULT_REGION." >&2
    exit 1
  fi

  SECRET_JSON="$(aws secretsmanager get-secret-value \
    --secret-id "${NOTEBOOKLM_AUTH_SECRET_ID}" \
    --region "${AWS_REGION}" \
    --query SecretString \
    --output text)"
else
  echo "Error: set NOTEBOOKLM_AUTH_SECRET_FILE, NOTEBOOKLM_AUTH_SECRET_JSON, or NOTEBOOKLM_AUTH_SECRET_ID." >&2
  exit 1
fi

if [[ -z "${SECRET_JSON}" || "${SECRET_JSON}" == "None" ]]; then
  echo "Error: secret payload is empty." >&2
  exit 1
fi

# Validate minimum required structure.
if ! echo "${SECRET_JSON}" | jq -e '.cookies' >/dev/null 2>&1; then
  echo "Error: secret JSON must include .cookies" >&2
  exit 1
fi

# Write cookies.json exactly as provided under .cookies.
echo "${SECRET_JSON}" | jq '.cookies' > "${COOKIES_FILE}"

# metadata is optional; generate safe default if missing.
if echo "${SECRET_JSON}" | jq -e '.metadata' >/dev/null 2>&1; then
  echo "${SECRET_JSON}" | jq '.metadata' > "${METADATA_FILE}"
else
  jq -n \
    --arg now "$(date -u +"%Y-%m-%dT%H:%M:%S")" \
    '{csrf_token:"", session_id:"", email:null, last_validated:$now}' \
    > "${METADATA_FILE}"
fi

chmod 700 "${NOTEBOOKLM_MCP_CLI_PATH}" "${NOTEBOOKLM_MCP_CLI_PATH}/profiles" "${PROFILE_DIR}" || true
chmod 600 "${COOKIES_FILE}" "${METADATA_FILE}" || true

echo "NotebookLM auth injected to: ${PROFILE_DIR}"
echo "Set NOTEBOOKLM_MCP_CLI_PATH=${NOTEBOOKLM_MCP_CLI_PATH} for OpenClaw runtime."
