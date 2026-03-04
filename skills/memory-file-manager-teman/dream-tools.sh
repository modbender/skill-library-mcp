#!/usr/bin/env bash
# dream-tools.sh — Dream skill utility script
# All precise calculations, file operations, and date arithmetic are handled here; AI does no mental math
# Dependencies: jq, wc, md5sum (macOS uses md5), openclaw CLI
# Usage: dream-tools.sh <--command> [args...]

set -euo pipefail

# ── Environment Variables ───────────────────────────────────────────────────

DREAM_VAULT_PATH="${DREAM_VAULT_PATH:-$HOME/Documents/Obsidian/dream-vault}"
WORKSPACE_PATH="${OPENCLAW_WORKSPACE:-$HOME/.openclaw/workspace}"
MEMORY_MD="$WORKSPACE_PATH/MEMORY.md"
LEDGER_MD="$DREAM_VAULT_PATH/ledger.md"
LEDGER_INDEX="$DREAM_VAULT_PATH/ledger-index.json"
REMOVED_ENTRIES="$DREAM_VAULT_PATH/meta/removed-entries.json"
OBSIDIAN_INDEX="$DREAM_VAULT_PATH/obsidian-index/_index.md"
MEMORY_HARD_LIMIT=18000
MEMORY_COMPRESS_TRIGGER=16000

# ── Utility Functions ───────────────────────────────────────────────────────

log() { echo "[dream-tools] $*" >&2; }

die() { echo "[dream-tools] ERROR: $*" >&2; exit 1; }

# Cross-platform MD5 (macOS uses md5, Linux uses md5sum)
md5_hash() {
    local input="$1"
    if command -v md5sum &>/dev/null; then
        echo -n "$input" | md5sum | cut -c1-8
    elif command -v md5 &>/dev/null; then
        echo -n "$input" | md5 -q | cut -c1-8
    else
        die "Neither md5sum nor md5 command found"
    fi
}

# Ensure parent directory exists
ensure_dir() { mkdir -p "$(dirname "$1")"; }

# ── Command Implementations ─────────────────────────────────────────────────

# --check-idle
# Check if OpenClaw is idle; returns "idle" or "busy"
# Defaults to "busy" after 5s timeout to avoid hanging when gateway is unresponsive
cmd_check_idle() {
    local status
    status=$(timeout 5s openclaw agent status 2>/dev/null) || {
        echo "busy"
        return 0
    }
    # Treat output containing "running" / "active" / "processing" / "busy" as busy
    if echo "$status" | grep -qiE "running|active|processing|busy"; then
        echo "busy"
    else
        echo "idle"
    fi
}

# --check-size
# Returns current character count of MEMORY.md
# Output format: <current_chars> <compress_trigger> <hard_limit> <status:ok|warn|critical>
cmd_check_size() {
    if [[ ! -f "$MEMORY_MD" ]]; then
        echo "0 $MEMORY_COMPRESS_TRIGGER $MEMORY_HARD_LIMIT ok"
        return 0
    fi
    local size
    size=$(wc -c < "$MEMORY_MD" | tr -d ' ')
    local state="ok"
    if [[ $size -ge $MEMORY_HARD_LIMIT ]]; then
        state="critical"
    elif [[ $size -ge $MEMORY_COMPRESS_TRIGGER ]]; then
        state="warn"
    fi
    echo "$size $MEMORY_COMPRESS_TRIGGER $MEMORY_HARD_LIMIT $state"
}

# --hash "<content>"
# Outputs an 8-character short hash for entry ID generation and deduplication
cmd_hash() {
    local input="${1:-}"
    [[ -z "$input" ]] && die "--hash requires a content argument"
    md5_hash "$input"
}

# --atomic-write <target-file> <tmp-file>
# Verifies tmp-file exists and does not exceed the hard limit, then atomically replaces target-file
# For MEMORY.md targets, also enforces character count; other files only check existence
cmd_atomic_write() {
    local target="${1:-}"
    local tmpfile="${2:-}"
    [[ -z "$target" || -z "$tmpfile" ]] && die "--atomic-write requires <target> <tmpfile>"
    [[ ! -f "$tmpfile" ]] && die "tmp file does not exist: $tmpfile"

    # If target is MEMORY.md, check character count limit
    if [[ "$(realpath "$target" 2>/dev/null)" == "$(realpath "$MEMORY_MD" 2>/dev/null)" ]] || \
       [[ "$target" == *"MEMORY.md" ]]; then
        local size
        size=$(wc -c < "$tmpfile" | tr -d ' ')
        if [[ $size -gt $MEMORY_HARD_LIMIT ]]; then
            die "Write aborted: tmp file size ${size} chars exceeds hard limit ${MEMORY_HARD_LIMIT}. Please compress content first."
        fi
        log "MEMORY.md write validation passed: ${size}/${MEMORY_HARD_LIMIT} chars"
    fi

    ensure_dir "$target"
    # mv is atomic on the same filesystem
    mv "$tmpfile" "$target"
    log "Atomic write complete: $target"
}

# --ledger-append <id> <category> <content> [<note>]
# Appends a record block to ledger.md and updates ledger-index.json
cmd_ledger_append() {
    local id="${1:-}"
    local category="${2:-}"
    local content="${3:-}"
    local note="${4:-First archived}"
    [[ -z "$id" || -z "$category" || -z "$content" ]] && \
        die "--ledger-append requires <id> <category> <content>"

    ensure_dir "$LEDGER_MD"
    ensure_dir "$LEDGER_INDEX"

    local timestamp
    timestamp=$(date '+%Y-%m-%d %H:%M')
    local datestamp
    datestamp=$(date '+%Y-%m-%d')

    # Append block to ledger.md
    cat >> "$LEDGER_MD" << EOF

---
ID: $id
Archived: $timestamp
Category: $category
Content: $content
Note: $note
---
EOF

    # Update ledger-index.json
    # Initialize as empty array if file missing or empty
    if [[ ! -f "$LEDGER_INDEX" ]] || [[ ! -s "$LEDGER_INDEX" ]]; then
        echo '[]' > "$LEDGER_INDEX"
    fi

    # Check if ID already exists
    local exists
    exists=$(jq --arg id "$id" 'any(.[]; .id == $id)' "$LEDGER_INDEX")

    if [[ "$exists" == "true" ]]; then
        # Exists: append event record to this entry's events array
        local tmp_index
        tmp_index=$(mktemp)
        jq --arg id "$id" \
           --arg ts "$timestamp" \
           --arg note "$note" \
           'map(if .id == $id then
               .events += [{"time": $ts, "note": $note}] |
               .last_updated = $ts
           else . end)' \
           "$LEDGER_INDEX" > "$tmp_index"
        mv "$tmp_index" "$LEDGER_INDEX"
        log "ledger-index updated (event appended to existing entry): $id"
    else
        # New entry
        local tmp_index
        tmp_index=$(mktemp)
        jq --arg id "$id" \
           --arg category "$category" \
           --arg content "$content" \
           --arg ts "$timestamp" \
           --arg date "$datestamp" \
           --arg note "$note" \
           '. += [{
               "id": $id,
               "category": $category,
               "summary": ($content | .[0:80]),
               "first_archived": $date,
               "last_updated": $ts,
               "status": "active",
               "events": [{"time": $ts, "note": $note}]
           }]' \
           "$LEDGER_INDEX" > "$tmp_index"
        mv "$tmp_index" "$LEDGER_INDEX"
        log "ledger-index new entry: $id"
    fi

    log "Ledger append complete: [$category] ${content:0:60}..."
}

# --ledger-search "<keyword>"
# Searches ledger-index.json and outputs matching entries: ID, category, summary, archive date
cmd_ledger_search() {
    local keyword="${1:-}"
    [[ -z "$keyword" ]] && die "--ledger-search requires a keyword"
    [[ ! -f "$LEDGER_INDEX" ]] && { echo "[]"; return 0; }

    # Case-insensitive string match against summary and category
    jq --arg kw "$keyword" \
       '[.[] | select(
           (.summary | ascii_downcase | contains($kw | ascii_downcase)) or
           (.category | ascii_downcase | contains($kw | ascii_downcase))
       ) | {id, category, summary, first_archived, status}]' \
       "$LEDGER_INDEX"
}

# --ledger-mark-reemergence <id>
# Marks the specified entry as re-emerged and appends an event record to ledger
cmd_ledger_mark_reemergence() {
    local id="${1:-}"
    [[ -z "$id" ]] && die "--ledger-mark-reemergence requires an ID"
    [[ ! -f "$LEDGER_INDEX" ]] && die "ledger-index.json does not exist"

    local timestamp
    timestamp=$(date '+%Y-%m-%d %H:%M')

    # Append event to ledger.md
    cat >> "$LEDGER_MD" << EOF

---
ID: $id
Updated: $timestamp
Event: re-emerged
Note: This entry was previously forgotten and reappeared in a later conversation; priority elevated
---
EOF

    # Update status and events in ledger-index.json
    local tmp_index
    tmp_index=$(mktemp)
    jq --arg id "$id" \
       --arg ts "$timestamp" \
       'map(if .id == $id then
           .status = "re-emerged" |
           .last_updated = $ts |
           .events += [{"time": $ts, "note": "re-emerged"}]
       else . end)' \
       "$LEDGER_INDEX" > "$tmp_index"
    mv "$tmp_index" "$LEDGER_INDEX"
    log "ledger re-emergence marked: $id"
}

# --dedup-index "<url-or-hash>"
# Checks whether obsidian-index/_index.md already contains this entry
# Returns: exists or new
cmd_dedup_index() {
    local input="${1:-}"
    [[ -z "$input" ]] && die "--dedup-index requires a URL or hash"

    if [[ ! -f "$OBSIDIAN_INDEX" ]]; then
        echo "new"
        return 0
    fi

    local hash
    hash=$(md5_hash "$input")

    # Search the index file for the original URL or its hash
    if grep -qF "$input" "$OBSIDIAN_INDEX" 2>/dev/null || \
       grep -qF "$hash" "$OBSIDIAN_INDEX" 2>/dev/null; then
        echo "exists"
    else
        echo "new"
    fi
}

# --record-removed "<id>" "<summary>" "<content-hash>"
# Writes a removed MEMORY.md entry to removed-entries.json (for Re-emergence detection)
cmd_record_removed() {
    local id="${1:-}"
    local summary="${2:-}"
    local content_hash="${3:-}"
    [[ -z "$id" || -z "$summary" ]] && die "--record-removed requires <id> <summary>"

    ensure_dir "$REMOVED_ENTRIES"

    if [[ ! -f "$REMOVED_ENTRIES" ]] || [[ ! -s "$REMOVED_ENTRIES" ]]; then
        echo '[]' > "$REMOVED_ENTRIES"
    fi

    local timestamp
    timestamp=$(date '+%Y-%m-%d %H:%M')
    local datestamp
    datestamp=$(date '+%Y-%m-%d')

    local tmp
    tmp=$(mktemp)
    jq --arg id "$id" \
       --arg summary "$summary" \
       --arg hash "$content_hash" \
       --arg ts "$timestamp" \
       --arg date "$datestamp" \
       '. += [{
           "id": $id,
           "summary": $summary,
           "content_hash": $hash,
           "removed_at": $date,
           "removed_ts": $ts,
           "reemergence_count": 0
       }]' \
       "$REMOVED_ENTRIES" > "$tmp"
    mv "$tmp" "$REMOVED_ENTRIES"
    log "removed-entries recorded: $id"
}

# --check-reemergence "<content>"
# Checks whether new content is similar to a previously removed entry
# Current implementation: keyword matching (sufficient accuracy, avoids vector dependency)
# Returns: matched <id> <summary>  OR  no-match
cmd_check_reemergence() {
    local content="${1:-}"
    [[ -z "$content" ]] && die "--check-reemergence requires content"
    [[ ! -f "$REMOVED_ENTRIES" ]] && { echo "no-match"; return 0; }

    # Extract keywords from content (strip common stop words, take first 5 meaningful words)
    local keywords
    keywords=$(echo "$content" | \
        tr '[:upper:]' '[:lower:]' | \
        grep -oE '[a-z\u4e00-\u9fa5]{2,}' | \
        grep -vE '^(the|and|for|with|that|this|from|have|will|been|they|them|a|an|is|in|on|at|to|of|or|by|as|be|it|we|do|so|if|no|up|he|she|my|we|us|me)$' | \
        head -5 | tr '\n' '|' | sed 's/|$//')

    if [[ -z "$keywords" ]]; then
        echo "no-match"
        return 0
    fi

    # Search keywords in removed-entries summaries
    local match
    match=$(jq --arg pattern "$keywords" \
        '[.[] | select(.summary | test($pattern; "i"))] | first // empty' \
        "$REMOVED_ENTRIES" 2>/dev/null)

    if [[ -n "$match" && "$match" != "null" ]]; then
        local matched_id matched_summary
        matched_id=$(echo "$match" | jq -r '.id')
        matched_summary=$(echo "$match" | jq -r '.summary')

        # Increment reemergence_count
        local tmp
        tmp=$(mktemp)
        jq --arg id "$matched_id" \
            'map(if .id == $id then
                .reemergence_count += 1
            else . end)' \
            "$REMOVED_ENTRIES" > "$tmp"
        mv "$tmp" "$REMOVED_ENTRIES"

        echo "matched $matched_id $matched_summary"
    else
        echo "no-match"
    fi
}

# --active-days-since "<YYYY-MM-DD>"
# Counts active days recorded in active-days.json since the given date
cmd_active_days_since() {
    local since="${1:-}"
    [[ -z "$since" ]] && die "--active-days-since requires a date (YYYY-MM-DD)"

    local active_days_file="$DREAM_VAULT_PATH/meta/active-days.json"
    if [[ ! -f "$active_days_file" ]]; then
        echo "0"
        return 0
    fi

    jq --arg since "$since" \
        '[.[] | select(. >= $since)] | length' \
        "$active_days_file"
}

# --record-active-day
# Adds today to active-days.json (deduplicated)
cmd_record_active_day() {
    local active_days_file="$DREAM_VAULT_PATH/meta/active-days.json"
    ensure_dir "$active_days_file"

    local today
    today=$(date '+%Y-%m-%d')

    if [[ ! -f "$active_days_file" ]] || [[ ! -s "$active_days_file" ]]; then
        echo '[]' > "$active_days_file"
    fi

    local tmp
    tmp=$(mktemp)
    jq --arg today "$today" \
        'if any(.[]; . == $today) then . else . += [$today] | sort end' \
        "$active_days_file" > "$tmp"
    mv "$tmp" "$active_days_file"
    log "Active day recorded: $today"
}

# --init
# Initializes the Dream vault directory structure
cmd_init() {
    log "Initializing Dream vault: $DREAM_VAULT_PATH"

    mkdir -p "$DREAM_VAULT_PATH/meta"
    mkdir -p "$DREAM_VAULT_PATH/obsidian-index/topics"

    # Initialize JSON files
    [[ ! -f "$LEDGER_INDEX" ]]      && echo '[]' > "$LEDGER_INDEX"
    [[ ! -f "$REMOVED_ENTRIES" ]]   && echo '[]' > "$REMOVED_ENTRIES"
    [[ ! -f "$DREAM_VAULT_PATH/meta/active-days.json" ]] && \
        echo '[]' > "$DREAM_VAULT_PATH/meta/active-days.json"

    # Initialize dream-state.txt
    if [[ ! -f "$DREAM_VAULT_PATH/meta/dream-state.txt" ]]; then
        echo "active" > "$DREAM_VAULT_PATH/meta/dream-state.txt"
    fi

    # Initialize ledger.md with header
    if [[ ! -f "$LEDGER_MD" ]]; then
        cat > "$LEDGER_MD" << 'EOF'
# Dream Ledger — Permanent Archive

> Append-only, never deleted. Each record represents content that once reached long-term memory.
> Even if forgotten or removed, the historical record is permanently preserved.

EOF
    fi

    # Initialize obsidian-index/_index.md
    if [[ ! -f "$OBSIDIAN_INDEX" ]]; then
        cat > "$OBSIDIAN_INDEX" << 'EOF'
# Obsidian Content Index

> Maintained by the Dream skill. Structured index of articles, notes, and web pages, in reverse chronological order.

EOF
    fi

    log "Initialization complete"
    echo "ok"
}

# --status
# Outputs a Dream system status summary (low IO, read-only meta)
cmd_status() {
    local state_file="$DREAM_VAULT_PATH/meta/dream-state.txt"
    local last_review_file="$DREAM_VAULT_PATH/meta/last-review.txt"
    local active_days_file="$DREAM_VAULT_PATH/meta/active-days.json"

    local state="unknown"
    [[ -f "$state_file" ]] && state=$(cat "$state_file")

    local last_review="Never"
    local hours_since="-"
    if [[ -f "$last_review_file" ]]; then
        last_review=$(cat "$last_review_file")
        # Calculate hours since last distillation
        if command -v python3 &>/dev/null; then
            hours_since=$(python3 -c "
from datetime import datetime
last = datetime.strptime('$last_review', '%Y-%m-%d %H:%M')
diff = datetime.now() - last
print(int(diff.total_seconds() / 3600))
" 2>/dev/null || echo "-")
        fi
    fi

    local memory_size=0
    [[ -f "$MEMORY_MD" ]] && memory_size=$(wc -c < "$MEMORY_MD" | tr -d ' ')

    local ledger_count=0
    [[ -f "$LEDGER_INDEX" ]] && \
        ledger_count=$(jq 'length' "$LEDGER_INDEX" 2>/dev/null || echo 0)

    local active_days=0
    [[ -f "$active_days_file" ]] && \
        active_days=$(jq 'length' "$active_days_file" 2>/dev/null || echo 0)

    local obsidian_count=0
    [[ -f "$OBSIDIAN_INDEX" ]] && \
        obsidian_count=$(grep -c '^## ' "$OBSIDIAN_INDEX" 2>/dev/null || echo 0)

    cat << EOF
MEMORY.md: ${memory_size} chars / ${MEMORY_HARD_LIMIT} limit
Permanent archive: ${ledger_count} records
Active days: ${active_days} days
Last distillation: ${last_review} (${hours_since} hours ago)
System state: ${state}
Obsidian index: ${obsidian_count} entries
EOF
}

# ── Main Entry Point ─────────────────────────────────────────────────────────

CMD="${1:-}"
shift || true

case "$CMD" in
    --check-idle)             cmd_check_idle ;;
    --check-size)             cmd_check_size ;;
    --hash)                   cmd_hash "$@" ;;
    --atomic-write)           cmd_atomic_write "$@" ;;
    --ledger-append)          cmd_ledger_append "$@" ;;
    --ledger-search)          cmd_ledger_search "$@" ;;
    --ledger-mark-reemergence) cmd_ledger_mark_reemergence "$@" ;;
    --dedup-index)            cmd_dedup_index "$@" ;;
    --record-removed)         cmd_record_removed "$@" ;;
    --check-reemergence)      cmd_check_reemergence "$@" ;;
    --active-days-since)      cmd_active_days_since "$@" ;;
    --record-active-day)      cmd_record_active_day ;;
    --init)                   cmd_init ;;
    --status)                 cmd_status ;;
    *)
        cat << 'EOF'
Usage: dream-tools.sh <command> [args...]

Commands:
  --check-idle                        Check if OpenClaw is idle (returns idle/busy)
  --check-size                        Return MEMORY.md character count and status
  --hash "<content>"                  Generate 8-char short hash (for ID generation/dedup)
  --atomic-write <target> <tmpfile>   Atomically replace file (with MEMORY.md char count check)
  --ledger-append <id> <cat> <content> [note]  Append a record to ledger
  --ledger-search "<keyword>"         Search ledger-index.json
  --ledger-mark-reemergence <id>      Mark a ledger entry as re-emerged
  --dedup-index "<url-or-hash>"       Check if obsidian-index already has this entry
  --record-removed <id> <summary> <hash>  Record an entry removed from MEMORY.md
  --check-reemergence "<content>"     Check if content matches a previously removed entry
  --active-days-since "<YYYY-MM-DD>"  Count active days since given date
  --record-active-day                 Record today as an active day
  --init                              Initialize Dream vault directory structure
  --status                            Output system status summary

Environment Variables:
  DREAM_VAULT_PATH    Dream vault path (default: ~/Documents/Obsidian/dream-vault)
  OPENCLAW_WORKSPACE  OpenClaw workspace path (default: ~/.openclaw/workspace)
EOF
        exit 1
        ;;
esac
