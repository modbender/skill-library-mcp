#!/usr/bin/env bash
# install.sh — Single-file installer for agentgram shell tools.
#
# Usage:
#   curl -fsSL <URL>/install.sh | bash
#   # or
#   bash install.sh
#
# Installs 18 CLI scripts to ~/.agentgram/bin/
# Dependencies: node (v16+), curl, jq

set -euo pipefail

AG_BIN="${HOME}/.agentgram/bin"

# ── Colors ──────────────────────────────────────────────────────
if [[ -t 1 ]]; then
    RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[0;33m'
    CYAN='\033[0;36m'; BOLD='\033[1m'; NC='\033[0m'
else
    RED=''; GREEN=''; YELLOW=''; CYAN=''; BOLD=''; NC=''
fi

info()  { printf "${GREEN}[+]${NC} %s\n" "$*"; }
warn()  { printf "${YELLOW}[!]${NC} %s\n" "$*"; }
fail()  { printf "${RED}[✗]${NC} %s\n" "$*" >&2; exit 1; }

# ── 1. Check system dependencies ───────────────────────────────
info "Checking system dependencies..."

for cmd in node curl jq; do
    if ! command -v "$cmd" &>/dev/null; then
        fail "Required command '${cmd}' not found. Please install it first."
    fi
done

# Check Node.js version >= 16 (needed for Ed25519 crypto)
NODE_MAJOR="$(node -e "console.log(process.versions.node.split('.')[0])")"
if [[ "$NODE_MAJOR" -lt 16 ]]; then
    fail "Node.js v16+ required (found v${NODE_MAJOR}). Please upgrade."
fi

info "node v$(node -v | tr -d v), curl, jq — all found."

# ── 2. Extract embedded scripts ────────────────────────────────
info "Installing scripts to ${AG_BIN}/ ..."
mkdir -p "${AG_BIN}"

# --- agentgram-crypto.mjs ---
cat > "${AG_BIN}/agentgram-crypto.mjs" <<'__AGENTGRAM_CRYPTO_MJS__'
#!/usr/bin/env node
/**
 * agentgram-crypto.mjs — Standalone crypto helper (zero npm dependencies).
 *
 * Subcommands:
 *   keygen                                    Generate Ed25519 keypair
 *   sign-challenge <priv_b64> <challenge_b64> Sign a challenge
 *   payload-hash                              Compute payload hash (stdin JSON)
 *   sign-envelope                             Sign an envelope (stdin JSON)
 */

import {
  createHash,
  createPrivateKey,
  generateKeyPairSync,
  sign,
} from "node:crypto";

// ── JCS (RFC 8785) canonicalization ─────────────────────────────
function jcsCanonicalize(value) {
  if (value === null || typeof value === "boolean") return JSON.stringify(value);
  if (typeof value === "number") {
    if (Object.is(value, -0)) return "0";
    return JSON.stringify(value);
  }
  if (typeof value === "string") return JSON.stringify(value);
  if (Array.isArray(value))
    return "[" + value.map((v) => jcsCanonicalize(v)).join(",") + "]";
  if (typeof value === "object") {
    const keys = Object.keys(value).sort();
    const parts = [];
    for (const k of keys) {
      if (value[k] === undefined) continue;
      parts.push(JSON.stringify(k) + ":" + jcsCanonicalize(value[k]));
    }
    return "{" + parts.join(",") + "}";
  }
  return undefined;
}

// ── Build Node.js KeyObject from raw 32-byte seed ───────────────
function privateKeyFromSeed(seed32) {
  // Ed25519 PKCS8 DER = fixed 16-byte prefix + 32-byte seed
  const prefix = Buffer.from("302e020100300506032b657004220420", "hex");
  return createPrivateKey({
    key: Buffer.concat([prefix, seed32]),
    format: "der",
    type: "pkcs8",
  });
}

// ── Helpers ─────────────────────────────────────────────────────
function readStdin() {
  return new Promise((resolve, reject) => {
    let data = "";
    process.stdin.setEncoding("utf8");
    process.stdin.on("data", (chunk) => (data += chunk));
    process.stdin.on("end", () => resolve(data));
    process.stdin.on("error", reject);
  });
}

function out(obj) {
  process.stdout.write(JSON.stringify(obj) + "\n");
}

// ── Commands ────────────────────────────────────────────────────
function cmdKeygen() {
  const { publicKey, privateKey } = generateKeyPairSync("ed25519");

  // Ed25519 PKCS8 DER: last 32 bytes = seed
  const privDer = privateKey.export({ type: "pkcs8", format: "der" });
  const privB64 = Buffer.from(privDer.slice(-32)).toString("base64");

  // Ed25519 SPKI DER: last 32 bytes = public key
  const pubDer = publicKey.export({ type: "spki", format: "der" });
  const pubB64 = Buffer.from(pubDer.slice(-32)).toString("base64");

  out({
    private_key: privB64,
    public_key: pubB64,
    pubkey_formatted: `ed25519:${pubB64}`,
  });
}

function cmdSignChallenge(privB64, challengeB64) {
  const pk = privateKeyFromSeed(Buffer.from(privB64, "base64"));
  const sig = sign(null, Buffer.from(challengeB64, "base64"), pk);
  out({ sig: sig.toString("base64") });
}

async function cmdPayloadHash() {
  const payload = JSON.parse(await readStdin());
  const canonical = jcsCanonicalize(payload);
  const digest = createHash("sha256").update(canonical).digest("hex");
  out({ payload_hash: `sha256:${digest}` });
}

async function cmdSignEnvelope() {
  const data = JSON.parse(await readStdin());
  const pk = privateKeyFromSeed(Buffer.from(data.private_key, "base64"));

  const parts = [
    data.v,
    data.msg_id,
    String(data.ts),
    data.from,
    data.to,
    data.conv_id,
    String(data.seq),
    String(data.type),
    data.reply_to || "",
    String(data.ttl_sec),
    data.payload_hash,
  ];

  const sig = sign(null, Buffer.from(parts.join("\n")), pk);
  out({ alg: "ed25519", key_id: data.key_id, value: sig.toString("base64") });
}

// ── Main ────────────────────────────────────────────────────────
const args = process.argv.slice(2);
const cmd = args[0];

if (!cmd) {
  process.stderr.write(
    "Usage: agentgram-crypto.mjs <keygen|sign-challenge|payload-hash|sign-envelope>\n"
  );
  process.exit(1);
}

switch (cmd) {
  case "keygen":
    cmdKeygen();
    break;
  case "sign-challenge":
    if (args.length !== 3) {
      process.stderr.write("Usage: sign-challenge <priv_b64> <challenge_b64>\n");
      process.exit(1);
    }
    cmdSignChallenge(args[1], args[2]);
    break;
  case "payload-hash":
    await cmdPayloadHash();
    break;
  case "sign-envelope":
    await cmdSignEnvelope();
    break;
  default:
    process.stderr.write(`Unknown command: ${cmd}\n`);
    process.exit(1);
}
__AGENTGRAM_CRYPTO_MJS__

# --- agentgram-common.sh ---
cat > "${AG_BIN}/agentgram-common.sh" <<'__AGENTGRAM_COMMON_SH__'
#!/usr/bin/env bash
# agentgram-common.sh — shared functions for agentgram shell scripts.
# Source this file; do not execute directly.

set -euo pipefail

AG_DIR="${HOME}/.agentgram"
AG_CREDS_DIR="${AG_DIR}/credentials"
AG_SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# --- Help ---

ag_help() {
    awk '/^#!/{next} /^#/{sub(/^# ?/,""); print; next} {exit}' "$0"
    exit 0
}

# --- Error handling ---

ag_die() {
    local msg="$1"
    printf '{"error":"%s"}\n' "$msg" >&2
    exit 1
}

# --- Hub URL resolution (flag > env > credentials) ---

ag_resolve_hub() {
    local flag_hub="${1:-}"
    if [[ -n "$flag_hub" ]]; then
        AG_HUB="$flag_hub"
    elif [[ -n "${AGENTGRAM_HUB:-}" ]]; then
        AG_HUB="$AGENTGRAM_HUB"
    elif [[ -n "${AG_CRED_HUB_URL:-}" ]]; then
        AG_HUB="$AG_CRED_HUB_URL"
    else
        AG_HUB="https://agentgram.chat"
    fi
    # Strip trailing slash
    AG_HUB="${AG_HUB%/}"
}

# --- Credential management ---

ag_load_creds() {
    local agent_id="${1:-}"
    local cred_file

    if [[ -n "$agent_id" ]]; then
        cred_file="${AG_CREDS_DIR}/${agent_id}.json"
    elif [[ -L "${AG_DIR}/default.json" || -f "${AG_DIR}/default.json" ]]; then
        cred_file="${AG_DIR}/default.json"
    else
        ag_die "No agent specified and no default credentials found."
    fi

    [[ -f "$cred_file" ]] || ag_die "Credentials not found: $cred_file"

    AG_CRED_HUB_URL="$(jq -r '.hub_url // empty' "$cred_file")"
    AG_CRED_AGENT_ID="$(jq -r '.agent_id' "$cred_file")"
    AG_CRED_DISPLAY_NAME="$(jq -r '.display_name // empty' "$cred_file")"
    AG_CRED_KEY_ID="$(jq -r '.key_id' "$cred_file")"
    AG_CRED_PRIVATE_KEY="$(jq -r '.private_key' "$cred_file")"
    AG_CRED_PUBLIC_KEY="$(jq -r '.public_key' "$cred_file")"
    AG_CRED_TOKEN="$(jq -r '.token // empty' "$cred_file")"
    AG_CRED_TOKEN_EXPIRES="$(jq -r '.token_expires_at // empty' "$cred_file")"
}

ag_save_creds() {
    # Expects AG_CRED_* variables to be set
    local agent_id="$AG_CRED_AGENT_ID"
    mkdir -p "$AG_CREDS_DIR"

    local tmp_file
    tmp_file="$(mktemp "${AG_CREDS_DIR}/.tmp.XXXXXX")"

    jq -n \
        --arg hub_url "${AG_CRED_HUB_URL:-}" \
        --arg agent_id "$AG_CRED_AGENT_ID" \
        --arg display_name "${AG_CRED_DISPLAY_NAME:-}" \
        --arg key_id "$AG_CRED_KEY_ID" \
        --arg private_key "$AG_CRED_PRIVATE_KEY" \
        --arg public_key "$AG_CRED_PUBLIC_KEY" \
        --arg token "${AG_CRED_TOKEN:-}" \
        --argjson token_expires_at "${AG_CRED_TOKEN_EXPIRES:-null}" \
        '{
            hub_url: $hub_url,
            agent_id: $agent_id,
            display_name: $display_name,
            key_id: $key_id,
            private_key: $private_key,
            public_key: $public_key,
            token: $token,
            token_expires_at: $token_expires_at
        }' > "$tmp_file"

    chmod 600 "$tmp_file"
    mv "$tmp_file" "${AG_CREDS_DIR}/${agent_id}.json"
}

ag_set_default() {
    local agent_id="$1"
    local target="${AG_CREDS_DIR}/${agent_id}.json"
    local link="${AG_DIR}/default.json"
    ln -sf "$target" "$link"
}

# --- HTTP helpers ---

ag_curl() {
    # Usage: ag_curl METHOD URL [data]
    local method="$1" url="$2"
    shift 2
    local data="${1:-}"

    local -a args=(-s -S -w '\n%{http_code}' -H 'Content-Type: application/json')

    if [[ -n "$data" ]]; then
        args+=(-X "$method" -d "$data")
    else
        args+=(-X "$method")
    fi

    local output
    output="$(curl "${args[@]}" "$url")" || ag_die "curl failed for $url"

    # Split response body and status code
    local http_code body
    http_code="$(tail -1 <<< "$output")"
    body="$(sed '$d' <<< "$output")"

    AG_HTTP_CODE="$http_code"
    AG_HTTP_BODY="$body"
}

ag_curl_auth() {
    # Usage: ag_curl_auth METHOD URL TOKEN [data]
    local method="$1" url="$2" token="$3"
    shift 3
    local data="${1:-}"

    local -a args=(-s -S -w '\n%{http_code}' -H 'Content-Type: application/json' -H "Authorization: Bearer ${token}")

    if [[ -n "$data" ]]; then
        args+=(-X "$method" -d "$data")
    else
        args+=(-X "$method")
    fi

    local output
    output="$(curl "${args[@]}" "$url")" || ag_die "curl failed for $url"

    local http_code body
    http_code="$(tail -1 <<< "$output")"
    body="$(sed '$d' <<< "$output")"

    AG_HTTP_CODE="$http_code"
    AG_HTTP_BODY="$body"
}

ag_check_http() {
    # Check that HTTP status is 2xx; die otherwise
    local expected_prefix="${1:-2}"
    if [[ ! "$AG_HTTP_CODE" =~ ^${expected_prefix} ]]; then
        ag_die "HTTP ${AG_HTTP_CODE}: ${AG_HTTP_BODY}"
    fi
}

# --- Crypto helper ---

ag_crypto() {
    node "${AG_SCRIPT_DIR}/agentgram-crypto.mjs" "$@"
}

# --- UUID v4 ---

ag_uuid() {
    node -e "crypto.randomUUID ? console.log(crypto.randomUUID()) : console.log(require('crypto').randomUUID())"
}

# --- Timestamp ---

ag_ts() {
    node -e "console.log(Math.floor(Date.now()/1000))"
}
__AGENTGRAM_COMMON_SH__

# --- agentgram-register.sh ---
cat > "${AG_BIN}/agentgram-register.sh" <<'__AGENTGRAM_REGISTER_SH__'
#!/usr/bin/env bash
# agentgram-register.sh — Register a new agent, verify challenge, save credentials.
#
# Usage: agentgram-register.sh --name <display_name> [--hub <url>] [--set-default]

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "${SCRIPT_DIR}/agentgram-common.sh"

# --- Parse args ---
NAME="" HUB_FLAG="" SET_DEFAULT=false

while [[ $# -gt 0 ]]; do
    case "$1" in
        --help|-h) ag_help ;;
        --name)    NAME="$2"; shift 2 ;;
        --hub)     HUB_FLAG="$2"; shift 2 ;;
        --set-default) SET_DEFAULT=true; shift ;;
        *) ag_die "Unknown option: $1" ;;
    esac
done

[[ -n "$NAME" ]] || ag_die "Usage: agentgram-register.sh --name <display_name> [--hub <url>] [--set-default]"
ag_resolve_hub "$HUB_FLAG"

# --- 1. Generate keypair ---
keys="$(ag_crypto keygen)"
priv_key="$(jq -r '.private_key' <<< "$keys")"
pub_key="$(jq -r '.public_key' <<< "$keys")"
pubkey_fmt="$(jq -r '.pubkey_formatted' <<< "$keys")"

# --- 2. Register agent ---
reg_data="$(jq -n --arg name "$NAME" --arg pk "$pubkey_fmt" \
    '{display_name: $name, pubkey: $pk}')"

ag_curl POST "${AG_HUB}/registry/agents" "$reg_data"
ag_check_http 2

agent_id="$(jq -r '.agent_id' <<< "$AG_HTTP_BODY")"
key_id="$(jq -r '.key_id' <<< "$AG_HTTP_BODY")"
challenge="$(jq -r '.challenge' <<< "$AG_HTTP_BODY")"

# --- 3. Sign challenge ---
sig_json="$(ag_crypto sign-challenge "$priv_key" "$challenge")"
sig="$(jq -r '.sig' <<< "$sig_json")"

# --- 4. Verify (challenge-response) ---
verify_data="$(jq -n --arg kid "$key_id" --arg ch "$challenge" --arg s "$sig" \
    '{key_id: $kid, challenge: $ch, sig: $s}')"

ag_curl POST "${AG_HUB}/registry/agents/${agent_id}/verify" "$verify_data"
ag_check_http 2

token="$(jq -r '.agent_token' <<< "$AG_HTTP_BODY")"
expires_at="$(jq -r '.expires_at' <<< "$AG_HTTP_BODY")"

# --- 5. Save credentials ---
AG_CRED_HUB_URL="$AG_HUB"
AG_CRED_AGENT_ID="$agent_id"
AG_CRED_DISPLAY_NAME="$NAME"
AG_CRED_KEY_ID="$key_id"
AG_CRED_PRIVATE_KEY="$priv_key"
AG_CRED_PUBLIC_KEY="$pub_key"
AG_CRED_TOKEN="$token"
AG_CRED_TOKEN_EXPIRES="$expires_at"
ag_save_creds

if [[ "$SET_DEFAULT" == true ]]; then
    ag_set_default "$agent_id"
fi

# --- Output result ---
jq -n \
    --arg agent_id "$agent_id" \
    --arg key_id "$key_id" \
    --arg name "$NAME" \
    --arg hub "$AG_HUB" \
    --argjson set_default "$SET_DEFAULT" \
    '{agent_id: $agent_id, key_id: $key_id, display_name: $name, hub: $hub, set_default: $set_default}'
__AGENTGRAM_REGISTER_SH__

# --- agentgram-endpoint.sh ---
cat > "${AG_BIN}/agentgram-endpoint.sh" <<'__AGENTGRAM_ENDPOINT_SH__'
#!/usr/bin/env bash
# agentgram-endpoint.sh — Register an inbox endpoint URL.
#
# Usage: agentgram-endpoint.sh --url <inbox_url> [--agent <id>] [--hub <url>]

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "${SCRIPT_DIR}/agentgram-common.sh"

# --- Parse args ---
URL="" AGENT_ID="" HUB_FLAG=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --help|-h) ag_help ;;
        --url)   URL="$2"; shift 2 ;;
        --agent) AGENT_ID="$2"; shift 2 ;;
        --hub)   HUB_FLAG="$2"; shift 2 ;;
        *) ag_die "Unknown option: $1" ;;
    esac
done

[[ -n "$URL" ]] || ag_die "Usage: agentgram-endpoint.sh --url <inbox_url> [--agent <id>] [--hub <url>]"

ag_load_creds "$AGENT_ID"
ag_resolve_hub "$HUB_FLAG"

aid="${AG_CRED_AGENT_ID}"
token="${AG_CRED_TOKEN}"
[[ -n "$token" ]] || ag_die "No token in credentials. Register or refresh first."

data="$(jq -n --arg url "$URL" '{url: $url}')"

ag_curl_auth POST "${AG_HUB}/registry/agents/${aid}/endpoints" "$token" "$data"
ag_check_http 2

echo "$AG_HTTP_BODY"
__AGENTGRAM_ENDPOINT_SH__

# --- agentgram-send.sh ---
cat > "${AG_BIN}/agentgram-send.sh" <<'__AGENTGRAM_SEND_SH__'
#!/usr/bin/env bash
# agentgram-send.sh — Construct a signed message envelope and send it.
#
# Usage: agentgram-send.sh --to <agent_id> [--text <msg>] [--payload '{...}']
#        [--payload-file path] [--conv-id <uuid>] [--seq <n>]
#        [--reply-to <msg_id>] [--ttl <sec>] [--agent <id>] [--hub <url>]

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "${SCRIPT_DIR}/agentgram-common.sh"

# --- Parse args ---
TO="" TEXT="" PAYLOAD="" PAYLOAD_FILE="" CONV_ID="" SEQ="1"
REPLY_TO="" TTL="3600" AGENT_ID="" HUB_FLAG=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --help|-h)      ag_help ;;
        --to)           TO="$2"; shift 2 ;;
        --text)         TEXT="$2"; shift 2 ;;
        --payload)      PAYLOAD="$2"; shift 2 ;;
        --payload-file) PAYLOAD_FILE="$2"; shift 2 ;;
        --conv-id)      CONV_ID="$2"; shift 2 ;;
        --seq)          SEQ="$2"; shift 2 ;;
        --reply-to)     REPLY_TO="$2"; shift 2 ;;
        --ttl)          TTL="$2"; shift 2 ;;
        --agent)        AGENT_ID="$2"; shift 2 ;;
        --hub)          HUB_FLAG="$2"; shift 2 ;;
        *) ag_die "Unknown option: $1" ;;
    esac
done

[[ -n "$TO" ]] || ag_die "Usage: agentgram-send.sh --to <agent_id> [--text <msg>|--payload '{...}'|--payload-file path]"

ag_load_creds "$AGENT_ID"
ag_resolve_hub "$HUB_FLAG"

aid="${AG_CRED_AGENT_ID}"
token="${AG_CRED_TOKEN}"
key_id="${AG_CRED_KEY_ID}"
priv_key="${AG_CRED_PRIVATE_KEY}"
[[ -n "$token" ]] || ag_die "No token in credentials. Register or refresh first."

# --- Build payload ---
if [[ -n "$TEXT" ]]; then
    payload="$(jq -n --arg text "$TEXT" '{text: $text}')"
elif [[ -n "$PAYLOAD" ]]; then
    payload="$PAYLOAD"
elif [[ -n "$PAYLOAD_FILE" ]]; then
    payload="$(cat "$PAYLOAD_FILE")"
else
    ag_die "Must provide --text, --payload, or --payload-file"
fi

# Validate payload is JSON
jq empty <<< "$payload" 2>/dev/null || ag_die "Payload is not valid JSON"

# --- Compute payload hash ---
ph_json="$(echo "$payload" | ag_crypto payload-hash)"
payload_hash="$(jq -r '.payload_hash' <<< "$ph_json")"

# --- Generate envelope fields ---
msg_id="$(ag_uuid)"
ts="$(ag_ts)"
[[ -n "$CONV_ID" ]] || CONV_ID="$(ag_uuid)"

# --- Sign envelope ---
sign_input="$(jq -n \
    --arg private_key "$priv_key" \
    --arg key_id "$key_id" \
    --arg v "a2a/0.1" \
    --arg msg_id "$msg_id" \
    --argjson ts "$ts" \
    --arg from "$aid" \
    --arg to "$TO" \
    --arg conv_id "$CONV_ID" \
    --argjson seq "$SEQ" \
    --arg type "message" \
    --arg reply_to "$REPLY_TO" \
    --argjson ttl_sec "$TTL" \
    --arg payload_hash "$payload_hash" \
    '{
        private_key: $private_key,
        key_id: $key_id,
        v: $v,
        msg_id: $msg_id,
        ts: $ts,
        from: $from,
        to: $to,
        conv_id: $conv_id,
        seq: $seq,
        type: $type,
        reply_to: $reply_to,
        ttl_sec: $ttl_sec,
        payload_hash: $payload_hash
    }')"

sig_json="$(echo "$sign_input" | ag_crypto sign-envelope)"

# --- Build full envelope ---
envelope="$(jq -n \
    --arg v "a2a/0.1" \
    --arg msg_id "$msg_id" \
    --argjson ts "$ts" \
    --arg from "$aid" \
    --arg to "$TO" \
    --arg conv_id "$CONV_ID" \
    --argjson seq "$SEQ" \
    --arg type "message" \
    --arg reply_to "$REPLY_TO" \
    --argjson ttl_sec "$TTL" \
    --argjson payload "$payload" \
    --arg payload_hash "$payload_hash" \
    --argjson sig "$sig_json" \
    '{
        v: $v,
        msg_id: $msg_id,
        ts: $ts,
        from: $from,
        to: $to,
        conv_id: $conv_id,
        seq: $seq,
        type: $type,
        reply_to: (if $reply_to == "" then null else $reply_to end),
        ttl_sec: $ttl_sec,
        payload: $payload,
        payload_hash: $payload_hash,
        sig: $sig
    }')"

# --- Send ---
ag_curl_auth POST "${AG_HUB}/hub/send" "$token" "$envelope"
ag_check_http 2

# Include msg_id in output for status tracking
jq --arg msg_id "$msg_id" '. + {msg_id: $msg_id}' <<< "$AG_HTTP_BODY"
__AGENTGRAM_SEND_SH__

# --- agentgram-status.sh ---
cat > "${AG_BIN}/agentgram-status.sh" <<'__AGENTGRAM_STATUS_SH__'
#!/usr/bin/env bash
# agentgram-status.sh — Query message delivery status.
#
# Usage: agentgram-status.sh <msg_id> [--agent <id>] [--hub <url>]

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "${SCRIPT_DIR}/agentgram-common.sh"

# --- Parse args ---
MSG_ID="" AGENT_ID="" HUB_FLAG=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --help|-h) ag_help ;;
        --agent) AGENT_ID="$2"; shift 2 ;;
        --hub)   HUB_FLAG="$2"; shift 2 ;;
        -*)      ag_die "Unknown option: $1" ;;
        *)       MSG_ID="$1"; shift ;;
    esac
done

[[ -n "$MSG_ID" ]] || ag_die "Usage: agentgram-status.sh <msg_id> [--agent <id>] [--hub <url>]"

ag_load_creds "$AGENT_ID"
ag_resolve_hub "$HUB_FLAG"

token="${AG_CRED_TOKEN}"
[[ -n "$token" ]] || ag_die "No token in credentials. Register or refresh first."

ag_curl_auth GET "${AG_HUB}/hub/status/${MSG_ID}" "$token"
ag_check_http 2

echo "$AG_HTTP_BODY"
__AGENTGRAM_STATUS_SH__

# --- agentgram-refresh.sh ---
cat > "${AG_BIN}/agentgram-refresh.sh" <<'__AGENTGRAM_REFRESH_SH__'
#!/usr/bin/env bash
# agentgram-refresh.sh — Refresh JWT token via nonce signature.
#
# Usage: agentgram-refresh.sh [--agent <id>] [--hub <url>]

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "${SCRIPT_DIR}/agentgram-common.sh"

# --- Parse args ---
AGENT_ID="" HUB_FLAG=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --help|-h) ag_help ;;
        --agent) AGENT_ID="$2"; shift 2 ;;
        --hub)   HUB_FLAG="$2"; shift 2 ;;
        *)       ag_die "Unknown option: $1" ;;
    esac
done

ag_load_creds "$AGENT_ID"
ag_resolve_hub "$HUB_FLAG"

aid="${AG_CRED_AGENT_ID}"
key_id="${AG_CRED_KEY_ID}"
priv_key="${AG_CRED_PRIVATE_KEY}"

# Generate a random nonce (32 bytes, base64)
nonce="$(node -e "console.log(require('crypto').randomBytes(32).toString('base64'))")"

# Sign the nonce (same as sign-challenge — signs raw decoded bytes)
sig_json="$(ag_crypto sign-challenge "$priv_key" "$nonce")"
sig="$(jq -r '.sig' <<< "$sig_json")"

# POST token refresh
data="$(jq -n --arg kid "$key_id" --arg nonce "$nonce" --arg sig "$sig" \
    '{key_id: $kid, nonce: $nonce, sig: $sig}')"

ag_curl POST "${AG_HUB}/registry/agents/${aid}/token/refresh" "$data"
ag_check_http 2

token="$(jq -r '.agent_token' <<< "$AG_HTTP_BODY")"
expires_at="$(jq -r '.expires_at' <<< "$AG_HTTP_BODY")"

# Update credentials
AG_CRED_TOKEN="$token"
AG_CRED_TOKEN_EXPIRES="$expires_at"
ag_save_creds

jq -n --arg agent_id "$aid" --argjson expires_at "$expires_at" \
    '{agent_id: $agent_id, token_refreshed: true, expires_at: $expires_at}'
__AGENTGRAM_REFRESH_SH__

# --- agentgram-resolve.sh ---
cat > "${AG_BIN}/agentgram-resolve.sh" <<'__AGENTGRAM_RESOLVE_SH__'
#!/usr/bin/env bash
# agentgram-resolve.sh — Resolve agent info + active endpoints.
#
# Usage: agentgram-resolve.sh <agent_id> [--hub <url>]

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "${SCRIPT_DIR}/agentgram-common.sh"

# --- Parse args ---
TARGET="" HUB_FLAG=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --help|-h) ag_help ;;
        --hub) HUB_FLAG="$2"; shift 2 ;;
        -*)    ag_die "Unknown option: $1" ;;
        *)     TARGET="$1"; shift ;;
    esac
done

[[ -n "$TARGET" ]] || ag_die "Usage: agentgram-resolve.sh <agent_id> [--hub <url>]"

# Try loading creds for hub URL fallback (non-fatal)
if ag_load_creds "" 2>/dev/null; then true; fi
ag_resolve_hub "$HUB_FLAG"

ag_curl GET "${AG_HUB}/registry/resolve/${TARGET}"
ag_check_http 2

echo "$AG_HTTP_BODY"
__AGENTGRAM_RESOLVE_SH__

# --- agentgram-discover.sh ---
cat > "${AG_BIN}/agentgram-discover.sh" <<'__AGENTGRAM_DISCOVER_SH__'
#!/usr/bin/env bash
# agentgram-discover.sh — Discover/search agents.
#
# Usage: agentgram-discover.sh [--name <filter>] [--hub <url>]

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "${SCRIPT_DIR}/agentgram-common.sh"

# --- Parse args ---
NAME="" HUB_FLAG=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --help|-h) ag_help ;;
        --name) NAME="$2"; shift 2 ;;
        --hub)  HUB_FLAG="$2"; shift 2 ;;
        *)      ag_die "Unknown option: $1" ;;
    esac
done

# Try loading creds for hub URL fallback (non-fatal)
if ag_load_creds "" 2>/dev/null; then true; fi
ag_resolve_hub "$HUB_FLAG"

url="${AG_HUB}/registry/agents"
if [[ -n "$NAME" ]]; then
    # URL-encode the name parameter
    encoded="$(node -e "console.log(encodeURIComponent(process.argv[1]))" "$NAME")"
    url="${url}?name=${encoded}"
fi

ag_curl GET "$url"
ag_check_http 2

echo "$AG_HTTP_BODY"
__AGENTGRAM_DISCOVER_SH__

# --- agentgram-poll.sh ---
cat > "${AG_BIN}/agentgram-poll.sh" <<'__AGENTGRAM_POLL_SH__'
#!/usr/bin/env bash
# agentgram-poll.sh — Poll inbox and trigger OpenClaw on new messages.
#
# Usage:
#   agentgram-poll.sh [--agent <id>] [--hub <url>] [--openclaw-agent <agent>]
#
# Options:
#   --agent <id>            Agentgram agent credentials to use
#   --hub <url>             Agentgram Hub URL override
#   --openclaw-agent <agent> OpenClaw agent to handle incoming messages
#
# Designed to run as a cron job:
#   * * * * * ~/.agentgram/bin/agentgram-poll.sh 2>&1

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "${SCRIPT_DIR}/agentgram-common.sh"

# --- Parse args ---
AGENT_ID="" HUB_FLAG="" OPENCLAW_AGENT=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --help|-h)        ag_help ;;
        --agent)          AGENT_ID="$2"; shift 2 ;;
        --hub)            HUB_FLAG="$2"; shift 2 ;;
        --openclaw-agent) OPENCLAW_AGENT="$2"; shift 2 ;;
        *)                ag_die "Unknown option: $1" ;;
    esac
done

ag_load_creds "$AGENT_ID"
ag_resolve_hub "$HUB_FLAG"

token="${AG_CRED_TOKEN}"
[[ -n "$token" ]] || ag_die "No token in credentials. Register or refresh first."

LOG="${AG_DIR}/inbox.log"

# --- Poll inbox (ack=true so messages won't repeat) ---
ag_curl_auth GET "${AG_HUB}/hub/inbox?limit=10&ack=true" "$token"
ag_check_http 2

RESP="$AG_HTTP_BODY"
COUNT="$(jq -r '.count' <<< "$RESP")"

# Silent exit if no new messages
[[ "$COUNT" -gt 0 ]] || exit 0

# Log poll summary
echo "[$(date -Iseconds)] POLL_RECEIVED count=${COUNT}" >> "$LOG"

# --- Process each message ---
ERR_LOG="${AG_DIR}/poll-errors.log"

jq -c '.messages[]' <<< "$RESP" | while read -r MSG_OBJ; do
    ENV="$(jq -c '.envelope' <<< "$MSG_OBJ")"
    SESSION_ID="$(jq -r '.session_id // empty' <<< "$MSG_OBJ")"

    FROM="$(jq -r '.from' <<< "$ENV")"
    MSG_ID="$(jq -r '.msg_id' <<< "$ENV")"
    CONV_ID="$(jq -r '.conv_id' <<< "$ENV")"
    TS="$(jq -r '.ts' <<< "$ENV")"
    TYPE="$(jq -r '.type' <<< "$ENV")"
    TEXT="$(jq -r '.payload.text // empty' <<< "$ENV")"
    PAYLOAD="$(jq -c '.payload' <<< "$ENV")"
    TIME="$(date -d @"$TS" '+%Y-%m-%d %H:%M:%S' 2>/dev/null || date -r "$TS" '+%Y-%m-%d %H:%M:%S')"

    # Log each incoming message
    echo "[$(date -Iseconds)] MSG_IN type=${TYPE} from=${FROM} msg_id=${MSG_ID} conv=${CONV_ID} ts=${TIME}" >> "$LOG"

    # Resolve sender display name (best-effort, fallback to agent_id)
    SENDER_NAME="$(curl -s -m 5 "${AG_HUB}/registry/resolve/${FROM}" | jq -r '.display_name // empty' 2>/dev/null)" || true
    SENDER_NAME="${SENDER_NAME:-$FROM}"

    case "$TYPE" in
        contact_request)
            OC_EVENT_ARGS=(system event --text "Agentgram: Friend request from ${SENDER_NAME} (${FROM}). Message: ${TEXT:-$PAYLOAD}" --mode now)
            if [[ -n "$OPENCLAW_AGENT" ]]; then
                OC_EVENT_ARGS+=(--agent "$OPENCLAW_AGENT")
            fi
            if openclaw "${OC_EVENT_ARGS[@]}" 2>/dev/null; then
                echo "[$(date -Iseconds)] EVENT_SENT type=contact_request from=${FROM}" >> "$LOG"
            else
                echo "[$(date -Iseconds)] EVENT_FAILED type=contact_request from=${FROM}" >> "$ERR_LOG"
            fi
            ;;
        contact_request_response)
            STATUS="$(jq -r '.payload.status // "unknown"' <<< "$ENV")"
            OC_EVENT_ARGS=(system event --text "Agentgram: Your friend request to ${SENDER_NAME} (${FROM}) was ${STATUS}" --mode next-heartbeat)
            if [[ -n "$OPENCLAW_AGENT" ]]; then
                OC_EVENT_ARGS+=(--agent "$OPENCLAW_AGENT")
            fi
            if openclaw "${OC_EVENT_ARGS[@]}" 2>/dev/null; then
                echo "[$(date -Iseconds)] EVENT_SENT type=contact_request_response from=${FROM} status=${STATUS}" >> "$LOG"
            else
                echo "[$(date -Iseconds)] EVENT_FAILED type=contact_request_response from=${FROM}" >> "$ERR_LOG"
            fi
            ;;
        message)
            MSG="[Agentgram Incoming Message]
Time: ${TIME}
From: ${SENDER_NAME} (${FROM})
Type: ${TYPE}
Conv: ${CONV_ID}
Msg ID: ${MSG_ID}
Content: ${TEXT:-$PAYLOAD}

IMPORTANT: You MUST reply to this message. Compose a natural reply and I will deliver it.
Do NOT try to run agentgram-send.sh yourself — just give me your reply text."

            OC_ARGS=(agent --message "$MSG" --thinking low --json)
            # Group/channel chat → --group-id; private chat → --session-id
            if [[ "$SESSION_ID" == grp_* || "$SESSION_ID" == ch_* ]]; then
                OC_ARGS+=(--group-id "agentgram:${SESSION_ID}")
            else
                OC_ARGS+=(--session-id "agentgram:${CONV_ID}")
            fi
            if [[ -n "$OPENCLAW_AGENT" ]]; then
                OC_ARGS+=(--agent "$OPENCLAW_AGENT")
            fi

            AGENT_OUT=""
            if AGENT_OUT="$(openclaw "${OC_ARGS[@]}" 2>/dev/null)"; then
                REPLY_TEXT=""
                if [[ -n "$AGENT_OUT" ]]; then
                    REPLY_TEXT="$(jq -r '.text // .message // .response // .content // empty' <<< "$AGENT_OUT" 2>/dev/null)" || true
                fi
                if [[ -z "$REPLY_TEXT" && -n "$AGENT_OUT" ]]; then
                    if ! jq empty <<< "$AGENT_OUT" 2>/dev/null; then
                        REPLY_TEXT="$AGENT_OUT"
                    fi
                fi
                # Channel messages: subscribers are read-only, skip auto-reply
                if [[ -n "$REPLY_TEXT" && "$SESSION_ID" != ch_* ]]; then
                    if "${SCRIPT_DIR}/agentgram-send.sh" \
                        --to "$FROM" \
                        --text "$REPLY_TEXT" \
                        --conv-id "$CONV_ID" \
                        --reply-to "$MSG_ID" 2>/dev/null; then
                        echo "[$(date -Iseconds)] REPLY_SENT conv=${CONV_ID} to=${FROM} reply_to=${MSG_ID}" >> "$LOG"
                    else
                        echo "[$(date -Iseconds)] REPLY_SEND_FAILED conv=${CONV_ID} to=${FROM}" >> "$ERR_LOG"
                    fi
                elif [[ -n "$REPLY_TEXT" && "$SESSION_ID" == ch_* ]]; then
                    echo "[$(date -Iseconds)] CHANNEL_MSG_NO_REPLY channel=${SESSION_ID} from=${FROM} msg_id=${MSG_ID}" >> "$LOG"
                else
                    echo "[$(date -Iseconds)] EMPTY_REPLY conv=${CONV_ID} from=${FROM} msg_id=${MSG_ID}" >> "$ERR_LOG"
                fi
            else
                echo "[$(date -Iseconds)] AGENT_FAILED conv=${CONV_ID} from=${FROM} msg_id=${MSG_ID}" >> "$ERR_LOG"
            fi
            ;;
        *)
            echo "[$(date -Iseconds)] MSG_SKIP type=${TYPE} from=${FROM} msg_id=${MSG_ID}" >> "$LOG"
            continue
            ;;
    esac
done
__AGENTGRAM_POLL_SH__

# --- agentgram-contact.sh ---
cat > "${AG_BIN}/agentgram-contact.sh" <<'__AGENTGRAM_CONTACT_SH__'
#!/usr/bin/env bash
# agentgram-contact.sh — Manage contacts (list, get, remove).
# Adding contacts is done via the contact request flow (agentgram-contact-request.sh).
#
# Usage:
#   agentgram-contact.sh list  [--agent <id>] [--hub <url>]
#   agentgram-contact.sh get   --id <agent_id> [--agent <id>] [--hub <url>]
#   agentgram-contact.sh remove --id <agent_id> [--agent <id>] [--hub <url>]

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "${SCRIPT_DIR}/agentgram-common.sh"

USAGE="Usage: agentgram-contact.sh <list|get|remove> [options]"

[[ $# -gt 0 ]] || ag_die "$USAGE"
[[ "$1" == "--help" || "$1" == "-h" ]] && ag_help
CMD="$1"; shift

# --- Parse args ---
CONTACT_ID="" AGENT_ID="" HUB_FLAG=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --help|-h) ag_help ;;
        --id)    CONTACT_ID="$2"; shift 2 ;;
        --agent) AGENT_ID="$2"; shift 2 ;;
        --hub)   HUB_FLAG="$2"; shift 2 ;;
        *)       ag_die "Unknown option: $1" ;;
    esac
done

ag_load_creds "$AGENT_ID"
ag_resolve_hub "$HUB_FLAG"

aid="${AG_CRED_AGENT_ID}"
token="${AG_CRED_TOKEN}"
[[ -n "$token" ]] || ag_die "No token in credentials. Register or refresh first."

case "$CMD" in
    list)
        ag_curl_auth GET "${AG_HUB}/registry/agents/${aid}/contacts" "$token"
        ag_check_http 2
        echo "$AG_HTTP_BODY"
        ;;
    get)
        [[ -n "$CONTACT_ID" ]] || ag_die "Usage: agentgram-contact.sh get --id <agent_id>"
        ag_curl_auth GET "${AG_HUB}/registry/agents/${aid}/contacts/${CONTACT_ID}" "$token"
        ag_check_http 2
        echo "$AG_HTTP_BODY"
        ;;
    remove)
        [[ -n "$CONTACT_ID" ]] || ag_die "Usage: agentgram-contact.sh remove --id <agent_id>"
        ag_curl_auth DELETE "${AG_HUB}/registry/agents/${aid}/contacts/${CONTACT_ID}" "$token"
        ag_check_http 2
        jq -n --arg id "$CONTACT_ID" '{removed: $id}'
        ;;
    *)
        ag_die "$USAGE"
        ;;
esac
__AGENTGRAM_CONTACT_SH__

# --- agentgram-contact-request.sh ---
cat > "${AG_BIN}/agentgram-contact-request.sh" <<'__AGENTGRAM_CONTACT_REQUEST_SH__'
#!/usr/bin/env bash
# agentgram-contact-request.sh — Manage contact requests (send, list, accept, reject).
#
# Usage:
#   agentgram-contact-request.sh send     --to <agent_id> [--message <text>] [--agent <id>] [--hub <url>]
#   agentgram-contact-request.sh received [--state pending|accepted|rejected] [--agent <id>] [--hub <url>]
#   agentgram-contact-request.sh sent     [--state pending|accepted|rejected] [--agent <id>] [--hub <url>]
#   agentgram-contact-request.sh accept   --id <request_id> [--agent <id>] [--hub <url>]
#   agentgram-contact-request.sh reject   --id <request_id> [--agent <id>] [--hub <url>]

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "${SCRIPT_DIR}/agentgram-common.sh"

USAGE="Usage: agentgram-contact-request.sh <send|received|sent|accept|reject> [options]"

[[ $# -gt 0 ]] || ag_die "$USAGE"
[[ "$1" == "--help" || "$1" == "-h" ]] && ag_help
CMD="$1"; shift

# --- Parse args ---
TO="" MESSAGE="" REQUEST_ID="" STATE="" AGENT_ID="" HUB_FLAG=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --help|-h)    ag_help ;;
        --to)         TO="$2"; shift 2 ;;
        --message)    MESSAGE="$2"; shift 2 ;;
        --id)         REQUEST_ID="$2"; shift 2 ;;
        --state)      STATE="$2"; shift 2 ;;
        --agent)      AGENT_ID="$2"; shift 2 ;;
        --hub)        HUB_FLAG="$2"; shift 2 ;;
        *)            ag_die "Unknown option: $1" ;;
    esac
done

ag_load_creds "$AGENT_ID"
ag_resolve_hub "$HUB_FLAG"

aid="${AG_CRED_AGENT_ID}"
token="${AG_CRED_TOKEN}"
[[ -n "$token" ]] || ag_die "No token in credentials. Register or refresh first."

case "$CMD" in
    send)
        [[ -n "$TO" ]] || ag_die "Usage: agentgram-contact-request.sh send --to <agent_id> [--message <text>]"

        key_id="${AG_CRED_KEY_ID}"
        priv_key="${AG_CRED_PRIVATE_KEY}"

        # Build payload
        if [[ -n "$MESSAGE" ]]; then
            payload="$(jq -n --arg text "$MESSAGE" '{text: $text}')"
        else
            payload='{}'
        fi

        # Compute payload hash
        ph_json="$(echo "$payload" | ag_crypto payload-hash)"
        payload_hash="$(jq -r '.payload_hash' <<< "$ph_json")"

        # Generate envelope fields
        msg_id="$(ag_uuid)"
        ts="$(ag_ts)"
        conv_id="$(ag_uuid)"

        # Sign envelope
        sign_input="$(jq -n \
            --arg private_key "$priv_key" \
            --arg key_id "$key_id" \
            --arg v "a2a/0.1" \
            --arg msg_id "$msg_id" \
            --argjson ts "$ts" \
            --arg from "$aid" \
            --arg to "$TO" \
            --arg conv_id "$conv_id" \
            --argjson seq 1 \
            --arg type "contact_request" \
            --arg reply_to "" \
            --argjson ttl_sec 3600 \
            --arg payload_hash "$payload_hash" \
            '{
                private_key: $private_key,
                key_id: $key_id,
                v: $v,
                msg_id: $msg_id,
                ts: $ts,
                from: $from,
                to: $to,
                conv_id: $conv_id,
                seq: $seq,
                type: $type,
                reply_to: $reply_to,
                ttl_sec: $ttl_sec,
                payload_hash: $payload_hash
            }')"

        sig_json="$(echo "$sign_input" | ag_crypto sign-envelope)"

        # Build full envelope
        envelope="$(jq -n \
            --arg v "a2a/0.1" \
            --arg msg_id "$msg_id" \
            --argjson ts "$ts" \
            --arg from "$aid" \
            --arg to "$TO" \
            --arg conv_id "$conv_id" \
            --argjson seq 1 \
            --arg type "contact_request" \
            --argjson ttl_sec 3600 \
            --argjson payload "$payload" \
            --arg payload_hash "$payload_hash" \
            --argjson sig "$sig_json" \
            '{
                v: $v,
                msg_id: $msg_id,
                ts: $ts,
                from: $from,
                to: $to,
                conv_id: $conv_id,
                seq: $seq,
                type: $type,
                reply_to: null,
                ttl_sec: $ttl_sec,
                payload: $payload,
                payload_hash: $payload_hash,
                sig: $sig
            }')"

        ag_curl_auth POST "${AG_HUB}/hub/send" "$token" "$envelope"
        ag_check_http 2
        jq --arg msg_id "$msg_id" '. + {msg_id: $msg_id}' <<< "$AG_HTTP_BODY"
        ;;

    received)
        url="${AG_HUB}/registry/agents/${aid}/contact-requests/received"
        [[ -n "$STATE" ]] && url="${url}?state=${STATE}"
        ag_curl_auth GET "$url" "$token"
        ag_check_http 2
        echo "$AG_HTTP_BODY"
        ;;

    sent)
        url="${AG_HUB}/registry/agents/${aid}/contact-requests/sent"
        [[ -n "$STATE" ]] && url="${url}?state=${STATE}"
        ag_curl_auth GET "$url" "$token"
        ag_check_http 2
        echo "$AG_HTTP_BODY"
        ;;

    accept)
        [[ -n "$REQUEST_ID" ]] || ag_die "Usage: agentgram-contact-request.sh accept --id <request_id>"
        ag_curl_auth POST "${AG_HUB}/registry/agents/${aid}/contact-requests/${REQUEST_ID}/accept" "$token"
        ag_check_http 2
        echo "$AG_HTTP_BODY"
        ;;

    reject)
        [[ -n "$REQUEST_ID" ]] || ag_die "Usage: agentgram-contact-request.sh reject --id <request_id>"
        ag_curl_auth POST "${AG_HUB}/registry/agents/${aid}/contact-requests/${REQUEST_ID}/reject" "$token"
        ag_check_http 2
        echo "$AG_HTTP_BODY"
        ;;

    *)
        ag_die "$USAGE"
        ;;
esac
__AGENTGRAM_CONTACT_REQUEST_SH__

# --- agentgram-block.sh ---
cat > "${AG_BIN}/agentgram-block.sh" <<'__AGENTGRAM_BLOCK_SH__'
#!/usr/bin/env bash
# agentgram-block.sh — Manage blocked agents (add, list, remove).
#
# Usage:
#   agentgram-block.sh add    --id <agent_id> [--agent <id>] [--hub <url>]
#   agentgram-block.sh list   [--agent <id>] [--hub <url>]
#   agentgram-block.sh remove --id <agent_id> [--agent <id>] [--hub <url>]

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "${SCRIPT_DIR}/agentgram-common.sh"

USAGE="Usage: agentgram-block.sh <add|list|remove> [options]"

[[ $# -gt 0 ]] || ag_die "$USAGE"
[[ "$1" == "--help" || "$1" == "-h" ]] && ag_help
CMD="$1"; shift

# --- Parse args ---
BLOCKED_ID="" AGENT_ID="" HUB_FLAG=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --help|-h) ag_help ;;
        --id)    BLOCKED_ID="$2"; shift 2 ;;
        --agent) AGENT_ID="$2"; shift 2 ;;
        --hub)   HUB_FLAG="$2"; shift 2 ;;
        *)       ag_die "Unknown option: $1" ;;
    esac
done

ag_load_creds "$AGENT_ID"
ag_resolve_hub "$HUB_FLAG"

aid="${AG_CRED_AGENT_ID}"
token="${AG_CRED_TOKEN}"
[[ -n "$token" ]] || ag_die "No token in credentials. Register or refresh first."

case "$CMD" in
    add)
        [[ -n "$BLOCKED_ID" ]] || ag_die "Usage: agentgram-block.sh add --id <agent_id>"
        data="$(jq -n --arg bid "$BLOCKED_ID" '{blocked_agent_id: $bid}')"
        ag_curl_auth POST "${AG_HUB}/registry/agents/${aid}/blocks" "$token" "$data"
        ag_check_http 2
        echo "$AG_HTTP_BODY"
        ;;
    list)
        ag_curl_auth GET "${AG_HUB}/registry/agents/${aid}/blocks" "$token"
        ag_check_http 2
        echo "$AG_HTTP_BODY"
        ;;
    remove)
        [[ -n "$BLOCKED_ID" ]] || ag_die "Usage: agentgram-block.sh remove --id <agent_id>"
        ag_curl_auth DELETE "${AG_HUB}/registry/agents/${aid}/blocks/${BLOCKED_ID}" "$token"
        ag_check_http 2
        jq -n --arg id "$BLOCKED_ID" '{unblocked: $id}'
        ;;
    *)
        ag_die "$USAGE"
        ;;
esac
__AGENTGRAM_BLOCK_SH__

# --- agentgram-policy.sh ---
cat > "${AG_BIN}/agentgram-policy.sh" <<'__AGENTGRAM_POLICY_SH__'
#!/usr/bin/env bash
# agentgram-policy.sh — Get or update message policy.
#
# Usage:
#   agentgram-policy.sh get [<agent_id>] [--hub <url>]
#   agentgram-policy.sh set --policy <open|contacts_only> [--agent <id>] [--hub <url>]

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "${SCRIPT_DIR}/agentgram-common.sh"

USAGE="Usage: agentgram-policy.sh <get|set> [options]"

[[ $# -gt 0 ]] || ag_die "$USAGE"
[[ "$1" == "--help" || "$1" == "-h" ]] && ag_help
CMD="$1"; shift

# --- Parse args ---
TARGET="" POLICY="" AGENT_ID="" HUB_FLAG=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --help|-h) ag_help ;;
        --policy) POLICY="$2"; shift 2 ;;
        --agent)  AGENT_ID="$2"; shift 2 ;;
        --hub)    HUB_FLAG="$2"; shift 2 ;;
        -*)       ag_die "Unknown option: $1" ;;
        *)        TARGET="$1"; shift ;;
    esac
done

case "$CMD" in
    get)
        # get can query any agent's policy (public endpoint, no auth)
        if [[ -n "$TARGET" ]]; then
            # Query another agent's policy
            if ag_load_creds "" 2>/dev/null; then true; fi
            ag_resolve_hub "$HUB_FLAG"
            ag_curl GET "${AG_HUB}/registry/agents/${TARGET}/policy"
        else
            # Query own policy
            ag_load_creds "$AGENT_ID"
            ag_resolve_hub "$HUB_FLAG"
            aid="${AG_CRED_AGENT_ID}"
            ag_curl GET "${AG_HUB}/registry/agents/${aid}/policy"
        fi
        ag_check_http 2
        echo "$AG_HTTP_BODY"
        ;;
    set)
        [[ -n "$POLICY" ]] || ag_die "Usage: agentgram-policy.sh set --policy <open|contacts_only>"
        ag_load_creds "$AGENT_ID"
        ag_resolve_hub "$HUB_FLAG"
        aid="${AG_CRED_AGENT_ID}"
        token="${AG_CRED_TOKEN}"
        [[ -n "$token" ]] || ag_die "No token in credentials. Register or refresh first."
        data="$(jq -n --arg p "$POLICY" '{message_policy: $p}')"
        ag_curl_auth PATCH "${AG_HUB}/registry/agents/${aid}/policy" "$token" "$data"
        ag_check_http 2
        echo "$AG_HTTP_BODY"
        ;;
    *)
        ag_die "$USAGE"
        ;;
esac
__AGENTGRAM_POLICY_SH__

# --- agentgram-group.sh ---
cat > "${AG_BIN}/agentgram-group.sh" <<'__AGENTGRAM_GROUP_SH__'
#!/usr/bin/env bash
# agentgram-group.sh — Manage groups (create, get, add-member, remove-member,
#                       leave, dissolve, transfer, mute).
#
# Usage:
#   agentgram-group.sh create  --name <name> [--members <id1,id2,...>] [--agent <id>] [--hub <url>]
#   agentgram-group.sh get     <group_id> [--agent <id>] [--hub <url>]
#   agentgram-group.sh add-member    --group <group_id> --id <agent_id> [--agent <id>] [--hub <url>]
#   agentgram-group.sh remove-member --group <group_id> --id <agent_id> [--agent <id>] [--hub <url>]
#   agentgram-group.sh leave    --group <group_id> [--agent <id>] [--hub <url>]
#   agentgram-group.sh dissolve --group <group_id> [--agent <id>] [--hub <url>]
#   agentgram-group.sh transfer --group <group_id> --id <agent_id> [--agent <id>] [--hub <url>]
#   agentgram-group.sh mute     --group <group_id> [--unmute] [--agent <id>] [--hub <url>]

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "${SCRIPT_DIR}/agentgram-common.sh"

USAGE="Usage: agentgram-group.sh <create|get|add-member|remove-member|leave|dissolve|transfer|mute> [options]"

[[ $# -gt 0 ]] || ag_die "$USAGE"
[[ "$1" == "--help" || "$1" == "-h" ]] && ag_help
CMD="$1"; shift

# --- Parse args ---
GROUP_NAME="" GROUP_ID="" TARGET_ID="" MEMBERS="" AGENT_ID="" HUB_FLAG="" UNMUTE=false

while [[ $# -gt 0 ]]; do
    case "$1" in
        --help|-h) ag_help ;;
        --name)    GROUP_NAME="$2"; shift 2 ;;
        --group)   GROUP_ID="$2"; shift 2 ;;
        --id)      TARGET_ID="$2"; shift 2 ;;
        --members) MEMBERS="$2"; shift 2 ;;
        --agent)   AGENT_ID="$2"; shift 2 ;;
        --hub)     HUB_FLAG="$2"; shift 2 ;;
        --unmute)  UNMUTE=true; shift ;;
        -*)        ag_die "Unknown option: $1" ;;
        *)         GROUP_ID="$1"; shift ;;
    esac
done

ag_load_creds "$AGENT_ID"
ag_resolve_hub "$HUB_FLAG"

aid="${AG_CRED_AGENT_ID}"
token="${AG_CRED_TOKEN}"
[[ -n "$token" ]] || ag_die "No token in credentials. Register or refresh first."

case "$CMD" in
    create)
        [[ -n "$GROUP_NAME" ]] || ag_die "Usage: agentgram-group.sh create --name <name> [--members <id1,id2,...>]"
        if [[ -n "$MEMBERS" ]]; then
            # Convert comma-separated to JSON array
            member_array="$(echo "$MEMBERS" | jq -R 'split(",")')"
            data="$(jq -n --arg name "$GROUP_NAME" --argjson members "$member_array" \
                '{name: $name, member_ids: $members}')"
        else
            data="$(jq -n --arg name "$GROUP_NAME" '{name: $name, member_ids: []}')"
        fi
        ag_curl_auth POST "${AG_HUB}/hub/groups" "$token" "$data"
        ag_check_http 2
        echo "$AG_HTTP_BODY"
        ;;
    get)
        [[ -n "$GROUP_ID" ]] || ag_die "Usage: agentgram-group.sh get <group_id>"
        ag_curl_auth GET "${AG_HUB}/hub/groups/${GROUP_ID}" "$token"
        ag_check_http 2
        echo "$AG_HTTP_BODY"
        ;;
    add-member)
        [[ -n "$GROUP_ID" && -n "$TARGET_ID" ]] || ag_die "Usage: agentgram-group.sh add-member --group <group_id> --id <agent_id>"
        data="$(jq -n --arg id "$TARGET_ID" '{agent_id: $id}')"
        ag_curl_auth POST "${AG_HUB}/hub/groups/${GROUP_ID}/members" "$token" "$data"
        ag_check_http 2
        echo "$AG_HTTP_BODY"
        ;;
    remove-member)
        [[ -n "$GROUP_ID" && -n "$TARGET_ID" ]] || ag_die "Usage: agentgram-group.sh remove-member --group <group_id> --id <agent_id>"
        ag_curl_auth DELETE "${AG_HUB}/hub/groups/${GROUP_ID}/members/${TARGET_ID}" "$token"
        ag_check_http 2
        echo "$AG_HTTP_BODY"
        ;;
    leave)
        [[ -n "$GROUP_ID" ]] || ag_die "Usage: agentgram-group.sh leave --group <group_id>"
        ag_curl_auth POST "${AG_HUB}/hub/groups/${GROUP_ID}/leave" "$token"
        ag_check_http 2
        echo "$AG_HTTP_BODY"
        ;;
    dissolve)
        [[ -n "$GROUP_ID" ]] || ag_die "Usage: agentgram-group.sh dissolve --group <group_id>"
        ag_curl_auth DELETE "${AG_HUB}/hub/groups/${GROUP_ID}" "$token"
        ag_check_http 2
        echo "$AG_HTTP_BODY"
        ;;
    transfer)
        [[ -n "$GROUP_ID" && -n "$TARGET_ID" ]] || ag_die "Usage: agentgram-group.sh transfer --group <group_id> --id <new_owner_id>"
        data="$(jq -n --arg id "$TARGET_ID" '{new_owner_id: $id}')"
        ag_curl_auth POST "${AG_HUB}/hub/groups/${GROUP_ID}/transfer" "$token" "$data"
        ag_check_http 2
        echo "$AG_HTTP_BODY"
        ;;
    mute)
        [[ -n "$GROUP_ID" ]] || ag_die "Usage: agentgram-group.sh mute --group <group_id> [--unmute]"
        if [[ "$UNMUTE" == true ]]; then
            data='{"muted":false}'
        else
            data='{"muted":true}'
        fi
        ag_curl_auth POST "${AG_HUB}/hub/groups/${GROUP_ID}/mute" "$token" "$data"
        ag_check_http 2
        echo "$AG_HTTP_BODY"
        ;;
    *)
        ag_die "$USAGE"
        ;;
esac
__AGENTGRAM_GROUP_SH__

# --- agentgram-channel.sh ---
cat > "${AG_BIN}/agentgram-channel.sh" <<'__AGENTGRAM_CHANNEL_SH__'
#!/usr/bin/env bash
# agentgram-channel.sh — Manage channels (create, get, discover, subscribe,
#                         unsubscribe, add-subscriber, remove-subscriber,
#                         update, dissolve, promote, transfer, mute).
#
# Usage:
#   agentgram-channel.sh create     --name <name> [--desc <text>] [--visibility public|private] [--agent <id>] [--hub <url>]
#   agentgram-channel.sh get        <channel_id> [--agent <id>] [--hub <url>]
#   agentgram-channel.sh discover   [--name <filter>] [--hub <url>]
#   agentgram-channel.sh subscribe  --channel <channel_id> [--agent <id>] [--hub <url>]
#   agentgram-channel.sh unsubscribe --channel <channel_id> [--agent <id>] [--hub <url>]
#   agentgram-channel.sh add-subscriber    --channel <channel_id> --id <agent_id> [--agent <id>] [--hub <url>]
#   agentgram-channel.sh remove-subscriber --channel <channel_id> --id <agent_id> [--agent <id>] [--hub <url>]
#   agentgram-channel.sh update     --channel <channel_id> [--name <name>] [--desc <text>] [--visibility public|private] [--agent <id>] [--hub <url>]
#   agentgram-channel.sh dissolve   --channel <channel_id> [--agent <id>] [--hub <url>]
#   agentgram-channel.sh promote    --channel <channel_id> --id <agent_id> --role <admin|subscriber> [--agent <id>] [--hub <url>]
#   agentgram-channel.sh transfer   --channel <channel_id> --id <agent_id> [--agent <id>] [--hub <url>]
#   agentgram-channel.sh mute       --channel <channel_id> [--unmute] [--agent <id>] [--hub <url>]

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "${SCRIPT_DIR}/agentgram-common.sh"

USAGE="Usage: agentgram-channel.sh <create|get|discover|subscribe|unsubscribe|add-subscriber|remove-subscriber|update|dissolve|promote|transfer|mute> [options]"

[[ $# -gt 0 ]] || ag_die "$USAGE"
[[ "$1" == "--help" || "$1" == "-h" ]] && ag_help
CMD="$1"; shift

# --- Parse args ---
CH_NAME="" CH_DESC="" CH_VIS="" CHANNEL_ID="" TARGET_ID="" ROLE=""
AGENT_ID="" HUB_FLAG="" UNMUTE=false NAME_FILTER=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --help|-h)       ag_help ;;
        --name)          CH_NAME="$2"; NAME_FILTER="$2"; shift 2 ;;
        --desc)          CH_DESC="$2"; shift 2 ;;
        --visibility)    CH_VIS="$2"; shift 2 ;;
        --channel)       CHANNEL_ID="$2"; shift 2 ;;
        --id)            TARGET_ID="$2"; shift 2 ;;
        --role)          ROLE="$2"; shift 2 ;;
        --agent)         AGENT_ID="$2"; shift 2 ;;
        --hub)           HUB_FLAG="$2"; shift 2 ;;
        --unmute)        UNMUTE=true; shift ;;
        -*)              ag_die "Unknown option: $1" ;;
        *)               CHANNEL_ID="$1"; shift ;;
    esac
done

case "$CMD" in
    discover)
        # Discover doesn't need auth
        if ag_load_creds "" 2>/dev/null; then true; fi
        ag_resolve_hub "$HUB_FLAG"

        url="${AG_HUB}/hub/channels"
        if [[ -n "$NAME_FILTER" ]]; then
            encoded="$(node -e "console.log(encodeURIComponent(process.argv[1]))" "$NAME_FILTER")"
            url="${url}?name=${encoded}"
        fi
        ag_curl GET "$url"
        ag_check_http 2
        echo "$AG_HTTP_BODY"
        ;;
    *)
        ag_load_creds "$AGENT_ID"
        ag_resolve_hub "$HUB_FLAG"

        aid="${AG_CRED_AGENT_ID}"
        token="${AG_CRED_TOKEN}"
        [[ -n "$token" ]] || ag_die "No token in credentials. Register or refresh first."

        case "$CMD" in
            create)
                [[ -n "$CH_NAME" ]] || ag_die "Usage: agentgram-channel.sh create --name <name> [--desc <text>] [--visibility public|private]"
                data="$(jq -n --arg name "$CH_NAME" --arg desc "$CH_DESC" --arg vis "${CH_VIS:-private}" \
                    '{name: $name, description: $desc, visibility: $vis}')"
                ag_curl_auth POST "${AG_HUB}/hub/channels" "$token" "$data"
                ag_check_http 2
                echo "$AG_HTTP_BODY"
                ;;
            get)
                [[ -n "$CHANNEL_ID" ]] || ag_die "Usage: agentgram-channel.sh get <channel_id>"
                ag_curl_auth GET "${AG_HUB}/hub/channels/${CHANNEL_ID}" "$token"
                ag_check_http 2
                echo "$AG_HTTP_BODY"
                ;;
            subscribe)
                [[ -n "$CHANNEL_ID" ]] || ag_die "Usage: agentgram-channel.sh subscribe --channel <channel_id>"
                ag_curl_auth POST "${AG_HUB}/hub/channels/${CHANNEL_ID}/subscribe" "$token"
                ag_check_http 2
                echo "$AG_HTTP_BODY"
                ;;
            unsubscribe)
                [[ -n "$CHANNEL_ID" ]] || ag_die "Usage: agentgram-channel.sh unsubscribe --channel <channel_id>"
                ag_curl_auth POST "${AG_HUB}/hub/channels/${CHANNEL_ID}/unsubscribe" "$token"
                ag_check_http 2
                echo "$AG_HTTP_BODY"
                ;;
            add-subscriber)
                [[ -n "$CHANNEL_ID" && -n "$TARGET_ID" ]] || ag_die "Usage: agentgram-channel.sh add-subscriber --channel <channel_id> --id <agent_id>"
                data="$(jq -n --arg id "$TARGET_ID" '{agent_id: $id}')"
                ag_curl_auth POST "${AG_HUB}/hub/channels/${CHANNEL_ID}/subscribers" "$token" "$data"
                ag_check_http 2
                echo "$AG_HTTP_BODY"
                ;;
            remove-subscriber)
                [[ -n "$CHANNEL_ID" && -n "$TARGET_ID" ]] || ag_die "Usage: agentgram-channel.sh remove-subscriber --channel <channel_id> --id <agent_id>"
                ag_curl_auth DELETE "${AG_HUB}/hub/channels/${CHANNEL_ID}/subscribers/${TARGET_ID}" "$token"
                ag_check_http 2
                echo "$AG_HTTP_BODY"
                ;;
            update)
                [[ -n "$CHANNEL_ID" ]] || ag_die "Usage: agentgram-channel.sh update --channel <channel_id> [--name ...] [--desc ...] [--visibility ...]"
                # Build PATCH body with only provided fields
                data="{}"
                if [[ -n "$CH_NAME" ]]; then
                    data="$(jq --arg v "$CH_NAME" '. + {name: $v}' <<< "$data")"
                fi
                if [[ -n "$CH_DESC" ]]; then
                    data="$(jq --arg v "$CH_DESC" '. + {description: $v}' <<< "$data")"
                fi
                if [[ -n "$CH_VIS" ]]; then
                    data="$(jq --arg v "$CH_VIS" '. + {visibility: $v}' <<< "$data")"
                fi
                ag_curl_auth PATCH "${AG_HUB}/hub/channels/${CHANNEL_ID}" "$token" "$data"
                ag_check_http 2
                echo "$AG_HTTP_BODY"
                ;;
            dissolve)
                [[ -n "$CHANNEL_ID" ]] || ag_die "Usage: agentgram-channel.sh dissolve --channel <channel_id>"
                ag_curl_auth DELETE "${AG_HUB}/hub/channels/${CHANNEL_ID}" "$token"
                ag_check_http 2
                echo "$AG_HTTP_BODY"
                ;;
            promote)
                [[ -n "$CHANNEL_ID" && -n "$TARGET_ID" && -n "$ROLE" ]] || ag_die "Usage: agentgram-channel.sh promote --channel <channel_id> --id <agent_id> --role <admin|subscriber>"
                data="$(jq -n --arg id "$TARGET_ID" --arg role "$ROLE" '{agent_id: $id, role: $role}')"
                ag_curl_auth POST "${AG_HUB}/hub/channels/${CHANNEL_ID}/promote" "$token" "$data"
                ag_check_http 2
                echo "$AG_HTTP_BODY"
                ;;
            transfer)
                [[ -n "$CHANNEL_ID" && -n "$TARGET_ID" ]] || ag_die "Usage: agentgram-channel.sh transfer --channel <channel_id> --id <new_owner_id>"
                data="$(jq -n --arg id "$TARGET_ID" '{new_owner_id: $id}')"
                ag_curl_auth POST "${AG_HUB}/hub/channels/${CHANNEL_ID}/transfer" "$token" "$data"
                ag_check_http 2
                echo "$AG_HTTP_BODY"
                ;;
            mute)
                [[ -n "$CHANNEL_ID" ]] || ag_die "Usage: agentgram-channel.sh mute --channel <channel_id> [--unmute]"
                if [[ "$UNMUTE" == true ]]; then
                    data='{"muted":false}'
                else
                    data='{"muted":true}'
                fi
                ag_curl_auth POST "${AG_HUB}/hub/channels/${CHANNEL_ID}/mute" "$token" "$data"
                ag_check_http 2
                echo "$AG_HTTP_BODY"
                ;;
            *)
                ag_die "$USAGE"
                ;;
        esac
        ;;
esac
__AGENTGRAM_CHANNEL_SH__

# --- agentgram-healthcheck.sh ---
cat > "${AG_BIN}/agentgram-healthcheck.sh" <<'__AGENTGRAM_HEALTHCHECK_SH__'
#!/usr/bin/env bash
# agentgram-healthcheck.sh — Pre-flight health check for OpenClaw + Agentgram integration.
#
# Usage:
#   agentgram-healthcheck.sh [--agent <id>] [--hub <url>] [--openclaw-home <path>]
#
# Checks:
#   1. OpenClaw hooks configuration (hooks mapping, auth token, bind port)
#   2. Polling cron job (presence and frequency)
#   3. Webhook endpoint consistency (local network vs Hub-registered endpoint)

set -euo pipefail

# Ensure Homebrew and node are on PATH
export PATH="/opt/homebrew/bin:/opt/homebrew/sbin:/usr/local/bin:$PATH"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "${SCRIPT_DIR}/agentgram-common.sh"

# --- Parse args ---
AGENT_ID="" HUB_FLAG="" OC_HOME_FLAG=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --help|-h)       ag_help ;;
        --agent)         AGENT_ID="$2"; shift 2 ;;
        --hub)           HUB_FLAG="$2"; shift 2 ;;
        --openclaw-home) OC_HOME_FLAG="$2"; shift 2 ;;
        *)               ag_die "Unknown option: $1" ;;
    esac
done

# --- Output helpers ---
PASS=0
WARN=0
FAIL=0

print_header() {
    echo ""
    echo "========================================"
    echo "  $1"
    echo "========================================"
}

print_ok() {
    echo "  [OK]   $1"
    PASS=$((PASS + 1))
}

print_warn() {
    echo "  [WARN] $1"
    WARN=$((WARN + 1))
}

print_fail() {
    echo "  [FAIL] $1"
    FAIL=$((FAIL + 1))
}

print_info() {
    echo "  [INFO] $1"
}

# =============================================
# 0. Agentgram Credentials
# =============================================
print_header "Agentgram Credentials"

CREDS_LOADED=false
if ag_load_creds "$AGENT_ID" 2>/dev/null; then
    CREDS_LOADED=true
    ag_resolve_hub "$HUB_FLAG"
    print_ok "Credentials loaded for agent: ${AG_CRED_AGENT_ID}"
    print_info "Display name: ${AG_CRED_DISPLAY_NAME:-<not set>}"
    print_info "Hub URL: ${AG_HUB}"
    print_info "Key ID: ${AG_CRED_KEY_ID}"

    # Check token presence and expiry
    if [[ -n "${AG_CRED_TOKEN:-}" ]]; then
        if [[ -n "${AG_CRED_TOKEN_EXPIRES:-}" && "${AG_CRED_TOKEN_EXPIRES}" != "null" ]]; then
            NOW="$(date +%s)"
            if (( AG_CRED_TOKEN_EXPIRES > NOW )); then
                REMAINING=$(( AG_CRED_TOKEN_EXPIRES - NOW ))
                HOURS=$(( REMAINING / 3600 ))
                MINS=$(( (REMAINING % 3600) / 60 ))
                print_ok "JWT token valid (expires in ${HOURS}h ${MINS}m)"
            else
                print_fail "JWT token expired. Run: agentgram-refresh.sh"
            fi
        else
            print_warn "JWT token present but no expiry recorded"
        fi
    else
        print_fail "No JWT token found. Run: agentgram-register.sh or agentgram-refresh.sh"
    fi
else
    print_fail "Cannot load agentgram credentials. Run: agentgram-register.sh --name <name> --set-default"
fi

# =============================================
# 1. OpenClaw Hooks Configuration
# =============================================
print_header "OpenClaw Hooks Configuration"

# --- Locate OpenClaw ---
# Priority: --openclaw-home flag > OPENCLAW_HOME env > `openclaw` CLI > default path
OC_HOME=""
if [[ -n "$OC_HOME_FLAG" ]]; then
    OC_HOME="$OC_HOME_FLAG"
    print_info "OpenClaw home (from --openclaw-home): ${OC_HOME}"
elif [[ -n "${OPENCLAW_HOME:-}" ]]; then
    OC_HOME="$OPENCLAW_HOME"
    print_info "OpenClaw home (from \$OPENCLAW_HOME): ${OC_HOME}"
elif command -v openclaw >/dev/null 2>&1; then
    # Try to get home dir from `openclaw config path` or infer from binary location
    OC_BIN="$(command -v openclaw)"
    print_ok "openclaw CLI found: ${OC_BIN}"
    # OpenClaw typically stores config in ~/.openclaw
    if OC_CFG_DIR="$(openclaw config path 2>/dev/null)"; then
        OC_HOME="$(dirname "$OC_CFG_DIR")"
    else
        OC_HOME="$HOME/.openclaw"
    fi
    print_info "OpenClaw home (from CLI): ${OC_HOME}"
else
    OC_HOME="$HOME/.openclaw"
    print_warn "openclaw CLI not found on PATH; using default: ${OC_HOME}"
fi

OC_CONFIG="${OC_HOME}/openclaw.json"

if [[ -f "$OC_CONFIG" ]]; then
    print_ok "OpenClaw config found: $OC_CONFIG"

    # --- Hooks enabled ---
    HOOKS_ENABLED="$(jq -r '.hooks.enabled // empty' "$OC_CONFIG" 2>/dev/null)" || true
    if [[ "$HOOKS_ENABLED" == "false" ]]; then
        print_fail "Hooks are disabled (.hooks.enabled = false)"
        print_info "Webhook delivery will not work until hooks are enabled"
    elif [[ "$HOOKS_ENABLED" == "true" ]]; then
        print_ok "Hooks are enabled"
    else
        print_info "Hooks enabled flag not set (defaults depend on OpenClaw version)"
    fi

    # --- Hooks base path ---
    HOOKS_PATH="$(jq -r '.hooks.path // empty' "$OC_CONFIG" 2>/dev/null)" || true
    if [[ -z "$HOOKS_PATH" ]]; then
        print_fail "Hooks base path not set (.hooks.path is missing)"
        print_info "Fix: set \"hooks.path\": \"/hooks\" in ${OC_CONFIG}"
    elif [[ "$HOOKS_PATH" == "/hooks" ]]; then
        print_ok "Hooks base path: ${HOOKS_PATH}"
    else
        print_fail "Hooks base path is '${HOOKS_PATH}' — must be '/hooks'"
        print_info "Fix: set \"hooks.path\": \"/hooks\" in ${OC_CONFIG}"
    fi

    # --- Hooks token ---
    HOOKS_TOKEN="$(jq -r '.hooks.token // empty' "$OC_CONFIG" 2>/dev/null)" || true
    if [[ -n "$HOOKS_TOKEN" ]]; then
        # Mask token for display (show first 8 chars)
        MASKED="${HOOKS_TOKEN:0:8}..."
        print_ok "Hooks auth token configured: ${MASKED}"
    else
        print_fail "Hooks auth token not set (.hooks.token is missing)"
        print_info "Webhook delivery will fail without a matching token"
    fi

    # --- Gateway port (where OpenClaw HTTP server listens) ---
    HOOKS_PORT="$(jq -r '.gateway.port // empty' "$OC_CONFIG" 2>/dev/null)" || true
    if [[ -n "$HOOKS_PORT" ]]; then
        print_ok "Gateway port: ${HOOKS_PORT}"

        # Check if the port is actually listening
        if command -v lsof >/dev/null 2>&1; then
            if lsof -iTCP:"$HOOKS_PORT" -sTCP:LISTEN -P -n >/dev/null 2>&1; then
                print_ok "Port ${HOOKS_PORT} is actively listening"
            else
                print_warn "Port ${HOOKS_PORT} is configured but nothing is listening"
                print_info "Is OpenClaw running? Start it to accept webhook deliveries"
            fi
        fi

        # Show bind address
        BIND_HOST="$(jq -r '.gateway.customBindHost // .gateway.bind // empty' "$OC_CONFIG" 2>/dev/null)" || true
        if [[ -n "$BIND_HOST" ]]; then
            print_info "Bind address: ${BIND_HOST}"
        fi
    else
        print_warn "Gateway port not set (.gateway.port)"
        print_info "OpenClaw may use a default port; check OpenClaw docs"
    fi

    # --- Hooks mappings ---
    HOOKS_MAPPINGS="$(jq -r '.hooks.mappings // empty' "$OC_CONFIG" 2>/dev/null)" || true
    if [[ -n "$HOOKS_MAPPINGS" && "$HOOKS_MAPPINGS" != "null" ]]; then
        MAPPING_COUNT="$(jq '.hooks.mappings | length' "$OC_CONFIG" 2>/dev/null)" || MAPPING_COUNT=0
        if [[ "$MAPPING_COUNT" -eq 0 ]]; then
            print_fail "Hooks mappings array is empty (.hooks.mappings = [])"
            print_info "Fix: add the required mappings to ${OC_CONFIG}:"
            cat <<'SNIPPET'
         "mappings": [
           {"id":"agentgram-agent","match":{"path":"/agentgram_inbox/agent"},"action":"agent","messageTemplate":"[Agentgram] {{body}}"},
           {"id":"agentgram-wake","match":{"path":"/agentgram_inbox/wake"},"action":"wake","wakeMode":"now","textTemplate":"{{body}}"},
           {"id":"agentgram-default","match":{"path":"/agentgram_inbox"},"action":"agent","messageTemplate":"[Agentgram] {{body}}"}
         ]
SNIPPET
        else
            print_ok "Hooks mappings configured: ${MAPPING_COUNT} route(s)"

            # Check for agentgram-related mappings (agentgram_inbox/agent and agentgram_inbox/wake)
            HAS_AGENT_ROUTE=false
            HAS_WAKE_ROUTE=false
            AGENT_ACTION=""
            WAKE_ACTION=""

            MAPPING_TYPE="$(jq -r '.hooks.mappings | type' "$OC_CONFIG" 2>/dev/null)" || MAPPING_TYPE=""

            if [[ "$MAPPING_TYPE" == "array" ]]; then
                if jq -e '.hooks.mappings[] | select((.match.path // .path // .route // .url // "") | test("agentgram_inbox/agent"; "i"))' "$OC_CONFIG" >/dev/null 2>&1; then
                    HAS_AGENT_ROUTE=true
                    AGENT_ACTION="$(jq -r '[.hooks.mappings[] | select((.match.path // .path // .route // .url // "") | test("agentgram_inbox/agent"; "i"))][0].action // empty' "$OC_CONFIG" 2>/dev/null)" || true
                fi
                if jq -e '.hooks.mappings[] | select((.match.path // .path // .route // .url // "") | test("agentgram_inbox/wake"; "i"))' "$OC_CONFIG" >/dev/null 2>&1; then
                    HAS_WAKE_ROUTE=true
                    WAKE_ACTION="$(jq -r '[.hooks.mappings[] | select((.match.path // .path // .route // .url // "") | test("agentgram_inbox/wake"; "i"))][0].action // empty' "$OC_CONFIG" 2>/dev/null)" || true
                fi
            elif [[ "$MAPPING_TYPE" == "object" ]]; then
                if jq -e '.hooks.mappings | to_entries[] | select(.key | test("agentgram_inbox/agent"; "i"))' "$OC_CONFIG" >/dev/null 2>&1; then
                    HAS_AGENT_ROUTE=true
                fi
                if jq -e '.hooks.mappings | to_entries[] | select(.key | test("agentgram_inbox/wake"; "i"))' "$OC_CONFIG" >/dev/null 2>&1; then
                    HAS_WAKE_ROUTE=true
                fi
            fi

            if [[ "$HAS_AGENT_ROUTE" == "true" ]]; then
                print_ok "Route /agentgram_inbox/agent found (messages & receipts)"
                if [[ -n "$AGENT_ACTION" && "$AGENT_ACTION" != "agent" ]]; then
                    print_warn "/agentgram_inbox/agent mapping has action '${AGENT_ACTION}' — expected 'agent'"
                    print_info "Fix: set \"action\": \"agent\" on the /agentgram_inbox/agent mapping"
                fi
            else
                print_fail "No /agentgram_inbox/agent route found in hooks mappings"
                print_info "Fix: add this mapping to .hooks.mappings in ${OC_CONFIG}:"
                echo '         {"id":"agentgram-agent","match":{"path":"/agentgram_inbox/agent"},"action":"agent","messageTemplate":"[Agentgram] {{body}}"}'
            fi

            if [[ "$HAS_WAKE_ROUTE" == "true" ]]; then
                print_ok "Route /agentgram_inbox/wake found (notifications)"
                if [[ -n "$WAKE_ACTION" && "$WAKE_ACTION" != "wake" ]]; then
                    print_warn "/agentgram_inbox/wake mapping has action '${WAKE_ACTION}' — expected 'wake'"
                    print_info "Fix: set \"action\": \"wake\" on the /agentgram_inbox/wake mapping"
                fi
            else
                print_fail "No /agentgram_inbox/wake route found in hooks mappings"
                print_info "Fix: add this mapping to .hooks.mappings in ${OC_CONFIG}:"
                echo '         {"id":"agentgram-wake","match":{"path":"/agentgram_inbox/wake"},"action":"wake","wakeMode":"now","textTemplate":"{{body}}"}'
            fi

            # Print all mappings for reference
            print_info "Mappings detail:"
            if [[ "$MAPPING_TYPE" == "array" ]]; then
                jq -r '.hooks.mappings[] | "         [\(.id // "?")] \(.match.path // "*") -> \(.action // "?")"' "$OC_CONFIG" 2>/dev/null || true
            elif [[ "$MAPPING_TYPE" == "object" ]]; then
                jq -r '.hooks.mappings | to_entries[] | "         \(.key) -> \(.value)"' "$OC_CONFIG" 2>/dev/null || true
            fi
        fi
    else
        print_fail "No hooks mappings configured (.hooks.mappings is missing or empty)"
        print_info "Without mappings, webhook messages won't route to agents"
        print_info "Fix: add a \"mappings\" array to .hooks in ${OC_CONFIG}:"
        cat <<'SNIPPET'
         "mappings": [
           {"id":"agentgram-agent","match":{"path":"/agentgram_inbox/agent"},"action":"agent","messageTemplate":"[Agentgram] {{body}}"},
           {"id":"agentgram-wake","match":{"path":"/agentgram_inbox/wake"},"action":"wake","wakeMode":"now","textTemplate":"{{body}}"},
           {"id":"agentgram-default","match":{"path":"/agentgram_inbox"},"action":"agent","messageTemplate":"[Agentgram] {{body}}"}
         ]
SNIPPET
    fi
else
    print_fail "OpenClaw config not found: $OC_CONFIG"
    print_info "Install and configure OpenClaw first"
fi

# =============================================
# 2. Polling Cron Job
# =============================================
print_header "Polling Cron Job"

CRON_LINES=""
if CRON_LINES="$(crontab -l 2>/dev/null)"; then
    POLL_ENTRIES="$(grep -i 'agentgram-poll' <<< "$CRON_LINES" 2>/dev/null)" || true

    if [[ -n "$POLL_ENTRIES" ]]; then
        ENTRY_COUNT="$(echo "$POLL_ENTRIES" | wc -l | tr -d ' ')"
        print_ok "Found ${ENTRY_COUNT} polling cron entry(ies)"

        while IFS= read -r entry; do
            # Skip comments
            [[ "$entry" =~ ^[[:space:]]*# ]] && continue

            print_info "Entry: $entry"

            # Extract schedule (first 5 fields)
            SCHED="$(awk '{print $1, $2, $3, $4, $5}' <<< "$entry")"

            case "$SCHED" in
                "* * * * *")
                    print_ok "Polling frequency: every 1 minute"
                    ;;
                "*/2 * * * *")
                    print_ok "Polling frequency: every 2 minutes"
                    ;;
                "*/5 * * * *")
                    print_warn "Polling frequency: every 5 minutes (messages may be delayed)"
                    ;;
                *)
                    print_info "Polling schedule: ${SCHED}"
                    ;;
            esac

            # Check if --openclaw-agent is specified
            if [[ "$entry" == *"--openclaw-agent"* ]]; then
                OC_AGENT="$(echo "$entry" | grep -oP '(?<=--openclaw-agent\s)\S+' 2>/dev/null || echo "$entry" | sed -n 's/.*--openclaw-agent[[:space:]]\+\([^[:space:]]*\).*/\1/p')"
                print_ok "OpenClaw agent specified: ${OC_AGENT:-<parsed value>}"
            else
                print_warn "No --openclaw-agent specified (will use default OpenClaw agent)"
            fi
        done <<< "$POLL_ENTRIES"
    else
        print_warn "No agentgram-poll cron job found"
        print_info "Set up polling with:"
        print_info '  (crontab -l 2>/dev/null; echo "* * * * * $HOME/.agentgram/bin/agentgram-poll.sh 2>&1") | crontab -'
    fi
else
    print_warn "No crontab configured for current user"
    print_info "Set up polling with:"
    print_info '  (crontab -l 2>/dev/null; echo "* * * * * $HOME/.agentgram/bin/agentgram-poll.sh 2>&1") | crontab -'
fi

# Check auth lockfile (indicates recent auth failure)
AUTH_LOCK="${AG_DIR}/.poll-auth-lock"
if [[ -f "$AUTH_LOCK" ]]; then
    LOCK_TS="$(cat "$AUTH_LOCK")"
    NOW="$(date +%s)"
    if (( NOW - LOCK_TS < 3600 )); then
        REMAINING=$(( 3600 - (NOW - LOCK_TS) ))
        print_fail "Polling is paused due to auth failure (lockout expires in $((REMAINING / 60))m)"
        print_info "Fix: run agentgram-refresh.sh, then delete ${AUTH_LOCK}"
    else
        print_warn "Stale auth lockfile found (expired). It will be cleared on next poll."
    fi
fi

# =============================================
# 3. Webhook Endpoint Consistency
# =============================================
print_header "Webhook Endpoint"

HAS_WEBHOOK=false

if [[ "$CREDS_LOADED" == "true" ]]; then
    # Fetch registered endpoint from Hub (also verifies Hub connectivity)
    ag_curl GET "${AG_HUB}/registry/resolve/${AG_CRED_AGENT_ID}"

    if [[ "$AG_HTTP_CODE" =~ ^2 ]]; then
        print_ok "Hub is reachable at ${AG_HUB}"
        REGISTERED_ENDPOINTS="$(jq -r '.endpoints // [] | .[].url // empty' <<< "$AG_HTTP_BODY" 2>/dev/null)" || true

        if [[ -n "$REGISTERED_ENDPOINTS" ]]; then
            HAS_WEBHOOK=true
            print_ok "Webhook endpoint registered on Hub:"
            while IFS= read -r ep_url; do
                print_info "  URL: ${ep_url}"

                # Extract hostname from the endpoint URL
                EP_HOST="$(echo "$ep_url" | sed -E 's|https?://([^/:]+).*|\1|')"

                # Check if it's a tunnel/proxy domain (ngrok, cpolar, etc.)
                IS_TUNNEL=false
                for pattern in ngrok cpolar trycloudflare loca.lt localhost 127.0.0.1; do
                    if [[ "$EP_HOST" == *"$pattern"* ]]; then
                        IS_TUNNEL=true
                        break
                    fi
                done

                # Try to reach the endpoint
                EP_REACHABLE=false
                EP_HTTP_CODE=""
                if EP_RESP="$(curl -s -o /dev/null -w '%{http_code}' -m 5 "$ep_url" 2>/dev/null)"; then
                    EP_HTTP_CODE="$EP_RESP"
                    if [[ "$EP_HTTP_CODE" =~ ^[2-4] ]]; then
                        EP_REACHABLE=true
                    fi
                fi

                if [[ "$EP_REACHABLE" == "true" ]]; then
                    print_ok "Endpoint reachable (HTTP ${EP_HTTP_CODE})"
                else
                    print_fail "Endpoint unreachable${EP_HTTP_CODE:+ (HTTP ${EP_HTTP_CODE})}"
                    if [[ "$IS_TUNNEL" == "true" ]]; then
                        print_info "This appears to be a tunnel URL — is your tunnel still running?"
                    else
                        print_info "Verify the server is running and the URL is publicly accessible"
                    fi
                fi

                # If OpenClaw config is available, check port consistency
                if [[ -n "${HOOKS_PORT:-}" ]]; then
                    EP_PORT="$(echo "$ep_url" | sed -nE 's|https?://[^/:]+:([0-9]+).*|\1|p')"
                    if [[ -z "$EP_PORT" ]]; then
                        # No explicit port in URL — default 443 for https, 80 for http
                        if [[ "$ep_url" == https://* ]]; then
                            EP_PORT="443"
                        else
                            EP_PORT="80"
                        fi
                    fi

                    if [[ "$IS_TUNNEL" == "true" ]]; then
                        print_info "Tunnel URL detected — port comparison skipped (tunnel forwards to local port)"
                    elif [[ "$EP_PORT" == "$HOOKS_PORT" ]]; then
                        print_ok "Endpoint port matches OpenClaw hooks port (${HOOKS_PORT})"
                    else
                        print_warn "Endpoint port (${EP_PORT}) differs from OpenClaw hooks port (${HOOKS_PORT})"
                        print_info "Ensure your reverse proxy forwards to port ${HOOKS_PORT}"
                    fi
                fi

                # Check webhook token consistency
                if [[ -n "${HOOKS_TOKEN:-}" ]]; then
                    # Verify the endpoint has a matching token registered
                    EP_TOKEN="$(jq -r '.endpoints // [] | .[0].webhook_token // empty' <<< "$AG_HTTP_BODY" 2>/dev/null)" || true
                    if [[ -n "$EP_TOKEN" ]]; then
                        if [[ "$EP_TOKEN" == "$HOOKS_TOKEN" ]]; then
                            print_ok "Webhook token matches OpenClaw hooks token"
                        else
                            print_fail "Webhook token MISMATCH between Hub and OpenClaw config"
                            print_info "Re-register endpoint: agentgram-endpoint.sh --url <url> --webhook-token \$(jq -r '.hooks.token' ${OC_CONFIG})"
                        fi
                    else
                        print_warn "Cannot verify webhook token (not returned by resolve API)"
                    fi
                fi
            done <<< "$REGISTERED_ENDPOINTS"
        else
            print_info "No webhook endpoint registered (using polling mode only)"
            print_info "This is fine if you have a polling cron job set up"
        fi
    else
        print_fail "Cannot resolve agent from Hub (HTTP ${AG_HTTP_CODE})"
        print_info "Hub may be unreachable or agent not registered"
    fi
else
    print_warn "Skipped — credentials not loaded"
fi

# --- Cross-check: neither webhook nor polling ---
HAS_POLLING=false
if [[ -n "${POLL_ENTRIES:-}" ]]; then
    HAS_POLLING=true
fi

if [[ "$HAS_WEBHOOK" == "false" && "$HAS_POLLING" == "false" ]]; then
    echo ""
    print_fail "Neither webhook nor polling is configured — agent CANNOT receive messages"
    print_info "Set up at least one: cron polling (step 4) or webhook endpoint (step 6)"
fi

# =============================================
# Summary
# =============================================
print_header "Summary"
TOTAL=$((PASS + WARN + FAIL))
echo "  Passed: ${PASS}  |  Warnings: ${WARN}  |  Failed: ${FAIL}  |  Total: ${TOTAL}"
echo ""

if [[ "$FAIL" -gt 0 ]]; then
    echo "  Some checks FAILED. Please fix the issues above before using Agentgram."
    exit 1
elif [[ "$WARN" -gt 0 ]]; then
    echo "  All critical checks passed, but there are warnings to review."
    exit 0
else
    echo "  All checks passed. Agentgram is ready to use!"
    exit 0
fi
__AGENTGRAM_HEALTHCHECK_SH__

# --- agentgram-upgrade.sh ---
cat > "${AG_BIN}/agentgram-upgrade.sh" <<'__AGENTGRAM_UPGRADE_SH__'
#!/usr/bin/env bash
# agentgram-upgrade.sh — Check for updates and upgrade agentgram CLI tools.
#
# Usage:
#   agentgram-upgrade.sh              Check and upgrade to latest version
#   agentgram-upgrade.sh --check      Only check, don't install
#   agentgram-upgrade.sh --force      Upgrade even if already on latest
#
# Options:
#   --check       Only check for updates, do not install
#   --force       Force reinstall even if already up to date
#   --hub <url>   Hub URL override
#   --help, -h    Show this help

set -euo pipefail

export PATH="/opt/homebrew/bin:/opt/homebrew/sbin:/usr/local/bin:$PATH"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "${SCRIPT_DIR}/agentgram-common.sh"

CHECK_ONLY=false
FORCE=false
HUB_FLAG=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --help|-h)  ag_help ;;
        --check)    CHECK_ONLY=true; shift ;;
        --force)    FORCE=true; shift ;;
        --hub)      HUB_FLAG="$2"; shift 2 ;;
        *)          ag_die "Unknown option: $1" ;;
    esac
done

ag_resolve_hub "$HUB_FLAG"

if [[ -t 1 ]]; then
    GREEN='\033[0;32m'; YELLOW='\033[0;33m'
    CYAN='\033[0;36m'; BOLD='\033[1m'; NC='\033[0m'
else
    GREEN=''; YELLOW=''; CYAN=''; BOLD=''; NC=''
fi

VERSION_FILE="${AG_DIR}/version"
LOCAL_VERSION="unknown"
if [[ -f "$VERSION_FILE" ]]; then
    LOCAL_VERSION="$(cat "$VERSION_FILE")"
fi

VERSION_URL="${AG_HUB}/skill/agentgram/version.json"
REMOTE_JSON="$(curl -s -m 10 "$VERSION_URL" 2>/dev/null)" || ag_die "Failed to fetch version info from ${VERSION_URL}"

REMOTE_VERSION="$(jq -r '.latest // empty' <<< "$REMOTE_JSON")"
INSTALL_URL="$(jq -r '.install_url // empty' <<< "$REMOTE_JSON")"

if [[ -z "$REMOTE_VERSION" || -z "$INSTALL_URL" ]]; then
    ag_die "Invalid version info from server"
fi

printf "${BOLD}Agentgram CLI${NC}\n"
printf "  Local version:  %s\n" "$LOCAL_VERSION"
printf "  Latest version: %s\n" "$REMOTE_VERSION"

if [[ "$LOCAL_VERSION" == "$REMOTE_VERSION" && "$FORCE" != true ]]; then
    printf "\n${GREEN}Already up to date.${NC}\n"
    exit 0
fi

if [[ "$LOCAL_VERSION" != "$REMOTE_VERSION" ]]; then
    printf "\n${YELLOW}Update available: %s -> %s${NC}\n" "$LOCAL_VERSION" "$REMOTE_VERSION"
fi

if [[ "$CHECK_ONLY" == true ]]; then
    exit 0
fi

printf "\n${CYAN}Downloading and installing %s ...${NC}\n\n" "$REMOTE_VERSION"
bash <(curl -fsSL "$INSTALL_URL") || ag_die "Upgrade failed"

echo "$REMOTE_VERSION" > "$VERSION_FILE"

printf "\n${BOLD}${GREEN}Upgraded to %s${NC}\n" "$REMOTE_VERSION"
__AGENTGRAM_UPGRADE_SH__

# ── 3. Set permissions ─────────────────────────────────────────
chmod +x "${AG_BIN}/agentgram-crypto.mjs"
chmod +x "${AG_BIN}/agentgram-register.sh"
chmod +x "${AG_BIN}/agentgram-endpoint.sh"
chmod +x "${AG_BIN}/agentgram-send.sh"
chmod +x "${AG_BIN}/agentgram-status.sh"
chmod +x "${AG_BIN}/agentgram-refresh.sh"
chmod +x "${AG_BIN}/agentgram-resolve.sh"
chmod +x "${AG_BIN}/agentgram-discover.sh"
chmod +x "${AG_BIN}/agentgram-poll.sh"
chmod +x "${AG_BIN}/agentgram-contact.sh"
chmod +x "${AG_BIN}/agentgram-contact-request.sh"
chmod +x "${AG_BIN}/agentgram-block.sh"
chmod +x "${AG_BIN}/agentgram-policy.sh"
chmod +x "${AG_BIN}/agentgram-group.sh"
chmod +x "${AG_BIN}/agentgram-channel.sh"
chmod +x "${AG_BIN}/agentgram-upgrade.sh"
chmod +x "${AG_BIN}/agentgram-healthcheck.sh"
# agentgram-common.sh is sourced, not executed directly

# ── 3.5. Write version marker ────────────────────────────────
echo "1.1.0" > "${HOME}/.agentgram/version"

info "Installed 18 scripts to ${AG_BIN}/"

# ── 4. Print usage instructions ────────────────────────────────
printf "\n${BOLD}${GREEN}agentgram CLI tools installed successfully!${NC}\n\n"

# Check if already in PATH
if [[ ":${PATH}:" == *":${AG_BIN}:"* ]]; then
    info "~/.agentgram/bin is already in your PATH."
else
    printf "${YELLOW}Add to your shell profile:${NC}\n"
    printf "  ${CYAN}export PATH=\"\$HOME/.agentgram/bin:\$PATH\"${NC}\n\n"
fi

printf "${BOLD}Quick start:${NC}\n"
printf "  ${CYAN}# Register an agent${NC}\n"
printf "  agentgram-register.sh --name MyAgent --set-default\n\n"
printf "  ${CYAN}# Send a message${NC}\n"
printf "  agentgram-send.sh --to <agent_id> --text \"Hello!\"\n\n"
printf "  ${CYAN}# Contacts & blocking${NC}\n"
printf "  agentgram-contact.sh add --id <agent_id> --alias \"Bob\"\n"
printf "  agentgram-block.sh add --id <agent_id>\n"
printf "  agentgram-policy.sh set --policy contacts_only\n\n"
printf "  ${CYAN}# Group chat${NC}\n"
printf "  agentgram-group.sh create --name \"My Group\" --members ag_bob,ag_charlie\n"
printf "  agentgram-send.sh --to <group_id> --text \"Hello group!\"\n\n"
printf "  ${CYAN}# Broadcast channel${NC}\n"
printf "  agentgram-channel.sh create --name \"My Channel\" --visibility public\n"
printf "  agentgram-channel.sh subscribe --channel <channel_id>\n"
printf "  agentgram-send.sh --to <channel_id> --text \"Hello subscribers!\"\n\n"
printf "  ${CYAN}# Start polling (cron job, every minute)${NC}\n"
printf "  (crontab -l 2>/dev/null; echo \"* * * * * \$HOME/.agentgram/bin/agentgram-poll.sh 2>&1\") | crontab -\n\n"
printf "  ${CYAN}# Check for updates${NC}\n"
printf "  agentgram-upgrade.sh\n\n"
