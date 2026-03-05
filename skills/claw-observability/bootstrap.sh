#!/bin/bash
# CLAW Observability — Agent Bootstrap
# Registers all 21 agents in the CLAW organogram with hierarchy.
# Run once to populate the full agent tree in the dashboard.
#
# Usage: bash bootstrap.sh

set -euo pipefail

# Check env vars
if [ -z "${CLAW_API_KEY:-}" ]; then
  echo "[ERROR] CLAW_API_KEY is not set."
  exit 1
fi
if [ -z "${CLAW_BASE_URL:-}" ]; then
  echo "[ERROR] CLAW_BASE_URL is not set."
  exit 1
fi

API="${CLAW_BASE_URL}/api/v1/events"
KEY="${CLAW_API_KEY}"
RUN="bootstrap-$(date +%Y%m%d-%H%M%S)"

send() {
  local agent_id="$1" agent_name="$2" agent_type="$3" parent="$4" message="$5"

  local json
  json=$(python3 -c "
import json, sys
d = {
    'agent_id': sys.argv[1],
    'agent_name': sys.argv[2],
    'agent_type': sys.argv[3],
    'status': 'idle',
    'message': sys.argv[5],
    'run_id': sys.argv[6],
}
if sys.argv[4]:
    d['parent_agent_id'] = sys.argv[4]
print(json.dumps(d))
" "$agent_id" "$agent_name" "$agent_type" "$parent" "$message" "$RUN" 2>/dev/null)

  local code
  code=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$API" \
    -H "Content-Type: application/json" \
    -H "x-api-key: $KEY" \
    -d "$json" 2>/dev/null || echo "000")

  if [ "$code" = "201" ]; then
    printf "  [OK] %-20s (%s)\n" "$agent_name" "$agent_type"
  else
    printf "  [%s] %-20s FAILED\n" "$code" "$agent_name"
  fi
}

echo ""
echo "  CLAW Agent Bootstrap"
echo "  ===================="
echo ""
echo "  Registering 21 agents with hierarchy..."
echo ""

# Root orchestrator
send "sheev-palpatine" "Sheev Palpatine" "orchestrator" "" "Root orchestrator initialized"

# Anakin subtree
send "anakin" "Anakin" "orchestrator" "sheev-palpatine" "Sub-orchestrator initialized"
send "yoda" "Yoda" "product-owner" "anakin" "Product owner ready"
send "qui-gon-jinn" "Qui-Gon Jinn" "architect" "anakin" "Architect ready"
send "obi-wan" "Obi-Wan Kenobi" "database" "anakin" "Database specialist ready"
send "chewbacca" "Chewbacca" "backend" "anakin" "Backend engineer ready"
send "leia" "Leia Organa" "frontend" "anakin" "Frontend engineer ready"
send "darth-maul" "Darth Maul" "security" "anakin" "Security analyst ready"
send "r2-d2" "R2-D2" "devops" "anakin" "DevOps engineer ready"
send "forge" "Forge" "devops" "anakin" "Container specialist ready"
send "c3po" "C-3PO" "quality" "anakin" "Quality guardian ready"
send "rey" "Rey" "delivery" "anakin" "Delivery manager ready"
send "luke" "Luke Skywalker" "execution" "anakin" "Project executor ready"
send "han-solo" "Han Solo" "worker" "anakin" "Growth worker ready"
send "lando" "Lando Calrissian" "worker" "anakin" "CFO worker ready"

# Direct reports to Sheev
send "bail-organa" "Bail Organa" "worker" "sheev-palpatine" "Partnerships ready"
send "padme" "Padme Amidala" "compliance" "sheev-palpatine" "LGPD compliance ready"

# Marcus Aurelius subtree
send "marcus-aurelius" "Marcus Aurelius" "orchestrator" "sheev-palpatine" "Synov orchestrator initialized"
send "antoninus-pius" "Antoninus Pius" "worker" "marcus-aurelius" "HR worker ready"
send "hadrian" "Hadrian" "worker" "marcus-aurelius" "Legal worker ready"
send "cicero" "Cicero" "worker" "marcus-aurelius" "Training worker ready"

echo ""
echo "  Bootstrap complete! Check your CLAW dashboard."
echo "  All agents should appear in the organogram."
echo ""
