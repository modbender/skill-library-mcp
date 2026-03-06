#!/bin/bash
# Codespace Manager - GitHub Codespace-like isolated dev environments
# Powered by code-server + Docker + Cloudflare Tunnel
# Usage: codespace <command> [name] [options]

set -e

CODESPACE_BASE="${CODESPACE_BASE:-$HOME/codespaces}"
CODESPACE_PASSWORD="${CODESPACE_PASSWORD:-codespace}"
CODESPACE_IMAGE="codespace-manager:latest"
SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

usage() {
    cat << EOF
Codespace Manager - Isolated Dev Environments

Usage: codespace <command> [name] [options]

Commands:
  setup                                         Build the Docker image (run once)
  create <name> [--git <repo>] [--opencode]     Create a new codespace
  start <name>                                  Start codespace (returns access URL)
  stop <name>                                   Stop codespace
  restart <name>                                Restart codespace
  delete <name>                                 Delete codespace (data will be lost!)
  list                                          List all codespaces
  status [name]                                 View status
  logs <name>                                   View logs
  url <name>                                    Get access URL (regenerate tunnel)
  password <new-password>                       Set default password for new codespaces

Environment Variables:
  CODESPACE_PASSWORD    Access password (default: codespace)
  CODESPACE_BASE        Data directory (default: ~/codespaces)

Examples:
  codespace setup
  codespace create myproject
  codespace create myproject --opencode
  codespace create web-app --git https://github.com/user/repo --opencode
  codespace start myproject
  codespace password mysecretpass
  codespace list

EOF
    exit 1
}

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[OK]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

ensure_base_dir() {
    mkdir -p "$CODESPACE_BASE"
}

check_dependencies() {
    local missing=""
    command -v docker &>/dev/null || missing="docker"
    command -v cloudflared &>/dev/null || missing="$missing cloudflared"
    if [ -n "$missing" ]; then
        log_error "Missing dependencies: $missing"
        log_info "Install docker: https://docs.docker.com/get-docker/"
        log_info "Install cloudflared: https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/"
        exit 1
    fi
}

check_image() {
    if ! docker image inspect "$CODESPACE_IMAGE" &>/dev/null; then
        log_error "Docker image '$CODESPACE_IMAGE' not found."
        log_info "Run 'codespace setup' first to build the image."
        exit 1
    fi
}

get_container_name() {
    echo "codespace-$1"
}

get_port() {
    local hash=$(echo -n "$1" | md5sum | cut -c1-4)
    local port=$((0x$hash % 1000 + 9000))
    echo $port
}

codespace_exists() {
    [ -d "$CODESPACE_BASE/$1" ]
}

container_running() {
    local container=$(get_container_name "$1")
    docker ps --format '{{.Names}}' | grep -q "^${container}$"
}

container_exists() {
    local container=$(get_container_name "$1")
    docker ps -a --format '{{.Names}}' | grep -q "^${container}$"
}

# Load saved password
load_password() {
    local pw_file="$CODESPACE_BASE/.default_password"
    if [ -f "$pw_file" ] && [ "$CODESPACE_PASSWORD" = "codespace" ]; then
        CODESPACE_PASSWORD=$(cat "$pw_file")
    fi
}

# Setup: build the Docker image
cmd_setup() {
    local dockerfile="$SKILL_DIR/assets/Dockerfile.txt"
    if [ ! -f "$dockerfile" ]; then
        log_error "Dockerfile not found at $dockerfile"
        exit 1
    fi

    log_info "Building codespace image..."
    log_info "This includes: code-server, Bun, uv, OpenCode, git, build-essential"
    docker build -t "$CODESPACE_IMAGE" -f "$dockerfile" "$SKILL_DIR/assets/"
    log_success "Image '$CODESPACE_IMAGE' built successfully"
    log_info "Pre-installed tools: bun, uv, opencode, git, curl, wget"
}

# Set default password
cmd_password() {
    local new_pw="$1"
    if [ -z "$new_pw" ]; then
        log_error "Please provide a new password"
        exit 1
    fi
    ensure_base_dir
    echo "$new_pw" > "$CODESPACE_BASE/.default_password"
    chmod 600 "$CODESPACE_BASE/.default_password"
    log_success "Default password updated (applies to new codespaces)"
}

# Create codespace
cmd_create() {
    local name="$1"
    shift || true
    local git_repo=""
    local init_opencode=""

    while [[ $# -gt 0 ]]; do
        case $1 in
            --git) git_repo="$2"; shift 2 ;;
            --opencode) init_opencode="yes"; shift ;;
            *) log_error "Unknown option: $1"; exit 1 ;;
        esac
    done

    if [ -z "$name" ]; then
        log_error "Please provide a codespace name"
        exit 1
    fi

    if codespace_exists "$name"; then
        log_error "Codespace '$name' already exists"
        exit 1
    fi

    check_image
    ensure_base_dir
    local workspace="$CODESPACE_BASE/$name"
    mkdir -p "$workspace"

    log_info "Creating codespace: $name"
    log_info "Workspace: $workspace"

    if [ -n "$git_repo" ]; then
        log_info "Cloning repo: $git_repo"
        git clone "$git_repo" "$workspace/project"
    else
        mkdir -p "$workspace/project"
        echo "# $name" > "$workspace/project/README.md"
    fi

    # Initialize OpenCode project config
    if [ "$init_opencode" = "yes" ]; then
        log_info "Initializing OpenCode project config..."
        cat > "$workspace/project/opencode.json" << 'OCEOF'
{
  "$schema": "https://opencode.ai/config.json",
  "model": "anthropic/claude-sonnet-4-5",
  "autoupdate": true
}
OCEOF
        log_success "Created opencode.json"
    fi

    # Fix permissions: code-server runs as UID 1000 inside the container
    chown -R 1000:1000 "$workspace/project"

    # Save metadata
    cat > "$workspace/.codespace.json" << EOF
{
    "name": "$name",
    "created": "$(date -Iseconds)",
    "git_repo": "$git_repo",
    "opencode": "$init_opencode",
    "port": $(get_port "$name"),
    "password": "$CODESPACE_PASSWORD"
}
EOF

    log_success "Codespace '$name' created"
    log_info "Run 'codespace start $name' to launch"
}

# Start codespace
cmd_start() {
    local name="$1"

    if [ -z "$name" ]; then
        log_error "Please provide a codespace name"
        exit 1
    fi

    if ! codespace_exists "$name"; then
        log_error "Codespace '$name' does not exist"
        exit 1
    fi

    check_image
    local container=$(get_container_name "$name")
    local port=$(get_port "$name")
    local workspace="$CODESPACE_BASE/$name"

    # Read per-codespace password from metadata
    local cs_password="$CODESPACE_PASSWORD"
    if [ -f "$workspace/.codespace.json" ]; then
        local saved_pw=$(jq -r '.password // empty' "$workspace/.codespace.json" 2>/dev/null)
        [ -n "$saved_pw" ] && cs_password="$saved_pw"
    fi

    if container_running "$name"; then
        log_warn "Codespace '$name' is already running"
    else
        if container_exists "$name"; then
            log_info "Starting existing container..."
            docker start "$container"
        else
            log_info "Creating and starting container..."
            docker run -d \
                --name "$container" \
                -p "127.0.0.1:$port:8080" \
                -v "$workspace/project:/home/coder/project" \
                -e "PASSWORD=$cs_password" \
                --restart unless-stopped \
                "$CODESPACE_IMAGE" \
                --bind-addr 0.0.0.0:8080 \
                --auth password \
                /home/coder/project
        fi
        sleep 2
    fi

    # Start cloudflare tunnel
    log_info "Creating Cloudflare Tunnel..."

    pkill -f "cloudflared.*localhost:$port" 2>/dev/null || true
    sleep 1

    local tunnel_log="$workspace/.tunnel.log"
    nohup cloudflared tunnel --url "http://localhost:$port" > "$tunnel_log" 2>&1 &
    local tunnel_pid=$!
    echo $tunnel_pid > "$workspace/.tunnel.pid"

    sleep 5
    local url=$(grep -o 'https://[a-z0-9-]*\.trycloudflare\.com' "$tunnel_log" 2>/dev/null | head -1)

    if [ -n "$url" ]; then
        log_success "Codespace '$name' is running"
        echo ""
        echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo -e "${GREEN}  URL:      ${YELLOW}$url${NC}"
        echo -e "${GREEN}  Password: ${YELLOW}$cs_password${NC}"
        echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo ""

        # Update metadata
        local meta="$workspace/.codespace.json"
        if [ -f "$meta" ]; then
            local tmp=$(mktemp)
            jq --arg url "$url" '. + {url: $url, last_start: now | todate}' "$meta" > "$tmp" 2>/dev/null && mv "$tmp" "$meta"
        fi
    else
        log_warn "Tunnel starting, run 'codespace url $name' to get the URL shortly"
    fi
}

# Stop codespace
cmd_stop() {
    local name="$1"

    if [ -z "$name" ]; then
        log_error "Please provide a codespace name"
        exit 1
    fi

    local container=$(get_container_name "$name")
    local workspace="$CODESPACE_BASE/$name"
    local port=$(get_port "$name")

    # Stop tunnel
    if [ -f "$workspace/.tunnel.pid" ]; then
        local pid=$(cat "$workspace/.tunnel.pid")
        kill $pid 2>/dev/null || true
        rm "$workspace/.tunnel.pid"
    fi
    pkill -f "cloudflared.*localhost:$port" 2>/dev/null || true

    # Stop container
    if container_running "$name"; then
        docker stop "$container"
        log_success "Codespace '$name' stopped"
    else
        log_warn "Codespace '$name' is not running"
    fi
}

# Restart codespace
cmd_restart() {
    local name="$1"
    cmd_stop "$name"
    sleep 1
    cmd_start "$name"
}

# Delete codespace
cmd_delete() {
    local name="$1"

    if [ -z "$name" ]; then
        log_error "Please provide a codespace name"
        exit 1
    fi

    if ! codespace_exists "$name"; then
        log_error "Codespace '$name' does not exist"
        exit 1
    fi

    local container=$(get_container_name "$name")
    local workspace="$CODESPACE_BASE/$name"
    local port=$(get_port "$name")

    pkill -f "cloudflared.*localhost:$port" 2>/dev/null || true
    docker stop "$container" 2>/dev/null || true
    docker rm "$container" 2>/dev/null || true
    rm -rf "$workspace"

    log_success "Codespace '$name' deleted"
}

# List all codespaces
cmd_list() {
    ensure_base_dir

    echo ""
    echo -e "${BLUE}Codespaces:${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    printf "%-15s %-10s %-45s\n" "NAME" "STATUS" "URL"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    local found=0
    for dir in "$CODESPACE_BASE"/*/; do
        [ -d "$dir" ] || continue
        found=1

        local name=$(basename "$dir")
        local status="stopped"
        local url="-"

        if container_running "$name"; then
            status="${GREEN}running${NC}"
            local meta="$dir/.codespace.json"
            if [ -f "$meta" ]; then
                url=$(jq -r '.url // "-"' "$meta" 2>/dev/null)
            fi
        else
            status="${YELLOW}stopped${NC}"
        fi

        printf "%-15s %-20b %-45s\n" "$name" "$status" "$url"
    done

    if [ $found -eq 0 ]; then
        echo "  (no codespaces yet)"
    fi

    echo ""
}

# View status
cmd_status() {
    local name="$1"

    if [ -z "$name" ]; then
        cmd_list
        return
    fi

    if ! codespace_exists "$name"; then
        log_error "Codespace '$name' does not exist"
        exit 1
    fi

    local container=$(get_container_name "$name")
    local workspace="$CODESPACE_BASE/$name"
    local meta="$workspace/.codespace.json"

    echo ""
    echo -e "${BLUE}Codespace: $name${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    if [ -f "$meta" ]; then
        echo "Created:   $(jq -r '.created // "unknown"' "$meta")"
        echo "Git repo:  $(jq -r '.git_repo // "-"' "$meta")"
        echo "Port:      $(jq -r '.port // "-"' "$meta")"
        echo "OpenCode:  $(jq -r 'if .opencode == "yes" then "enabled" else "no" end' "$meta")"
    fi

    if container_running "$name"; then
        echo -e "Status:    ${GREEN}running${NC}"
        if [ -f "$meta" ]; then
            echo "URL:       $(jq -r '.url // "-"' "$meta")"
        fi
    else
        echo -e "Status:    ${YELLOW}stopped${NC}"
    fi

    echo "Workspace: $workspace/project"
    echo ""
}

# Get URL
cmd_url() {
    local name="$1"

    if [ -z "$name" ]; then
        log_error "Please provide a codespace name"
        exit 1
    fi

    if ! container_running "$name"; then
        log_error "Codespace '$name' is not running, start it first"
        exit 1
    fi

    local workspace="$CODESPACE_BASE/$name"
    local port=$(get_port "$name")

    pkill -f "cloudflared.*localhost:$port" 2>/dev/null || true
    sleep 1

    local tunnel_log="$workspace/.tunnel.log"
    nohup cloudflared tunnel --url "http://localhost:$port" > "$tunnel_log" 2>&1 &
    echo $! > "$workspace/.tunnel.pid"

    sleep 5
    local url=$(grep -o 'https://[a-z0-9-]*\.trycloudflare\.com' "$tunnel_log" 2>/dev/null | head -1)

    if [ -n "$url" ]; then
        # Read password
        local cs_password="$CODESPACE_PASSWORD"
        local meta="$workspace/.codespace.json"
        if [ -f "$meta" ]; then
            local saved_pw=$(jq -r '.password // empty' "$meta" 2>/dev/null)
            [ -n "$saved_pw" ] && cs_password="$saved_pw"
        fi

        echo ""
        echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo -e "${GREEN}  URL:      ${YELLOW}$url${NC}"
        echo -e "${GREEN}  Password: ${YELLOW}$cs_password${NC}"
        echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo ""

        if [ -f "$meta" ]; then
            local tmp=$(mktemp)
            jq --arg url "$url" '.url = $url' "$meta" > "$tmp" 2>/dev/null && mv "$tmp" "$meta"
        fi
    else
        log_error "Failed to get URL, try again shortly"
    fi
}

# View logs
cmd_logs() {
    local name="$1"

    if [ -z "$name" ]; then
        log_error "Please provide a codespace name"
        exit 1
    fi

    local container=$(get_container_name "$name")
    docker logs --tail 50 "$container"
}

# Main
check_dependencies
load_password

case "${1:-}" in
    setup)    cmd_setup ;;
    create)   shift; cmd_create "$@" ;;
    start)    shift; cmd_start "$@" ;;
    stop)     shift; cmd_stop "$@" ;;
    restart)  shift; cmd_restart "$@" ;;
    delete)   shift; cmd_delete "$@" ;;
    list)     cmd_list ;;
    status)   shift; cmd_status "$@" ;;
    url)      shift; cmd_url "$@" ;;
    logs)     shift; cmd_logs "$@" ;;
    password) shift; cmd_password "$@" ;;
    *)        usage ;;
esac
