#!/usr/bin/env bash
# Verify Ollama embeddings endpoint with selected model.
# Checks: model exists in Ollama → endpoint reachable → valid embedding response.
set -euo pipefail
IFS=$'\n\t'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMMON_SH="${SCRIPT_DIR}/lib/common.sh"
CONFIG_CLI="${SCRIPT_DIR}/lib/config.js"
if [ ! -f "${COMMON_SH}" ]; then
  echo "[ERROR] Missing shared helper: ${COMMON_SH}" >&2
  exit 1
fi
if [ ! -f "${CONFIG_CLI}" ]; then
  echo "[ERROR] Missing config helper: ${CONFIG_CLI}" >&2
  exit 1
fi
source "${COMMON_SH}"

MODEL=""
BASE_URL=""
CONFIG_PATH="${OPENCLAW_CONFIG_PATH:-${HOME}/.openclaw/openclaw.json}"
VERBOSE=0
TMP_BODY=""
TMP_ERR=""

usage() {
  cat <<'EOF'
Usage:
  verify.sh [--model <id>] [--base-url <url>] [--openclaw-config <path>] [--verbose]

Verifies that the configured Ollama embeddings endpoint is working correctly.

Behavior:
  - If --model is omitted, reads memorySearch.model from OpenClaw config.
  - If --base-url is omitted, reads memorySearch.remote.baseUrl from config,
    then defaults to http://127.0.0.1:11434/v1/
  - Checks: (1) model exists in Ollama, (2) endpoint returns valid embedding.
  - Use --verbose to dump raw API response on failure.
EOF
}

while [ $# -gt 0 ]; do
  case "$1" in
    --model) MODEL="$2"; shift 2 ;;
    --base-url) BASE_URL="$2"; shift 2 ;;
    --openclaw-config) CONFIG_PATH="$2"; shift 2 ;;
    --verbose) VERBOSE=1; shift ;;
    --help|-h) usage; exit 0 ;;
    *) echo "Unknown option: $1"; usage; exit 1 ;;
  esac
done

cleanup() {
  if [ -n "${TMP_BODY:-}" ] && [ -f "${TMP_BODY:-}" ]; then
    rm -f "${TMP_BODY}"
  fi
  if [ -n "${TMP_ERR:-}" ] && [ -f "${TMP_ERR:-}" ]; then
    rm -f "${TMP_ERR}"
  fi
}
trap cleanup EXIT INT TERM

require_cmd node
require_cmd curl

# ── Read config if needed ────────────────────────────────────────────────────

if [ -z "$MODEL" ] || [ -z "$BASE_URL" ]; then
  MAP_OUTPUT="$(node "${CONFIG_CLI}" resolve-model-base "${CONFIG_PATH}")"
  CFG_MODEL="$(printf "%s\n" "$MAP_OUTPUT" | sed -n '1p')"
  CFG_BASE_URL="$(printf "%s\n" "$MAP_OUTPUT" | sed -n '2p')"
  [ -z "$MODEL" ] && MODEL="$CFG_MODEL"
  [ -z "$BASE_URL" ] && BASE_URL="$CFG_BASE_URL"
fi

if [ -z "$MODEL" ]; then
  echo "ERROR: Could not determine embedding model."
  echo "  Provide --model <id> or configure memorySearch.model in ${CONFIG_PATH}"
  exit 1
fi

# Normalize model tag
MODEL="$(normalize_model "$MODEL")"

# Normalize URL to .../v1 and call /embeddings
BASE_URL="${BASE_URL%/}"
if [[ "$BASE_URL" != */v1 ]]; then
  BASE_URL="${BASE_URL}/v1"
fi
EMBED_URL="${BASE_URL}/embeddings"

echo "Checking Ollama embeddings:"
echo "  URL:   ${EMBED_URL}"
echo "  Model: ${MODEL}"

# ── Step 1: Check model exists in Ollama ─────────────────────────────────────

echo ""
echo "  [1/2] Checking model availability in Ollama..."
if command -v ollama >/dev/null 2>&1; then
  if ! ollama list 2>/dev/null | awk 'NR>1{print $1}' | grep -qFx "${MODEL}" 2>/dev/null && \
     ! ollama list 2>/dev/null | awk 'NR>1{print $1}' | grep -qFx "${MODEL%%:*}" 2>/dev/null; then
    echo "  WARNING: model '${MODEL}' not found in 'ollama list'."
    echo "  The model may not be pulled. Try: ollama pull ${MODEL%%:*}"
    echo ""
    echo "  Continuing with endpoint check anyway..."
  else
    echo "  Model '${MODEL}' found in Ollama."
  fi
else
  echo "  NOTE: 'ollama' CLI not in PATH; skipping model existence check."
fi

# ── Step 2: Call embeddings endpoint ─────────────────────────────────────────

echo "  [2/2] Calling embeddings endpoint..."

PAYLOAD=$(cat <<EOF
{"model":"${MODEL}","input":"openclaw memory embeddings health check"}
EOF
)

HTTP_CODE=""
RESP=""

# Capture HTTP status and response body without mixing stderr into status code.
TMP_BODY="$(mktemp)"
TMP_ERR="$(mktemp)"
set +e
HTTP_CODE="$(curl -sS -o "$TMP_BODY" -w "%{http_code}" \
  -H "Content-Type: application/json" \
  -d "$PAYLOAD" \
  "$EMBED_URL" 2>"$TMP_ERR")"
CURL_STATUS=$?
set -e

RESP="$(<"$TMP_BODY")"
CURL_ERR="$(<"$TMP_ERR")"

if [ "$CURL_STATUS" -ne 0 ]; then
  echo "  ERROR: curl failed to reach ${EMBED_URL}"
  echo "  Is Ollama running? Check: curl http://127.0.0.1:11434/api/tags"
  if [ "$VERBOSE" -eq 1 ] && [ -n "$CURL_ERR" ]; then
    echo "  curl error: ${CURL_ERR}"
  fi
  exit 1
fi

if [ "$HTTP_CODE" != "200" ]; then
  echo "  ERROR: embeddings endpoint returned HTTP ${HTTP_CODE}"
  if [ "$VERBOSE" -eq 1 ] && [ -n "$RESP" ]; then
    echo ""
    echo "  Raw response (first 2000 chars):"
    echo "  ${RESP:0:2000}"
  fi
  # Try to extract error message
  if [ -n "$RESP" ]; then
    ERR_MSG="$(echo "$RESP" | node -e '
      let d=""; process.stdin.on("data",c=>d+=c); process.stdin.on("end",()=>{
        try { const j=JSON.parse(d); console.log(j.error||j.message||""); } catch { console.log(""); }
      });
    ' 2>/dev/null)" || true
    if [ -n "$ERR_MSG" ]; then
      echo "  Server error: ${ERR_MSG}"
    fi
  fi
  exit 1
fi

node - "$TMP_BODY" "$VERBOSE" <<'NODEOF'
const fs = require("fs");
const bodyPath = process.argv[2];
const verbose = process.argv[3] === "1";
const raw = fs.readFileSync(bodyPath, "utf8");
let body;
try { body = JSON.parse(raw); } catch {
  console.error("  ERROR: embeddings endpoint did not return valid JSON.");
  if (verbose) {
    console.error("  Raw response (first 2000 chars):");
    console.error("  " + raw.slice(0, 2000));
  }
  process.exit(1);
}

const arr = body?.data?.[0]?.embedding;
if (!Array.isArray(arr) || arr.length === 0) {
  console.error("  ERROR: embeddings response missing data[0].embedding.");
  console.error("  Top-level keys: " + Object.keys(body).join(", "));
  if (verbose) {
    console.error("  Raw response (first 2000 chars):");
    console.error("  " + raw.slice(0, 2000));
  }
  process.exit(1);
}
console.log(`  OK: received embedding vector (dims=${arr.length})`);
NODEOF
