#!/bin/bash
# Generic Alexa command wrapper
# Usage: ./alexa-cmd.sh "Your voice command" ["Device Name"]
#
# Examples:
#   ./alexa-cmd.sh "Set an alarm for 6:30 am"
#   ./alexa-cmd.sh "Play BBC Radio 6" "Kitchen Echo"
#   ./alexa-cmd.sh "Turn off the lights" "Living Room Echo"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ALEXA_DIR="${ALEXA_REMOTE_DIR:-$SCRIPT_DIR/../../alexa-remote-control}"

COMMAND="${1:?Usage: $0 \"command\" [\"Device Name\"]}"
DEVICE="${2:-Bedroom Echo Show}"

# Set these environment variables or edit here
export REFRESH_TOKEN="${REFRESH_TOKEN:?Set REFRESH_TOKEN env var}"
export AMAZON="${AMAZON:-amazon.co.uk}"
export ALEXA="${ALEXA:-alexa.amazon.co.uk}"

"$ALEXA_DIR/alexa_remote_control.sh" -d "$DEVICE" -e "textcommand:$COMMAND"
