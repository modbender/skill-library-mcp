#!/bin/bash
# Deploy Koda (OpenClaw) Container
# Usage: ./04-deploy-koda.sh [PORT]
# Run as root

set -e

KODA_PORT="${1:-18789}"  # Custom port, default 18789

echo "🐻 Deploying Koda"
echo "================="
echo "Port: $KODA_PORT"
echo ""

KODA_HOME="/home/koda"
KODA_DIR="$KODA_HOME/koda"

# Create Koda directories
echo "[1/4] Creating directories..."
mkdir -p "$KODA_DIR"/{config,workspace}
chown -R koda:koda "$KODA_DIR"

# Create docker-compose.yml
echo "[2/4] Creating docker-compose configuration..."
cat > "$KODA_DIR/docker-compose.yml" << EOF
services:
  koda:
    build:
      context: .
      dockerfile: Dockerfile
    image: koda:local
    container_name: koda
    restart: unless-stopped
    ports:
      - "${KODA_PORT}:18789"
    volumes:
      - ./config:/home/node/.openclaw
      - ./workspace:/home/node/clawd
    environment:
      - HOME=/home/node
      - TERM=xterm-256color
      - NODE_ENV=production
EOF

# Create Dockerfile
cat > "$KODA_DIR/Dockerfile" << 'EOF'
FROM node:22-slim

RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*
RUN corepack enable

WORKDIR /app

# Clone and build OpenClaw
RUN git clone --depth 1 https://github.com/openclaw/openclaw.git . && \
    pnpm install --frozen-lockfile && \
    pnpm build && \
    pnpm ui:build || true && \
    rm -rf .git

RUN useradd -m -s /bin/bash node || true
RUN chown -R node:node /app
USER node

ENV NODE_ENV=production
ENV HOME=/home/node

EXPOSE 18789

CMD ["node", "dist/index.js", "gateway", "--bind", "lan", "--port", "18789"]
EOF

# Save port config
echo "$KODA_PORT" > "$KODA_DIR/.port"
chown -R koda:koda "$KODA_DIR"

# Build and start
echo "[3/4] Building Koda image (this may take a few minutes)..."
cd "$KODA_DIR"
docker compose build

echo "[4/4] Starting Koda..."
docker compose up -d

# Wait for container to be ready
echo "Waiting for Koda to start..."
sleep 10

# Get server IP
SERVER_IP=$(curl -s ifconfig.me 2>/dev/null || hostname -I | awk '{print $1}')

# Check if running
if docker ps | grep -q koda; then
    echo ""
    echo "✅ Koda deployed successfully!"
    echo ""
    echo "Access webchat at: http://$SERVER_IP:$KODA_PORT"
    echo ""
    echo "Useful commands:"
    echo "  docker logs -f koda     # View logs"
    echo "  docker restart koda     # Restart"
    echo "  docker compose down     # Stop"
    echo ""
    echo "Next: Run 05-configure-identity.sh to set up the agent identity"
else
    echo "❌ Koda failed to start. Check logs with: docker logs koda"
    exit 1
fi
