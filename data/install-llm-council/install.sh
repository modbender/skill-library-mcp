#!/usr/bin/env bash
set -euo pipefail

MODE="auto"
TARGET_DIR="${HOME}/workspace/llm-council"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --mode)
      MODE="${2:-auto}"; shift 2 ;;
    --dir)
      TARGET_DIR="${2:-$TARGET_DIR}"; shift 2 ;;
    *)
      echo "Unknown arg: $1"
      echo "Usage: $0 [--mode auto|preview|dev] [--dir PATH]"
      exit 1 ;;
  esac
done

mkdir -p "$(dirname "$TARGET_DIR")"

if [[ -d "$TARGET_DIR/.git" ]]; then
  echo "- Updating existing repo: $TARGET_DIR"
  git -C "$TARGET_DIR" pull --ff-only
else
  echo "- Cloning repo to: $TARGET_DIR"
  git clone https://github.com/jeadland/llm-council.git "$TARGET_DIR"
fi

cd "$TARGET_DIR"

# Persist chat history outside the app folder so reinstalls/updates don't wipe it.
STATE_ROOT="${OPENCLAW_STATE_DIR:-$HOME/.openclaw}"
PERSIST_DIR="$STATE_ROOT/apps-data/llm-council"
mkdir -p "$PERSIST_DIR"

if [[ -d "$TARGET_DIR/data" && ! -L "$TARGET_DIR/data" ]]; then
  # Merge any existing local data into persistent location first.
  mkdir -p "$PERSIST_DIR/data"
  cp -a "$TARGET_DIR/data/." "$PERSIST_DIR/data/" 2>/dev/null || true
  rm -rf "$TARGET_DIR/data"
fi

if [[ ! -e "$TARGET_DIR/data" ]]; then
  ln -s "$PERSIST_DIR/data" "$TARGET_DIR/data"
fi

echo "- Persistent data path: $PERSIST_DIR/data"

echo "- Installing backend dependencies (uv sync)"
uv sync

echo "- Installing frontend dependencies (npm ci)"
( cd frontend && npm ci )

# Credentials: prefer OpenClaw gateway if available; else keep OPENROUTER_API_KEY if present.
API_MODE="gateway"
if curl -sf --max-time 2 -X POST http://127.0.0.1:18789/v1/chat/completions -o /dev/null 2>/dev/null; then
  API_MODE="gateway"
else
  API_MODE="openrouter"
fi

echo "- Starting LLM Council in background (mode: $MODE, api: $API_MODE)"
nohup "$TARGET_DIR/start.sh" --mode "$MODE" >"$TARGET_DIR/.llm-council.log" 2>&1 &
echo $! > "$TARGET_DIR/.llm-council.pid"

sleep 2

HOST_IP=$(hostname -I 2>/dev/null | awk '{print $1}')
[[ -z "${HOST_IP:-}" ]] && HOST_IP="127.0.0.1"

echo ""
echo "✅ LLM Council installed and started"
echo ""
echo "  Mode:     $MODE"
echo "  API:      $API_MODE"
echo "  Dir:      $TARGET_DIR"
echo "  Log:      $TARGET_DIR/.llm-council.log"
echo ""
echo "  Try URLs:"
echo "    - http://$HOST_IP:5173   (Caddy route, if configured)"
echo "    - http://$HOST_IP:4173   (preview default)"
echo "    - http://$HOST_IP:5174   (common dev fallback)"
echo ""
echo "  Stop:     bash $(dirname "$0")/stop.sh --dir "$TARGET_DIR""
echo "  Status:   bash $(dirname "$0")/status.sh --dir "$TARGET_DIR""
