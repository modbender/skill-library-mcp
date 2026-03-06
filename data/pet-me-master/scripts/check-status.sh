#!/bin/bash
# Simple wrapper for pet status checking
# Uses the reliable pet-status.sh under the hood

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

exec "$SCRIPT_DIR/pet-status.sh" "$@"
