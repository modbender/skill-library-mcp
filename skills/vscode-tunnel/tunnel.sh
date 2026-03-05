#!/bin/bash
#
# VS Code Tunnel Manager
# Manage VS Code Remote Tunnels in Docker containers
#
# Usage: tunnel.sh <command> [options]
#   start [name]  - Start tunnel
#   stop          - Stop tunnel
#   status        - View status
#   log           - View logs
#

set -e

# ==========================================
# Configuration
# ==========================================
CLI_DIR="${VSCODE_CLI_DIR:-$HOME/.vscode-cli}"
CLI_URL="https://code.visualstudio.com/sha/download?build=stable&os=cli-alpine-x64"
LOG_FILE="$CLI_DIR/tunnel.log"
PID_FILE="$CLI_DIR/tunnel.pid"

# ==========================================
# Color Output
# ==========================================
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${BLUE}[INFO]${NC} $(date '+%H:%M:%S') $1"
}

log_success() {
    echo -e "${GREEN}[OK]${NC} $(date '+%H:%M:%S') $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $(date '+%H:%M:%S') $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $(date '+%H:%M:%S') $1"
}

# ==========================================
# Utility Functions
# ==========================================
check_dependencies() {
    local missing=()
    
    for cmd in curl tar grep; do
        if ! command -v "$cmd" &> /dev/null; then
            missing+=("$cmd")
        fi
    done
    
    if [ ${#missing[@]} -gt 0 ]; then
        log_error "Missing dependencies: ${missing[*]}"
        log_info "Install with: apk add ${missing[*]} or apt install ${missing[*]}"
        exit 1
    fi
}

ensure_cli_dir() {
    if [ ! -d "$CLI_DIR" ]; then
        log_info "Creating CLI directory: $CLI_DIR"
        mkdir -p "$CLI_DIR"
    fi
}

download_cli() {
    local cli_bin="$CLI_DIR/code"
    
    if [ -f "$cli_bin" ]; then
        log_info "CLI already exists, skipping download"
        return 0
    fi
    
    log_info "Downloading VS Code CLI..."
    
    local tmp_file="$CLI_DIR/vscode_cli.tar.gz"
    
    if ! curl -sL "$CLI_URL" -o "$tmp_file"; then
        log_error "Download failed"
        rm -f "$tmp_file"
        exit 1
    fi
    
    log_info "Extracting CLI..."
    if ! tar -xzf "$tmp_file" -C "$CLI_DIR"; then
        log_error "Extraction failed"
        rm -f "$tmp_file"
        exit 1
    fi
    
    rm -f "$tmp_file"
    chmod +x "$cli_bin"
    log_success "CLI downloaded: $cli_bin"
}

get_tunnel_name() {
    local provided_name="$1"
    
    # Priority: argument > env variable > interactive input
    if [ -n "$provided_name" ]; then
        echo "$provided_name"
        return
    fi
    
    if [ -n "$VSCODE_TUNNEL_NAME" ]; then
        echo "$VSCODE_TUNNEL_NAME"
        return
    fi
    
    # Interactive input
    echo ""
    read -p "$(echo -e ${YELLOW}Enter tunnel name [default: docker-dev]: ${NC})" name
    echo "${name:-docker-dev}"
}

get_tunnel_pid() {
    if [ -f "$PID_FILE" ]; then
        local pid=$(cat "$PID_FILE")
        if kill -0 "$pid" 2>/dev/null; then
            echo "$pid"
            return
        fi
    fi
    
    # Fallback: find by process name
    pgrep -f "code tunnel" 2>/dev/null | head -1
}

# ==========================================
# Command Implementations
# ==========================================
cmd_start() {
    local tunnel_name=$(get_tunnel_name "$1")
    
    log_info "Starting VS Code Tunnel..."
    log_info "Tunnel name: $tunnel_name"
    
    # Check if already running
    local existing_pid=$(get_tunnel_pid)
    if [ -n "$existing_pid" ]; then
        log_warn "Tunnel already running (PID: $existing_pid)"
        log_info "Use 'tunnel.sh status' to check status"
        exit 0
    fi
    
    # Prepare environment
    check_dependencies
    ensure_cli_dir
    download_cli
    
    # Start tunnel
    log_info "Launching tunnel..."
    cd "$CLI_DIR"
    
    nohup ./code tunnel \
        --accept-server-license-terms \
        --name "$tunnel_name" \
        > "$LOG_FILE" 2>&1 &
    
    local pid=$!
    echo "$pid" > "$PID_FILE"
    
    log_success "Tunnel started (PID: $pid)"
    
    # Wait and show authorization info
    log_info "Waiting for tunnel initialization..."
    sleep 5
    
    echo ""
    echo "========================================"
    echo "         Authorization Info"
    echo "========================================"
    
    if grep -q "To grant access" "$LOG_FILE" 2>/dev/null; then
        grep -iA 3 "To grant access" "$LOG_FILE"
    else
        log_info "No authorization code detected, may already be authorized"
        echo "Log preview:"
        head -n 10 "$LOG_FILE"
    fi
    
    echo "========================================"
    echo ""
    log_info "Tunnel name: $tunnel_name"
    log_info "Use 'tunnel.sh log' to view full logs"
    log_info "Use 'tunnel.sh status' to check status"
}

cmd_stop() {
    log_info "Stopping VS Code Tunnel..."
    
    local pid=$(get_tunnel_pid)
    
    if [ -z "$pid" ]; then
        log_warn "No running tunnel found"
        exit 0
    fi
    
    if kill "$pid" 2>/dev/null; then
        rm -f "$PID_FILE"
        log_success "Tunnel stopped (PID: $pid)"
    else
        log_error "Failed to stop, may lack permissions"
        exit 1
    fi
}

cmd_status() {
    echo ""
    echo "========================================"
    echo "        VS Code Tunnel Status"
    echo "========================================"
    
    local pid=$(get_tunnel_pid)
    
    if [ -z "$pid" ]; then
        echo -e "Status: ${RED}Not running${NC}"
    else
        echo -e "Status: ${GREEN}Running${NC}"
        echo "PID: $pid"
        echo "CLI Directory: $CLI_DIR"
        echo "Log File: $LOG_FILE"
        
        # Show process info
        echo ""
        echo "Process Info:"
        ps -p "$pid" -o pid,vsz,rss,time,comm 2>/dev/null || echo "Unable to get process details"
    fi
    
    echo "========================================"
}

cmd_log() {
    if [ ! -f "$LOG_FILE" ]; then
        log_error "Log file not found: $LOG_FILE"
        log_info "Please start the tunnel first"
        exit 1
    fi
    
    log_info "Showing live logs (Ctrl+C to exit)..."
    echo ""
    tail -f "$LOG_FILE"
}

cmd_usage() {
    echo "
VS Code Tunnel Manager

Usage: tunnel.sh <command> [options]

Commands:
  start [name]    Start tunnel with optional name
  stop            Stop tunnel
  status          View running status
  log             View live logs

Environment Variables:
  VSCODE_TUNNEL_NAME  Tunnel name
  VSCODE_CLI_DIR      CLI directory (default: ~/.vscode-cli)

Examples:
  tunnel.sh start              # Interactive name input
  tunnel.sh start my-tunnel    # Specify name
  VSCODE_TUNNEL_NAME=dev tunnel.sh start  # Via env variable
"
}

# ==========================================
# Entry Point
# ==========================================
case "${1:-}" in
    start)
        cmd_start "$2"
        ;;
    stop)
        cmd_stop
        ;;
    status)
        cmd_status
        ;;
    log)
        cmd_log
        ;;
    -h|--help|help)
        cmd_usage
        ;;
    *)
        cmd_usage
        exit 1
        ;;
esac
