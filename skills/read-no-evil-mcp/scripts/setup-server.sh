#!/usr/bin/env bash
set -euo pipefail

# Flag-driven setup for read-no-evil-mcp Docker container.
# Pulls the official image, loads credentials from .env, and starts the server.
# Designed for invocation by LLM agents (no interactive prompts).

IMAGE="ghcr.io/thekie/read-no-evil-mcp:0.3"

# --- Defaults ---
CONFIG=""
ENV_FILE=""
PORT=8000
CONTAINER_NAME="rnoe-mcp"

# --- Parse flags ---
while [[ $# -gt 0 ]]; do
    case "$1" in
        --config)   CONFIG="$2";         shift 2 ;;
        --env-file) ENV_FILE="$2";       shift 2 ;;
        --port)     PORT="$2";           shift 2 ;;
        --name)     CONTAINER_NAME="$2"; shift 2 ;;
        -h|--help)
            echo "Usage: setup-server.sh --config PATH --env-file PATH [--port 8000] [--name rnoe-mcp]"
            echo
            echo "Flags:"
            echo "  --config    Config file path (required)"
            echo "  --env-file  .env file with credentials (required)"
            echo "  --port      Host port to bind (default: 8000)"
            echo "  --name      Docker container name (default: rnoe-mcp)"
            exit 0
            ;;
        *)
            echo "Error: Unknown flag: $1" >&2
            echo "Run with --help for usage." >&2
            exit 1
            ;;
    esac
done

# --- Validate required flags ---
if [ -z "$CONFIG" ]; then
    echo "Error: --config is required." >&2
    exit 1
fi
if [ -z "$ENV_FILE" ]; then
    echo "Error: --env-file is required." >&2
    exit 1
fi
if [ ! -f "$CONFIG" ]; then
    echo "Error: Config file not found: $CONFIG" >&2
    exit 1
fi
if [ ! -f "$ENV_FILE" ]; then
    echo "Error: .env file not found: $ENV_FILE" >&2
    exit 1
fi

# --- Check Docker ---
if ! command -v docker &>/dev/null; then
    echo "Error: Docker is not installed. Please install Docker first." >&2
    echo "  https://docs.docker.com/get-docker/" >&2
    exit 1
fi

if ! docker info &>/dev/null 2>&1; then
    echo "Error: Docker daemon is not running. Please start Docker." >&2
    exit 1
fi

echo "Docker is ready."

# --- Pull image ---
echo "Pulling $IMAGE ..."
docker pull "$IMAGE"

# --- Load credentials from .env ---
env_args=()
while IFS= read -r line || [ -n "$line" ]; do
    line="${line%%#*}"  # strip comments
    line="$(echo "$line" | xargs)"  # trim whitespace
    if [[ "$line" == RNOE_ACCOUNT_*_PASSWORD=* ]]; then
        env_args+=("-e" "$line")
    fi
done < "$ENV_FILE"
echo "Loaded ${#env_args[@]} credential(s) from $ENV_FILE."

# --- Stop existing container ---
if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    echo "Stopping existing $CONTAINER_NAME container..."
    docker rm -f "$CONTAINER_NAME" >/dev/null 2>&1 || true
fi

# --- Start container ---
echo "Starting container..."
docker run -d \
    --name "$CONTAINER_NAME" \
    -p "${PORT}:8000" \
    -v "$CONFIG:/app/rnoe.yaml:ro" \
    -e RNOE_TRANSPORT=http \
    "${env_args[@]}" \
    "$IMAGE"

# --- Health check ---
echo "Waiting for server to start..."
for i in $(seq 1 30); do
    if curl -sf "http://localhost:${PORT}/mcp" -X POST \
        -H "Content-Type: application/json" \
        -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-03-26","capabilities":{},"clientInfo":{"name":"setup","version":"0.1.0"}}}' \
        >/dev/null 2>&1; then
        echo
        echo "Server is ready!"
        echo "  URL: http://localhost:${PORT}"
        echo "  Container: $CONTAINER_NAME"
        exit 0
    fi
    sleep 1
    printf "."
done

echo
echo "Warning: Server did not respond within 30 seconds." >&2
echo "Check logs: docker logs $CONTAINER_NAME" >&2
exit 1
