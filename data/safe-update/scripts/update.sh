#!/bin/bash
# Safe Update Script
# Update OpenClaw from source with configurable path and branch

set -e

# Default values
PROJECT_DIR="${OPENCLAW_PROJECT_DIR:-$HOME/projects/openclaw}"
BRANCH="${OPENCLAW_BRANCH:-main}"
DRY_RUN="${DRY_RUN:-false}"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Usage function
usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --dir PATH       OpenClaw project directory (default: $PROJECT_DIR)"
    echo "  --branch NAME    Git branch to update (default: $BRANCH)"
    echo "  --dry-run        Show what would be done without executing"
    echo "  --help           Show this help message"
    echo ""
    echo "Environment Variables:"
    echo "  OPENCLAW_PROJECT_DIR  Project directory (default: ~/projects/openclaw)"
    echo "  OPENCLAW_BRANCH      Git branch (default: main)"
    echo "  DRY_RUN             Set to 'true' for dry-run mode"
    exit 0
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --dir)
            PROJECT_DIR="$2"
            shift 2
            ;;
        --branch)
            BRANCH="$2"
            shift 2
            ;;
        --dry-run)
            DRY_RUN="true"
            shift
            ;;
        --help)
            usage
            ;;
        *)
            echo "Unknown option: $1"
            usage
            ;;
    esac
done

# Functions
log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1" >&2; }

run_cmd() {
    if [ "$DRY_RUN" = "true" ]; then
        echo -e "${YELLOW}[DRY-RUN]${NC} Would execute: $*"
    else
        log_info "Executing: $*"
        "$@"
    fi
}

# Validate branch name to prevent shell injection
validate_branch() {
    local branch="$1"
    if [[ ! "$branch" =~ ^[a-zA-Z0-9][a-zA-Z0-9_./-]*$ ]]; then
        log_error "Invalid branch name: $branch"
        log_error "Branch names can only contain alphanumeric characters, underscores, hyphens, dots, and forward slashes."
        exit 1
    fi
}

# Check required binaries
check_dependencies() {
    log_info "Checking dependencies..."
    
    local missing=()
    
    for cmd in git npm node; do
        if ! command -v $cmd &> /dev/null; then
            missing+=($cmd)
        fi
    done
    
    if [ ${#missing[@]} -gt 0 ]; then
        log_error "Missing required binaries: ${missing[*]}"
        log_error "Please install them before running this script."
        exit 1
    fi
    
    log_info "All dependencies found: git, npm, node"
}

# Check project directory
check_project() {
    log_info "Checking project directory: $PROJECT_DIR"
    
    if [ ! -d "$PROJECT_DIR" ]; then
        log_error "Project directory does not exist: $PROJECT_DIR"
        exit 1
    fi
    
    if [ ! -d "$PROJECT_DIR/.git" ]; then
        log_error "Not a git repository: $PROJECT_DIR"
        exit 1
    fi
    
    log_info "Project directory valid"
}

# Check git status
check_git_status() {
    log_info "Checking git status..."
    
    cd "$PROJECT_DIR"
    
    # Check for uncommitted changes
    if [ -n "$(git status --porcelain)" ]; then
        log_warn "You have uncommitted changes!"
        log_warn "Please commit or stash them before updating."
        if [ "$DRY_RUN" != "true" ]; then
            read -p "Continue anyway? (y/N) " -n 1 -r
            echo
            if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                log_info "Aborted."
                exit 0
            fi
        fi
    fi
}

# Backup config files
backup_config() {
    log_info "Backing up config files..."
    
    local backup_dir="$HOME/.openclaw/backups"
    mkdir -p "$backup_dir"
    
    local backup_suffix=$(date +%Y%m%d-%H%M%S)
    
    # Backup openclaw.json
    if [ -f "$HOME/.openclaw/openclaw.json" ]; then
        run_cmd cp "$HOME/.openclaw/openclaw.json" "$backup_dir/openclaw.json.bak.$backup_suffix"
        log_info "Backed up: openclaw.json"
    fi
    
    # Backup auth profiles
    if [ -f "$HOME/.openclaw/agents/main/agent/auth-profiles.json" ]; then
        run_cmd cp "$HOME/.openclaw/agents/main/agent/auth-profiles.json" "$backup_dir/auth-profiles.json.bak.$backup_suffix"
        log_info "Backed up: auth-profiles.json"
    fi
    
    log_info "Backups saved to: $backup_dir"
}

# Main update process
main() {
    echo "========================================"
    echo "       Safe Update for OpenClaw"
    echo "========================================"
    echo ""
    echo "Configuration:"
    echo "  Project Dir: $PROJECT_DIR"
    echo "  Branch:      $BRANCH"
    echo "  Dry Run:     $DRY_RUN"
    echo ""
    
    if [ "$DRY_RUN" = "true" ]; then
        log_warn "DRY-RUN MODE: No actual changes will be made"
        echo ""
    fi
    
    # Pre-run warning
    echo "========================================"
    echo "⚠️  PRE-RUN CHECKLIST"
    echo "========================================"
    echo "Before continuing, ensure you have:"
    echo "  [ ] Backed up ~/.openclaw/openclaw.json"
    echo "  [ ] Backed up auth profiles (if exist)"
    echo "  [ ] Committed or stashed local changes"
    echo ""
    
    if [ "$DRY_RUN" != "true" ]; then
        read -p "Continue with update? (y/N) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log_info "Aborted."
            exit 0
        fi
    fi
    
    echo ""
    
    # Run checks
    check_dependencies
    check_project
    check_git_status
    
    # Backup
    if [ "$DRY_RUN" != "true" ]; then
        backup_config
    fi
    
    # Update process
    log_info "Starting update process..."
    
    cd "$PROJECT_DIR"
    
    # Validate branch name
    validate_branch "$BRANCH"
    
    # Add upstream if needed
    git remote add upstream https://github.com/openclaw/openclaw.git 2>/dev/null || true
    
    # Fetch upstream
    run_cmd git fetch upstream
    
    # Checkout and merge
    run_cmd git checkout "$BRANCH"
    run_cmd git merge "upstream/$BRANCH"
    
    # Build and install
    run_cmd npm run build
    run_cmd npm i -g .
    
    # Check version
    if [ "$DRY_RUN" != "true" ]; then
        NEW_VERSION=$(openclaw --version)
        log_info "Update complete! New version: $NEW_VERSION"
    fi
    
    # Restart gateway
    if [ "$DRY_RUN" != "true" ]; then
        log_info "Restarting Gateway..."
        run_cmd systemctl --user restart openclaw-gateway
        
        sleep 3
        
        # Check health
        if command -v openclaw &> /dev/null; then
            openclaw health 2>/dev/null || openclaw status || true
        fi
    fi
    
    echo ""
    echo "========================================"
    echo "✅ Update Process Complete!"
    echo "========================================"
    echo ""
    echo "Note: If issues occur, restore from ~/.openclaw/backups/"
}

# Run main
main
