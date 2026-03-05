#!/usr/bin/env bash
# smart-memory: memory-manager.sh
# Zero-cost persistent memory engine for OpenClaw
# All data stored locally as JSON — no external APIs, no cost.
#
# Usage:
#   memory-manager.sh <command> [options]
#
# Commands:
#   store       Store a new memory
#   search      Search memories by keyword
#   get         Get a specific memory by key
#   update      Update an existing memory
#   forget      Soft-delete a memory
#   maintain    Run daily maintenance (prune, dedup, integrity check)
#   log-saving  Log estimated token savings
#   export      Export all memories as JSON to stdout
#   purge       Permanently delete all memories
#   init        Initialize the memory store

set -euo pipefail

# ─── Configuration ───────────────────────────────────────────────────────────

MEMORY_DIR="${OPENCLAW_MEMORY_DIR:-$HOME/.openclaw/smart-memory}"
MEMORIES_FILE="$MEMORY_DIR/memories.json"
ARCHIVE_FILE="$MEMORY_DIR/archive.json"
STATS_FILE="$MEMORY_DIR/stats.json"
CONFIG_FILE="$MEMORY_DIR/config.json"
LOCK_FILE="$MEMORY_DIR/.lock"

# Defaults (overridden by config.json if present)
PRUNE_DAYS=90
MAX_MEMORIES=10000
ARCHIVE_RETENTION_DAYS=30

# ─── Helpers ─────────────────────────────────────────────────────────────────

die() { echo "ERROR: $*" >&2; exit 1; }
info() { echo "INFO: $*" >&2; }
now_iso() { date -u +"%Y-%m-%dT%H:%M:%SZ"; }
now_epoch() { date -u +%s; }

# Simple file-based lock to prevent concurrent writes
acquire_lock() {
    local attempts=0
    while [ -f "$LOCK_FILE" ]; do
        attempts=$((attempts + 1))
        if [ "$attempts" -gt 10 ]; then
            # Stale lock — remove if older than 60 seconds
            if [ -f "$LOCK_FILE" ]; then
                local lock_age
                lock_age=$(( $(now_epoch) - $(stat -c %Y "$LOCK_FILE" 2>/dev/null || echo 0) ))
                if [ "$lock_age" -gt 60 ]; then
                    rm -f "$LOCK_FILE"
                    break
                fi
            fi
            die "Could not acquire lock after 10 attempts"
        fi
        sleep 0.1
    done
    echo $$ > "$LOCK_FILE"
}

release_lock() {
    rm -f "$LOCK_FILE"
}

# Load config overrides
load_config() {
    if [ -f "$CONFIG_FILE" ]; then
        PRUNE_DAYS=$(jq -r '.prune_days // 90' "$CONFIG_FILE" 2>/dev/null || echo 90)
        MAX_MEMORIES=$(jq -r '.max_memories // 10000' "$CONFIG_FILE" 2>/dev/null || echo 10000)
        ARCHIVE_RETENTION_DAYS=$(jq -r '.archive_retention_days // 30' "$CONFIG_FILE" 2>/dev/null || echo 30)
    fi
}

# Ensure jq is available
require_jq() {
    command -v jq >/dev/null 2>&1 || die "jq is required but not installed. Install it: sudo apt install jq"
}

# ─── Init ────────────────────────────────────────────────────────────────────

cmd_init() {
    mkdir -p "$MEMORY_DIR"

    if [ ! -f "$MEMORIES_FILE" ]; then
        echo '{"memories":[],"version":"1.0.0","created":"'"$(now_iso)"'"}' | jq . > "$MEMORIES_FILE"
        info "Created memories store: $MEMORIES_FILE"
    fi

    if [ ! -f "$ARCHIVE_FILE" ]; then
        echo '{"archived":[],"version":"1.0.0"}' | jq . > "$ARCHIVE_FILE"
        info "Created archive: $ARCHIVE_FILE"
    fi

    if [ ! -f "$STATS_FILE" ]; then
        cat > "$STATS_FILE" <<'STATSJSON'
{
  "total_stores": 0,
  "total_retrievals": 0,
  "total_updates": 0,
  "total_deletes": 0,
  "total_tokens_saved": 0,
  "savings_log": [],
  "created": null,
  "last_maintenance": null
}
STATSJSON
        # Patch in the created timestamp
        local tmp
        tmp=$(jq --arg ts "$(now_iso)" '.created = $ts' "$STATS_FILE")
        echo "$tmp" > "$STATS_FILE"
        info "Created stats tracker: $STATS_FILE"
    fi

    if [ ! -f "$CONFIG_FILE" ]; then
        cat > "$CONFIG_FILE" <<'CONFJSON'
{
  "prune_days": 90,
  "max_memories": 10000,
  "archive_retention_days": 30,
  "auto_dedup": true,
  "confidence_threshold": "low"
}
CONFJSON
        info "Created default config: $CONFIG_FILE"
    fi

    echo "smart-memory initialized at $MEMORY_DIR"
}

# ─── Store ───────────────────────────────────────────────────────────────────

cmd_store() {
    local category="" key="" value="" confidence="medium" source="conversation"

    while [[ $# -gt 0 ]]; do
        case "$1" in
            --category)  category="$2";    shift 2 ;;
            --key)       key="$2";         shift 2 ;;
            --value)     value="$2";       shift 2 ;;
            --confidence) confidence="$2"; shift 2 ;;
            --source)    source="$2";      shift 2 ;;
            *) die "Unknown option for store: $1" ;;
        esac
    done

    [ -z "$key" ]   && die "Missing required --key"
    [ -z "$value" ] && die "Missing required --value"
    [ -z "$category" ] && category="general"

    # Validate confidence
    case "$confidence" in
        high|medium|low) ;;
        *) die "Invalid confidence: $confidence (must be high, medium, or low)" ;;
    esac

    acquire_lock
    trap release_lock EXIT

    # Check for duplicate key
    local existing
    existing=$(jq -r --arg k "$key" '.memories[] | select(.key == $k) | .key' "$MEMORIES_FILE" 2>/dev/null || true)
    if [ -n "$existing" ]; then
        info "Memory with key '$key' already exists. Use 'update' to modify it."
        release_lock
        trap - EXIT
        # Auto-update instead of failing
        cmd_update --key "$key" --value "$value" --reason "auto-updated via store (duplicate key)"
        return
    fi

    # Check memory limit
    local count
    count=$(jq '.memories | length' "$MEMORIES_FILE")
    if [ "$count" -ge "$MAX_MEMORIES" ]; then
        die "Memory limit reached ($MAX_MEMORIES). Run 'maintain' to prune old entries."
    fi

    # Build the new memory entry
    local timestamp
    timestamp=$(now_iso)
    local new_memory
    new_memory=$(jq -n \
        --arg key "$key" \
        --arg value "$value" \
        --arg category "$category" \
        --arg confidence "$confidence" \
        --arg source "$source" \
        --arg created "$timestamp" \
        --arg updated "$timestamp" \
        '{
            key: $key,
            value: $value,
            category: $category,
            confidence: $confidence,
            source: $source,
            created: $created,
            updated: $updated,
            access_count: 0,
            last_accessed: null,
            history: [],
            forgotten: false
        }')

    # Append to memories
    local updated_file
    updated_file=$(jq --argjson mem "$new_memory" '.memories += [$mem]' "$MEMORIES_FILE")
    echo "$updated_file" > "$MEMORIES_FILE"

    # Update stats
    local updated_stats
    updated_stats=$(jq '.total_stores += 1' "$STATS_FILE")
    echo "$updated_stats" > "$STATS_FILE"

    release_lock
    trap - EXIT

    echo "Stored memory: [$category] $key"
    echo "$new_memory" | jq .
}

# ─── Search ──────────────────────────────────────────────────────────────────

cmd_search() {
    local query="" category="" limit=10

    while [[ $# -gt 0 ]]; do
        case "$1" in
            --query)    query="$2";    shift 2 ;;
            --category) category="$2"; shift 2 ;;
            --limit)    limit="$2";    shift 2 ;;
            *) die "Unknown option for search: $1" ;;
        esac
    done

    [ -z "$query" ] && die "Missing required --query"

    # Convert query to lowercase for case-insensitive search
    local query_lower
    query_lower=$(echo "$query" | tr '[:upper:]' '[:lower:]')

    # Split query into individual words for multi-term matching
    local results
    if [ -n "$category" ]; then
        results=$(jq -r --arg q "$query_lower" --arg cat "$category" '
            .memories[]
            | select(.forgotten == false)
            | select(.category == $cat)
            | select(
                ((.key | ascii_downcase) | test($q)) or
                ((.value | ascii_downcase) | test($q)) or
                ((.category | ascii_downcase) | test($q))
            )
        ' "$MEMORIES_FILE" 2>/dev/null | jq -s '.' || echo '[]')
    else
        results=$(jq -r --arg q "$query_lower" '
            .memories[]
            | select(.forgotten == false)
            | select(
                ((.key | ascii_downcase) | test($q)) or
                ((.value | ascii_downcase) | test($q)) or
                ((.category | ascii_downcase) | test($q))
            )
        ' "$MEMORIES_FILE" 2>/dev/null | jq -s '.' || echo '[]')
    fi

    local count
    count=$(echo "$results" | jq 'length')

    if [ "$count" -eq 0 ]; then
        echo "No memories found matching: $query"
        return 0
    fi

    # Update access counts for matched memories
    acquire_lock
    trap release_lock EXIT

    local timestamp
    timestamp=$(now_iso)
    local keys_accessed
    keys_accessed=$(echo "$results" | jq -r '.[].key')

    while IFS= read -r accessed_key; do
        local updated_file
        updated_file=$(jq --arg k "$accessed_key" --arg ts "$timestamp" '
            .memories |= map(
                if .key == $k then
                    .access_count += 1 | .last_accessed = $ts
                else . end
            )
        ' "$MEMORIES_FILE")
        echo "$updated_file" > "$MEMORIES_FILE"
    done <<< "$keys_accessed"

    # Update retrieval stats
    local updated_stats
    updated_stats=$(jq --arg n "$count" '.total_retrievals += ($n | tonumber)' "$STATS_FILE")
    echo "$updated_stats" > "$STATS_FILE"

    release_lock
    trap - EXIT

    # Output results (limited)
    echo "$results" | jq --argjson lim "$limit" '.[:$lim]'
    echo ""
    echo "Found $count matching memories (showing up to $limit)"
}

# ─── Get ─────────────────────────────────────────────────────────────────────

cmd_get() {
    local key=""

    while [[ $# -gt 0 ]]; do
        case "$1" in
            --key) key="$2"; shift 2 ;;
            *) die "Unknown option for get: $1" ;;
        esac
    done

    [ -z "$key" ] && die "Missing required --key"

    local result
    result=$(jq --arg k "$key" '.memories[] | select(.key == $k and .forgotten == false)' "$MEMORIES_FILE" 2>/dev/null || true)

    if [ -z "$result" ]; then
        echo "No memory found with key: $key"
        return 1
    fi

    # Update access count
    acquire_lock
    trap release_lock EXIT

    local timestamp
    timestamp=$(now_iso)
    local updated_file
    updated_file=$(jq --arg k "$key" --arg ts "$timestamp" '
        .memories |= map(
            if .key == $k then
                .access_count += 1 | .last_accessed = $ts
            else . end
        )
    ' "$MEMORIES_FILE")
    echo "$updated_file" > "$MEMORIES_FILE"

    local updated_stats
    updated_stats=$(jq '.total_retrievals += 1' "$STATS_FILE")
    echo "$updated_stats" > "$STATS_FILE"

    release_lock
    trap - EXIT

    echo "$result" | jq .
}

# ─── Update ──────────────────────────────────────────────────────────────────

cmd_update() {
    local key="" value="" reason=""

    while [[ $# -gt 0 ]]; do
        case "$1" in
            --key)    key="$2";    shift 2 ;;
            --value)  value="$2";  shift 2 ;;
            --reason) reason="$2"; shift 2 ;;
            *) die "Unknown option for update: $1" ;;
        esac
    done

    [ -z "$key" ]   && die "Missing required --key"
    [ -z "$value" ] && die "Missing required --value"
    [ -z "$reason" ] && reason="updated"

    acquire_lock
    trap release_lock EXIT

    # Check memory exists
    local existing
    existing=$(jq --arg k "$key" '.memories[] | select(.key == $k)' "$MEMORIES_FILE" 2>/dev/null || true)
    if [ -z "$existing" ]; then
        release_lock
        trap - EXIT
        die "No memory found with key: $key"
    fi

    local old_value
    old_value=$(echo "$existing" | jq -r '.value')
    local timestamp
    timestamp=$(now_iso)

    # Update the memory, preserving old value in history
    local updated_file
    updated_file=$(jq --arg k "$key" --arg v "$value" --arg r "$reason" --arg ts "$timestamp" --arg old "$old_value" '
        .memories |= map(
            if .key == $k then
                .history += [{
                    old_value: $old,
                    changed_at: $ts,
                    reason: $r
                }]
                | .value = $v
                | .updated = $ts
            else . end
        )
    ' "$MEMORIES_FILE")
    echo "$updated_file" > "$MEMORIES_FILE"

    # Update stats
    local updated_stats
    updated_stats=$(jq '.total_updates += 1' "$STATS_FILE")
    echo "$updated_stats" > "$STATS_FILE"

    release_lock
    trap - EXIT

    echo "Updated memory: $key"
    echo "  Old: $old_value"
    echo "  New: $value"
    echo "  Reason: $reason"
}

# ─── Forget ──────────────────────────────────────────────────────────────────

cmd_forget() {
    local key=""

    while [[ $# -gt 0 ]]; do
        case "$1" in
            --key) key="$2"; shift 2 ;;
            *) die "Unknown option for forget: $1" ;;
        esac
    done

    [ -z "$key" ] && die "Missing required --key"

    acquire_lock
    trap release_lock EXIT

    local existing
    existing=$(jq --arg k "$key" '.memories[] | select(.key == $k)' "$MEMORIES_FILE" 2>/dev/null || true)
    if [ -z "$existing" ]; then
        release_lock
        trap - EXIT
        die "No memory found with key: $key"
    fi

    local timestamp
    timestamp=$(now_iso)

    # Soft-delete: mark as forgotten and move to archive
    local updated_file
    updated_file=$(jq --arg k "$key" --arg ts "$timestamp" '
        .memories |= map(
            if .key == $k then
                .forgotten = true | .forgotten_at = $ts
            else . end
        )
    ' "$MEMORIES_FILE")
    echo "$updated_file" > "$MEMORIES_FILE"

    # Copy to archive
    local archived_entry
    archived_entry=$(echo "$existing" | jq --arg ts "$timestamp" '. + {forgotten: true, forgotten_at: $ts}')
    local updated_archive
    updated_archive=$(jq --argjson entry "$archived_entry" '.archived += [$entry]' "$ARCHIVE_FILE")
    echo "$updated_archive" > "$ARCHIVE_FILE"

    # Update stats
    local updated_stats
    updated_stats=$(jq '.total_deletes += 1' "$STATS_FILE")
    echo "$updated_stats" > "$STATS_FILE"

    release_lock
    trap - EXIT

    echo "Forgotten memory: $key (archived for $ARCHIVE_RETENTION_DAYS days)"
}

# ─── Log Token Savings ──────────────────────────────────────────────────────

cmd_log_saving() {
    local tokens=0

    while [[ $# -gt 0 ]]; do
        case "$1" in
            --tokens) tokens="$2"; shift 2 ;;
            *) die "Unknown option for log-saving: $1" ;;
        esac
    done

    [ "$tokens" -eq 0 ] && die "Missing or zero --tokens"

    acquire_lock
    trap release_lock EXIT

    local timestamp
    timestamp=$(now_iso)
    local updated_stats
    updated_stats=$(jq --arg t "$tokens" --arg ts "$timestamp" '
        .total_tokens_saved += ($t | tonumber)
        | .savings_log += [{tokens: ($t | tonumber), timestamp: $ts}]
        | .savings_log = (.savings_log | .[-100:])
    ' "$STATS_FILE")
    echo "$updated_stats" > "$STATS_FILE"

    release_lock
    trap - EXIT

    local total
    total=$(echo "$updated_stats" | jq '.total_tokens_saved')
    echo "Logged $tokens tokens saved. Total lifetime savings: $total tokens"
}

# ─── Maintain ────────────────────────────────────────────────────────────────

cmd_maintain() {
    info "Starting daily maintenance..."

    acquire_lock
    trap release_lock EXIT

    local timestamp
    timestamp=$(now_iso)
    local cutoff_epoch
    cutoff_epoch=$(( $(now_epoch) - (PRUNE_DAYS * 86400) ))
    local archive_cutoff_epoch
    archive_cutoff_epoch=$(( $(now_epoch) - (ARCHIVE_RETENTION_DAYS * 86400) ))

    # 1. Prune stale low-confidence memories
    local pruned_count=0
    local to_prune
    to_prune=$(jq --arg days "$PRUNE_DAYS" '
        [.memories[] | select(
            .confidence == "low"
            and .forgotten == false
            and .access_count == 0
            and ((.created | split("T")[0] | split("-") | map(tonumber)) as [$y,$m,$d] |
                 (now - ([$y,$m,$d,0,0,0,0] | mktime)) > (($days | tonumber) * 86400))
        ) | .key]
    ' "$MEMORIES_FILE" 2>/dev/null || echo '[]')

    pruned_count=$(echo "$to_prune" | jq 'length')
    if [ "$pruned_count" -gt 0 ]; then
        # Move pruned memories to archive
        local pruned_memories
        pruned_memories=$(jq --argjson keys "$to_prune" '
            [.memories[] | select(.key as $k | $keys | index($k) != null)]
            | map(. + {pruned: true, pruned_at: "'"$timestamp"'"})
        ' "$MEMORIES_FILE")

        local updated_archive
        updated_archive=$(jq --argjson entries "$pruned_memories" '.archived += $entries' "$ARCHIVE_FILE")
        echo "$updated_archive" > "$ARCHIVE_FILE"

        # Remove from active memories
        local updated_file
        updated_file=$(jq --argjson keys "$to_prune" '
            .memories |= [.[] | select(.key as $k | $keys | index($k) == null)]
        ' "$MEMORIES_FILE")
        echo "$updated_file" > "$MEMORIES_FILE"
        info "Pruned $pruned_count stale low-confidence memories"
    fi

    # 2. Remove forgotten memories from active store (already in archive)
    local forgotten_removed
    forgotten_removed=$(jq '[.memories[] | select(.forgotten == true)] | length' "$MEMORIES_FILE")
    if [ "$forgotten_removed" -gt 0 ]; then
        local updated_file
        updated_file=$(jq '.memories |= [.[] | select(.forgotten == false)]' "$MEMORIES_FILE")
        echo "$updated_file" > "$MEMORIES_FILE"
        info "Removed $forgotten_removed forgotten memories from active store"
    fi

    # 3. Clean old archive entries
    local archive_cleaned=0
    archive_cleaned=$(jq --arg days "$ARCHIVE_RETENTION_DAYS" '
        [.archived[] | select(
            ((.forgotten_at // .pruned_at // .created) | split("T")[0] | split("-") | map(tonumber)) as [$y,$m,$d] |
            (now - ([$y,$m,$d,0,0,0,0] | mktime)) > (($days | tonumber) * 86400)
        )] | length
    ' "$ARCHIVE_FILE" 2>/dev/null || echo 0)

    if [ "$archive_cleaned" -gt 0 ]; then
        local updated_archive
        updated_archive=$(jq --arg days "$ARCHIVE_RETENTION_DAYS" '
            .archived |= [.[] | select(
                ((.forgotten_at // .pruned_at // .created) | split("T")[0] | split("-") | map(tonumber)) as [$y,$m,$d] |
                (now - ([$y,$m,$d,0,0,0,0] | mktime)) <= (($days | tonumber) * 86400)
            )]
        ' "$ARCHIVE_FILE")
        echo "$updated_archive" > "$ARCHIVE_FILE"
        info "Cleaned $archive_cleaned expired archive entries"
    fi

    # 4. Deduplicate — find memories with identical values
    local dedup_count=0
    local dedup_keys
    dedup_keys=$(jq '
        [.memories | group_by(.value)[] | select(length > 1) | .[1:][].key]
    ' "$MEMORIES_FILE" 2>/dev/null || echo '[]')
    dedup_count=$(echo "$dedup_keys" | jq 'length')

    if [ "$dedup_count" -gt 0 ]; then
        local updated_file
        updated_file=$(jq --argjson keys "$dedup_keys" '
            .memories |= [.[] | select(.key as $k | $keys | index($k) == null)]
        ' "$MEMORIES_FILE")
        echo "$updated_file" > "$MEMORIES_FILE"
        info "Removed $dedup_count duplicate memories"
    fi

    # 5. Integrity check — ensure valid JSON
    if ! jq empty "$MEMORIES_FILE" 2>/dev/null; then
        die "CRITICAL: memories.json is corrupted! Attempting recovery..."
    fi
    if ! jq empty "$ARCHIVE_FILE" 2>/dev/null; then
        die "CRITICAL: archive.json is corrupted!"
    fi

    # 6. Update maintenance timestamp
    local updated_stats
    updated_stats=$(jq --arg ts "$timestamp" '.last_maintenance = $ts' "$STATS_FILE")
    echo "$updated_stats" > "$STATS_FILE"

    release_lock
    trap - EXIT

    # Summary
    local active_count
    active_count=$(jq '.memories | length' "$MEMORIES_FILE")
    local archive_count
    archive_count=$(jq '.archived | length' "$ARCHIVE_FILE")

    echo "=== Maintenance Complete ==="
    echo "Active memories:  $active_count"
    echo "Archived:         $archive_count"
    echo "Pruned this run:  $pruned_count"
    echo "Deduped this run: $dedup_count"
    echo "Archive cleaned:  $archive_cleaned"
    echo "All files valid:  YES"
    echo "Timestamp:        $timestamp"
}

# ─── Export ──────────────────────────────────────────────────────────────────

cmd_export() {
    jq '{
        memories: .memories,
        exported_at: now | todate,
        count: (.memories | length)
    }' "$MEMORIES_FILE"
}

# ─── Purge ───────────────────────────────────────────────────────────────────

cmd_purge() {
    local confirm=""

    while [[ $# -gt 0 ]]; do
        case "$1" in
            --confirm) confirm="yes"; shift ;;
            *) die "Unknown option for purge: $1" ;;
        esac
    done

    if [ "$confirm" != "yes" ]; then
        die "Purge requires --confirm flag. This will PERMANENTLY delete all memories."
    fi

    acquire_lock
    trap release_lock EXIT

    echo '{"memories":[],"version":"1.0.0","created":"'"$(now_iso)"'","purged":true}' | jq . > "$MEMORIES_FILE"
    echo '{"archived":[],"version":"1.0.0"}' | jq . > "$ARCHIVE_FILE"

    local updated_stats
    updated_stats=$(jq --arg ts "$(now_iso)" '. + {
        total_stores: 0,
        total_retrievals: 0,
        total_updates: 0,
        total_deletes: 0,
        last_maintenance: $ts
    }' "$STATS_FILE")
    echo "$updated_stats" > "$STATS_FILE"

    release_lock
    trap - EXIT

    echo "All memories have been permanently deleted."
}

# ─── Main ────────────────────────────────────────────────────────────────────

main() {
    require_jq

    local command="${1:-help}"
    shift || true

    # Auto-init if memory directory doesn't exist
    if [ "$command" != "init" ] && [ ! -f "$MEMORIES_FILE" ]; then
        info "Memory store not found. Initializing..."
        cmd_init
    fi

    load_config

    case "$command" in
        init)        cmd_init ;;
        store)       cmd_store "$@" ;;
        search)      cmd_search "$@" ;;
        get)         cmd_get "$@" ;;
        update)      cmd_update "$@" ;;
        forget)      cmd_forget "$@" ;;
        maintain)    cmd_maintain ;;
        log-saving)  cmd_log_saving "$@" ;;
        export)      cmd_export ;;
        purge)       cmd_purge "$@" ;;
        help|--help|-h)
            echo "smart-memory: Zero-cost persistent memory for OpenClaw"
            echo ""
            echo "Usage: memory-manager.sh <command> [options]"
            echo ""
            echo "Commands:"
            echo "  init                         Initialize the memory store"
            echo "  store     --key --value ...   Store a new memory"
            echo "  search    --query ...         Search memories by keyword"
            echo "  get       --key ...           Get a specific memory"
            echo "  update    --key --value ...   Update an existing memory"
            echo "  forget    --key ...           Soft-delete a memory"
            echo "  maintain                      Run daily maintenance"
            echo "  log-saving --tokens N         Log estimated token savings"
            echo "  export                        Export all memories as JSON"
            echo "  purge     --confirm           Delete everything permanently"
            echo ""
            echo "Run with no arguments or 'help' to see this message."
            ;;
        *)
            die "Unknown command: $command. Run with 'help' for usage."
            ;;
    esac
}

main "$@"
