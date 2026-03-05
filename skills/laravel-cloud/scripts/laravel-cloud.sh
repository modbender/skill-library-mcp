#!/usr/bin/env bash
# laravel-cloud — Laravel Cloud API CLI
# https://cloud.laravel.com/docs/api/introduction
set -euo pipefail

BASE="https://cloud.laravel.com/api"
CREDS="${HOME}/.openclaw/credentials/laravel-cloud/config.json"

# If token is a 1Password reference (op://...), resolve it first.
# If resolution fails, treat it as unset so we can fall back to creds file.
if [[ -n "${LARAVEL_CLOUD_API_TOKEN:-}" ]] && [[ "${LARAVEL_CLOUD_API_TOKEN}" == op://* ]]; then
  if command -v op >/dev/null 2>&1; then
    _resolved_token="$(op read "${LARAVEL_CLOUD_API_TOKEN}" 2>/dev/null || true)"
    if [[ -n "${_resolved_token}" ]]; then
      LARAVEL_CLOUD_API_TOKEN="${_resolved_token}"
    else
      unset LARAVEL_CLOUD_API_TOKEN
    fi
  else
    unset LARAVEL_CLOUD_API_TOKEN
  fi
fi

[[ -z "${LARAVEL_CLOUD_API_TOKEN:-}" ]] && [[ -f "$CREDS" ]] && \
  LARAVEL_CLOUD_API_TOKEN=$(jq -r '.token // empty' "$CREDS" 2>/dev/null || true)
: "${LARAVEL_CLOUD_API_TOKEN:?Set LARAVEL_CLOUD_API_TOKEN or create $CREDS with {\"token\":\"...\"}}"

die() { echo "Error: $*" >&2; exit 1; }

# api METHOD /path [json-body]
api() {
  local a=(-s -S -X "$1" -H "Authorization: Bearer $LARAVEL_CLOUD_API_TOKEN" -H "Accept: application/json")
  [[ ${3+x} ]] && a+=(-H "Content-Type: application/json" -d "$3")
  curl "${a[@]}" "${BASE}$2" | jq .
}

# Extract --name value from args
flag() {
  local f="--$1"; shift
  while [[ $# -gt 0 ]]; do [[ "$1" == "$f" && $# -gt 1 ]] && echo "$2" && return; shift; done
}

# Query string helper: qs key value → ?key=value (empty if no value)
qs() { [[ -n "${2:-}" ]] && echo "?$1=$2"; }

# Build JSON from key=value pairs, dropping empties. Use :bool/:int suffixes for type coercion.
jb() {
  local args=()
  for kv in "$@"; do
    local k="${kv%%=*}" v="${kv#*=}"
    [[ -z "$v" ]] && continue
    case "$k" in
      *:bool) args+=(--argjson "${k%:bool}" "$([[ $v == true ]] && echo true || echo false)") ;;
      *:int)  args+=(--argjson "${k%:int}" "$v") ;;
      *)      args+=(--arg "$k" "$v") ;;
    esac
  done
  [[ ${#args[@]} -eq 0 ]] && echo '{}' && return
  jq -n "${args[@]}" '$ARGS.named'
}

# Parse comma-separated KEY=val pairs to JSON array
parse_vars() {
  echo "$1" | tr ',' '\n' | jq -R 'split("=") | {key:.[0], value:(.[1:]|join("="))}' | jq -s .
}

# ── apps ──
cmd_apps() {
  local act=${1:-help}; shift 2>/dev/null || true
  case $act in
    list)   api GET /applications ;;
    get)    [[ ${1:-} ]] || die "app-id required"; api GET "/applications/$1" ;;
    create)
      local n=$(flag name "$@") r=$(flag region "$@") repo=$(flag repository "$@") scp=$(flag source-control "$@")
      : "${scp:=github}"
      [[ $n && $r && $repo ]] || die "usage: apps create --name NAME --region REGION --repository owner/repo [--source-control github|gitlab|bitbucket]"
      local body; body="$(jb name="$n" region="$r" repository="$repo" source_control_provider_type="$scp")"
      api POST /applications "$body" ;;
    update)
      [[ ${1:-} ]] || die "app-id required"; local id=$1; shift
      api PATCH "/applications/$id" "$(jb name="$(flag name "$@")" slack_channel="$(flag slack-channel "$@")")" ;;
    delete) [[ ${1:-} ]] || die "app-id required"; api DELETE "/applications/$1" ;;
    *) echo "apps: list | get <id> | create --name N --region R --repository owner/repo [--source-control github|gitlab|bitbucket] | update <id> [--name N] [--slack-channel C] | delete <id>" ;;
  esac
}

# ── envs ──
cmd_envs() {
  local act=${1:-help}; shift 2>/dev/null || true
  case $act in
    list)    [[ ${1:-} ]] || die "app-id required"; api GET "/applications/$1/environments" ;;
    get)     [[ ${1:-} ]] || die "env-id required"
             api GET "/environments/$1$(qs include "$(flag include "${@:2}")")" ;;
    create)
      [[ ${1:-} ]] || die "app-id required"; local app=$1; shift
      local n=$(flag name "$@") b=$(flag branch "$@")
      [[ $n && $b ]] || die "usage: envs create <app-id> --name N --branch B"
      api POST "/applications/$app/environments" \
        "$(jb name="$n" branch="$b" cluster_id="$(flag cluster-id "$@")")" ;;
    update)
      [[ ${1:-} ]] || die "env-id required"; local id=$1; shift
      local body; body="$(jb \
        php_major_version="$(flag php-version "$@")" node_version="$(flag node-version "$@")" \
        build_command="$(flag build-command "$@")" deploy_command="$(flag deploy-command "$@")" \
        database_schema_id="$(flag database-schema-id "$@")" \
        cache_id="$(flag cache-id "$@")" \
        websocket_application_id="$(flag websocket-app-id "$@")")"
      local fk=$(flag filesystem-key "$@") fd=$(flag filesystem-disk "$@")
      if [[ -n "$fk" ]]; then
        : "${fd:=s3}"
        body="$(echo "$body" | jq --arg k "$fk" --arg d "$fd" '. + {filesystem_keys: [{id: $k, disk: $d, is_default_disk: true}]}')"
      fi
      api PATCH "/environments/$id" "$body" ;;
    delete)  [[ ${1:-} ]] || die "env-id required"; api DELETE "/environments/$1" ;;
    start)   [[ ${1:-} ]] || die "env-id required"; api POST "/environments/$1/start" '{}' ;;
    stop)    [[ ${1:-} ]] || die "env-id required"; api POST "/environments/$1/stop" '{}' ;;
    metrics) [[ ${1:-} ]] || die "env-id required"
             api GET "/environments/$1/metrics$(qs period "$(flag period "${@:2}")")" ;;
    logs)
      [[ ${1:-} ]] || die "env-id required"; local eid=$1; shift 2>/dev/null || true
      local f=$(flag from "$@") t=$(flag to "$@")
      # Default: last 15 minutes
      [[ -z "$f" ]] && f=$(date -u -d '15 minutes ago' '+%Y-%m-%dT%H:%M:%S.000000Z' 2>/dev/null || date -u -v-15M '+%Y-%m-%dT%H:%M:%S.000000Z')
      [[ -z "$t" ]] && t=$(date -u '+%Y-%m-%dT%H:%M:%S.000000Z')
      api GET "/environments/$eid/logs?from=$(jq -rn --arg v "$f" '$v|@uri')&to=$(jq -rn --arg v "$t" '$v|@uri')" ;;
    vars-add)
      [[ ${1:-} ]] || die "env-id required"; local id=$1; shift
      local v=$(flag vars "$@"); [[ $v ]] || die "--vars required"
      local m=$(flag method "$@")
      api POST "/environments/$id/variables" \
        "$(jq -n --arg m "${m:-set}" --argjson v "$(parse_vars "$v")" '{method:$m,variables:$v}')" ;;
    vars-replace)
      [[ ${1:-} ]] || die "env-id required"; local id=$1; shift
      local c=$(flag content "$@") v=$(flag vars "$@")
      if [[ $c ]]; then api PUT "/environments/$id/variables" "$(jq -n --arg c "$c" '{content:$c}')"
      elif [[ $v ]]; then api PUT "/environments/$id/variables" "$(jq -n --argjson v "$(parse_vars "$v")" '{variables:$v}')"
      else die "--content or --vars required"; fi ;;
    *) cat <<'EOF'
envs: list <app-id> | get <env-id> [--include app,branch,...] | delete <env-id>
      create <app-id> --name N --branch B [--cluster-id ID]
      update <env-id> [--php-version V] [--node-version V] [--build-command C] [--deploy-command C]
             [--database-schema-id ID] [--cache-id ID] [--websocket-app-id ID]
      start <env-id> | stop <env-id> | metrics <env-id> [--period 1h|6h|24h|7d|30d]
      logs <env-id> [--from ISO8601] [--to ISO8601]  (default: last 15 min)
      vars-add <env-id> --vars 'K=V,K2=V2' [--method set|append]
      vars-replace <env-id> --content '...' | --vars 'K=V,K2=V2'
EOF
  esac
}

# ── commands ──
cmd_commands() {
  local act=${1:-help}; shift 2>/dev/null || true
  case $act in
    list) [[ ${1:-} ]] || die "env-id required"; api GET "/environments/$1/commands" ;;
    get)  [[ ${1:-} ]] || die "command-id required"; api GET "/commands/$1" ;;
    run)
      [[ ${1:-} ]] || die "env-id required"; local id=$1; shift
      local c=$(flag command "$@"); [[ $c ]] || die "--command required"
      api POST "/environments/$id/commands" "$(jb command="$c")" ;;
    *) echo 'commands: list <env-id> | get <cmd-id> | run <env-id> --command "php artisan ..."' ;;
  esac
}

# ── deployments ──
cmd_deployments() {
  local act=${1:-help}; shift 2>/dev/null || true
  case $act in
    list)     [[ ${1:-} ]] || die "env-id required"; api GET "/environments/$1/deployments" ;;
    get)      [[ ${1:-} ]] || die "deployment-id required"; api GET "/deployments/$1" ;;
    initiate) [[ ${1:-} ]] || die "env-id required"; api POST "/environments/$1/deployments" '{}' ;;
    *) echo "deployments: list <env-id> | get <dep-id> | initiate <env-id>" ;;
  esac
}

# ── domains ──
cmd_domains() {
  local act=${1:-help}; shift 2>/dev/null || true
  case $act in
    list)   [[ ${1:-} ]] || die "env-id required"; api GET "/environments/$1/domains" ;;
    get)    [[ ${1:-} ]] || die "domain-id required"; api GET "/domains/$1" ;;
    create)
      [[ ${1:-} ]] || die "env-id required"; local eid=$1; shift
      local n=$(flag name "$@"); [[ $n ]] || die "--name required"
      api POST "/environments/$eid/domains" "$(jb name="$n" \
        www_redirect="$(flag redirect "$@")" verification_method="$(flag verification-method "$@")" \
        wildcard_enabled:bool="$(flag wildcard "$@")")" ;;
    update)
      [[ ${1:-} ]] || die "domain-id required"; local id=$1; shift
      api PATCH "/domains/$id" "$(jb www_redirect="$(flag redirect "$@")" \
        wildcard_enabled:bool="$(flag wildcard "$@")")" ;;
    delete) [[ ${1:-} ]] || die "domain-id required"; api DELETE "/domains/$1" ;;
    verify) [[ ${1:-} ]] || die "domain-id required"; api POST "/domains/$1/verify" '{}' ;;
    *) cat <<'EOF'
domains: list <env-id> | get <id> | delete <id> | verify <id>
         create <env-id> --name example.com [--redirect root_to_www|www_to_root] [--wildcard true]
         update <id> [--redirect ...] [--wildcard true|false]
EOF
  esac
}

# ── instances ──
cmd_instances() {
  local act=${1:-help}; shift 2>/dev/null || true
  case $act in
    list)  [[ ${1:-} ]] || die "env-id required"; api GET "/environments/$1/instances" ;;
    get)   [[ ${1:-} ]] || die "instance-id required"; api GET "/instances/$1" ;;
    sizes) api GET /instances/sizes ;;
    create)
      [[ ${1:-} ]] || die "env-id required"; local eid=$1; shift
      local n=$(flag name "$@") s=$(flag size "$@")
      [[ $n && $s ]] || die "usage: instances create <env-id> --name N --size S"
      api POST "/environments/$eid/instances" "$(jb name="$n" size="$s" \
        type="$(flag type "$@")" scaling_type="$(flag scaling-type "$@")" \
        min_replicas:int="$(flag min-replicas "$@")" max_replicas:int="$(flag max-replicas "$@")" \
        uses_scheduler:bool="$(flag uses-scheduler "$@")")" ;;
    update)
      [[ ${1:-} ]] || die "instance-id required"; local id=$1; shift
      api PATCH "/instances/$id" "$(jb size="$(flag size "$@")" scaling_type="$(flag scaling-type "$@")" \
        min_replicas:int="$(flag min-replicas "$@")" max_replicas:int="$(flag max-replicas "$@")" \
        scaling_cpu_threshold_percentage:int="$(flag scaling-cpu-threshold "$@")" \
        scaling_memory_threshold_percentage:int="$(flag scaling-memory-threshold "$@")")" ;;
    delete) [[ ${1:-} ]] || die "instance-id required"; api DELETE "/instances/$1" ;;
    *) cat <<'EOF'
instances: list <env-id> | get <id> | sizes | delete <id>
           create <env-id> --name N --size S [--type service] [--scaling-type none|custom|auto]
                  [--min-replicas 1] [--max-replicas 3] [--uses-scheduler false]
           update <id> [--size S] [--scaling-type none|custom|auto] [--min-replicas N] [--max-replicas N]
                  [--scaling-cpu-threshold N] [--scaling-memory-threshold N]
EOF
  esac
}

# ── bg-processes ──
cmd_bg_processes() {
  local act=${1:-help}; shift 2>/dev/null || true
  case $act in
    list) [[ ${1:-} ]] || die "instance-id required"; api GET "/instances/$1/background-processes" ;;
    get)  [[ ${1:-} ]] || die "bg-process-id required"; api GET "/background-processes/$1" ;;
    create)
      [[ ${1:-} ]] || die "instance-id required"; local iid=$1; shift
      local n=$(flag name "$@") c=$(flag command "$@")
      [[ $n && $c ]] || die "usage: bg-processes create <instance-id> --name N --command C"
      api POST "/instances/$iid/background-processes" "$(jb name="$n" command="$c")" ;;
    update)
      [[ ${1:-} ]] || die "bg-process-id required"; local id=$1; shift
      api PATCH "/background-processes/$id" "$(jb name="$(flag name "$@")" command="$(flag command "$@")")" ;;
    delete) [[ ${1:-} ]] || die "bg-process-id required"; api DELETE "/background-processes/$1" ;;
    *) echo 'bg-processes: list <inst-id> | get <id> | create <inst-id> --name N --command C | update <id> [--name N] [--command C] | delete <id>' ;;
  esac
}

# ── databases ──
cmd_databases() {
  local act=${1:-help}; shift 2>/dev/null || true
  case $act in
    clusters)        api GET /databases/clusters ;;
    cluster)         [[ ${1:-} ]] || die "cluster-id required"; api GET "/databases/clusters/$1" ;;
    cluster-create)
      local n=$(flag name "$@") t=$(flag type "$@") r=$(flag region "$@")
      [[ $n && $t && $r ]] || die "usage: databases cluster-create --name N --type T --region R [--size S] [--storage N] [--public true|false] [--scheduled-snapshots true|false] [--retention-days N] [--cluster-id ID]"
      local ss=$(flag scheduled-snapshots "$@") rd=$(flag retention-days "$@")
      local cfg=$(jb size="$(flag size "$@")" storage:int="$(flag storage "$@")" \
        is_public:bool="$(flag public "$@")" \
        uses_scheduled_snapshots:bool="${ss:-true}" \
        retention_days:int="${rd:-1}")
      api POST /databases/clusters "$(jq -n \
        --arg name "$n" --arg type "$t" --arg region "$r" \
        --argjson config "$cfg" \
        --arg cluster_id "$(flag cluster-id "$@")" \
        '{name:$name, type:$type, region:$region, config:$config} + (if $cluster_id != "" then {cluster_id:($cluster_id|tonumber)} else {} end)')" ;;
    cluster-update)
      [[ ${1:-} ]] || die "cluster-id required"; local id=$1; shift
      api PATCH "/databases/clusters/$id" "$(jb name="$(flag name "$@")")" ;;
    cluster-delete)  [[ ${1:-} ]] || die "cluster-id required"; api DELETE "/databases/clusters/$1" ;;
    cluster-metrics) [[ ${1:-} ]] || die "cluster-id required"
                     api GET "/databases/clusters/$1/metrics$(qs period "$(flag period "${@:2}")")" ;;
    types)    api GET /databases/types ;;
    list)     [[ ${1:-} ]] || die "cluster-id required"; api GET "/databases/clusters/$1/databases" ;;
    get)      [[ ${1:-} ]] || die "database-id required"; api GET "/databases/$1" ;;
    create)
      [[ ${1:-} ]] || die "cluster-id required"; local cid=$1; shift
      local n=$(flag name "$@"); [[ $n ]] || die "--name required"
      api POST "/databases/clusters/$cid/databases" "$(jb name="$n")" ;;
    delete)          [[ ${1:-} ]] || die "database-id required"; api DELETE "/databases/$1" ;;
    snapshots)       [[ ${1:-} ]] || die "cluster-id required"; api GET "/databases/clusters/$1/snapshots" ;;
    snapshot)        [[ ${1:-} ]] || die "snapshot-id required"; api GET "/database-snapshots/$1" ;;
    snapshot-create) [[ ${1:-} ]] || die "cluster-id required"; api POST "/databases/clusters/$1/snapshots" '{}' ;;
    snapshot-delete) [[ ${1:-} ]] || die "snapshot-id required"; api DELETE "/database-snapshots/$1" ;;
    restore)
      [[ ${1:-} ]] || die "cluster-id required"; local cid=$1; shift
      local n=$(flag name "$@"); [[ $n ]] || die "--name required"
      api POST "/databases/clusters/$cid/restore" "$(jb name="$n" \
        snapshot_id="$(flag snapshot-id "$@")" point_in_time="$(flag point-in-time "$@")")" ;;
    dedicated) api GET /dedicated-clusters ;;
    *) cat <<'EOF'
databases: clusters | cluster <id>
           cluster-create --name N --type T --region R [--size S] [--storage N] [--public true|false]
                          [--scheduled-snapshots true|false] [--retention-days N] [--cluster-id ID]
           cluster-update <id> [--name N] | cluster-delete <id> | cluster-metrics <id> [--period ...]
           types | list <cluster-id> | get <db-id> | create <cluster-id> --name N | delete <db-id>
           snapshots <cluster-id> | snapshot <id> | snapshot-create <cluster-id> | snapshot-delete <id>
           restore <cluster-id> --name N [--snapshot-id ID] [--point-in-time DATETIME] | dedicated
EOF
  esac
}

# ── caches ──
cmd_caches() {
  local act=${1:-help}; shift 2>/dev/null || true
  case $act in
    list)  api GET /caches ;;
    get)   [[ ${1:-} ]] || die "cache-id required"; api GET "/caches/$1" ;;
    types) api GET /caches/types ;;
    create)
      local n=$(flag name "$@") t=$(flag type "$@") r=$(flag region "$@") s=$(flag size "$@")
      [[ $n && $t && $r && $s ]] || die "usage: caches create --name N --type T --region R --size S [--auto-upgrade true] [--public false] [--eviction-policy P]"
      local au=$(flag auto-upgrade "$@") ip=$(flag public "$@")
      local body; body="$(jb name="$n" type="$t" region="$r" size="$s" \
        eviction_policy="$(flag eviction-policy "$@")" \
        auto_upgrade_enabled:bool="${au:-true}")"
      # Upstash rejects is_public; all other types require it
      if [[ "$t" != "upstash_redis" ]]; then
        body="$(echo "$body" | jq --argjson p "$(echo "${ip:-false}" | jq -R 'if . == "true" then true else false end')" '. + {is_public: $p}')"
      fi
      api POST /caches "$body" ;;
    update)
      [[ ${1:-} ]] || die "cache-id required"; local id=$1; shift
      api PATCH "/caches/$id" "$(jb size="$(flag size "$@")" \
        auto_upgrade_enabled:bool="$(flag auto-upgrade "$@")")" ;;
    delete)  [[ ${1:-} ]] || die "cache-id required"; api DELETE "/caches/$1" ;;
    metrics) [[ ${1:-} ]] || die "cache-id required"
             api GET "/caches/$1/metrics$(qs period "$(flag period "${@:2}")")" ;;
    *) cat <<'EOF'
caches: list | get <id> | types | delete <id> | metrics <id> [--period 1h|6h|24h|7d|30d]
        create --name N --type T --region R --size S [--auto-upgrade true] [--public false] [--eviction-policy allkeys-lru]
        update <id> [--size S] [--auto-upgrade true|false]
EOF
  esac
}

# ── buckets ──
cmd_buckets() {
  local act=${1:-help}; shift 2>/dev/null || true
  case $act in
    list)   api GET /buckets ;;
    get)    [[ ${1:-} ]] || die "bucket-id required"; api GET "/buckets/$1" ;;
    create)
      local n=$(flag name "$@") r=$(flag region "$@") vis=$(flag visibility "$@") jur=$(flag jurisdiction "$@")
      local kn=$(flag key-name "$@") kp=$(flag key-permission "$@")
      : "${vis:=private}" "${jur:=default}" "${kp:=read_write}"
      [[ -z "$kn" ]] && kn="${n}-key"
      [[ $n && $r ]] || die "usage: buckets create --name N --region R [--visibility private|public] [--jurisdiction default|eu] [--key-name N] [--key-permission read_write|read_only]"
      api POST /buckets "$(jb name="$n" region="$r" visibility="$vis" jurisdiction="$jur" key_name="$kn" key_permission="$kp")" ;;
    update)
      [[ ${1:-} ]] || die "bucket-id required"; local id=$1; shift
      api PATCH "/buckets/$id" "$(jb name="$(flag name "$@")")" ;;
    delete) [[ ${1:-} ]] || die "bucket-id required"; api DELETE "/buckets/$1" ;;
    *) echo "buckets: list | get <id> | create --name N --region R [--visibility private|public] [--jurisdiction default|eu] [--key-name N] [--key-permission read_write|read_only] | update <id> [--name N] | delete <id>" ;;
  esac
}

# ── bucket-keys ──
cmd_bucket_keys() {
  local act=${1:-help}; shift 2>/dev/null || true
  case $act in
    list) [[ ${1:-} ]] || die "bucket-id required"; api GET "/buckets/$1/keys" ;;
    get)  [[ ${1:-} ]] || die "key-id required"; api GET "/bucket-keys/$1" ;;
    create)
      [[ ${1:-} ]] || die "bucket-id required"; local bid=$1; shift
      local n=$(flag name "$@"); [[ $n ]] || die "--name required"
      local perm=$(flag permission "$@")
      api POST "/buckets/$bid/keys" "$(jb name="$n" permission="${perm:-read_write}")" ;;
    update)
      [[ ${1:-} ]] || die "key-id required"; local id=$1; shift
      api PATCH "/bucket-keys/$id" "$(jb name="$(flag name "$@")" \
        permission="$(flag permission "$@")")" ;;
    delete) [[ ${1:-} ]] || die "key-id required"; api DELETE "/bucket-keys/$1" ;;
    *) echo "bucket-keys: list <bucket-id> | get <id> | create <bucket-id> --name N [--permission read_write|read_only] | update <id> [--name N] [--permission P] | delete <id>" ;;
  esac
}

# ── websockets ──
cmd_websockets() {
  local act=${1:-help}; shift 2>/dev/null || true
  case $act in
    list)   api GET /websocket-servers ;;
    get)    [[ ${1:-} ]] || die "ws-cluster-id required"; api GET "/websocket-servers/$1" ;;
    create)
      local n=$(flag name "$@") r=$(flag region "$@")
      [[ $n && $r ]] || die "usage: websockets create --name N --region R"
      api POST /websocket-servers "$(jb name="$n" region="$r" size="$(flag size "$@")")" ;;
    update)
      [[ ${1:-} ]] || die "ws-cluster-id required"; local id=$1; shift
      api PATCH "/websocket-servers/$id" "$(jb name="$(flag name "$@")" size="$(flag size "$@")")" ;;
    delete)  [[ ${1:-} ]] || die "ws-cluster-id required"; api DELETE "/websocket-servers/$1" ;;
    metrics) [[ ${1:-} ]] || die "ws-cluster-id required"
             api GET "/websocket-servers/$1/metrics$(qs period "$(flag period "${@:2}")")" ;;
    *) echo "websockets: list | get <id> | create --name N --region R [--size S] | update <id> [--name N] [--size S] | delete <id> | metrics <id> [--period ...]" ;;
  esac
}

# ── ws-apps ──
cmd_ws_apps() {
  local act=${1:-help}; shift 2>/dev/null || true
  case $act in
    list) [[ ${1:-} ]] || die "ws-cluster-id required (get one from: laravel-cloud websockets list)"; api GET "/websocket-servers/$1/applications" ;;
    get)  [[ ${1:-} ]] || die "ws-app-id required"; api GET "/websocket-applications/$1" ;;
    create)
      [[ ${1:-} ]] || die "ws-cluster-id required"; local wid=$1; shift
      local n=$(flag name "$@"); [[ $n ]] || die "--name required"
      api POST "/websocket-servers/$wid/applications" "$(jb name="$n")" ;;
    update)
      [[ ${1:-} ]] || die "ws-app-id required"; local id=$1; shift
      api PATCH "/websocket-applications/$id" "$(jb name="$(flag name "$@")")" ;;
    delete)  [[ ${1:-} ]] || die "ws-app-id required"; api DELETE "/websocket-applications/$1" ;;
    metrics) [[ ${1:-} ]] || die "ws-app-id required"
             api GET "/websocket-applications/$1/metrics$(qs period "$(flag period "${@:2}")")" ;;
    *) echo "ws-apps: list <ws-id> | get <id> | create <ws-id> --name N | update <id> [--name N] | delete <id> | metrics <id> [--period ...]" ;;
  esac
}

# ── simple resources ──
cmd_ips()     { api GET /ip; }
cmd_org()     { api GET /meta/organization; }
cmd_regions() { api GET /meta/regions; }

# ── help ──
show_help() {
  cat <<'EOF'
laravel-cloud — Laravel Cloud API CLI

Usage: laravel-cloud <resource> <action> [args...]

Resources:
  apps          Applications                envs          Environments + env vars
  commands      Run artisan/shell commands  deployments   Deployment management
  domains       Custom domains              instances     Compute + scaling
  bg-processes  Background workers          databases     DB clusters, schemas, snapshots
  caches        Redis/Valkey clusters       buckets       Object storage (S3-compatible)
  bucket-keys   Bucket access keys          websockets    WebSocket clusters (Reverb)
  ws-apps       WebSocket applications      ips           Whitelisted IPs
  org           Organization info           regions       Available regions

Auth: export LARAVEL_CLOUD_API_TOKEN=... or create ~/.openclaw/credentials/laravel-cloud/config.json
Help: laravel-cloud <resource> help
EOF
}

# ── dispatch ──
resource=${1:-help}; shift 2>/dev/null || true
case $resource in
  apps|applications)                 cmd_apps "$@" ;;
  envs|environments)                 cmd_envs "$@" ;;
  commands|cmd)                      cmd_commands "$@" ;;
  deployments|deploy)                cmd_deployments "$@" ;;
  domains)                           cmd_domains "$@" ;;
  instances)                         cmd_instances "$@" ;;
  bg-processes|background-processes) cmd_bg_processes "$@" ;;
  databases|db)                      cmd_databases "$@" ;;
  caches)                            cmd_caches "$@" ;;
  buckets)                           cmd_buckets "$@" ;;
  bucket-keys)                       cmd_bucket_keys "$@" ;;
  websockets|ws)                     cmd_websockets "$@" ;;
  ws-apps|websocket-apps)            cmd_ws_apps "$@" ;;
  ips)                               cmd_ips ;;
  org|organization)                  cmd_org ;;
  regions)                           cmd_regions ;;
  help|--help|-h)                    show_help ;;
  *) die "Unknown resource: $resource — run: laravel-cloud help" ;;
esac
