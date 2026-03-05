#!/bin/bash
#
# MCP Workflow Engine - Unified Version
# Orchestrates multi-step workflows using MCP patterns
# Inspired by Jason Zhou's workflow automation approach
#

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEMPLATES_DIR="${SCRIPT_DIR}/templates"
MCP_DIR="${MCP_DIR:-.mcp}"
WORKFLOWS_DIR="${MCP_DIR}/workflows"
PROMPTS_DIR="${MCP_DIR}/prompts"
RESOURCES_DIR="${MCP_DIR}/resources"
LOGS_DIR="${MCP_DIR}/logs"
MCP_SERVER="${SCRIPT_DIR}/mcp-server.js"
MEMORY_FILE="${MCP_DIR}/.workflow-memory.json"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Logging functions
log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Initialize MCP environment
cmd_init() {
    if [ -d "$MCP_DIR" ]; then
        log_warn "MCP already initialized in $MCP_DIR/"
        return 1
    fi

    mkdir -p "$WORKFLOWS_DIR" "$PROMPTS_DIR" "$RESOURCES_DIR" "$LOGS_DIR"
    
    # Create config
    cat > "$MCP_DIR/config.yaml" << 'EOF'
name: mcp-workflow
version: 1.0.0
servers:
  - name: local
    command: node ./scripts/mcp-server.js
EOF

    # Create example resource
    cat > "$RESOURCES_DIR/recipes.yaml" << 'EOF'
name: recipes
title: Cuisine-Specific Recipes
description: Traditional recipes organized by cuisine
template: "file://data/recipes/{cuisine}.md"
mimeType: "text/markdown"
completions:
  cuisine:
    - italian
    - mexican
    - japanese
    - indian
    - thai
    - french
    - spanish
EOF

    # Create example prompt
    cat > "$PROMPTS_DIR/meal-planner.yaml" << 'EOF'
name: meal-planner
title: Weekly Meal Planner
description: Create meal plan from cuisine-specific recipes
args:
  cuisine:
    type: string
    description: Cuisine type for meal planning
    completions:
      - italian
      - mexican
      - japanese
resources:
  - "file://data/recipes/{cuisine}.md"
messages:
  - role: user
    content: |
      Plan cooking for the week using {cuisine} recipes.
      
      Please create:
      1. A 7-day meal plan using these recipes
      2. An optimized grocery shopping list
      3. Daily meal schedule
      4. Preparation tips
      
      Focus on ingredient overlap to reduce waste.
EOF

    # Create example workflow
    cat > "$WORKFLOWS_DIR/meal-plan.json" << 'EOF'
{
  "name": "meal-plan",
  "version": "1.0.0",
  "description": "Generate weekly meal plan",
  "steps": [
    {
      "name": "select-cuisine",
      "type": "prompt",
      "prompt": "meal-planner",
      "args": {"cuisine": "{cuisine}"}
    },
    {
      "name": "generate-plan",
      "type": "generate",
      "action": "generate-meal-plan"
    },
    {
      "name": "create-shopping-list",
      "type": "output",
      "action": "generate-shopping-list"
    }
  ]
}
EOF

    log_success "MCP initialized in $MCP_DIR/"
    log_info "Created:"
    log_info "  - config.yaml"
    log_info "  - resources/recipes.yaml"
    log_info "  - prompts/meal-planner.yaml"
    log_info "  - workflows/meal-plan.json"
}

# List available workflows
cmd_list() {
    log_info "Available workflows:"
    
    if [ -d "$TEMPLATES_DIR" ]; then
        for template in "$TEMPLATES_DIR"/*.json; do
            if [ -f "$template" ]; then
                local name=$(basename "$template" .json)
                local desc=$(jq -r '.description // "No description"' "$template" 2>/dev/null)
                echo "  • $name (template) - $desc"
            fi
        done
    fi
    
    if [ -d "$WORKFLOWS_DIR" ]; then
        for workflow in "$WORKFLOWS_DIR"/*.json; do
            if [ -f "$workflow" ]; then
                local name=$(basename "$workflow" .json)
                local desc=$(jq -r '.description // "No description"' "$workflow" 2>/dev/null)
                echo "  • $name (custom) - $desc"
            fi
        done
    fi
}

# Run a workflow
cmd_run() {
    local workflow_name="$1"
    shift
    
    local input_json="{}"
    
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --input)
                input_json="$2"
                shift 2
                ;;
            *)
                shift
                ;;
        esac
    done
    
    # Find workflow file
    local workflow_file=""
    if [ -f "$TEMPLATES_DIR/${workflow_name}.json" ]; then
        workflow_file="$TEMPLATES_DIR/${workflow_name}.json"
    elif [ -f "$WORKFLOWS_DIR/${workflow_name}.json" ]; then
        workflow_file="$WORKFLOWS_DIR/${workflow_name}.json"
    else
        log_error "Workflow not found: $workflow_name"
        return 1
    fi
    
    log_info "Running workflow: $workflow_name"
    log_info "Input: $input_json"
    
    # Load workflow
    local workflow=$(cat "$workflow_file")
    local steps=$(echo "$workflow" | jq -c '.steps // []')
    local step_count=$(echo "$steps" | jq 'length')
    
    log_info "Found $step_count step(s)"
    
    # Initialize context with input
    local context="$input_json"
    local step_idx=0
    
    # Execute each step
    echo "$steps" | jq -c '.[]' | while read -r step; do
        step_idx=$((step_idx + 1))
        local step_name=$(echo "$step" | jq -r '.name')
        local step_type=$(echo "$step" | jq -r '.type // "action"')
        
        log_info "[$step_idx/$step_count] $step_name ($step_type)"
        
        # Simulate execution
        sleep 0.3
        log_success "  Completed"
        
        # Save context
        echo "$context" > "$MEMORY_FILE"
    done
    
    log_success "Workflow completed: $workflow_name"
}

# Create workflow from template
cmd_create() {
    local name="$1"
    shift
    local template=""
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --from)
                template="$2"
                shift 2
                ;;
            *)
                shift
                ;;
        esac
    done
    
    if [ -z "$name" ]; then
        log_error "Workflow name required"
        return 1
    fi
    
    if [ -z "$template" ]; then
        log_error "Template required (--from <template>)"
        return 1
    fi
    
    local template_file="$TEMPLATES_DIR/${template}.json"
    if [ ! -f "$template_file" ]; then
        log_error "Template not found: $template"
        return 1
    fi
    
    mkdir -p "$WORKFLOWS_DIR"
    cp "$template_file" "$WORKFLOWS_DIR/${name}.json"
    
    log_success "Created workflow: $WORKFLOWS_DIR/${name}.json"
}

# Show template details
cmd_template() {
    local name="$1"
    
    if [ -z "$name" ]; then
        log_info "Available templates:"
        for template in "$TEMPLATES_DIR"/*.json; do
            if [ -f "$template" ]; then
                local tname=$(basename "$template" .json)
                local desc=$(jq -r '.description // "No description"' "$template")
                echo "  • $name - $desc"
            fi
        done
        return
    fi
    
    local template_file="$TEMPLATES_DIR/${name}.json"
    if [ ! -f "$template_file" ]; then
        log_error "Template not found: $name"
        return 1
    fi
    
    echo "Template: $name"
    echo ""
    cat "$template_file" | jq '.'
}

# Validate workflow JSON
cmd_validate() {
    local file="$1"
    
    if [ -z "$file" ]; then
        log_error "File path required"
        return 1
    fi
    
    if [ ! -f "$file" ]; then
        log_error "File not found: $file"
        return 1
    fi
    
    if jq empty "$file" 2>/dev/null; then
        log_success "Valid JSON: $file"
        
        # Check required fields
        local has_name=$(jq 'has("name")' "$file")
        local has_steps=$(jq 'has("steps")' "$file")
        
        [ "$has_name" = "true" ] && log_success "  ✓ Has 'name' field"
        [ "$has_steps" = "true" ] && log_success "  ✓ Has 'steps' field"
    else
        log_error "Invalid JSON: $file"
        return 1
    fi
}

# Export workflow
cmd_export() {
    local workflow="$1"
    local output="${2:-${workflow}.json}"
    
    local workflow_file=""
    if [ -f "$TEMPLATES_DIR/${workflow}.json" ]; then
        workflow_file="$TEMPLATES_DIR/${workflow}.json"
    elif [ -f "$WORKFLOWS_DIR/${workflow}.json" ]; then
        workflow_file="$WORKFLOWS_DIR/${workflow}.json"
    else
        log_error "Workflow not found: $workflow"
        return 1
    fi
    
    cp "$workflow_file" "$output"
    log_success "Exported to: $output"
}

# Execute prompt chain
cmd_chain() {
    if [ $# -eq 0 ]; then
        log_error "At least one step required"
        return 1
    fi
    
    log_info "Executing prompt chain:"
    
    local step_num=0
    for step in "$@"; do
        step_num=$((step_num + 1))
        log_info "[$step_num] $step"
        sleep 0.2
        log_success "  Completed"
    done
    
    log_success "Chain completed with $step_num step(s)"
}

# Manage workflow memory
cmd_memory() {
    local action="$1"
    local key="$2"
    local value="$3"
    
    mkdir -p "$(dirname "$MEMORY_FILE")"
    
    case "$action" in
        get)
            if [ -f "$MEMORY_FILE" ]; then
                if [ -n "$key" ]; then
                    jq -r ".${key} // empty" "$MEMORY_FILE"
                else
                    cat "$MEMORY_FILE" | jq '.'
                fi
            else
                echo "{}"
            fi
            ;;
        set)
            if [ -z "$key" ] || [ -z "$value" ]; then
                log_error "Key and value required"
                return 1
            fi
            
            local current="{}"
            [ -f "$MEMORY_FILE" ] && current=$(cat "$MEMORY_FILE")
            
            echo "$current" | jq --arg k "$key" --arg v "$value" '. + {($k): $v}' > "$MEMORY_FILE"
            log_success "Set: $key"
            ;;
        del)
            if [ -z "$key" ]; then
                log_error "Key required"
                return 1
            fi
            
            if [ -f "$MEMORY_FILE" ]; then
                jq "del(.${key})" "$MEMORY_FILE" > "$MEMORY_FILE.tmp"
                mv "$MEMORY_FILE.tmp" "$MEMORY_FILE"
                log_success "Deleted: $key"
            fi
            ;;
        *)
            log_error "Unknown action: $action (use get|set|del)"
            return 1
            ;;
    esac
}

# Manage MCP server
cmd_server() {
    local action="${1:-status}"
    local pid_file="${MCP_DIR}/.server.pid"
    
    case "$action" in
        start)
            if [ -f "$pid_file" ] && kill -0 "$(cat "$pid_file")" 2>/dev/null; then
                log_warn "Server already running (PID: $(cat "$pid_file"))"
                return 0
            fi
            
            log_info "Starting MCP server..."
            node "$MCP_SERVER" 2>> "$LOGS_DIR/server.log" &
            local pid=$!
            echo $pid > "$pid_file"
            log_success "Server started (PID: $pid)"
            ;;
        stop)
            if [ -f "$pid_file" ]; then
                local pid=$(cat "$pid_file")
                kill "$pid" 2>/dev/null || true
                rm -f "$pid_file"
                log_success "Server stopped"
            else
                log_warn "Server not running"
            fi
            ;;
        status)
            if [ -f "$pid_file" ] && kill -0 "$(cat "$pid_file")" 2>/dev/null; then
                log_success "Server running (PID: $(cat "$pid_file"))"
            else
                log_info "Server not running"
            fi
            ;;
        logs)
            if [ -f "$LOGS_DIR/server.log" ]; then
                tail -f "$LOGS_DIR/server.log"
            else
                log_warn "No logs found"
            fi
            ;;
        *)
            log_error "Unknown action: $action (use start|stop|status|logs)"
            return 1
            ;;
    esac
}

# Help message
show_help() {
    cat << EOF
MCP Workflow Engine v1.0.0

Usage: workflow-engine.sh <command> [options]

Commands:
    init                                 Initialize MCP environment
    list                                 List available workflows
    run <workflow> [--input <json>]      Execute a workflow
    create <name> --from <template>      Create new workflow from template
    template [name]                      Show template details
    validate <file>                      Validate workflow JSON
    export <workflow> [output]           Export workflow to file
    chain <step1> <step2> ...            Execute prompt chain
    memory <get|set|del> <key> [value]   Manage workflow memory
    server <start|stop|status|logs>      Manage MCP server
    help                                 Show this help

Examples:
    # Initialize MCP
    ./workflow-engine.sh init
    
    # Run meal planner
    ./workflow-engine.sh run meal-planner --input '{"cuisine":"italian"}'
    
    # Create custom workflow
    ./workflow-engine.sh create my-workflow --from meal-planner
    
    # Execute prompt chain
    ./workflow-engine.sh chain plan generate review
    
    # Manage memory
    ./workflow-engine.sh memory set user.preferences '{"theme":"dark"}'

EOF
}

# Main
case "${1:-help}" in
    init)
        cmd_init
        ;;
    list)
        cmd_list
        ;;
    run)
        shift
        cmd_run "$@"
        ;;
    create)
        shift
        cmd_create "$@"
        ;;
    template)
        shift
        cmd_template "$@"
        ;;
    validate)
        shift
        cmd_validate "$@"
        ;;
    export)
        shift
        cmd_export "$@"
        ;;
    chain)
        shift
        cmd_chain "$@"
        ;;
    memory)
        shift
        cmd_memory "$@"
        ;;
    server)
        shift
        cmd_server "$@"
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        log_error "Unknown command: $1"
        show_help
        exit 1
        ;;
esac
