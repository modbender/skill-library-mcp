#!/usr/bin/env bash
# Memory Guard - Agent Memory Integrity & Security Tool
# By Nix (nixus.pro)

set -euo pipefail

GUARD_DIR="${MEMORY_GUARD_DIR:-.memory-guard}"
HASH_FILE="$GUARD_DIR/hashes.json"
LOG_DIR="$GUARD_DIR/logs"
ACTIONS_LOG="$LOG_DIR/actions.log"
REJECTIONS_LOG="$LOG_DIR/rejections.log"
HANDOFFS_LOG="$LOG_DIR/handoffs.log"
AUDIT_LOG="$LOG_DIR/audit.log"

# Critical files that should rarely change
CRITICAL_FILES=("SOUL.md" "AGENTS.md" "IDENTITY.md")
# Monitored files that change often but should be tracked
MONITORED_FILES=("MEMORY.md" "HEARTBEAT.md" "TOOLS.md" "USER.md")

timestamp() { date -u +"%Y-%m-%dT%H:%M:%SZ"; }

log_action() { echo "[$(timestamp)] ACTION: $*" >> "$ACTIONS_LOG"; }
log_rejection() { echo "[$(timestamp)] REJECT: $*" >> "$REJECTIONS_LOG"; }
log_handoff() { echo "[$(timestamp)] HANDOFF: $*" >> "$HANDOFFS_LOG"; }
log_audit() { echo "[$(timestamp)] AUDIT: $*" >> "$AUDIT_LOG"; }

ensure_dirs() {
    mkdir -p "$GUARD_DIR" "$LOG_DIR"
    [ -f "$HASH_FILE" ] || echo '{}' > "$HASH_FILE"
}

hash_file() {
    local f="$1"
    if [ -f "$f" ]; then
        sha256sum "$f" | cut -d' ' -f1
    else
        echo "MISSING"
    fi
}

file_mtime() {
    local f="$1"
    if [ -f "$f" ]; then
        stat -c %Y "$f" 2>/dev/null || stat -f %m "$f" 2>/dev/null || echo "0"
    else
        echo "0"
    fi
}

git_last_modifier() {
    local f="$1"
    if git rev-parse --git-dir &>/dev/null; then
        git log -1 --format="%an at %ai" -- "$f" 2>/dev/null || echo "unknown"
    else
        echo "no-git"
    fi
}

# INIT: Set up integrity tracking
cmd_init() {
    ensure_dirs
    echo '{}' > "$HASH_FILE"

    local tmp
    tmp=$(mktemp)
    echo '{' > "$tmp"
    local first=true

    for f in "${CRITICAL_FILES[@]}" "${MONITORED_FILES[@]}"; do
        if [ -f "$f" ]; then
            local h
            h=$(hash_file "$f")
            local mt
            mt=$(file_mtime "$f")
            local sz
            sz=$(wc -c < "$f")
            if [ "$first" = true ]; then first=false; else echo ',' >> "$tmp"; fi
            cat >> "$tmp" << ENTRY
  "$f": {
    "hash": "$h",
    "mtime": $mt,
    "size": $sz,
    "registered": "$(timestamp)",
    "critical": $(echo "${CRITICAL_FILES[@]}" | grep -qw "$f" && echo true || echo false)
  }
ENTRY
        fi
    done

    echo '}' >> "$tmp"
    # Use python to validate/format JSON, fallback to raw
    if command -v python3 &>/dev/null; then
        python3 -m json.tool "$tmp" > "$HASH_FILE" 2>/dev/null || mv "$tmp" "$HASH_FILE"
    else
        mv "$tmp" "$HASH_FILE"
    fi
    rm -f "$tmp"

    log_action "Initialized memory-guard. Tracked files: ${CRITICAL_FILES[*]} ${MONITORED_FILES[*]}"
    echo "Memory Guard initialized. Tracking $(python3 -c "import json; print(len(json.load(open('$HASH_FILE'))))" 2>/dev/null || echo "?") files."
    echo "Hash registry: $HASH_FILE"
    echo "Logs: $LOG_DIR/"
}

# VERIFY: Check all tracked files
cmd_verify() {
    ensure_dirs
    if [ ! -s "$HASH_FILE" ] || [ "$(cat "$HASH_FILE")" = "{}" ]; then
        echo "No files tracked. Run: memory-guard init"
        return 1
    fi

    local issues=0
    local checked=0
    local result=""

    while IFS= read -r fname; do
        local stored_hash
        stored_hash=$(python3 -c "
import json
d = json.load(open('$HASH_FILE'))
print(d.get('$fname', {}).get('hash', 'UNTRACKED'))
" 2>/dev/null)

        [ "$stored_hash" = "UNTRACKED" ] && continue

        checked=$((checked + 1))
        local current_hash
        current_hash=$(hash_file "$fname")

        local is_critical
        is_critical=$(python3 -c "
import json
d = json.load(open('$HASH_FILE'))
print(d.get('$fname', {}).get('critical', False))
" 2>/dev/null)

        if [ "$current_hash" = "MISSING" ]; then
            issues=$((issues + 1))
            result+="  MISSING  $fname (was tracked, now gone)\n"
            log_audit "FILE MISSING: $fname"
        elif [ "$current_hash" != "$stored_hash" ]; then
            issues=$((issues + 1))
            local modifier
            modifier=$(git_last_modifier "$fname")
            local severity="CHANGED"
            [ "$is_critical" = "True" ] && severity="CRITICAL CHANGED"

            result+="  $severity  $fname (modifier: $modifier)\n"
            log_audit "$severity: $fname | old=$stored_hash | new=$current_hash | modifier=$modifier"

            if [ "$is_critical" = "True" ]; then
                log_handoff "CRITICAL FILE CHANGED: $fname - requires human verification. Modifier: $modifier"
            fi
        else
            result+="  OK       $fname\n"
        fi
    done < <(python3 -c "
import json
for k in json.load(open('$HASH_FILE')):
    print(k)
" 2>/dev/null)

    echo "Memory Guard Verification Report"
    echo "================================="
    echo "Time: $(timestamp)"
    echo "Files checked: $checked"
    echo "Issues found: $issues"
    echo ""
    echo -e "$result"

    if [ "$issues" -gt 0 ]; then
        log_action "Verification FAILED: $issues issues in $checked files"
        echo "ACTION REQUIRED: $issues file(s) changed since last snapshot."
        echo "Run 'memory-guard accept' to update hashes after review."
        return 1
    else
        log_action "Verification PASSED: $checked files clean"
        echo "All files verified. No tampering detected."
        return 0
    fi
}

# ACCEPT: Update hashes after human review
cmd_accept() {
    ensure_dirs
    local target="${1:-all}"

    if [ "$target" = "all" ]; then
        cmd_init  # Re-register everything
        log_action "Accepted all current file states as trusted"
        echo "All file hashes updated to current state."
    elif [ -f "$target" ]; then
        local h
        h=$(hash_file "$target")
        python3 -c "
import json
d = json.load(open('$HASH_FILE'))
if '$target' in d:
    d['$target']['hash'] = '$h'
    d['$target']['accepted'] = '$(timestamp)'
    json.dump(d, open('$HASH_FILE', 'w'), indent=2)
    print('Accepted: $target')
else:
    print('Not tracked: $target')
" 2>/dev/null
        log_action "Accepted new hash for $target"
    else
        echo "File not found: $target"
        return 1
    fi
}

# AUDIT: Full audit report
cmd_audit() {
    ensure_dirs
    echo "Memory Guard Audit Report"
    echo "========================="
    echo "Generated: $(timestamp)"
    echo ""

    echo "--- Tracked Files ---"
    python3 -c "
import json, os
d = json.load(open('$HASH_FILE'))
for f, info in d.items():
    status = 'EXISTS' if os.path.exists(f) else 'MISSING'
    crit = 'CRITICAL' if info.get('critical') else 'monitored'
    print(f'  {status:8s} {crit:10s} {f} (registered: {info.get(\"registered\", \"?\")}, size: {info.get(\"size\", \"?\")}b)')
" 2>/dev/null

    echo ""
    echo "--- Recent Actions (last 20) ---"
    tail -20 "$ACTIONS_LOG" 2>/dev/null || echo "  (none)"

    echo ""
    echo "--- Recent Rejections (last 10) ---"
    tail -10 "$REJECTIONS_LOG" 2>/dev/null || echo "  (none)"

    echo ""
    echo "--- Handoffs (last 10) ---"
    tail -10 "$HANDOFFS_LOG" 2>/dev/null || echo "  (none)"

    echo ""
    echo "--- Audit Events (last 20) ---"
    tail -20 "$AUDIT_LOG" 2>/dev/null || echo "  (none)"
}

# STAMP: Add provenance to a memory entry
cmd_stamp() {
    local file="${1:-}"
    local rationale="${2:-No rationale provided}"
    local confidence="${3:-0.7}"

    if [ -z "$file" ]; then
        echo "Usage: memory-guard stamp <file> [rationale] [confidence]"
        return 1
    fi

    local stamp="<!-- [memory-guard] agent=$(whoami) | ts=$(timestamp) | confidence=$confidence | rationale=$rationale -->"

    if [ -f "$file" ]; then
        # Prepend stamp to file
        local tmp
        tmp=$(mktemp)
        echo "$stamp" > "$tmp"
        cat "$file" >> "$tmp"
        mv "$tmp" "$file"
        log_action "Stamped $file with provenance (confidence=$confidence)"
        echo "Provenance stamp added to $file"
    else
        echo "File not found: $file"
        return 1
    fi
}

# WATCH: One-shot verification for cron/heartbeat use
cmd_watch() {
    local result
    if result=$(cmd_verify 2>&1); then
        echo "MEMORY_GUARD_OK"
    else
        echo "MEMORY_GUARD_ALERT"
        echo "$result" | grep -E "(CRITICAL|CHANGED|MISSING)"
    fi
}

# Main dispatcher
case "${1:-help}" in
    init)    cmd_init ;;
    verify)  cmd_verify ;;
    accept)  cmd_accept "${2:-all}" ;;
    audit)   cmd_audit ;;
    stamp)   cmd_stamp "${2:-}" "${3:-}" "${4:-}" ;;
    watch)   cmd_watch ;;
    help|*)
        echo "Memory Guard - Agent Memory Integrity & Security"
        echo ""
        echo "Usage: memory-guard <command> [args]"
        echo ""
        echo "Commands:"
        echo "  init              Initialize integrity tracking"
        echo "  verify            Check all files for unauthorized changes"
        echo "  accept [file]     Accept current state as trusted (after review)"
        echo "  audit             Full audit report with logs"
        echo "  stamp <f> [r] [c] Add provenance header to a file"
        echo "  watch             One-shot verify for cron (returns OK or ALERT)"
        echo ""
        echo "Built by Nix - nixus.pro"
        ;;
esac
