#!/bin/bash
# 🧠 Configuration loader for bash scripts
# Source this file to load config variables

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Check if config.json exists, otherwise use example
CONFIG_FILE="$SCRIPT_DIR/config.json"
if [[ ! -f "$CONFIG_FILE" ]]; then
    CONFIG_FILE="$SCRIPT_DIR/config.example.json"
    echo "⚠️  Using config.example.json - copy to config.json and customize!" >&2
fi

if [[ ! -f "$CONFIG_FILE" ]]; then
    echo "❌ No config file found! Create config.json from config.example.json" >&2
    exit 1
fi

# Extract config values using Python (most portable way)
get_config() {
    local key="$1"
    local default="$2"
    python3 -c "
import json, sys
try:
    with open('$CONFIG_FILE') as f:
        config = json.load(f)
    keys = '$key'.split('.')
    value = config
    for k in keys:
        value = value[k]
    print(value)
except:
    if '$default':
        print('$default')
    else:
        sys.exit(1)
"
}

# Load commonly used config values
HUMAN_NAME=$(get_config "human.name" "Human")
AGENT_NAME=$(get_config "agent.name" "Agent")
AGENT_EMOJI=$(get_config "agent.emoji" "🤖")
DATA_DIR=$(get_config "system.data_dir" "$SCRIPT_DIR")
TELEGRAM_TARGET=$(get_config "human.telegram_target" "@human")
TIMEZONE=$(get_config "human.timezone" "UTC")
GIT_EMAIL=$(get_config "agent.git_email" "agent@openclaw.local")
GIT_NAME=$(get_config "agent.git_name" "Agent")

# Expand ~ in DATA_DIR if present
DATA_DIR="${DATA_DIR/#\~/$HOME}"

# Export for use in other scripts
export HUMAN_NAME AGENT_NAME AGENT_EMOJI DATA_DIR TELEGRAM_TARGET TIMEZONE GIT_EMAIL GIT_NAME