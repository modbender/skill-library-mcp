#!/bin/bash
#
# Deploy Hummingbot API trading infrastructure
#
# Usage:
#   # Check if already installed
#   bash scripts/deploy_hummingbot_api.sh status
#
#   # Fresh install (interactive)
#   bash scripts/deploy_hummingbot_api.sh install
#
#   # Fresh install with defaults (non-interactive / containers)
#   bash scripts/deploy_hummingbot_api.sh install --defaults
#
#   # Upgrade existing installation
#   bash scripts/deploy_hummingbot_api.sh upgrade
#
#   # View logs
#   bash scripts/deploy_hummingbot_api.sh logs
#
#   # Reset (stop and remove)
#   bash scripts/deploy_hummingbot_api.sh reset
#
set -e

INSTALL_DIR="${HUMMINGBOT_API_DIR:-./hummingbot-api}"
REPO_URL="https://github.com/hummingbot/hummingbot-api.git"

# Colors (if terminal supports it)
if [ -t 1 ]; then
    GREEN='\033[0;32m'
    RED='\033[0;31m'
    YELLOW='\033[1;33m'
    NC='\033[0m'
else
    GREEN='' RED='' YELLOW='' NC=''
fi

ok()   { echo -e "${GREEN}✓${NC} $*"; }
fail() { echo -e "${RED}✗${NC} $*"; }
warn() { echo -e "${YELLOW}!${NC} $*"; }

check_docker() {
    if ! command -v docker &>/dev/null; then
        fail "Docker is not installed"
        exit 1
    fi
    if ! docker info &>/dev/null; then
        fail "Docker daemon is not running"
        exit 1
    fi
    if ! docker compose version &>/dev/null; then
        fail "Docker Compose is not available"
        exit 1
    fi
}

is_running() {
    if [ -d "$INSTALL_DIR" ]; then
        cd "$INSTALL_DIR"
        if docker compose ps --status running 2>/dev/null | grep -q "hummingbot-api"; then
            return 0
        fi
    fi
    return 1
}

cmd_status() {
    echo "Hummingbot API Status"
    echo "====================="
    echo ""

    if [ ! -d "$INSTALL_DIR" ]; then
        fail "Not installed (directory $INSTALL_DIR not found)"
        echo ""
        echo "Run: bash scripts/deploy_hummingbot_api.sh install"
        return
    fi

    cd "$INSTALL_DIR"

    if is_running; then
        ok "Hummingbot API is running"
        echo ""

        # Show container info
        docker compose ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}" 2>/dev/null || true

        # Verify API is responding
        API_URL="${HUMMINGBOT_API_URL:-http://localhost:8000}"
        if curl -s "$API_URL/docs" 2>/dev/null | grep -qi "swagger"; then
            echo ""
            ok "API is accessible at $API_URL"
            echo "  Swagger UI: $API_URL/docs"
        else
            echo ""
            warn "API container is running but not responding yet (may still be starting)"
        fi
    else
        fail "Hummingbot API is not running"
        echo ""
        echo "Start with: cd $INSTALL_DIR && make deploy"
    fi
}

cmd_install() {
    local USE_DEFAULTS=false
    for arg in "$@"; do
        [ "$arg" = "--defaults" ] && USE_DEFAULTS=true
    done

    echo "Installing Hummingbot API"
    echo "========================="
    echo ""

    check_docker

    if [ -d "$INSTALL_DIR" ]; then
        if is_running; then
            ok "Already installed and running at $INSTALL_DIR"
            return
        fi
        warn "Directory exists but not running. Starting..."
        cd "$INSTALL_DIR"
        make deploy
        sleep 3
        if is_running; then
            ok "Hummingbot API started"
        else
            fail "Failed to start. Check logs: docker compose logs -f"
        fi
        return
    fi

    # Clone
    echo "Cloning hummingbot-api..."
    git clone "$REPO_URL" "$INSTALL_DIR"
    cd "$INSTALL_DIR"

    # Detect container environment
    IN_CONTAINER=false
    if [ -f /.dockerenv ] || grep -q docker /proc/1/cgroup 2>/dev/null || grep -q containerd /proc/1/cgroup 2>/dev/null; then
        IN_CONTAINER=true
    fi

    HAS_TTY=false
    [ -t 0 ] && HAS_TTY=true

    if [ "$IN_CONTAINER" = "true" ] || [ "$USE_DEFAULTS" = "true" ] || [ "$HAS_TTY" = "false" ]; then
        echo "Setting up with defaults (admin/admin)..."

        # Set USER env var and create sudo shim if needed
        export USER=${USER:-root}
        if [ "$(id -u)" = "0" ] && ! command -v sudo &>/dev/null; then
            echo -e '#!/bin/bash\nwhile [[ "$1" == *=* ]]; do export "$1"; shift; done\nexec "$@"' > /usr/local/bin/sudo
            chmod +x /usr/local/bin/sudo
        fi

        # Create .env manually
        cat > .env << EOF
USERNAME=admin
PASSWORD=admin
CONFIG_PASSWORD=admin
DEBUG_MODE=false
BROKER_HOST=hummingbot-broker
BROKER_PORT=1883
BROKER_USERNAME=admin
BROKER_PASSWORD=password
DATABASE_URL=postgresql+asyncpg://hbot:hummingbot-api@hummingbot-postgres:5432/hummingbot_api
BOTS_PATH=/hummingbot-api/bots
EOF

        # Patch docker-compose for container environments
        if [ "$IN_CONTAINER" = "true" ]; then
            sed -i 's|./bots:/hummingbot-api/bots|hummingbot-bots:/hummingbot-api/bots|g' docker-compose.yml
            sed -i '/init-db.sql.*docker-entrypoint/d' docker-compose.yml
            tail -5 docker-compose.yml | grep -q "hummingbot-bots:" || echo "  hummingbot-bots: { }" >> docker-compose.yml
        fi

        touch .setup-complete
    else
        echo "Running interactive setup..."
        make setup
    fi

    # Deploy
    echo "Deploying..."
    make deploy

    # Verify
    echo ""
    echo "Waiting for API to start..."
    sleep 3

    if docker logs hummingbot-api 2>&1 | grep -qi "uvicorn running"; then
        ok "Hummingbot API is running"
        echo "  URL: http://localhost:8000"
        echo "  Swagger UI: http://localhost:8000/docs"
    else
        warn "API may still be starting. Check: docker logs hummingbot-api"
    fi
}

cmd_upgrade() {
    echo "Upgrading Hummingbot API"
    echo "========================"

    if [ ! -d "$INSTALL_DIR" ]; then
        fail "Not installed. Run install first."
        exit 1
    fi

    cd "$INSTALL_DIR"
    echo "Pulling latest..."
    git pull
    echo "Redeploying..."
    make deploy
    sleep 3
    ok "Upgrade complete"
}

cmd_logs() {
    if [ ! -d "$INSTALL_DIR" ]; then
        fail "Not installed"
        exit 1
    fi
    cd "$INSTALL_DIR"
    docker compose logs --tail=100
}

cmd_reset() {
    if [ ! -d "$INSTALL_DIR" ]; then
        fail "Not installed"
        return
    fi

    echo "Stopping and removing Hummingbot API..."
    cd "$INSTALL_DIR"
    docker compose down -v 2>/dev/null || true
    cd ~
    rm -rf "$INSTALL_DIR"
    ok "Hummingbot API removed"
}

# Main
COMMAND="${1:-status}"
shift 2>/dev/null || true

case "$COMMAND" in
    status)  cmd_status ;;
    install) cmd_install "$@" ;;
    upgrade) cmd_upgrade ;;
    logs)    cmd_logs ;;
    reset)   cmd_reset ;;
    *)
        echo "Usage: deploy_hummingbot_api.sh {status|install|upgrade|logs|reset}"
        echo ""
        echo "Commands:"
        echo "  status   Check installation status"
        echo "  install  Install Hummingbot API (--defaults for non-interactive)"
        echo "  upgrade  Pull latest and redeploy"
        echo "  logs     View container logs"
        echo "  reset    Stop and remove installation"
        exit 1
        ;;
esac
