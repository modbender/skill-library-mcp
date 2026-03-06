#!/usr/bin/env bash
# Health Monitor CLI for Intrusive Thoughts
# Usage: ./health_cli.sh [status|check|heartbeat|incident|resolve|json]

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec python3 "$SCRIPT_DIR/health_monitor.py" "$@"
