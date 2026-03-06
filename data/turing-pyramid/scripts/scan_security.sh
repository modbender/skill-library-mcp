#!/bin/bash
# scan_security.sh - Check system stability, backups, and security hygiene
# Returns: 3=secure, 2=minor concerns, 1=issues, 0=compromised
# Event-sensitive: backup events, security concerns, updates

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/_scan_helper.sh"

NEED="security"
# WORKSPACE validated by _scan_helper.sh
MEMORY_DIR="$WORKSPACE/memory"
TODAY=$(date +%Y-%m-%d)
YESTERDAY=$(date -d "yesterday" +%Y-%m-%d 2>/dev/null || date -v-1d +%Y-%m-%d 2>/dev/null)

# Get time-based satisfaction
time_sat=$(calc_time_satisfaction "$NEED")

# Always check events — security issues should surface immediately
issues=0
positive_signals=0

# Check core files exist
[[ ! -f "$WORKSPACE/SOUL.md" ]] && issues=$((issues + 2))
[[ ! -f "$WORKSPACE/MEMORY.md" ]] && issues=$((issues + 1))
[[ ! -f "$WORKSPACE/AGENTS.md" ]] && issues=$((issues + 1))

# Check for backup indicators (generic)
BACKUP_DIR="${BACKUP_DIR:-}"
if [[ -n "$BACKUP_DIR" && -d "$BACKUP_DIR" ]]; then
    # Check if backup is recent (within 48h)
    recent_backup=$(find -P "$BACKUP_DIR" -type f -mmin -2880 2>/dev/null | head -1)
    [[ -z "$recent_backup" ]] && issues=$((issues + 1))
fi

# Scan memory for security events (word count)
scan_security_events() {
    local file="$1"
    [[ ! -f "$file" ]] && return
    
    # Positive: backup completed, security check passed, updated, patched
    local pos=$(grep -oiE "(backup completed|backup success|security check|passed audit|updated|patched|secured|vault intact|integrity ok)" "$file" 2>/dev/null | wc -l) || pos=0
    positive_signals=$((positive_signals + pos))
    
    # Negative: backup failed, security issue, compromised, breach, vulnerable
    local neg=$(grep -oiE "(backup failed|security issue|compromised|breach|vulnerable|attack|unauthorized|leaked|exposed|credential.*(stolen|leaked))" "$file" 2>/dev/null | wc -l) || neg=0
    issues=$((issues + neg * 2))  # Security issues weighted heavier
}

scan_security_events "$MEMORY_DIR/$TODAY.md"
scan_security_events "$MEMORY_DIR/$YESTERDAY.md"

# Calculate event satisfaction
if [[ $issues -ge 4 ]]; then
    event_sat=0  # Compromised
elif [[ $issues -ge 2 ]]; then
    event_sat=1  # Issues present
elif [[ $issues -ge 1 ]]; then
    event_sat=2  # Minor concerns
elif [[ $positive_signals -ge 2 ]]; then
    event_sat=3  # Actively maintained
else
    event_sat=$time_sat  # Default to time-based
fi

smart_satisfaction "$NEED" "$event_sat"
