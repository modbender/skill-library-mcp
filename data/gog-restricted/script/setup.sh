#!/bin/bash
set -euo pipefail

GOG_BIN="$(command -v gog 2>/dev/null || true)"
if [[ -z "$GOG_BIN" ]]; then
  echo "Error: gog binary not found in PATH" >&2
  exit 1
fi
GOG_DIR="$(dirname "$GOG_BIN")"
GOG_REAL="${GOG_DIR}/.gog-real"

# --- Idempotency guard ---
if [[ -f "$GOG_REAL" ]]; then
  echo "Note: $GOG_REAL already exists, skipping move."
else
  # Refuse to move if gog is already a shell script (i.e., already a wrapper)
  if file "$GOG_BIN" | grep -q "shell script\|text"; then
    echo "Error: $GOG_BIN appears to be a shell script, not the original binary." >&2
    echo "If the wrapper is already installed, $GOG_REAL should exist." >&2
    exit 1
  fi
  sudo mv "$GOG_BIN" "$GOG_REAL"
fi

# --- Install wrapper ---
# Write shebang and GOG_REAL with expansion, then append the rest quoted.
printf '#!/bin/bash\nset -euo pipefail\n\nGOG_REAL="%s"\n' "$GOG_REAL" | sudo tee "$GOG_BIN" > /dev/null

sudo tee -a "$GOG_BIN" > /dev/null << 'WRAPPER'
ORIG_ARGS=("$@")

# ---------------------------------------------------------------------------
# Parse positional args only — flags and their values are discarded so they
# can never influence subcommand matching.
#
# Conservative flag handling: every --flag is assumed to consume the next
# argument as its value. This can only make the wrapper MORE restrictive
# (by accidentally eating a positional), never less.
# ---------------------------------------------------------------------------
POSITIONAL=()
HAS_HELP=false
HAS_VERSION=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --help|-h)
      HAS_HELP=true
      shift
      ;;
    --version)
      HAS_VERSION=true
      shift
      ;;
    --*)
      shift
      [[ $# -gt 0 ]] && shift
      ;;
    -*)
      shift
      ;;
    *)
      POSITIONAL+=("$1")
      shift
      ;;
  esac
done

NPOS=${#POSITIONAL[@]}
P0="${POSITIONAL[0]:-}"
P1="${POSITIONAL[1]:-}"
P2="${POSITIONAL[2]:-}"

ALLOWED=false

# --- Try 3-word subcommand match ---
if [[ $NPOS -ge 3 ]]; then
  case "$P0 $P1 $P2" in
    "gmail messages search"|\
    "gmail labels list"|\
    "gmail labels create"|\
    "gmail labels add"|\
    "gmail labels remove"|\
    "gmail thread modify"|\
    "gmail thread attachments"|\
    "gmail batch modify")
      ALLOWED=true ;;
  esac
fi

# --- Try 2-word subcommand match ---
if [[ "$ALLOWED" == false && $NPOS -ge 2 ]]; then
  case "$P0 $P1" in
    "auth status"|\
    "auth list"|\
    "auth services"|\
    "gmail search"|\
    "gmail read"|\
    "gmail get"|\
    "gmail attachment"|\
    "gmail url"|\
    "gmail history"|\
    "gmail thread"|\
    "gmail labels"|\
    "calendar create"|\
    "calendar list"|\
    "calendar get"|\
    "calendar events"|\
    "calendar event"|\
    "calendar calendars"|\
    "calendar search"|\
    "calendar freebusy"|\
    "calendar conflicts"|\
    "calendar colors"|\
    "calendar time"|\
    "calendar acl"|\
    "calendar users"|\
    "calendar team")
      ALLOWED=true ;;
  esac
fi

# --- Handle --help for known group prefixes (exact positional count) ---
# Prevents "gog gmail send --help" from slipping through.
if [[ "$ALLOWED" == false && "$HAS_HELP" == true ]]; then
  case "$NPOS" in
    0) ALLOWED=true ;;
    1) case "$P0" in
         gmail|auth|calendar) ALLOWED=true ;;
       esac ;;
    2) case "$P0 $P1" in
         "gmail messages"|"gmail labels"|"gmail batch"|"gmail thread") ALLOWED=true ;;
       esac ;;
  esac
fi

# --- Handle --version (top-level only) ---
if [[ "$ALLOWED" == false && "$HAS_VERSION" == true && $NPOS -eq 0 ]]; then
  ALLOWED=true
fi

# --- Command-specific flag restrictions ---
# calendar create is allowed but attendee/invite flags are blocked to prevent
# egress (Google sends invitation emails to attendees).
if [[ "$ALLOWED" == true && "$P0" == "calendar" && "$P1" == "create" ]]; then
  for arg in "${ORIG_ARGS[@]}"; do
    case "$arg" in
      --attendees|--attendees=*|\
      --send-updates|--send-updates=*|\
      --with-meet|\
      --guests-can-invite|\
      --guests-can-modify|\
      --guests-can-see-others)
        echo "BLOCKED: $arg is not allowed with calendar create." >&2
        exit 1
        ;;
    esac
  done
fi

if [[ "$ALLOWED" == true ]]; then
  exec "$GOG_REAL" "${ORIG_ARGS[@]}"
fi

echo "BLOCKED: this command is not in the allowlist." >&2
exit 1
WRAPPER

sudo chmod +x "$GOG_BIN"
echo "Security wrapper installed at $GOG_BIN"
echo "Original binary preserved at $GOG_REAL"
