#!/bin/bash
#
# Install Hummingbot MCP Server for AI agents
# Usage: ./install_mcp.sh --agent <cli> --url <url> --user <user> --pass <pass>
#
# Examples:
#   ./install_mcp.sh --agent claude
#   ./install_mcp.sh --agent gemini --user admin --pass admin
#   ./install_mcp.sh --agent codex --url http://localhost:8000
#
set -eu

# Detect OS for Docker host URL
# MCP runs in Docker, so it needs host.docker.internal (Mac/Windows) or host-gateway (Linux)
get_docker_host_url() {
    local os=$(uname -s | tr '[:upper:]' '[:lower:]')
    if [[ "$os" == "darwin" ]] || [[ "$os" == *"mingw"* ]] || [[ "$os" == *"msys"* ]]; then
        # macOS or Windows - use host.docker.internal
        echo "http://host.docker.internal:8000"
    else
        # Linux - host.docker.internal works with Docker 20.10+
        echo "http://host.docker.internal:8000"
    fi
}

# Defaults
API_URL=$(get_docker_host_url)
API_USER="admin"
API_PASS="admin"
AGENT_CLI=""
MCP_IMAGE="hummingbot/hummingbot-mcp:latest"

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --agent) AGENT_CLI="$2"; shift 2 ;;
        --url) API_URL="$2"; shift 2 ;;
        --user) API_USER="$2"; shift 2 ;;
        --pass) API_PASS="$2"; shift 2 ;;
        -h|--help)
            echo "Usage: $0 --agent <cli> [--url <url>] [--user <user>] [--pass <pass>]"
            echo ""
            echo "Options:"
            echo "  --agent CLI    Agent CLI command (claude, gemini, codex, etc.)"
            echo "  --url URL      Hummingbot API URL (default: http://host.docker.internal:8000)"
            echo "  --user USER    API username (default: admin)"
            echo "  --pass PASS    API password (default: admin)"
            echo ""
            echo "Examples:"
            echo "  $0 --agent claude"
            echo "  $0 --agent gemini --user myuser --pass mypass"
            exit 0
            ;;
        *) shift ;;
    esac
done

# Validate agent
if [[ -z "$AGENT_CLI" ]]; then
    echo "Error: --agent is required"
    echo "Usage: $0 --agent <cli> [--url <url>] [--user <user>] [--pass <pass>]"
    exit 1
fi

# Check if agent CLI exists
if ! command -v "$AGENT_CLI" &>/dev/null; then
    echo "Error: '$AGENT_CLI' command not found"
    exit 1
fi

echo "Installing Hummingbot MCP Server"
echo "================================"
echo "Agent CLI: $AGENT_CLI"
echo "API URL: $API_URL"
echo "API User: $API_USER"
echo ""

# Pull MCP image
echo "Pulling MCP image..."
docker pull "$MCP_IMAGE"

# Configure MCP for the agent
echo "Configuring MCP for $AGENT_CLI..."

# Build the docker command
DOCKER_CMD="docker run --rm -i -e HUMMINGBOT_API_URL=$API_URL -e HUMMINGBOT_API_USERNAME=$API_USER -e HUMMINGBOT_API_PASSWORD=$API_PASS -v hummingbot_mcp:/root/.hummingbot_mcp $MCP_IMAGE"

# Different CLIs have slightly different syntax
case "$AGENT_CLI" in
    gemini)
        # Gemini: gemini mcp add <name> <command> [args...]
        $AGENT_CLI mcp add hummingbot $DOCKER_CMD
        ;;
    *)
        # Claude/Codex: <cli> mcp add <name> -- <command> [args...]
        $AGENT_CLI mcp add hummingbot -- $DOCKER_CMD
        ;;
esac

echo ""
echo "Done! Restart $AGENT_CLI to load the MCP server."
