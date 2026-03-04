#!/usr/bin/env bash
set -euo pipefail

SCRIPT_PATH="$(readlink -f "${BASH_SOURCE[0]}")"
SCRIPT_DIR="$(cd -- "$(dirname -- "$SCRIPT_PATH")" && pwd)"
SKILL_DIR="$(cd -- "${SCRIPT_DIR}/.." && pwd)"
CFG_EXAMPLE="${SKILL_DIR}/config.env.example"
CFG_REAL="${SKILL_DIR}/config.env"

have() { command -v "$1" >/dev/null 2>&1; }
fail() { echo "ssh-op onboarding: $*" >&2; exit 1; }

prereqs() {
  have op || fail "missing op"
  have ssh || fail "missing ssh"
  have ssh-agent || fail "missing ssh-agent"
  have ssh-add || fail "missing ssh-add"
  op whoami >/dev/null 2>&1 || fail "op not authenticated (run: op whoami). If using service accounts, ensure OP_SERVICE_ACCOUNT_TOKEN is set."
}

write_real_config() {
  local vault="$1"
  local item="$2"
  local field="$3"
  local fp="$4"
  [[ -f "$CFG_EXAMPLE" ]] || fail "missing example config: $CFG_EXAMPLE"

  cat > "$CFG_REAL" <<EOF
# ssh-op config (machine-specific)
# Example file: ${CFG_EXAMPLE}

SSH_OP_VAULT_NAME="${vault}"
SSH_OP_ITEM_TITLE="${item}"
SSH_OP_KEY_FIELD="${field}"
SSH_OP_KEY_FINGERPRINT_SHA256="${fp}"

SSH_OP_HOSTS_FILE="hosts.conf"
EOF
  echo "Wrote: $CFG_REAL"
}

main() {
  prereqs

  echo "Using example config: $CFG_EXAMPLE"
  echo "Writing real config:   $CFG_REAL"
  echo

  read -r -p "1Password vault name: " vault
  read -r -p "1Password item title: " item
  read -r -p "Key field name [private key]: " field
  field="${field:-private key}"

  echo
  echo "Optional: fingerprint from 'ssh-add -l' (SHA256:...)" 
  read -r -p "Fingerprint (leave blank to always load): " fp

  echo
  echo "About to set:" 
  echo "  SSH_OP_VAULT_NAME=\"$vault\""
  echo "  SSH_OP_ITEM_TITLE=\"$item\""
  echo "  SSH_OP_KEY_FIELD=\"$field\""
  echo "  SSH_OP_KEY_FINGERPRINT_SHA256=\"$fp\""
  read -r -p "Confirm? [y/N]: " ok
  [[ "$ok" =~ ^[Yy]$ ]] || fail "aborted"

  write_real_config "$vault" "$item" "$field" "$fp"

  echo "\nNext: ensure ssh-op is on PATH (optional):"
  echo "  mkdir -p ~/.local/bin && ln -sf ~/.openclaw/skills/ssh-op/scripts/ssh-op ~/.local/bin/ssh-op"

  echo "\nTest (will prompt for host alias):"
  echo "  ssh-op -T <host-alias>"

  echo "\nOptional: put Host entries into ${SKILL_DIR}/hosts.conf and run:"
  echo "  ${SKILL_DIR}/scripts/ensure_ssh_config.py"
}

main "$@"
