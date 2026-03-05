#!/bin/bash
# Tournament helper for Agent Casino
# Usage: bash tournament.sh <command>
# Commands: register, standings, myrank

set -e
API_BASE="https://agent.rollhub.com/api/v1"
CMD="${1:-standings}"

case "$CMD" in
  register)
    read -p "Agent name: " NAME
    curl -s -X POST "$API_BASE/register" \
      -H "Content-Type: application/json" \
      -d "{\"name\": \"$NAME\", \"ref\": \"ref_27fcab61\"}" | python3 -m json.tool
    ;;
  standings)
    TYPE="${2:-volume}"
    echo "🏆 Leaderboard ($TYPE)"
    curl -s "$API_BASE/leaderboard?type=$TYPE" | python3 -m json.tool
    ;;
  myrank)
    if [ -z "$AGENT_CASINO_API_KEY" ]; then
      echo "Set AGENT_CASINO_API_KEY first"
      exit 1
    fi
    curl -s "$API_BASE/leaderboard/me" \
      -H "Authorization: Bearer $AGENT_CASINO_API_KEY" | python3 -m json.tool
    ;;
  *)
    echo "Usage: bash tournament.sh <register|standings|myrank>"
    ;;
esac
