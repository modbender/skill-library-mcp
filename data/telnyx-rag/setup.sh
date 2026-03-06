#!/usr/bin/env bash
#
# Telnyx RAG Memory - Setup Script
#
# Quick setup for semantic search over your OpenClaw workspace.
# Only requirement: TELNYX_API_KEY
#
# Usage: 
#   ./setup.sh [bucket-name]     # Full setup
#   ./setup.sh --check          # Dry-run validation only
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BUCKET="${1:-openclaw-memory}"
DRY_RUN=false

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}ℹ${NC} $1"; }
log_ok()   { echo -e "${GREEN}✓${NC} $1"; }
log_warn() { echo -e "${YELLOW}⚠${NC} $1"; }
log_err()  { echo -e "${RED}✗${NC} $1"; }

# Track setup results
CHECKS_PASSED=0
CHECKS_FAILED=0
SETUP_ERRORS=()

check_python() {
    log_info "Checking Python installation..."
    
    if ! command -v python3 &> /dev/null; then
        log_err "Python 3 is required but not installed"
        SETUP_ERRORS+=("Python 3 not found")
        ((CHECKS_FAILED++))
        return 1
    fi
    
    # Check Python version >= 3.8
    python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    if python3 -c "import sys; sys.exit(0 if sys.version_info >= (3, 8) else 1)" 2>/dev/null; then
        log_ok "Python $python_version found"
        ((CHECKS_PASSED++))
    else
        log_err "Python 3.8+ required, found $python_version"
        SETUP_ERRORS+=("Python version too old: $python_version")
        ((CHECKS_FAILED++))
        return 1
    fi
}

check_syntax() {
    log_info "Validating script syntax..."
    
    # Check Python files
    for py_file in "$SCRIPT_DIR"/*.py; do
        if [[ -f "$py_file" ]]; then
            if python3 -c "import py_compile; py_compile.compile('$py_file', doraise=True)" 2>/dev/null; then
                log_ok "$(basename "$py_file") syntax OK"
            else
                log_err "$(basename "$py_file") has syntax errors"
                SETUP_ERRORS+=("Syntax error in $(basename "$py_file")")
                ((CHECKS_FAILED++))
                return 1
            fi
        fi
    done
    
    # Check bash files
    for sh_file in "$SCRIPT_DIR"/*.sh; do
        if [[ -f "$sh_file" ]]; then
            if bash -n "$sh_file" 2>/dev/null; then
                log_ok "$(basename "$sh_file") syntax OK"
            else
                log_err "$(basename "$sh_file") has syntax errors"
                SETUP_ERRORS+=("Syntax error in $(basename "$sh_file")")
                ((CHECKS_FAILED++))
                return 1
            fi
        fi
    done
    
    ((CHECKS_PASSED++))
}

check_credentials() {
    log_info "Checking Telnyx API credentials..."
    
    # Check for API key
    if [[ -n "${TELNYX_API_KEY:-}" ]]; then
        log_ok "TELNYX_API_KEY found in environment"
    elif [[ -f "$SCRIPT_DIR/.env" ]]; then
        log_ok ".env file found"
        # Source the .env file to get the key
        set -a  # Enable export of all variables
        source "$SCRIPT_DIR/.env"
        set +a  # Disable export
    else
        log_err "No Telnyx API key found"
        echo ""
        echo "   Please set your API key using one of these methods:"
        echo ""
        echo "   Option 1: Environment variable"
        echo "     export TELNYX_API_KEY=\"KEY....\""
        echo ""
        echo "   Option 2: Create .env file in this directory"
        echo "     echo 'TELNYX_API_KEY=KEY....' > $SCRIPT_DIR/.env"
        echo ""
        echo "   Get your API key at: https://portal.telnyx.com/#/app/api-keys"
        echo ""
        SETUP_ERRORS+=("No API key found")
        ((CHECKS_FAILED++))
        return 1
    fi
    
    # Test API key by making a simple request
    if [[ -n "${TELNYX_API_KEY:-}" ]]; then
        log_info "Testing API key validity..."
        
        # Use a simple API call to validate the key
        if test_api_key; then
            log_ok "API key is valid"
            ((CHECKS_PASSED++))
        else
            log_err "API key test failed"
            SETUP_ERRORS+=("Invalid or expired API key")
            ((CHECKS_FAILED++))
            return 1
        fi
    else
        log_warn "Could not load API key for testing"
        ((CHECKS_FAILED++))
        return 1
    fi
}

test_api_key() {
    # Make a simple API call to test the key
    local response
    response=$(curl -s -w "%{http_code}" -o /dev/null \
        -H "Authorization: Bearer $TELNYX_API_KEY" \
        -H "Content-Type: application/json" \
        "https://api.telnyx.com/v2/ai/embeddings/similarity-search" \
        -d '{"bucket_name":"test-nonexistent","query":"test","num_docs":1}' \
        2>/dev/null || echo "000")
    
    # We expect 404 (bucket not found) which means API key works
    # 401/403 would mean bad/expired key
    if [[ "$response" =~ ^[2-4][0-9][0-9]$ ]]; then
        return 0  # API key works (got a valid HTTP response)
    else
        return 1  # Network error or invalid key
    fi
}

check_config() {
    log_info "Validating configuration..."
    
    if [[ ! -f "$SCRIPT_DIR/config.json" ]]; then
        log_err "config.json not found"
        SETUP_ERRORS+=("Missing config.json")
        ((CHECKS_FAILED++))
        return 1
    fi
    
    if python3 -c "import json; json.load(open('$SCRIPT_DIR/config.json'))" 2>/dev/null; then
        log_ok "config.json is valid JSON"
        ((CHECKS_PASSED++))
    else
        log_err "config.json has invalid JSON syntax"
        SETUP_ERRORS+=("Invalid config.json syntax")
        ((CHECKS_FAILED++))
        return 1
    fi
}

make_executable() {
    log_info "Making scripts executable..."
    
    if chmod +x "$SCRIPT_DIR"/*.py "$SCRIPT_DIR"/*.sh 2>/dev/null; then
        log_ok "Scripts marked executable"
        ((CHECKS_PASSED++))
    else
        log_warn "Could not make all scripts executable"
        # Don't fail on this, just warn
    fi
}

update_config() {
    log_info "Updating config.json with bucket name..."
    
    if ! python3 -c "
import json
import sys
try:
    config_path = '$SCRIPT_DIR/config.json'
    with open(config_path) as f:
        config = json.load(f)
    config['bucket'] = '$BUCKET'
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    print('   ✓ Bucket set to: $BUCKET')
except Exception as e:
    print(f'   ✗ Failed to update config: {e}', file=sys.stderr)
    sys.exit(1)
"; then
        log_err "Failed to update config.json"
        SETUP_ERRORS+=("Could not update config.json")
        ((CHECKS_FAILED++))
        return 1
    fi
    
    ((CHECKS_PASSED++))
}

create_bucket() {
    log_info "Creating bucket..."
    
    if python3 "$SCRIPT_DIR/sync.py" --create-bucket --quiet; then
        log_ok "Bucket created/verified"
        ((CHECKS_PASSED++))
    else
        log_err "Failed to create bucket"
        SETUP_ERRORS+=("Bucket creation failed")
        ((CHECKS_FAILED++))
        return 1
    fi
}

sync_files() {
    log_info "Syncing workspace files..."
    
    if python3 "$SCRIPT_DIR/sync.py" --quiet; then
        log_ok "Files synced successfully"
        ((CHECKS_PASSED++))
    else
        log_err "File sync failed"
        SETUP_ERRORS+=("File sync failed")
        ((CHECKS_FAILED++))
        return 1
    fi
}

trigger_embedding() {
    log_info "Triggering embedding process..."
    
    if python3 "$SCRIPT_DIR/sync.py" --embed --quiet; then
        log_ok "Embedding triggered successfully"
        ((CHECKS_PASSED++))
    else
        log_warn "Embedding trigger failed (you can try manually later)"
        # Don't fail setup for this
    fi
}

show_summary() {
    echo ""
    echo "================================================"
    echo ""
    
    if [[ $CHECKS_FAILED -eq 0 ]]; then
        log_ok "Setup completed successfully! ✨"
        echo ""
        echo "Usage:"
        echo "  Search:  ./search.py \"What do you know about X?\""
        echo "  Sync:    ./sync.py"
        echo "  Status:  ./sync.py --status"
        echo ""
        echo "Note: Embeddings may take 1-2 minutes to process."
        echo "Test with: ./search.py \"test\" after a few minutes."
        echo ""
    else
        log_err "Setup completed with $CHECKS_FAILED errors:"
        echo ""
        for error in "${SETUP_ERRORS[@]}"; do
            echo "  • $error"
        done
        echo ""
        echo "Please fix the above issues and run setup again."
        echo ""
        return 1
    fi
}

show_help() {
    cat << EOF
Telnyx RAG Memory - Setup Script

Usage: $0 [OPTIONS] [bucket-name]

OPTIONS:
  --check     Validate requirements without making changes
  --help      Show this help message

ARGUMENTS:
  bucket-name Custom bucket name (default: openclaw-memory)

EXAMPLES:
  $0                    # Full setup with default bucket
  $0 my-bucket          # Full setup with custom bucket
  $0 --check            # Validate requirements only

REQUIREMENTS:
  - Python 3.8+
  - TELNYX_API_KEY environment variable or .env file
  - Network access to Telnyx APIs

Get your API key at: https://portal.telnyx.com/#/app/api-keys
EOF
}

main() {
    # Parse arguments
    case "${1:-}" in
        --check)
            DRY_RUN=true
            shift
            BUCKET="${1:-openclaw-memory}"
            ;;
        --help|-h)
            show_help
            exit 0
            ;;
        --*)
            log_err "Unknown option: $1"
            echo "Use --help for usage information."
            exit 1
            ;;
        *)
            # Positional argument is bucket name
            BUCKET="${1:-openclaw-memory}"
            ;;
    esac
    
    echo ""
    echo "🧠 Telnyx RAG Memory Setup"
    echo "=========================="
    echo ""
    echo "Bucket: $BUCKET"
    if [[ "$DRY_RUN" == "true" ]]; then
        echo "Mode: Validation Only (--check)"
    fi
    echo ""
    
    # Run checks
    check_python
    check_syntax
    check_credentials
    check_config
    
    if [[ "$DRY_RUN" == "true" ]]; then
        echo ""
        log_info "Dry-run complete. No changes were made."
        show_summary
        return $?
    fi
    
    # Proceed with setup if checks pass
    if [[ $CHECKS_FAILED -eq 0 ]]; then
        make_executable
        update_config
        create_bucket
        sync_files
        trigger_embedding
    fi
    
    show_summary
}

main "$@"