#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
WATCHDOG_SCRIPT="$BASE_DIR/scripts/gateway-watchdog.sh"
TEMPLATE="$BASE_DIR/references/com.openclaw.gateway-watchdog.plist.template"

LAUNCHD_LABEL="${GW_WATCHDOG_LABEL:-com.openclaw.gateway-watchdog}"
LAUNCHD_DIR="$HOME/Library/LaunchAgents"
LAUNCHD_PLIST="$LAUNCHD_DIR/${LAUNCHD_LABEL}.plist"
INTERVAL="${GW_WATCHDOG_INTERVAL_SECONDS:-30}"
LOAD_AFTER_INSTALL=0

usage() {
  cat <<EOF
Usage: $(basename "$0") [--interval <seconds>] [--load]

Options:
  --interval <seconds>  LaunchAgent interval (default: 30)
  --load                Load/reload the LaunchAgent after install
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --interval)
      INTERVAL="${2:-30}"
      (( $# >= 2 )) && shift 2 || shift
      ;;
    --load)
      LOAD_AFTER_INSTALL=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "unknown option: $1" >&2
      usage
      exit 1
      ;;
  esac
done

mkdir -p "$LAUNCHD_DIR"

if [[ ! -f "$TEMPLATE" ]]; then
  echo "template missing: $TEMPLATE" >&2
  exit 1
fi

if [[ ! -x "$WATCHDOG_SCRIPT" ]]; then
  chmod +x "$WATCHDOG_SCRIPT"
fi

sed \
  -e "s#__WATCHDOG_LABEL__#$LAUNCHD_LABEL#g" \
  -e "s#__WATCHDOG_SCRIPT__#$WATCHDOG_SCRIPT#g" \
  -e "s#__WATCHDOG_INTERVAL__#$INTERVAL#g" \
  "$TEMPLATE" > "$LAUNCHD_PLIST"

echo "installed: $LAUNCHD_PLIST"
echo "interval: ${INTERVAL}s"

if [[ "$LOAD_AFTER_INSTALL" -eq 1 ]]; then
  launchctl bootout "gui/$UID/$LAUNCHD_LABEL" >/dev/null 2>&1 || true
  launchctl bootstrap "gui/$UID" "$LAUNCHD_PLIST"
  launchctl kickstart -k "gui/$UID/$LAUNCHD_LABEL"
  echo "launchd loaded: $LAUNCHD_LABEL"
else
  echo "launchd not loaded. run:"
  echo "  launchctl bootstrap gui/$UID \"$LAUNCHD_PLIST\""
  echo "  launchctl kickstart -k gui/$UID/$LAUNCHD_LABEL"
fi
