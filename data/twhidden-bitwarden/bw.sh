#!/usr/bin/env bash
# SECURITY MANIFEST:
# Environment variables accessed: BW_SERVER, BW_EMAIL, BW_MASTER_PASSWORD, CREDS_FILE (optional)
# External endpoints called: User-configured BW_SERVER (Bitwarden/Vaultwarden API)
# Local files read: $CREDS_FILE (default: secrets/bitwarden.env), /tmp/.bw_session
# Local files written: /tmp/.bw_session (session token cache)
# Dependencies: bash, openssl (3.x+), curl, bw CLI, xxd, grep, base64

# Bitwarden CLI wrapper for OpenClaw
# Works with both official Bitwarden and Vaultwarden servers
# Usage: bw.sh <command> [args...]
# Commands: register, login, unlock, lock, list, get, create, edit, delete, generate, sync, status

set -euo pipefail

# Configuration: set via environment or credentials file
# Required env vars: BW_SERVER, BW_EMAIL, BW_MASTER_PASSWORD
CREDS_FILE="${CREDS_FILE:-${OPENCLAW_WORKSPACE:-$HOME/.openclaw/workspace}/secrets/bitwarden.env}"
SESSION_FILE="/tmp/.bw_session"

load_creds() {
  # SECURITY: Safe KEY=VALUE parsing without executing arbitrary shell code
  if [[ -f "$CREDS_FILE" ]]; then
    while IFS='=' read -r key value; do
      # Skip comments and empty lines
      [[ "$key" =~ ^[[:space:]]*# ]] && continue
      [[ -z "$key" ]] && continue
      # Strip quotes and whitespace
      value="${value%\"}"
      value="${value#\"}"
      value="${value%\'}"
      value="${value#\'}"
      key="${key//[[:space:]]/}"
      # Export only expected variables
      case "$key" in
        BW_SERVER|BW_EMAIL|BW_MASTER_PASSWORD)
          export "$key=$value"
          ;;
      esac
    done < "$CREDS_FILE"
  fi
  
  if [[ -z "${BW_SERVER:-}" ]]; then
    echo "ERROR: BW_SERVER not set. Configure via environment or credentials file." >&2
    exit 1
  fi
  if [[ -z "${BW_EMAIL:-}" ]]; then
    echo "ERROR: BW_EMAIL not set. Configure via environment or credentials file." >&2
    exit 1
  fi
  if [[ -z "${BW_MASTER_PASSWORD:-}" ]]; then
    echo "ERROR: BW_MASTER_PASSWORD not set. Configure via environment or credentials file." >&2
    exit 1
  fi
}

get_session() {
  if [[ -f "$SESSION_FILE" ]]; then
    cat "$SESSION_FILE"
  elif [[ -n "${BW_SESSION:-}" ]]; then
    echo "$BW_SESSION"
  fi
}

ensure_session() {
  local session
  session=$(get_session)
  if [[ -z "$session" ]]; then
    do_login
    session=$(get_session)
  fi
  if [[ -z "$session" ]]; then
    echo "ERROR: No active session. Run: bw.sh login" >&2
    exit 1
  fi
  export BW_SESSION="$session"
}

do_login() {
  load_creds

  # Configure server
  bw config server "$BW_SERVER" >/dev/null 2>&1 || true

  local status
  # Parse status JSON without python - extract "status":"value" pattern
  local raw_status
  raw_status=$(bw status 2>/dev/null || echo '{}')
  status=$(echo "$raw_status" | grep -oP '"status"\s*:\s*"\K[^"]+' 2>/dev/null || echo "unauthenticated")

  if [[ "$status" == "unauthenticated" ]]; then
    local session
    session=$(bw login "$BW_EMAIL" "$BW_MASTER_PASSWORD" --raw 2>/dev/null)
    echo "$session" > "$SESSION_FILE"
    chmod 600 "$SESSION_FILE"
    echo "Logged in successfully."
  elif [[ "$status" == "locked" ]]; then
    local session
    session=$(bw unlock "$BW_MASTER_PASSWORD" --raw 2>/dev/null)
    echo "$session" > "$SESSION_FILE"
    chmod 600 "$SESSION_FILE"
    echo "Vault unlocked."
  else
    echo "Already logged in and unlocked."
  fi
}

do_register() {
  load_creds
  local reg_email="${1:-$BW_EMAIL}"
  local reg_pass="${2:-$BW_MASTER_PASSWORD}"
  local reg_name="${3:-OpenClaw}"
  local kdf_iterations=600000

  # Validate inputs
  if [[ -z "$reg_email" || -z "$reg_pass" ]]; then
    echo "ERROR: Email and password are required for registration." >&2
    exit 1
  fi
  if [[ ${#reg_pass} -lt 12 ]]; then
    echo "ERROR: Master password must be at least 12 characters." >&2
    exit 1
  fi

  # Pure bash + openssl implementation of Bitwarden key derivation protocol:
  #   1. PBKDF2-SHA256 to derive master key from password + email (salt)
  #   2. PBKDF2-SHA256 (1 iteration) to derive master password hash for auth
  #   3. HKDF-Expand to derive encryption key and MAC key from master key
  #   4. AES-256-CBC + HMAC-SHA256 to encrypt the generated symmetric key

  local email_lower
  email_lower=$(echo -n "$reg_email" | tr '[:upper:]' '[:lower:]')

  # Step 1: Master key = PBKDF2-SHA256(password, email_lower, 600000, 32 bytes)
  local master_key_hex
  master_key_hex=$(openssl kdf -keylen 32 -kdfopt digest:SHA256 \
    -kdfopt "pass:$reg_pass" -kdfopt "hexsalt:$(echo -n "$email_lower" | xxd -p | tr -d '\n')" \
    -kdfopt "iter:$kdf_iterations" -binary PBKDF2 | xxd -p | tr -d '\n')

  # Step 2: Master password hash = PBKDF2-SHA256(master_key, password, 1, 32) → base64
  local master_password_hash
  master_password_hash=$(openssl kdf -keylen 32 -kdfopt digest:SHA256 \
    -kdfopt "hexpass:$master_key_hex" \
    -kdfopt "hexsalt:$(echo -n "$reg_pass" | xxd -p | tr -d '\n')" \
    -kdfopt "iter:1" -binary PBKDF2 | base64 -w0)

  # Step 3: HKDF-Expand to derive enc_key (32 bytes) and mac_key (32 bytes)
  local enc_key_hex mac_key_hex
  enc_key_hex=$(openssl kdf -keylen 32 -kdfopt digest:SHA256 \
    -kdfopt mode:EXPAND_ONLY \
    -kdfopt "hexkey:$master_key_hex" \
    -kdfopt "hexinfo:$(echo -n 'enc' | xxd -p | tr -d '\n')" \
    -binary HKDF | xxd -p | tr -d '\n')

  mac_key_hex=$(openssl kdf -keylen 32 -kdfopt digest:SHA256 \
    -kdfopt mode:EXPAND_ONLY \
    -kdfopt "hexkey:$master_key_hex" \
    -kdfopt "hexinfo:$(echo -n 'mac' | xxd -p | tr -d '\n')" \
    -binary HKDF | xxd -p | tr -d '\n')

  # Step 4: Generate 64-byte random symmetric key, encrypt with AES-256-CBC
  local sym_key_hex iv_hex ct_b64 iv_b64
  sym_key_hex=$(openssl rand -hex 64)
  iv_hex=$(openssl rand -hex 16)

  # AES-256-CBC encrypt (PKCS7 padding is default in openssl enc)
  ct_b64=$(echo -n "$sym_key_hex" | xxd -r -p | \
    openssl enc -aes-256-cbc -nosalt -K "$enc_key_hex" -iv "$iv_hex" | base64 -w0)

  iv_b64=$(echo -n "$iv_hex" | xxd -r -p | base64 -w0)

  # Step 5: HMAC-SHA256(iv || ciphertext, mac_key) for integrity
  local mac_b64
  mac_b64=$( (echo -n "$iv_hex" | xxd -r -p; echo -n "$ct_b64" | base64 -d) | \
    openssl dgst -sha256 -mac hmac -macopt "hexkey:$mac_key_hex" -binary | base64 -w0)

  # Format: type 2 = AES-CBC-256 + HMAC-SHA256
  local encrypted_key="2.${iv_b64}|${ct_b64}|${mac_b64}"

  # Submit registration via curl
  local response http_code body
  response=$(curl -s -w "\n%{http_code}" -X POST \
    "${BW_SERVER}/api/accounts/register" \
    -H "Content-Type: application/json" \
    -d "$(cat <<JSON
{
  "name": "$reg_name",
  "email": "$reg_email",
  "masterPasswordHash": "$master_password_hash",
  "masterPasswordHint": "",
  "key": "$encrypted_key",
  "kdf": 0,
  "kdfIterations": $kdf_iterations
}
JSON
)" --max-time 30)

  http_code=$(echo "$response" | tail -1)
  body=$(echo "$response" | sed '$d')

  if [[ "$http_code" == "200" ]]; then
    echo "Account registered successfully: $reg_email"
  else
    local msg
    msg=$(echo "$body" | grep -oP '"message"\s*:\s*"\K[^"]+' 2>/dev/null || echo "HTTP $http_code")
    echo "Registration failed: $msg" >&2
    exit 1
  fi
}

cmd="${1:-help}"
shift || true

case "$cmd" in
  register)
    do_register "$@"
    ;;
  login)
    do_login
    ;;
  status)
    bw status 2>/dev/null
    ;;
  sync)
    ensure_session
    bw sync
    ;;
  list)
    ensure_session
    if [[ $# -gt 0 ]]; then
      bw list items --search "$*"
    else
      bw list items
    fi
    ;;
  get)
    ensure_session
    bw get item "$1"
    ;;
  get-password)
    ensure_session
    bw get password "$1"
    ;;
  get-username)
    ensure_session
    bw get username "$1"
    ;;
  get-notes)
    ensure_session
    bw get notes "$1"
    ;;
  create)
    ensure_session
    local_name="${1:?name required}"
    local_user="${2:?username required}"
    local_pass="${3:?password required}"
    local_uri="${4:-}"
    local_notes="${5:-}"

    uris_json="[]"
    if [[ -n "$local_uri" ]]; then
      uris_json="[{\"uri\":\"$local_uri\"}]"
    fi

    template="{\"type\":1,\"name\":\"$local_name\",\"login\":{\"username\":\"$local_user\",\"password\":\"$local_pass\",\"uris\":$uris_json},\"notes\":\"$local_notes\"}"
    echo "$template" | bw encode | bw create item
    ;;
  create-json)
    ensure_session
    if [[ $# -gt 0 ]]; then
      echo "$1" | bw encode | bw create item
    else
      bw encode | bw create item
    fi
    ;;
  edit)
    ensure_session
    echo "$2" | bw encode | bw edit item "$1"
    ;;
  delete)
    ensure_session
    bw delete item "$1"
    ;;
  generate)
    local_len="${1:-24}"
    bw generate --length "$local_len" --uppercase --lowercase --number --special
    ;;
  lock)
    bw lock
    rm -f "$SESSION_FILE"
    ;;
  logout)
    bw logout
    rm -f "$SESSION_FILE"
    ;;
  help|*)
    cat <<EOF
Bitwarden CLI Wrapper (works with Bitwarden and Vaultwarden)

Usage: bw.sh <command> [args...]

Commands:
  register [email] [pass] [name] Register new account (uses env defaults)
  login                          Login/unlock vault
  status                         Show vault status
  sync                           Sync vault
  list [search]                  List items (optional search filter)
  get <name|id>                  Get full item
  get-password <name|id>         Get just the password
  get-username <name|id>         Get just the username
  get-notes <name|id>            Get just the notes
  create <name> <user> <pass> [uri] [notes]  Create login item
  create-json <json>             Create item from JSON
  edit <id> <json>               Edit item
  delete <id>                    Delete item
  generate [length]              Generate secure password
  lock                           Lock vault
  logout                         Logout
EOF
    ;;
esac
