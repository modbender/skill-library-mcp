#!/usr/bin/env bash
# dev-serve — Start a dev server in tmux and expose it via Caddy
#
# Usage:
#   dev-serve up <repo-path> [port]      Start dev server + add Caddy route
#   dev-serve down <name>                Stop dev server + remove Caddy route
#   dev-serve ls                         List active dev servers
#   dev-serve restart <name>             Restart the dev server (keep Caddy route)
#
# The subdomain is derived from the repo folder name:
#   ~/projects/myapp → myapp.YOUR_DOMAIN
#
# Port auto-assigns starting at 5200 if not specified.
# Dev server command is detected from package.json scripts.dev
# or can be overridden with DEV_CMD env var.
#
# Configuration (env vars):
#   DEV_SERVE_DOMAIN     Required. Your wildcard domain (e.g. mini.example.com)
#   DEV_SERVE_STATE_DIR  State directory (default: ~/.config/dev-serve)
#   CADDYFILE            Caddyfile path (default: ~/.config/caddy/Caddyfile)
#   CADDY_ADMIN          Caddy admin API (default: http://localhost:2019)
#   DEV_CMD              Override the dev server command

set -euo pipefail

# --- Configuration ---
DOMAIN="${DEV_SERVE_DOMAIN:-}"
if [[ -z "$DOMAIN" ]]; then
  echo "Error: DEV_SERVE_DOMAIN is not set." >&2
  echo "Export it in your shell profile, e.g.: export DEV_SERVE_DOMAIN=mini.example.com" >&2
  exit 1
fi

STATE_DIR="${DEV_SERVE_STATE_DIR:-${HOME}/.config/dev-serve}"
STATE_FILE="${STATE_DIR}/state.json"
CADDYFILE="${CADDYFILE:-${HOME}/.config/caddy/Caddyfile}"
CADDY_ADMIN="${CADDY_ADMIN:-http://localhost:2019}"

mkdir -p "$STATE_DIR"
[[ -f "$STATE_FILE" ]] || echo '{}' > "$STATE_FILE"

usage() {
  sed -n '2,/^$/p' "$0" | sed 's/^# \?//'
  exit 1
}

# Find next available port (starting at 5200)
next_port() {
  local port=5200
  local used
  used=$(jq -r '.[].port // empty' "$STATE_FILE" 2>/dev/null | sort -n)
  # Also check Caddyfile for ports in use
  local caddy_ports
  caddy_ports=$(grep -oE 'localhost:[0-9]+' "$CADDYFILE" 2>/dev/null | sed 's/localhost://' | sort -n)
  local all_used
  all_used=$(printf "%s\n%s" "$used" "$caddy_ports" | sort -nu)
  while echo "$all_used" | grep -qx "$port"; do
    port=$((port + 1))
  done
  echo "$port"
}

# Detect dev command from package.json
detect_dev_cmd() {
  local repo="$1"
  local port="$2"

  # Check for override
  if [[ -n "${DEV_CMD:-}" ]]; then
    echo "$DEV_CMD"
    return
  fi

  # Detect package manager
  local pm="npm"
  if [[ -f "$repo/pnpm-lock.yaml" ]]; then
    pm="pnpm"
  elif [[ -f "$repo/bun.lockb" ]] || [[ -f "$repo/bun.lock" ]]; then
    pm="bun"
  elif [[ -f "$repo/yarn.lock" ]]; then
    pm="yarn"
  fi

  # Read dev script
  local dev_script
  dev_script=$(jq -r '.scripts.dev // empty' "$repo/package.json" 2>/dev/null)

  if [[ -z "$dev_script" ]]; then
    echo >&2 "Error: No 'dev' script in package.json. Set DEV_CMD env var."
    exit 1
  fi

  # Check if it's a vite-based server (needs --host and --port flags)
  if echo "$dev_script" | grep -qiE '(vite|next|nuxt|svelte)'; then
    echo "$pm run dev -- --host 0.0.0.0 --port $port"
  else
    echo "PORT=$port $pm run dev"
  fi
}

# Add Caddy route to Caddyfile
add_caddy_route() {
  local name="$1"
  local port="$2"
  local subdomain="${name}.${DOMAIN}"

  # Check if route already exists
  if grep -q "${subdomain}" "$CADDYFILE"; then
    echo "  Caddy route for ${subdomain} already exists, updating port..."
    # Update the port in existing route
    if [[ "$(uname)" == "Darwin" ]]; then
      sed -i '' "/${subdomain}/,/^}/s/localhost:[0-9]*/localhost:${port}/" "$CADDYFILE"
    else
      sed -i "/${subdomain}/,/^}/s/localhost:[0-9]*/localhost:${port}/" "$CADDYFILE"
    fi
  else
    # Add new route block
    cat >> "$CADDYFILE" <<EOF

# ${name} (dev-serve)
${subdomain} {
	import vercel_tls
	reverse_proxy localhost:${port}
}
EOF

    # Add to dashboard HTML if there's a </ul> tag
    if grep -q '</ul>' "$CADDYFILE"; then
      local dashboard_entry="<li><a href=\"https://${subdomain}\">${name}<div class=\"desc\">Dev Server</div></a></li>"
      if [[ "$(uname)" == "Darwin" ]]; then
        sed -i '' "s|</ul>|${dashboard_entry}\n\t</ul>|" "$CADDYFILE"
      else
        sed -i "s|</ul>|${dashboard_entry}\n\t</ul>|" "$CADDYFILE"
      fi
    fi
  fi
}

# Remove Caddy route from Caddyfile
remove_caddy_route() {
  local name="$1"
  local subdomain="${name}.${DOMAIN}"

  if [[ "$(uname)" == "Darwin" ]]; then
    # Remove the server block (comment line + block)
    sed -i '' "/# ${name} (dev-serve)/,/^}/d" "$CADDYFILE"
    # Remove dashboard entry
    sed -i '' "/${subdomain}/d" "$CADDYFILE"
  else
    sed -i "/# ${name} (dev-serve)/,/^}/d" "$CADDYFILE"
    sed -i "/${subdomain}/d" "$CADDYFILE"
  fi
}

# Reload Caddy via admin API
reload_caddy() {
  echo "  Reloading Caddy..."
  if curl -sf -X POST "${CADDY_ADMIN}/load" \
    -H "Content-Type: text/caddyfile" \
    --data-binary "@${CADDYFILE}" >/dev/null 2>&1; then
    echo "  ✅ Caddy reloaded"
  else
    echo "  ⚠️  Caddy API reload failed. Try: caddy reload --config ${CADDYFILE} --address localhost:2019"
  fi
}

# Patch Vite allowedHosts to include the subdomain
patch_vite_allowed_hosts() {
  local repo="$1"
  local subdomain="$2"

  # Find vite config file
  local vite_config=""
  for candidate in "vite.config.ts" "vite.config.js" "vite.config.mts" "vite.config.mjs"; do
    if [[ -f "$repo/$candidate" ]]; then
      vite_config="$repo/$candidate"
      break
    fi
  done

  if [[ -z "$vite_config" ]]; then
    return 0  # Not a Vite project
  fi

  # Check if subdomain already in allowedHosts
  if grep -q "$subdomain" "$vite_config" 2>/dev/null; then
    echo "  allowedHosts already includes ${subdomain}"
    return 0
  fi

  # Check if allowedHosts array exists
  if grep -q "allowedHosts" "$vite_config" 2>/dev/null; then
    if [[ "$(uname)" == "Darwin" ]]; then
      sed -i '' "s/allowedHosts: \[/allowedHosts: ['${subdomain}', /" "$vite_config"
    else
      sed -i "s/allowedHosts: \[/allowedHosts: ['${subdomain}', /" "$vite_config"
    fi
    echo "  ✅ Added ${subdomain} to allowedHosts in $(basename "$vite_config")"
  elif grep -q "server:" "$vite_config" 2>/dev/null; then
    if [[ "$(uname)" == "Darwin" ]]; then
      sed -i '' "/server:.*{/a\\
\\      allowedHosts: ['${subdomain}'],
" "$vite_config"
    else
      sed -i "/server:.*{/a\\      allowedHosts: ['${subdomain}']," "$vite_config"
    fi
    echo "  ✅ Added allowedHosts with ${subdomain} to $(basename "$vite_config")"
  else
    echo "  ⚠️  Could not auto-patch allowedHosts. Add manually to $(basename "$vite_config"):"
    echo "     server: { allowedHosts: ['${subdomain}'] }"
  fi
}

# Wait for dev server to be listening, then verify HTTPS end-to-end
verify_deployment() {
  local name="$1"
  local port="$2"
  local subdomain="${name}.${DOMAIN}"
  local url="https://${subdomain}"
  local max_wait=90
  local elapsed=0

  # Phase 1: Wait for dev server to listen on the port
  echo "  Waiting for dev server on port ${port}..."
  local lsof_cmd="/usr/sbin/lsof"
  [[ -x "$lsof_cmd" ]] || lsof_cmd="lsof"
  while ! $lsof_cmd -i ":${port}" -sTCP:LISTEN >/dev/null 2>&1; do
    sleep 2
    elapsed=$((elapsed + 2))
    if [[ $elapsed -ge 30 ]]; then
      echo "  ❌ Dev server not listening on port ${port} after 30s"
      echo "     Check: tmux attach -t dev-${name}"
      return 1
    fi
  done
  echo "  ✅ Dev server listening on port ${port} (${elapsed}s)"

  # Phase 2: Wait for HTTPS to work (cert provisioning)
  echo "  Waiting for HTTPS cert..."
  local http_code
  while true; do
    http_code=$(curl -sk -o /dev/null -w "%{http_code}" "$url/" 2>/dev/null || echo "000")
    if [[ "$http_code" =~ ^[23] ]]; then
      echo "  ✅ ${url} → HTTP ${http_code} (${elapsed}s total)"
      return 0
    fi
    sleep 3
    elapsed=$((elapsed + 3))
    if [[ $elapsed -ge $max_wait ]]; then
      if [[ "$http_code" == "000" ]]; then
        echo "  ❌ TLS cert not provisioned after ${max_wait}s"
        echo "     Check your Caddy error log for ACME failures"
      else
        echo "  ❌ ${url} → HTTP ${http_code} after ${max_wait}s"
      fi
      return 1
    fi
  done
}

cmd_up() {
  local repo="${1:?missing repo path}"
  local repo_abs
  repo_abs=$(cd "$repo" 2>/dev/null && pwd) || { echo "Error: '$repo' not found" >&2; exit 1; }
  local name
  name=$(basename "$repo_abs")
  local port="${2:-$(next_port)}"

  # Check if already running
  if jq -e ".\"$name\"" "$STATE_FILE" >/dev/null 2>&1; then
    echo "Error: '$name' is already running. Use 'dev-serve down $name' first or 'dev-serve restart $name'." >&2
    exit 1
  fi

  local dev_cmd
  dev_cmd=$(detect_dev_cmd "$repo_abs" "$port")
  local subdomain="${name}.${DOMAIN}"

  echo "🚀 Starting ${name}"
  echo "  Repo: ${repo_abs}"
  echo "  Port: ${port}"
  echo "  Command: ${dev_cmd}"
  echo "  URL: https://${subdomain}"
  echo ""

  # Patch Vite allowedHosts if needed
  patch_vite_allowed_hosts "$repo_abs" "$subdomain"

  # Create tmux session with dev server
  local session_name="dev-${name}"
  if tmux has-session -t "$session_name" 2>/dev/null; then
    echo "  Killing existing tmux session..."
    tmux kill-session -t "$session_name"
  fi

  tmux new-session -d -s "$session_name" -c "$repo_abs"
  tmux send-keys -t "$session_name" "$dev_cmd" C-m

  # Add Caddy route
  add_caddy_route "$name" "$port"

  # Reload Caddy
  reload_caddy

  # Save state
  local tmp
  tmp=$(mktemp)
  jq --arg name "$name" \
     --arg repo "$repo_abs" \
     --argjson port "$port" \
     --arg cmd "$dev_cmd" \
     --arg ts "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
     '. + {($name): {repo: $repo, port: $port, cmd: $cmd, tmux: ("dev-" + $name), created: $ts}}' \
     "$STATE_FILE" > "$tmp" && mv "$tmp" "$STATE_FILE"

  # Verify everything actually works
  echo ""
  if verify_deployment "$name" "$port"; then
    echo ""
    echo "✅ ${name} is live!"
    echo "   https://${subdomain}"
    echo "   tmux: ${session_name}"
  else
    echo ""
    echo "⚠️  ${name} started but verification failed."
    echo "   tmux: ${session_name}"
    echo "   Run 'dev-serve down ${name}' to clean up, or debug with the commands above."
  fi
}

cmd_down() {
  local name="${1:?missing name}"

  if ! jq -e ".\"$name\"" "$STATE_FILE" >/dev/null 2>&1; then
    echo "Error: '$name' not found in state" >&2
    exit 1
  fi

  local session_name="dev-${name}"

  echo "🛑 Stopping ${name}"

  # Kill tmux session
  if tmux has-session -t "$session_name" 2>/dev/null; then
    tmux kill-session -t "$session_name"
    echo "  Killed tmux session: ${session_name}"
  fi

  # Remove Caddy route
  remove_caddy_route "$name"

  # Reload Caddy
  reload_caddy

  # Remove from state
  local tmp
  tmp=$(mktemp)
  jq --arg name "$name" 'del(.[$name])' "$STATE_FILE" > "$tmp" && mv "$tmp" "$STATE_FILE"

  echo "✅ ${name} stopped"
}

cmd_restart() {
  local name="${1:?missing name}"

  if ! jq -e ".\"$name\"" "$STATE_FILE" >/dev/null 2>&1; then
    echo "Error: '$name' not found in state" >&2
    exit 1
  fi

  local repo cmd session_name
  repo=$(jq -r ".\"$name\".repo" "$STATE_FILE")
  cmd=$(jq -r ".\"$name\".cmd" "$STATE_FILE")
  session_name="dev-${name}"

  echo "🔄 Restarting ${name}"

  # Kill and recreate tmux session
  if tmux has-session -t "$session_name" 2>/dev/null; then
    tmux kill-session -t "$session_name"
  fi

  tmux new-session -d -s "$session_name" -c "$repo"
  tmux send-keys -t "$session_name" "$cmd" C-m

  echo "✅ ${name} restarted (tmux: ${session_name})"
}

cmd_ls() {
  if [[ ! -s "$STATE_FILE" ]] || [[ "$(jq 'length' "$STATE_FILE")" == "0" ]]; then
    echo "No active dev servers"
    return
  fi

  printf "%-20s %-8s %-15s %-40s %s\n" "NAME" "PORT" "TMUX" "URL" "STATUS"
  printf "%-20s %-8s %-15s %-40s %s\n" "----" "----" "----" "---" "------"
  jq -r 'to_entries[] | [.key, (.value.port|tostring), .value.tmux] | @tsv' "$STATE_FILE" | \
    while IFS=$'\t' read -r name port session; do
      local url="https://${name}.${DOMAIN}"
      local status="?"
      if tmux has-session -t "$session" 2>/dev/null; then
        status="running"
      else
        status="stopped"
      fi
      printf "%-20s %-8s %-15s %-40s %s\n" "$name" "$port" "$session" "$url" "$status"
    done
}

case "${1:-}" in
  up)      shift; cmd_up "$@" ;;
  down)    shift; cmd_down "$@" ;;
  restart) shift; cmd_restart "$@" ;;
  ls)      cmd_ls ;;
  *)       usage ;;
esac
