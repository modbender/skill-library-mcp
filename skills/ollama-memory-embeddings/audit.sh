#!/usr/bin/env bash
# Read-only audit: report commands, config drift, and recommended actions (no execution).
# Output: JSON per AUDIT_REPORT_CONTRACT (schemaVersion 1.0.0).
set -euo pipefail
IFS=$'\n\t'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMMON_SH="${SCRIPT_DIR}/lib/common.sh"
CONFIG_CLI="${SCRIPT_DIR}/lib/config.js"
if [ ! -f "${COMMON_SH}" ] || [ ! -f "${CONFIG_CLI}" ]; then
  echo '{"schemaVersion":"1.0.0","status":"fail","error":"missing lib"}' >&2
  exit 1
fi
source "${COMMON_SH}"

CONFIG_PATH="${OPENCLAW_CONFIG_PATH:-${HOME}/.openclaw/openclaw.json}"
AUDIT_MODEL="${AUDIT_MODEL:-embeddinggemma:latest}"
AUDIT_BASE_URL="${AUDIT_BASE_URL:-http://127.0.0.1:11434/v1/}"
OUTPUT_FORMAT="${AUDIT_OUTPUT:-json}"

require_cmd node

# Normalize base URL for comparison (trailing /v1/)
_normalize_url() {
  local u="${1%/}"
  [[ "$u" != */v1 ]] && u="${u}/v1"
  echo "${u}/"
}

AUDIT_BASE_NORM="$(normalize_base_url "$AUDIT_BASE_URL")"

# Detect a single command: path and version (first line of --version or similar).
_detect_cmd() {
  local name="$1"
  local required="${2:-1}"
  local path version
  path="$(command -v "$name" 2>/dev/null)" || true
  if [ -z "$path" ]; then
    printf 'missing\t\t\t%s\n' "$required"
    return
  fi
  version=""
  case "$name" in
    node)   version="$("$path" --version 2>/dev/null | head -n1 | tr -d '\n')" || true ;;
    ollama) version="$("$path" --version 2>/dev/null | head -n1 | tr -d '\n')" || true ;;
    curl)   version="$("$path" --version 2>/dev/null | head -n1 | tr -d '\n')" || true ;;
    openclaw) version="$("$path" --version 2>/dev/null | head -n1 | tr -d '\n')" || version="unknown" ;;
    *)      version="unknown" ;;
  esac
  printf 'detected\t%s\t%s\t%s\n' "$path" "${version:-unknown}" "$required"
}

# Build commands.detected, .missing, .broken (sorted).
detected=()
missing=()
broken=()

for cmd in node ollama curl openclaw; do
  required=1
  [ "$cmd" = "openclaw" ] && required=0
  IFS=$'\t' read -r status path version req < <( _detect_cmd "$cmd" "$required" )
  if [ "$status" = "missing" ]; then
    if [ "$req" -eq 1 ]; then
      broken+=( "$(printf '{"name":"%s","required":true}' "$cmd")" )
    else
      missing+=( "$(printf '{"name":"%s","required":false}' "$cmd")" )
    fi
  else
    detected+=( "$(printf '{"name":"%s","path":"%s","version":"%s"}' "$cmd" "${path//\"/\\\"}" "${version//\"/\\\"}")" )
  fi
done

# Drift: run config.js check-drift
drift_detected="false"
drift_json="null"
if [ -f "$CONFIG_PATH" ]; then
  set +e
  node "${CONFIG_CLI}" check-drift "${CONFIG_PATH}" "${AUDIT_MODEL}" "${AUDIT_BASE_NORM}" >/dev/null 2>&1
  drift_status=$?
  set -e
  if [ "$drift_status" -eq 10 ]; then
    drift_detected="true"
    current_fp="$(node "${CONFIG_CLI}" fingerprint "$CONFIG_PATH")"
    drift_json="$(printf '{"detected":true,"expected":{"provider":"openai","model":"%s","baseUrl":"%s","apiKeyPolicy":"non-empty"},"actual":%s}' "$AUDIT_MODEL" "$AUDIT_BASE_NORM" "$current_fp")"
  fi
else
  drift_detected="true"
  drift_json='{"detected":true,"error":"config file not found"}'
fi

# Status and summary
status="ok"
issues_total=0
critical=0
high=0
medium=0
low=0
if [ ${#broken[@]} -gt 0 ]; then
  status="fail"
  critical=${#broken[@]}
  issues_total=$((issues_total + critical))
fi
if [ "$drift_detected" = "true" ]; then
  [ "$status" = "ok" ] && status="warn"
  high=$((high + 1))
  issues_total=$((issues_total + 1))
fi
if [ ${#missing[@]} -gt 0 ]; then
  [ "$status" = "ok" ] && status="warn"
  low=$((low + ${#missing[@]}))
  issues_total=$((issues_total + ${#missing[@]}))
fi

# Recommended actions (audit-only: never autoExecutable)
recommended=()
if [ "$drift_detected" = "true" ]; then
  recommended+=( '{"id":"fix_drift","priority":"high","description":"Run enforce.sh to apply desired memorySearch config","autoExecutable":false}' )
fi
if [ ${#broken[@]} -gt 0 ]; then
  recommended+=( '{"id":"install_missing_commands","priority":"high","description":"Install missing required commands (node, ollama, curl)","autoExecutable":false}' )
fi

# Sort recommended by priority then id (already ordered)
# Build JSON arrays (bash 4+ associative order; we build by hand for portability)
detected_str="["
for i in "${!detected[@]}"; do
  [ "$i" -gt 0 ] && detected_str+=","
  detected_str+="${detected[$i]}"
done
detected_str+="]"

missing_str="["
for i in "${!missing[@]}"; do
  [ "$i" -gt 0 ] && missing_str+=","
  missing_str+="${missing[$i]}"
done
missing_str+="]"

broken_str="["
for i in "${!broken[@]}"; do
  [ "$i" -gt 0 ] && broken_str+=","
  broken_str+="${broken[$i]}"
done
broken_str+="]"

rec_str="["
for i in "${!recommended[@]}"; do
  [ "$i" -gt 0 ] && rec_str+=","
  rec_str+="${recommended[$i]}"
done
rec_str+="]"

generated_at="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
host="$(hostname 2>/dev/null || echo "unknown")"
os="$(uname -s 2>/dev/null || echo "unknown")"
arch="$(uname -m 2>/dev/null || echo "unknown")"

# Emit single JSON object (one line for ndjson, or pretty for human)
if [ "$OUTPUT_FORMAT" = "text" ]; then
  status_upper="$(echo "$status" | tr '[:lower:]' '[:upper:]')"
  echo "Audit Status: ${status_upper} (${issues_total} findings: ${critical} critical, ${high} high, ${medium} medium, ${low} low)"
  echo ""
  echo "Environment:"
  echo "- Host: ${host} (${os}/${arch})"
  echo "- Config: ${CONFIG_PATH}"
  echo ""
  echo "Commands: detected ${#detected[@]}, missing ${#missing[@]}, broken ${#broken[@]}"
  echo ""
  if [ "$drift_detected" = "true" ]; then
    echo "Config Drift: detected (run enforce.sh to fix)"
  else
    echo "Config Drift: none"
  fi
  echo ""
  echo "Note: Audit-only mode did not execute any changes."
else
  cat <<EOF
{
  "schemaVersion": "1.0.0",
  "generatedAt": "${generated_at}",
  "tool": { "name": "ollama-memory-embeddings-audit", "version": "1.0.0" },
  "target": {
    "host": "${host}",
    "os": "${os}",
    "arch": "${arch}",
    "configPath": "${CONFIG_PATH}"
  },
  "status": "${status}",
  "summary": {
    "issuesTotal": ${issues_total},
    "critical": ${critical},
    "high": ${high},
    "medium": ${medium},
    "low": ${low}
  },
  "commands": {
    "detected": ${detected_str},
    "missing": ${missing_str},
    "broken": ${broken_str}
  },
  "drift": ${drift_json},
  "recommendedActions": ${rec_str},
  "notes": ["Audit-only mode did not execute any changes."]
}
EOF
fi

[ "$status" = "ok" ] && exit 0 || exit 1
