#!/usr/bin/env bash
# ClawVault Provider — Git (auto-commit + push with Ed25519 key)
set -euo pipefail
VAULT_DIR="$HOME/.clawvault"; CONFIG="$VAULT_DIR/config.yaml"; REPO_DIR="$VAULT_DIR/.git-local"
PROVIDER_CONFIG="$VAULT_DIR/.provider-git.json"
timestamp() { date -u +"%Y-%m-%dT%H:%M:%SZ"; }; log() { echo "[clawvault:git $(timestamp)] $*"; }

_git() { GIT_SSH_COMMAND="ssh -i $VAULT_DIR/keys/clawvault_ed25519 -o StrictHostKeyChecking=no" git -C "$REPO_DIR" "$@"; }

get_profile_name() {
  if [[ -n "${CLAWVAULT_PROFILE:-}" ]]; then echo "$CLAWVAULT_PROFILE"; return; fi
  local name
  name=$(grep 'profile_name:' "$CONFIG" 2>/dev/null | head -1 | awk '{print $2}' | tr -d '"')
  echo "${name:-$(hostname -s 2>/dev/null || echo default)}"
}

cmd_setup() {
  echo ""; echo "Git Remote Setup"; echo "================"
  read -rp "Git remote URL (SSH or HTTPS): " remote_url
  read -rp "Branch [main]: " branch; branch="${branch:-main}"

  if [[ -z "$remote_url" ]]; then log "URL required."; return 1; fi

  echo ""; echo "Add this deploy key to your repo (read/write access):"
  echo "────────────────────────────────"
  cat "$VAULT_DIR/keys/clawvault_ed25519.pub" 2>/dev/null
  echo "────────────────────────────────"
  echo ""; read -rp "Press Enter once the key is added..."

  if [[ -d "$REPO_DIR/.git" ]]; then
    _git remote set-url origin "$remote_url" 2>/dev/null || _git remote add origin "$remote_url"
  else
    GIT_SSH_COMMAND="ssh -i $VAULT_DIR/keys/clawvault_ed25519 -o StrictHostKeyChecking=no" git clone "$remote_url" "$REPO_DIR" 2>/dev/null || {
      mkdir -p "$REPO_DIR"; git -C "$REPO_DIR" init; git -C "$REPO_DIR" checkout -b "$branch"
      git -C "$REPO_DIR" remote add origin "$remote_url"
    }
  fi

  cat > "$PROVIDER_CONFIG" <<JSON
{"provider":"git","remote_url":"$remote_url","branch":"$branch","configured":"$(timestamp)"}
JSON
  log "Git configured → $remote_url ($branch)"
}

cmd_push() {
  if [[ ! -f "$PROVIDER_CONFIG" ]]; then log "Not configured."; return 1; fi
  local branch
  branch=$(python3 -c "import json;print(json.load(open('$PROVIDER_CONFIG'))['branch'])" 2>/dev/null || echo "main")

  local hostname_str profile_name
  hostname_str=$(hostname -s 2>/dev/null || echo "unknown")
  profile_name=$(get_profile_name)
  local profile_dir="$REPO_DIR/profiles/$profile_name"

  # Fetch latest from remote, reset to it
  _git fetch origin "$branch" --quiet 2>/dev/null || true
  _git reset --hard "origin/$branch" --quiet 2>/dev/null || true

  # Apply vault contents into profile subdirectory
  mkdir -p "$profile_dir/identity" "$profile_dir/knowledge"
  rsync -a --delete --exclude '.git' "$VAULT_DIR/identity/" "$profile_dir/identity/" 2>/dev/null || true
  rsync -a --delete "$VAULT_DIR/knowledge/" "$profile_dir/knowledge/" 2>/dev/null || true
  [[ -f "$VAULT_DIR/requirements.yaml" ]] && cp "$VAULT_DIR/requirements.yaml" "$profile_dir/"
  [[ -f "$VAULT_DIR/manifest.json" ]] && cp "$VAULT_DIR/manifest.json" "$profile_dir/"

  # Commit and push
  _git add -A
  if _git diff --cached --quiet 2>/dev/null; then
    log "No changes to push"
    return 0
  fi

  _git commit -m "vault sync $(timestamp) from $hostname_str [profile: $profile_name]" --quiet
  _git push origin "$branch" --quiet 2>/dev/null && log "Pushed to git (profile: $profile_name)" || log "Push failed"
}

cmd_pull() {
  if [[ ! -f "$PROVIDER_CONFIG" ]]; then log "Not configured."; return 1; fi
  local branch
  branch=$(python3 -c "import json;print(json.load(open('$PROVIDER_CONFIG'))['branch'])" 2>/dev/null || echo "main")

  local profile_name
  profile_name=$(get_profile_name)

  _git fetch origin "$branch" --quiet 2>/dev/null
  _git reset --hard "origin/$branch" --quiet 2>/dev/null || _git pull origin "$branch" --quiet 2>/dev/null

  local source_dir="$REPO_DIR/profiles/$profile_name"
  # Fallback for legacy (pre-profile) repos
  [[ ! -d "$source_dir" ]] && source_dir="$REPO_DIR"

  for f in identity/USER.md knowledge/MEMORY.md requirements.yaml manifest.json identity/instances.yaml; do
    [[ -f "$source_dir/$f" ]] && mkdir -p "$(dirname "$VAULT_DIR/$f")" && cp "$source_dir/$f" "$VAULT_DIR/$f"
  done
  [[ -d "$source_dir/knowledge/projects" ]] && mkdir -p "$VAULT_DIR/knowledge/projects" && \
    cp -r "$source_dir/knowledge/projects/"* "$VAULT_DIR/knowledge/projects/" 2>/dev/null || true

  [[ -f "$source_dir/requirements.yaml" ]] && cp "$source_dir/requirements.yaml" "$VAULT_DIR/.vault-requirements.yaml"
  log "Pulled from git (profile: $profile_name)"
}

cmd_list_profiles() {
  if [[ ! -d "$REPO_DIR/.git" ]]; then log "Not configured."; return 1; fi
  local branch
  branch=$(python3 -c "import json;print(json.load(open('$PROVIDER_CONFIG'))['branch'])" 2>/dev/null || echo "main")

  _git fetch origin "$branch" --quiet 2>/dev/null || true
  _git reset --hard "origin/$branch" --quiet 2>/dev/null || true

  local current_profile
  current_profile=$(get_profile_name)

  echo ""
  echo "Remote Profiles"
  echo "==============="
  if [[ -d "$REPO_DIR/profiles" ]]; then
    ls -1 "$REPO_DIR/profiles/" 2>/dev/null | while read -r p; do
      local marker=""
      [[ "$p" == "$current_profile" ]] && marker=" ← current"
      echo "  $p$marker"
    done
  else
    echo "  (no profiles yet — legacy single-vault format)"
  fi
  echo ""
}

cmd_test() {
  if [[ ! -d "$REPO_DIR/.git" ]]; then log "Not configured."; return 1; fi
  _git fetch --dry-run 2>/dev/null && log "Git remote reachable" || log "Cannot reach remote"
}

cmd_info() {
  if [[ -f "$PROVIDER_CONFIG" ]]; then
    local url branch
    url=$(python3 -c "import json;print(json.load(open('$PROVIDER_CONFIG'))['remote_url'])" 2>/dev/null)
    branch=$(python3 -c "import json;print(json.load(open('$PROVIDER_CONFIG'))['branch'])" 2>/dev/null)
    echo "  Remote: $url ($branch)"
    echo "  Profile: $(get_profile_name)"
    if [[ -d "$REPO_DIR/.git" ]]; then
      local count; count=$(_git rev-list --count HEAD 2>/dev/null || echo "0")
      echo "  Commits: $count"
    fi
  else echo "  Not configured"; fi
}

case "${1:-info}" in setup) cmd_setup;; push) cmd_push;; pull) cmd_pull;; test) cmd_test;; info) cmd_info;; list-profiles) cmd_list_profiles;; esac
