#!/usr/bin/env bash
# ──────────────────────────────────────────────────────────────────────
# ServiceNow Table API CLI — sn.sh
# The first ServiceNow skill for OpenClaw
#
# Author:  Brandon Wilson — ServiceNow Certified Technical Architect (CTA)
# Company: OnlyFlows (https://onlyflows.tech)
# GitHub:  https://github.com/onlyflowstech/servicenow-openclaw-skill
# License: MIT
# ──────────────────────────────────────────────────────────────────────
# Usage: bash sn.sh <command> [args...]
# Commands: query, get, create, update, delete, aggregate, schema, attach, batch, health
set -euo pipefail

# ── Configuration ──────────────────────────────────────────────────────
: "${SN_INSTANCE:?SN_INSTANCE env var required (e.g. https://instance.service-now.com)}"
: "${SN_USER:?SN_USER env var required}"
: "${SN_PASSWORD:?SN_PASSWORD env var required}"

# Ensure instance URL has no trailing slash and has https://
SN_INSTANCE="${SN_INSTANCE%/}"
[[ "$SN_INSTANCE" != http* ]] && SN_INSTANCE="https://$SN_INSTANCE"

AUTH="$SN_USER:$SN_PASSWORD"

# ── Helpers ────────────────────────────────────────────────────────────
die()  { echo "ERROR: $*" >&2; exit 1; }
info() { echo "→ $*" >&2; }

sn_curl() {
  local method="$1" url="$2"
  shift 2
  curl -sf -X "$method" "$url" \
    -u "$AUTH" \
    -H "Accept: application/json" \
    -H "Content-Type: application/json" \
    "$@"
}

# ── query ──────────────────────────────────────────────────────────────
cmd_query() {
  local table="" query="" fields="" limit="20" offset="" orderby="" display=""
  table="${1:?Usage: sn.sh query <table> [options]}"
  shift

  while [[ $# -gt 0 ]]; do
    case "$1" in
      --query)   query="$2";   shift 2 ;;
      --fields)  fields="$2";  shift 2 ;;
      --limit)   limit="$2";   shift 2 ;;
      --offset)  offset="$2";  shift 2 ;;
      --orderby) orderby="$2"; shift 2 ;;
      --display) display="$2"; shift 2 ;;
      *) die "Unknown option: $1" ;;
    esac
  done

  local url="${SN_INSTANCE}/api/now/table/${table}?sysparm_limit=${limit}"
  [[ -n "$query" ]]   && url+="&sysparm_query=$(jq -rn --arg v "$query" '$v | @uri')"
  [[ -n "$fields" ]]  && url+="&sysparm_fields=${fields}"
  [[ -n "$offset" ]]  && url+="&sysparm_offset=${offset}"
  [[ -n "$orderby" ]] && url+="&sysparm_orderby=${orderby}"
  [[ -n "$display" ]] && url+="&sysparm_display_value=${display}"

  info "GET $table (limit=$limit)"
  local resp
  resp=$(sn_curl GET "$url") || die "API request failed"

  local count
  count=$(echo "$resp" | jq '.result | length')
  echo "$resp" | jq '{record_count: (.result | length), results: .result}'
  info "Returned $count record(s)"
}

# ── get ────────────────────────────────────────────────────────────────
cmd_get() {
  local table="${1:?Usage: sn.sh get <table> <sys_id> [options]}"
  local sys_id="${2:?Usage: sn.sh get <table> <sys_id> [options]}"
  shift 2

  local fields="" display=""
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --fields)  fields="$2";  shift 2 ;;
      --display) display="$2"; shift 2 ;;
      *) die "Unknown option: $1" ;;
    esac
  done

  local url="${SN_INSTANCE}/api/now/table/${table}/${sys_id}"
  local sep="?"
  [[ -n "$fields" ]]  && url+="${sep}sysparm_fields=${fields}" && sep="&"
  [[ -n "$display" ]] && url+="${sep}sysparm_display_value=${display}"

  info "GET $table/$sys_id"
  sn_curl GET "$url" | jq '.result'
}

# ── create ─────────────────────────────────────────────────────────────
cmd_create() {
  local table="${1:?Usage: sn.sh create <table> '<json>'}"
  local json="${2:?Usage: sn.sh create <table> '<json>'}"
  shift 2

  # Validate JSON
  echo "$json" | jq . >/dev/null 2>&1 || die "Invalid JSON: $json"

  local url="${SN_INSTANCE}/api/now/table/${table}"
  info "POST $table"
  local resp
  resp=$(sn_curl POST "$url" -d "$json") || die "Create failed"
  echo "$resp" | jq '{sys_id: .result.sys_id, number: .result.number, result: .result}'
  info "Created record: $(echo "$resp" | jq -r '.result.sys_id')"
}

# ── update ─────────────────────────────────────────────────────────────
cmd_update() {
  local table="${1:?Usage: sn.sh update <table> <sys_id> '<json>'}"
  local sys_id="${2:?Usage: sn.sh update <table> <sys_id> '<json>'}"
  local json="${3:?Usage: sn.sh update <table> <sys_id> '<json>'}"
  shift 3

  echo "$json" | jq . >/dev/null 2>&1 || die "Invalid JSON: $json"

  local url="${SN_INSTANCE}/api/now/table/${table}/${sys_id}"
  info "PATCH $table/$sys_id"
  local resp
  resp=$(sn_curl PATCH "$url" -d "$json") || die "Update failed"
  echo "$resp" | jq '.result'
  info "Updated record: $sys_id"
}

# ── delete ─────────────────────────────────────────────────────────────
cmd_delete() {
  local table="${1:?Usage: sn.sh delete <table> <sys_id> --confirm}"
  local sys_id="${2:?Usage: sn.sh delete <table> <sys_id> --confirm}"
  shift 2

  local confirmed=false
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --confirm) confirmed=true; shift ;;
      *) die "Unknown option: $1" ;;
    esac
  done

  [[ "$confirmed" != "true" ]] && die "Must pass --confirm to delete records. This is a safety measure."

  local url="${SN_INSTANCE}/api/now/table/${table}/${sys_id}"
  info "DELETE $table/$sys_id"
  local http_code
  http_code=$(curl -s -o /dev/null -w "%{http_code}" -X DELETE "$url" \
    -u "$AUTH" \
    -H "Accept: application/json")

  if [[ "$http_code" == "204" || "$http_code" == "200" ]]; then
    echo '{"status":"deleted","sys_id":"'"$sys_id"'","table":"'"$table"'"}'
    info "Deleted $table/$sys_id"
  elif [[ "$http_code" == "404" ]]; then
    die "Record not found: $table/$sys_id"
  else
    die "Delete failed with HTTP $http_code"
  fi
}

# ── aggregate ──────────────────────────────────────────────────────────
cmd_aggregate() {
  local table="${1:?Usage: sn.sh aggregate <table> --type <TYPE> [options]}"
  shift

  local agg_type="" query="" field="" group_by="" display=""
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --type)     agg_type="$2"; shift 2 ;;
      --query)    query="$2";    shift 2 ;;
      --field)    field="$2";    shift 2 ;;
      --group-by) group_by="$2"; shift 2 ;;
      --display)  display="$2";  shift 2 ;;
      *) die "Unknown option: $1" ;;
    esac
  done

  [[ -z "$agg_type" ]] && die "Usage: sn.sh aggregate <table> --type <COUNT|AVG|MIN|MAX|SUM> [options]"
  agg_type=$(echo "$agg_type" | tr '[:lower:]' '[:upper:]')

  # Validate: AVG/MIN/MAX/SUM need --field
  if [[ "$agg_type" != "COUNT" && -z "$field" ]]; then
    die "$agg_type requires --field <fieldname>"
  fi

  local url="${SN_INSTANCE}/api/now/stats/${table}"
  local sep="?"

  if [[ "$agg_type" == "COUNT" ]]; then
    url+="${sep}sysparm_count=true"
  else
    url+="${sep}sysparm_${agg_type,,}_fields=${field}"
  fi
  sep="&"

  [[ -n "$query" ]]    && url+="${sep}sysparm_query=$(jq -rn --arg v "$query" '$v | @uri')"
  [[ -n "$group_by" ]] && url+="${sep}sysparm_group_by=${group_by}"
  [[ -n "$display" ]]  && url+="${sep}sysparm_display_value=${display}"

  info "STATS $agg_type on $table"
  local resp
  resp=$(sn_curl GET "$url") || die "Aggregate request failed"
  echo "$resp" | jq '.result'
}

# ── schema ─────────────────────────────────────────────────────────────
cmd_schema() {
  local table="${1:?Usage: sn.sh schema <table> [--fields-only]}"
  shift
  local fields_only=false
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --fields-only) fields_only=true; shift ;;
      *) die "Unknown option: $1" ;;
    esac
  done

  info "SCHEMA $table (via sys_dictionary)"

  local url="${SN_INSTANCE}/api/now/table/sys_dictionary?sysparm_query=name=${table}^internal_type!=collection&sysparm_fields=element,column_label,internal_type,max_length,mandatory,reference&sysparm_limit=500&sysparm_display_value=true"

  local resp
  resp=$(sn_curl GET "$url") || die "Schema request failed"

  if [[ "$fields_only" == "true" ]]; then
    echo "$resp" | jq '[.result[] | select(.element != "") | .element] | sort'
  else
    echo "$resp" | jq '[.result[] | select(.element != "") | {
      field: .element,
      label: .column_label,
      type: .internal_type,
      max_length: .max_length,
      mandatory: .mandatory,
      reference: (if .reference != "" then .reference else null end)
    }] | sort_by(.field)'
  fi
}

# ── attach ─────────────────────────────────────────────────────────────
cmd_attach() {
  local subcmd="${1:?Usage: sn.sh attach <list|download|upload> ...}"
  shift

  case "$subcmd" in
    list)
      local table="${1:?Usage: sn.sh attach list <table> <sys_id>}"
      local sys_id="${2:?Usage: sn.sh attach list <table> <sys_id>}"
      local url="${SN_INSTANCE}/api/now/attachment?sysparm_query=table_name=${table}^table_sys_id=${sys_id}"
      info "LIST attachments on $table/$sys_id"
      sn_curl GET "$url" | jq '[.result[] | {sys_id: .sys_id, file_name: .file_name, size_bytes: .size_bytes, content_type: .content_type, download_link: .download_link}]'
      ;;
    download)
      local att_id="${1:?Usage: sn.sh attach download <attachment_sys_id> <output_path>}"
      local output="${2:?Usage: sn.sh attach download <attachment_sys_id> <output_path>}"
      local url="${SN_INSTANCE}/api/now/attachment/${att_id}/file"
      info "DOWNLOAD attachment $att_id → $output"
      curl -sf -o "$output" "$url" -u "$AUTH" || die "Download failed"
      echo '{"status":"downloaded","path":"'"$output"'"}'
      ;;
    upload)
      local table="${1:?Usage: sn.sh attach upload <table> <sys_id> <file_path> [content_type]}"
      local sys_id="${2:?Usage: sn.sh attach upload <table> <sys_id> <file_path> [content_type]}"
      local filepath="${3:?Usage: sn.sh attach upload <table> <sys_id> <file_path> [content_type]}"
      local ctype="${4:-application/octet-stream}"
      local filename
      filename=$(basename "$filepath")
      local url="${SN_INSTANCE}/api/now/attachment/file?table_name=${table}&table_sys_id=${sys_id}&file_name=${filename}"
      info "UPLOAD $filename to $table/$sys_id"
      curl -sf -X POST "$url" \
        -u "$AUTH" \
        -H "Accept: application/json" \
        -H "Content-Type: ${ctype}" \
        --data-binary "@${filepath}" | jq '.result | {sys_id, file_name, size_bytes, table_name, table_sys_id}'
      ;;
    *) die "Unknown attach subcommand: $subcmd (use list, download, upload)" ;;
  esac
}

# ── batch ──────────────────────────────────────────────────────────────
cmd_batch() {
  local table="${1:?Usage: sn.sh batch <table> --query \"<query>\" --action <update|delete> [--fields '{...}'] [--dry-run] [--limit 200] [--confirm]}"
  shift

  local query="" action="" fields="" dry_run=true limit=200 confirmed=false
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --query)   query="$2";   shift 2 ;;
      --action)  action="$2";  shift 2 ;;
      --fields)  fields="$2";  shift 2 ;;
      --dry-run) dry_run=true; shift ;;
      --limit)   limit="$2";   shift 2 ;;
      --confirm) confirmed=true; dry_run=false; shift ;;
      *) die "Unknown option: $1" ;;
    esac
  done

  [[ -z "$action" ]] && die "Missing --action <update|delete>"
  [[ "$action" != "update" && "$action" != "delete" ]] && die "--action must be 'update' or 'delete'"
  [[ -z "$query" ]] && die "Missing --query (required for batch operations — refusing to operate on all records)"
  [[ "$action" == "update" && -z "$fields" ]] && die "--fields required for update action"

  # Validate fields JSON if provided
  if [[ -n "$fields" ]]; then
    echo "$fields" | jq . >/dev/null 2>&1 || die "Invalid JSON in --fields: $fields"
  fi

  # Safety cap on limit
  if (( limit > 10000 )); then
    info "WARNING: Capping limit from $limit to 10000 for safety"
    limit=10000
  fi

  # Step 1: Query matching records (sys_id only for efficiency)
  local url="${SN_INSTANCE}/api/now/table/${table}?sysparm_fields=sys_id&sysparm_limit=${limit}"
  url+="&sysparm_query=$(jq -rn --arg v "$query" '$v | @uri')"

  info "Querying $table for matching records..."
  local resp
  resp=$(sn_curl GET "$url") || die "Failed to query matching records"

  local matched
  matched=$(echo "$resp" | jq '.result | length')
  info "Found $matched record(s) matching query on $table"

  # Step 2: Dry-run check
  if [[ "$dry_run" == "true" ]]; then
    echo "{\"action\":\"$action\",\"table\":\"$table\",\"matched\":$matched,\"dry_run\":true,\"message\":\"Dry run — no changes made. Use --confirm to execute.\"}"
    return 0
  fi

  # Step 3: Safety confirmation
  if [[ "$confirmed" != "true" ]]; then
    die "Must pass --confirm to execute batch $action. Found $matched records. This is a safety measure."
  fi

  if [[ "$matched" -eq 0 ]]; then
    echo "{\"action\":\"$action\",\"table\":\"$table\",\"matched\":0,\"processed\":0,\"failed\":0}"
    return 0
  fi

  # Step 4: Extract sys_ids and iterate
  local sys_ids
  sys_ids=$(echo "$resp" | jq -r '.result[].sys_id')

  local processed=0 failed=0 total="$matched"

  while IFS= read -r sys_id; do
    [[ -z "$sys_id" ]] && continue

    if [[ "$action" == "update" ]]; then
      local patch_url="${SN_INSTANCE}/api/now/table/${table}/${sys_id}"
      if sn_curl PATCH "$patch_url" -d "$fields" >/dev/null 2>&1; then
        processed=$((processed + 1))
      else
        failed=$((failed + 1))
        info "FAILED to update $sys_id"
      fi
    elif [[ "$action" == "delete" ]]; then
      local del_url="${SN_INSTANCE}/api/now/table/${table}/${sys_id}"
      local http_code
      http_code=$(curl -s -o /dev/null -w "%{http_code}" -X DELETE "$del_url" \
        -u "$AUTH" \
        -H "Accept: application/json")
      if [[ "$http_code" == "204" || "$http_code" == "200" ]]; then
        processed=$((processed + 1))
      else
        failed=$((failed + 1))
        info "FAILED to delete $sys_id (HTTP $http_code)"
      fi
    fi

    # Progress every 10 records or at the end
    if (( processed % 10 == 0 )) || (( processed + failed == total )); then
      info "${action^}d $((processed + failed)) of $total records ($failed failed)"
    fi
  done <<< "$sys_ids"

  echo "{\"action\":\"$action\",\"table\":\"$table\",\"matched\":$matched,\"processed\":$processed,\"failed\":$failed}"
  info "Batch $action complete: $processed succeeded, $failed failed out of $matched"
}

# ── health ─────────────────────────────────────────────────────────────
cmd_health() {
  local check="all"
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --check) check="$2"; shift 2 ;;
      *) die "Unknown option: $1" ;;
    esac
  done

  local valid_checks="all version nodes jobs semaphores stats"
  if [[ ! " $valid_checks " =~ " $check " ]]; then
    die "Invalid check: $check (valid: $valid_checks)"
  fi

  local timestamp
  timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

  # Start building JSON output
  local output
  output=$(jq -n --arg inst "$SN_INSTANCE" --arg ts "$timestamp" \
    '{instance: $inst, timestamp: $ts}')

  # ── version check ──
  if [[ "$check" == "all" || "$check" == "version" ]]; then
    info "Checking instance version..."
    local ver_output='{}'

    # Get glide.war (build version)
    local ver_url="${SN_INSTANCE}/api/now/table/sys_properties?sysparm_query=name=glide.war&sysparm_fields=value&sysparm_limit=1"
    local ver_resp
    if ver_resp=$(sn_curl GET "$ver_url" 2>/dev/null); then
      local build_val
      build_val=$(echo "$ver_resp" | jq -r '.result[0].value // "unknown"')
      ver_output=$(echo "$ver_output" | jq --arg b "$build_val" '. + {build: $b}')
    else
      ver_output=$(echo "$ver_output" | jq '. + {build: "unavailable"}')
    fi

    # Get build date
    local date_url="${SN_INSTANCE}/api/now/table/sys_properties?sysparm_query=name=glide.build.date&sysparm_fields=value&sysparm_limit=1"
    if ver_resp=$(sn_curl GET "$date_url" 2>/dev/null); then
      local build_date
      build_date=$(echo "$ver_resp" | jq -r '.result[0].value // "unknown"')
      ver_output=$(echo "$ver_output" | jq --arg d "$build_date" '. + {build_date: $d}')
    fi

    # Get build tag
    local tag_url="${SN_INSTANCE}/api/now/table/sys_properties?sysparm_query=name=glide.build.tag&sysparm_fields=value&sysparm_limit=1"
    if ver_resp=$(sn_curl GET "$tag_url" 2>/dev/null); then
      local build_tag
      build_tag=$(echo "$ver_resp" | jq -r '.result[0].value // "unknown"')
      ver_output=$(echo "$ver_output" | jq --arg t "$build_tag" '. + {build_tag: $t}')
    fi

    output=$(echo "$output" | jq --argjson v "$ver_output" '. + {version: $v}')
    info "Version check complete"
  fi

  # ── nodes check ──
  if [[ "$check" == "all" || "$check" == "nodes" ]]; then
    info "Checking cluster nodes..."
    local nodes_url="${SN_INSTANCE}/api/now/table/sys_cluster_state?sysparm_fields=node_id,status,system_id,most_recent_message&sysparm_limit=50"
    local nodes_resp
    if nodes_resp=$(sn_curl GET "$nodes_url" 2>/dev/null); then
      local nodes_arr
      nodes_arr=$(echo "$nodes_resp" | jq '[.result[] | {
        node_id: .node_id,
        status: .status,
        system_id: .system_id,
        most_recent_message: .most_recent_message
      }]')
      output=$(echo "$output" | jq --argjson n "$nodes_arr" '. + {nodes: $n}')
    else
      output=$(echo "$output" | jq '. + {nodes: {"error": "Unable to query sys_cluster_state — check ACLs"}}')
    fi
    info "Nodes check complete"
  fi

  # ── jobs check ──
  if [[ "$check" == "all" || "$check" == "jobs" ]]; then
    info "Checking scheduled jobs..."
    local jobs_query="state=0^next_action<javascript:gs.minutesAgo(30)"
    local jobs_url="${SN_INSTANCE}/api/now/table/sys_trigger?sysparm_fields=name,next_action,state,trigger_type&sysparm_limit=20"
    jobs_url+="&sysparm_query=$(jq -rn --arg v "$jobs_query" '$v | @uri')"
    local jobs_resp
    if jobs_resp=$(sn_curl GET "$jobs_url" 2>/dev/null); then
      local stuck_count overdue_list
      stuck_count=$(echo "$jobs_resp" | jq '.result | length')
      overdue_list=$(echo "$jobs_resp" | jq '[.result[] | {
        name: .name,
        next_action: .next_action,
        state: .state,
        trigger_type: .trigger_type
      }]')
      output=$(echo "$output" | jq --argjson sc "$stuck_count" --argjson ol "$overdue_list" \
        '. + {jobs: {stuck: $sc, overdue: $ol}}')
    else
      output=$(echo "$output" | jq '. + {jobs: {"error": "Unable to query sys_trigger — check ACLs"}}')
    fi
    info "Jobs check complete"
  fi

  # ── semaphores check ──
  if [[ "$check" == "all" || "$check" == "semaphores" ]]; then
    info "Checking semaphores..."
    local sem_url="${SN_INSTANCE}/api/now/table/sys_semaphore?sysparm_query=state=active&sysparm_fields=name,state,holder&sysparm_limit=20"
    local sem_resp
    if sem_resp=$(sn_curl GET "$sem_url" 2>/dev/null); then
      local sem_count sem_list
      sem_count=$(echo "$sem_resp" | jq '.result | length')
      sem_list=$(echo "$sem_resp" | jq '[.result[] | {
        name: .name,
        state: .state,
        holder: .holder
      }]')
      output=$(echo "$output" | jq --argjson ac "$sem_count" --argjson sl "$sem_list" \
        '. + {semaphores: {active: $ac, list: $sl}}')
    else
      output=$(echo "$output" | jq '. + {semaphores: {"error": "Unable to query sys_semaphore — check ACLs"}}')
    fi
    info "Semaphores check complete"
  fi

  # ── stats check ──
  if [[ "$check" == "all" || "$check" == "stats" ]]; then
    info "Gathering instance stats..."
    local stats_output='{}'

    # Active incidents (state != 7 = Closed)
    local inc_url="${SN_INSTANCE}/api/now/stats/incident?sysparm_count=true&sysparm_query=$(jq -rn --arg v 'state!=7' '$v | @uri')"
    local inc_resp
    if inc_resp=$(sn_curl GET "$inc_url" 2>/dev/null); then
      local inc_count
      inc_count=$(echo "$inc_resp" | jq -r '.result.stats.count // "0"')
      stats_output=$(echo "$stats_output" | jq --arg c "$inc_count" '. + {incidents_active: ($c | tonumber)}')
    fi

    # Open P1 incidents
    local p1_url="${SN_INSTANCE}/api/now/stats/incident?sysparm_count=true&sysparm_query=$(jq -rn --arg v 'active=true^priority=1' '$v | @uri')"
    local p1_resp
    if p1_resp=$(sn_curl GET "$p1_url" 2>/dev/null); then
      local p1_count
      p1_count=$(echo "$p1_resp" | jq -r '.result.stats.count // "0"')
      stats_output=$(echo "$stats_output" | jq --arg c "$p1_count" '. + {p1_open: ($c | tonumber)}')
    fi

    # Active changes
    local chg_url="${SN_INSTANCE}/api/now/stats/change_request?sysparm_count=true&sysparm_query=$(jq -rn --arg v 'active=true' '$v | @uri')"
    local chg_resp
    if chg_resp=$(sn_curl GET "$chg_url" 2>/dev/null); then
      local chg_count
      chg_count=$(echo "$chg_resp" | jq -r '.result.stats.count // "0"')
      stats_output=$(echo "$stats_output" | jq --arg c "$chg_count" '. + {changes_active: ($c | tonumber)}')
    fi

    # Open problems
    local prb_url="${SN_INSTANCE}/api/now/stats/problem?sysparm_count=true&sysparm_query=$(jq -rn --arg v 'active=true' '$v | @uri')"
    local prb_resp
    if prb_resp=$(sn_curl GET "$prb_url" 2>/dev/null); then
      local prb_count
      prb_count=$(echo "$prb_resp" | jq -r '.result.stats.count // "0"')
      stats_output=$(echo "$stats_output" | jq --arg c "$prb_count" '. + {problems_open: ($c | tonumber)}')
    fi

    output=$(echo "$output" | jq --argjson s "$stats_output" '. + {stats: $s}')
    info "Stats check complete"
  fi

  echo "$output" | jq .
}

# ── Main dispatcher ────────────────────────────────────────────────────
cmd="${1:?Usage: sn.sh <query|get|create|update|delete|aggregate|schema|attach|batch|health> ...}"
shift

case "$cmd" in
  query)     cmd_query "$@" ;;
  get)       cmd_get "$@" ;;
  create)    cmd_create "$@" ;;
  update)    cmd_update "$@" ;;
  delete)    cmd_delete "$@" ;;
  aggregate) cmd_aggregate "$@" ;;
  schema)    cmd_schema "$@" ;;
  attach)    cmd_attach "$@" ;;
  batch)     cmd_batch "$@" ;;
  health)    cmd_health "$@" ;;
  *)         die "Unknown command: $cmd" ;;
esac
