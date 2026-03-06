#!/usr/bin/env bash
# install.sh — One-shot installer & launcher for LLM Council
# Usage: install.sh [--mode dev|preview] [--dir PATH]
# OpenClaw-native: reads credentials from OpenClaw config — no API key prompt.

set -euo pipefail

# ── Defaults ──────────────────────────────────────────────────────────────────
MODE="dev"
INSTALL_DIR="${HOME}/workspace/llm-council"
SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PID_FILE="${SKILL_DIR}/pids"
WORKSPACE_ENV="${HOME}/.openclaw/workspace/.env"
OPENCLAW_CONFIG="${HOME}/.openclaw/openclaw.json"

# ── Arg parsing ───────────────────────────────────────────────────────────────
while [[ $# -gt 0 ]]; do
  case "$1" in
    --mode) MODE="$2"; shift 2 ;;
    --dir) INSTALL_DIR="$2"; shift 2 ;;
    *) echo "Unknown flag: $1" >&2; exit 1 ;;
  esac
done

# ── Colors ────────────────────────────────────────────────────────────────────
GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; NC='\033[0m'
info()  { echo -e "${GREEN}[council-brief]${NC} $*"; }
warn()  { echo -e "${YELLOW}[council-brief]${NC} $*"; }
error() { echo -e "${RED}[council-brief] ERROR:${NC} $*" >&2; exit 1; }

# ── Resolve credentials — OpenClaw-native (no interactive prompt) ─────────────
#
# Priority order:
#   1. Environment: OPENROUTER_API_KEY (already exported)
#   2. Workspace .env: ~/.openclaw/workspace/.env
#   3. OpenClaw local gateway: ~/.openclaw/openclaw.json → gateway.auth.token
#      Uses http://127.0.0.1:<port>/v1/chat/completions as drop-in OpenAI API
#
API_MODE="openrouter"  # or "openclaw_gateway"
OPENROUTER_API_KEY="${OPENROUTER_API_KEY:-}"
OPENCLAW_GATEWAY_TOKEN=""
OPENCLAW_GATEWAY_PORT=""

# Try workspace .env
if [[ -z "$OPENROUTER_API_KEY" && -f "$WORKSPACE_ENV" ]]; then
  OPENROUTER_API_KEY="$(grep -E '^OPENROUTER_API_KEY=' "$WORKSPACE_ENV" \
    | cut -d= -f2- | tr -d '"' | tr -d "'" | head -1 || true)"
fi

# Try OpenClaw local gateway as fallback
if [[ -z "$OPENROUTER_API_KEY" ]] && command -v jq &>/dev/null && [[ -f "$OPENCLAW_CONFIG" ]]; then
  OPENCLAW_GATEWAY_TOKEN="$(jq -r '.gateway.auth.token // empty' "$OPENCLAW_CONFIG" 2>/dev/null || true)"
  OPENCLAW_GATEWAY_PORT="$(jq -r '.gateway.port // 18789' "$OPENCLAW_CONFIG" 2>/dev/null || true)"
  if [[ -n "$OPENCLAW_GATEWAY_TOKEN" ]]; then
    API_MODE="openclaw_gateway"
    info "No OPENROUTER_API_KEY found — using OpenClaw local gateway on :${OPENCLAW_GATEWAY_PORT}"
  fi
fi

if [[ -z "$OPENROUTER_API_KEY" && "$API_MODE" != "openclaw_gateway" ]]; then
  error "No API credentials found. Set OPENROUTER_API_KEY in environment or ~/.openclaw/workspace/.env, or ensure OpenClaw gateway is configured in ${OPENCLAW_CONFIG}"
fi

if [[ "$API_MODE" == "openrouter" ]]; then
  info "API: OpenRouter (key: ${#OPENROUTER_API_KEY} chars)"
else
  info "API: OpenClaw local gateway (port ${OPENCLAW_GATEWAY_PORT})"
fi

# ── Check prerequisites ───────────────────────────────────────────────────────
for cmd in git uv npm; do
  command -v "$cmd" &>/dev/null || error "Required tool not found: $cmd"
done

# ── Clone or update repo ──────────────────────────────────────────────────────
if [[ -d "$INSTALL_DIR/.git" ]]; then
  info "Repo exists at $INSTALL_DIR — pulling latest..."
  git -C "$INSTALL_DIR" pull --ff-only 2>&1 | tail -1
else
  info "Cloning llm-council to $INSTALL_DIR..."
  mkdir -p "$(dirname "$INSTALL_DIR")"
  git clone https://github.com/jeadland/llm-council.git "$INSTALL_DIR"
fi

cd "$INSTALL_DIR"

# ── Write .env ────────────────────────────────────────────────────────────────
info "Writing .env..."
if [[ "$API_MODE" == "openclaw_gateway" ]]; then
  # Use local OpenClaw gateway — OpenAI-compatible endpoint, no external key needed
  cat > .env <<EOF
# OpenClaw local gateway — no external API key required
OPENROUTER_API_KEY=${OPENCLAW_GATEWAY_TOKEN}
OPENROUTER_API_URL=http://127.0.0.1:${OPENCLAW_GATEWAY_PORT}/v1/chat/completions
EOF
  info ".env: OpenClaw gateway mode (http://127.0.0.1:${OPENCLAW_GATEWAY_PORT}/v1/chat/completions)"
else
  cat > .env <<EOF
OPENROUTER_API_KEY=${OPENROUTER_API_KEY}
EOF
  info ".env: OpenRouter direct mode"
fi

# ── Backend: uv sync ──────────────────────────────────────────────────────────
info "Running uv sync (Python backend)..."
uv sync 2>&1 | tail -5

# ── Frontend: npm ci ──────────────────────────────────────────────────────────
info "Running npm ci (frontend)..."
cd frontend
npm ci --silent
cd ..

# ── Stop any existing services ────────────────────────────────────────────────
if [[ -f "$PID_FILE" ]]; then
  warn "Stopping existing services..."
  while IFS= read -r pid; do
    [[ -z "$pid" ]] && continue
    kill "$pid" 2>/dev/null && info "  Killed PID $pid" || true
  done < "$PID_FILE"
  rm -f "$PID_FILE"
  sleep 1  # give OS a moment to release ports
fi

# ── Build frontend (preview mode only) ───────────────────────────────────────
if [[ "$MODE" == "preview" ]]; then
  info "Building frontend for preview..."
  cd frontend
  npm run build 2>&1 | tail -5
  cd ..
fi

# ── Kill any stale listeners on ports we need ─────────────────────────────────
PORTS_TO_FREE=(8001 5173 4173)
for port in "${PORTS_TO_FREE[@]}"; do
  STALE="$(lsof -nP -iTCP:${port} -sTCP:LISTEN -t 2>/dev/null || true)"
  if [[ -n "$STALE" ]]; then
    warn "Port ${port} in use by PID(s) $STALE — killing..."
    echo "$STALE" | xargs -r kill 2>/dev/null || true
  fi
done
# Wait for all ports to be freed
sleep 2
for port in "${PORTS_TO_FREE[@]}"; do
  STALE="$(lsof -nP -iTCP:${port} -sTCP:LISTEN -t 2>/dev/null || true)"
  if [[ -n "$STALE" ]]; then
    warn "Port ${port} still in use — force-killing PID(s) $STALE..."
    echo "$STALE" | xargs -r kill -9 2>/dev/null || true
    sleep 1
  fi
done

# ── Start backend ─────────────────────────────────────────────────────────────
BACKEND_LOG="/tmp/llm-council-backend.log"
info "Starting backend (FastAPI on :8001)..."
uv run python -m backend.main > "$BACKEND_LOG" 2>&1 &
BACKEND_PID=$!
echo "$BACKEND_PID" >> "$PID_FILE"
info "  Backend PID: $BACKEND_PID (log: $BACKEND_LOG)"

# Give backend a moment to start
sleep 2
if ! kill -0 "$BACKEND_PID" 2>/dev/null; then
  error "Backend failed to start. Check $BACKEND_LOG"
fi

# ── Start frontend ────────────────────────────────────────────────────────────
FRONTEND_LOG="/tmp/llm-council-frontend.log"
cd frontend

if [[ "$MODE" == "dev" ]]; then
  FRONTEND_PORT=5173
  info "Starting frontend (Vite dev on :${FRONTEND_PORT})..."
  npm run dev -- --host 0.0.0.0 --port "$FRONTEND_PORT" > "$FRONTEND_LOG" 2>&1 &
  FRONTEND_PID=$!
  LOCAL_IP="$(hostname -I | awk '{print $1}')"
  ACCESS_URL="http://${LOCAL_IP}:${FRONTEND_PORT}"
else
  FRONTEND_PORT=4173
  info "Starting frontend (Vite preview on :${FRONTEND_PORT})..."
  npm run preview -- --host 0.0.0.0 --port "$FRONTEND_PORT" > "$FRONTEND_LOG" 2>&1 &
  FRONTEND_PID=$!
  LOCAL_IP="$(hostname -I | awk '{print $1}')"
  ACCESS_URL="http://${LOCAL_IP}:${FRONTEND_PORT}"
fi

echo "$FRONTEND_PID" >> "$PID_FILE"
cd ..
info "  Frontend PID: $FRONTEND_PID (log: $FRONTEND_LOG)"

# ── Wait for frontend to bind ─────────────────────────────────────────────────
sleep 2

# ── Done ──────────────────────────────────────────────────────────────────────
echo ""
echo -e "${GREEN}✅ LLM Council installed and running!${NC}"
echo ""
echo "  Mode:     $MODE"
echo "  API:      $API_MODE"
echo "  Backend:  http://127.0.0.1:8001"
echo "  Frontend: ${ACCESS_URL}"
echo ""
echo "  Quick query: /council-brief 'Your question here'"
echo "  Stop:        bash ${SKILL_DIR}/stop.sh"
echo "  Status:      bash ${SKILL_DIR}/status.sh"
echo "  Backend log:  $BACKEND_LOG"
echo "  Frontend log: $FRONTEND_LOG"
echo ""
