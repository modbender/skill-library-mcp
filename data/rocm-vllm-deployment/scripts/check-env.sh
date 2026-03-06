#!/bin/bash
#
# check-env.sh - Check and load HF_TOKEN and HF_HOME environment variables
#
# This script is part of the rocm_vllm_deployment skill.
# It sources ~/.bashrc and validates environment variables.
#
# Priority Order:
#   1. Environment variables already set (e.g., from parent process/parameters)
#   2. ~/.bashrc (sourced by this script)
#   3. Default values (HF_HOME only; HF_TOKEN remains unset)
#
# Usage:
#   ./check-env.sh [--strict] [--quiet]
#
# Options:
#   --strict   Fail if HF_HOME is not set (default: warn only)
#   --quiet    Suppress informational output
#
# Exit Codes:
#   0 - Environment check completed (variables loaded or defaulted)
#   2 - Critical error (e.g., cannot source ~/.bashrc)
#
# Environment Variables:
#   HF_TOKEN - Optional here, required only for gated models (checked at download time)
#   HF_HOME  - Optional: Custom model cache directory (default: ~/.cache/huggingface/hub)
#

set -e

# Parse arguments
STRICT_MODE=false
QUIET_MODE=false

for arg in "$@"; do
    case $arg in
        --strict)
            STRICT_MODE=true
            shift
            ;;
        --quiet)
            QUIET_MODE=true
            shift
            ;;
    esac
done

# Helper function for output
log() {
    if [ "$QUIET_MODE" = false ]; then
        echo "$@"
    fi
}

# Track source of variables
HF_TOKEN_SOURCE="not set"
HF_HOME_SOURCE="not set"

#------------------------------------------------------------------------------
# Step 1: Check if already set in environment (from parameters/parent process)
#------------------------------------------------------------------------------
log "=== Environment Check ==="
log ""

if [ -n "$HF_TOKEN" ]; then
    HF_TOKEN_SOURCE="environment/parameter"
    log "✓ HF_TOKEN already set in environment: ${HF_TOKEN:0:10}..."
fi

if [ -n "$HF_HOME" ]; then
    HF_HOME_SOURCE="environment/parameter"
    log "✓ HF_HOME already set in environment: $HF_HOME"
fi

#------------------------------------------------------------------------------
# Step 2: Source ~/.bashrc to load missing variables
#------------------------------------------------------------------------------
if [ -f "$HOME/.bashrc" ]; then
    # Source .bashrc to load HF_TOKEN and HF_HOME if not already set
    source "$HOME/.bashrc"
    log "✓ Loaded ~/.bashrc"
    
    # Check if variables were loaded from .bashrc
    if [ -z "$HF_TOKEN_SOURCE" ] && [ -n "$HF_TOKEN" ]; then
        HF_TOKEN_SOURCE="~/.bashrc"
        log "✓ HF_TOKEN loaded from ~/.bashrc: ${HF_TOKEN:0:10}..."
    fi
    
    if [ -z "$HF_HOME_SOURCE" ] && [ -n "$HF_HOME" ]; then
        HF_HOME_SOURCE="~/.bashrc"
        log "✓ HF_HOME loaded from ~/.bashrc: $HF_HOME"
    fi
else
    log "⚠️  WARNING: ~/.bashrc not found"
    log "Creating empty ~/.bashrc for future use..."
    touch "$HOME/.bashrc"
fi

log ""

#------------------------------------------------------------------------------
# Step 3: Apply defaults for missing variables
#------------------------------------------------------------------------------

# HF_TOKEN: No default, will fail at download time if required
if [ -z "$HF_TOKEN" ]; then
    HF_TOKEN_SOURCE="not set (public models only)"
    log "⚠️  HF_TOKEN not set"
    log "  - Public models: Will proceed without authentication"
    log "  - Gated models: Will fail at download time with clear error"
    log ""
    log "To avoid authentication errors, add to ~/.bashrc:"
    log "  export HF_TOKEN=\"hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx\""
else
    log "✓ HF_TOKEN: ${HF_TOKEN:0:10}... (source: $HF_TOKEN_SOURCE)"
fi

# HF_HOME: Default to ~/.cache/huggingface/hub
if [ -z "$HF_HOME" ]; then
    if [ "$STRICT_MODE" = true ]; then
        log "❌ ERROR: HF_HOME is not set (strict mode)"
        log ""
        log "Please add the following to ~/.bashrc:"
        log ""
        log "  export HF_HOME=\"/path/to/models\""
        log ""
        exit 1
    else
        HF_HOME_SOURCE="default"
        HF_HOME="$HOME/.cache/huggingface/hub"
        log "⚠️  HF_HOME not set, using default: $HF_HOME"
        log ""
        log "For production, consider adding to ~/.bashrc:"
        log "  export HF_HOME=\"/data/models/huggingface\""
    fi
else
    log "✓ HF_HOME: $HF_HOME (source: $HF_HOME_SOURCE)"
fi

#------------------------------------------------------------------------------
# Step 4: Export for child processes
#------------------------------------------------------------------------------
export HF_TOKEN
export HF_HOME

log ""
log "=== Environment Ready ==="
log ""
log "Summary:"
log "  HF_TOKEN: ${HF_TOKEN:0:10}... ($HF_TOKEN_SOURCE)"
log "  HF_HOME:  $HF_HOME ($HF_HOME_SOURCE)"
log ""

# Output for parsing (optional, for automation)
if [ "$QUIET_MODE" = true ]; then
    echo "HF_TOKEN_SOURCE=$HF_TOKEN_SOURCE"
    echo "HF_HOME_SOURCE=$HF_HOME_SOURCE"
fi

exit 0
