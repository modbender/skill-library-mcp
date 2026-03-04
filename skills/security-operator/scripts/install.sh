#!/usr/bin/env bash
set -euo pipefail

# Security Operator: VPS baseline hardening (workshop-safe)
#
# Default behavior: plan-only. Prints commands. Makes NO changes.
# Optional: --apply-firewall applies ONLY UFW baseline with confirmations.
#
# Intentionally does NOT edit SSH config, users, sudoers, or OpenClaw config.
# Those are the easiest ways to brick someone in a workshop.

APPLY_FIREWALL=0
if [[ "${1:-}" == "--apply-firewall" ]]; then
  APPLY_FIREWALL=1
fi

say() { printf "%s\n" "$*"; }
ask() {
  local prompt="$1"
  local default="${2:-}"
  local out
  if [[ -n "$default" ]]; then
    read -r -p "$prompt [$default]: " out || true
    echo "${out:-$default}"
  else
    read -r -p "$prompt: " out || true
    echo "$out"
  fi
}
confirm() {
  local prompt="$1"
  local yn
  read -r -p "$prompt (y/N): " yn || true
  [[ "${yn,,}" == "y" || "${yn,,}" == "yes" ]]
}

say ""
say "Security Operator install (workshop baseline)"
say "- Default: plan only (no changes)."
say "- Optional: --apply-firewall applies ONLY UFW baseline (safer)."
say ""

PLATFORM=$(ask "Platform" "hostinger-vps")
OS=$(ask "OS" "ubuntu")
HAS_CONSOLE=$(ask "Do you have provider web console access as backup" "yes")
ALLOW_SSH_FROM=$(ask "Allow SSH from which IP (blank = allow all)" "")
SSH_PORT=$(ask "SSH port to allow in firewall (default 22)" "22")

say ""
say "Summary"
say "- platform: $PLATFORM"
say "- os: $OS"
say "- console backup: $HAS_CONSOLE"
if [[ -n "$ALLOW_SSH_FROM" ]]; then
  say "- ssh allowlist ip: $ALLOW_SSH_FROM"
else
  say "- ssh allowlist ip: (none)"
fi
say "- ssh port allowed: $SSH_PORT"

say ""
say "Baseline plan (workshop-safe)"
say "1) Update packages (optional)"
say "2) Install UFW"
say "3) UFW defaults: deny inbound, allow outbound"
say "4) Allow SSH (port $SSH_PORT)"
say "5) Enable UFW"

CMD_UPDATE="sudo apt-get update && sudo apt-get -y upgrade"
CMD_UFW_INSTALL="sudo apt-get -y install ufw"
CMD_UFW_DEFAULTS="sudo ufw default deny incoming && sudo ufw default allow outgoing"

if [[ -n "$ALLOW_SSH_FROM" ]]; then
  CMD_UFW_SSH_ALLOW="sudo ufw allow from $ALLOW_SSH_FROM to any port $SSH_PORT proto tcp"
else
  CMD_UFW_SSH_ALLOW="sudo ufw allow $SSH_PORT/tcp"
fi
CMD_UFW_ENABLE="sudo ufw --force enable && sudo ufw status verbose"

say ""
say "Commands (copy/paste)"
cat <<EOF
$CMD_UPDATE
$CMD_UFW_INSTALL
$CMD_UFW_DEFAULTS
$CMD_UFW_SSH_ALLOW
$CMD_UFW_ENABLE
EOF

if [[ $APPLY_FIREWALL -eq 0 ]]; then
  say ""
  say "Plan only complete. No changes were made."
  exit 0
fi

say ""
say "Applying UFW baseline only (with confirmations)."

if confirm "Install ufw"; then
  bash -lc "$CMD_UFW_INSTALL"
fi

if confirm "Set UFW defaults (deny inbound, allow outbound)"; then
  bash -lc "$CMD_UFW_DEFAULTS"
fi

if confirm "Allow SSH in UFW"; then
  bash -lc "$CMD_UFW_SSH_ALLOW"
fi

if confirm "Enable UFW"; then
  bash -lc "$CMD_UFW_ENABLE"
fi

say ""
say "Done. This script did not touch SSH config or OpenClaw config."
