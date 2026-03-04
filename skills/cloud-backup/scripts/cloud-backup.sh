#!/usr/bin/env bash
# OpenClaw Cloud Backup — back up ~/.openclaw locally and optionally to S3-compatible storage.
# Config: skills.entries.cloud-backup.config.* / .env.* in ~/.openclaw/openclaw.json
set -euo pipefail

# State dir: respect OPENCLAW_STATE_DIR, fall back to ~/.openclaw
OPENCLAW_STATE="${OPENCLAW_STATE_DIR:-$HOME/.openclaw}"
OPENCLAW_CONFIG="${OPENCLAW_CONFIG:-$OPENCLAW_STATE/openclaw.json}"
MAX_LOCAL=7  # hard cap on local archives regardless of retentionCount

# Snapshot denylist — excluded from 'backup full' in snapshot mode.
# Everything else under $OPENCLAW_STATE is included.
SNAPSHOT_DENY=(backups .cache .npm .local .config .cursor .codex
               logs completions delivery-queue media
               "*.bak" "*.bak-*" "*.bak.[0-9]*")

die()  { echo "ERROR: $*" >&2; exit 1; }
info() { echo ":: $*"; }
warn() { echo "WARN: $*" >&2; }
has()  { command -v "$1" >/dev/null 2>&1; }
need() { for b in "$@"; do has "$b" || die "missing: $b"; done; }

cfg() {
  has jq && [ -f "$OPENCLAW_CONFIG" ] || return 0
  jq -r ".skills.entries[\"cloud-backup\"].$1.$2 | if . == null then empty else tostring end" \
    "$OPENCLAW_CONFIG" 2>/dev/null || true
}

# --- config ---

load_config() {
  BUCKET="$(cfg config bucket)"
  REGION="$(cfg config region)";             REGION="${REGION:-us-east-1}"
  ENDPOINT="$(cfg config endpoint)"
  SOURCE="$OPENCLAW_STATE"
  BACKUPS="$SOURCE/backups"
  PREFIX="openclaw-backups/$(hostname -s 2>/dev/null || hostname)/"

  UPLOAD="$(cfg config upload)";             UPLOAD="${UPLOAD:-true}"
  ENCRYPT="$(cfg config encrypt)";           ENCRYPT="${ENCRYPT:-false}"
  KEEP="$(cfg config retentionCount)";       KEEP="${KEEP:-10}"
  DAYS="$(cfg config retentionDays)";        DAYS="${DAYS:-30}"
  : "${AWS_ACCESS_KEY_ID:=$(cfg env ACCESS_KEY_ID)}"
  : "${AWS_SECRET_ACCESS_KEY:=$(cfg env SECRET_ACCESS_KEY)}"
  : "${AWS_SESSION_TOKEN:=$(cfg env SESSION_TOKEN)}"
  : "${AWS_PROFILE:=$(cfg config profile)}"
  : "${GPG_PASSPHRASE:=$(cfg env GPG_PASSPHRASE)}"
  export AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY AWS_SESSION_TOKEN

  HAS_ACCESS_KEY=false
  HAS_SECRET_KEY=false
  HAS_KEY_PAIR=false
  PARTIAL_KEYS=false
  [ -n "$AWS_ACCESS_KEY_ID" ] && HAS_ACCESS_KEY=true
  [ -n "$AWS_SECRET_ACCESS_KEY" ] && HAS_SECRET_KEY=true
  if [ "$HAS_ACCESS_KEY" = "true" ] && [ "$HAS_SECRET_KEY" = "true" ]; then
    HAS_KEY_PAIR=true
  elif [ "$HAS_ACCESS_KEY" = "true" ] || [ "$HAS_SECRET_KEY" = "true" ]; then
    PARTIAL_KEYS=true
  fi

  CLOUD=false
  if [ "$PARTIAL_KEYS" != "true" ] && [ -n "$BUCKET" ] && has aws && { [ -n "$AWS_PROFILE" ] || [ "$HAS_KEY_PAIR" = "true" ]; }; then
    CLOUD=true
  fi

  mkdir -p "$BACKUPS" "$BACKUPS/_tmp"
}

s3() {
  local a=(aws)
  [ -n "$AWS_PROFILE" ] && a+=(--profile "$AWS_PROFILE")
  [ -n "$REGION" ]      && a+=(--region "$REGION")
  [ -n "$ENDPOINT" ]    && a+=(--endpoint-url "$ENDPOINT")
  "${a[@]}" s3 "$@"
}

# --- utilities ---

sha_cmd() { has sha256sum && echo sha256sum || { has shasum && echo "shasum -a 256"; } || die "need sha256sum"; }
sha_make()   { local d; d="$(dirname "$1")"; (cd "$d" && $(sha_cmd) "$(basename "$1")" > "$(basename "$1").sha256"); }
sha_check()  { [ -f "$1.sha256" ] || die "no checksum: $1.sha256"; local d; d="$(dirname "$1")"; (cd "$d" && $(sha_cmd) -c "$(basename "$1").sha256" >/dev/null) || die "checksum mismatch"; }

gpg_enc() {
  local o="$1.gpg"
  if [ -n "$GPG_PASSPHRASE" ]; then
    gpg --batch --yes --pinentry-mode loopback --passphrase "$GPG_PASSPHRASE" --symmetric --cipher-algo AES256 -o "$o" "$1"
  else
    gpg --symmetric --cipher-algo AES256 -o "$o" "$1"
  fi; echo "$o"
}
gpg_dec() {
  local o="${1%.gpg}"
  if [ -n "$GPG_PASSPHRASE" ]; then
    gpg --batch --yes --pinentry-mode loopback --passphrase "$GPG_PASSPHRASE" -o "$o" -d "$1"
  else
    gpg -o "$o" -d "$1"
  fi; echo "$o"
}

tar_safe() {
  local bad; bad="$(tar -tzf "$1" 2>/dev/null | grep -E '^/|^\.\.(\/|$)|/\.\.(\/|$)' || true)"
  [ -z "$bad" ] || { echo "$bad" >&2; die "unsafe paths in archive"; }
}

tar_supports_ignore_failed_read() {
  tar --help 2>/dev/null | grep -q -- '--ignore-failed-read'
}

safe_rm() {
  local p
  for p in "$@"; do
    [ -n "$p" ] || continue
    [ "$p" != "/" ] || die "refusing to delete root path"
    rm -f "$p"
  done
}

# List local archive files (sorted oldest first)
local_archives() {
  for f in "$BACKUPS"/openclaw_*.tar.gz "$BACKUPS"/openclaw_*.tar.gz.gpg; do
    [ -f "$f" ] && echo "$f"
  done | sort
}

# List logical local backup sets (dedup tar/gpg variants), oldest first.
local_backup_sets() {
  local f stem ts
  for f in "$BACKUPS"/openclaw_*.tar.gz "$BACKUPS"/openclaw_*.tar.gz.gpg; do
    [ -f "$f" ] || continue
    stem="${f%.gpg}"
    stem="${stem%.tar.gz}"
    ts="$(arc_ts "$stem")"
    [ -n "$ts" ] || continue
    printf '%s\t%s\n' "$ts" "$stem"
  done | sort -u | cut -f2-
}

# Timestamp from archive filename → YYYYMMDDHHMMSS
arc_ts() { basename "$1" | sed -n 's/.*_\([0-9]\{8\}_[0-9]\{6\}\)_.*/\1/p' | tr -d _; }

# --- commands ---

cmd_backup() {
  local mode="${1:-full}"
  case "$mode" in full|workspace|skills|settings) ;; *) die "mode: full, workspace, skills, settings" ;; esac
  need tar; [ -d "$SOURCE" ] || die "source missing: $SOURCE"

  if [ "$ENCRYPT" != "true" ]; then
    warn "Encryption is disabled — backup archive will be stored in plaintext."
    warn "To enable encryption: set config.encrypt=true and env.GPG_PASSPHRASE."
  fi

  # Prevent concurrent runs
  LOCKDIR="$BACKUPS/_lock"
  mkdir "$LOCKDIR" 2>/dev/null || die "backup already running (lock: $LOCKDIR)"
  # Controlled lifecycle: this skill owns backup-manifest.json for each run.
  trap 'rmdir "$LOCKDIR" 2>/dev/null || true; rm -f "$SOURCE/backup-manifest.json"' EXIT

  local ts host arc payload
  ts="$(date +%Y%m%d_%H%M%S)"
  host="$(hostname -s 2>/dev/null || hostname)"
  arc="$BACKUPS/openclaw_${mode}_${ts}_${host//[^a-zA-Z0-9._-]/_}.tar.gz"

  # Embed manifest in archive
  printf '{"v":1,"mode":"%s","ts":"%s","host":"%s","os":"%s"}\n' \
    "$mode" "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$host" "${OSTYPE:-unknown}" \
    > "$SOURCE/backup-manifest.json"

  if [ "$mode" = "full" ]; then
    # Snapshot: tar entire state dir minus denylist
    local -a ex=()
    for x in "${SNAPSHOT_DENY[@]}"; do ex+=(--exclude="$x"); done
    info "Creating $mode snapshot"
    if tar_supports_ignore_failed_read; then
      tar -czf "$arc" -C "$SOURCE" --ignore-failed-read "${ex[@]}" .
    else
      warn "tar lacks --ignore-failed-read; proceeding without it"
      tar -czf "$arc" -C "$SOURCE" "${ex[@]}" .
    fi
  else
    # Allowlist: specific files/dirs only (workspace, skills, settings)
    local -a cands paths=()
    case "$mode" in
      workspace) cands=(openclaw.json settings.json settings.local.json projects.json skills commands mcp contexts templates modules workspace) ;;
      skills)    cands=(skills commands) ;;
      settings)  cands=(openclaw.json settings.json settings.local.json projects.json mcp) ;;
    esac
    for c in "${cands[@]}"; do [ -e "$SOURCE/$c" ] && paths+=("$c"); done
    [ ${#paths[@]} -gt 0 ] || die "nothing to back up ($mode)"
    info "Creating $mode backup (${#paths[@]} items)"
    tar -czf "$arc" -C "$SOURCE" --exclude=backups "${paths[@]}" backup-manifest.json
  fi
  rm -f "$SOURCE/backup-manifest.json"
  payload="$arc"

  if [ "$ENCRYPT" = "true" ]; then
    need gpg
    info "Encrypting"
    payload="$(gpg_enc "$arc")"
    safe_rm "$arc" "$arc.sha256"
  fi
  sha_make "$payload"

  if [ "$UPLOAD" = "true" ] && [ "$CLOUD" = "true" ]; then
    info "Uploading to s3://$BUCKET/$PREFIX"
    s3 cp "$payload" "s3://$BUCKET/$PREFIX$(basename "$payload")"
    s3 cp "$payload.sha256" "s3://$BUCKET/$PREFIX$(basename "$payload").sha256"
    info "Backup complete: $payload"
    info "Uploaded to: s3://$BUCKET/$PREFIX$(basename "$payload")"
  elif [ "$UPLOAD" != "false" ] && [ "$CLOUD" != "true" ]; then
    info "Backup complete: $payload"
    warn "Cloud storage is not configured — backup is local only."
  else
    info "Backup complete: $payload"
  fi
}

cmd_list() {
  info "Local ($BACKUPS):"
  local f count=0
  while IFS= read -r f; do
    echo "  $(du -h "$f" | cut -f1)  $(basename "$f")"
    count=$((count + 1))
  done < <(local_archives)
  [ "$count" -gt 0 ] || echo "  (none)"

  if [ "$CLOUD" = "true" ]; then
    echo ""; info "Remote (s3://$BUCKET/$PREFIX):"
    s3 ls "s3://$BUCKET/$PREFIX" --recursive
  fi
}

cmd_cleanup() {
  local deleted=0

  # Local: keep min(KEEP, MAX_LOCAL) newest logical backup sets
  local cap=$KEEP
  [ "$cap" -gt "$MAX_LOCAL" ] && cap=$MAX_LOCAL
  local -a sets=()
  while IFS= read -r f; do sets+=("$f"); done < <(local_backup_sets)
  if [ ${#sets[@]} -gt "$cap" ]; then
    local n=$(( ${#sets[@]} - cap ))
    info "Pruning $n local backup set(s) (keep $cap)"
    local stem
    for ((i=0; i<n; i++)); do
      stem="${sets[$i]}"
      safe_rm \
        "$stem.tar.gz" "$stem.tar.gz.sha256" \
        "$stem.tar.gz.gpg" "$stem.tar.gz.gpg.sha256"
      deleted=$((deleted + 1))
    done
  fi

  # Remote: count + age retention
  if [ "$CLOUD" = "true" ]; then
    local tmp="$BACKUPS/_tmp/ls-$$.txt"
    s3 ls "s3://$BUCKET/$PREFIX" --recursive > "$tmp"
    local -a rk=()
    while read -r _ _ _ key; do
      case "$key" in *.tar.gz|*.tar.gz.gpg) rk+=("$key") ;; esac
    done < "$tmp"; rm -f "$tmp"

    # By count
    if [ ${#rk[@]} -gt "$KEEP" ]; then
      local n=$(( ${#rk[@]} - KEEP ))
      info "Pruning $n remote archive(s) (keep $KEEP)"
      for ((i=0; i<n; i++)); do
        s3 rm "s3://$BUCKET/${rk[$i]}"; s3 rm "s3://$BUCKET/${rk[$i]}.sha256" 2>/dev/null || true
        deleted=$((deleted + 1))
      done
    fi

    # By age
    if [ "$DAYS" -gt 0 ]; then
      local cutoff=""
      if date -d "now" >/dev/null 2>&1; then cutoff="$(date -d "$DAYS days ago" +%Y%m%d%H%M%S)"
      elif date -v-1d >/dev/null 2>&1; then cutoff="$(date -v-${DAYS}d +%Y%m%d%H%M%S)"; fi
      if [ -n "$cutoff" ]; then
        for key in "${rk[@]}"; do
          local ts; ts="$(arc_ts "$key")"; [ -n "$ts" ] || continue
          if [ "$ts" -lt "$cutoff" ]; then
            s3 rm "s3://$BUCKET/$key"; s3 rm "s3://$BUCKET/$key.sha256" 2>/dev/null || true
            deleted=$((deleted + 1))
          fi
        done
      fi
    fi
  fi

  info "Cleanup done. Deleted $deleted."
}

cmd_restore() {
  local name="$1" dry="$2" yes="$3"
  [ -n "$name" ] || die "restore needs a backup name (run 'list' first)"
  need tar

  local src=""
  if [ -f "$BACKUPS/$name" ]; then
    src="$BACKUPS/$name"; info "Restoring from local"
  elif [ "$CLOUD" = "true" ]; then
    local key="$name"; [[ "$key" == */* ]] || key="${PREFIX}${key}"
    local dir="$BACKUPS/_tmp/restore-$$"; mkdir -p "$dir"
    src="$dir/$(basename "$key")"
    info "Downloading s3://$BUCKET/$key"
    s3 cp "s3://$BUCKET/$key" "$src"
    s3 cp "s3://$BUCKET/$key.sha256" "$src.sha256"
  else
    die "'$name' not found locally and cloud not configured"
  fi

  sha_check "$src"
  local ext="$src"
  case "$src" in *.gpg) need gpg; info "Decrypting"; ext="$(gpg_dec "$src")" ;; esac
  tar_safe "$ext"

  if [ "$dry" = "true" ]; then info "Dry run:"; tar -tzf "$ext"; return; fi

  if [ "$yes" != "true" ]; then
    [ -t 0 ] || die "non-interactive restore needs --yes"
    printf "Overwrite files in %s? [y/N] " "$SOURCE"; read -r ans
    case "$ans" in [Yy]*) ;; *) info "Cancelled."; return ;; esac
  fi

  tar -xzf "$ext" -C "$SOURCE" --no-same-owner --no-same-permissions
  info "Restored to $SOURCE"
}

cmd_status() {
  cat <<EOF
OpenClaw Cloud Backup

Config:  $OPENCLAW_CONFIG
Source:  $SOURCE
Backups: $BACKUPS

Settings: upload=$UPLOAD  encrypt=$ENCRYPT  keep=$KEEP  days=$DAYS  local-cap=$MAX_LOCAL
EOF

  if [ "$ENCRYPT" != "true" ]; then
    warn "Encryption is disabled — backups are plaintext until config.encrypt=true."
  fi

  if [ "$UPLOAD" = "true" ] || [ -n "$BUCKET" ]; then
    echo ""
    echo "Cloud: bucket=$BUCKET  region=$REGION  endpoint=${ENDPOINT:-<default>}"
    if [ -n "$AWS_PROFILE" ]; then echo "Credentials: profile=$AWS_PROFILE"
    elif [ "$HAS_KEY_PAIR" = "true" ]; then echo "Credentials: key=${AWS_ACCESS_KEY_ID:0:4}...${AWS_ACCESS_KEY_ID: -4}"
    elif [ "$PARTIAL_KEYS" = "true" ]; then echo "Credentials: partial key config (need ACCESS_KEY_ID + SECRET_ACCESS_KEY)"
    else echo "Credentials: <not set>"; fi
    echo "Cloud ready: $CLOUD"
    [ "$PARTIAL_KEYS" = "true" ] && warn "Partial cloud credentials detected; set both ACCESS_KEY_ID and SECRET_ACCESS_KEY or use profile."
  else
    echo ""; echo "Mode: local-only"
  fi

  echo ""
  local bins=(bash tar jq)
  { [ "$UPLOAD" = "true" ] || [ -n "$BUCKET" ]; } && bins+=(aws)
  [ "$ENCRYPT" = "true" ] && bins+=(gpg)
  for b in "${bins[@]}"; do
    has "$b" && echo "  $b: $(command -v "$b")" || echo "  $b: NOT FOUND"
  done
}

cmd_setup() {
  cat <<'EOF'
OpenClaw Cloud Backup Setup

Local-only (no cloud needed):
  openclaw config patch 'skills.entries.cloud-backup.config.upload=false'

With cloud upload:
  openclaw config patch 'skills.entries.cloud-backup.config.bucket="my-bucket"'
  openclaw config patch 'skills.entries.cloud-backup.config.endpoint="https://..."'
  openclaw config patch 'skills.entries.cloud-backup.env.ACCESS_KEY_ID="..."'
  openclaw config patch 'skills.entries.cloud-backup.env.SECRET_ACCESS_KEY="..."'

Or ask your agent: "Set up cloud-backup with Cloudflare R2" (etc.)
EOF
  echo ""; cmd_status

  if [ "$CLOUD" = "true" ]; then
    echo ""; echo "Testing connection..."
    s3 ls "s3://$BUCKET/" --max-items 1 >/dev/null 2>&1 \
      && echo "✓ Connected" || echo "✗ Failed — check credentials"
  fi
}

# --- main ---

cmd="${1:-help}"; shift || true
load_config

case "$cmd" in
  backup)  cmd_backup "${1:-full}" ;;
  list)    cmd_list ;;
  cleanup) cmd_cleanup ;;
  restore)
    name="${1:-}"; shift || true
    dry=false; yes=false
    for a in "$@"; do case "$a" in --dry-run) dry=true ;; --yes) yes=true ;; *) die "unknown: $a" ;; esac; done
    cmd_restore "$name" "$dry" "$yes" ;;
  status)  cmd_status ;;
  setup)   cmd_setup ;;
  help|-h|--help)
    echo "Usage: $(basename "$0") <backup|list|restore|cleanup|status|setup>"
    echo "  backup [full|workspace|skills|settings]  Create backup (default: full)"
    echo "  list                               List local (and cloud) backups"
    echo "  restore <name> [--dry-run] [--yes] Restore from local or cloud"
    echo "  cleanup                            Prune old local + remote backups"
    echo "  status                             Show config and deps"
    echo "  setup                              Setup guide + connection test" ;;
  *) die "unknown: $cmd" ;;
esac
