#!/usr/bin/env bash
set -euo pipefail

BASE_DIR="$(cd "$(dirname "$0")/.." && pwd)"
DB="$BASE_DIR/data/tasks.json"

init_db(){
  if [[ ! -f "$DB" ]]; then
    cat > "$DB" <<JSON
{"tasks":[],"nextId":1}
JSON
  fi
}

priority_weight(){
  case "$1" in
    P0) echo 0 ;;
    P1) echo 1 ;;
    P2) echo 2 ;;
    P3) echo 3 ;;
    *) echo 9 ;;
  esac
}

cmd_add(){
  local title="" priority="P2" due="" tags=""
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --title) title="$2"; shift 2 ;;
      --priority) priority="$2"; shift 2 ;;
      --due) due="$2"; shift 2 ;;
      --tags) tags="$2"; shift 2 ;;
      *) shift ;;
    esac
  done
  [[ -z "$title" ]] && { echo "missing --title"; exit 1; }
  local now id w
  now="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  id=$(jq -r '.nextId' "$DB")
  w=$(priority_weight "$priority")
  jq --arg title "$title" --arg priority "$priority" --arg due "$due" --arg tags "$tags" --arg now "$now" --argjson id "$id" --argjson w "$w" '
    .tasks += [{id:$id,title:$title,status:"open",priority:$priority,priorityWeight:$w,due:$due,tags:($tags|split(",")|map(select(length>0))),createdAt:$now,updatedAt:$now}] |
    .nextId += 1
  ' "$DB" > "$DB.tmp" && mv "$DB.tmp" "$DB"
  echo "added #$id"
}

cmd_update(){
  local id="" status="" priority="" due="" title=""
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --id) id="$2"; shift 2 ;;
      --status) status="$2"; shift 2 ;;
      --priority) priority="$2"; shift 2 ;;
      --due) due="$2"; shift 2 ;;
      --title) title="$2"; shift 2 ;;
      *) shift ;;
    esac
  done
  [[ -z "$id" ]] && { echo "missing --id"; exit 1; }
  local now w
  now="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  w=$(priority_weight "${priority:-P9}")
  jq --argjson id "$id" --arg status "$status" --arg priority "$priority" --arg due "$due" --arg title "$title" --arg now "$now" --argjson w "$w" '
    .tasks |= map(if .id==$id then
      .status = (if $status=="" then .status else $status end) |
      .priority = (if $priority=="" then .priority else $priority end) |
      .priorityWeight = (if $priority=="" then .priorityWeight else $w end) |
      .due = (if $due=="" then .due else $due end) |
      .title = (if $title=="" then .title else $title end) |
      .updatedAt = $now
    else . end)
  ' "$DB" > "$DB.tmp" && mv "$DB.tmp" "$DB"
  echo "updated #$id"
}

cmd_done(){
  cmd_update --id "$1" --status done
}

cmd_list(){
  local status="" sort="priority,due,createdAt"
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --status) status="$2"; shift 2 ;;
      --sort) sort="$2"; shift 2 ;;
      *) shift ;;
    esac
  done
  jq -r --arg status "$status" '
    .tasks
    | (if $status=="" then . else map(select(.status==$status)) end)
    | sort_by(.priorityWeight, (if .due=="" then "9999-12-31" else .due end), .createdAt)
    | .[]
    | "[\(.status)][\(.priority)] #\(.id) \(.title)" + (if .due=="" then "" else " (due: \(.due))" end) + (if (.tags|length)>0 then " tags:" + (.tags|join(",")) else "" end)
  ' "$DB"
}

main(){
  init_db
  local cmd="${1:-}"
  shift || true
  case "$cmd" in
    add) cmd_add "$@" ;;
    update) cmd_update "$@" ;;
    done) cmd_done "$@" ;;
    list) cmd_list "$@" ;;
    *) echo "usage: task.sh {add|update|done|list}"; exit 1 ;;
  esac
}

main "$@"
