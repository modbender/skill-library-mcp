#!/usr/bin/env bash
set -euo pipefail

# BrainDB Single-Node Setup
# One command: ./setup.sh
# Requires: Docker + Docker Compose

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "🧠 BrainDB Single-Node Setup"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Parse args
for arg in "$@"; do
  case "$arg" in
    --port=*) BRAINDB_PORT="${arg#*=}" ;;
  esac
done

# Check Docker
if ! command -v docker &>/dev/null; then
  echo "❌ Docker not found. Install: https://docs.docker.com/get-docker/"
  exit 1
fi

if ! docker compose version &>/dev/null 2>&1; then
  echo "❌ Docker Compose not found. Install: https://docs.docker.com/compose/install/"
  exit 1
fi

# Create .env with secure random password if missing
if [ ! -f .env ]; then
  RANDOM_PASS=$(openssl rand -base64 18 | tr -d '/+=' | head -c 24)
  sed "s/CHANGE_ME/$RANDOM_PASS/" .env.example > .env
  echo "📋 Created .env with auto-generated Neo4j password"
fi

# Source .env for port variables
set -a; source .env 2>/dev/null || true; set +a

# Override port from --port flag if provided
GATEWAY_PORT="${BRAINDB_PORT:-${GATEWAY_PORT:-3333}}"
# Write port override back to .env if --port was used
if [ -n "${BRAINDB_PORT:-}" ] && [ -f .env ]; then
  if grep -q "^GATEWAY_PORT=" .env; then
    sed -i'' -e "s/^GATEWAY_PORT=.*/GATEWAY_PORT=$BRAINDB_PORT/" .env
  else
    echo "GATEWAY_PORT=$BRAINDB_PORT" >> .env
  fi
fi

# Check port availability
if curl -sf "http://localhost:$GATEWAY_PORT/health" >/dev/null 2>&1; then
  echo ""
  echo "⚠️  Port $GATEWAY_PORT is already in use."
  echo "   Use --port=<number> to pick a different port, e.g.:"
  echo "   ./setup.sh --port=3345"
  echo ""
  exit 1
fi

# Build and start
echo ""
echo "🔨 Building containers (first run downloads ~2GB for embedding model)..."
docker compose build

echo ""
echo "🚀 Starting BrainDB..."
docker compose up -d

echo ""
echo "⏳ Waiting for services..."

GATEWAY_PORT="${GATEWAY_PORT:-3333}"

# Wait for gateway (depends on neo4j + embedder, so if gateway is up, all are up)
echo -n "  Starting"
for i in $(seq 1 90); do
  if curl -sf "http://localhost:$GATEWAY_PORT/health" >/dev/null 2>&1; then
    echo " ✅"
    break
  fi
  [ "$i" -eq 90 ] && echo " ❌ timeout (check: docker compose logs)" && exit 1
  echo -n "."
  sleep 2
done

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ BrainDB is running!"
echo ""
echo "  Gateway: http://localhost:$GATEWAY_PORT (localhost only)"
echo ""
echo "Quick test:"
echo "  curl -s http://localhost:$GATEWAY_PORT/health | python3 -m json.tool"
echo ""
echo "Encode a memory:"
echo "  curl -s -X POST http://localhost:$GATEWAY_PORT/memory/encode \\"
echo "    -H 'Content-Type: application/json' \\"
echo "    -d '{\"event\":\"test\",\"content\":\"BrainDB is alive\",\"shard\":\"episodic\"}'"
echo ""
echo "Recall:"
echo "  curl -s -X POST http://localhost:$GATEWAY_PORT/memory/recall \\"
echo "    -H 'Content-Type: application/json' \\"
echo "    -d '{\"query\":\"what is BrainDB\"}'"
echo ""
echo "Stop:    docker compose down"
echo "Logs:    docker compose logs -f"
echo "Reset:   docker compose down -v  (⚠️ deletes all data)"
