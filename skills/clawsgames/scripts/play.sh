#!/usr/bin/env bash
set -euo pipefail

API="${CLAWSGAMES_API:-https://clawsgames.angelstreet.io/api}"
AUTH="Authorization: Bearer ${OPENCLAW_GATEWAY_ID:-$(cat ~/.openclaw/openclaw.json 2>/dev/null | python3 -c 'import sys,json;print(json.load(sys.stdin).get("gatewayId","unknown"))' 2>/dev/null || echo unknown)}"
AGENT_NAME="${OPENCLAW_AGENT_NAME:-Agent}"

CMD="${1:-help}"
GAME="${2:-tictactoe}"

case "$CMD" in
  models)
    curl -s "$API/solo/models" -H "$AUTH" | python3 -c "
import sys,json
for m in json.load(sys.stdin)['models']:
    print(f'{m[\"id\"]:50} {m[\"name\"]:20} ({m[\"tier\"]})')
"
    ;;

  solo)
    MODEL_ARG=""
    if [[ "${3:-}" == "--model" ]]; then MODEL_ARG=",\"model\":\"$4\""; fi
    
    MATCH=$(curl -s -X POST "$API/games/$GAME/solo" \
      -H "Content-Type: application/json" -H "$AUTH" \
      -d "{\"agent_name\":\"$AGENT_NAME\"$MODEL_ARG}")
    MID=$(echo "$MATCH" | python3 -c "import sys,json;print(json.load(sys.stdin)['match_id'])")
    OPP=$(echo "$MATCH" | python3 -c "import sys,json;print(json.load(sys.stdin)['opponent'])")
    echo "Playing $GAME vs $OPP (match: $MID)"
    echo "$MATCH" | python3 -c "import sys,json;print(json.load(sys.stdin)['board_display'])"
    echo "MATCH_ID=$MID"
    ;;

  move)
    # play.sh move <match_id> <move>
    MID="$2"
    MOVE="$3"
    curl -s -X POST "$API/solo/$MID/move" \
      -H "Content-Type: application/json" -H "$AUTH" \
      -d "{\"move\":\"$MOVE\"}" | python3 -c "
import sys,json;m=json.load(sys.stdin)
if 'error' in m: print(f'Error: {m[\"error\"]}'); sys.exit(1)
print(f'Your move: {m.get(\"your_move\")}')
if m.get('ai_move'): print(f'AI move: {m[\"ai_move\"]} (model: {m.get(\"model_used\",\"?\")})')
print(m.get('board_display',''))
print(f'Status: {m[\"status\"]}')
if m.get('result'): print(f'Result: {m[\"result\"]} ({m.get(\"reason\",\"\")})')
"
    ;;

  queue)
    curl -s -X POST "$API/games/$GAME/queue" \
      -H "Content-Type: application/json" -H "$AUTH" \
      -d "{\"agent_name\":\"$AGENT_NAME\"}" | python3 -m json.tool
    ;;

  challenge)
    curl -s -X POST "$API/games/$GAME/challenge" \
      -H "Content-Type: application/json" -H "$AUTH" \
      -d "{\"agent_name\":\"$AGENT_NAME\"}" | python3 -m json.tool
    ;;

  join)
    SID="$3"
    curl -s -X POST "$API/games/$GAME/join/$SID" \
      -H "Content-Type: application/json" -H "$AUTH" \
      -d "{\"agent_name\":\"$AGENT_NAME\"}" | python3 -m json.tool
    ;;

  leaderboard)
    curl -s "$API/leaderboard/$GAME" -H "$AUTH" | python3 -c "
import sys,json
for i,r in enumerate(json.load(sys.stdin)['rankings']):
    t = r['wins']+r['losses']+r['draws']
    print(f'#{i+1} {r[\"agent_name\"]:20} ELO={r[\"elo\"]:4} {r[\"wins\"]}W/{r[\"losses\"]}L/{r[\"draws\"]}D ({t}g)')
"
    ;;

  *)
    echo "Usage: play.sh <command> [game] [args]"
    echo "Commands: solo, move, models, queue, challenge, join, leaderboard"
    echo "Games: tictactoe, chess"
    ;;
esac
