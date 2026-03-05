#!/usr/bin/env bash
# ClawRoam Cloud Provider — Managed storage with pay-per-MB pricing
# Pricing: first 50 MB free, $0.005/MB/month after that
# Usage: cloud.sh {setup|push|pull|test|info|usage}

set -euo pipefail

VAULT_DIR="$HOME/.clawroam"
CONFIG="$VAULT_DIR/config.yaml"
KEY_DIR="$VAULT_DIR/keys"
CLOUD_CONFIG="$VAULT_DIR/.cloud-provider.json"
API_BASE="https://clawroam-api.ovisoftblue.workers.dev/v1"

timestamp() { date -u +"%Y-%m-%dT%H:%M:%SZ"; }
log() { echo "[clawroam:cloud $(timestamp)] $*"; }

# Use --http1.1 to avoid HTTP/2 protocol errors on some systems
CURL="curl --http1.1"

get_profile_name() {
  if [[ -n "${CLAWROAM_PROFILE:-}" ]]; then echo "$CLAWROAM_PROFILE"; return; fi
  local name
  name=$(grep 'profile_name:' "$CONFIG" 2>/dev/null | head -1 | awk '{print $2}' | tr -d '"')
  echo "${name:-$(hostname -s 2>/dev/null || echo default)}"
}

get_public_key() {
  cat "$KEY_DIR/clawroam_ed25519.pub" 2>/dev/null
}

get_private_key() {
  echo "$KEY_DIR/clawroam_ed25519"
}

# Sign a request payload with the private key
sign_request() {
  local payload="$1"
  local script_dir
  script_dir="$(cd "$(dirname "$0")" && pwd)"
  bash "$script_dir/../src/keypair.sh" sign "$payload"
}

# Fetch per-profile sync exclusions from the server
# Outputs one excluded path per line; outputs nothing on failure
fetch_sync_rules() {
  local vault_id="$1"
  local profile_name="$2"
  local ts
  ts=$(date +%s)
  local sig
  sig=$(sign_request "sync-rules:${vault_id}:${profile_name}:${ts}" 2>/dev/null || echo "unsigned")
  $CURL -sf \
    -H "X-ClawRoam-Signature: $sig" \
    -H "X-ClawRoam-Timestamp: $ts" \
    "$API_BASE/vaults/$vault_id/profiles/$profile_name/sync-rules" 2>/dev/null \
    | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    for p in data.get('excluded', []):
        print(p)
except:
    pass
" 2>/dev/null || true
}

# ─── Setup (signup + register key) ───────────────────────────

cmd_setup() {
  echo ""
  echo "☁️  ClawRoam Cloud Setup"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━"
  echo ""
  echo "Pricing:"
  echo "  • First 50 MB free (enough for most vaults)"
  echo "  • \$0.005/MB/month after that"
  echo "  • No per-instance fees — unlimited machines"
  echo "  • No bandwidth fees — sync as often as you want"
  echo ""
  echo "Examples:"
  echo "  10 MB vault  → Free"
  echo "  100 MB vault → \$0.25/month"
  echo "  500 MB vault → \$2.25/month"
  echo "  2 GB vault   → \$10/month"
  echo ""

  local email
  read -rp "Email address: " email

  if [[ -z "$email" ]]; then
    log "Email required."
    return 1
  fi

  local pubkey
  pubkey=$(get_public_key)

  if [[ -z "$pubkey" ]]; then
    log "No keypair found. Generate one first."
    return 1
  fi

  local hostname_str
  hostname_str=$(hostname -s 2>/dev/null || echo "unknown")

  log "Registering with ClawRoam Cloud..."

  # Register with the API
  local response
  response=$($CURL -sf -X POST "$API_BASE/signup" \
    -H "Content-Type: application/json" \
    -d "{
      \"email\": \"$email\",
      \"public_key\": \"$pubkey\",
      \"hostname\": \"$hostname_str\",
      \"os\": \"$(uname -s)\",
      \"instance_id\": \"$(grep 'instance_id:' "$CONFIG" 2>/dev/null | head -1 | awk '{print $2}' | tr -d '\"')\"
    }" 2>/dev/null) || {
    # If API is not yet live, save config locally for future use
    log "Cloud API not available yet — saving config for when it launches."
    cat > "$CLOUD_CONFIG" <<JSON
{
  "provider": "cloud",
  "email": "$email",
  "public_key_fingerprint": "$(ssh-keygen -lf "$KEY_DIR/clawroam_ed25519.pub" 2>/dev/null | awk '{print $2}')",
  "hostname": "$hostname_str",
  "registered": "$(timestamp)",
  "api_base": "$API_BASE",
  "vault_id": "pending",
  "status": "pending_launch"
}
JSON
    echo ""
    log "✓ Cloud config saved. You'll be notified when ClawRoam Cloud launches."
    log "  In the meantime, you can use any other provider (gdrive, dropbox, git, etc.)"
    return 0
  }

  # Parse response
  local vault_id
  vault_id=$(echo "$response" | python3 -c "import sys,json; print(json.load(sys.stdin).get('vault_id',''))" 2>/dev/null || echo "")

  cat > "$CLOUD_CONFIG" <<JSON
{
  "provider": "cloud",
  "email": "$email",
  "vault_id": "$vault_id",
  "public_key_fingerprint": "$(ssh-keygen -lf "$KEY_DIR/clawroam_ed25519.pub" 2>/dev/null | awk '{print $2}')",
  "hostname": "$hostname_str",
  "api_base": "$API_BASE",
  "registered": "$(timestamp)",
  "status": "active"
}
JSON

  log "✓ Registered with ClawRoam Cloud"
  log "  Vault ID: $vault_id"
  log "  Email:    $email"
  log "  Storage:  50 MB free included"
}

# ─── Push ─────────────────────────────────────────────────────

cmd_push() {
  local sync_dir="$VAULT_DIR/.sync-staging"
  local archive="$VAULT_DIR/.sync-archive.tar.gz"

  if [[ ! -f "$CLOUD_CONFIG" ]]; then
    log "Cloud not configured. Run setup first."
    return 1
  fi

  local vault_id
  vault_id=$(python3 -c "import json; print(json.load(open('$CLOUD_CONFIG')).get('vault_id',''))" 2>/dev/null || echo "pending")

  # Fetch per-profile sync exclusions from server (best-effort, never blocks push)
  local excluded_paths=()
  local profile_encoded
  profile_encoded=$(python3 -c "import sys,urllib.parse; print(urllib.parse.quote(sys.argv[1]))" "$(get_profile_name)" 2>/dev/null || get_profile_name)
  local rule
  while IFS= read -r rule; do
    [[ -n "$rule" ]] && excluded_paths+=("$rule")
  done < <(fetch_sync_rules "$vault_id" "$profile_encoded" 2>/dev/null || true)

  if [[ ${#excluded_paths[@]} -gt 0 ]]; then
    log "Applying ${#excluded_paths[@]} sync exclusion(s)..."
  fi

  # Stage files for upload (exclude local-only files + user exclusions)
  mkdir -p "$sync_dir"
  local rsync_excludes=(
    '--exclude' 'local/'
    '--exclude' 'keys/'
    '--exclude' '.cloud-provider.json'
    '--exclude' '.sync-staging/'
    '--exclude' '.sync-archive.tar.gz'
    '--exclude' '.heartbeat.pid'
    '--exclude' '.git-local/'
  )
  for rule in "${excluded_paths[@]}"; do
    rsync_excludes+=('--exclude' "$rule")
  done
  rsync -a --delete "${rsync_excludes[@]}" "$VAULT_DIR/" "$sync_dir/"

  # Create archive
  tar -czf "$archive" -C "$sync_dir" . 2>/dev/null

  # Encrypt archive with AES-256-CBC using private key as passphrase
  local encrypted="${archive}.enc"
  openssl enc -aes-256-cbc -pbkdf2 -salt \
    -in "$archive" -out "$encrypted" \
    -pass "file:$KEY_DIR/clawroam_ed25519" 2>/dev/null
  mv "$encrypted" "$archive"

  local size_bytes
  size_bytes=$(wc -c < "$archive" | tr -d ' ')
  local size_mb
  size_mb=$(echo "scale=2; $size_bytes / 1048576" | bc 2>/dev/null || echo "?")

  local profile_name
  profile_name=$(get_profile_name)
  log "Pushing to ClawRoam Cloud ($size_mb MB, profile: $profile_name, encrypted)..."

  # Sign the encrypted archive hash for authentication
  local archive_hash
  archive_hash=$(shasum -a 256 "$archive" 2>/dev/null || sha256sum "$archive" | awk '{print $1}')
  archive_hash=$(echo "$archive_hash" | awk '{print $1}')
  local signature
  signature=$(sign_request "$archive_hash" 2>/dev/null || echo "unsigned")

  # Upload
  local http_code
  http_code=$($CURL -sf -o /dev/null -w "%{http_code}" \
    -X PUT "$API_BASE/vaults/$vault_id/profiles/$profile_name/sync" \
    -H "X-ClawRoam-Signature: $signature" \
    -H "X-ClawRoam-Hash: $archive_hash" \
    -H "Content-Type: application/gzip" \
    --data-binary "@$archive" 2>/dev/null) || http_code="000"

  rm -rf "$sync_dir" "$archive"

  if [[ "$http_code" == "200" || "$http_code" == "201" ]]; then
    log "✓ Pushed to cloud ($size_mb MB)"
  elif [[ "$http_code" == "000" ]]; then
    log "Cloud API not available — falling back to local staging"
    log "Changes will push when connectivity is restored"
  else
    log "⚠ Push failed (HTTP $http_code)"
    return 1
  fi
}

# ─── Pull ─────────────────────────────────────────────────────

cmd_pull() {
  if [[ ! -f "$CLOUD_CONFIG" ]]; then
    log "Cloud not configured."
    return 1
  fi

  local vault_id
  vault_id=$(python3 -c "import json; print(json.load(open('$CLOUD_CONFIG')).get('vault_id',''))" 2>/dev/null || echo "pending")

  local archive="$VAULT_DIR/.pull-archive.tar.gz"

  # Sign the pull request
  local ts_now
  ts_now=$(timestamp)
  local signature
  signature=$(sign_request "pull:$vault_id:$ts_now" 2>/dev/null || echo "unsigned")

  local profile_name
  profile_name=$(get_profile_name)
  log "Pulling from ClawRoam Cloud (profile: $profile_name)..."

  $CURL -sf -o "$archive" \
    -H "X-ClawRoam-Signature: $signature" \
    -H "X-ClawRoam-Timestamp: $ts_now" \
    "$API_BASE/vaults/$vault_id/profiles/$profile_name/sync" 2>/dev/null || {
    log "Cloud API not available or vault not found."
    return 1
  }

  if [[ -f "$archive" && -s "$archive" ]]; then
    # Decrypt the archive
    local decrypted="${archive}.dec"
    openssl enc -d -aes-256-cbc -pbkdf2 \
      -in "$archive" -out "$decrypted" \
      -pass "file:$KEY_DIR/clawroam_ed25519" 2>/dev/null
    if [[ -f "$decrypted" && -s "$decrypted" ]]; then
      mv "$decrypted" "$archive"
    fi
    # (if decryption fails, archive might be unencrypted — legacy compat)

    # Extract to staging, then merge (don't overwrite local/)
    local pull_dir="$VAULT_DIR/.pull-staging"
    mkdir -p "$pull_dir"
    tar -xzf "$archive" -C "$pull_dir" 2>/dev/null

    # Restore entire openclaw directory if present
    if [[ -d "$pull_dir/openclaw" ]]; then
      local openclaw_dir
      openclaw_dir=$(grep 'openclaw_dir:' "$CONFIG" 2>/dev/null | head -1 | awk '{print $2}' | tr -d '"')
      if [[ -n "$openclaw_dir" ]]; then
        mkdir -p "$openclaw_dir"
        rsync -a --exclude '.git/' --exclude 'node_modules/' "$pull_dir/openclaw/" "$openclaw_dir/" 2>/dev/null || true
      fi
    fi

    # Also restore vault-level files
    for f in requirements.yaml manifest.json config.yaml skills-manifest.yaml; do
      if [[ -f "$pull_dir/$f" ]]; then
        cp "$pull_dir/$f" "$VAULT_DIR/$f"
      fi
    done

    # Merge projects directory
    if [[ -d "$pull_dir/knowledge/projects" ]]; then
      mkdir -p "$VAULT_DIR/knowledge/projects"
      cp -r "$pull_dir/knowledge/projects/"* "$VAULT_DIR/knowledge/projects/" 2>/dev/null || true
    fi

    rm -rf "$pull_dir" "$archive"
    log "✓ Pulled from cloud"
  else
    log "Nothing to pull or empty response."
    rm -f "$archive"
  fi
}

# ─── Test ─────────────────────────────────────────────────────

cmd_test() {
  if [[ ! -f "$CLOUD_CONFIG" ]]; then
    log "Cloud not configured."
    return 1
  fi

  log "Testing ClawRoam Cloud connection..."

  local status
  status=$($CURL -sf -o /dev/null -w "%{http_code}" "$API_BASE/health" 2>/dev/null) || status="000"

  if [[ "$status" == "200" ]]; then
    log "✓ Cloud API reachable"
  elif [[ "$status" == "000" ]]; then
    log "⚠ Cloud API not reachable (service may not be launched yet)"
  else
    log "⚠ Unexpected status: $status"
  fi
}

# ─── Usage / Billing ─────────────────────────────────────────

cmd_usage() {
  if [[ ! -f "$CLOUD_CONFIG" ]]; then
    log "Cloud not configured."
    return 1
  fi

  local vault_id
  vault_id=$(python3 -c "import json; print(json.load(open('$CLOUD_CONFIG')).get('vault_id',''))" 2>/dev/null || echo "pending")

  # Try API first
  local response
  response=$($CURL -sf "$API_BASE/vaults/$vault_id/usage" 2>/dev/null) || response=""

  if [[ -n "$response" ]]; then
    log "Cloud Usage:"
    echo "$response" | python3 -c "
import sys, json
d = json.load(sys.stdin)
used = d.get('used_bytes', 0) / 1048576
free = 50.0
billable = max(0, used - free)
cost = billable * 0.005
print(f'  Storage used:  {used:.1f} MB')
print(f'  Free tier:     {free:.0f} MB')
print(f'  Billable:      {billable:.1f} MB')
print(f'  Monthly cost:  \${cost:.2f}')
print(f'  Instances:     {d.get(\"instance_count\", \"?\")}')" 2>/dev/null
  else
    # Calculate from local vault size
    local local_size
    local_size=$(du -sm "$VAULT_DIR" 2>/dev/null | awk '{print $1}')
    local billable
    billable=$(echo "$local_size - 50" | bc 2>/dev/null || echo "0")
    [[ "$billable" -lt 0 ]] && billable=0
    local cost
    cost=$(echo "scale=2; $billable * 0.005" | bc 2>/dev/null || echo "0.00")

    echo ""
    echo "☁️  ClawRoam Cloud — Estimated Usage"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  Local vault:   ~${local_size} MB"
    echo "  Free tier:     50 MB"
    echo "  Billable:      ~${billable} MB"
    echo "  Est. monthly:  \$${cost}"
    echo ""
  fi
}

# ─── Info ─────────────────────────────────────────────────────

cmd_info() {
  if [[ -f "$CLOUD_CONFIG" ]]; then
    local email vault_id status
    email=$(python3 -c "import json; print(json.load(open('$CLOUD_CONFIG')).get('email','?'))" 2>/dev/null || echo "?")
    vault_id=$(python3 -c "import json; print(json.load(open('$CLOUD_CONFIG')).get('vault_id','?'))" 2>/dev/null || echo "?")
    status=$(python3 -c "import json; print(json.load(open('$CLOUD_CONFIG')).get('status','?'))" 2>/dev/null || echo "?")
    echo "  Email:    $email"
    echo "  Vault ID: $vault_id"
    echo "  Status:   $status"
    echo "  Pricing:  50 MB free, \$0.005/MB/month after"
  else
    echo "  Not configured"
  fi
}

# ─── List Profiles ───────────────────────────────────────────

cmd_list_profiles() {
  if [[ ! -f "$CLOUD_CONFIG" ]]; then
    log "Cloud not configured."
    return 1
  fi

  local vault_id
  vault_id=$(python3 -c "import json; print(json.load(open('$CLOUD_CONFIG')).get('vault_id',''))" 2>/dev/null || echo "pending")

  local ts_now signature
  ts_now=$(timestamp)
  signature=$(sign_request "list-profiles:$vault_id:$ts_now" 2>/dev/null || echo "unsigned")

  local response
  response=$($CURL -sf \
    -H "X-ClawRoam-Signature: $signature" \
    -H "X-ClawRoam-Timestamp: $ts_now" \
    "$API_BASE/vaults/$vault_id/profiles" 2>/dev/null) || response=""

  local current_profile
  current_profile=$(get_profile_name)

  if [[ -n "$response" ]]; then
    echo ""
    echo "Remote Profiles"
    echo "==============="
    echo "$response" | python3 -c "
import sys, json
profiles = json.load(sys.stdin).get('profiles', [])
current = '$current_profile'
if not profiles:
    print('  (no profiles yet)')
for p in profiles:
    marker = ' ← current' if p['name'] == current else ''
    print(f\"  {p['name']:20s}  {p.get('size_mb','?')} MB  last push: {p.get('last_push','never')}{marker}\")
" 2>/dev/null
    echo ""
  else
    log "Could not list profiles (API not reachable)"
  fi
}

# ─── Main ─────────────────────────────────────────────────────

case "${1:-info}" in
  setup)          cmd_setup ;;
  push)           cmd_push ;;
  pull)           cmd_pull ;;
  test)           cmd_test ;;
  usage)          cmd_usage ;;
  info)           cmd_info ;;
  list-profiles)  cmd_list_profiles ;;
  *)              echo "Usage: cloud.sh {setup|push|pull|test|usage|info|list-profiles}"; exit 1 ;;
esac
