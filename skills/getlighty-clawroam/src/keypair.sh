#!/usr/bin/env bash
# ClawRoam — Keypair Management
# Ed25519 keypair for authenticating with vault providers
# Private key in OpenSSH format (works with SSH/git providers)
# PEM copy derived automatically for API signing (openssl pkeyutl)
# Public key in SSH format (for display and provider registration)
# Usage: keypair.sh {generate|show-public|fingerprint|rotate|verify|sign|push-public}

set -euo pipefail

VAULT_DIR="$HOME/.clawroam"
KEY_DIR="$VAULT_DIR/keys"
PRIVATE_KEY="$KEY_DIR/clawroam_ed25519"
PUBLIC_KEY="$KEY_DIR/clawroam_ed25519.pub"
SIGNING_KEY="$KEY_DIR/clawroam_ed25519.pem"

timestamp() { date -u +"%Y-%m-%dT%H:%M:%SZ"; }
log() { echo "[clawroam:keys $(timestamp)] $*"; }

# Convert OpenSSH Ed25519 private key → PKCS8 PEM for openssl signing.
# Pure Python, no external deps. Parses the OpenSSH wire format to
# extract the 32-byte Ed25519 seed and wraps it in PKCS8 DER.
derive_pem_privkey() {
  local ssh_key="$1" pem_out="$2"
  python3 -c "
import base64, struct, sys

data = open('$ssh_key','rb').read()
lines = data.split(b'\n')
b64 = b''.join(l for l in lines if not l.startswith(b'-----'))
raw = base64.b64decode(b64)

# Skip 'openssh-key-v1\0' magic (15 bytes)
o = 15
def read_str(d, p):
    n = struct.unpack('>I', d[p:p+4])[0]
    return d[p+4:p+4+n], p+4+n

cipher, o = read_str(raw, o)
kdf, o = read_str(raw, o)
kdf_opts, o = read_str(raw, o)
num_keys = struct.unpack('>I', raw[o:o+4])[0]; o += 4
pub_blob, o = read_str(raw, o)
priv_blob, o = read_str(raw, o)

# Parse private section: checkint1(4) + checkint2(4) + keytype(str) + pubkey(str) + privkey(str)
p = 8  # skip two checkints
kt, p = read_str(priv_blob, p)
pub_raw, p = read_str(priv_blob, p)
priv_raw, p = read_str(priv_blob, p)  # 64 bytes: 32-byte seed + 32-byte pub
seed = priv_raw[:32]

# Build PKCS8 DER: SEQUENCE { INTEGER(0), SEQUENCE { OID Ed25519 }, OCTET STRING { OCTET STRING { seed } } }
version = b'\x02\x01\x00'
oid_seq = b'\x30\x05\x06\x03\x2b\x65\x70'
inner = b'\x04\x20' + seed
outer = b'\x04' + bytes([len(inner)]) + inner
body = version + oid_seq + outer
der = b'\x30' + bytes([len(body)]) + body

pem = b'-----BEGIN PRIVATE KEY-----\n'
b64 = base64.b64encode(der).decode()
for i in range(0, len(b64), 64):
    pem += (b64[i:i+64] + '\n').encode()
pem += b'-----END PRIVATE KEY-----\n'

open('$pem_out','wb').write(pem)
" 2>/dev/null
  chmod 600 "$pem_out"
}

# Ensure the PEM signing key exists (derive from OpenSSH key if missing)
ensure_signing_key() {
  if [[ ! -f "$SIGNING_KEY" ]] && [[ -f "$PRIVATE_KEY" ]]; then
    derive_pem_privkey "$PRIVATE_KEY" "$SIGNING_KEY"
  fi
}

# ─── Generate ─────────────────────────────────────────────────

cmd_generate() {
  mkdir -p "$KEY_DIR"

  if [[ -f "$PRIVATE_KEY" ]]; then
    log "Keypair already exists."
    log "  Public key: $PUBLIC_KEY"
    log "  Use 'keypair.sh rotate' to regenerate."
    return 0
  fi

  log "Generating Ed25519 keypair..."

  local comment
  comment="clawroam@$(hostname -s 2>/dev/null || echo unknown)-$(date +%s)"

  # Generate OpenSSH-format Ed25519 key (works with SSH/git providers)
  ssh-keygen -t ed25519 \
    -f "$PRIVATE_KEY" \
    -N "" \
    -C "$comment" \
    -q

  # Derive PEM copy for API signing (openssl pkeyutl)
  derive_pem_privkey "$PRIVATE_KEY" "$SIGNING_KEY"

  # Lock down permissions
  chmod 700 "$KEY_DIR"
  chmod 600 "$PRIVATE_KEY"
  chmod 600 "$SIGNING_KEY"
  chmod 644 "$PUBLIC_KEY"

  local fingerprint
  fingerprint=$(ssh-keygen -lf "$PUBLIC_KEY" 2>/dev/null | awk '{print $2}')

  log "Keypair generated"
  log "  Private key: $PRIVATE_KEY (600 — never share this)"
  log "  Public key:  $PUBLIC_KEY"
  log "  Fingerprint: $fingerprint"
  echo ""
  echo "Public key (add this to your vault provider):"
  echo "────────────────────────────────────────────────"
  cat "$PUBLIC_KEY"
  echo "────────────────────────────────────────────────"
}

# ─── Show Public ──────────────────────────────────────────────

cmd_show_public() {
  if [[ ! -f "$PUBLIC_KEY" ]]; then
    log "No keypair found. Run 'keypair.sh generate' first."
    return 1
  fi

  echo ""
  echo "ClawRoam Public Key"
  echo "━━━━━━━━━━━━━━━━━━━━"
  cat "$PUBLIC_KEY"
  echo ""

  local fingerprint
  fingerprint=$(ssh-keygen -lf "$PUBLIC_KEY" 2>/dev/null | awk '{print $2}')
  echo "Fingerprint: $fingerprint"
  echo ""
}

# ─── Fingerprint ──────────────────────────────────────────────

cmd_fingerprint() {
  if [[ ! -f "$PUBLIC_KEY" ]]; then
    log "No keypair found."
    return 1
  fi
  ssh-keygen -lf "$PUBLIC_KEY" 2>/dev/null
}

# ─── Rotate ───────────────────────────────────────────────────

cmd_rotate() {
  if [[ ! -f "$PRIVATE_KEY" ]]; then
    log "No existing keypair. Generating new one..."
    cmd_generate
    return $?
  fi

  echo ""
  echo "Key rotation will:"
  echo "   1. Archive your current keypair"
  echo "   2. Generate a new Ed25519 keypair"
  echo "   3. You'll need to re-register with your vault provider"
  echo ""
  read -rp "Continue? [y/N]: " yn
  if [[ ! "$yn" =~ ^[Yy] ]]; then
    log "Rotation cancelled."
    return 0
  fi

  # Archive old keys
  local archive_dir="$KEY_DIR/archived"
  mkdir -p "$archive_dir"
  local ts
  ts=$(date +%Y%m%d-%H%M%S)
  mv "$PRIVATE_KEY" "$archive_dir/clawroam_ed25519.$ts"
  mv "$PUBLIC_KEY" "$archive_dir/clawroam_ed25519.$ts.pub"
  [[ -f "$SIGNING_KEY" ]] && mv "$SIGNING_KEY" "$archive_dir/clawroam_ed25519.$ts.pem"
  log "Old keypair archived to $archive_dir/"

  # Generate new
  cmd_generate

  echo ""
  log "Remember to update your public key with your vault provider!"
  log "  For ClawRoam Cloud: clawroam.sh cloud update-key"
  log "  For Git: add the new public key to your repo's deploy keys"
  log "  For others: re-run 'clawroam.sh provider setup <name>'"
}

# ─── Verify ───────────────────────────────────────────────────

cmd_verify() {
  if [[ ! -f "$PRIVATE_KEY" || ! -f "$PUBLIC_KEY" ]]; then
    log "Keypair not found"
    return 1
  fi

  local issues=0

  # Check permissions
  local priv_perms
  priv_perms=$(stat -c "%a" "$PRIVATE_KEY" 2>/dev/null || stat -f "%OLp" "$PRIVATE_KEY" 2>/dev/null)

  if [[ "$priv_perms" != "600" ]]; then
    log "Private key permissions are $priv_perms (should be 600)"
    log "  Fix: chmod 600 $PRIVATE_KEY"
    issues=$((issues + 1))
  fi

  # Verify key pair matches
  local priv_pub stored_pub
  priv_pub=$(ssh-keygen -yf "$PRIVATE_KEY" 2>/dev/null | awk '{print $2}')
  stored_pub=$(awk '{print $2}' "$PUBLIC_KEY")

  if [[ "$priv_pub" != "$stored_pub" ]]; then
    log "Public key doesn't match private key!"
    issues=$((issues + 1))
  fi

  # Test SSH signing
  local test_file
  test_file=$(mktemp)
  echo "clawroam-verify-test" > "$test_file"

  if ssh-keygen -Y sign -f "$PRIVATE_KEY" -n clawroam "$test_file" &>/dev/null; then
    log "SSH signing works"
  else
    log "SSH signing failed"
    issues=$((issues + 1))
  fi
  rm -f "$test_file" "$test_file.sig"

  # Test API signing (PEM key)
  ensure_signing_key
  if [[ -f "$SIGNING_KEY" ]]; then
    local test_payload test_sig pub_pem
    test_payload=$(mktemp)
    test_sig=$(mktemp)
    pub_pem=$(mktemp)
    echo -n "verify-test" > "$test_payload"
    openssl pkey -in "$SIGNING_KEY" -pubout -out "$pub_pem" 2>/dev/null

    if openssl pkeyutl -sign -inkey "$SIGNING_KEY" -rawin -in "$test_payload" -out "$test_sig" 2>/dev/null && \
       openssl pkeyutl -verify -pubin -inkey "$pub_pem" -rawin -in "$test_payload" -sigfile "$test_sig" 2>/dev/null; then
      log "API signing works"
    else
      log "API signing failed"
      issues=$((issues + 1))
    fi
    rm -f "$test_payload" "$test_sig" "$pub_pem"
  fi

  if [[ $issues -eq 0 ]]; then
    log "Keypair is healthy"
    local fingerprint
    fingerprint=$(ssh-keygen -lf "$PUBLIC_KEY" 2>/dev/null | awk '{print $2}')
    log "  Fingerprint: $fingerprint"
  else
    log "$issues issue(s) found"
  fi
}

# ─── Sign (used by cloud.sh for API auth) ────────────────────

cmd_sign() {
  local payload="${2:-}"
  if [[ -z "$payload" ]]; then
    log "Usage: keypair.sh sign <payload_string>"
    return 1
  fi

  if [[ ! -f "$PRIVATE_KEY" ]]; then
    log "No keypair found."
    return 1
  fi

  # Ensure PEM signing key exists
  ensure_signing_key

  local tmp_payload tmp_sig
  tmp_payload=$(mktemp)
  tmp_sig=$(mktemp)
  echo -n "$payload" > "$tmp_payload"
  openssl pkeyutl -sign -inkey "$SIGNING_KEY" -rawin -in "$tmp_payload" -out "$tmp_sig" 2>/dev/null
  base64 -w0 "$tmp_sig" 2>/dev/null || base64 -i "$tmp_sig"
  rm -f "$tmp_payload" "$tmp_sig"
}

# ─── Push Public Key ──────────────────────────────────────────

cmd_push_public() {
  if [[ ! -f "$PUBLIC_KEY" ]]; then
    log "No keypair found. Run 'keypair.sh generate' first."
    return 1
  fi

  local instance_id hostname_str fingerprint
  instance_id=$(grep 'instance_id:' "$VAULT_DIR/config.yaml" 2>/dev/null | head -1 | awk '{print $2}' | tr -d '"')
  hostname_str=$(hostname -s 2>/dev/null || echo "unknown")
  fingerprint=$(ssh-keygen -lf "$PUBLIC_KEY" 2>/dev/null | awk '{print $2}')

  mkdir -p "$VAULT_DIR/identity/public-keys"

  local dest="$VAULT_DIR/identity/public-keys/${hostname_str}.pub"
  cp "$PUBLIC_KEY" "$dest"

  log "Public key pushed to vault"
  log "  Stored as: identity/public-keys/${hostname_str}.pub"
  log "  Fingerprint: $fingerprint"
  log "  Instance: $instance_id"
}

# ─── Main ─────────────────────────────────────────────────────

case "${1:-show-public}" in
  generate)     cmd_generate ;;
  show-public)  cmd_show_public ;;
  fingerprint)  cmd_fingerprint ;;
  rotate)       cmd_rotate ;;
  verify)       cmd_verify ;;
  sign)         cmd_sign "$@" ;;
  push-public)  cmd_push_public ;;
  *)            echo "Usage: keypair.sh {generate|show-public|fingerprint|rotate|verify|push-public|sign}"; exit 1 ;;
esac
