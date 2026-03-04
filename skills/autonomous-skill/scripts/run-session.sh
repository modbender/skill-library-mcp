#!/bin/bash
#
# Autonomous Skill - Session Runner
# Executes Claude Code in headless mode with auto-continuation
#
# Usage:
#   ./run-session.sh "task description"
#   ./run-session.sh --task-name <name> --continue
#   ./run-session.sh --list
#   ./run-session.sh --help
#

set -euo pipefail

# Configuration
AUTO_CONTINUE_DELAY=3
MAX_TURNS_INIT=50
MAX_TURNS_EXEC=100

# Use CLAUDE_PLUGIN_ROOT or fallback to script directory
if [ -n "$CLAUDE_PLUGIN_ROOT" ]; then
    SKILL_DIR="${CLAUDE_PLUGIN_ROOT}/skills/autonomous-skill"
else
    SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
fi

# Task directory base (in project root)
AUTONOMOUS_DIR=".autonomous"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Print colored output
print_header() {
    echo -e "${BLUE}==========================================${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}==========================================${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${CYAN}ℹ $1${NC}"
}

# Show help
show_help() {
    echo "Autonomous Skill - Session Runner"
    echo ""
    echo "Usage:"
    echo "  $0 \"task description\"           Start new task (auto-generates name)"
    echo "  $0 --task-name <name> --continue Continue specific task"
    echo "  $0 --list                        List all tasks"
    echo "  $0 --help                        Show this help"
    echo ""
    echo "Options:"
    echo "  --task-name <name>       Specify task name explicitly"
    echo "  --continue, -c           Continue existing task"
    echo "  --no-auto-continue       Don't auto-continue after session"
    echo "  --max-sessions N         Limit to N sessions"
    echo "  --list                   List all existing tasks"
    echo ""
    echo "Examples:"
    echo "  $0 \"Build a REST API for todo app\""
    echo "  $0 --task-name build-rest-api --continue"
    echo "  $0 --list"
    echo ""
    echo "Task Directory: $AUTONOMOUS_DIR/<task-name>/"
    echo "Skill Directory: $SKILL_DIR"
    echo ""
}

# Generate task name from description
generate_task_name() {
    local desc="${1:-}"
    # Convert to lowercase, replace non-alphanumeric with hyphens, collapse multiple hyphens, trim
    local result
    result=$(echo "$desc" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/-/g' | sed 's/--*/-/g' | cut -c1-30 | sed 's/^-//' | sed 's/-$//')

    # If result is empty (description was non-ASCII or only special chars), use timestamp fallback
    if [ -z "$result" ]; then
        result="task-$(date +%Y%m%d-%H%M%S)"
        print_warning "Non-alphanumeric description detected, using generated name: $result"
    fi
    echo "$result"
}

# Validate task name (security: prevent path traversal)
validate_task_name() {
    local name="$1"
    # Reject if contains path traversal attempts or invalid characters
    if [[ "$name" == *".."* ]] || [[ "$name" == *"/"* ]] || [[ "$name" == *"\\"* ]]; then
        print_error "Invalid task name: '$name' (contains path traversal characters)"
        return 1
    fi
    # Reject if empty
    if [ -z "$name" ]; then
        print_error "Task name cannot be empty"
        return 1
    fi
    # Reject if starts with hyphen (could be confused with options)
    if [[ "$name" == -* ]]; then
        print_error "Task name cannot start with a hyphen"
        return 1
    fi
    return 0
}

# Verify required commands exist
check_dependencies() {
    if ! command -v claude &> /dev/null; then
        print_error "Required command 'claude' not found"
        echo "Please install Claude Code CLI: https://claude.ai/code"
        exit 1
    fi
}

# List all tasks
list_tasks() {
    print_header "AUTONOMOUS TASKS"

    if [ ! -d "$AUTONOMOUS_DIR" ]; then
        print_warning "No tasks found. Directory $AUTONOMOUS_DIR does not exist."
        echo ""
        return
    fi

    # Check if directory is empty (no subdirectories)
    local dir_count
    dir_count=$(find "$AUTONOMOUS_DIR" -mindepth 1 -maxdepth 1 -type d 2>/dev/null | wc -l)
    if [ "$dir_count" -eq 0 ]; then
        print_warning "No tasks found in $AUTONOMOUS_DIR/"
        echo ""
        return
    fi

    local found=0
    for task_dir in "$AUTONOMOUS_DIR"/*/; do
        # Skip if glob didn't match (empty directory case)
        [ -d "$task_dir" ] || continue

        local task_name
        task_name=$(basename "$task_dir")
        local task_list="$task_dir/task_list.md"

        if [ -f "$task_list" ]; then
            local total
            local done_count
            total=$(grep -c '^\- \[' "$task_list" 2>/dev/null || echo "0")
            done_count=$(grep -c '^\- \[x\]' "$task_list" 2>/dev/null || echo "0")

            # Safe percent calculation (avoid divide by zero)
            local percent=0
            if [ "$total" -gt 0 ]; then
                percent=$((done_count * 100 / total))
            fi

            if [ "$done_count" -eq "$total" ] && [ "$total" -gt 0 ]; then
                echo -e "  ${GREEN}✓${NC} $task_name ($done_count/$total - 100% complete)"
            else
                echo -e "  ${YELLOW}○${NC} $task_name ($done_count/$total - $percent%)"
            fi
            found=$((found + 1))
        else
            echo -e "  ${RED}?${NC} $task_name (no task_list.md)"
            found=$((found + 1))
        fi
    done

    if [ "$found" -eq 0 ]; then
        print_warning "No valid tasks found in $AUTONOMOUS_DIR/"
    fi

    echo ""
}

# Check if task exists
task_exists() {
    local task_name="$1"
    [ -f "$AUTONOMOUS_DIR/$task_name/task_list.md" ]
}

# Get task directory
get_task_dir() {
    local task_name="$1"
    echo "$AUTONOMOUS_DIR/$task_name"
}

# Get progress from task_list.md
get_progress() {
    local task_dir="$1"
    if [ -f "$task_dir/task_list.md" ]; then
        local total=$(grep -c '^\- \[' "$task_dir/task_list.md" 2>/dev/null || echo "0")
        local done=$(grep -c '^\- \[x\]' "$task_dir/task_list.md" 2>/dev/null || echo "0")
        echo "$done/$total"
    else
        echo "0/0"
    fi
}

# Check if all tasks are complete
is_complete() {
    local task_dir="$1"
    if [ -f "$task_dir/task_list.md" ]; then
        local total=$(grep -c '^\- \[' "$task_dir/task_list.md" 2>/dev/null || echo "0")
        local done=$(grep -c '^\- \[x\]' "$task_dir/task_list.md" 2>/dev/null || echo "0")
        if [ "$done" -eq "$total" ] && [ "$total" -gt 0 ]; then
            return 0  # complete
        fi
    fi
    return 1  # not complete
}

# Run initializer session
run_initializer() {
    local task_name="$1"
    local task_desc="$2"
    local task_dir=$(get_task_dir "$task_name")

    print_header "INITIALIZER SESSION"
    echo "Task: $task_desc"
    echo "Task Name: $task_name"
    echo "Task Directory: $task_dir"
    echo ""

    # Create task directory
    mkdir -p "$task_dir"

    # Read initializer prompt template and substitute {TASK_DIR} placeholder
    local init_prompt=$(cat "$SKILL_DIR/templates/initializer-prompt.md" | sed "s|{TASK_DIR}|$task_dir|g")

    # Execute Claude in headless mode (bypass permissions for autonomous execution)
    claude -p "Task: $task_desc
Task Name: $task_name
Task Directory: $task_dir

$init_prompt" \
        --output-format stream-json \
        --max-turns $MAX_TURNS_INIT \
        --permission-mode bypassPermissions \
        --append-system-prompt "You are the Initializer Agent. Create task_list.md and progress.md in the $task_dir directory. All task files must be created in $task_dir/, not in the current directory."

    echo ""
    print_success "Initializer session complete"
}

# Run executor session
run_executor() {
    local task_name="$1"
    local task_dir=$(get_task_dir "$task_name")

    print_header "EXECUTOR SESSION"
    echo "Task Name: $task_name"
    echo "Task Directory: $task_dir"
    echo ""

    # Read current state
    local task_list=$(cat "$task_dir/task_list.md" 2>/dev/null || echo "No task list found")
    local progress_notes=$(cat "$task_dir/progress.md" 2>/dev/null || echo "No progress notes yet")

    # Read executor prompt template and substitute {TASK_DIR} placeholder
    local exec_prompt=$(cat "$SKILL_DIR/templates/executor-prompt.md" | sed "s|{TASK_DIR}|$task_dir|g")

    # Execute Claude in headless mode (bypass permissions for autonomous execution)
    claude -p "Continue working on the task.
Task Name: $task_name
Task Directory: $task_dir

Current task_list.md:
$task_list

Previous progress notes:
$progress_notes

$exec_prompt" \
        --output-format stream-json \
        --max-turns $MAX_TURNS_EXEC \
        --permission-mode bypassPermissions \
        --append-system-prompt "You are the Executor Agent. Complete tasks and update files in the $task_dir directory. All task files are in $task_dir/, not in the current directory."

    echo ""
    print_success "Executor session complete"
}

# Main execution loop
main() {
    local task_desc=""
    local task_name=""
    local auto_continue=true
    local max_sessions=0
    local session_num=1
    local continue_mode=false

    # Check dependencies first (only for commands that need claude)
    # We'll check later before actually running claude

    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --help|-h)
                show_help
                exit 0
                ;;
            --list|-l)
                list_tasks
                exit 0
                ;;
            --task-name|-n)
                task_name="${2:-}"
                shift 2
                ;;
            --continue|-c)
                continue_mode=true
                shift
                ;;
            --no-auto-continue)
                auto_continue=false
                shift
                ;;
            --max-sessions)
                max_sessions="${2:-0}"
                shift 2
                ;;
            *)
                task_desc="$1"
                shift
                ;;
        esac
    done

    # Determine task name
    if [ -z "$task_name" ] && [ -n "$task_desc" ]; then
        task_name=$(generate_task_name "$task_desc")
        print_info "Generated task name: $task_name"
    fi

    # Validate
    if [ -z "$task_name" ]; then
        if [ "$continue_mode" = true ]; then
            # Try to find most recent task
            if [ -d "$AUTONOMOUS_DIR" ]; then
                task_name=$(ls -t "$AUTONOMOUS_DIR" 2>/dev/null | head -1) || true
            fi
            if [ -z "$task_name" ]; then
                print_error "No task name provided and no existing tasks found"
                echo "Usage: $0 \"Your task description\""
                echo "       $0 --task-name <name> --continue"
                exit 1
            fi
            print_info "Continuing most recent task: $task_name"
        else
            print_error "No task description or name provided"
            show_help
            exit 1
        fi
    fi

    # Security: Validate task name to prevent path traversal
    if ! validate_task_name "$task_name"; then
        exit 1
    fi

    # Check that claude command is available before starting sessions
    check_dependencies

    local task_dir
    task_dir=$(get_task_dir "$task_name")

    # Main loop
    while true; do
        echo ""
        print_header "SESSION $session_num - $task_name"

        # Show current progress
        if task_exists "$task_name"; then
            echo "Progress: $(get_progress "$task_dir")"
            echo ""
        fi

        # Determine which agent to run
        if task_exists "$task_name"; then
            # Task list exists - run executor
            run_executor "$task_name"
        else
            # No task list - run initializer
            if [ -z "$task_desc" ]; then
                print_error "Task '$task_name' not found and no description provided"
                echo "Provide a task description to initialize: $0 \"Your task description\""
                exit 1
            fi
            run_initializer "$task_name" "$task_desc"
        fi

        # Show progress after session
        echo ""
        echo "=== Progress: $(get_progress "$task_dir") ==="

        # Check completion
        if is_complete "$task_dir"; then
            echo ""
            print_success "ALL TASKS COMPLETED!"
            echo ""
            echo "Task directory: $task_dir"
            echo "Final task list:"
            cat "$task_dir/task_list.md"
            exit 0
        fi

        # Check max sessions
        if [ $max_sessions -gt 0 ] && [ $session_num -ge $max_sessions ]; then
            print_warning "Reached maximum sessions ($max_sessions)"
            exit 0
        fi

        # Auto-continue logic
        if [ "$auto_continue" = true ]; then
            echo ""
            echo "Continuing in $AUTO_CONTINUE_DELAY seconds... (Press Ctrl+C to pause)"

            # Sleep with countdown
            for i in $(seq $AUTO_CONTINUE_DELAY -1 1); do
                echo -ne "\r$i... "
                sleep 1
            done
            echo ""
        else
            echo ""
            print_warning "Auto-continue disabled. Run again to continue."
            exit 0
        fi

        session_num=$((session_num + 1))
    done
}

# Handle Ctrl+C gracefully
trap 'echo ""; print_warning "Interrupted. Progress saved in $AUTONOMOUS_DIR/$task_name/"; echo "Run again to continue: $0 --task-name $task_name --continue"; exit 130' INT

# Run main
main "$@"
