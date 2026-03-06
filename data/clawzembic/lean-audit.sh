#!/usr/bin/env bash
# Clawzembic — Weight Loss for Your OpenClaw Instance
# Usage: bash lean-audit.sh [--remote user@host] [--json] [--fix]
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REMOTE=""
JSON_MODE=false
FIX_MODE=false
OPENCLAW_DIR="${OPENCLAW_DIR:-$HOME/.openclaw}"

while [[ $# -gt 0 ]]; do
  case $1 in
    --remote) REMOTE="$2"; shift 2 ;;
    --json)   JSON_MODE=true; shift ;;
    --fix)    FIX_MODE=true; shift ;;
    --dir)    OPENCLAW_DIR="$2"; shift 2 ;;
    -h|--help) echo "Usage: lean-audit.sh [--remote user@host] [--json] [--fix] [--dir /path/to/.openclaw]"; exit 0 ;;
    *) echo "Unknown option: $1"; exit 1 ;;
  esac
done

# If remote, SSH the whole script over
if [[ -n "$REMOTE" ]]; then
  exec ssh "$REMOTE" "export PATH=/opt/homebrew/bin:/opt/homebrew/lib/node_modules/.bin:/usr/local/bin:\$PATH && bash -s" < "$SCRIPT_DIR/lean-audit.sh" -- $([ "$JSON_MODE" = true ] && echo "--json") $([ "$FIX_MODE" = true ] && echo "--fix")
fi

# Collect all data, then pass to Python for scoring + display
python3 "$SCRIPT_DIR/lean-report.py" \
  --openclaw-dir "$OPENCLAW_DIR" \
  $([ "$JSON_MODE" = true ] && echo "--json" || true) \
  $([ "$FIX_MODE" = true ] && echo "--fix" || true)
