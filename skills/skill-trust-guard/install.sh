#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
HOOK_SCRIPT="$SCRIPT_DIR/hooks/pre-install.sh"

RED="\033[31m"; GREEN="\033[32m"; YELLOW="\033[33m"; BLUE="\033[34m"; BOLD="\033[1m"; RESET="\033[0m"
log(){ echo -e "${BLUE}${BOLD}[*]${RESET} $*"; }
warn(){ echo -e "${YELLOW}${BOLD}[!]${RESET} $*"; }
err(){ echo -e "${RED}${BOLD}[x]${RESET} $*"; }
ok(){ echo -e "${GREEN}${BOLD}[✓]${RESET} $*"; }

usage() {
  cat <<'EOF'
Usage: install.sh [global opts] [--yes] <slug|path|git-url> [install opts]

Security wrapper for `clawhub install`.

Policy:
  score < 50     -> block
  50 <= score <75 -> warn + ask (or auto-approve with --yes)
  score >= 75    -> allow
EOF
}

command -v clawhub >/dev/null 2>&1 || { err "clawhub not found"; exit 1; }
command -v node >/dev/null 2>&1 || { err "node not found"; exit 1; }
command -v npx >/dev/null 2>&1 || { err "npx not found"; exit 1; }
[[ -x "$HOOK_SCRIPT" ]] || { err "hook script missing: $HOOK_SCRIPT"; exit 1; }

YES=0
GLOBAL_OPTS=()
INSTALL_OPTS=()
TARGET=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    -h|--help) usage; exit 0 ;;
    -y|--yes) YES=1; shift ;;
    --dir|--workdir|--registry|--site)
      [[ $# -lt 2 ]] && { err "Missing value for $1"; exit 1; }
      GLOBAL_OPTS+=("$1" "$2"); shift 2 ;;
    --no-input)
      GLOBAL_OPTS+=("$1"); shift ;;
    --version|--tag)
      [[ $# -lt 2 ]] && { err "Missing value for $1"; exit 1; }
      INSTALL_OPTS+=("$1" "$2"); shift 2 ;;
    --force)
      INSTALL_OPTS+=("$1"); shift ;;
    --*)
      INSTALL_OPTS+=("$1"); shift ;;
    *)
      if [[ -z "$TARGET" ]]; then TARGET="$1"; else INSTALL_OPTS+=("$1"); fi
      shift ;;
  esac
done

[[ -n "$TARGET" ]] || { err "Missing skill slug/path/git-url"; usage; exit 1; }

TMPDIR=$(mktemp -d -t skill-trust-guard-XXXXXX)
trap 'rm -rf "$TMPDIR"' EXIT

ORIGIN="clawhub"
SCAN_PATH=""
INSTALL_NAME="$TARGET"

if [[ -d "$TARGET" ]]; then
  ORIGIN="local"
  SCAN_PATH="$(cd "$TARGET" && pwd)"
  INSTALL_NAME="$(basename "$SCAN_PATH")"
elif [[ "$TARGET" =~ ^https?:// || "$TARGET" =~ \.git$ ]]; then
  ORIGIN="git"
  INSTALL_NAME="$(basename "${TARGET%.git}")"
  command -v git >/dev/null 2>&1 || { err "git not found for git source"; exit 1; }
  log "Cloning git source for scan..."
  git clone --depth=1 "$TARGET" "$TMPDIR/source" >/tmp/skill-trust-guard.git.log 2>&1 || {
    err "Git clone failed. See /tmp/skill-trust-guard.git.log"; exit 1; }
  SCAN_PATH="$TMPDIR/source"
fi

if [[ "$ORIGIN" == "clawhub" ]]; then
  log "Fetching skill for scan: $TARGET"
  if ! clawhub "${GLOBAL_OPTS[@]}" --dir "$TMPDIR" install "$TARGET" "${INSTALL_OPTS[@]}" --force >/tmp/skill-trust-guard.install.log 2>&1; then
    err "Failed to fetch from clawhub. See /tmp/skill-trust-guard.install.log"
    exit 1
  fi
  SCAN_PATH="$TMPDIR/$TARGET"
fi

[[ -d "$SCAN_PATH" ]] || { err "Scan path not found: $SCAN_PATH"; exit 1; }

log "Running pre-install security scan..."
set +e
HOOK_OUTPUT=$("$HOOK_SCRIPT" "$SCAN_PATH")
HOOK_RC=$?
set -e

echo "$HOOK_OUTPUT" | sed 's/^/    /'
SCORE=$(awk -F= '/^SCORE=/{print $2}' <<<"$HOOK_OUTPUT")
DECISION=$(awk -F= '/^DECISION=/{print $2}' <<<"$HOOK_OUTPUT")
SUMMARY=$(awk -F= '/^SUMMARY=/{sub(/^SUMMARY=/,""); print}' <<<"$HOOK_OUTPUT")

if [[ $HOOK_RC -eq 30 ]]; then
  err "Scan failed or output parse failed"
  exit 1
fi

log "Scan summary: ${SUMMARY:-n/a}, score=${SCORE:-n/a}"

if [[ "$DECISION" == "reject" || $HOOK_RC -eq 20 ]]; then
  err "Score < 50, installation blocked"
  echo "----- Scanner JSON report -----"
  "$HOOK_SCRIPT" --json "$SCAN_PATH" || true
  exit 1
fi

if [[ "$DECISION" == "warn" || $HOOK_RC -eq 10 ]]; then
  warn "Score in warning range (50-74)"
  if [[ $YES -eq 0 ]]; then
    read -r -p "Proceed with installation? [y/N]: " ans
    case "$ans" in
      [yY]|[yY][eE][sS]) ;;
      *) err "Installation aborted by user"; exit 1 ;;
    esac
  else
    warn "Auto-approved due to --yes"
  fi
else
  ok "Score >= 75, proceeding"
fi

if [[ "$ORIGIN" == "clawhub" ]]; then
  log "Installing from clawhub..."
  clawhub "${GLOBAL_OPTS[@]}" install "$TARGET" "${INSTALL_OPTS[@]}"
else
  TARGET_DIR="$HOME/.openclaw/skills"
  for ((i=0; i<${#GLOBAL_OPTS[@]}; i++)); do
    if [[ "${GLOBAL_OPTS[$i]}" == "--dir" ]]; then TARGET_DIR="${GLOBAL_OPTS[$((i+1))]}"; fi
  done
  mkdir -p "$TARGET_DIR"
  rm -rf "$TARGET_DIR/$INSTALL_NAME"
  cp -R "$SCAN_PATH" "$TARGET_DIR/$INSTALL_NAME"
  ok "Copied skill to $TARGET_DIR/$INSTALL_NAME"
fi

ok "Done: $TARGET"
