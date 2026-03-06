#!/usr/bin/env bash
set -euo pipefail

# agent-security-ops: One-command repo security setup
# MARKER:agent-security-ops

SCRIPT_VERSION="1.1.0"

# Colors (degrade gracefully)
if [ -t 2 ]; then
  GREEN='\033[0;32m'; YELLOW='\033[0;33m'; RED='\033[0;31m'; BLUE='\033[0;34m'; NC='\033[0m'; BOLD='\033[1m'
else
  GREEN=''; YELLOW=''; RED=''; BLUE=''; NC=''; BOLD=''
fi

log()  { printf "${GREEN}✓${NC} %s\n" "$1" >&2; }
warn() { printf "${YELLOW}⚠${NC} %s\n" "$1" >&2; }
err()  { printf "${RED}✗${NC} %s\n" "$1" >&2; }
info() { printf "${BLUE}→${NC} %s\n" "$1" >&2; }

export PATH="$HOME/.local/bin:$PATH"

# Portable timeout: use coreutils timeout/gtimeout if available, otherwise perl
run_timeout() {
  local secs="$1"; shift
  if command -v timeout >/dev/null 2>&1; then
    timeout "$secs" "$@"
  elif command -v gtimeout >/dev/null 2>&1; then
    gtimeout "$secs" "$@"
  else
    # Perl-based fallback (available on macOS and most Linux)
    perl -e 'alarm shift; exec @ARGV' "$secs" "$@"
  fi
}

# Parse flags
FIX_SSH=0
REPO=""
for arg in "$@"; do
  case "$arg" in
    --fix-ssh) FIX_SSH=1 ;;
    --help|-h)
      cat >&2 <<'USAGE'
Usage: setup.sh [OPTIONS] [/path/to/repo]

Options:
  --fix-ssh     Also fix SSH key/config permissions
  --help, -h    Show this help
  --version     Show version

Environment:
  TRUFFLEHOG_VERSION   Pin trufflehog version (default: 3.88.0, must be semver)
USAGE
      exit 0
      ;;
    --version)
      echo "agent-security-ops setup.sh v${SCRIPT_VERSION}" >&2
      exit 0
      ;;
    *) REPO="$arg" ;;
  esac
done

REPO="${REPO:-.}"
REPO="$(cd "$REPO" && pwd)"

if [ ! -d "$REPO/.git" ]; then
  err "Not a git repository: $REPO"
  exit 1
fi

printf "${BOLD}agent-security-ops: Setting up %s${NC}\n" "$REPO" >&2
echo "" >&2
ACTIONS=()

# 1. Install TruffleHog
TRUFFLEHOG_VERSION="${TRUFFLEHOG_VERSION:-3.88.0}"

# [M4] Validate semver
if ! echo "$TRUFFLEHOG_VERSION" | grep -qE '^[0-9]+\.[0-9]+\.[0-9]+(-[A-Za-z0-9.]+)?$'; then
  err "Invalid TRUFFLEHOG_VERSION '$TRUFFLEHOG_VERSION' — must be semver (e.g. 3.88.0)"
  exit 1
fi

export PATH="$HOME/.local/bin:$PATH"
if command -v trufflehog >/dev/null 2>&1; then
  log "TruffleHog already installed ($(trufflehog --version 2>&1 || echo 'unknown'))"
else
  info "Installing TruffleHog v${TRUFFLEHOG_VERSION}..."
  ARCH="$(uname -m)"
  case "$ARCH" in
    x86_64) ARCH="amd64" ;;
    aarch64|arm64) ARCH="arm64" ;;
  esac
  OS="$(uname -s | tr '[:upper:]' '[:lower:]')"
  VERSION="$TRUFFLEHOG_VERSION"
  TMP="$(mktemp -d)"
  TARBALL="trufflehog_${VERSION}_${OS}_${ARCH}.tar.gz"
  URL="https://github.com/trufflesecurity/trufflehog/releases/download/v${VERSION}/${TARBALL}"
  CHECKSUMS_URL="https://github.com/trufflesecurity/trufflehog/releases/download/v${VERSION}/trufflehog_${VERSION}_checksums.txt"

  info "Downloading $URL"
  if ! curl -sfL "$URL" -o "$TMP/$TARBALL"; then
    rm -rf "$TMP"
    err "Failed to download TruffleHog tarball"
    exit 1
  fi

  # [C1] Checksum verification
  info "Verifying SHA256 checksum..."
  if ! curl -sfL "$CHECKSUMS_URL" -o "$TMP/checksums.txt"; then
    rm -rf "$TMP"
    err "Failed to download checksums file"
    exit 1
  fi

  EXPECTED_HASH=$(grep "$TARBALL" "$TMP/checksums.txt" | awk '{print $1}')
  if [ -z "$EXPECTED_HASH" ]; then
    rm -rf "$TMP"
    err "Tarball not found in checksums file"
    exit 1
  fi

  if command -v sha256sum >/dev/null 2>&1; then
    ACTUAL_HASH=$(sha256sum "$TMP/$TARBALL" | awk '{print $1}')
  else
    ACTUAL_HASH=$(shasum -a 256 "$TMP/$TARBALL" | awk '{print $1}')
  fi

  if [ "$EXPECTED_HASH" != "$ACTUAL_HASH" ]; then
    rm -rf "$TMP"
    err "Checksum mismatch! Expected: $EXPECTED_HASH Got: $ACTUAL_HASH"
    exit 1
  fi
  log "Checksum verified"

  if tar xzf "$TMP/$TARBALL" -C "$TMP" 2>/dev/null; then
    INSTALL_DIR="$HOME/.local/bin"
    mkdir -p "$INSTALL_DIR"
    mv "$TMP/trufflehog" "$INSTALL_DIR/trufflehog"
    chmod +x "$INSTALL_DIR/trufflehog"
    rm -rf "$TMP"
    export PATH="$INSTALL_DIR:$PATH"
  else
    rm -rf "$TMP"
    # [H5] Removed brew fallback — prefer verified direct download only
    err "Failed to extract TruffleHog. Install manually: https://github.com/trufflesecurity/trufflehog"
    exit 1
  fi

  if command -v trufflehog >/dev/null 2>&1; then
    log "TruffleHog installed ($(trufflehog --version 2>&1 || echo 'unknown'))"
    ACTIONS+=("Installed TruffleHog")
  else
    err "Failed to install TruffleHog"
    exit 1
  fi
fi

# 2. Create pre-commit hook (scans staged changes only)
# [C2] Fail-closed: block commit if trufflehog not found
# [B1] Use temp file instead of pipe to avoid PIPESTATUS issues
# [H2] Consistent flags: scan all secrets, highlight verified
HOOK="$REPO/.git/hooks/pre-commit"
HOOK_MARKER='# MARKER:agent-security-ops'
HOOK_CONTENT='#!/usr/bin/env bash
# agent-security-ops pre-commit hook: scan for secrets
# MARKER:agent-security-ops
set -euo pipefail

# [C2] Fail-closed: if trufflehog is missing, block the commit.
# Use "git commit --no-verify" to bypass in emergencies (NOT recommended — see SKILL.md).
if ! command -v trufflehog >/dev/null 2>&1; then
  echo "✗ trufflehog not found — commit blocked (fail-closed). Install it or use git commit --no-verify." >&2
  exit 1
fi

echo "🔍 Scanning for secrets..." >&2

# [B1] Capture to temp file to avoid PIPESTATUS issues with pipes
SCAN_TMP=$(mktemp)
trap "rm -f \"$SCAN_TMP\"" EXIT

exit_code=0
trufflehog git file://. --since-commit HEAD --fail --no-update --json 2>/dev/null > "$SCAN_TMP" || exit_code=$?

if [ "$exit_code" -ne 0 ] && [ -s "$SCAN_TMP" ]; then
  echo "✗ Secrets detected! Commit blocked." >&2
  # Show first few findings
  head -5 "$SCAN_TMP" >&2
  echo "" >&2
  echo "To bypass in emergencies: git commit --no-verify" >&2
  echo "⚠ WARNING: bypassing means secrets may be committed. Rotate immediately if this happens." >&2
  exit 1
fi
echo "✓ No secrets found." >&2'

if [ -f "$HOOK" ] && grep -q "$HOOK_MARKER" "$HOOK" 2>/dev/null; then
  if grep -q '# --- agent-security-ops appended hook ---' "$HOOK" 2>/dev/null; then
    # Appended mode — replace only our section
    HOOK_TMP=$(mktemp)
    sed '/# --- agent-security-ops appended hook ---/,$d' "$HOOK" > "$HOOK_TMP"
    printf '\n# --- agent-security-ops appended hook ---\n' >> "$HOOK_TMP"
    printf '%s\n' "$HOOK_CONTENT" | tail -n +2 >> "$HOOK_TMP"
    mv "$HOOK_TMP" "$HOOK"
    chmod +x "$HOOK"
    log "Pre-commit hook updated (preserved existing hook)"
    ACTIONS+=("Updated pre-commit hook (appended section)")
  else
    # Exclusively our hook — safe to overwrite
    printf '%s\n' "$HOOK_CONTENT" > "$HOOK"
    chmod +x "$HOOK"
    log "Pre-commit hook updated"
    ACTIONS+=("Updated pre-commit hook")
  fi
elif [ -f "$HOOK" ]; then
  # [POLISH] Existing non-ours hook — append instead of overwriting
  warn "Existing pre-commit hook found — appending agent-security-ops block"
  cp "$HOOK" "${HOOK}.bak"
  printf '\n\n%s\n' "# --- agent-security-ops appended hook ---" >> "$HOOK"
  # Write the scanning portion (skip the shebang)
  printf '%s\n' "$HOOK_CONTENT" | tail -n +2 >> "$HOOK"
  chmod +x "$HOOK"
  log "Pre-commit hook appended (original backed up to ${HOOK}.bak)"
  ACTIONS+=("Appended pre-commit hook (preserved existing)")
else
  printf '%s\n' "$HOOK_CONTENT" > "$HOOK"
  chmod +x "$HOOK"
  log "Pre-commit hook installed"
  ACTIONS+=("Installed pre-commit hook")
fi

# 3. Harden .gitignore
GITIGNORE="$REPO/.gitignore"
PATTERNS=(
  '.env*'
  '*.pem'
  '*.key'
  'id_rsa*'
  '*.p12'
  '*.pfx'
  'credentials.json'
  'token.json'
  'service-account*.json'
  '*.keystore'
  '.security-ops/'
  '.terraform/'
)
# Test filenames that should be caught by the corresponding gitignore pattern
TEST_FILES=(
  '.env'
  'test.pem'
  'test.key'
  'id_rsa'
  'test.p12'
  'test.pfx'
  'credentials.json'
  'token.json'
  'service-account-test.json'
  'test.keystore'
  '.security-ops/'
  '.terraform/'
)

touch "$GITIGNORE"
ADDED=()
idx=0
for pattern in "${PATTERNS[@]}"; do
  # [M6] Use git check-ignore with realistic test filenames
  if ! git -C "$REPO" check-ignore -q "${TEST_FILES[$idx]}" 2>/dev/null; then
    ADDED+=("$pattern")
  fi
  idx=$((idx + 1))
done

if [ ${#ADDED[@]} -gt 0 ]; then
  printf '\n# agent-security-ops: secret patterns\n' >> "$GITIGNORE"
  for p in "${ADDED[@]}"; do
    echo "$p" >> "$GITIGNORE"
  done
  log "Added ${#ADDED[@]} patterns to .gitignore: ${ADDED[*]}"
  ACTIONS+=("Hardened .gitignore (+${#ADDED[@]} patterns)")
else
  log ".gitignore already covers all secret patterns"
fi

# 4. SSH Permission Fixing (opt-in only with --fix-ssh)
if [ "$FIX_SSH" -eq 1 ] && [ -d "$HOME/.ssh" ]; then
  info "Fixing SSH permissions (--fix-ssh)..."
  ssh_fixed=0
  ssh_dir_perms=$(stat -f '%Lp' "$HOME/.ssh" 2>/dev/null || stat -c '%a' "$HOME/.ssh" 2>/dev/null || true)
  if [ -n "$ssh_dir_perms" ] && [ "$ssh_dir_perms" != "700" ]; then
    chmod 700 "$HOME/.ssh"
    log "Fixed ~/.ssh permissions ($ssh_dir_perms → 700)"
    ssh_fixed=$((ssh_fixed + 1))
  fi
  for keyfile in "$HOME/.ssh"/id_*; do
    [ -f "$keyfile" ] || continue
    case "$keyfile" in *.pub) continue ;; esac
    key_perms=$(stat -f '%Lp' "$keyfile" 2>/dev/null || stat -c '%a' "$keyfile" 2>/dev/null || true)
    if [ -n "$key_perms" ] && [ "$key_perms" != "600" ]; then
      chmod 600 "$keyfile"
      log "Fixed $keyfile permissions ($key_perms → 600)"
      ssh_fixed=$((ssh_fixed + 1))
    fi
  done
  if [ -f "$HOME/.ssh/config" ]; then
    cfg_perms=$(stat -f '%Lp' "$HOME/.ssh/config" 2>/dev/null || stat -c '%a' "$HOME/.ssh/config" 2>/dev/null || true)
    if [ -n "$cfg_perms" ] && [ "$cfg_perms" != "600" ] && [ "$cfg_perms" != "644" ]; then
      chmod 600 "$HOME/.ssh/config"
      log "Fixed ~/.ssh/config permissions ($cfg_perms → 600)"
      ssh_fixed=$((ssh_fixed + 1))
    fi
  fi
  if [ "$ssh_fixed" -eq 0 ]; then
    log "SSH permissions already correct"
  else
    ACTIONS+=("Fixed $ssh_fixed SSH permission(s)")
  fi
fi

# 5. Initial TruffleHog scan
# [C3] Scan ALL secrets, not just verified
info "Running initial secret scan..."
SCAN_OUTPUT=$(run_timeout 300 trufflehog git "file://$REPO" --no-update --json 2>/dev/null) || true
FINDING_COUNT=$(echo "$SCAN_OUTPUT" | grep -c '"SourceMetadata"' 2>/dev/null || true)
FINDING_COUNT="${FINDING_COUNT:-0}"
FINDING_COUNT=$(echo "$FINDING_COUNT" | tr -d '[:space:]')
VERIFIED_COUNT=0
if [ "$FINDING_COUNT" -gt 0 ]; then
  VERIFIED_COUNT=$(echo "$SCAN_OUTPUT" | grep -c '"Verified":true' 2>/dev/null || true)
  VERIFIED_COUNT=$(echo "$VERIFIED_COUNT" | tr -d '[:space:]')
  warn "Found $FINDING_COUNT secret(s) ($VERIFIED_COUNT verified) in repo!"
  ACTIONS+=("Initial scan: $FINDING_COUNT secret(s), $VERIFIED_COUNT verified")
else
  log "Initial scan: clean"
  ACTIONS+=("Initial scan: clean")
fi

# [M5] Also run filesystem scan to catch untracked files
info "Running filesystem scan (untracked files)..."
FS_OUTPUT=$(run_timeout 120 trufflehog filesystem "$REPO" --no-update --json 2>/dev/null) || true
FS_COUNT=$(echo "$FS_OUTPUT" | grep -c '"SourceMetadata"' 2>/dev/null || true)
FS_COUNT=$(echo "$FS_COUNT" | tr -d '[:space:]')
if [ "${FS_COUNT:-0}" -gt 0 ]; then
  warn "Filesystem scan found $FS_COUNT secret(s) in untracked/working files"
  ACTIONS+=("Filesystem scan: $FS_COUNT finding(s)")
else
  log "Filesystem scan: clean"
fi

# 6. Summary
echo "" >&2
printf "${BOLD}Setup complete:${NC}\n" >&2
for action in "${ACTIONS[@]}"; do
  printf "  • %s\n" "$action" >&2
done
printf "  💡 More agent-ops at theagentwire.ai\n" >&2
echo "" >&2
