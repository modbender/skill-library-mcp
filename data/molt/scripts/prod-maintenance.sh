#!/bin/bash
# Production maintenance utilities for MoltFundMe.
# Run from the repo clone on the VM: /home/moltfund/molt-repo/scripts/prod-maintenance.sh
#
# Usage:
#   ./scripts/prod-maintenance.sh backup              # Back up database
#   ./scripts/prod-maintenance.sh status              # Show container status and health
#   ./scripts/prod-maintenance.sh logs <service>      # Tail logs (api, web, nginx-proxy)
#   ./scripts/prod-maintenance.sh db-shell            # Open SQLite shell on prod.db
#   ./scripts/prod-maintenance.sh db-query "<sql>"    # Run a single SQL query
#   ./scripts/prod-maintenance.sh cleanup-duplicates  # Find and remove duplicate campaigns
#   ./scripts/prod-maintenance.sh verify              # Verify data integrity
set -e

DATA_DIR="/home/moltfund/molt-data"
BACKUP_DIR="/home/moltfund/backups"
PROD_DIR="/home/moltfund/molt-repo/moltfundme-prod"
DB="$DATA_DIR/prod.db"

cmd_backup() {
    mkdir -p "$BACKUP_DIR"
    TIMESTAMP=$(date +%Y%m%d_%H%M%S)
    if [ ! -f "$DB" ]; then
        echo "Error: Database not found at $DB"
        exit 1
    fi
    cp "$DB" "$BACKUP_DIR/prod_${TIMESTAMP}.db"
    echo "Backed up to $BACKUP_DIR/prod_${TIMESTAMP}.db"
    echo "Size: $(du -h "$BACKUP_DIR/prod_${TIMESTAMP}.db" | cut -f1)"
    # Show recent backups
    echo ""
    echo "Recent backups:"
    ls -lht "$BACKUP_DIR"/prod_*.db 2>/dev/null | head -5
}

cmd_status() {
    echo "=== Container Status ==="
    cd "$PROD_DIR"
    docker compose ps
    echo ""
    echo "=== Health Checks ==="
    API_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health 2>/dev/null || echo "000")
    echo "API: $API_STATUS"
    echo ""
    echo "=== Disk Usage ==="
    echo "Data dir: $(du -sh "$DATA_DIR" 2>/dev/null | cut -f1)"
    echo "Database: $(du -h "$DB" 2>/dev/null | cut -f1)"
    echo "Backups:  $(du -sh "$BACKUP_DIR" 2>/dev/null | cut -f1)"
    echo ""
    echo "=== Image Versions ==="
    docker inspect --format='{{.Config.Image}} created={{.Created}}' moltfundme-api 2>/dev/null || echo "API container not found"
    docker inspect --format='{{.Config.Image}} created={{.Created}}' moltfundme-web 2>/dev/null || echo "Web container not found"
}

cmd_logs() {
    SERVICE="${1:-api}"
    cd "$PROD_DIR"
    docker compose logs --tail=100 -f "$SERVICE"
}

cmd_db_shell() {
    if [ ! -f "$DB" ]; then
        echo "Error: Database not found at $DB"
        exit 1
    fi
    echo "Opening SQLite shell on $DB"
    echo "Type .quit to exit, .tables to list tables"
    echo ""
    sqlite3 "$DB"
}

cmd_db_query() {
    QUERY="${1:?Usage: prod-maintenance.sh db-query \"SELECT ...\"}"
    if [ ! -f "$DB" ]; then
        echo "Error: Database not found at $DB"
        exit 1
    fi
    sqlite3 -header -column "$DB" "$QUERY"
}

cmd_cleanup_duplicates() {
    if [ ! -f "$DB" ]; then
        echo "Error: Database not found at $DB"
        exit 1
    fi

    echo "=== Finding Duplicate Campaigns ==="
    echo "(Same creator + title within 5 minutes)"
    echo ""

    # Show duplicates
    sqlite3 -header -column "$DB" "
        SELECT c1.id, c1.title, c1.creator_id, c1.created_at
        FROM campaigns c1
        INNER JOIN campaigns c2 ON c1.creator_id = c2.creator_id
            AND c1.title = c2.title
            AND c1.id != c2.id
            AND abs(strftime('%s', c1.created_at) - strftime('%s', c2.created_at)) < 300
        ORDER BY c1.title, c1.created_at;
    "

    echo ""
    read -p "Remove duplicates? (keep earliest of each group) [y/N] " confirm
    if [ "$confirm" = "y" ] || [ "$confirm" = "Y" ]; then
        # Back up first
        cmd_backup

        # Delete all but the earliest in each duplicate group
        sqlite3 "$DB" "
            DELETE FROM campaigns WHERE id IN (
                SELECT c1.id
                FROM campaigns c1
                INNER JOIN campaigns c2 ON c1.creator_id = c2.creator_id
                    AND c1.title = c2.title
                    AND c1.id != c2.id
                    AND abs(strftime('%s', c1.created_at) - strftime('%s', c2.created_at)) < 300
                WHERE c1.created_at > c2.created_at
            );
        "
        echo "Duplicates removed."
    else
        echo "Aborted."
    fi
}

cmd_verify() {
    if [ ! -f "$DB" ]; then
        echo "Error: Database not found at $DB"
        exit 1
    fi

    echo "=== Data Integrity Check ==="
    echo ""

    # SQLite integrity check
    INTEGRITY=$(sqlite3 "$DB" "PRAGMA integrity_check;")
    if [ "$INTEGRITY" = "ok" ]; then
        echo "SQLite integrity: OK"
    else
        echo "SQLite integrity: FAILED"
        echo "$INTEGRITY"
    fi

    echo ""
    echo "=== Table Counts ==="
    sqlite3 -header -column "$DB" "
        SELECT 'campaigns' as tbl, count(*) as cnt FROM campaigns
        UNION ALL SELECT 'creators', count(*) FROM creators
        UNION ALL SELECT 'agents', count(*) FROM agents
        UNION ALL SELECT 'donations', count(*) FROM donations
        UNION ALL SELECT 'war_room_posts', count(*) FROM war_room_posts;
    "

    echo ""
    echo "=== Upload Directories ==="
    for dir in "$DATA_DIR/uploads/campaigns" "$DATA_DIR/uploads/agents" "$DATA_DIR/uploads/kyc"; do
        if [ -d "$dir" ]; then
            echo "$(basename "$dir"): $(find "$dir" -type f | wc -l) files"
        fi
    done
}

# Route to subcommand
case "${1:-help}" in
    backup)             cmd_backup ;;
    status)             cmd_status ;;
    logs)               cmd_logs "$2" ;;
    db-shell)           cmd_db_shell ;;
    db-query)           cmd_db_query "$2" ;;
    cleanup-duplicates) cmd_cleanup_duplicates ;;
    verify)             cmd_verify ;;
    help|*)
        echo "MoltFundMe Production Maintenance"
        echo ""
        echo "Usage: $0 <command> [args]"
        echo ""
        echo "Commands:"
        echo "  backup              Back up the production database"
        echo "  status              Show container status, health, and disk usage"
        echo "  logs <service>      Tail logs for a service (api, web, nginx-proxy)"
        echo "  db-shell            Open interactive SQLite shell"
        echo "  db-query \"<sql>\"    Run a single SQL query"
        echo "  cleanup-duplicates  Find and remove duplicate campaigns"
        echo "  verify              Run data integrity checks"
        ;;
esac
