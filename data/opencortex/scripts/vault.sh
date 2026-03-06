#!/bin/bash
# OpenCortex Vault — Encrypted key-value store for sensitive data
# Uses GPG symmetric encryption (AES-256).
# Passphrase storage (in order of preference):
#   1. System keyring (secret-tool / macOS Keychain / keyctl)
#   2. Environment variable OPENCORTEX_VAULT_PASS
#   3. File at .vault/.passphrase (mode 600) — fallback
#
# Usage:
#   vault.sh init              — Set up vault (creates encrypted store + stores passphrase)
#   vault.sh set <key> <value> — Store a secret
#   vault.sh get <key>         — Retrieve a secret (stdout only, no logging)
#   vault.sh list              — List stored keys (not values)
#   vault.sh delete <key>      — Remove a secret
#   vault.sh rotate            — Rotate passphrase (re-encrypts all secrets)

set -euo pipefail

WORKSPACE="${CLAWD_WORKSPACE:-$(cd "$(dirname "$0")/.." && pwd)}"
VAULT_DIR="$WORKSPACE/.vault"
VAULT_FILE="$VAULT_DIR/secrets.gpg"
VAULT_PASS_FILE="$VAULT_DIR/.passphrase"
KEYRING_LABEL="opencortex-vault"

# --- Passphrase backend detection ---

_keyring_backend() {
  # Returns: secret-tool, keychain, keyctl, env, file, none
  if command -v secret-tool &>/dev/null; then
    echo "secret-tool"
  elif command -v security &>/dev/null && [[ "$OSTYPE" == darwin* ]]; then
    echo "keychain"
  elif command -v keyctl &>/dev/null; then
    echo "keyctl"
  elif [ -n "${OPENCORTEX_VAULT_PASS:-}" ]; then
    echo "env"
  elif [ -f "$VAULT_PASS_FILE" ]; then
    echo "file"
  else
    echo "none"
  fi
}

_store_passphrase() {
  local pass="$1"
  local backend=$(_keyring_backend)
  
  case "$backend" in
    secret-tool)
      echo "$pass" | secret-tool store --label="$KEYRING_LABEL" service opencortex key vault-passphrase 2>/dev/null
      echo "   🔐 Passphrase stored in system keyring (secret-tool)"
      ;;
    keychain)
      security add-generic-password -a opencortex -s "$KEYRING_LABEL" -w "$pass" 2>/dev/null || \
        security delete-generic-password -a opencortex -s "$KEYRING_LABEL" 2>/dev/null && \
        security add-generic-password -a opencortex -s "$KEYRING_LABEL" -w "$pass"
      echo "   🔐 Passphrase stored in macOS Keychain"
      ;;
    keyctl)
      local ring=$(keyctl newring opencortex @u 2>/dev/null || keyctl search @u keyring opencortex 2>/dev/null)
      echo "$pass" | keyctl padd user vault-passphrase "$ring" >/dev/null 2>&1
      echo "   🔐 Passphrase stored in kernel keyring (keyctl)"
      ;;
    *)
      # Fallback to file — only if explicitly allowed
      if [ "${OPENCORTEX_ALLOW_FILE_PASSPHRASE:-0}" = "1" ]; then
        echo "$pass" > "$VAULT_PASS_FILE"
        chmod 600 "$VAULT_PASS_FILE"
        echo "   📁 Passphrase stored in $VAULT_PASS_FILE (mode 600)"
        echo "   ⚠️  File-based storage is less secure than a system keyring"
      else
        echo "   ❌ No system keyring available (need secret-tool, macOS Keychain, or keyctl)."
        echo "   💡 Install a keyring tool, or set OPENCORTEX_ALLOW_FILE_PASSPHRASE=1 to allow file-based storage."
        return 1
      fi
      ;;
  esac
}

_get_passphrase() {
  local backend=$(_keyring_backend)
  
  case "$backend" in
    secret-tool)
      secret-tool lookup service opencortex key vault-passphrase 2>/dev/null
      ;;
    keychain)
      security find-generic-password -a opencortex -s "$KEYRING_LABEL" -w 2>/dev/null
      ;;
    keyctl)
      local ring=$(keyctl search @u keyring opencortex 2>/dev/null) || { echo ""; return 1; }
      local key=$(keyctl search "$ring" user vault-passphrase 2>/dev/null) || { echo ""; return 1; }
      keyctl print "$key" 2>/dev/null
      ;;
    env)
      echo "${OPENCORTEX_VAULT_PASS:-}"
      ;;
    file)
      cat "$VAULT_PASS_FILE" 2>/dev/null
      ;;
    *)
      echo ""
      return 1
      ;;
  esac
}

_ensure_vault() {
  if [ ! -f "$VAULT_FILE" ]; then
    echo "Vault not initialized. Run: vault.sh init"
    exit 1
  fi
  local pass=$(_get_passphrase)
  if [ -z "$pass" ]; then
    echo "❌ Cannot retrieve vault passphrase."
    echo "   Checked: system keyring, OPENCORTEX_VAULT_PASS env, $VAULT_PASS_FILE"
    echo "   Run 'vault.sh init' to set up, or set OPENCORTEX_VAULT_PASS."
    exit 1
  fi
}

# Passphrase passed via fd 3 to avoid exposure in process list
_encrypt() {
  local content="$1"
  local pass=$(_get_passphrase)
  local tmpfile=$(mktemp)
  echo "$content" > "$tmpfile"
  gpg --batch --yes --passphrase-fd 3 --quiet --symmetric --cipher-algo AES256 --output "$VAULT_FILE" "$tmpfile" 3<<< "$pass" 2>/dev/null
  rm -f "$tmpfile"
  chmod 600 "$VAULT_FILE"
}

_decrypt() {
  local pass=$(_get_passphrase)
  gpg --batch --yes --passphrase-fd 3 --quiet --decrypt "$VAULT_FILE" 3<<< "$pass" 2>/dev/null
}

case "${1:-help}" in
  init)
    mkdir -p "$VAULT_DIR"
    chmod 700 "$VAULT_DIR"
    
    # Check if vault already exists with a retrievable passphrase
    if [ -f "$VAULT_FILE" ]; then
      local_pass=$(_get_passphrase 2>/dev/null || true)
      if [ -n "$local_pass" ]; then
        echo "Vault already initialized at $VAULT_DIR"
        echo "   Backend: $(_keyring_backend)"
        exit 0
      fi
    fi
    
    # Generate random passphrase
    PASS=$(openssl rand -base64 32)
    
    # Store in best available backend
    _store_passphrase "$PASS"
    
    # Create empty vault
    # Temporarily set file backend for initial encrypt
    echo "$PASS" > "$VAULT_PASS_FILE"
    chmod 600 "$VAULT_PASS_FILE"
    _encrypt ""
    
    # If we stored in keyring, remove the file
    local backend=$(_keyring_backend)
    if [ "$backend" != "file" ] && [ "$backend" != "none" ]; then
      rm -f "$VAULT_PASS_FILE"
      echo "   🗑️  Removed file-based passphrase (using $backend instead)"
    fi
    
    echo "✅ Vault initialized at $VAULT_DIR"
    ;;
    
  set)
    _ensure_vault
    KEY="${2:-}"
    VALUE="${3:-}"
    
    if [ -z "$KEY" ] || [ -z "$VALUE" ]; then
      echo "Usage: vault.sh set <key> <value>"
      exit 1
    fi

    # Validate key name
    if ! echo "$KEY" | grep -qE '^[a-zA-Z_][a-zA-Z0-9_]*$'; then
      echo "❌ Invalid key name: '$KEY'"
      echo "   Key must start with a letter or underscore, and contain only"
      echo "   letters, digits, and underscores."
      exit 1
    fi

    CONTENT=$(_decrypt | grep -v "^${KEY}=" || true)
    CONTENT="${CONTENT}
${KEY}=${VALUE}"
    _encrypt "$CONTENT"
    
    echo "✅ Stored: $KEY"
    ;;
    
  get)
    _ensure_vault
    KEY="${2:-}"
    
    if [ -z "$KEY" ]; then
      echo "Usage: vault.sh get <key>"
      exit 1
    fi
    
    VALUE=$(_decrypt | grep "^${KEY}=" | head -1 | cut -d= -f2-)
    
    if [ -z "$VALUE" ]; then
      echo "Key not found: $KEY" >&2
      exit 1
    fi
    
    echo "$VALUE"
    ;;
    
  list)
    _ensure_vault
    _decrypt | grep -v "^$" | cut -d= -f1 | sort
    ;;
    
  delete)
    _ensure_vault
    KEY="${2:-}"
    
    if [ -z "$KEY" ]; then
      echo "Usage: vault.sh delete <key>"
      exit 1
    fi
    
    CONTENT=$(_decrypt | grep -v "^${KEY}=" || true)
    _encrypt "$CONTENT"
    
    echo "✅ Deleted: $KEY"
    ;;
    
  rotate)
    _ensure_vault
    echo "🔄 Rotating vault passphrase..."

    # Decrypt all secrets with current passphrase
    CONTENT=$(_decrypt)

    # Generate new passphrase
    NEW_PASS=$(openssl rand -base64 32)

    # Store new passphrase
    _store_passphrase "$NEW_PASS"
    
    # If file backend, update directly
    if [ -f "$VAULT_PASS_FILE" ]; then
      echo "$NEW_PASS" > "$VAULT_PASS_FILE"
      chmod 600 "$VAULT_PASS_FILE"
    fi

    # Re-encrypt with new passphrase (fd 3 to avoid process list exposure)
    local tmpfile=$(mktemp)
    echo "$CONTENT" > "$tmpfile"
    gpg --batch --yes --passphrase-fd 3 --quiet --symmetric --cipher-algo AES256 --output "$VAULT_FILE" "$tmpfile" 3<<< "$NEW_PASS" 2>/dev/null
    rm -f "$tmpfile"
    chmod 600 "$VAULT_FILE"

    echo "✅ Passphrase rotated. All secrets re-encrypted."
    echo "   Backend: $(_keyring_backend)"
    ;;

  migrate)
    # Migrate passphrase from file to system keyring
    _ensure_vault
    if [ ! -f "$VAULT_PASS_FILE" ]; then
      echo "No file-based passphrase to migrate."
      echo "Current backend: $(_keyring_backend)"
      exit 0
    fi
    
    PASS=$(cat "$VAULT_PASS_FILE")
    OLD_BACKEND=$(_keyring_backend)
    
    # Try to store in keyring (will use best available non-file backend)
    if command -v secret-tool &>/dev/null || { command -v security &>/dev/null && [[ "$OSTYPE" == darwin* ]]; } || command -v keyctl &>/dev/null; then
      _store_passphrase "$PASS"
      # Verify we can retrieve it
      VERIFY=$(_get_passphrase)
      if [ "$VERIFY" = "$PASS" ]; then
        rm -f "$VAULT_PASS_FILE"
        echo "✅ Migrated passphrase from file → $(_keyring_backend)"
        echo "   🗑️  Removed $VAULT_PASS_FILE"
      else
        echo "❌ Migration failed — keyring retrieval mismatch. File kept."
      fi
    else
      echo "❌ No system keyring available (need secret-tool, macOS Keychain, or keyctl)."
      echo "   Passphrase remains in $VAULT_PASS_FILE"
    fi
    ;;

  backend)
    echo "Passphrase backend: $(_keyring_backend)"
    if [ -f "$VAULT_PASS_FILE" ]; then
      echo "⚠️  File-based passphrase exists at $VAULT_PASS_FILE"
      echo "   Run 'vault.sh migrate' to move to system keyring"
    fi
    ;;

  help|*)
    echo "OpenCortex Vault — Encrypted secret storage"
    echo ""
    echo "Commands:"
    echo "  init              Set up vault (auto-detects best passphrase storage)"
    echo "  set <key> <value> Store a secret"
    echo "  get <key>         Retrieve a secret"
    echo "  list              List keys (not values)"
    echo "  delete <key>      Remove a secret"
    echo "  rotate            Rotate passphrase (re-encrypts all secrets)"
    echo "  migrate           Move passphrase from file → system keyring"
    echo "  backend           Show current passphrase storage backend"
    echo ""
    echo "Passphrase storage (in order of preference):"
    echo "  1. secret-tool    Linux keyring (GNOME/KDE)"
    echo "  2. security       macOS Keychain"
    echo "  3. keyctl         Linux kernel keyring"
    echo "  4. env var        OPENCORTEX_VAULT_PASS"
    echo "  5. file           .vault/.passphrase (mode 600, fallback)"
    echo ""
    echo "Current backend: $(_keyring_backend)"
    ;;
esac
