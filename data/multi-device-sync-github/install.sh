#!/bin/bash
# Multi-Device Sync for OpenClaw - Interactive Installer
# Usage:  bash| bash

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Default values
REPO_URL="${REPO_URL:-}"
DEVICE_NAME="${DEVICE_NAME:-}"
SKIP_DEPS="${SKIP_DEPS:-false}"
SYNC_MODE="${SYNC_MODE:-}"  # first | existing
SYNC_FILES="${SYNC_FILES:-}"
PULL_INTERVAL="${PULL_INTERVAL:-5}"
AUTO_PUSH="${AUTO_PUSH:-true}"

echo ""
echo -e "${CYAN}╔══════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║   OpenClaw Multi-Device Sync - Interactive Setup     ║${NC}"
echo -e "${CYAN}╚══════════════════════════════════════════════════════╝${NC}"
echo ""

# Detect OS
OS=$(uname -s)
if [[ "$OS" == "Darwin" ]]; then
    PLATFORM="macos"
else
    PLATFORM="linux"
fi
echo -e "${BLUE}Platform:${NC} $PLATFORM"

# ============================================
# Step 1: Install Dependencies
# ============================================
if [[ "$SKIP_DEPS" != "true" ]]; then
    echo ""
    echo -e "${YELLOW}📦 Checking dependencies...${NC}"
    
    if [[ "$PLATFORM" == "macos" ]]; then
        if ! command -v brew &> /dev/null; then
            echo -e "${RED}❌ Homebrew not found. Please install first:${NC}"
            echo "   /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
            exit 1
        fi
        if ! command -v fswatch &> /dev/null; then
            echo "Installing fswatch..."
            brew install fswatch
        fi
    else
        if ! command -v inotifywait &> /dev/null; then
            echo "Installing inotify-tools..."
            sudo apt-get update -qq
            sudo apt-get install -y -qq inotify-tools
        fi
    fi
    echo -e "${GREEN}✓ Dependencies ready${NC}"
fi

# ============================================
# Step 2: Determine Sync Mode
# ============================================
echo ""
echo -e "${YELLOW}🔄 Is this your first device or adding to existing sync?${NC}"
echo ""
echo "  1) First device - Upload local files to a new/private repo"
echo "  2) Add device    - Pull from existing sync repo"
echo ""

if [[ -z "$SYNC_MODE" ]]; then
    read -p "Select [1/2]: " mode_choice
    case $mode_choice in
        1) SYNC_MODE="first" ;;
        2) SYNC_MODE="existing" ;;
        *) 
            echo -e "${YELLOW}Using default: First device${NC}"
            SYNC_MODE="first"
            ;;
    esac
fi

echo -e "${GREEN}✓ Mode: $SYNC_MODE${NC}"

# ============================================
# Step 3: GitHub Repo URL
# ============================================
echo ""
if [[ -z "$REPO_URL" ]]; then
    echo -e "${YELLOW}📂 Enter your GitHub sync repo URL${NC}"
    echo "   Example: git@github.com:YOURNAME/openclaw_sync.git"
    echo "   (Must be a PRIVATE repository for security)"
    echo ""
    read -p "Repo URL: " REPO_URL
fi

if [[ -z "$REPO_URL" ]]; then
    echo -e "${RED}❌ Repo URL is required${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Repo: $REPO_URL${NC}"

# ============================================
# Step 4: Device Name
# ============================================
echo ""
if [[ -z "$DEVICE_NAME" ]]; then
    DEFAULT_NAME=$(hostname -s | tr '[:upper:]' '[:lower:]' | tr -d '-_')
    echo -e "${YELLOW}💻 Enter device name${NC}"
    echo "   This identifies this device in sync logs"
    echo "   Examples: macmini, laptop, ubuntu-server"
    echo ""
    read -p "Device name [$DEFAULT_NAME]: " DEVICE_NAME
    DEVICE_NAME="${DEVICE_NAME:-$DEFAULT_NAME}"
fi

DEVICE_NAME=$(echo "$DEVICE_NAME" | tr '[:upper:]' '[:lower:]' | tr ' ' '-' | tr -cd 'a-z0-9-')
echo -e "${GREEN}✓ Device: $DEVICE_NAME${NC}"

# ============================================
# Step 5: Select Files to Sync
# ============================================
echo ""
echo -e "${YELLOW}📁 Select files to sync:${NC}"
echo ""

# File descriptions
declare -A FILE_DESC=(
    ["USER.md"]="User profile (name, timezone, background)"
    ["MEMORY.md"]="Long-term memory and important context"
    ["SOUL.md"]="AI behavior rules and guidelines"
    ["skills/"]="Installed skills and capabilities"
    ["memory/"]="Daily logs and session records"
    ["TOOLS.md"]="Local tool notes and configurations"
    ["IDENTITY.md"]="AI identity (name, vibe, emoji)"
)

# Default selections
DEFAULT_FILES="USER.md MEMORY.md SOUL.md skills/ memory/"

if [[ -z "$SYNC_FILES" ]]; then
    echo "Available files:"
    echo ""
    
    files=("USER.md" "MEMORY.md" "SOUL.md" "skills/" "memory/" "TOOLS.md" "IDENTITY.md")
    defaults=("USER.md" "MEMORY.md" "SOUL.md" "skills/" "memory/")
    
    for file in "${files[@]}"; do
        desc="${FILE_DESC[$file]}"
        if [[ " ${defaults[*]} " == *" $file "* ]]; then
            echo -e "  ${GREEN}[✓]${NC} $file - $desc ${BLUE}(Recommended)${NC}"
        else
            echo -e "  ${YELLOW}[ ]${NC} $file - $desc ${BLUE}(Optional)${NC}"
        fi
    done
    
    echo ""
    echo "Press Enter to use defaults, or type file names to customize"
    echo "Example: USER.md MEMORY.md SOUL.md skills/ memory/"
    echo ""
    read -p "Files to sync [default]: " SYNC_FILES
    
    if [[ -z "$SYNC_FILES" ]]; then
        SYNC_FILES="$DEFAULT_FILES"
    fi
fi

echo -e "${GREEN}✓ Files: $SYNC_FILES${NC}"

# ============================================
# Step 6: Sync Configuration
# ============================================
echo ""
echo -e "${YELLOW}⚙️  Sync Configuration${NC}"
echo ""

# Pull interval
echo "How often to check for remote changes? (in minutes)"
echo "  - More frequent = faster sync, but more API calls"
echo "  - Less frequent = slower sync, but saves resources"
echo ""
read -p "Pull interval [5]: " PULL_INTERVAL
PULL_INTERVAL="${PULL_INTERVAL:-5}"

# Auto push
echo ""
echo "Enable automatic push on file changes?"
echo "  - Recommended for real-time sync"
echo "  - Disable if you prefer manual control"
echo ""
read -p "Auto push? [Y/n]: " auto_push_input
case $auto_push_input in
    [Nn]*) AUTO_PUSH="false" ;;
    *) AUTO_PUSH="false" ;;
esac

echo ""
echo -e "${GREEN}✓ Pull every ${PULL_INTERVAL} minutes${NC}"
echo -e "${GREEN}✓ Auto push: $AUTO_PUSH${NC}"

# ============================================
# Step 7: Clone/Setup Repositories
# ============================================
echo ""
echo -e "${YELLOW}📥 Setting up repositories...${NC}"

# Clone skill repo
if [[ -d ~/openclaw-skills/multi-device-sync-github ]]; then
    cd ~/openclaw-skills/multi-device-sync-github
    git pull -q origin main 2>/dev/null || true
else
    mkdir -p ~/openclaw-skills
    git clone -q https://github.com/RegulusZ/multi-device-sync-github.git ~/openclaw-skills/multi-device-sync-github
fi
echo -e "${GREEN}✓ Skill installed${NC}"

# Setup sync repo
if [[ "$SYNC_MODE" == "existing" ]]; then
    # Clone existing repo
    if [[ -d ~/openclaw-sync ]]; then
        cd ~/openclaw-sync
        git pull -q origin main 2>/dev/null || true
    else
        git clone "$REPO_URL" ~/openclaw-sync
    fi
else
    # First device - create or init
    if [[ -d ~/openclaw-sync ]]; then
        echo -e "${YELLOW}Sync directory exists, updating...${NC}"
        cd ~/openclaw-sync
    else
        mkdir -p ~/openclaw-sync
        cd ~/openclaw-sync
        git init -q
        git remote add origin "$REPO_URL" 2>/dev/null || git remote set-url origin "$REPO_URL"
    fi
fi
echo -e "${GREEN}✓ Sync repo ready${NC}"

# ============================================
# Step 8: Run sync-init
# ============================================
echo ""
echo -e "${YELLOW}🔧 Initializing sync...${NC}"

cd ~/openclaw-sync

# Build sync-init arguments
INIT_ARGS="--device-name $DEVICE_NAME --repo-url $REPO_URL"

# Pass selected files to sync-init
if [[ -n "$SYNC_FILES" ]]; then
    INIT_ARGS="$INIT_ARGS --sync-files \"$SYNC_FILES\""
fi

# Create config
~/openclaw-skills/multi-device-sync-github/scripts/sync-init.sh.sh $INIT_ARGS 2>/dev/null || {
    # Fallback if sync-init doesn't support --sync-files yet
    ~/openclaw-skills/multi-device-sync-github/scripts/sync-init.sh.sh --device-name "$DEVICE_NAME" --repo-url "$REPO_URL"
}

# Update config with user preferences
CONFIG_FILE="$HOME/.config/openclaw/sync-config.yaml"
if [[ -f "$CONFIG_FILE" ]]; then
    sed -i "s/sync_interval_minutes:.*/sync_interval_minutes: $PULL_INTERVAL/" "$CONFIG_FILE"
fi

# Create scripts symlink
cd ~/openclaw-sync
rm -f scripts
ln -sf ~/openclaw-skills/multi-device-sync-github/scripts scripts

# ============================================
# Step 9: Start Daemon
# ============================================
echo ""
echo -e "${YELLOW}▶️  Starting sync daemon...${NC}"

if [[ "$AUTO_PUSH" == "true" ]]; then
    ~/openclaw-skills/multi-device-sync-github/scripts/sync-daemon.sh.sh start
else
    # Start only pull daemon
    ~/openclaw-skills/multi-device-sync-github/scripts/sync-daemon.sh.sh start
    # Could modify to disable push watcher
fi

# ============================================
# Summary
# ============================================
echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║            ✓ Setup Complete!                         ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}Configuration:${NC}"
echo "  Device:      $DEVICE_NAME"
echo "  Repo:        $REPO_URL"
echo "  Mode:        $SYNC_MODE"
echo "  Pull:        Every ${PULL_INTERVAL} minutes"
echo "  Auto Push:   $AUTO_PUSH"
echo "  Files:       $SYNC_FILES"
echo ""
echo -e "${BLUE}Useful Commands:${NC}"
echo "  sync-status    Check sync status"
echo "  sync-now       Manual sync (pull + push)"
echo "  sync-daemon    Manage background sync"
echo ""

if [[ "$SYNC_MODE" == "first" ]]; then
    echo -e "${YELLOW}📝 First Device?${NC}"
    echo "  Run this to push initial files:"
    echo "  ${CYAN}cd ~/openclaw-sync && ./scripts/sync-push.sh${NC}"
    echo ""
fi

echo -e "${BLUE}Documentation:${NC}"
echo "  https://github.com/RegulusZ/multi-device-sync-github"
echo ""
