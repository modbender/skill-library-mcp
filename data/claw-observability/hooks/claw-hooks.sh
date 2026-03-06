#!/bin/bash
# CLAW Observability — Claude Code Hook Handler
# Automatically reports agent activity to the CLAW dashboard.
# Fires on: UserPromptSubmit, PreToolUse, PostToolUse, PostToolUseFailure, Stop
#
# Requires: CLAW_API_KEY, CLAW_BASE_URL, curl, python3
# Performance: < 50ms per invocation (non-blocking curl)

# ─── Early exit if not configured ───
[ -z "${CLAW_API_KEY:-}" ] && exit 0
[ -z "${CLAW_BASE_URL:-}" ] && exit 0

# ─── Read stdin once ───
INPUT=$(cat 2>/dev/null || echo '{}')

# ─── Fast JSON field extractor (python3) ───
pj() {
  python3 -c "
import sys,json
try:
 d=json.load(sys.stdin)
 for k in sys.argv[1:]:
  d=d.get(k,'') if isinstance(d,dict) else ''
 print(d if d else '')
except: print('')
" "$@" <<< "$INPUT" 2>/dev/null
}

EVENT=$(pj hook_event_name)
[ -z "$EVENT" ] && exit 0

SESSION_ID=$(pj session_id)
RUN_ID="session-${SESSION_ID:0:32}"

# ─── Agent registry: id → "name|type|parent" ───
agent_meta() {
  case "$1" in
    sheev-palpatine)  echo "Sheev Palpatine|orchestrator|" ;;
    anakin)           echo "Anakin|orchestrator|sheev-palpatine" ;;
    yoda)             echo "Yoda|product-owner|anakin" ;;
    qui-gon-jinn)     echo "Qui-Gon Jinn|architect|anakin" ;;
    obi-wan)          echo "Obi-Wan Kenobi|database|anakin" ;;
    chewbacca)        echo "Chewbacca|backend|anakin" ;;
    leia)             echo "Leia Organa|frontend|anakin" ;;
    darth-maul)       echo "Darth Maul|security|anakin" ;;
    r2-d2)            echo "R2-D2|devops|anakin" ;;
    forge)            echo "Forge|devops|anakin" ;;
    c3po)             echo "C-3PO|quality|anakin" ;;
    rey)              echo "Rey|delivery|anakin" ;;
    luke)             echo "Luke Skywalker|execution|anakin" ;;
    padme)            echo "Padme Amidala|compliance|sheev-palpatine" ;;
    han-solo)         echo "Han Solo|worker|anakin" ;;
    lando)            echo "Lando Calrissian|worker|anakin" ;;
    bail-organa)      echo "Bail Organa|worker|sheev-palpatine" ;;
    marcus-aurelius)  echo "Marcus Aurelius|orchestrator|sheev-palpatine" ;;
    antoninus-pius)   echo "Antoninus Pius|worker|marcus-aurelius" ;;
    hadrian)          echo "Hadrian|worker|marcus-aurelius" ;;
    cicero)           echo "Cicero|worker|marcus-aurelius" ;;
    *)                echo "$1|worker|anakin" ;;
  esac
}

# ─── subagent_type → CLAW agent_id ───
map_subagent() {
  case "$1" in
    anakin)                   echo "anakin" ;;
    yoda)                     echo "yoda" ;;
    han-architect)            echo "qui-gon-jinn" ;;
    chewie-backend)           echo "chewbacca" ;;
    leia-frontend)            echo "leia" ;;
    obi-wan)                  echo "obi-wan" ;;
    darth-maul)               echo "darth-maul" ;;
    r2-devops-platform)       echo "r2-d2" ;;
    forge)                    echo "forge" ;;
    c3po-quality-guardian)    echo "c3po" ;;
    rey-delivery-governance)  echo "rey" ;;
    luke-project-execution)   echo "luke" ;;
    padme-lgpd-compliance)    echo "padme" ;;
    Explore|general-purpose)  echo "anakin" ;;
    Plan)                     echo "yoda" ;;
    Bash)                     echo "sheev-palpatine" ;;
    *)                        echo "anakin" ;;
  esac
}

# ─── Fire-and-forget event reporter ───
report() {
  local agent_id="$1" status="$2" message="$3" task_id="${4:-}"
  IFS='|' read -r name type parent <<< "$(agent_meta "$agent_id")"

  # Build JSON with python3 (proper escaping for any message content)
  local json
  json=$(python3 -c "
import json,sys
d={'agent_id':sys.argv[1],'agent_name':sys.argv[2],'agent_type':sys.argv[3],'status':sys.argv[4],'message':sys.argv[5][:450],'run_id':sys.argv[6]}
if sys.argv[7]: d['parent_agent_id']=sys.argv[7]
if sys.argv[8]: d['task_id']=sys.argv[8]
print(json.dumps(d))
" "$agent_id" "$name" "$type" "$status" "$message" "$RUN_ID" "$parent" "$task_id" 2>/dev/null)

  [ -z "$json" ] && return 0

  # Non-blocking: curl runs in background subshell, detached from hook process
  (curl -s -m 5 -X POST "${CLAW_BASE_URL}/api/v1/events" \
    -H "Content-Type: application/json" \
    -H "x-api-key: ${CLAW_API_KEY}" \
    -d "$json" > /dev/null 2>&1 &)
}

# ─── Task ID from description ───
make_task_id() {
  echo "$1" | tr '[:upper:]' '[:lower:]' | tr ' ' '-' | sed 's/[^a-z0-9-]//g' | cut -c1-50
}

# ─── Route hook events ───
case "$EVENT" in
  UserPromptSubmit)
    report "sheev-palpatine" "running" "Processing user request"
    ;;
  PreToolUse)
    TOOL_NAME=$(pj tool_name)
    if [ "$TOOL_NAME" = "Task" ]; then
      SUBAGENT_TYPE=$(pj tool_input subagent_type)
      DESCRIPTION=$(pj tool_input description)
      AGENT_ID=$(map_subagent "$SUBAGENT_TYPE")
      TASK_ID=$(make_task_id "$DESCRIPTION")
      report "$AGENT_ID" "running" "${DESCRIPTION:-Working on task}" "$TASK_ID"
    fi
    ;;
  PostToolUse)
    TOOL_NAME=$(pj tool_name)
    if [ "$TOOL_NAME" = "Task" ]; then
      SUBAGENT_TYPE=$(pj tool_input subagent_type)
      DESCRIPTION=$(pj tool_input description)
      AGENT_ID=$(map_subagent "$SUBAGENT_TYPE")
      TASK_ID=$(make_task_id "$DESCRIPTION")
      report "$AGENT_ID" "success" "Completed: ${DESCRIPTION:-task}" "$TASK_ID"
    fi
    ;;
  PostToolUseFailure)
    TOOL_NAME=$(pj tool_name)
    if [ "$TOOL_NAME" = "Task" ]; then
      SUBAGENT_TYPE=$(pj tool_input subagent_type)
      DESCRIPTION=$(pj tool_input description)
      AGENT_ID=$(map_subagent "$SUBAGENT_TYPE")
      TASK_ID=$(make_task_id "$DESCRIPTION")
      report "$AGENT_ID" "error" "Failed: ${DESCRIPTION:-task}" "$TASK_ID"
    fi
    ;;
  Stop)
    report "sheev-palpatine" "success" "Finished responding to user"
    ;;
esac

exit 0
