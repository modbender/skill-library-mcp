#!/usr/bin/env bash
set -euo pipefail
_REAL_SCRIPT="$(readlink -f "$0")"
_SCRIPT_DIR="$(dirname "$_REAL_SCRIPT")"
DB="${TASK_DB:-$(dirname "$_SCRIPT_DIR")/tasks.db}"
die() { printf '\033[1;31mError:\033[0m %s\n' "$1" >&2; exit 1; }
ok()  { printf '\033[1;32m✓\033[0m %s\n' "$1"; }
warn(){ printf '\033[1;33m⚠\033[0m %s\n' "$1"; }
require_int() {
  local val="$1"
  local name="${2:-argument}"
  [[ "$val" =~ ^[0-9]+$ ]] || die "$name must be a positive integer (got: '$val')"
}
sql() {
  local _tmpf
  _tmpf=$(mktemp)
  printf '%s\n' "$1" > "$_tmpf"
  sqlite3 -batch "$DB" < "$_tmpf"
  local _rc=$?
  rm -f "$_tmpf"
  return $_rc
}
sql_table() {
  local _tmpf
  _tmpf=$(mktemp)
  printf '.mode column\n.headers on\n.width %s\n%s\n' "$1" "$2" > "$_tmpf"
  sqlite3 -batch "$DB" < "$_tmpf"
  local _rc=$?
  rm -f "$_tmpf"
  return $_rc
}
ensure_db() {
  [ -f "$DB" ] || die "Database not found at '$DB'. Run install.sh first."
  local has_project
  has_project=$(sqlite3 -batch "$DB" "SELECT COUNT(*) FROM pragma_table_info('tasks') WHERE name='project';")
  if [ "$has_project" -eq 0 ]; then
    sqlite3 -batch "$DB" "ALTER TABLE tasks ADD COLUMN project TEXT;"
  fi
}
usage() {
cat <<'EOF'
task — local task management
USAGE:
  task create "description" [--priority=N] [--parent=ID] [--project=NAME]
  task start   ID
  task block   ID "reason"
  task complete ID
  task list    [--status=STATUS] [--parent=ID] [--project=NAME]
  task show    ID
  task stuck
  task break   ID "subtask 1" "subtask 2" ...
  task delete  ID [--force]
  task depend  ID DEPENDS_ON_ID
STATUSES: pending, in_progress, blocked, done
ENVIRONMENT:
  TASK_DB   Path to SQLite database (default: ./tasks.db)
EOF
exit 0
}
cmd_create() {
  local desc="" priority="" parent="" project=""
  while [ $# -gt 0 ]; do
    case "$1" in
      --priority=*) priority="${1#*=}" ;;
      --parent=*)   parent="${1#*=}" ;;
      --project=*)  project="${1#*=}" ;;
      -*)           die "Unknown flag: $1" ;;
      *)            desc="$1" ;;
    esac
    shift
  done
  [ -z "$desc" ] && die "Usage: task create \"description\" [--priority=N] [--parent=ID] [--project=NAME]"
  if [ -n "$parent" ]; then
    require_int "$parent" "--parent"
  fi
  if [ -n "$parent" ] && [ -z "$priority" ]; then
    priority=$(sql "SELECT priority FROM tasks WHERE id = $parent;")
  elif [ -z "$priority" ]; then
    priority=5
  fi
  require_int "$priority" "--priority"
  if [ "$priority" -lt 1 ] || [ "$priority" -gt 10 ]; then
    die "Priority must be 1-10"
  fi
  if [ -n "$parent" ]; then
    local pcount
    pcount=$(sql "SELECT count(*) FROM tasks WHERE id = $parent;")
    [ "$pcount" -eq 0 ] && die "Parent task $parent does not exist"
  fi
  local parent_val="NULL"
  [ -n "$parent" ] && parent_val="$parent"
  local project_val="NULL"
  [ -n "$project" ] && project_val="'$(printf '%s' "$project" | sed "s/'/''/g")'"
  local safe_desc
  safe_desc=$(printf '%s' "$desc" | sed "s/'/''/g")
  local task_id
  task_id=$(sql "INSERT INTO tasks (request_text, project, status, priority, parent_id, created_at, last_updated)
    VALUES ('$safe_desc', $project_val, 'pending', $priority, $parent_val, datetime('now'), datetime('now'));
    SELECT last_insert_rowid();")
  ok "Created task #$task_id: $desc (priority=$priority${project:+, project=$project})"
  echo "$task_id"
}
cmd_start() {
  local id="${1:-}"
  [ -z "$id" ] && die "Usage: task start ID"
  require_int "$id" "ID"
  local status
  status=$(sql "SELECT status FROM tasks WHERE id = $id;" 2>/dev/null) || true
  [ -z "$status" ] && die "Task #$id not found"
  [ "$status" = "done" ] && die "Task #$id is already done"
  [ "$status" = "in_progress" ] && die "Task #$id is already in progress"
  local blocking
  blocking=$(sql "SELECT d.depends_on_task_id || ': ' || t.request_text
    FROM dependencies d
    JOIN tasks t ON t.id = d.depends_on_task_id
    WHERE d.task_id = $id AND t.status != 'done';")
  if [ -n "$blocking" ]; then
    warn "Cannot start task #$id — blocked by unfinished dependencies:"
    echo "$blocking" | while IFS= read -r line; do
      printf '  → %s\n' "$line"
    done
    exit 1
  fi
  sql "UPDATE tasks SET status = 'in_progress', started_at = datetime('now'), last_updated = datetime('now') WHERE id = $id;"
  ok "Started task #$id"
}
cmd_block() {
  local id="${1:-}"
  local reason="${2:-}"
  [ -z "$id" ] && die "Usage: task block ID \"reason\""
  require_int "$id" "ID"
  local status
  status=$(sql "SELECT status FROM tasks WHERE id = $id;" 2>/dev/null) || true
  [ -z "$status" ] && die "Task #$id not found"
  [ "$status" = "done" ] && die "Task #$id is already done"
  local safe_reason
  safe_reason=$(printf '%s' "$reason" | sed "s/'/''/g")
  sql "UPDATE tasks SET status = 'blocked',
    notes = CASE WHEN notes IS NULL OR notes = '' THEN 'BLOCKED: $safe_reason'
            ELSE notes || char(10) || 'BLOCKED: $safe_reason' END,
    last_updated = datetime('now')
    WHERE id = $id;"
  ok "Blocked task #$id: $reason"
}
cmd_complete() {
  local id="${1:-}"
  [ -z "$id" ] && die "Usage: task complete ID"
  require_int "$id" "ID"
  local status
  status=$(sql "SELECT status FROM tasks WHERE id = $id;" 2>/dev/null) || true
  [ -z "$status" ] && die "Task #$id not found"
  [ "$status" = "done" ] && die "Task #$id is already done"
  sql "UPDATE tasks SET status = 'done', completed_at = datetime('now'), last_updated = datetime('now'), started_at = COALESCE(started_at, datetime('now')) WHERE id = $id;"
  ok "Completed task #$id"
  local dependents
  dependents=$(sql "SELECT DISTINCT d.task_id FROM dependencies d
    WHERE d.depends_on_task_id = $id;")
  if [ -n "$dependents" ]; then
    while IFS= read -r dep_id; do
      require_int "$dep_id" "dep_id"
      local unfinished
      unfinished=$(sql "SELECT count(*) FROM dependencies d
        JOIN tasks t ON t.id = d.depends_on_task_id
        WHERE d.task_id = $dep_id AND t.status != 'done';")
      if [ "$unfinished" -eq 0 ]; then
        local dep_status
        dep_status=$(sql "SELECT status FROM tasks WHERE id = $dep_id;")
        if [ "$dep_status" = "blocked" ]; then
          sql "UPDATE tasks SET status = 'pending', last_updated = datetime('now') WHERE id = $dep_id;"
          ok "Auto-unblocked task #$dep_id (all dependencies satisfied)"
        fi
      fi
    done <<< "$dependents"
  fi
}
cmd_list() {
  local filter_status="" filter_parent="" filter_project="" filter_since="" filter_search=""
  while [ $# -gt 0 ]; do
    case "$1" in
      --status=*)  filter_status="${1#*=}" ;;
      --parent=*)  filter_parent="${1#*=}" ;;
      --project=*) filter_project="${1#*=}" ;;
      --since=*)   filter_since="${1#*=}" ;;
      --search=*)  filter_search="${1#*=}" ;;
      -*)          die "Unknown flag: $1" ;;
    esac
    shift
  done
  local where="WHERE 1=1"
  if [ -n "$filter_status" ]; then
    case "$filter_status" in
      pending|in_progress|blocked|done) ;;
      *) die "Unknown status: '$filter_status'. Use: pending, in_progress, blocked, done" ;;
    esac
    where="$where AND status = '$filter_status'"
  fi
  if [ -n "$filter_parent" ]; then
    require_int "$filter_parent" "--parent"
    where="$where AND parent_id = $filter_parent"
  fi
  if [ -n "$filter_project" ]; then
    local safe_proj
    safe_proj=$(printf '%s' "$filter_project" | sed "s/'/''/g")
    where="$where AND project = '$safe_proj'"
  fi
  if [ -n "$filter_since" ]; then
    [[ "$filter_since" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}$ ]] || die "--since must be in YYYY-MM-DD format"
    where="$where AND (created_at >= '$filter_since' OR last_updated >= '$filter_since')"
  fi
  if [ -n "$filter_search" ]; then
    local safe_search
    safe_search=$(printf '%s' "$filter_search" | sed "s/'/''/g" | sed 's/%/%%/g')
    where="$where AND request_text LIKE '%$safe_search%'"
  fi
  local results
  results=$(sql_table "4 12 30 12 8 6" "SELECT id, IFNULL(project, '') AS project, request_text AS description, status, priority AS pri, parent_id AS parent FROM tasks $where ORDER BY priority DESC, created_at ASC;")
  if [ -z "$results" ]; then
    echo "No tasks found."
  else
    echo "$results"
  fi
}
cmd_show() {
  local id="${1:-}"
  [ -z "$id" ] && die "Usage: task show ID"
  require_int "$id" "ID"
  local row
  local show_sql="SELECT *,
    CASE
      WHEN started_at IS NULL THEN NULL
      ELSE ROUND((julianday(IFNULL(completed_at, datetime('now'))) - julianday(started_at)) * 24.0, 1) || ' hours'
    END AS duration
    FROM tasks WHERE id = $id;"
  local row
  row=$(sqlite3 -batch "$DB" ".mode line" "$show_sql")
  [ -z "$row" ] && die "Task #$id not found"
  echo "$row"
  local deps
  deps=$(sql "SELECT d.depends_on_task_id || ' (' || t.status || '): ' || t.request_text
    FROM dependencies d
    JOIN tasks t ON t.id = d.depends_on_task_id
    WHERE d.task_id = $id;")
  if [ -n "$deps" ]; then
    echo ""
    echo "Dependencies:"
    echo "$deps" | while IFS= read -r line; do
      printf '  → %s\n' "$line"
    done
  fi
  local subs
  subs=$(sql "SELECT id || ' (' || status || '): ' || request_text FROM tasks WHERE parent_id = $id;")
  if [ -n "$subs" ]; then
    echo ""
    echo "Subtasks:"
    echo "$subs" | while IFS= read -r line; do
      printf '  → %s\n' "$line"
    done
  fi
}
cmd_stuck() {
  local results
  results=$(sql_table "4 40 20" "SELECT id, request_text AS description, last_updated FROM tasks WHERE status = 'in_progress' AND last_updated < datetime('now', '-30 minutes') ORDER BY last_updated ASC;")
  if [ -z "$results" ]; then
    ok "No stalled tasks."
  else
    warn "Stalled tasks (inactive >30 min):"
    echo "$results"
  fi
}
cmd_break() {
  local parent_id="${1:-}"
  [ -z "$parent_id" ] && die "Usage: task break PARENT_ID \"subtask 1\" \"subtask 2\" ..."
  require_int "$parent_id" "PARENT_ID"
  shift
  [ $# -eq 0 ] && die "Provide at least one subtask description"
  local pstatus
  pstatus=$(sql "SELECT status FROM tasks WHERE id = $parent_id;" 2>/dev/null) || true
  [ -z "$pstatus" ] && die "Parent task #$parent_id not found"
  local parent_priority parent_project
  parent_priority=$(sql "SELECT priority FROM tasks WHERE id = $parent_id;")
  parent_project=$(sql "SELECT project FROM tasks WHERE id = $parent_id;")
  require_int "$parent_priority" "parent_priority"
  local project_val="NULL"
  [ -n "$parent_project" ] && project_val="'$(printf '%s' "$parent_project" | sed "s/'/''/g")'"
  local prev_id=""
  local first_id=""
  for desc in "$@"; do
    local safe_desc
    safe_desc=$(printf '%s' "$desc" | sed "s/'/''/g")
    local sub_id
    sub_id=$(sql "INSERT INTO tasks (request_text, project, status, priority, parent_id, created_at, last_updated)
      VALUES ('$safe_desc', $project_val, 'pending', $parent_priority, $parent_id, datetime('now'), datetime('now'));
      SELECT last_insert_rowid();")
    require_int "$sub_id" "sub_id"
    [ -z "$first_id" ] && first_id="$sub_id"
    if [ -n "$prev_id" ]; then
      sql "INSERT INTO dependencies (task_id, depends_on_task_id) VALUES ($sub_id, $prev_id);"
    fi
    ok "Created subtask #$sub_id: $desc"
    prev_id="$sub_id"
  done
  ok "Decomposed task #$parent_id into $(($# )) subtasks (#$first_id → #$prev_id)"
}
cmd_depend() {
  local id="${1:-}"
  local dep="${2:-}"
  [ -z "$id" ] || [ -z "$dep" ] && die "Usage: task depend TASK_ID DEPENDS_ON_ID"
  require_int "$id" "TASK_ID"
  require_int "$dep" "DEPENDS_ON_ID"
  local c1 c2
  c1=$(sql "SELECT count(*) FROM tasks WHERE id = $id;")
  c2=$(sql "SELECT count(*) FROM tasks WHERE id = $dep;")
  [ "$c1" -eq 0 ] && die "Task #$id not found"
  [ "$c2" -eq 0 ] && die "Task #$dep not found"
  [ "$id" = "$dep" ] && die "A task cannot depend on itself"
  local existing
  existing=$(sql "SELECT count(*) FROM dependencies WHERE task_id = $id AND depends_on_task_id = $dep;")
  [ "$existing" -gt 0 ] && die "Dependency already exists"
  sql "INSERT INTO dependencies (task_id, depends_on_task_id) VALUES ($id, $dep);"
  ok "Task #$id now depends on task #$dep"
}
cmd_delete() {
  local id="${1:-}"
  local force=false
  [ -z "$id" ] && die "Usage: task delete ID [--force]"
  require_int "$id" "ID"
  if [ "${2:-}" = "--force" ]; then
    force=true
  fi
  local desc
  desc=$(sql "SELECT request_text FROM tasks WHERE id = $id;") || true
  [ -z "$desc" ] && die "Task #$id not found"
  local sub_count
  sub_count=$(sql "SELECT count(*) FROM tasks WHERE parent_id = $id;")
  if [ "$sub_count" -gt 0 ] && [ "$force" = false ]; then
    die "Task #$id has $sub_count subtask(s). Use --force to delete with subtasks."
  fi
  if [ "$sub_count" -gt 0 ]; then
    sql "DELETE FROM dependencies WHERE task_id IN (SELECT id FROM tasks WHERE parent_id = $id)
         OR depends_on_task_id IN (SELECT id FROM tasks WHERE parent_id = $id);"
    sql "DELETE FROM tasks WHERE parent_id = $id;"
    ok "Deleted $sub_count subtask(s)"
  fi
  sql "DELETE FROM dependencies WHERE task_id = $id OR depends_on_task_id = $id;"
  sql "DELETE FROM tasks WHERE id = $id;"
  ok "Deleted task #$id: $desc"
}
[ $# -eq 0 ] && usage
ensure_db
case "$1" in
  create)   shift; cmd_create "$@" ;;
  start)    shift; cmd_start "$@" ;;
  block)    shift; cmd_block "$@" ;;
  complete) shift; cmd_complete "$@" ;;
  delete)   shift; cmd_delete "$@" ;;
  list)     shift; cmd_list "$@" ;;
  show)     shift; cmd_show "$@" ;;
  stuck)    shift; cmd_stuck "$@" ;;
  break)    shift; cmd_break "$@" ;;
  depend)   shift; cmd_depend "$@" ;;
  help|--help|-h) usage ;;
  *)        die "Unknown command: $1. Run 'task help' for usage." ;;
esac
