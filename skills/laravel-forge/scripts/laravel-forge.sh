#!/usr/bin/env bash
# laravel-forge — Laravel Forge API CLI
# https://forge.laravel.com/api-documentation
set -euo pipefail

BASE="https://forge.laravel.com/api"
CREDS="${HOME}/.openclaw/credentials/laravel-forge/config.json"

# Check if this is a help command
IS_HELP=false
for arg in "$@"; do
  if [[ "$arg" =~ ^(help|--help|-h)$ ]]; then
    IS_HELP=true
    break
  fi
done

# Allow help commands without credentials
if [[ "$IS_HELP" == true ]]; then
  # Skip credential check for help
  LARAVEL_FORGE_API_TOKEN=""
  ORG=""
else
  # Load credentials
  [[ -z "${LARAVEL_FORGE_API_TOKEN:-}" ]] && [[ -f "$CREDS" ]] && \
    LARAVEL_FORGE_API_TOKEN=$(jq -r '.token // empty' "$CREDS" 2>/dev/null || true)
  : "${LARAVEL_FORGE_API_TOKEN:?Set LARAVEL_FORGE_API_TOKEN or create $CREDS with {\"token\":\"...\",\"org\":\"...\"}}"

  # Load default org
  ORG="${LARAVEL_FORGE_ORG:-}"
  [[ -z "$ORG" && -f "$CREDS" ]] && ORG=$(jq -r '.org // empty' "$CREDS" 2>/dev/null || true)
fi

die() { echo "Error: $*" >&2; exit 1; }

# API call helper - extracts data.attributes from JSON:API responses when present
api() {
  local a=(-s -S -X "$1" -H "Authorization: Bearer $LARAVEL_FORGE_API_TOKEN" -H "Accept: application/json")
  [[ ${3+x} ]] && a+=(-H "Content-Type: application/json" -d "$3")
  local out; out=$(curl "${a[@]}" "${BASE}$2")
  
  # Check if it's valid JSON
  if echo "$out" | jq . >/dev/null 2>&1; then
    # Try to extract data.attributes for JSON:API format, otherwise return as-is
    if echo "$out" | jq -e '.data.attributes' >/dev/null 2>&1; then
      echo "$out" | jq '.data'
    elif echo "$out" | jq -e '.data' >/dev/null 2>&1; then
      echo "$out" | jq '.data'
    else
      echo "$out" | jq .
    fi
  else
    # Plain text response (logs, scripts, etc.)
    echo "$out"
  fi
}

# Extract flag value from args
flag() {
  local f="--$1"; shift
  while [[ $# -gt 0 ]]; do [[ "$1" == "$f" && $# -gt 1 ]] && echo "$2" && return; shift; done
}

# Build query string
qs() { [[ -n "${2:-}" ]] && echo "?$1=$2"; }

# Build JSON body from key=value pairs
jb() {
  local args=()
  for kv in "$@"; do
    local k="${kv%%=*}" v="${kv#*=}"
    [[ -z "$v" ]] && continue
    case "$k" in
      *:bool) args+=(--argjson "${k%:bool}" "$([[ $v == true ]] && echo true || echo false)") ;;
      *:int)  args+=(--argjson "${k%:int}" "$v") ;;
      *:arr)  args+=(--argjson "${k%:arr}" "$v") ;;
      *)      args+=(--arg "$k" "$v") ;;
    esac
  done
  [[ ${#args[@]} -eq 0 ]] && echo '{}' && return
  jq -n "${args[@]}" '$ARGS.named'
}

# Get org from flag or env/config
get_org() {
  # Return empty for help commands (check all args)
  for arg in "$@"; do
    if [[ "$arg" =~ ^(help|--help|-h)$ ]]; then
      echo ""
      return
    fi
  done
  
  local o=$(flag org "$@")
  [[ -n "$o" ]] && echo "$o" && return
  [[ -n "$ORG" ]] && echo "$ORG" && return
  # Auto-detect: fetch first org
  o=$(curl -s -H "Authorization: Bearer $LARAVEL_FORGE_API_TOKEN" -H "Accept: application/json" \
    "${BASE}/orgs" | jq -r '.data[0].attributes.slug // empty' 2>/dev/null)
  if [[ -n "$o" ]]; then
    echo "(auto-detected org: $o)" >&2
    echo "$o"
    return
  fi
  die "Organization required: pass --org ORG_SLUG or set LARAVEL_FORGE_ORG or add 'org' to $CREDS"
}

# ══════════════════════════════════════════════════════════════════════════════
# USER
# ══════════════════════════════════════════════════════════════════════════════

cmd_user() {
  local act=${1:-get}; shift 2>/dev/null || true
  case $act in
    get|me) api GET /user ;;
    *) echo 'user: get | me' ;;
  esac
}

# ══════════════════════════════════════════════════════════════════════════════
# ORGANIZATIONS
# ══════════════════════════════════════════════════════════════════════════════

cmd_organizations() {
  local act=${1:-help}; shift 2>/dev/null || true
  case $act in
    list) api GET /orgs ;;
    get)
      local org=$(get_org "$@")
      api GET "/orgs/$org" ;;
    *) cat <<'EOF'
organizations: list | get [--org ORG]
EOF
  esac
}

# ══════════════════════════════════════════════════════════════════════════════
# PROVIDERS
# ══════════════════════════════════════════════════════════════════════════════

cmd_providers() {
  local act=${1:-help}; shift 2>/dev/null || true
  case $act in
    list) api GET /providers ;;
    get)
      [[ ${1:-} ]] || die "provider required"
      api GET "/providers/$1" ;;
    sizes)
      [[ ${1:-} ]] || die "provider required"
      api GET "/providers/$1/sizes" ;;
    size)
      [[ ${1:-} && ${2:-} ]] || die "provider size-id required"
      api GET "/providers/$1/sizes/$2" ;;
    regions)
      [[ ${1:-} ]] || die "provider required"
      api GET "/providers/$1/regions" ;;
    region)
      [[ ${1:-} && ${2:-} ]] || die "provider region-id required"
      api GET "/providers/$1/regions/$2" ;;
    region-sizes)
      [[ ${1:-} && ${2:-} ]] || die "provider region-id required"
      api GET "/providers/$1/regions/$2/sizes" ;;
    region-size)
      [[ ${1:-} && ${2:-} && ${3:-} ]] || die "provider region-id size-id required"
      api GET "/providers/$1/regions/$2/sizes/$3" ;;
    *) cat <<'EOF'
providers: list | get <provider> | sizes <provider> | size <provider> <size-id>
           regions <provider> | region <provider> <region-id>
           region-sizes <provider> <region-id> | region-size <provider> <region-id> <size-id>
EOF
  esac
}

# ══════════════════════════════════════════════════════════════════════════════
# SERVERS
# ══════════════════════════════════════════════════════════════════════════════

cmd_servers() {
  local act=${1:-help}; shift 2>/dev/null || true
  local org=$(get_org "$@")
  
  case $act in
    list)
      api GET "/orgs/$org/servers" ;;
    
    get)
      [[ ${1:-} ]] || die "server-id required"
      api GET "/orgs/$org/servers/$1" ;;
    
    create)
      local body=$(jb \
        name="$(flag name "$@")" \
        provider="$(flag provider "$@")" \
        credential_id:int="$(flag credential-id "$@")" \
        team_id:int="$(flag team-id "$@")" \
        type="$(flag type "$@")" \
        ubuntu_version="$(flag ubuntu-version "$@")" \
        php_version="$(flag php-version "$@")" \
        database_type="$(flag database-type "$@")" \
        recipe_id:int="$(flag recipe-id "$@")" \
        tags:arr="$(flag tags "$@")")
      api POST "/orgs/$org/servers" "$body" ;;
    
    delete)
      [[ ${1:-} ]] || die "server-id required"
      api DELETE "/orgs/$org/servers/$1" ;;
    
    action)
      [[ ${1:-} ]] || die "server-id required"; local sid=$1; shift
      local a=$(flag action "$@"); [[ $a ]] || die "--action required (reboot|revoke)"
      api POST "/orgs/$org/servers/$sid/actions" "$(jb action="$a")" ;;
    
    archives)
      api GET "/orgs/$org/servers/archives" ;;
    
    archive)
      [[ ${1:-} ]] || die "server-id required"
      api POST "/orgs/$org/servers/archives" "$(jb server_id:int="$1")" ;;
    
    unarchive)
      [[ ${1:-} ]] || die "server-id required"
      api DELETE "/orgs/$org/servers/archives/$1" ;;
    
    events)
      [[ ${1:-} ]] || die "server-id required"
      api GET "/orgs/$org/servers/$1/events" ;;
    
    event)
      [[ ${1:-} && ${2:-} ]] || die "server-id event-id required"
      api GET "/orgs/$org/servers/$1/events/$2" ;;
    
    event-output)
      [[ ${1:-} && ${2:-} ]] || die "server-id event-id required"
      api GET "/orgs/$org/servers/$1/events/$2/output" ;;
    
    key)
      [[ ${1:-} ]] || die "server-id required"
      api GET "/orgs/$org/servers/$1/key" ;;
    
    update-key)
      [[ ${1:-} ]] || die "server-id required"; local sid=$1; shift
      local k=$(flag key "$@"); [[ $k ]] || die "--key required"
      api PUT "/orgs/$org/servers/$sid/key" "$(jb key="$k")" ;;
    
    *) cat <<'EOF'
servers: list [--org ORG] | get <id> [--org ORG] | delete <id> [--org ORG]
         create --name N --provider P --credential-id ID --type T --ubuntu-version V [--php-version V] [--database-type mysql|postgres] [--org ORG]
         action <id> --action reboot|revoke [--org ORG]
         archives [--org ORG] | archive <id> [--org ORG] | unarchive <id> [--org ORG]
         events <id> [--org ORG] | event <id> <event-id> [--org ORG] | event-output <id> <event-id> [--org ORG]
         key <id> [--org ORG] | update-key <id> --key KEY [--org ORG]
EOF
  esac
}

# ══════════════════════════════════════════════════════════════════════════════
# SERVICES (nginx, mysql, postgres, redis, php, supervisor)
# ══════════════════════════════════════════════════════════════════════════════

cmd_services() {
  local act=${1:-help}; shift 2>/dev/null || true
  local org=$(get_org "$@")
  
  case $act in
    nginx|mysql|postgres|redis|supervisor)
      [[ ${1:-} ]] || die "server-id required"; local sid=$1; shift
      local a=$(flag action "$@"); [[ $a ]] || die "--action required"
      api POST "/orgs/$org/servers/$sid/services/$act/actions" "$(jb action="$a")" ;;
    
    php)
      [[ ${1:-} ]] || die "server-id required"; local sid=$1; shift
      local a=$(flag action "$@") v=$(flag version "$@")
      [[ $a ]] || die "--action required"
      api POST "/orgs/$org/servers/$sid/services/php/actions" "$(jb action="$a" version="$v")" ;;
    
    *) cat <<'EOF'
services: nginx <server-id> --action start|stop|restart [--org ORG]
          mysql <server-id> --action start|stop|restart [--org ORG]
          postgres <server-id> --action start|stop|restart [--org ORG]
          redis <server-id> --action start|stop|restart [--org ORG]
          supervisor <server-id> --action start|stop|restart [--org ORG]
          php <server-id> --action start|stop|restart [--version phpXX] [--org ORG]
EOF
  esac
}

# ══════════════════════════════════════════════════════════════════════════════
# PHP MANAGEMENT
# ══════════════════════════════════════════════════════════════════════════════

cmd_php() {
  local act=${1:-help}; shift 2>/dev/null || true
  
  # Show help without requiring server-id
  if [[ $act == "help" || $act == "--help" ]]; then
    cat <<'EOF'
php: cli-version <srv> | update-cli-version <srv> --php-version V
     site-version <srv> | update-site-version <srv> --php-version V
     versions <srv> | version <srv> <php-version> | install <srv> --version V [--cli-default true] [--site-default true]
     update-version <srv> <php-version> [--cli-default true] [--site-default true] | uninstall <srv> <php-version>
     fpm-config <srv> <php-version> | update-fpm-config <srv> <php-version> --config CONFIG
     cli-config <srv> <php-version> | update-cli-config <srv> <php-version> --config CONFIG
     pool-config <srv> <php-version> | update-pool-config <srv> <php-version> --config CONFIG [--user USER]
     max-upload-size <srv> | update-max-upload-size <srv> --size SIZE
     max-execution-time <srv> | update-max-execution-time <srv> --time TIME
     opcache <srv> | enable-opcache <srv> | disable-opcache <srv>
     [--org ORG for all commands]
EOF
    return
  fi
  
  local org=$(get_org "$@")
  [[ ${1:-} ]] || die "server-id required"; local sid=$1; shift 2>/dev/null || true
  
  case $act in
    cli-version)
      api GET "/orgs/$org/servers/$sid/php/cli-version" ;;
    
    update-cli-version)
      local v=$(flag php-version "$@"); [[ $v ]] || die "--php-version required"
      api PUT "/orgs/$org/servers/$sid/php/cli-version" "$(jb php_version="$v")" ;;
    
    site-version)
      api GET "/orgs/$org/servers/$sid/php/site-version" ;;
    
    update-site-version)
      local v=$(flag php-version "$@"); [[ $v ]] || die "--php-version required"
      api PUT "/orgs/$org/servers/$sid/php/site-version" "$(jb php_version="$v")" ;;
    
    versions)
      api GET "/orgs/$org/servers/$sid/php/versions" ;;
    
    version)
      [[ ${1:-} ]] || die "php-version required"
      api GET "/orgs/$org/servers/$sid/php/versions/$1" ;;
    
    install)
      local v=$(flag version "$@"); [[ $v ]] || die "--version required"
      api POST "/orgs/$org/servers/$sid/php/versions" "$(jb \
        version="$v" \
        cli_default:bool="$(flag cli-default "$@")" \
        site_default:bool="$(flag site-default "$@")")" ;;
    
    update-version)
      [[ ${1:-} ]] || die "php-version required"; local pv=$1; shift
      api PUT "/orgs/$org/servers/$sid/php/versions/$pv" "$(jb \
        cli_default:bool="$(flag cli-default "$@")" \
        site_default:bool="$(flag site-default "$@")")" ;;
    
    uninstall)
      [[ ${1:-} ]] || die "php-version required"
      api DELETE "/orgs/$org/servers/$sid/php/versions/$1" ;;
    
    fpm-config)
      [[ ${1:-} ]] || die "php-version required"
      api GET "/orgs/$org/servers/$sid/php/versions/$1/configs/fpm" ;;
    
    update-fpm-config)
      [[ ${1:-} ]] || die "php-version required"; local pv=$1; shift
      local cfg=$(flag config "$@"); [[ $cfg ]] || die "--config required"
      api PUT "/orgs/$org/servers/$sid/php/versions/$pv/configs/fpm" "$(jb config="$cfg")" ;;
    
    cli-config)
      [[ ${1:-} ]] || die "php-version required"
      api GET "/orgs/$org/servers/$sid/php/versions/$1/configs/cli" ;;
    
    update-cli-config)
      [[ ${1:-} ]] || die "php-version required"; local pv=$1; shift
      local cfg=$(flag config "$@"); [[ $cfg ]] || die "--config required"
      api PUT "/orgs/$org/servers/$sid/php/versions/$pv/configs/cli" "$(jb config="$cfg")" ;;
    
    pool-config)
      [[ ${1:-} ]] || die "php-version required"
      api GET "/orgs/$org/servers/$sid/php/versions/$1/configs/pool" ;;
    
    update-pool-config)
      [[ ${1:-} ]] || die "php-version required"; local pv=$1; shift
      local cfg=$(flag config "$@") u=$(flag user "$@")
      [[ $cfg ]] || die "--config required"
      api PUT "/orgs/$org/servers/$sid/php/versions/$pv/configs/pool" "$(jb config="$cfg" user="$u")" ;;
    
    max-upload-size)
      api GET "/orgs/$org/servers/$sid/php/max-upload-size" ;;
    
    update-max-upload-size)
      local s=$(flag size "$@"); [[ $s ]] || die "--size required"
      api PUT "/orgs/$org/servers/$sid/php/max-upload-size" "$(jb max_upload_size:int="$s")" ;;
    
    max-execution-time)
      api GET "/orgs/$org/servers/$sid/php/max-execution-time" ;;
    
    update-max-execution-time)
      local t=$(flag time "$@"); [[ $t ]] || die "--time required"
      api PUT "/orgs/$org/servers/$sid/php/max-execution-time" "$(jb max_execution_time:int="$t")" ;;
    
    opcache)
      api GET "/orgs/$org/servers/$sid/php/opcache" ;;
    
    enable-opcache)
      api POST "/orgs/$org/servers/$sid/php/opcache" ;;
    
    disable-opcache)
      api DELETE "/orgs/$org/servers/$sid/php/opcache" ;;
    
    *) cat <<'EOF'
php: cli-version <srv> | update-cli-version <srv> --php-version V
     site-version <srv> | update-site-version <srv> --php-version V
     versions <srv> | version <srv> <php-version> | install <srv> --version V [--cli-default true] [--site-default true]
     update-version <srv> <php-version> [--cli-default true] [--site-default true] | uninstall <srv> <php-version>
     fpm-config <srv> <php-version> | update-fpm-config <srv> <php-version> --config CONFIG
     cli-config <srv> <php-version> | update-cli-config <srv> <php-version> --config CONFIG
     pool-config <srv> <php-version> | update-pool-config <srv> <php-version> --config CONFIG [--user USER]
     max-upload-size <srv> | update-max-upload-size <srv> --size SIZE
     max-execution-time <srv> | update-max-execution-time <srv> --time TIME
     opcache <srv> | enable-opcache <srv> | disable-opcache <srv>
     [--org ORG for all commands]
EOF
  esac
}

# ══════════════════════════════════════════════════════════════════════════════
# BACKGROUND PROCESSES
# ══════════════════════════════════════════════════════════════════════════════

cmd_background_processes() {
  local act=${1:-help}; shift 2>/dev/null || true
  
  if [[ $act == "help" || $act == "--help" ]]; then
    cat <<'EOF'
background-processes: list <srv> | get <srv> <id> | log <srv> <id>
                      create <srv> --name N --command C --user U [--directory D] [--processes N]
                      update <srv> <id> --name N [--config CONFIG]
                      delete <srv> <id> | action <srv> <id> --action restart
                      [--org ORG for all commands]
EOF
    return
  fi
  
  local org=$(get_org "$@")
  [[ ${1:-} ]] || die "server-id required"; local sid=$1; shift 2>/dev/null || true
  
  case $act in
    list)
      api GET "/orgs/$org/servers/$sid/background-processes" ;;
    
    get)
      [[ ${1:-} ]] || die "process-id required"
      api GET "/orgs/$org/servers/$sid/background-processes/$1" ;;
    
    create)
      local body=$(jb \
        name="$(flag name "$@")" \
        command="$(flag command "$@")" \
        user="$(flag user "$@")" \
        directory="$(flag directory "$@")" \
        processes:int="$(flag processes "$@")" \
        startsecs:int="$(flag startsecs "$@")" \
        stopwaitsecs:int="$(flag stopwaitsecs "$@")" \
        stopsignal="$(flag stopsignal "$@")")
      api POST "/orgs/$org/servers/$sid/background-processes" "$body" ;;
    
    update)
      [[ ${1:-} ]] || die "process-id required"; local pid=$1; shift
      local body=$(jb \
        name="$(flag name "$@")" \
        config="$(flag config "$@")")
      api PUT "/orgs/$org/servers/$sid/background-processes/$pid" "$body" ;;
    
    delete)
      [[ ${1:-} ]] || die "process-id required"
      api DELETE "/orgs/$org/servers/$sid/background-processes/$1" ;;
    
    log)
      [[ ${1:-} ]] || die "process-id required"
      api GET "/orgs/$org/servers/$sid/background-processes/$1/log" ;;
    
    action)
      [[ ${1:-} ]] || die "process-id required"; local pid=$1; shift
      local a=$(flag action "$@"); [[ $a ]] || die "--action restart required"
      api POST "/orgs/$org/servers/$sid/background-processes/$pid/actions" "$(jb action="$a")" ;;
    
    *) cat <<'EOF'
background-processes: list <srv> | get <srv> <id> | log <srv> <id>
                      create <srv> --name N --command C --user U [--directory D] [--processes N]
                      update <srv> <id> --name N [--config CONFIG]
                      delete <srv> <id> | action <srv> <id> --action restart
                      [--org ORG for all commands]
EOF
  esac
}

# ══════════════════════════════════════════════════════════════════════════════
# FIREWALL RULES
# ══════════════════════════════════════════════════════════════════════════════

cmd_firewall() {
  local act=${1:-help}; shift 2>/dev/null || true
  local org=$(get_org "$@")
  [[ ${1:-} ]] || die "server-id required"; local sid=$1; shift 2>/dev/null || true
  
  case $act in
    list)
      api GET "/orgs/$org/servers/$sid/firewall-rules" ;;
    
    get)
      [[ ${1:-} ]] || die "rule-id required"
      api GET "/orgs/$org/servers/$sid/firewall-rules/$1" ;;
    
    create)
      local body=$(jb \
        name="$(flag name "$@")" \
        port:int="$(flag port "$@")" \
        type="$(flag type "$@")" \
        ip_address="$(flag ip "$@")")
      api POST "/orgs/$org/servers/$sid/firewall-rules" "$body" ;;
    
    delete)
      [[ ${1:-} ]] || die "rule-id required"
      api DELETE "/orgs/$org/servers/$sid/firewall-rules/$1" ;;
    
    *) cat <<'EOF'
firewall: list <srv> | get <srv> <rule-id> | delete <srv> <rule-id>
          create <srv> --name N --type allow|deny [--port N] [--ip IP]
          [--org ORG for all commands]
EOF
  esac
}

# ══════════════════════════════════════════════════════════════════════════════
# SCHEDULED JOBS
# ══════════════════════════════════════════════════════════════════════════════

cmd_jobs() {
  local act=${1:-help}; shift 2>/dev/null || true
  local org=$(get_org "$@")
  
  # Check if this is server-scoped or site-scoped
  if [[ ${2:-} ]]; then
    # Site-scoped: jobs <srv> <site> ...
    local sid=$1 siteid=$2; shift 2 2>/dev/null || true
    case $act in
      list)
        api GET "/orgs/$org/servers/$sid/sites/$siteid/scheduled-jobs" ;;
      get)
        [[ ${1:-} ]] || die "job-id required"
        api GET "/orgs/$org/servers/$sid/sites/$siteid/scheduled-jobs/$1" ;;
      create)
        local body=$(jb \
          name="$(flag name "$@")" \
          command="$(flag command "$@")" \
          user="$(flag user "$@")" \
          frequency="$(flag frequency "$@")" \
          cron="$(flag cron "$@")" \
          heartbeat:int="$(flag heartbeat "$@")" \
          grace_period:int="$(flag grace-period "$@")")
        api POST "/orgs/$org/servers/$sid/sites/$siteid/scheduled-jobs" "$body" ;;
      delete)
        [[ ${1:-} ]] || die "job-id required"
        api DELETE "/orgs/$org/servers/$sid/sites/$siteid/scheduled-jobs/$1" ;;
      output)
        [[ ${1:-} ]] || die "job-id required"
        api GET "/orgs/$org/servers/$sid/sites/$siteid/scheduled-jobs/$1/output" ;;
      *) die "Unknown action: $act" ;;
    esac
  else
    # Server-scoped: jobs <srv> ...
    [[ ${1:-} ]] || die "server-id required"; local sid=$1; shift 2>/dev/null || true
    case $act in
      list)
        api GET "/orgs/$org/servers/$sid/scheduled-jobs" ;;
      get)
        [[ ${1:-} ]] || die "job-id required"
        api GET "/orgs/$org/servers/$sid/scheduled-jobs/$1" ;;
      create)
        local body=$(jb \
          name="$(flag name "$@")" \
          command="$(flag command "$@")" \
          user="$(flag user "$@")" \
          frequency="$(flag frequency "$@")" \
          cron="$(flag cron "$@")" \
          heartbeat:int="$(flag heartbeat "$@")" \
          grace_period:int="$(flag grace-period "$@")")
        api POST "/orgs/$org/servers/$sid/scheduled-jobs" "$body" ;;
      delete)
        [[ ${1:-} ]] || die "job-id required"
        api DELETE "/orgs/$org/servers/$sid/scheduled-jobs/$1" ;;
      output)
        [[ ${1:-} ]] || die "job-id required"
        api GET "/orgs/$org/servers/$sid/scheduled-jobs/$1/output" ;;
      help|--help)
        cat <<'EOF'
jobs: list <srv> | get <srv> <job-id> | output <srv> <job-id> | delete <srv> <job-id>
      create <srv> --command C --user U --frequency F [--cron CRON] [--name N]
      
      # Site-scoped jobs:
      list <srv> <site> | get <srv> <site> <job-id> | output <srv> <site> <job-id>
      create <srv> <site> --command C --user U --frequency F
      delete <srv> <site> <job-id>
      
      [--org ORG for all commands]
EOF
        return ;;
      *) die "Unknown action: $act" ;;
    esac
  fi
}

# ══════════════════════════════════════════════════════════════════════════════
# SSH KEYS
# ══════════════════════════════════════════════════════════════════════════════

cmd_keys() {
  local act=${1:-help}; shift 2>/dev/null || true
  local org=$(get_org "$@")
  [[ ${1:-} ]] || die "server-id required"; local sid=$1; shift 2>/dev/null || true
  
  case $act in
    list)
      api GET "/orgs/$org/servers/$sid/ssh-keys" ;;
    
    get)
      [[ ${1:-} ]] || die "key-id required"
      api GET "/orgs/$org/servers/$sid/ssh-keys/$1" ;;
    
    create)
      local body=$(jb \
        name="$(flag name "$@")" \
        key="$(flag key "$@")" \
        user="$(flag user "$@")")
      api POST "/orgs/$org/servers/$sid/ssh-keys" "$body" ;;
    
    delete)
      [[ ${1:-} ]] || die "key-id required"
      api DELETE "/orgs/$org/servers/$sid/ssh-keys/$1" ;;
    
    *) cat <<'EOF'
keys: list <srv> | get <srv> <key-id> | delete <srv> <key-id>
      create <srv> --name N --key KEY --user USER
      [--org ORG for all commands]
EOF
  esac
}

# ══════════════════════════════════════════════════════════════════════════════
# DATABASES
# ══════════════════════════════════════════════════════════════════════════════

cmd_databases() {
  local act=${1:-help}; shift 2>/dev/null || true
  
  if [[ $act == "help" || $act == "--help" ]]; then
    cat <<'EOF'
databases: list <srv> | get <srv> <db-id> | delete <srv> <db-id>
           create <srv> --name N [--user U --password P]
           sync <srv> | update-password <srv> --password PW
           [--org ORG for all commands]
EOF
    return
  fi
  
  local org=$(get_org "$@")
  [[ ${1:-} ]] || die "server-id required"; local sid=$1; shift 2>/dev/null || true
  
  case $act in
    list)
      api GET "/orgs/$org/servers/$sid/database/schemas" ;;
    
    get)
      [[ ${1:-} ]] || die "database-id required"
      api GET "/orgs/$org/servers/$sid/database/schemas/$1" ;;
    
    create)
      local body=$(jb \
        name="$(flag name "$@")" \
        user="$(flag user "$@")" \
        password="$(flag password "$@")")
      api POST "/orgs/$org/servers/$sid/database/schemas" "$body" ;;
    
    delete)
      [[ ${1:-} ]] || die "database-id required"
      api DELETE "/orgs/$org/servers/$sid/database/schemas/$1" ;;
    
    sync)
      api POST "/orgs/$org/servers/$sid/database/schemas/synchronizations" ;;
    
    update-password)
      local pw=$(flag password "$@"); [[ $pw ]] || die "--password required"
      api PUT "/orgs/$org/servers/$sid/database/password" "$(jb password="$pw")" ;;
    
    *) cat <<'EOF'
databases: list <srv> | get <srv> <db-id> | delete <srv> <db-id>
           create <srv> --name N [--user U --password P]
           sync <srv> | update-password <srv> --password PW
           [--org ORG for all commands]
EOF
  esac
}

# ══════════════════════════════════════════════════════════════════════════════
# DATABASE USERS
# ══════════════════════════════════════════════════════════════════════════════

cmd_db_users() {
  local act=${1:-help}; shift 2>/dev/null || true
  local org=$(get_org "$@")
  [[ ${1:-} ]] || die "server-id required"; local sid=$1; shift 2>/dev/null || true
  
  case $act in
    list)
      api GET "/orgs/$org/servers/$sid/database/users" ;;
    
    get)
      [[ ${1:-} ]] || die "user-id required"
      api GET "/orgs/$org/servers/$sid/database/users/$1" ;;
    
    create)
      local body=$(jb \
        name="$(flag name "$@")" \
        password="$(flag password "$@")" \
        read_only:bool="$(flag read-only "$@")" \
        database_ids:arr="$(flag database-ids "$@")")
      api POST "/orgs/$org/servers/$sid/database/users" "$body" ;;
    
    update)
      [[ ${1:-} ]] || die "user-id required"; local uid=$1; shift
      local body=$(jb \
        password="$(flag password "$@")" \
        database_ids:arr="$(flag database-ids "$@")")
      api PUT "/orgs/$org/servers/$sid/database/users/$uid" "$body" ;;
    
    delete)
      [[ ${1:-} ]] || die "user-id required"
      api DELETE "/orgs/$org/servers/$sid/database/users/$1" ;;
    
    *) cat <<'EOF'
db-users: list <srv> | get <srv> <user-id> | delete <srv> <user-id>
          create <srv> --name N --password P [--read-only true] [--database-ids "[1,2]"]
          update <srv> <user-id> [--password P] [--database-ids "[1,2]"]
          [--org ORG for all commands]
EOF
  esac
}

# ══════════════════════════════════════════════════════════════════════════════
# BACKUPS
# ══════════════════════════════════════════════════════════════════════════════

cmd_backups() {
  local act=${1:-help}; shift 2>/dev/null || true
  
  # Show help without requiring server-id
  if [[ $act == "help" || $act == "--help" ]]; then
    cat <<'EOF'
backups: configs <srv> | config <srv> <config-id> | delete-config <srv> <config-id>
         create-config <srv> --storage-provider-id ID --frequency F --retention N --database-ids "[1,2]"
         update-config <srv> <config-id> [--name N] [--frequency F] [--retention N]
         list <srv> <config-id> | get <srv> <config-id> <backup-id> | delete <srv> <config-id> <backup-id>
         create <srv> <config-id> | restore <srv> <config-id> <backup-id> --database-id ID
         [--org ORG for all commands]
EOF
    return
  fi
  
  local org=$(get_org "$@")
  [[ ${1:-} ]] || die "server-id required"; local sid=$1; shift 2>/dev/null || true
  
  case $act in
    configs)
      api GET "/orgs/$org/servers/$sid/database/backups" ;;
    
    config)
      [[ ${1:-} ]] || die "config-id required"
      api GET "/orgs/$org/servers/$sid/database/backups/$1" ;;
    
    create-config)
      local body=$(jb \
        storage_provider_id:int="$(flag storage-provider-id "$@")" \
        name="$(flag name "$@")" \
        bucket="$(flag bucket "$@")" \
        directory="$(flag directory "$@")" \
        frequency="$(flag frequency "$@")" \
        day="$(flag day "$@")" \
        time="$(flag time "$@")" \
        cron="$(flag cron "$@")" \
        retention:int="$(flag retention "$@")" \
        notification_email="$(flag notification-email "$@")" \
        database_ids:arr="$(flag database-ids "$@")")
      api POST "/orgs/$org/servers/$sid/database/backups" "$body" ;;
    
    update-config)
      [[ ${1:-} ]] || die "config-id required"; local cid=$1; shift
      local body=$(jb \
        storage_provider_id:int="$(flag storage-provider-id "$@")" \
        name="$(flag name "$@")" \
        bucket="$(flag bucket "$@")" \
        directory="$(flag directory "$@")" \
        frequency="$(flag frequency "$@")" \
        day="$(flag day "$@")" \
        time="$(flag time "$@")" \
        cron="$(flag cron "$@")" \
        retention:int="$(flag retention "$@")" \
        notification_email="$(flag notification-email "$@")" \
        database_ids:arr="$(flag database-ids "$@")")
      api PUT "/orgs/$org/servers/$sid/database/backups/$cid" "$body" ;;
    
    delete-config)
      [[ ${1:-} ]] || die "config-id required"
      api DELETE "/orgs/$org/servers/$sid/database/backups/$1" ;;
    
    list)
      [[ ${1:-} ]] || die "config-id required"
      api GET "/orgs/$org/servers/$sid/database/backups/$1/instances" ;;
    
    get)
      [[ ${1:-} && ${2:-} ]] || die "config-id backup-id required"
      api GET "/orgs/$org/servers/$sid/database/backups/$1/instances/$2" ;;
    
    create)
      [[ ${1:-} ]] || die "config-id required"
      api POST "/orgs/$org/servers/$sid/database/backups/$1/instances" ;;
    
    delete)
      [[ ${1:-} && ${2:-} ]] || die "config-id backup-id required"
      api DELETE "/orgs/$org/servers/$sid/database/backups/$1/instances/$2" ;;
    
    restore)
      [[ ${1:-} && ${2:-} ]] || die "config-id backup-id required"; local cid=$1 bid=$2; shift 2
      local dbid=$(flag database-id "$@"); [[ $dbid ]] || die "--database-id required"
      api POST "/orgs/$org/servers/$sid/database/backups/$cid/instances/$bid/restores" "$(jb database_id:int="$dbid")" ;;
    
    *) cat <<'EOF'
backups: configs <srv> | config <srv> <config-id> | delete-config <srv> <config-id>
         create-config <srv> --storage-provider-id ID --frequency F --retention N --database-ids "[1,2]"
         update-config <srv> <config-id> [--name N] [--frequency F] [--retention N]
         list <srv> <config-id> | get <srv> <config-id> <backup-id> | delete <srv> <config-id> <backup-id>
         create <srv> <config-id> | restore <srv> <config-id> <backup-id> --database-id ID
         [--org ORG for all commands]
EOF
  esac
}

# ══════════════════════════════════════════════════════════════════════════════
# MONITORS
# ══════════════════════════════════════════════════════════════════════════════

cmd_monitors() {
  local act=${1:-help}; shift 2>/dev/null || true
  local org=$(get_org "$@")
  [[ ${1:-} ]] || die "server-id required"; local sid=$1; shift 2>/dev/null || true
  
  case $act in
    list)
      api GET "/orgs/$org/servers/$sid/monitors" ;;
    
    get)
      [[ ${1:-} ]] || die "monitor-id required"
      api GET "/orgs/$org/servers/$sid/monitors/$1" ;;
    
    create)
      local body=$(jb \
        type="$(flag type "$@")" \
        operator="$(flag operator "$@")" \
        threshold:int="$(flag threshold "$@")" \
        minutes:int="$(flag minutes "$@")" \
        notify:bool="$(flag notify "$@")")
      api POST "/orgs/$org/servers/$sid/monitors" "$body" ;;
    
    delete)
      [[ ${1:-} ]] || die "monitor-id required"
      api DELETE "/orgs/$org/servers/$sid/monitors/$1" ;;
    
    *) cat <<'EOF'
monitors: list <srv> | get <srv> <id> | delete <srv> <id>
          create <srv> --type cpu|memory|disk --operator gt|lt|gte|lte --threshold N --notify true
          [--org ORG for all commands]
EOF
  esac
}

# ══════════════════════════════════════════════════════════════════════════════
# NGINX TEMPLATES
# ══════════════════════════════════════════════════════════════════════════════

cmd_nginx_templates() {
  local act=${1:-help}; shift 2>/dev/null || true
  local org=$(get_org "$@")
  [[ ${1:-} ]] || die "server-id required"; local sid=$1; shift 2>/dev/null || true
  
  case $act in
    list)
      api GET "/orgs/$org/servers/$sid/nginx/templates" ;;
    
    get)
      [[ ${1:-} ]] || die "template-id required"
      api GET "/orgs/$org/servers/$sid/nginx/templates/$1" ;;
    
    create)
      local body=$(jb \
        name="$(flag name "$@")" \
        content="$(flag content "$@")")
      api POST "/orgs/$org/servers/$sid/nginx/templates" "$body" ;;
    
    update)
      [[ ${1:-} ]] || die "template-id required"; local tid=$1; shift
      local body=$(jb \
        name="$(flag name "$@")" \
        content="$(flag content "$@")")
      api PUT "/orgs/$org/servers/$sid/nginx/templates/$tid" "$body" ;;
    
    delete)
      [[ ${1:-} ]] || die "template-id required"
      api DELETE "/orgs/$org/servers/$sid/nginx/templates/$1" ;;
    
    *) cat <<'EOF'
nginx-templates: list <srv> | get <srv> <id> | delete <srv> <id>
                 create <srv> --name N --content CONTENT
                 update <srv> <id> --name N --content CONTENT
                 [--org ORG for all commands]
EOF
  esac
}

# ══════════════════════════════════════════════════════════════════════════════
# LOGS
# ══════════════════════════════════════════════════════════════════════════════

cmd_logs() {
  local act=${1:-help}; shift 2>/dev/null || true
  local org=$(get_org "$@")
  [[ ${1:-} ]] || die "server-id required"; local sid=$1; shift 2>/dev/null || true
  
  case $act in
    get)
      [[ ${1:-} ]] || die "log-key required (e.g., nginx_error, mysql_error)"
      api GET "/orgs/$org/servers/$sid/logs/$1" ;;
    
    delete)
      [[ ${1:-} ]] || die "log-key required"
      api DELETE "/orgs/$org/servers/$sid/logs/$1" ;;
    
    *) cat <<'EOF'
logs: get <srv> <key> | delete <srv> <key>
      Common keys: nginx_error, nginx_access, mysql_error, postgres_error, redis_error
      [--org ORG for all commands]
EOF
  esac
}

# ══════════════════════════════════════════════════════════════════════════════
# SITES
# ══════════════════════════════════════════════════════════════════════════════

cmd_sites() {
  local act=${1:-help}; shift 2>/dev/null || true
  local org=$(get_org "$@")
  
  case $act in
    list-all)
      # Cross-org list
      api GET /sites ;;
    
    list)
      if [[ ${1:-} ]]; then
        # Server-scoped list
        api GET "/orgs/$org/servers/$1/sites"
      else
        # Org-scoped list
        api GET "/orgs/$org/sites"
      fi ;;
    
    get)
      [[ ${1:-} ]] || die "site-id required"
      api GET "/orgs/$org/sites/$1" ;;
    
    create)
      [[ ${1:-} ]] || die "server-id required"; local sid=$1; shift
      local body=$(jb \
        type="$(flag type "$@")" \
        domain_mode="$(flag domain-mode "$@")" \
        name="$(flag name "$@")" \
        www_redirect_type="$(flag www-redirect "$@")" \
        allow_wildcard_subdomains:bool="$(flag allow-wildcards "$@")" \
        root_directory="$(flag root-directory "$@")" \
        web_directory="$(flag web-directory "$@")" \
        is_isolated:bool="$(flag isolated "$@")" \
        isolated_user="$(flag isolated-user "$@")" \
        php_version="$(flag php-version "$@")" \
        zero_downtime_deployments:bool="$(flag zero-downtime "$@")" \
        nginx_template_id:int="$(flag nginx-template-id "$@")" \
        source_control_provider="$(flag source-control-provider "$@")" \
        repository="$(flag repository "$@")" \
        branch="$(flag branch "$@")" \
        database_id:int="$(flag database-id "$@")" \
        database_user_id:int="$(flag database-user-id "$@")" \
        push_to_deploy:bool="$(flag push-to-deploy "$@")" \
        tags:arr="$(flag tags "$@")")
      api POST "/orgs/$org/servers/$sid/sites" "$body" ;;
    
    update)
      [[ ${1:-} && ${2:-} ]] || die "server-id site-id required"; local sid=$1 siteid=$2; shift 2
      local body=$(jb \
        root_path="$(flag root-path "$@")" \
        directory="$(flag directory "$@")" \
        type="$(flag type "$@")" \
        php_version="$(flag php-version "$@")" \
        push_to_deploy:bool="$(flag push-to-deploy "$@")" \
        repository_branch="$(flag branch "$@")")
      api PUT "/orgs/$org/servers/$sid/sites/$siteid" "$body" ;;
    
    delete)
      [[ ${1:-} && ${2:-} ]] || die "server-id site-id required"
      api DELETE "/orgs/$org/servers/$1/sites/$2" ;;
    
    healthcheck)
      [[ ${1:-} && ${2:-} ]] || die "server-id site-id required"
      api GET "/orgs/$org/servers/$1/sites/$2/healthcheck" ;;
    
    update-healthcheck)
      [[ ${1:-} && ${2:-} ]] || die "server-id site-id required"; local sid=$1 siteid=$2; shift 2
      local h=$(flag healthcheck-endpoint "$@")
      api PUT "/orgs/$org/servers/$sid/sites/$siteid/healthcheck" "$(jb healthcheck_endpoint="$h")" ;;
    
    env)
      [[ ${1:-} && ${2:-} ]] || die "server-id site-id required"
      api GET "/orgs/$org/servers/$1/sites/$2/environment" ;;
    
    update-env)
      [[ ${1:-} && ${2:-} ]] || die "server-id site-id required"; local sid=$1 siteid=$2; shift 2
      local body=$(jb \
        environment="$(flag environment "$@")" \
        cache:bool="$(flag cache "$@")" \
        queues:bool="$(flag queues "$@")" \
        encryption_key="$(flag encryption-key "$@")")
      api PUT "/orgs/$org/servers/$sid/sites/$siteid/environment" "$body" ;;
    
    nginx)
      [[ ${1:-} && ${2:-} ]] || die "server-id site-id required"
      api GET "/orgs/$org/servers/$1/sites/$2/nginx" ;;
    
    update-nginx)
      [[ ${1:-} && ${2:-} ]] || die "server-id site-id required"; local sid=$1 siteid=$2; shift 2
      local cfg=$(flag config "$@"); [[ $cfg ]] || die "--config required"
      api PUT "/orgs/$org/servers/$sid/sites/$siteid/nginx" "$(jb config="$cfg")" ;;
    
    balancing)
      [[ ${1:-} && ${2:-} ]] || die "server-id site-id required"
      api GET "/orgs/$org/servers/$1/sites/$2/load-balancing-nodes" ;;
    
    update-balancing)
      [[ ${1:-} && ${2:-} ]] || die "server-id site-id required"; local sid=$1 siteid=$2; shift 2
      local body=$(jb \
        balancer_method="$(flag balancer-method "$@")" \
        balancing:arr="$(flag balancing "$@")")
      api PUT "/orgs/$org/servers/$sid/sites/$siteid/load-balancing-nodes" "$body" ;;
    
    log-nginx-access)
      [[ ${1:-} && ${2:-} ]] || die "server-id site-id required"
      api GET "/orgs/$org/servers/$1/sites/$2/logs/nginx-access" ;;
    
    delete-log-nginx-access)
      [[ ${1:-} && ${2:-} ]] || die "server-id site-id required"
      api DELETE "/orgs/$org/servers/$1/sites/$2/logs/nginx-access" ;;
    
    log-nginx-error)
      [[ ${1:-} && ${2:-} ]] || die "server-id site-id required"
      api GET "/orgs/$org/servers/$1/sites/$2/logs/nginx-error" ;;
    
    delete-log-nginx-error)
      [[ ${1:-} && ${2:-} ]] || die "server-id site-id required"
      api DELETE "/orgs/$org/servers/$1/sites/$2/logs/nginx-error" ;;
    
    log-application)
      [[ ${1:-} && ${2:-} ]] || die "server-id site-id required"
      api GET "/orgs/$org/servers/$1/sites/$2/logs/application" ;;
    
    delete-log-application)
      [[ ${1:-} && ${2:-} ]] || die "server-id site-id required"
      api DELETE "/orgs/$org/servers/$1/sites/$2/logs/application" ;;
    
    *) cat <<'EOF'
sites: list-all | list [<srv>] | get <site-id> | delete <srv> <site>
       create <srv> --type php|html --domain-mode single|multi --name DOMAIN [--www-redirect none|both|to-www|to-non-www]
              [--php-version V] [--isolated true] [--repository REPO --branch BRANCH]
       update <srv> <site> [--root-path P] [--directory D] [--php-version V]
       healthcheck <srv> <site> | update-healthcheck <srv> <site> --healthcheck-endpoint /health
       env <srv> <site> | update-env <srv> <site> --environment "APP_ENV=..." [--cache true] [--queues true]
       nginx <srv> <site> | update-nginx <srv> <site> --config "..."
       balancing <srv> <site> | update-balancing <srv> <site> --balancer-method roundrobin --balancing "[...]"
       log-nginx-access <srv> <site> | delete-log-nginx-access <srv> <site>
       log-nginx-error <srv> <site> | delete-log-nginx-error <srv> <site>
       log-application <srv> <site> | delete-log-application <srv> <site>
       [--org ORG for all commands]
EOF
  esac
}

# ══════════════════════════════════════════════════════════════════════════════
# DOMAINS (per-site)
# ══════════════════════════════════════════════════════════════════════════════

cmd_domains() {
  local act=${1:-help}; shift 2>/dev/null || true
  
  # Show help without requiring server-id/site-id
  if [[ $act == "help" || $act == "--help" ]]; then
    cat <<'EOF'
domains: list <srv> <site> | get <srv> <site> <domain-id> | delete <srv> <site> <domain-id>
         create <srv> <site> --name example.com [--allow-wildcards true] [--www-redirect none|to-www|to-non-www]
         update <srv> <site> <domain-id> --www-redirect none|to-www|to-non-www
         dns-config <srv> <site> <domain-id> | action <srv> <site> <domain-id> --action verify
         nginx <srv> <site> <domain-id> | update-nginx <srv> <site> <domain-id> --config "..."
         cert <srv> <site> <domain-id> | create-cert <srv> <site> <domain-id> --type letsencrypt [--letsencrypt true]
         delete-cert <srv> <site> <domain-id> | cert-action <srv> <site> <domain-id> --action activate
         [--org ORG for all commands]
EOF
    return
  fi
  
  local org=$(get_org "$@")
  [[ ${1:-} && ${2:-} ]] || die "server-id site-id required"; local sid=$1 siteid=$2; shift 2 2>/dev/null || true
  
  case $act in
    list)
      api GET "/orgs/$org/servers/$sid/sites/$siteid/domains" ;;
    
    get)
      [[ ${1:-} ]] || die "domain-id required"
      api GET "/orgs/$org/servers/$sid/sites/$siteid/domains/$1" ;;
    
    create)
      local body=$(jb \
        name="$(flag name "$@")" \
        allow_wildcard_subdomains:bool="$(flag allow-wildcards "$@")" \
        www_redirect_type="$(flag www-redirect "$@")")
      api POST "/orgs/$org/servers/$sid/sites/$siteid/domains" "$body" ;;
    
    update)
      [[ ${1:-} ]] || die "domain-id required"; local did=$1; shift
      local body=$(jb \
        www_redirect_type="$(flag www-redirect "$@")" \
        allow_wildcard_subdomains:bool="$(flag allow-wildcards "$@")")
      api PATCH "/orgs/$org/servers/$sid/sites/$siteid/domains/$did" "$body" ;;
    
    delete)
      [[ ${1:-} ]] || die "domain-id required"
      api DELETE "/orgs/$org/servers/$sid/sites/$siteid/domains/$1" ;;
    
    dns-config)
      [[ ${1:-} ]] || die "domain-id required"
      api GET "/orgs/$org/servers/$sid/sites/$siteid/domains/$1/configurations" ;;
    
    action)
      [[ ${1:-} ]] || die "domain-id required"; local did=$1; shift
      local a=$(flag action "$@"); [[ $a ]] || die "--action required"
      api POST "/orgs/$org/servers/$sid/sites/$siteid/domains/$did/actions" "$(jb action="$a")" ;;
    
    nginx)
      [[ ${1:-} ]] || die "domain-id required"
      api GET "/orgs/$org/servers/$sid/sites/$siteid/domains/$1/nginx" ;;
    
    update-nginx)
      [[ ${1:-} ]] || die "domain-id required"; local did=$1; shift
      local cfg=$(flag config "$@"); [[ $cfg ]] || die "--config required"
      api PUT "/orgs/$org/servers/$sid/sites/$siteid/domains/$did/nginx" "$(jb config="$cfg")" ;;
    
    cert)
      [[ ${1:-} ]] || die "domain-id required"
      api GET "/orgs/$org/servers/$sid/sites/$siteid/domains/$1/certificate" ;;
    
    create-cert)
      [[ ${1:-} ]] || die "domain-id required"; local did=$1; shift
      local body=$(jb \
        type="$(flag type "$@")" \
        letsencrypt:bool="$(flag letsencrypt "$@")" \
        existing="$(flag existing "$@")" \
        csr="$(flag csr "$@")" \
        clone:int="$(flag clone "$@")")
      api POST "/orgs/$org/servers/$sid/sites/$siteid/domains/$did/certificate" "$body" ;;
    
    delete-cert)
      [[ ${1:-} ]] || die "domain-id required"
      api DELETE "/orgs/$org/servers/$sid/sites/$siteid/domains/$1/certificate" ;;
    
    cert-action)
      [[ ${1:-} ]] || die "domain-id required"; local did=$1; shift
      local a=$(flag action "$@"); [[ $a ]] || die "--action activate required"
      api POST "/orgs/$org/servers/$sid/sites/$siteid/domains/$did/certificate/actions" "$(jb action="$a")" ;;
    
    *) cat <<'EOF'
domains: list <srv> <site> | get <srv> <site> <domain-id> | delete <srv> <site> <domain-id>
         create <srv> <site> --name example.com [--allow-wildcards true] [--www-redirect none|to-www|to-non-www]
         update <srv> <site> <domain-id> --www-redirect none|to-www|to-non-www
         dns-config <srv> <site> <domain-id> | action <srv> <site> <domain-id> --action verify
         nginx <srv> <site> <domain-id> | update-nginx <srv> <site> <domain-id> --config "..."
         cert <srv> <site> <domain-id> | create-cert <srv> <site> <domain-id> --type letsencrypt [--letsencrypt true]
         delete-cert <srv> <site> <domain-id> | cert-action <srv> <site> <domain-id> --action activate
         [--org ORG for all commands]
EOF
  esac
}

# ══════════════════════════════════════════════════════════════════════════════
# COMPOSER CREDENTIALS (per-site)
# ══════════════════════════════════════════════════════════════════════════════

cmd_composer_credentials() {
  local act=${1:-help}; shift 2>/dev/null || true
  local org=$(get_org "$@")
  [[ ${1:-} && ${2:-} ]] || die "server-id site-id required"; local sid=$1 siteid=$2; shift 2 2>/dev/null || true
  
  case $act in
    list)
      api GET "/orgs/$org/servers/$sid/sites/$siteid/composer/credentials" ;;
    
    get)
      [[ ${1:-} ]] || die "repository required"
      api GET "/orgs/$org/servers/$sid/sites/$siteid/composer/credentials/$1" ;;
    
    create)
      local body=$(jb \
        repository="$(flag repository "$@")" \
        username="$(flag username "$@")" \
        password="$(flag password "$@")")
      api POST "/orgs/$org/servers/$sid/sites/$siteid/composer/credentials" "$body" ;;
    
    update)
      [[ ${1:-} ]] || die "repository required"; local repo=$1; shift
      local body=$(jb \
        repository="$repo" \
        username="$(flag username "$@")" \
        password="$(flag password "$@")")
      api PUT "/orgs/$org/servers/$sid/sites/$siteid/composer/credentials/$repo" "$body" ;;
    
    delete)
      [[ ${1:-} ]] || die "repository required"
      api DELETE "/orgs/$org/servers/$sid/sites/$siteid/composer/credentials/$1" ;;
    
    *) cat <<'EOF'
composer-credentials: list <srv> <site> | get <srv> <site> <repository>
                      create <srv> <site> --repository REPO --username U --password P
                      update <srv> <site> <repository> --username U --password P
                      delete <srv> <site> <repository>
                      [--org ORG for all commands]
EOF
  esac
}

# ══════════════════════════════════════════════════════════════════════════════
# NPM CREDENTIALS (per-site)
# ══════════════════════════════════════════════════════════════════════════════

cmd_npm_credentials() {
  local act=${1:-help}; shift 2>/dev/null || true
  local org=$(get_org "$@")
  [[ ${1:-} && ${2:-} ]] || die "server-id site-id required"; local sid=$1 siteid=$2; shift 2 2>/dev/null || true
  
  case $act in
    list)
      api GET "/orgs/$org/servers/$sid/sites/$siteid/npm/credentials" ;;
    
    get)
      [[ ${1:-} ]] || die "registry required"
      api GET "/orgs/$org/servers/$sid/sites/$siteid/npm/credentials/$1" ;;
    
    create)
      local body=$(jb \
        registry="$(flag registry "$@")" \
        token="$(flag token "$@")" \
        scopes="$(flag scopes "$@")")
      api POST "/orgs/$org/servers/$sid/sites/$siteid/npm/credentials" "$body" ;;
    
    update)
      [[ ${1:-} ]] || die "registry required"; local reg=$1; shift
      local body=$(jb \
        registry="$reg" \
        token="$(flag token "$@")" \
        scopes="$(flag scopes "$@")")
      api PUT "/orgs/$org/servers/$sid/sites/$siteid/npm/credentials/$reg" "$body" ;;
    
    delete)
      [[ ${1:-} ]] || die "registry required"
      api DELETE "/orgs/$org/servers/$sid/sites/$siteid/npm/credentials/$1" ;;
    
    *) cat <<'EOF'
npm-credentials: list <srv> <site> | get <srv> <site> <registry>
                 create <srv> <site> --registry REG --token TOKEN [--scopes SCOPES]
                 update <srv> <site> <registry> --token TOKEN
                 delete <srv> <site> <registry>
                 [--org ORG for all commands]
EOF
  esac
}

# ══════════════════════════════════════════════════════════════════════════════
# HEARTBEATS (per-site)
# ══════════════════════════════════════════════════════════════════════════════

cmd_heartbeats() {
  local act=${1:-help}; shift 2>/dev/null || true
  local org=$(get_org "$@")
  [[ ${1:-} && ${2:-} ]] || die "server-id site-id required"; local sid=$1 siteid=$2; shift 2 2>/dev/null || true
  
  case $act in
    list)
      api GET "/orgs/$org/servers/$sid/sites/$siteid/heartbeats" ;;
    
    get)
      [[ ${1:-} ]] || die "heartbeat-id required"
      api GET "/orgs/$org/servers/$sid/sites/$siteid/heartbeats/$1" ;;
    
    create)
      local body=$(jb \
        name="$(flag name "$@")" \
        grace_period:int="$(flag grace-period "$@")" \
        frequency="$(flag frequency "$@")" \
        custom_frequency="$(flag custom-frequency "$@")")
      api POST "/orgs/$org/servers/$sid/sites/$siteid/heartbeats" "$body" ;;
    
    update)
      [[ ${1:-} ]] || die "heartbeat-id required"; local hid=$1; shift
      local body=$(jb \
        name="$(flag name "$@")" \
        grace_period:int="$(flag grace-period "$@")" \
        frequency="$(flag frequency "$@")" \
        custom_frequency="$(flag custom-frequency "$@")")
      api PUT "/orgs/$org/servers/$sid/sites/$siteid/heartbeats/$hid" "$body" ;;
    
    delete)
      [[ ${1:-} ]] || die "heartbeat-id required"
      api DELETE "/orgs/$org/servers/$sid/sites/$siteid/heartbeats/$1" ;;
    
    *) cat <<'EOF'
heartbeats: list <srv> <site> | get <srv> <site> <id> | delete <srv> <site> <id>
            create <srv> <site> --name N --grace-period SECS --frequency F
            update <srv> <site> <id> --name N --grace-period SECS
            [--org ORG for all commands]
EOF
  esac
}

# ══════════════════════════════════════════════════════════════════════════════
# DEPLOYMENTS
# ══════════════════════════════════════════════════════════════════════════════

cmd_deployments() {
  local act=${1:-help}; shift 2>/dev/null || true
  
  if [[ $act == "help" || $act == "--help" ]]; then
    cat <<'EOF'
deployments: list <srv> <site> | get <srv> <site> <id> | log <srv> <site> <id>
             deploy <srv> <site> | status <srv> <site> | enable <srv> <site>
             script <srv> <site> | update-script <srv> <site> --content "..."
             hook <srv> <site> | update-hook <srv> <site>
             push-to-deploy <srv> <site> | delete-push-to-deploy <srv> <site>
             [--org ORG for all commands]
EOF
    return
  fi
  
  local org=$(get_org "$@")
  [[ ${1:-} && ${2:-} ]] || die "server-id site-id required"; local sid=$1 siteid=$2; shift 2 2>/dev/null || true
  
  case $act in
    list)
      api GET "/orgs/$org/servers/$sid/sites/$siteid/deployments" ;;
    
    get)
      [[ ${1:-} ]] || die "deployment-id required"
      api GET "/orgs/$org/servers/$sid/sites/$siteid/deployments/$1" ;;
    
    deploy)
      api POST "/orgs/$org/servers/$sid/sites/$siteid/deployments" ;;
    
    status)
      api GET "/orgs/$org/servers/$sid/sites/$siteid/deployments/status" ;;
    
    enable)
      api DELETE "/orgs/$org/servers/$sid/sites/$siteid/deployments/status" ;;
    
    script)
      api GET "/orgs/$org/servers/$sid/sites/$siteid/deployments/script" ;;
    
    update-script)
      local c=$(flag content "$@"); [[ $c ]] || die "--content required"
      api PUT "/orgs/$org/servers/$sid/sites/$siteid/deployments/script" "$(jb \
        content="$c" \
        auto_source:bool="$(flag auto-source "$@")")" ;;
    
    hook)
      api GET "/orgs/$org/servers/$sid/sites/$siteid/deployments/deploy-hook" ;;
    
    update-hook)
      api PUT "/orgs/$org/servers/$sid/sites/$siteid/deployments/deploy-hook" ;;
    
    push-to-deploy)
      api POST "/orgs/$org/servers/$sid/sites/$siteid/deployments/push-to-deploy" ;;
    
    delete-push-to-deploy)
      api DELETE "/orgs/$org/servers/$sid/sites/$siteid/deployments/push-to-deploy" ;;
    
    log)
      [[ ${1:-} ]] || die "deployment-id required"
      api GET "/orgs/$org/servers/$sid/sites/$siteid/deployments/$1/log" ;;
    
    *) cat <<'EOF'
deployments: list <srv> <site> | get <srv> <site> <id> | log <srv> <site> <id>
             deploy <srv> <site> | status <srv> <site> | enable <srv> <site>
             script <srv> <site> | update-script <srv> <site> --content "..."
             hook <srv> <site> | update-hook <srv> <site>
             push-to-deploy <srv> <site> | delete-push-to-deploy <srv> <site>
             [--org ORG for all commands]
EOF
  esac
}

# ══════════════════════════════════════════════════════════════════════════════
# WEBHOOKS (deployment)
# ══════════════════════════════════════════════════════════════════════════════

cmd_webhooks() {
  local act=${1:-help}; shift 2>/dev/null || true
  local org=$(get_org "$@")
  [[ ${1:-} && ${2:-} ]] || die "server-id site-id required"; local sid=$1 siteid=$2; shift 2 2>/dev/null || true
  
  case $act in
    list)
      api GET "/orgs/$org/servers/$sid/sites/$siteid/webhooks" ;;
    
    get)
      [[ ${1:-} ]] || die "webhook-id required"
      api GET "/orgs/$org/servers/$sid/sites/$siteid/webhooks/$1" ;;
    
    create)
      local url=$(flag url "$@"); [[ $url ]] || die "--url required"
      api POST "/orgs/$org/servers/$sid/sites/$siteid/webhooks" "$(jb url="$url")" ;;
    
    delete)
      [[ ${1:-} ]] || die "webhook-id required"
      api DELETE "/orgs/$org/servers/$sid/sites/$siteid/webhooks/$1" ;;
    
    *) cat <<'EOF'
webhooks: list <srv> <site> | get <srv> <site> <id> | delete <srv> <site> <id>
          create <srv> <site> --url URL
          [--org ORG for all commands]
EOF
  esac
}

# ══════════════════════════════════════════════════════════════════════════════
# COMMANDS (run on site)
# ══════════════════════════════════════════════════════════════════════════════

cmd_commands() {
  local act=${1:-help}; shift 2>/dev/null || true
  local org=$(get_org "$@")
  [[ ${1:-} && ${2:-} ]] || die "server-id site-id required"; local sid=$1 siteid=$2; shift 2 2>/dev/null || true
  
  case $act in
    list)
      api GET "/orgs/$org/servers/$sid/sites/$siteid/commands" ;;
    
    get)
      [[ ${1:-} ]] || die "command-id required"
      api GET "/orgs/$org/servers/$sid/sites/$siteid/commands/$1" ;;
    
    run)
      local cmd=$(flag command "$@"); [[ $cmd ]] || die "--command required"
      api POST "/orgs/$org/servers/$sid/sites/$siteid/commands" "$(jb command="$cmd")" ;;
    
    delete)
      [[ ${1:-} ]] || die "command-id required"
      api DELETE "/orgs/$org/servers/$sid/sites/$siteid/commands/$1" ;;
    
    output)
      [[ ${1:-} ]] || die "command-id required"
      api GET "/orgs/$org/servers/$sid/sites/$siteid/commands/$1/output" ;;
    
    *) cat <<'EOF'
commands: list <srv> <site> | get <srv> <site> <id> | output <srv> <site> <id>
          run <srv> <site> --command "php artisan migrate" | delete <srv> <site> <id>
          [--org ORG for all commands]
EOF
  esac
}

# ══════════════════════════════════════════════════════════════════════════════
# REDIRECT RULES
# ══════════════════════════════════════════════════════════════════════════════

cmd_redirects() {
  local act=${1:-help}; shift 2>/dev/null || true
  local org=$(get_org "$@")
  [[ ${1:-} && ${2:-} ]] || die "server-id site-id required"; local sid=$1 siteid=$2; shift 2 2>/dev/null || true
  
  case $act in
    list)
      api GET "/orgs/$org/servers/$sid/sites/$siteid/redirect-rules" ;;
    
    get)
      [[ ${1:-} ]] || die "redirect-id required"
      api GET "/orgs/$org/servers/$sid/sites/$siteid/redirect-rules/$1" ;;
    
    create)
      local body=$(jb \
        from="$(flag from "$@")" \
        to="$(flag to "$@")" \
        type="$(flag type "$@")")
      api POST "/orgs/$org/servers/$sid/sites/$siteid/redirect-rules" "$body" ;;
    
    delete)
      [[ ${1:-} ]] || die "redirect-id required"
      api DELETE "/orgs/$org/servers/$sid/sites/$siteid/redirect-rules/$1" ;;
    
    *) cat <<'EOF'
redirects: list <srv> <site> | get <srv> <site> <id> | delete <srv> <site> <id>
           create <srv> <site> --from /old --to /new --type permanent|temporary
           [--org ORG for all commands]
EOF
  esac
}

# ══════════════════════════════════════════════════════════════════════════════
# SECURITY RULES
# ══════════════════════════════════════════════════════════════════════════════

cmd_security() {
  local act=${1:-help}; shift 2>/dev/null || true
  local org=$(get_org "$@")
  [[ ${1:-} && ${2:-} ]] || die "server-id site-id required"; local sid=$1 siteid=$2; shift 2 2>/dev/null || true
  
  case $act in
    list)
      api GET "/orgs/$org/servers/$sid/sites/$siteid/security-rules" ;;
    
    get)
      [[ ${1:-} ]] || die "security-rule-id required"
      api GET "/orgs/$org/servers/$sid/sites/$siteid/security-rules/$1" ;;
    
    create)
      local body=$(jb \
        name="$(flag name "$@")" \
        path="$(flag path "$@")" \
        credentials:arr="$(flag credentials "$@")")
      api POST "/orgs/$org/servers/$sid/sites/$siteid/security-rules" "$body" ;;
    
    update)
      [[ ${1:-} ]] || die "security-rule-id required"; local rid=$1; shift
      local body=$(jb \
        name="$(flag name "$@")" \
        path="$(flag path "$@")" \
        credentials:arr="$(flag credentials "$@")")
      api PUT "/orgs/$org/servers/$sid/sites/$siteid/security-rules/$rid" "$body" ;;
    
    delete)
      [[ ${1:-} ]] || die "security-rule-id required"
      api DELETE "/orgs/$org/servers/$sid/sites/$siteid/security-rules/$1" ;;
    
    *) cat <<'EOF'
security: list <srv> <site> | get <srv> <site> <id> | delete <srv> <site> <id>
          create <srv> <site> --name N --credentials "[{\"user\":\"u\",\"password\":\"p\"}]" [--path /admin]
          update <srv> <site> <id> --name N --path /new
          [--org ORG for all commands]
EOF
  esac
}

# ══════════════════════════════════════════════════════════════════════════════
# INTEGRATIONS (Horizon, Octane, Reverb, Pulse, Inertia, Maintenance, Scheduler)
# ══════════════════════════════════════════════════════════════════════════════

cmd_integrations() {
  local act=${1:-help}; shift 2>/dev/null || true
  local org=$(get_org "$@")
  
  case $act in
    horizon|octane|reverb|inertia|pulse|laravel-maintenance|laravel-scheduler)
      [[ ${1:-} && ${2:-} ]] || die "server-id site-id required"; local sid=$1 siteid=$2; shift 2
      local sub=${1:-help}; shift 2>/dev/null || true
      
      case $sub in
        get)
          api GET "/orgs/$org/servers/$sid/sites/$siteid/integrations/$act" ;;
        create|enable)
          if [[ $act == "octane" ]]; then
            local body=$(jb \
              port:int="$(flag port "$@")" \
              server="$(flag server "$@")")
            api POST "/orgs/$org/servers/$sid/sites/$siteid/integrations/$act" "$body"
          elif [[ $act == "reverb" ]]; then
            local body=$(jb \
              host="$(flag host "$@")" \
              port:int="$(flag port "$@")" \
              connections="$(flag connections "$@")")
            api POST "/orgs/$org/servers/$sid/sites/$siteid/integrations/$act" "$body"
          else
            api POST "/orgs/$org/servers/$sid/sites/$siteid/integrations/$act"
          fi ;;
        delete|disable)
          api DELETE "/orgs/$org/servers/$sid/sites/$siteid/integrations/$act" ;;
        *)
          echo "$act: get <srv> <site> | create <srv> <site> | delete <srv> <site>" ;;
      esac ;;
    
    *) cat <<'EOF'
integrations: horizon <srv> <site> get|create|delete
              octane <srv> <site> get|create --port N --server swoole|roadrunner|frankenphp | delete
              reverb <srv> <site> get|create --host H --port N --connections redis|in-memory | delete
              pulse <srv> <site> get|create|delete
              inertia <srv> <site> get|create
              laravel-maintenance <srv> <site> get|create|delete
              laravel-scheduler <srv> <site> get|create|delete
              [--org ORG for all commands]
EOF
  esac
}

# ══════════════════════════════════════════════════════════════════════════════
# RECIPES
# ══════════════════════════════════════════════════════════════════════════════

cmd_recipes() {
  local act=${1:-help}; shift 2>/dev/null || true
  local org=$(get_org "$@")
  
  case $act in
    list)
      api GET "/orgs/$org/recipes" ;;
    
    get)
      [[ ${1:-} ]] || die "recipe-id required"
      api GET "/orgs/$org/recipes/$1" ;;
    
    create)
      local body=$(jb \
        name="$(flag name "$@")" \
        user="$(flag user "$@")" \
        script="$(flag script "$@")" \
        team_id:int="$(flag team-id "$@")")
      api POST "/orgs/$org/recipes" "$body" ;;
    
    update)
      [[ ${1:-} ]] || die "recipe-id required"; local rid=$1; shift
      local body=$(jb \
        name="$(flag name "$@")" \
        user="$(flag user "$@")" \
        script="$(flag script "$@")")
      api PUT "/orgs/$org/recipes/$rid" "$body" ;;
    
    delete)
      [[ ${1:-} ]] || die "recipe-id required"
      api DELETE "/orgs/$org/recipes/$1" ;;
    
    runs)
      [[ ${1:-} ]] || die "recipe-id required"
      api GET "/orgs/$org/recipes/$1/runs" ;;
    
    run)
      [[ ${1:-} ]] || die "recipe-id required"; local rid=$1; shift
      local body=$(jb \
        email="$(flag email "$@")" \
        servers:arr="$(flag servers "$@")")
      api POST "/orgs/$org/recipes/$rid/runs" "$body" ;;
    
    run-log)
      [[ ${1:-} && ${2:-} ]] || die "recipe-id log-id required"
      api GET "/orgs/$org/recipes/$1/runs/$2" ;;
    
    forge-recipes)
      api GET /forge-recipes ;;
    
    forge-recipe)
      [[ ${1:-} ]] || die "forge-recipe-id required"
      api GET "/forge-recipes/$1" ;;
    
    run-forge-recipe)
      [[ ${1:-} ]] || die "forge-recipe-id required"; local frid=$1; shift
      local body=$(jb \
        email="$(flag email "$@")" \
        servers:arr="$(flag servers "$@")")
      api POST "/forge-recipes/$frid/runs" "$body" ;;
    
    *) cat <<'EOF'
recipes: list | get <id> | delete <id>
         create --name N --user U --script "..." [--team-id ID]
         update <id> --name N --script "..."
         runs <id> | run <id> --servers "[1,2]" | run-log <id> <log-id>
         forge-recipes | forge-recipe <id> | run-forge-recipe <id> --servers "[1,2]"
         [--org ORG for all commands]
EOF
  esac
}

# ══════════════════════════════════════════════════════════════════════════════
# STORAGE PROVIDERS
# ══════════════════════════════════════════════════════════════════════════════

cmd_storage_providers() {
  local act=${1:-help}; shift 2>/dev/null || true
  local org=$(get_org "$@")
  
  case $act in
    list)
      api GET "/orgs/$org/storage-providers" ;;
    
    get)
      [[ ${1:-} ]] || die "storage-provider-id required"
      api GET "/orgs/$org/storage-providers/$1" ;;
    
    create)
      local body=$(jb \
        name="$(flag name "$@")" \
        provider="$(flag provider "$@")" \
        region="$(flag region "$@")" \
        bucket="$(flag bucket "$@")" \
        directory="$(flag directory "$@")" \
        endpoint="$(flag endpoint "$@")" \
        access_key="$(flag access-key "$@")" \
        secret_key="$(flag secret-key "$@")" \
        assume_role:bool="$(flag assume-role "$@")")
      api POST "/orgs/$org/storage-providers" "$body" ;;
    
    update)
      [[ ${1:-} ]] || die "storage-provider-id required"; local spid=$1; shift
      local body=$(jb \
        name="$(flag name "$@")" \
        provider="$(flag provider "$@")" \
        region="$(flag region "$@")" \
        bucket="$(flag bucket "$@")" \
        endpoint="$(flag endpoint "$@")" \
        access_key="$(flag access-key "$@")" \
        secret_key="$(flag secret-key "$@")" \
        use_ec2_assumed_role:bool="$(flag use-ec2-assumed-role "$@")" \
        directory="$(flag directory "$@")")
      api PUT "/orgs/$org/storage-providers/$spid" "$body" ;;
    
    delete)
      [[ ${1:-} ]] || die "storage-provider-id required"
      api DELETE "/orgs/$org/storage-providers/$1" ;;
    
    *) cat <<'EOF'
storage-providers: list | get <id> | delete <id>
                   create --name N --provider s3|digitalocean|cloudflare --bucket B
                   update <id> --name N [--region R] [--access-key K]
                   [--org ORG for all commands]
EOF
  esac
}

# ══════════════════════════════════════════════════════════════════════════════
# TEAMS
# ══════════════════════════════════════════════════════════════════════════════

cmd_teams() {
  local act=${1:-help}; shift 2>/dev/null || true
  local org=$(get_org "$@")
  
  case $act in
    list)
      api GET "/orgs/$org/teams" ;;
    
    get)
      [[ ${1:-} ]] || die "team-id required"
      api GET "/orgs/$org/teams/$1" ;;
    
    create)
      local body=$(jb \
        name="$(flag name "$@")" \
        users:arr="$(flag users "$@")" \
        invites:arr="$(flag invites "$@")")
      api POST "/orgs/$org/teams" "$body" ;;
    
    update)
      [[ ${1:-} ]] || die "team-id required"; local tid=$1; shift
      local body=$(jb \
        name="$(flag name "$@")" \
        users:arr="$(flag users "$@")")
      api PUT "/orgs/$org/teams/$tid" "$body" ;;
    
    delete)
      [[ ${1:-} ]] || die "team-id required"
      api DELETE "/orgs/$org/teams/$1" ;;
    
    members)
      [[ ${1:-} ]] || die "team-id required"
      api GET "/orgs/$org/teams/$1/members" ;;
    
    member)
      [[ ${1:-} && ${2:-} ]] || die "team-id user-id required"
      api GET "/orgs/$org/teams/$1/members/$2" ;;
    
    update-member)
      [[ ${1:-} && ${2:-} ]] || die "team-id user-id required"; local tid=$1 uid=$2; shift 2
      local rid=$(flag role-id "$@"); [[ $rid ]] || die "--role-id required"
      api PUT "/orgs/$org/teams/$tid/members/$uid" "$(jb role_id:int="$rid")" ;;
    
    remove-member)
      [[ ${1:-} && ${2:-} ]] || die "team-id user-id required"
      api DELETE "/orgs/$org/teams/$1/members/$2" ;;
    
    invites)
      [[ ${1:-} ]] || die "team-id required"
      api GET "/orgs/$org/teams/$1/invites" ;;
    
    invite)
      [[ ${1:-} ]] || die "team-id required"; local tid=$1; shift
      local body=$(jb \
        role_id:int="$(flag role-id "$@")" \
        email="$(flag email "$@")")
      api POST "/orgs/$org/teams/$tid/invites" "$body" ;;
    
    get-invite)
      [[ ${1:-} && ${2:-} ]] || die "team-id invitation-id required"
      api GET "/orgs/$org/teams/$1/invites/$2" ;;
    
    delete-invite)
      [[ ${1:-} && ${2:-} ]] || die "team-id invitation-id required"
      api DELETE "/orgs/$org/teams/$1/invites/$2" ;;
    
    *) cat <<'EOF'
teams: list | get <id> | delete <id>
       create --name N [--users "[...]"] [--invites "[...]"]
       update <id> --name N
       members <id> | member <id> <user-id> | update-member <id> <user-id> --role-id RID
       remove-member <id> <user-id>
       invites <id> | invite <id> --role-id RID --email EMAIL
       get-invite <id> <invitation-id> | delete-invite <id> <invitation-id>
       [--org ORG for all commands]
EOF
  esac
}

# ══════════════════════════════════════════════════════════════════════════════
# ROLES
# ══════════════════════════════════════════════════════════════════════════════

cmd_roles() {
  local act=${1:-help}; shift 2>/dev/null || true
  local org=$(get_org "$@")
  
  case $act in
    predefined)
      api GET /predefined-roles ;;
    
    predefined-role)
      [[ ${1:-} ]] || die "role-id required"
      api GET "/predefined-roles/$1" ;;
    
    permissions)
      api GET /permissions ;;
    
    permission)
      [[ ${1:-} ]] || die "permission-id required"
      api GET "/permissions/$1" ;;
    
    list)
      api GET "/orgs/$org/roles" ;;
    
    get)
      [[ ${1:-} ]] || die "role-id required"
      api GET "/orgs/$org/roles/$1" ;;
    
    create)
      local body=$(jb \
        name="$(flag name "$@")" \
        permissions:arr="$(flag permissions "$@")")
      api POST "/orgs/$org/roles" "$body" ;;
    
    update)
      [[ ${1:-} ]] || die "role-id required"; local rid=$1; shift
      local body=$(jb \
        name="$(flag name "$@")" \
        permissions:arr="$(flag permissions "$@")")
      api PUT "/orgs/$org/roles/$rid" "$body" ;;
    
    delete)
      [[ ${1:-} ]] || die "role-id required"
      api DELETE "/orgs/$org/roles/$1" ;;
    
    role-permissions)
      [[ ${1:-} ]] || die "role-id required"
      api GET "/orgs/$org/roles/$1/permissions" ;;
    
    *) cat <<'EOF'
roles: predefined | predefined-role <id> | permissions | permission <id>
       list | get <id> | delete <id>
       create --name N --permissions "[...]"
       update <id> --name N --permissions "[...]"
       role-permissions <id>
       [--org ORG for list/get/create/update/delete/role-permissions]
EOF
  esac
}

# ══════════════════════════════════════════════════════════════════════════════
# SERVER CREDENTIALS & VPCs
# ══════════════════════════════════════════════════════════════════════════════

cmd_server_credentials() {
  local act=${1:-help}; shift 2>/dev/null || true
  local org=$(get_org "$@")
  
  case $act in
    list)
      api GET "/orgs/$org/server-credentials" ;;
    
    get)
      [[ ${1:-} ]] || die "credential-id required"
      api GET "/orgs/$org/server-credentials/$1" ;;
    
    vpcs)
      [[ ${1:-} && ${2:-} ]] || die "credential-id region required"
      api GET "/orgs/$org/server-credentials/$1/regions/$2/vpcs" ;;
    
    vpc)
      [[ ${1:-} && ${2:-} && ${3:-} ]] || die "credential-id region vpc-id required"
      api GET "/orgs/$org/server-credentials/$1/regions/$2/vpcs/$3" ;;
    
    create-vpc)
      [[ ${1:-} && ${2:-} ]] || die "credential-id region required"; local cid=$1 reg=$2; shift 2
      local n=$(flag name "$@"); [[ $n ]] || die "--name required"
      api POST "/orgs/$org/server-credentials/$cid/regions/$reg/vpcs" "$(jb name="$n")" ;;
    
    *) cat <<'EOF'
server-credentials: list | get <credential-id>
                    vpcs <credential-id> <region> | vpc <credential-id> <region> <vpc-id>
                    create-vpc <credential-id> <region> --name NAME
                    [--org ORG for all commands]
EOF
  esac
}

# ══════════════════════════════════════════════════════════════════════════════
# MAIN DISPATCH
# ══════════════════════════════════════════════════════════════════════════════

cmd=${1:-help}
shift 2>/dev/null || true

case $cmd in
  user) cmd_user "$@" ;;
  organizations|orgs) cmd_organizations "$@" ;;
  providers) cmd_providers "$@" ;;
  servers) cmd_servers "$@" ;;
  services) cmd_services "$@" ;;
  php) cmd_php "$@" ;;
  background-processes|daemons) cmd_background_processes "$@" ;;
  firewall) cmd_firewall "$@" ;;
  jobs|scheduled-jobs) cmd_jobs "$@" ;;
  keys|ssh-keys) cmd_keys "$@" ;;
  databases) cmd_databases "$@" ;;
  db-users) cmd_db_users "$@" ;;
  backups) cmd_backups "$@" ;;
  monitors) cmd_monitors "$@" ;;
  nginx-templates) cmd_nginx_templates "$@" ;;
  logs) cmd_logs "$@" ;;
  sites) cmd_sites "$@" ;;
  domains) cmd_domains "$@" ;;
  composer-credentials) cmd_composer_credentials "$@" ;;
  npm-credentials) cmd_npm_credentials "$@" ;;
  heartbeats) cmd_heartbeats "$@" ;;
  deployments|deploy) cmd_deployments "$@" ;;
  webhooks) cmd_webhooks "$@" ;;
  commands) cmd_commands "$@" ;;
  redirects|redirect-rules) cmd_redirects "$@" ;;
  security|security-rules) cmd_security "$@" ;;
  integrations) cmd_integrations "$@" ;;
  recipes) cmd_recipes "$@" ;;
  storage-providers) cmd_storage_providers "$@" ;;
  teams) cmd_teams "$@" ;;
  roles) cmd_roles "$@" ;;
  server-credentials) cmd_server_credentials "$@" ;;
  
  help|--help|-h)
    cat <<'EOF'
Laravel Forge API CLI

Usage: laravel-forge <resource> <action> [args...] [--org ORG]

Resources:
  user                     — Get current user
  organizations            — List/get organizations
  providers                — Cloud provider info (regions, sizes)
  servers                  — Manage servers
  services                 — Control services (nginx, mysql, postgres, redis, php, supervisor)
  php                      — PHP version management & configuration
  background-processes     — Background processes (daemons/supervisor)
  firewall                 — Firewall rules
  jobs                     — Scheduled jobs (cron)
  keys                     — SSH keys
  databases                — Database schemas
  db-users                 — Database users
  backups                  — Database backup configurations & instances
  monitors                 — Server monitors
  nginx-templates          — Nginx templates
  logs                     — Server logs
  sites                    — Site management
  domains                  — Per-site domain management
  composer-credentials     — Per-site Composer credentials
  npm-credentials          — Per-site NPM credentials
  heartbeats               — Site heartbeats
  deployments              — Deployments & scripts
  webhooks                 — Deployment webhooks
  commands                 — Run commands on sites
  redirects                — Redirect rules
  security                 — Security rules (HTTP auth)
  integrations             — Laravel integrations (Horizon, Octane, Reverb, Pulse, etc.)
  recipes                  — Recipes
  storage-providers        — Storage providers for backups
  teams                    — Team management
  roles                    — Role & permission management
  server-credentials       — Server credentials & VPCs

Run: laravel-forge <resource> help    for resource-specific help

Examples:
  laravel-forge user get
  laravel-forge organizations list
  laravel-forge servers list --org my-org
  laravel-forge sites list --org my-org
  laravel-forge deployments deploy 12345 67890 --org my-org

Configuration:
  Set LARAVEL_FORGE_API_TOKEN or create ~/.openclaw/credentials/laravel-forge/config.json:
    {"token":"your-token","org":"default-org-slug"}
EOF
    ;;
  
  *)
    echo "Unknown resource: $cmd"
    echo "Run: laravel-forge help"
    exit 1
    ;;
esac
