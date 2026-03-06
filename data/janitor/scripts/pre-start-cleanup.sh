#!/bin/bash

###############################################################################
# OpenClaw Pre-Start Cleanup Script
#
# This script runs BEFORE OpenClaw starts to clean up old sessions
# preventing context limit issues from the start.
#
# Usage:
#   ./pre-start-cleanup.sh [--config CONFIG_FILE]
#
# Installation (systemd):
#   Add to OpenClaw service: ExecStartPre=/path/to/pre-start-cleanup.sh
###############################################################################

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
OPENCLAW_HOME="${OPENCLAW_HOME:-$HOME/.openclaw}"
SESSION_DIR="${SESSION_DIR:-$OPENCLAW_HOME/agents/main/sessions}"
LOG_FILE="${LOG_FILE:-$OPENCLAW_HOME/logs/pre-start-cleanup.log}"
MAX_SESSIONS="${MAX_SESSIONS:-20}"
MAX_SESSION_AGE_DAYS="${MAX_SESSION_AGE_DAYS:-7}"
ARCHIVE_DIR="${ARCHIVE_DIR:-$OPENCLAW_HOME/archives}"
ENABLE_ARCHIVING="${ENABLE_ARCHIVING:-true}"

# Safety checks
validate_path() {
    local path="$1"
    local name="$2"

    # Check for path traversal
    if [[ "$path" == *".."* ]]; then
        echo "ERROR: Path traversal detected in $name: $path"
        exit 1
    fi

    # Check for absolute path starting with /home or expected location
    if [[ ! "$path" =~ ^(/home|/Users|$HOME) ]]; then
        echo "ERROR: Suspicious path in $name: $path (must start with /home, /Users, or \$HOME)"
        exit 1
    fi
}

# Validate all paths
validate_path "$SESSION_DIR" "SESSION_DIR"
validate_path "$LOG_FILE" "LOG_FILE"
validate_path "$ARCHIVE_DIR" "ARCHIVE_DIR"

# Sanity check: Don't allow deleting more than 1000 sessions at once
MAX_DELETE_LIMIT=1000

# Ensure log directory exists
mkdir -p "$(dirname "$LOG_FILE")"

# Logging function
log() {
    local level=$1
    shift
    local message="$@"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] [$level] $message" | tee -a "$LOG_FILE"
}

log_info() {
    echo -e "${BLUE}[INFO]${NC} $@"
    log "INFO" "$@"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $@"
    log "SUCCESS" "$@"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $@"
    log "WARNING" "$@"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $@"
    log "ERROR" "$@"
}

# Check if session directory exists
if [ ! -d "$SESSION_DIR" ]; then
    log_info "Session directory does not exist: $SESSION_DIR"
    log_info "Nothing to clean up. Exiting."
    exit 0
fi

# Count current sessions
SESSION_COUNT=$(find "$SESSION_DIR" -type f -name "*.json" 2>/dev/null | wc -l | tr -d ' ')

log_info "====================================================="
log_info "OpenClaw Pre-Start Cleanup"
log_info "====================================================="
log_info "Session Directory: $SESSION_DIR"
log_info "Current Sessions: $SESSION_COUNT"
log_info "Max Sessions: $MAX_SESSIONS"
log_info "Max Age: $MAX_SESSION_AGE_DAYS days"
log_info "====================================================="

# Check if cleanup is needed
if [ "$SESSION_COUNT" -lt "$MAX_SESSIONS" ]; then
    log_success "Session count ($SESSION_COUNT) is below threshold ($MAX_SESSIONS)"
    log_info "No cleanup needed. Exiting."
    exit 0
fi

log_warning "Session count ($SESSION_COUNT) exceeds threshold ($MAX_SESSIONS)"
log_info "Starting cleanup process..."

# Create archive directory if archiving is enabled
if [ "$ENABLE_ARCHIVING" = "true" ]; then
    mkdir -p "$ARCHIVE_DIR"
    log_info "Archiving enabled. Archive directory: $ARCHIVE_DIR"
fi

# Archive old sessions before deletion
if [ "$ENABLE_ARCHIVING" = "true" ]; then
    ARCHIVE_NAME="sessions-$(date '+%Y-%m-%d-%H%M%S')-pre-start.tar.gz"
    ARCHIVE_PATH="$ARCHIVE_DIR/$ARCHIVE_NAME"
    TEMP_DIR="/tmp/openclaw-pre-start-archive-$$"

    mkdir -p "$TEMP_DIR"

    log_info "Creating archive: $ARCHIVE_NAME"

    # Copy sessions to temp directory
    ARCHIVED_COUNT=0
    while IFS= read -r session_file; do
        cp "$session_file" "$TEMP_DIR/"
        ((ARCHIVED_COUNT++))
    done < <(find "$SESSION_DIR" -type f -name "*.json" -mtime +1)

    if [ $ARCHIVED_COUNT -gt 0 ]; then
        # Create archive
        (cd "$(dirname "$TEMP_DIR")" && tar -czf "$ARCHIVE_PATH" "$(basename "$TEMP_DIR")")
        log_success "Archived $ARCHIVED_COUNT sessions to $ARCHIVE_NAME"
    else
        log_info "No sessions to archive (all are recent)"
    fi

    # Cleanup temp directory (safe - temp dir is in /tmp with unique PID)
    if [[ "$TEMP_DIR" == /tmp/openclaw-pre-start-archive-* ]]; then
        rm -rf "$TEMP_DIR"
    else
        log_error "SAFETY: Refusing to delete suspicious temp dir: $TEMP_DIR"
    fi
fi

# Clean old sessions (older than MAX_SESSION_AGE_DAYS)
log_info "Removing sessions older than $MAX_SESSION_AGE_DAYS days..."

# Safety check: Count first
OLD_SESSION_COUNT=$(find "$SESSION_DIR" -type f -name "*.json" -mtime +$MAX_SESSION_AGE_DAYS 2>/dev/null | wc -l | tr -d ' ')

if [ "$OLD_SESSION_COUNT" -gt "$MAX_DELETE_LIMIT" ]; then
    log_error "SAFETY ABORT: Attempted to delete $OLD_SESSION_COUNT sessions (limit: $MAX_DELETE_LIMIT)"
    log_error "This seems unsafe. Please review SESSION_DIR and MAX_SESSION_AGE_DAYS"
    exit 1
fi

DELETED_COUNT=0
while IFS= read -r session_file; do
    rm -f "$session_file"
    ((DELETED_COUNT++))
done < <(find "$SESSION_DIR" -type f -name "*.json" -mtime +$MAX_SESSION_AGE_DAYS)

if [ $DELETED_COUNT -gt 0 ]; then
    log_success "Deleted $DELETED_COUNT old sessions"
else
    log_info "No old sessions to delete"
fi

# If still over threshold, delete oldest sessions
NEW_SESSION_COUNT=$(find "$SESSION_DIR" -type f -name "*.json" 2>/dev/null | wc -l | tr -d ' ')

if [ "$NEW_SESSION_COUNT" -gt "$MAX_SESSIONS" ]; then
    log_warning "Still over threshold ($NEW_SESSION_COUNT > $MAX_SESSIONS)"
    log_info "Removing oldest sessions to reach threshold..."

    EXTRA_SESSIONS=$((NEW_SESSION_COUNT - MAX_SESSIONS))

    ADDITIONAL_DELETED=0
    while IFS= read -r session_file; do
        rm -f "$session_file"
        ((ADDITIONAL_DELETED++))
        [ $ADDITIONAL_DELETED -ge $EXTRA_SESSIONS ] && break
    done < <(find "$SESSION_DIR" -type f -name "*.json" -printf '%T@ %p\n' | sort -n | cut -d' ' -f2-)

    log_success "Deleted $ADDITIONAL_DELETED additional sessions"
fi

# Final count
FINAL_COUNT=$(find "$SESSION_DIR" -type f -name "*.json" 2>/dev/null | wc -l | tr -d ' ')

log_info "====================================================="
log_success "Cleanup Complete!"
log_info "Before: $SESSION_COUNT sessions"
log_info "After: $FINAL_COUNT sessions"
log_info "Removed: $((SESSION_COUNT - FINAL_COUNT)) sessions"
log_info "====================================================="

# Clean old archives (older than 30 days)
if [ "$ENABLE_ARCHIVING" = "true" ] && [ -d "$ARCHIVE_DIR" ]; then
    log_info "Cleaning old archives (>30 days)..."

    OLD_ARCHIVES=$(find "$ARCHIVE_DIR" -type f -name "*.tar.gz" -mtime +30 2>/dev/null | wc -l | tr -d ' ')

    if [ "$OLD_ARCHIVES" -gt 0 ]; then
        find "$ARCHIVE_DIR" -type f -name "*.tar.gz" -mtime +30 -delete
        log_success "Deleted $OLD_ARCHIVES old archives"
    else
        log_info "No old archives to delete"
    fi
fi

log_success "Pre-start cleanup finished successfully"

exit 0
