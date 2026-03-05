#!/usr/bin/env bash
# ============================================================================
# Intrusive Thoughts — One-Command Setup
# GitHub Issue #15: One-Command ClawHub Installation
#
# Usage: ./setup.sh [--non-interactive] [--data-dir DIR]
#
# This script:
#   1. Checks Python 3.8+ is available
#   2. Creates data directories
#   3. Generates config.json from config.example.json (interactive or defaults)
#   4. Initializes data files
#   5. Validates the installation
#   6. Prints cron job setup instructions for OpenClaw
# ============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_EXAMPLE="$SCRIPT_DIR/config.example.json"
CONFIG="$SCRIPT_DIR/config.json"
NON_INTERACTIVE=false
DATA_DIR=""

# Parse args
while [[ $# -gt 0 ]]; do
    case $1 in
        --non-interactive) NON_INTERACTIVE=true; shift ;;
        --data-dir) DATA_DIR="$2"; shift 2 ;;
        -h|--help)
            echo "Usage: ./setup.sh [--non-interactive] [--data-dir DIR]"
            echo ""
            echo "Options:"
            echo "  --non-interactive  Use defaults, don't ask questions"
            echo "  --data-dir DIR     Override data directory"
            exit 0
            ;;
        *) echo "Unknown option: $1"; exit 1 ;;
    esac
done

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo ""
echo -e "${BLUE}🧠 Intrusive Thoughts — Setup${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 1. Check Python
echo -n "Checking Python 3.8+... "
if command -v python3 &>/dev/null; then
    PY_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    PY_MAJOR=$(echo "$PY_VERSION" | cut -d. -f1)
    PY_MINOR=$(echo "$PY_VERSION" | cut -d. -f2)
    if [[ "$PY_MAJOR" -ge 3 && "$PY_MINOR" -ge 8 ]]; then
        echo -e "${GREEN}✓${NC} Python $PY_VERSION"
    else
        echo -e "${RED}✗${NC} Python $PY_VERSION (need 3.8+)"
        exit 1
    fi
else
    echo -e "${RED}✗${NC} Python 3 not found"
    exit 1
fi

# 2. Check jq (optional but helpful)
echo -n "Checking jq... "
if command -v jq &>/dev/null; then
    echo -e "${GREEN}✓${NC} $(jq --version)"
else
    echo -e "${YELLOW}○${NC} Not found (optional, using python for JSON)"
fi

# 3. Generate config.json
if [[ -f "$CONFIG" ]]; then
    echo -e "\n${YELLOW}⚠ config.json already exists. Skipping config generation.${NC}"
    echo "  Delete it and re-run setup to regenerate."
else
    echo ""
    echo -e "${BLUE}Configuration${NC}"
    echo "━━━━━━━━━━━━━"

    if [[ "$NON_INTERACTIVE" == "true" ]]; then
        cp "$CONFIG_EXAMPLE" "$CONFIG"
        echo "Using default config (edit config.json to customize)"
    else
        # Read values interactively
        read -rp "Your name (default: Your Human): " HUMAN_NAME
        HUMAN_NAME="${HUMAN_NAME:-Your Human}"

        read -rp "Timezone (default: UTC): " TZ
        TZ="${TZ:-UTC}"

        read -rp "Agent name (default: Agent): " AGENT_NAME
        AGENT_NAME="${AGENT_NAME:-Agent}"

        read -rp "Agent emoji (default: 🦞): " AGENT_EMOJI
        AGENT_EMOJI="${AGENT_EMOJI:-🦞}"

        read -rp "Weather location (default: London, UK): " WEATHER_LOC
        WEATHER_LOC="${WEATHER_LOC:-London, UK}"

        read -rp "Morning mood time (default: 07:00): " MORNING_TIME
        MORNING_TIME="${MORNING_TIME:-07:00}"

        read -rp "Dashboard port (default: 3117): " DASH_PORT
        DASH_PORT="${DASH_PORT:-3117}"

        # Generate config using Python (no jq dependency)
        python3 -c "
import json
with open('$CONFIG_EXAMPLE') as f:
    cfg = json.load(f)

cfg['human']['name'] = '''$HUMAN_NAME'''
cfg['human']['timezone'] = '''$TZ'''
cfg['agent']['name'] = '''$AGENT_NAME'''
cfg['agent']['emoji'] = '''$AGENT_EMOJI'''
cfg['integrations']['weather']['location'] = '''$WEATHER_LOC'''
cfg['scheduling']['morning_mood_time'] = '''$MORNING_TIME'''
cfg['scheduling']['timezone'] = '''$TZ'''
cfg['system']['dashboard_port'] = int('''$DASH_PORT''')

with open('$CONFIG') as f2:
    pass  # just checking
" 2>/dev/null || true

        python3 << PYEOF
import json
with open("$CONFIG_EXAMPLE") as f:
    cfg = json.load(f)
cfg["human"]["name"] = "$HUMAN_NAME"
cfg["human"]["timezone"] = "$TZ"
cfg["agent"]["name"] = "$AGENT_NAME"
cfg["agent"]["emoji"] = "$AGENT_EMOJI"
cfg["integrations"]["weather"]["location"] = "$WEATHER_LOC"
cfg["scheduling"]["morning_mood_time"] = "$MORNING_TIME"
cfg["scheduling"]["timezone"] = "$TZ"
cfg["system"]["dashboard_port"] = int("$DASH_PORT")
with open("$CONFIG", "w") as f:
    json.dump(cfg, f, indent=2)
print("  Config saved to config.json")
PYEOF
    fi
fi

# 4. Create data directories
echo ""
echo -e "${BLUE}Initializing data directories${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

for dir in health memory_store wal buffer log journal evolution trust_store; do
    mkdir -p "$SCRIPT_DIR/$dir"
    echo -e "  ${GREEN}✓${NC} $dir/"
done

# 5. Initialize empty data files if they don't exist
echo ""
echo -e "${BLUE}Initializing data files${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━"

init_json() {
    local file="$1"
    local content="$2"
    if [[ ! -f "$SCRIPT_DIR/$file" ]]; then
        echo "$content" > "$SCRIPT_DIR/$file"
        echo -e "  ${GREEN}✓${NC} $file"
    else
        echo -e "  ${YELLOW}○${NC} $file (already exists)"
    fi
}

init_json "history.json" "[]"
init_json "mood_history.json" "[]"
init_json "streaks.json" "{}"
init_json "achievements_earned.json" "[]"
init_json "memory_store/episodic.json" "[]"
init_json "memory_store/semantic.json" "[]"
init_json "memory_store/procedural.json" "[]"
init_json "wal/current.json" "[]"
init_json "buffer/working_buffer.json" '{"active_items":[],"completed":[],"expired":[]}'
init_json "trust_store/trust_data.json" '{"trust_level":0.5,"action_categories":{},"history":[]}'
init_json "evolution/learnings.json" '{"version":1,"patterns":[],"weight_adjustments":{},"evolution_history":[]}'

# 6. Make scripts executable
echo ""
echo -n "Setting permissions... "
chmod +x "$SCRIPT_DIR"/*.sh "$SCRIPT_DIR"/*.py 2>/dev/null || true
echo -e "${GREEN}✓${NC}"

# 7. Validate installation
echo ""
echo -e "${BLUE}Validating installation${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━"
python3 "$SCRIPT_DIR/health_monitor.py" status

# 8. Print cron setup instructions
echo ""
echo -e "${BLUE}OpenClaw Cron Setup${NC}"
echo "━━━━━━━━━━━━━━━━━━━"
echo ""
echo "To enable autonomous behavior, add these cron jobs in OpenClaw:"
echo ""
echo -e "${YELLOW}Morning Mood Ritual (daily):${NC}"
echo '  Schedule: cron "0 7 * * *" (adjust time to preference)'
echo '  Payload: agentTurn'
echo '  Message: "Run the morning mood ritual. Read ~/Projects/intrusive-thoughts/SKILL.md for instructions."'
echo ""
echo -e "${YELLOW}Night Workshop (nightly, 03:00-07:00):${NC}"
echo '  Schedule: cron "17 3 * * *"'
echo '  Payload: agentTurn'
echo '  Message: "Night workshop session. Pick a thought from thoughts.json night category."'
echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}  ✅ Setup complete! Intrusive Thoughts is ready.${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "Next steps:"
echo "  1. Edit config.json to customize your setup"
echo "  2. Set up OpenClaw cron jobs (see above)"
echo "  3. Run './health_cli.sh status' to check health"
echo "  4. Run 'python3 dashboard.py' to start the dashboard"
echo ""
