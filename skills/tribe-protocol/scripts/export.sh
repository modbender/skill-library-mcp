#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/lib/db.sh"
check_db

DB_PATH="$(get_db_path)"

echo "# Tribe Protocol — Database Export"
echo ""
echo "Generated: $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
echo "DB: $DB_PATH"
echo ""

# Entities
echo "## Entities"
echo ""
ENTITIES=$(db_query "SELECT id, name, type, trust_tier, status, COALESCE(relationship, '-'), COALESCE(bio, '-') FROM entities ORDER BY trust_tier DESC, name;")
if [ -n "$ENTITIES" ]; then
    echo "| ID | Name | Type | Tier | Status | Relationship | Bio |"
    echo "|----|------|------|------|--------|--------------|-----|"
    while IFS='|' read -r ID NAME_V TYPE_V TIER_V STATUS_V REL_V BIO_V; do
        echo "| $ID | $NAME_V | $TYPE_V | $TIER_V ($(tier_label "$TIER_V")) | $STATUS_V | $REL_V | $BIO_V |"
    done <<< "$ENTITIES"
fi
echo ""

# Platform IDs
echo "## Platform IDs"
echo ""
PIDS=$(db_query "SELECT e.name, p.platform, p.platform_id, p.verified, p.primary_contact FROM platform_ids p JOIN entities e ON p.entity_id = e.id ORDER BY e.name;")
if [ -n "$PIDS" ]; then
    echo "| Entity | Platform | ID | Verified | Primary |"
    echo "|--------|----------|----|----------|---------|"
    while IFS='|' read -r NAME_V PLAT PLAT_ID VERIF PRIMARY; do
        echo "| $NAME_V | $PLAT | $PLAT_ID | $VERIF | $PRIMARY |"
    done <<< "$PIDS"
fi
echo ""

# Server Roles
echo "## Server Roles"
echo ""
ROLES=$(db_query "SELECT e.name, sr.server_slug, sr.role FROM server_roles sr JOIN entities e ON sr.entity_id = e.id ORDER BY sr.server_slug, e.name;")
if [ -n "$ROLES" ]; then
    echo "| Entity | Server | Role |"
    echo "|--------|--------|------|"
    while IFS='|' read -r NAME_V SERVER ROLE; do
        echo "| $NAME_V | $SERVER | $ROLE |"
    done <<< "$ROLES"
fi
echo ""

# Tags
echo "## Tags"
echo ""
TAGS=$(db_query "SELECT e.name, et.tag FROM entity_tags et JOIN entities e ON et.entity_id = e.id ORDER BY et.tag, e.name;")
if [ -n "$TAGS" ]; then
    echo "| Entity | Tag |"
    echo "|--------|-----|"
    while IFS='|' read -r NAME_V TAG; do
        echo "| $NAME_V | $TAG |"
    done <<< "$TAGS"
fi
echo ""

# Bot Metadata
echo "## Bot Metadata"
echo ""
BOTS=$(db_query "SELECT e.name, COALESCE(bm.framework,'-'), COALESCE(bm.model,'-'), COALESCE(bm.host_machine,'-') FROM bot_metadata bm JOIN entities e ON bm.entity_id = e.id ORDER BY e.name;")
if [ -n "$BOTS" ]; then
    echo "| Bot | Framework | Model | Machine |"
    echo "|-----|-----------|-------|---------|"
    while IFS='|' read -r NAME_V FW MODEL MACHINE; do
        echo "| $NAME_V | $FW | $MODEL | $MACHINE |"
    done <<< "$BOTS"
fi
echo ""

# Data Access Rules
echo "## Data Access Rules"
echo ""
RULES=$(db_query "SELECT min_tier, resource_pattern, allowed, COALESCE(description, '-') FROM data_access ORDER BY min_tier DESC, resource_pattern;")
if [ -n "$RULES" ]; then
    echo "| Min Tier | Pattern | Allowed | Description |"
    echo "|----------|---------|---------|-------------|"
    while IFS='|' read -r TIER_V PATTERN ALLOWED DESC; do
        echo "| $TIER_V | $PATTERN | $ALLOWED | $DESC |"
    done <<< "$RULES"
fi
echo ""

# Channel Access
echo "## Channel Access"
echo ""
ACCESS=$(db_query "SELECT e.name, ca.server_slug, COALESCE(ca.channel_name, ca.channel_id, 'all'), ca.can_read, ca.can_write FROM channel_access ca JOIN entities e ON ca.entity_id = e.id ORDER BY ca.server_slug, e.name;" 2>/dev/null || true)
if [ -n "$ACCESS" ]; then
    echo "| Entity | Server | Channel | Read | Write |"
    echo "|--------|--------|---------|------|-------|"
    while IFS='|' read -r NAME_V SERVER CHAN READ WRITE; do
        echo "| $NAME_V | $SERVER | $CHAN | $READ | $WRITE |"
    done <<< "$ACCESS"
fi
echo ""

echo "---"
echo "*Exported by tribe-protocol v1.0.0*"
