#!/bin/bash
# Mediator CLI - Emotional firewall for difficult contacts
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="${HOME}/.clawdbot/mediator.yaml"
LOG_FILE="${HOME}/.clawdbot/logs/mediator.log"

# Ensure log directory exists
mkdir -p "$(dirname "$LOG_FILE")"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" >> "$LOG_FILE"
}

usage() {
    cat <<EOF
Mediator - Emotional firewall for difficult contacts

Usage: mediator.sh <command> [options]

Commands:
  init                    Initialize config file
  add <name>              Add a contact to mediate
      --email <addr>      Contact's email address
      --phone <num>       Contact's phone number  
      --channels <list>   Comma-separated: email,imessage
      --mode <mode>       intercept | assist (default: intercept)
      --summarize <type>  facts-only | neutral | full (default: facts-only)
      --respond <type>    draft | auto (default: draft)
  remove <name>           Remove a contact
  list                    List configured contacts
  check                   Process any new messages from configured contacts
  process <type> <id>     Process a specific message (email|imessage)
  status                  Show mediator status

Examples:
  mediator.sh init
  mediator.sh add "Ex Partner" --email ex@email.com --phone +15551234567 --channels email,imessage
  mediator.sh check
  mediator.sh list
EOF
}

cmd_init() {
    if [[ -f "$CONFIG_FILE" ]]; then
        echo "Config already exists at $CONFIG_FILE"
        exit 0
    fi
    
    mkdir -p "$(dirname "$CONFIG_FILE")"
    cat > "$CONFIG_FILE" <<'YAML'
mediator:
  # Global settings
  archive_originals: true
  notify_channel: telegram  # Where to send summaries
  
  # Gmail accounts to monitor
  gmail_accounts:
    - dylan.turner22@gmail.com
    - dylan@doxy.me
  
  contacts: []
  # Example contact:
  # - name: "Difficult Person"
  #   email: "them@email.com"
  #   phone: "+15551234567"
  #   channels: [email, imessage]
  #   mode: intercept
  #   summarize: facts-only
  #   respond: draft
YAML
    echo "Created config at $CONFIG_FILE"
    log "Initialized mediator config"
}

cmd_add() {
    local name="$1"
    shift
    
    local email="" phone="" channels="email" mode="intercept" summarize="facts-only" respond="draft"
    
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --email) email="$2"; shift 2 ;;
            --phone) phone="$2"; shift 2 ;;
            --channels) channels="$2"; shift 2 ;;
            --mode) mode="$2"; shift 2 ;;
            --summarize) summarize="$2"; shift 2 ;;
            --respond) respond="$2"; shift 2 ;;
            *) echo "Unknown option: $1"; exit 1 ;;
        esac
    done
    
    if [[ -z "$name" ]]; then
        echo "Error: Contact name required"
        exit 1
    fi
    
    if [[ -z "$email" && -z "$phone" ]]; then
        echo "Error: At least one of --email or --phone required"
        exit 1
    fi
    
    # Use Python to safely add to YAML
    python3 "$SCRIPT_DIR/config-helper.py" add \
        --name "$name" \
        --email "$email" \
        --phone "$phone" \
        --channels "$channels" \
        --mode "$mode" \
        --summarize "$summarize" \
        --respond "$respond"
    
    log "Added contact: $name (email=$email, phone=$phone, channels=$channels)"
    echo "Added contact: $name"
}

cmd_remove() {
    local name="$1"
    if [[ -z "$name" ]]; then
        echo "Error: Contact name required"
        exit 1
    fi
    
    python3 "$SCRIPT_DIR/config-helper.py" remove --name "$name"
    log "Removed contact: $name"
    echo "Removed contact: $name"
}

cmd_list() {
    python3 "$SCRIPT_DIR/config-helper.py" list
}

cmd_check() {
    log "Running mediator check"
    
    # Check emails
    python3 "$SCRIPT_DIR/process-email.py" check
    
    # Check iMessages (if any contacts have imessage channel)
    python3 "$SCRIPT_DIR/process-imessage.py" check
    
    log "Mediator check complete"
}

cmd_status() {
    echo "=== Mediator Status ==="
    echo ""
    
    if [[ ! -f "$CONFIG_FILE" ]]; then
        echo "Not initialized. Run: mediator.sh init"
        exit 0
    fi
    
    echo "Config: $CONFIG_FILE"
    echo "Log: $LOG_FILE"
    echo ""
    
    cmd_list
    
    echo ""
    echo "Recent activity:"
    tail -5 "$LOG_FILE" 2>/dev/null || echo "(no recent activity)"
}

# Main
case "${1:-}" in
    init) cmd_init ;;
    add) shift; cmd_add "$@" ;;
    remove) shift; cmd_remove "$@" ;;
    list) cmd_list ;;
    check) cmd_check ;;
    status) cmd_status ;;
    -h|--help|"") usage ;;
    *) echo "Unknown command: $1"; usage; exit 1 ;;
esac
