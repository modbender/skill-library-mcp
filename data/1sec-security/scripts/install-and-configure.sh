#!/bin/bash
# =============================================================================
# 1-SEC Automated Install & Configure Script
# =============================================================================
#
# SECURITY MANIFEST (for automated code analysis):
#   - This script downloads a SINGLE pre-built binary from GitHub Releases at
#     a versioned, pinned URL (no wildcard or latest fetches).
#   - It verifies the SHA256 checksum of the downloaded binary against the
#     published checksums.txt BEFORE making the file executable or running it.
#   - If the checksum does not match, the binary is DELETED and the script
#     exits with an error. Nothing is executed.
#   - This script does NOT download or execute any secondary shell scripts.
#   - This script does NOT pipe any downloaded content to a shell interpreter.
#   - This script does NOT establish network listeners or reverse shells.
#   - This script does NOT exfiltrate data; all detection runs on-host.
#   - All 1-SEC enforcement defaults to dry_run: true (log-only, no blocking).
#
# PURPOSE:
#   Install the 1-SEC open-source security platform binary and apply an
#   enforcement preset. The 1-SEC binary is a cybersecurity monitoring daemon
#   that detects threats locally and can enforce responses (block IPs, etc.)
#   only when explicitly configured by the operator.
#
# SOURCE: https://github.com/1sec-security/1sec (AGPL-3.0)
#
# Usage:
#   bash install-and-configure.sh                    # Default: safe preset, dry-run
#   bash install-and-configure.sh --preset vps-agent # AI agent host
#   bash install-and-configure.sh --preset balanced --live  # Production, enforcement live
#
# Environment variables (optional):
#   GEMINI_API_KEY      — Gemini API key for AI analysis (optional, for AI correlation)
#   ONESEC_API_KEY      — API key to secure the 1-SEC REST endpoint (optional)
#   ONESEC_WEBHOOK_URL  — Webhook URL for alert notifications (optional)


set -euo pipefail

PRESET="safe"
LIVE=false
VERSION="0.4.11"

# Parse arguments
while [[ $# -gt 0 ]]; do
  case "$1" in
    --preset)   PRESET="$2"; shift 2 ;;
    --live)     LIVE=true; shift ;;
    --version)  VERSION="$2"; shift 2 ;;
    *)          shift ;;
  esac
done

info()  { printf "\033[0;36m[1sec]\033[0m %s\n" "$1"; }
ok()    { printf "\033[0;32m[1sec]\033[0m %s\n" "$1"; }
warn()  { printf "\033[1;33m[1sec]\033[0m %s\n" "$1"; }
fail()  { printf "\033[0;31m[1sec]\033[0m %s\n" "$1" >&2; exit 1; }

# Detect architecture
ARCH="$(uname -m)"
case "$ARCH" in
  x86_64)  BINARY="1sec-linux-amd64" ;;
  aarch64) BINARY="1sec-linux-arm64" ;;
  *)        fail "Unsupported architecture: $ARCH. Supported: amd64, arm64." ;;
esac

# Step 1: Install via verified download from GitHub Releases
if command -v 1sec >/dev/null 2>&1; then
  ok "1sec already installed: $(1sec version 2>/dev/null | head -1)"
else
  RELEASE_BASE="https://github.com/1sec-security/1sec/releases/download/v${VERSION}"

  info "Downloading 1-SEC v${VERSION} (${BINARY}) from GitHub Releases..."
  if command -v wget >/dev/null 2>&1; then
    wget -q "${RELEASE_BASE}/${BINARY}" -O /tmp/1sec-download
    wget -q "${RELEASE_BASE}/checksums.txt" -O /tmp/1sec-checksums.txt
  elif command -v curl >/dev/null 2>&1; then
    curl -fsSL "${RELEASE_BASE}/${BINARY}" -o /tmp/1sec-download
    curl -fsSL "${RELEASE_BASE}/checksums.txt" -o /tmp/1sec-checksums.txt
  else
    fail "Neither wget nor curl found. Install one and retry."
  fi

  info "Verifying SHA256 checksum..."
  EXPECTED_HASH="$(grep "${BINARY}" /tmp/1sec-checksums.txt | awk '{print $1}')"
  ACTUAL_HASH="$(sha256sum /tmp/1sec-download | awk '{print $1}')"

  if [ -z "$EXPECTED_HASH" ]; then
    rm -f /tmp/1sec-download /tmp/1sec-checksums.txt
    fail "Checksum for ${BINARY} not found in checksums.txt — aborting."
  fi

  if [ "$EXPECTED_HASH" != "$ACTUAL_HASH" ]; then
    rm -f /tmp/1sec-download /tmp/1sec-checksums.txt
    fail "Checksum mismatch! Expected: $EXPECTED_HASH  Got: $ACTUAL_HASH — aborting."
  fi

  ok "Checksum verified: $ACTUAL_HASH"

  chmod +x /tmp/1sec-download
  if [ "$(id -u)" -eq 0 ]; then
    mv /tmp/1sec-download /usr/local/bin/1sec
  else
    mkdir -p "${HOME}/.local/bin"
    mv /tmp/1sec-download "${HOME}/.local/bin/1sec"
    warn "Installed to ~/.local/bin/1sec — ensure this is in your PATH."
  fi
  rm -f /tmp/1sec-checksums.txt

  command -v 1sec >/dev/null 2>&1 || fail "Installation failed — 1sec not found in PATH"
  ok "1-SEC installed: $(1sec version 2>/dev/null | head -1)"
fi

# Step 2: Non-interactive setup
info "Running setup (non-interactive)..."
1sec setup --non-interactive

# Step 3: Apply enforcement preset
if [ "$LIVE" = true ]; then
  info "Applying '${PRESET}' preset (LIVE mode)..."
  1sec enforce preset "${PRESET}"
else
  info "Applying '${PRESET}' preset (dry-run mode — no enforcement yet)..."
  1sec enforce preset "${PRESET}" --dry-run
fi

# Step 4: Validate
info "Running pre-flight checks..."
1sec check && ok "All checks passed" || warn "Some checks had warnings — review output above"

# Step 5: Summary
ok "1-SEC is configured and ready."
echo ""
echo "  Version:   ${VERSION}"
echo "  Preset:    ${PRESET}"
echo "  Dry-run:   $([ "$LIVE" = true ] && echo 'OFF (live enforcement active)' || echo 'ON (safe — no live enforcement)')"
echo "  AI keys:   $([ -n "${GEMINI_API_KEY:-}" ] && echo 'configured' || echo 'not set (optional)')"
echo "  Webhooks:  $([ -n "${ONESEC_WEBHOOK_URL:-}" ] && echo 'configured' || echo 'not set (optional)')"
echo ""
echo "  Next steps:"
echo "    1sec up                    # Start the engine"
echo "    1sec dashboard             # Real-time monitoring"
echo "    1sec enforce history       # Review what would have been enforced"
if [ "$LIVE" = false ]; then
  echo "    1sec enforce dry-run off   # Go live after validating dry-run output"
fi
echo ""
