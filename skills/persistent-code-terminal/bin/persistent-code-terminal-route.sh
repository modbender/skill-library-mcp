#!/usr/bin/env bash
set -euo pipefail
BASE_DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=bin/persistent-code-terminal-lib.sh
source "$BASE_DIR/persistent-code-terminal-lib.sh"

DEBUG=0
INPUT_TEXT="${1:-}"
PARSE_ONLY=0
JSON_MODE=0

usage() {
  cat <<'EOF_USAGE'
Usage:
  persistent-code-terminal-route.sh [--debug] [--parse-only] [--json] "<user-message>"
EOF_USAGE
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --debug)
      DEBUG=1
      shift
      ;;
    --parse-only)
      PARSE_ONLY=1
      shift
      ;;
    --json)
      JSON_MODE=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      INPUT_TEXT="$1"
      shift
      ;;
  esac
done

if [ -z "${INPUT_TEXT:-}" ]; then
  echo "No input message provided." >&2
  usage >&2
  exit 1
fi

log_decision() {
  local detected="$1"
  local reason="$2"
  local is_git="$3"
  local detected_multi="${4:-false}"
  local tasks_count="${5:-0}"
  local parsed_projects="${6:-}"
  local line

  line="{\"ts\":\"$(pct_now_utc)\",\"detectedIntent\":${detected},\"triggerReason\":\"$(pct_json_escape "$reason")\",\"workingDirIsGitRepo\":${is_git},\"detectedMultiProject\":${detected_multi},\"tasksCount\":${tasks_count},\"parsedProjects\":\"$(pct_json_escape "$parsed_projects")\"}"
  printf '%s\n' "$line" >>"$(pwd)/.pct-routing.log"
  if [ "$DEBUG" -eq 1 ]; then
    printf '%s\n' "$line"
  fi
}

strip_prefix_instruction() {
  printf '%s' "$1" | sed -E 's/^[[:space:]]*(codex[[:space:]]+|用[[:space:]]*codex[[:space:]]+|使用[[:space:]]*codex[[:space:]]+)//'
}

contains_any() {
  local text="$1"
  shift
  local pattern
  for pattern in "$@"; do
    if printf '%s' "$text" | grep -Eiq "$pattern"; then
      return 0
    fi
  done
  return 1
}

trim_spaces() {
  printf '%s' "$1" | sed -E 's/^[[:space:]]+//; s/[[:space:]]+$//'
}

read_auto_code_routing_flag() {
  local config_file value

  if [ -n "${OPENCLAW_CONFIG_DEV_AUTO_CODE_ROUTING:-}" ]; then
    value="${OPENCLAW_CONFIG_DEV_AUTO_CODE_ROUTING}"
    case "$value" in
      true|TRUE|1|yes|YES) echo "true"; return 0 ;;
      *) echo "false"; return 0 ;;
    esac
  fi

  config_file="$(pwd)/openclaw.config.dev.json"
  if [ -f "$config_file" ]; then
    value="$(sed -n 's/.*"autoCodeRouting"[[:space:]]*:[[:space:]]*\(true\|false\).*/\1/p' "$config_file" | head -n 1)"
    if [ "$value" = "true" ]; then
      echo "true"
      return 0
    fi
  fi

  echo "false"
}

project_dir_from_name() {
  local project="$1"
  local cur base parent session path

  cur="$(pwd -P)"
  base="$(basename "$cur")"
  if [ "$project" = "$base" ]; then
    printf '%s\n' "$cur"
    return 0
  fi

  if [ -d "$cur/$project" ]; then
    cd "$cur/$project" && pwd -P
    return 0
  fi

  parent="$(cd "$cur/.." && pwd -P)"
  if [ -d "$parent/$project" ]; then
    cd "$parent/$project" && pwd -P
    return 0
  fi

  session="$(session_name_from_project "$project")"
  if command -v tmux >/dev/null 2>&1 && tmux has-session -t "$session" 2>/dev/null; then
    path="$(tmux display-message -p -t "$session" '#{pane_current_path}' 2>/dev/null || true)"
    if [ -n "$path" ] && [ -d "$path" ]; then
      cd "$path" && pwd -P
      return 0
    fi
  fi

  return 1
}

is_known_project() {
  local project="$1"
  if project_dir_from_name "$project" >/dev/null 2>&1; then
    return 0
  fi
  return 1
}

split_segments() {
  printf '%s' "$1" | sed 's/；/;/g' | tr '\n' ';' | tr ';' '\n'
}

parse_segment() {
  local seg="$1"
  local project=""
  local instruction=""

  seg="$(trim_spaces "$seg")"
  if [ -z "$seg" ]; then
    return 1
  fi

  if printf '%s' "$seg" | grep -Eq '^[给为对][[:space:]]*[[:alnum:]_.-]+[[:space:]]*项目'; then
    project="$(printf '%s' "$seg" | sed -E 's/^[给为对][[:space:]]*([[:alnum:]_.-]+)[[:space:]]*项目[:：]?[[:space:]]*(.*)$/\1/' | head -n 1)"
    instruction="$(printf '%s' "$seg" | sed -E 's/^[给为对][[:space:]]*([[:alnum:]_.-]+)[[:space:]]*项目[:：]?[[:space:]]*(.*)$/\2/' | head -n 1)"
  elif printf '%s' "$seg" | grep -Eq '^[给为对][[:space:]]*[[:alnum:]_.-]+[[:space:]]+'; then
    project="$(printf '%s' "$seg" | sed -E 's/^[给为对][[:space:]]*([[:alnum:]_.-]+)[[:space:]]+(.*)$/\1/' | head -n 1)"
    instruction="$(printf '%s' "$seg" | sed -E 's/^[给为对][[:space:]]*([[:alnum:]_.-]+)[[:space:]]+(.*)$/\2/' | head -n 1)"
  elif printf '%s' "$seg" | grep -Eq '^[[:alnum:]_.-]+[[:space:]]*项目'; then
    project="$(printf '%s' "$seg" | sed -E 's/^([[:alnum:]_.-]+)[[:space:]]*项目[:：]?[[:space:]]*(.*)$/\1/' | head -n 1)"
    instruction="$(printf '%s' "$seg" | sed -E 's/^([[:alnum:]_.-]+)[[:space:]]*项目[:：]?[[:space:]]*(.*)$/\2/' | head -n 1)"
  fi

  if [ -n "$project" ]; then
    instruction="$(trim_spaces "$instruction")"
    printf '%s|%s\n' "$project" "$instruction"
    return 0
  fi
  return 1
}

json_get_scalar() {
  local json="$1"
  local key="$2"
  printf '%s\n' "$json" | awk -v k="\"$key\"" '
    {
      if (match($0, k "[[:space:]]*:[[:space:]]*")) {
        rest = substr($0, RSTART + RLENGTH)
        if (substr(rest, 1, 1) == "\"") {
          sub(/^"/, "", rest)
          sub(/".*$/, "", rest)
          print rest
          exit
        }
        gsub(/[[:space:]]/, "", rest)
        sub(/[,}].*$/, "", rest)
        print rest
        exit
      }
    }
  '
}

json_get_first_error_line() {
  local json="$1"
  printf '%s\n' "$json" | awk '
    {
      if (match($0, /"errorLines"[[:space:]]*:[[:space:]]*\[/)) {
        rest = substr($0, RSTART + RLENGTH)
        if (match(rest, /^"[^"]*"/)) {
          first = substr(rest, RSTART + 1, RLENGTH - 2)
          print first
        }
        exit
      }
    }
  '
}

ACTION_PATTERNS=(
  '增加|新增|实现|添加'
  '修改|重构|优化'
  '修复|fix|解决'
  '删除|移除'
  '提交|commit|push'
  '跑测试|运行测试|build|npm|pnpm|yarn'
  '检查项目|分析代码'
  '修复测试失败'
  '用[[:space:]]*codex|用[[:space:]]*claude|帮我改代码|在当前项目中'
  '确保[[:space:]]*build[[:space:]]*通过|测试通过后提交|不要[[:space:]]*force[[:space:]]*push'
)
CONCEPT_PATTERNS=(
  '原理|概念|架构|理论|解释|是什么|为什么|教程|如何理解'
)

AUTO_ROUTING_ENABLED="$(read_auto_code_routing_flag)"
WORKING_DIR_IS_GIT_REPO="false"
if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  WORKING_DIR_IS_GIT_REPO="true"
fi
GLOBAL_SKILL_EXISTS="false"
if [ -d "$HOME/.openclaw/skills/persistent-code-terminal" ]; then
  GLOBAL_SKILL_EXISTS="true"
fi

if [ "$AUTO_ROUTING_ENABLED" != "true" ]; then
  log_decision "false" "autoCodeRoutingDisabled" "$WORKING_DIR_IS_GIT_REPO"
  echo "Auto code routing is disabled (openclaw.config.dev.autoCodeRouting=false)."
  exit 2
fi

RAW_TEXT="$INPUT_TEXT"
INSTRUCTION="$RAW_TEXT"
TRIGGER_REASON=""

if printf '%s' "$RAW_TEXT" | grep -Eiq '不要执行，只分析'; then
  log_decision "false" "explicitBypass" "$WORKING_DIR_IS_GIT_REPO"
  echo "Bypass requested: analyze-only mode."
  exit 3
fi

if printf '%s' "$RAW_TEXT" | grep -Eiq '^[[:space:]]*(codex[[:space:]]+|用[[:space:]]*codex[[:space:]]+|使用[[:space:]]*codex[[:space:]]+)'; then
  INSTRUCTION="$(strip_prefix_instruction "$RAW_TEXT")"
  TRIGGER_REASON="explicitPrefix"
fi

HAS_ACTION="false"
if contains_any "$INSTRUCTION" "${ACTION_PATTERNS[@]}"; then
  HAS_ACTION="true"
fi

if [ -z "$TRIGGER_REASON" ] && [ "$HAS_ACTION" = "true" ]; then
  TRIGGER_REASON="matchedPattern"
fi

if [ -z "$TRIGGER_REASON" ]; then
  log_decision "false" "noActionVerb" "$WORKING_DIR_IS_GIT_REPO"
  echo "No coding workflow intent detected."
  exit 4
fi

if [ "$WORKING_DIR_IS_GIT_REPO" != "true" ] && [ "$GLOBAL_SKILL_EXISTS" != "true" ]; then
  log_decision "false" "notGitRepoAndNoGlobalSkill" "$WORKING_DIR_IS_GIT_REPO"
  echo "Current directory is not a git repository and no global skill install detected; auto execution skipped."
  exit 5
fi

if [ "$TRIGGER_REASON" = "matchedPattern" ] && contains_any "$INSTRUCTION" "${CONCEPT_PATTERNS[@]}" && [ "$HAS_ACTION" != "true" ]; then
  log_decision "false" "conceptualOnly" "$WORKING_DIR_IS_GIT_REPO"
  echo "Conceptual question detected; auto execution skipped."
  exit 6
fi

TASK_PROJECTS=()
TASK_INSTRUCTIONS=()
TASK_VALID=()
TASK_DIRS=()
PARSED_PROJECTS=()

while IFS= read -r segment || [ -n "$segment" ]; do
  segment="$(trim_spaces "$segment")"
  [ -z "$segment" ] && continue
  parsed="$(parse_segment "$segment" || true)"
  if [ -z "$parsed" ]; then
    continue
  fi

  project="${parsed%%|*}"
  instruction_part="${parsed#*|}"
  TASK_PROJECTS+=("$project")
  TASK_INSTRUCTIONS+=("$instruction_part")
  if is_known_project "$project"; then
    if dir="$(project_dir_from_name "$project" 2>/dev/null || true)"; then
      if [ -n "$dir" ] && [ -d "$dir" ]; then
        TASK_VALID+=("true")
        TASK_DIRS+=("$dir")
      else
        TASK_VALID+=("false")
        TASK_DIRS+=("")
      fi
    else
      TASK_VALID+=("false")
      TASK_DIRS+=("")
    fi
  else
    TASK_VALID+=("false")
    TASK_DIRS+=("")
  fi
  PARSED_PROJECTS+=("$project")
done < <(split_segments "$INSTRUCTION")

TASKS_COUNT="${#TASK_PROJECTS[@]}"
DETECTED_MULTI_PROJECT="false"
if [ "$TASKS_COUNT" -gt 1 ]; then
  DETECTED_MULTI_PROJECT="true"
fi
PARSED_PROJECTS_JOINED="$(printf '%s,' "${PARSED_PROJECTS[@]:-}" | sed 's/,$//')"

if [ "$PARSE_ONLY" -eq 1 ]; then
  log_decision "true" "parseOnly" "$WORKING_DIR_IS_GIT_REPO" "$DETECTED_MULTI_PROJECT" "$TASKS_COUNT" "$PARSED_PROJECTS_JOINED"
  if [ "$JSON_MODE" -eq 1 ]; then
    json='{"detectedMultiProject":'
    if [ "$DETECTED_MULTI_PROJECT" = "true" ]; then
      json+='true'
    else
      json+='false'
    fi
    json+=',"tasks":['
    first=1
    i=0
    while [ "$i" -lt "$TASKS_COUNT" ]; do
      [ "$first" -eq 0 ] && json+=','
      json+='{"project":"'"$(pct_json_escape "${TASK_PROJECTS[$i]}")"'","instruction":"'"$(pct_json_escape "${TASK_INSTRUCTIONS[$i]}")"'","valid":'"${TASK_VALID[$i]}"'}'
      first=0
      i=$((i + 1))
    done
    json+=']}'
    printf '%s\n' "$json"
  else
    echo "detectedMultiProject=$DETECTED_MULTI_PROJECT tasksCount=$TASKS_COUNT"
    i=0
    while [ "$i" -lt "$TASKS_COUNT" ]; do
      echo "${TASK_PROJECTS[$i]} | ${TASK_VALID[$i]} | ${TASK_INSTRUCTIONS[$i]}"
      i=$((i + 1))
    done
  fi
  exit 0
fi

if [ "$TASKS_COUNT" -gt 1 ]; then
  log_decision "true" "matchedMultiProjectPattern" "$WORKING_DIR_IS_GIT_REPO" "true" "$TASKS_COUNT" "$PARSED_PROJECTS_JOINED"
  echo "Multi-project execution report:"
  i=0
  while [ "$i" -lt "$TASKS_COUNT" ]; do
    project="${TASK_PROJECTS[$i]}"
    task_instruction="${TASK_INSTRUCTIONS[$i]}"
    valid="${TASK_VALID[$i]}"
    project_dir="${TASK_DIRS[$i]}"
    if [ "$valid" != "true" ]; then
      echo "- $project: failure (invalid project, not found)"
      i=$((i + 1))
      continue
    fi

    run_status=0
    auto_json=""
    summary_json=""
    if [ -z "$project_dir" ] || [ ! -d "$project_dir" ]; then
      echo "- $project: failure (cannot resolve project directory)"
      i=$((i + 1))
      continue
    fi

    if ! (cd "$project_dir" && "$BASE_DIR/persistent-code-terminal-start.sh" --project "$project" >/dev/null 2>&1); then
      echo "- $project: failure (cannot start session)"
      i=$((i + 1))
      continue
    fi
    if ! auto_json="$(cd "$project_dir" && "$BASE_DIR/persistent-code-terminal-auto.sh" --max-retries 3 --instruction "$task_instruction" --json 2>&1)"; then
      run_status=$?
    fi
    if ! summary_json="$(cd "$project_dir" && "$BASE_DIR/persistent-code-terminal-summary.sh" --lines 120 --json 2>/dev/null || true)"; then
      summary_json=""
    fi

    if [ "$run_status" -ne 0 ] && printf '%s' "$auto_json" | grep -Eiq 'tmux not found|codex not found'; then
      echo "- $project: failure (runtime missing). Run $BASE_DIR/persistent-code-terminal-doctor.sh"
      i=$((i + 1))
      continue
    fi

    success="$(json_get_scalar "$auto_json" "success")"
    attempts="$(json_get_scalar "$auto_json" "attempts")"
    final_exit="$(json_get_scalar "$auto_json" "finalExitCode")"
    err_line="$(json_get_first_error_line "$summary_json")"
    if [ -z "$err_line" ]; then
      err_line="-"
    fi
    if [ -z "$attempts" ]; then
      attempts="0"
    fi
    if [ -z "$final_exit" ]; then
      final_exit="null"
    fi
    if [ "$success" = "true" ]; then
      status_label="success"
    else
      status_label="failure"
    fi
    echo "- $project: $status_label (attempts=$attempts, exit=$final_exit, error=$err_line)"
    i=$((i + 1))
  done
  exit 0
fi

log_decision "true" "$TRIGGER_REASON" "$WORKING_DIR_IS_GIT_REPO" "false" "1" "$(basename "$(pwd)")"

AUTO_OUTPUT=""
AUTO_STATUS=0
if ! AUTO_OUTPUT="$("$BASE_DIR/persistent-code-terminal-auto.sh" --max-retries 3 --instruction "$INSTRUCTION" 2>&1)"; then
  AUTO_STATUS=$?
fi

if [ "$AUTO_STATUS" -ne 0 ] && printf '%s' "$AUTO_OUTPUT" | grep -Eiq 'tmux not found|codex not found'; then
  echo "Auto execution could not start ($AUTO_OUTPUT)."
  echo "Fallback: run $BASE_DIR/persistent-code-terminal-doctor.sh and retry."
  exit 7
fi

"$BASE_DIR/persistent-code-terminal-summary.sh" --lines 120
