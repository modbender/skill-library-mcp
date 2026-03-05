#!/usr/bin/env bash
set -euo pipefail

# Debate Moderator — Scoreboard CLI
# SQLite-backed scoreboard for tracking debate results.
#
# Usage:
#   scoreboard.sh init                                  Create the database
#   scoreboard.sh record <winner> <loser> <topic> [fmt] Record a debate result
#   scoreboard.sh leaderboard                           Show standings
#   scoreboard.sh history [--limit N]                   Show recent debates
#   scoreboard.sh stats <participant>                   Individual stats
#   scoreboard.sh reset                                 Clear all data
#
# Environment:
#   DEBATE_SCOREBOARD_DB  Path to SQLite DB (default: ./data/scoreboard.db)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
DB="${DEBATE_SCOREBOARD_DB:-$SKILL_DIR/data/scoreboard.db}"

# Ensure sqlite3 is available
if ! command -v sqlite3 &>/dev/null; then
    echo "Error: sqlite3 is required but not found in PATH." >&2
    exit 1
fi

usage() {
    cat <<'EOF'
Debate Scoreboard CLI

Commands:
  init                                  Create/initialize the database
  record <winner> <loser> <topic> [fmt] Record a debate result
  leaderboard                           Show win/loss/winrate standings
  history [--limit N]                   Show recent debates (default: 10)
  stats <participant>                   Show individual stats
  reset                                 Clear all data (requires confirmation)

Environment:
  DEBATE_SCOREBOARD_DB    Path to SQLite database
                          Default: ./data/scoreboard.db
EOF
}

ensure_db() {
    if [[ ! -f "$DB" ]]; then
        echo "Error: Database not found at $DB" >&2
        echo "Run 'scoreboard.sh init' first." >&2
        exit 1
    fi
}

cmd_init() {
    local db_dir
    db_dir="$(dirname "$DB")"
    mkdir -p "$db_dir"

    sqlite3 "$DB" <<'SQL'
CREATE TABLE IF NOT EXISTS debates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    winner TEXT NOT NULL,
    loser TEXT NOT NULL,
    topic TEXT NOT NULL,
    format TEXT DEFAULT 'campfire',
    created_at DATETIME DEFAULT (datetime('now')),
    notes TEXT
);

CREATE TABLE IF NOT EXISTS participants (
    name TEXT PRIMARY KEY,
    wins INTEGER DEFAULT 0,
    losses INTEGER DEFAULT 0,
    draws INTEGER DEFAULT 0,
    first_debate DATETIME,
    last_debate DATETIME
);

CREATE INDEX IF NOT EXISTS idx_debates_winner ON debates(winner);
CREATE INDEX IF NOT EXISTS idx_debates_loser ON debates(loser);
CREATE INDEX IF NOT EXISTS idx_debates_created ON debates(created_at DESC);
SQL

    echo "Scoreboard initialized at $DB"
}

cmd_record() {
    local winner="${1:-}"
    local loser="${2:-}"
    local topic="${3:-}"
    local format="${4:-campfire}"

    if [[ -z "$winner" || -z "$loser" || -z "$topic" ]]; then
        echo "Usage: scoreboard.sh record <winner> <loser> <topic> [format]" >&2
        exit 1
    fi

    ensure_db

    local now
    now="$(date -u '+%Y-%m-%dT%H:%M:%SZ')"

    sqlite3 "$DB" <<SQL
INSERT INTO debates (winner, loser, topic, format) VALUES ('$(echo "$winner" | sed "s/'/''/g")', '$(echo "$loser" | sed "s/'/''/g")', '$(echo "$topic" | sed "s/'/''/g")', '$(echo "$format" | sed "s/'/''/g")');

INSERT INTO participants (name, wins, losses, draws, first_debate, last_debate)
VALUES ('$(echo "$winner" | sed "s/'/''/g")', 1, 0, 0, datetime('now'), datetime('now'))
ON CONFLICT(name) DO UPDATE SET
    wins = wins + 1,
    last_debate = datetime('now');

INSERT INTO participants (name, wins, losses, draws, first_debate, last_debate)
VALUES ('$(echo "$loser" | sed "s/'/''/g")', 0, 1, 0, datetime('now'), datetime('now'))
ON CONFLICT(name) DO UPDATE SET
    losses = losses + 1,
    last_debate = datetime('now');
SQL

    echo "Recorded: $winner defeated $loser"
    echo "Topic: $topic ($format)"
}

cmd_leaderboard() {
    ensure_db

    local count
    count=$(sqlite3 "$DB" "SELECT COUNT(*) FROM participants;")

    if [[ "$count" -eq 0 ]]; then
        echo "No debates recorded yet."
        return
    fi

    echo "🏆 DEBATE LEADERBOARD"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    printf "%-4s %-20s %4s %4s %4s %7s\n" "Rank" "Participant" "W" "L" "D" "Win%"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    local rank=1
    while IFS='|' read -r name wins losses draws; do
        local total=$((wins + losses + draws))
        local winrate
        if [[ $total -gt 0 ]]; then
            winrate=$(awk "BEGIN {printf \"%.0f\", ($wins / $total) * 100}")
        else
            winrate="0"
        fi
        printf "%-4s %-20s %4s %4s %4s %6s%%\n" "#$rank" "$name" "$wins" "$losses" "$draws" "$winrate"
        rank=$((rank + 1))
    done < <(sqlite3 -separator '|' "$DB" "SELECT name, wins, losses, draws FROM participants ORDER BY wins DESC, losses ASC, name ASC;")

    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    local total_debates
    total_debates=$(sqlite3 "$DB" "SELECT COUNT(*) FROM debates;")
    echo "Total debates: $total_debates"
}

cmd_history() {
    ensure_db

    local limit=10

    while [[ $# -gt 0 ]]; do
        case "$1" in
            --limit)
                limit="${2:-10}"
                shift 2
                ;;
            *)
                shift
                ;;
        esac
    done

    local count
    count=$(sqlite3 "$DB" "SELECT COUNT(*) FROM debates;")

    if [[ "$count" -eq 0 ]]; then
        echo "No debates recorded yet."
        return
    fi

    echo "📋 RECENT DEBATES (last $limit)"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    while IFS='|' read -r id winner loser topic format created_at; do
        echo ""
        echo "  #$id — $topic"
        echo "  Format: $format | $created_at"
        echo "  Winner: $winner  |  Loser: $loser"
    done < <(sqlite3 -separator '|' "$DB" "SELECT id, winner, loser, topic, format, created_at FROM debates ORDER BY created_at DESC LIMIT $limit;")

    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
}

cmd_stats() {
    local name="${1:-}"

    if [[ -z "$name" ]]; then
        echo "Usage: scoreboard.sh stats <participant>" >&2
        exit 1
    fi

    ensure_db

    local escaped_name
    escaped_name="$(echo "$name" | sed "s/'/''/g")"

    local result
    result=$(sqlite3 -separator '|' "$DB" "SELECT name, wins, losses, draws, first_debate, last_debate FROM participants WHERE LOWER(name) = LOWER('$escaped_name');")

    if [[ -z "$result" ]]; then
        echo "No record found for '$name'."
        return
    fi

    IFS='|' read -r p_name wins losses draws first_debate last_debate <<< "$result"
    local total=$((wins + losses + draws))
    local winrate
    if [[ $total -gt 0 ]]; then
        winrate=$(awk "BEGIN {printf \"%.0f\", ($wins / $total) * 100}")
    else
        winrate="0"
    fi

    echo "📊 STATS: $p_name"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  Wins:       $wins"
    echo "  Losses:     $losses"
    echo "  Draws:      $draws"
    echo "  Win Rate:   ${winrate}%"
    echo "  Total:      $total debates"
    echo "  First:      $first_debate"
    echo "  Last:       $last_debate"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    echo ""
    echo "Recent debates:"
    sqlite3 -separator '|' "$DB" "SELECT topic, format, CASE WHEN LOWER(winner) = LOWER('$escaped_name') THEN 'WIN' ELSE 'LOSS' END, created_at FROM debates WHERE LOWER(winner) = LOWER('$escaped_name') OR LOWER(loser) = LOWER('$escaped_name') ORDER BY created_at DESC LIMIT 5;" | while IFS='|' read -r topic format result date; do
        echo "  [$result] $topic ($format) — $date"
    done
}

cmd_reset() {
    ensure_db

    echo "⚠️  This will delete ALL debate records permanently."
    read -rp "Type 'RESET' to confirm: " confirm

    if [[ "$confirm" != "RESET" ]]; then
        echo "Reset cancelled."
        return
    fi

    sqlite3 "$DB" <<'SQL'
DELETE FROM debates;
DELETE FROM participants;
SQL

    echo "Scoreboard has been reset. All records deleted."
}

# Main dispatch
case "${1:-}" in
    init)
        cmd_init
        ;;
    record)
        shift
        cmd_record "$@"
        ;;
    leaderboard)
        cmd_leaderboard
        ;;
    history)
        shift
        cmd_history "$@"
        ;;
    stats)
        shift
        cmd_stats "$@"
        ;;
    reset)
        cmd_reset
        ;;
    -h|--help|help|"")
        usage
        ;;
    *)
        echo "Unknown command: $1" >&2
        usage
        exit 1
        ;;
esac
