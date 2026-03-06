#!/bin/bash
# 04-install-subagents.sh
# Installs dev team subagents to ~/.claude/agents/

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"

# Source config for valid models and agent lists
if [[ -f "$SKILL_DIR/config.sh" ]]; then
    source "$SKILL_DIR/config.sh"
fi

# Parse arguments
DRY_RUN=0
INSTALL_MODE="${INSTALL_MODE:-starter}"  # Default from config or "starter"

while [[ $# -gt 0 ]]; do
    case $1 in
        --dry-run|-n)
            DRY_RUN=1
            shift
            ;;
        --minimal|--starter)
            INSTALL_MODE="starter"
            shift
            ;;
        --full-team|--all)
            INSTALL_MODE="full"
            shift
            ;;
        --help|-h)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --dry-run, -n      Show what would be done without making changes"
            echo "  --minimal          Install starter pack only (3 core agents) [default]"
            echo "  --full-team        Install all 11 dev team agents"
            echo "  --help, -h         Show this help message"
            echo ""
            echo "Starter pack: senior-dev, project-manager, junior-dev"
            echo "Full team adds: frontend-dev, backend-dev, ai-engineer, ml-engineer,"
            echo "                data-scientist, data-engineer, product-manager"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Set agent list based on mode
if [[ "$INSTALL_MODE" == "full" ]]; then
    AGENTS_TO_INSTALL=("${FULL_TEAM_AGENTS[@]:-senior-dev project-manager junior-dev frontend-dev backend-dev ai-engineer ml-engineer data-scientist data-engineer product-manager}")
    echo "📦 Installing FULL TEAM (${#AGENTS_TO_INSTALL[@]} agents)"
else
    AGENTS_TO_INSTALL=("${STARTER_AGENTS[@]:-senior-dev project-manager junior-dev}")
    echo "📦 Installing STARTER PACK (${#AGENTS_TO_INSTALL[@]} agents)"
    echo "   (Use --full-team for all 11 agents)"
fi

# Valid Claude Code model names (from config.sh or defaults)
if [[ ${#VALID_MODELS[@]} -eq 0 ]]; then
    VALID_MODELS=("sonnet" "haiku" "opus" "claude-sonnet-4-5" "claude-haiku-3-5" "claude-opus-4")
fi

# Function to validate model name in agent config
validate_model() {
    local model="$1"
    local agent_file="$2"
    
    # Check if model is in valid list
    for valid in "${VALID_MODELS[@]}"; do
        if [[ "$model" == "$valid" ]]; then
            return 0
        fi
    done
    
    echo "⚠️  Warning: Invalid model '$model' in $(basename "$agent_file")"
    echo "   Valid models: ${VALID_MODELS[*]}"
    return 1
}
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
AGENTS_SRC="$SKILL_DIR/agents"
AGENTS_DEST="$HOME/.claude/agents"

if [[ $DRY_RUN -eq 1 ]]; then
    echo "🤖 Installing Dev Team Subagents (DRY RUN)"
else
    echo "🤖 Installing Dev Team Subagents"
fi
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check source exists
if [[ ! -d "$AGENTS_SRC" ]]; then
    echo "❌ Agents source directory not found: $AGENTS_SRC"
    exit 1
fi

# Create destination
if [[ $DRY_RUN -eq 0 ]]; then
    mkdir -p "$AGENTS_DEST"
fi
echo "📁 Target: $AGENTS_DEST"
echo ""

# Count agents
AGENT_COUNT=$(ls -1 "$AGENTS_SRC"/*.md 2>/dev/null | wc -l | tr -d ' ')
echo "📦 Found $AGENT_COUNT subagents to install"
echo ""

# Install each agent
INSTALLED=0
SKIPPED=0
UPDATED=0

VALIDATION_ERRORS=0

for agent_file in "$AGENTS_SRC"/*.md; do
    if [[ ! -f "$agent_file" ]]; then
        continue
    fi
    
    filename=$(basename "$agent_file")
    agent_basename="${filename%.md}"
    
    # Skip agents not in AGENTS_TO_INSTALL (if filtering enabled)
    if [[ ${#AGENTS_TO_INSTALL[@]} -gt 0 ]]; then
        skip=true
        for wanted in "${AGENTS_TO_INSTALL[@]}"; do
            if [[ "$agent_basename" == "$wanted" ]]; then
                skip=false
                break
            fi
        done
        if [[ "$skip" == "true" ]]; then
            continue
        fi
    fi
    dest_file="$AGENTS_DEST/$filename"
    
    # Extract agent name and model from file
    agent_name=$(grep -m1 "^name:" "$agent_file" | sed 's/name: *//' | tr -d '\r')
    agent_model=$(grep -m1 "^model:" "$agent_file" | sed 's/model: *//' | tr -d '\r')
    
    # Validate model name
    if [[ -n "$agent_model" ]]; then
        if ! validate_model "$agent_model" "$agent_file"; then
            VALIDATION_ERRORS=$((VALIDATION_ERRORS + 1))
        fi
    fi
    
    if [[ -f "$dest_file" ]]; then
        # Check if different
        if diff -q "$agent_file" "$dest_file" &>/dev/null; then
            echo "⏭️  $agent_name (unchanged)"
            SKIPPED=$((SKIPPED + 1))
        else
            if [[ $DRY_RUN -eq 1 ]]; then
                echo "🔄 $agent_name (would update)"
            else
                cp "$agent_file" "$dest_file"
                echo "🔄 $agent_name (updated)"
            fi
            UPDATED=$((UPDATED + 1))
        fi
    else
        if [[ $DRY_RUN -eq 1 ]]; then
            echo "✅ $agent_name (would install)"
        else
            cp "$agent_file" "$dest_file"
            echo "✅ $agent_name (installed)"
        fi
        INSTALLED=$((INSTALLED + 1))
    fi
done

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 Summary:"
echo "   Installed: $INSTALLED"
echo "   Updated:   $UPDATED"
echo "   Unchanged: $SKIPPED"
if [[ $VALIDATION_ERRORS -gt 0 ]]; then
    echo "   ⚠️  Model validation warnings: $VALIDATION_ERRORS"
fi
if [[ $DRY_RUN -eq 1 ]]; then
    echo ""
    echo "🔍 DRY RUN - No changes were made"
    echo "   Run without --dry-run to apply changes"
fi
echo ""

# List installed agents
echo "🤖 Installed Subagents:"
echo ""
printf "%-20s %-10s %s\n" "NAME" "MODEL" "DESCRIPTION"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

for agent_file in "$AGENTS_DEST"/*.md; do
    if [[ -f "$agent_file" ]]; then
        name=$(grep -m1 "^name:" "$agent_file" | sed 's/name: *//' | tr -d '\r')
        model=$(grep -m1 "^model:" "$agent_file" | sed 's/model: *//' | tr -d '\r')
        desc=$(grep -m1 "^description:" "$agent_file" | sed 's/description: *//' | cut -c1-45 | tr -d '\r')
        printf "%-20s %-10s %s...\n" "$name" "$model" "$desc"
    fi
done

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Subagents installed!"
echo ""
echo "Usage in Claude Code:"
echo "  /agents                    # List all agents"
echo "  Use the senior-dev agent to review this code"
echo "  Have project-manager create a timeline"
echo ""
echo "Next: ./05-setup-claude-mem.sh (optional)"
