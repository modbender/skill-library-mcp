#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
EXAMPLES_DIR="$ROOT_DIR/examples"
WORKSPACE_DIR="$EXAMPLES_DIR/workspace"

for bin in bash jq python3; do
  command -v "$bin" >/dev/null 2>&1 || {
    echo "missing dependency: $bin" >&2
    exit 2
  }
done

mkdir -p "$WORKSPACE_DIR/sessions" "$WORKSPACE_DIR/cron/runs" "$WORKSPACE_DIR/metrics"
mkdir -p "$EXAMPLES_DIR"

if [[ ! -f "$WORKSPACE_DIR/sessions/sessions.json" ]]; then
  cat > "$WORKSPACE_DIR/sessions/sessions.json" <<'JSON'
{
  "agent:main:demo": {
    "sessionId": "demo-session-1",
    "contextTokens": 200000,
    "totalTokens": 12000
  }
}
JSON
fi

if [[ ! -f "$WORKSPACE_DIR/sessions/demo-session-1.jsonl" ]]; then
  echo '{"type":"session","id":"demo-session-1"}' > "$WORKSPACE_DIR/sessions/demo-session-1.jsonl"
fi

if [[ ! -f "$WORKSPACE_DIR/metrics/daily-snapshots.jsonl" ]]; then
  cat > "$WORKSPACE_DIR/metrics/daily-snapshots.jsonl" <<'JSONL'
{"totalTokensUsed": 10000}
{"totalTokensUsed": 12000}
JSONL
fi

if [[ ! -f "$EXAMPLES_DIR/incident-state.json" ]]; then
  echo '{}' > "$EXAMPLES_DIR/incident-state.json"
fi

chmod +x "$ROOT_DIR/scripts"/*.sh

echo "setup_complete root=$ROOT_DIR"
echo "example_workspace=$WORKSPACE_DIR"
echo "example_state=$EXAMPLES_DIR/incident-state.json"
