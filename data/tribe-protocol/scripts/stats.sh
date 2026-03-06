#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/lib/db.sh"
check_db

TOTAL=$(db_query "SELECT COUNT(*) FROM entities WHERE status='active';")
HUMANS=$(db_query "SELECT COUNT(*) FROM entities WHERE type='human' AND status='active';")
BOTS=$(db_query "SELECT COUNT(*) FROM entities WHERE type='bot' AND status='active';")
SERVERS=$(db_query "SELECT COUNT(DISTINCT server_slug) FROM server_roles;")

# Tier distribution
T4=$(db_query "SELECT COUNT(*) FROM entities WHERE trust_tier=4 AND status='active';")
T3=$(db_query "SELECT COUNT(*) FROM entities WHERE trust_tier=3 AND status='active';")
T2=$(db_query "SELECT COUNT(*) FROM entities WHERE trust_tier=2 AND status='active';")
T1=$(db_query "SELECT COUNT(*) FROM entities WHERE trust_tier=1 AND status='active';")
T0=$(db_query "SELECT COUNT(*) FROM entities WHERE trust_tier=0 AND status='active';")

TAGS=$(db_query "SELECT COUNT(DISTINCT tag) FROM entity_tags;")
AUDIT=$(db_query "SELECT COUNT(*) FROM audit_log;")

echo "📊 Tribe Stats"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "   $TOTAL entities ($HUMANS human, $BOTS bot), $SERVERS servers"
echo "   Tier distribution: T4:$T4 T3:$T3 T2:$T2 T1:$T1 T0:$T0"
echo "   Tags: $TAGS unique | Audit entries: $AUDIT"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
