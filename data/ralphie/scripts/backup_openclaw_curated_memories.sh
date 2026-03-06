#!/usr/bin/env bash
set -euo pipefail

# backup_openclaw_curated_memories.sh
#
# Sync a *curated* allowlist of continuity files into a dedicated backup git repo,
# then commit+push *only if changed*.
#
# Option B support:
# - Always backs up curated workspace text (MEMORY.md, memory/*.md, SOUL/USER/etc.)
# - Optionally backs up selected OpenClaw files (openclaw.json*, skills/) based on config flags.
# - Optionally exports full Clawboard state (config/topics/tasks/logs + optional attachments).
#
# Config is read from:
#   $HOME/.openclaw/credentials/clawboard-memory-backup.json
# Fallback (optional):
#   $HOME/.openclaw/credentials/clawboard-memory-backup.env
#
# Auth methods:
# - authMethod=ssh (recommended): uses a GitHub Deploy Key (write access must be enabled in repo settings)
# - authMethod=pat (legacy): uses HTTPS + fine-grained PAT via GIT_ASKPASS

say() { printf "%s\n" "$*"; }
die() { say "ERROR: $*" >&2; exit 2; }

OPENCLAW_DIR="${OPENCLAW_DIR:-$HOME/.openclaw}"
CRED_JSON="$OPENCLAW_DIR/credentials/clawboard-memory-backup.json"
CRED_ENV="$OPENCLAW_DIR/credentials/clawboard-memory-backup.env"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
EXPORT_CLAWBOARD_HELPER="$SCRIPT_DIR/export_clawboard_backup.py"

need_cmd() {
  command -v "$1" >/dev/null 2>&1 || die "Missing required command: $1"
}

json_get() {
  # Usage: json_get <file> <jq-filter>
  local f="$1"; shift
  local filter="$1"; shift || true
  python3 - <<'PY' "$f" "$filter"
import json,sys
p=sys.argv[1]
filt=sys.argv[2]
with open(p,'r') as fh:
  d=json.load(fh)
# extremely tiny "jq-like" getter for dot paths: .a.b.c
if not filt.startswith('.'):
  print('')
  sys.exit(0)
keys=[k for k in filt.split('.') if k]
cur=d
try:
  for k in keys:
    cur=cur[k]
except Exception:
  cur=""
if cur is None:
  cur=""
print(cur if isinstance(cur,str) else json.dumps(cur))
PY
}

load_env_file() {
  local f="$1"
  [[ -f "$f" ]] || return 0
  # shellcheck disable=SC1090
  set -a; source "$f"; set +a
}

read_env_value() {
  local file_path="$1"
  local key="$2"
  local line
  [[ -f "$file_path" ]] || return 1
  line="$(awk -v key="$key" '
    $0 ~ "^[[:space:]]*" key "=" {
      print substr($0, index($0, "=") + 1)
    }
  ' "$file_path" | tail -n1)"
  line="${line//$'\r'/}"
  line="${line#"${line%%[![:space:]]*}"}"
  line="${line%"${line##*[![:space:]]}"}"
  line="${line%\"}"
  line="${line#\"}"
  line="${line%\'}"
  line="${line#\'}"
  [[ -n "$line" ]] || return 1
  printf "%s" "$line"
}

# --- Load config ---
if [[ -f "$CRED_JSON" ]]; then
  WORKSPACE_PATH="$(json_get "$CRED_JSON" '.workspacePath')"
  BACKUP_DIR="$(json_get "$CRED_JSON" '.backupDir')"
  REPO_URL="$(json_get "$CRED_JSON" '.repoUrl')"
  REPO_SSH_URL="$(json_get "$CRED_JSON" '.repoSshUrl')"
  AUTH_METHOD="$(json_get "$CRED_JSON" '.authMethod')"
  DEPLOY_KEY_PATH="$(json_get "$CRED_JSON" '.deployKeyPath')"
  GITHUB_USER="$(json_get "$CRED_JSON" '.githubUser')"
  GITHUB_PAT="$(json_get "$CRED_JSON" '.githubPat')"
  REMOTE_NAME="$(json_get "$CRED_JSON" '.remoteName')"
  BRANCH="$(json_get "$CRED_JSON" '.branch')"
  INCLUDE_OPENCLAW_CONFIG="$(json_get "$CRED_JSON" '.includeOpenclawConfig')"
  INCLUDE_OPENCLAW_SKILLS="$(json_get "$CRED_JSON" '.includeOpenclawSkills')"
  INCLUDE_CLAWBOARD_STATE="$(json_get "$CRED_JSON" '.includeClawboardState')"
  CLAWBOARD_DIR="$(json_get "$CRED_JSON" '.clawboardDir')"
  CLAWBOARD_API_URL="$(json_get "$CRED_JSON" '.clawboardApiUrl')"
  INCLUDE_CLAWBOARD_ATTACHMENTS="$(json_get "$CRED_JSON" '.includeClawboardAttachments')"
  INCLUDE_CLAWBOARD_ENV="$(json_get "$CRED_JSON" '.includeClawboardEnv')"
  CLAWBOARD_TOKEN="$(json_get "$CRED_JSON" '.clawboardToken')"
else
  load_env_file "$CRED_ENV"
  WORKSPACE_PATH="${WORKSPACE_PATH:-}"
  BACKUP_DIR="${BACKUP_DIR:-}"
  REPO_URL="${REPO_URL:-}"
  REPO_SSH_URL="${REPO_SSH_URL:-}"
  AUTH_METHOD="${AUTH_METHOD:-}"
  DEPLOY_KEY_PATH="${DEPLOY_KEY_PATH:-}"
  GITHUB_USER="${GITHUB_USER:-}"
  GITHUB_PAT="${GITHUB_PAT:-}"
  REMOTE_NAME="${REMOTE_NAME:-}"
  BRANCH="${BRANCH:-}"
  INCLUDE_OPENCLAW_CONFIG="${INCLUDE_OPENCLAW_CONFIG:-}"
  INCLUDE_OPENCLAW_SKILLS="${INCLUDE_OPENCLAW_SKILLS:-}"
  INCLUDE_CLAWBOARD_STATE="${INCLUDE_CLAWBOARD_STATE:-}"
  CLAWBOARD_DIR="${CLAWBOARD_DIR:-}"
  CLAWBOARD_API_URL="${CLAWBOARD_API_URL:-}"
  INCLUDE_CLAWBOARD_ATTACHMENTS="${INCLUDE_CLAWBOARD_ATTACHMENTS:-}"
  INCLUDE_CLAWBOARD_ENV="${INCLUDE_CLAWBOARD_ENV:-}"
  CLAWBOARD_TOKEN="${CLAWBOARD_BACKUP_TOKEN:-${CLAWBOARD_TOKEN:-}}"
fi

# Env file values override JSON for secrets/runtime configuration.
load_env_file "$CRED_ENV"
CLAWBOARD_TOKEN="${CLAWBOARD_BACKUP_TOKEN:-${CLAWBOARD_TOKEN:-}}"
CLAWBOARD_API_URL="${CLAWBOARD_BACKUP_API_URL:-${CLAWBOARD_API_URL:-}}"
CLAWBOARD_DIR="${CLAWBOARD_BACKUP_DIR:-${CLAWBOARD_DIR:-}}"

REMOTE_NAME="${REMOTE_NAME:-origin}"
BRANCH="${BRANCH:-main}"
AUTH_METHOD="${AUTH_METHOD:-ssh}"
CLAWBOARD_API_URL="${CLAWBOARD_API_URL:-http://localhost:8010}"

# bash 3.2 compatibility (macOS default /bin/bash): no ${var,,}
lc() { tr '[:upper:]' '[:lower:]' <<<"${1:-}"; }

# Booleans are stored as JSON true/false; our json_get returns a JSON string for non-strings.
# Accept: true/false/"true"/"false"/1/0/yes/no
as_bool() {
  local v="${1:-}"
  v="${v//\"/}"
  case "$(lc "$v")" in
    true|1|yes|y) return 0 ;;
    *) return 1 ;;
  esac
}

[[ -n "${WORKSPACE_PATH:-}" ]] || die "workspacePath not configured. Run setup-openclaw-memory-backup.sh first."
[[ -d "$WORKSPACE_PATH" ]] || die "workspacePath does not exist: $WORKSPACE_PATH"

[[ -n "${BACKUP_DIR:-}" ]] || die "backupDir not configured. Run setup-openclaw-memory-backup.sh first."

case "$(lc "${AUTH_METHOD:-}")" in
  ssh)
    [[ -n "${REPO_SSH_URL:-}" ]] || die "repoSshUrl not configured (needed for authMethod=ssh). Re-run setup."
    [[ -n "${DEPLOY_KEY_PATH:-}" ]] || die "deployKeyPath not configured (needed for authMethod=ssh). Re-run setup."
    [[ -f "$DEPLOY_KEY_PATH" ]] || die "deploy key not found: $DEPLOY_KEY_PATH"
    ;;
  pat)
    [[ -n "${REPO_URL:-}" ]] || die "repoUrl not configured (needed for authMethod=pat). Re-run setup."
    [[ -n "${GITHUB_USER:-}" ]] || die "githubUser not configured. Re-run setup."
    [[ -n "${GITHUB_PAT:-}" ]] || die "githubPat not configured. Re-run setup."
    ;;
  *)
    die "Unknown authMethod: ${AUTH_METHOD}. Expected 'ssh' or 'pat'."
    ;;
esac

need_cmd git
need_cmd rsync
need_cmd mktemp
need_cmd date
need_cmd python3

mkdir -p "$BACKUP_DIR"

# Avoid overlapping cron runs. If another backup is active, exit quietly.
LOCK_DIR="$BACKUP_DIR/.backup-lock"
if ! mkdir "$LOCK_DIR" >/dev/null 2>&1; then
  lock_pid="$(cat "$LOCK_DIR/pid" 2>/dev/null || true)"
  if [[ -n "${lock_pid:-}" ]] && kill -0 "$lock_pid" >/dev/null 2>&1; then
    exit 0
  fi
  rm -rf "$LOCK_DIR" >/dev/null 2>&1 || true
  mkdir "$LOCK_DIR" >/dev/null 2>&1 || exit 0
fi
printf "%s\n" "$$" > "$LOCK_DIR/pid"
trap 'rm -rf "$LOCK_DIR" >/dev/null 2>&1 || true' EXIT

# Ensure backup repo exists
if [[ ! -d "$BACKUP_DIR/.git" ]]; then
  (cd "$BACKUP_DIR" && git init -b "$BRANCH" >/dev/null)
fi

# Ensure remote is set
REMOTE_URL=""
if [[ "$(lc "${AUTH_METHOD:-}")" == "ssh" ]]; then
  REMOTE_URL="$REPO_SSH_URL"
else
  REMOTE_URL="$REPO_URL"
fi

if ! (cd "$BACKUP_DIR" && git remote get-url "$REMOTE_NAME" >/dev/null 2>&1); then
  (cd "$BACKUP_DIR" && git remote add "$REMOTE_NAME" "$REMOTE_URL")
else
  (cd "$BACKUP_DIR" && git remote set-url "$REMOTE_NAME" "$REMOTE_URL")
fi

# Ensure commits can be created in clean environments without global git identity.
if [[ -z "$(git -C "$BACKUP_DIR" config --get user.name || true)" ]]; then
  git -C "$BACKUP_DIR" config user.name "Clawboard Backup Bot"
fi
if [[ -z "$(git -C "$BACKUP_DIR" config --get user.email || true)" ]]; then
  git -C "$BACKUP_DIR" config user.email "clawboard-backup@localhost"
fi

# Make a staging subdir so we can delete removed files cleanly without nuking .git
STAGE_DIR="$BACKUP_DIR/.stage"
rm -rf "$STAGE_DIR"
mkdir -p "$STAGE_DIR"

# --- A) Curated workspace text (always) ---
# Note: do NOT use --delete when rsync'ing individual files into the same dest,
# or each call will delete what the previous call copied.
RSYNC_WORKSPACE=(
  "MEMORY.md"
  "USER.md"
  "SOUL.md"
  "AGENTS.md"
  "TOOLS.md"
  "IDENTITY.md"
  "HEARTBEAT.md"
  "memory"
)

for p in "${RSYNC_WORKSPACE[@]}"; do
  if [[ -e "$WORKSPACE_PATH/$p" ]]; then
    if [[ -d "$WORKSPACE_PATH/$p" ]]; then
      # directory
      rsync -a --prune-empty-dirs \
        --exclude ".DS_Store" \
        "$WORKSPACE_PATH/$p" \
        "$STAGE_DIR/" \
        >/dev/null
    else
      # file
      rsync -a --prune-empty-dirs \
        --exclude ".DS_Store" \
        "$WORKSPACE_PATH/$p" \
        "$STAGE_DIR/" \
        >/dev/null
    fi
  fi
done

# --- B) Selected OpenClaw files (optional) ---
if as_bool "${INCLUDE_OPENCLAW_CONFIG:-}"; then
  mkdir -p "$STAGE_DIR/openclaw"
  if [[ -f "$OPENCLAW_DIR/openclaw.json" ]]; then
    rsync -a "$OPENCLAW_DIR/openclaw.json" "$STAGE_DIR/openclaw/" >/dev/null
  fi
  # include backups if present (small, useful)
  shopt -s nullglob
  for f in "$OPENCLAW_DIR"/openclaw.json.bak*; do
    rsync -a "$f" "$STAGE_DIR/openclaw/" >/dev/null
  done
  shopt -u nullglob
fi

if as_bool "${INCLUDE_OPENCLAW_SKILLS:-}"; then
  if [[ -d "$OPENCLAW_DIR/skills" ]]; then
    mkdir -p "$STAGE_DIR/openclaw"
    rsync -a --delete --prune-empty-dirs \
      --exclude ".DS_Store" \
      "$OPENCLAW_DIR/skills/" \
      "$STAGE_DIR/openclaw/skills/" \
      >/dev/null
  fi
fi

# --- C) Full Clawboard state backup (optional) ---
if as_bool "${INCLUDE_CLAWBOARD_STATE:-}"; then
  [[ -f "$EXPORT_CLAWBOARD_HELPER" ]] || die "Missing exporter helper: $EXPORT_CLAWBOARD_HELPER"

  if [[ -n "${CLAWBOARD_DIR:-}" ]]; then
    # Expand "~" in a POSIX-safe way.
    case "$CLAWBOARD_DIR" in
      "~/"*) CLAWBOARD_DIR="$HOME/${CLAWBOARD_DIR#~/}" ;;
    esac
    [[ -d "$CLAWBOARD_DIR" ]] || die "clawboardDir does not exist: $CLAWBOARD_DIR"
  fi

  if [[ -z "${CLAWBOARD_TOKEN:-}" && -n "${CLAWBOARD_DIR:-}" && -f "$CLAWBOARD_DIR/.env" ]]; then
    CLAWBOARD_TOKEN="$(read_env_value "$CLAWBOARD_DIR/.env" "CLAWBOARD_TOKEN" || true)"
  fi
  [[ -n "${CLAWBOARD_TOKEN:-}" ]] || die "Clawboard token missing. Set CLAWBOARD_TOKEN in $CLAWBOARD_DIR/.env or CLAWBOARD_BACKUP_TOKEN in $CRED_ENV."

  CLAWBOARD_EXPORT_DIR="$STAGE_DIR/clawboard/export"
  mkdir -p "$CLAWBOARD_EXPORT_DIR"
  python3 "$EXPORT_CLAWBOARD_HELPER" \
    --api-base "$CLAWBOARD_API_URL" \
    --token "$CLAWBOARD_TOKEN" \
    --out-dir "$CLAWBOARD_EXPORT_DIR" \
    --include-raw \
    >/dev/null

  if as_bool "${INCLUDE_CLAWBOARD_ATTACHMENTS:-}"; then
    attachments_path=""
    if [[ -n "${CLAWBOARD_ATTACHMENTS_DIR:-}" ]]; then
      attachments_path="$CLAWBOARD_ATTACHMENTS_DIR"
    elif [[ -n "${CLAWBOARD_DIR:-}" && -f "$CLAWBOARD_DIR/.env" ]]; then
      attachments_path="$(read_env_value "$CLAWBOARD_DIR/.env" "CLAWBOARD_ATTACHMENTS_DIR" || true)"
    fi
    if [[ -z "$attachments_path" && -n "${CLAWBOARD_DIR:-}" ]]; then
      attachments_path="$CLAWBOARD_DIR/data/attachments"
    fi
    if [[ -n "$attachments_path" ]]; then
      case "$attachments_path" in
        "~/"*) attachments_path="$HOME/${attachments_path#~/}" ;;
      esac
      if [[ "${attachments_path#/}" == "$attachments_path" && -n "${CLAWBOARD_DIR:-}" ]]; then
        attachments_path="$CLAWBOARD_DIR/$attachments_path"
      fi
      if [[ -d "$attachments_path" ]]; then
        mkdir -p "$STAGE_DIR/clawboard/attachments"
        rsync -a --delete --prune-empty-dirs \
          --exclude ".DS_Store" \
          "$attachments_path/" \
          "$STAGE_DIR/clawboard/attachments/" \
          >/dev/null
      fi
    fi
  fi

  if as_bool "${INCLUDE_CLAWBOARD_ENV:-}" && [[ -n "${CLAWBOARD_DIR:-}" ]] && [[ -f "$CLAWBOARD_DIR/.env" ]]; then
    mkdir -p "$STAGE_DIR/clawboard"
    rsync -a "$CLAWBOARD_DIR/.env" "$STAGE_DIR/clawboard/" >/dev/null
  fi
fi

# Replace tracked content (keep .git)
rsync -a --delete --prune-empty-dirs \
  --exclude ".git" \
  --exclude ".stage" \
  "$STAGE_DIR/" \
  "$BACKUP_DIR/" \
  >/dev/null

rm -rf "$STAGE_DIR"

cd "$BACKUP_DIR"

if [[ -z "$(git status --porcelain)" ]]; then
  # Silent success: cron should not notify when there is nothing new.
  exit 0
fi

git add -A

ts="$(date -u +"%Y-%m-%d %H:%M:%SZ")"
scope="OpenClaw continuity (curated + selected)"
if as_bool "${INCLUDE_CLAWBOARD_STATE:-}"; then
  scope="$scope + Clawboard state"
fi
msg="Clawboard: auto backup $scope ($ts)"
if ! git commit -m "$msg" >/dev/null 2>&1; then
  if [[ -z "$(git status --porcelain)" ]]; then
    exit 0
  fi
  die "git commit failed"
fi

# Ensure branch exists locally
if ! git rev-parse --verify "$BRANCH" >/dev/null 2>&1; then
  git checkout -b "$BRANCH" >/dev/null
else
  git checkout "$BRANCH" >/dev/null
fi

# Push
if [[ "$(lc "${AUTH_METHOD:-}")" == "ssh" ]]; then
  # Use explicit key for this push so we don't depend on user-level ssh config.
  # Default: port 22 to github.com. If that fails (common on restrictive networks),
  # retry via ssh.github.com:443.
  export GIT_SSH_COMMAND="ssh -i $DEPLOY_KEY_PATH -o IdentitiesOnly=yes -o StrictHostKeyChecking=accept-new"

  set +e
  out="$(git push -u "$REMOTE_NAME" "$BRANCH" 2>&1)"
  code=$?

  if [[ $code -ne 0 ]]; then
    # Retry over port 443
    export GIT_SSH_COMMAND="ssh -i $DEPLOY_KEY_PATH -o IdentitiesOnly=yes -o StrictHostKeyChecking=accept-new -p 443 -o HostName=ssh.github.com"
    out2="$(git push -u "$REMOTE_NAME" "$BRANCH" 2>&1)"
    code2=$?
    if [[ $code2 -ne 0 ]]; then
      set -e
      say "$out" >&2
      say "--- retry over ssh.github.com:443 ---" >&2
      say "$out2" >&2
      die "git push failed (ssh). Confirm the Deploy Key was added AND 'Allow write access' is checked. If you're on a network blocking SSH, port 443 fallback may still be blocked."
    else
      set -e
      say "Backed up and pushed changes to $REPO_SSH_URL (via ssh.github.com:443)"
      exit 0
    fi
  fi
  set -e
  say "Backed up and pushed changes to $REPO_SSH_URL"
else
  # HTTPS + PAT via ephemeral askpass helper so we don't depend on OS keychains.
  ASKPASS="$(mktemp -t clawboard-git-askpass.XXXXXX)"
  chmod 700 "$ASKPASS"
  cat >"$ASKPASS" <<'SH'
#!/usr/bin/env bash
case "$1" in
  *Username*)
    printf "%s" "${GITHUB_USER}"
    ;;
  *Password*)
    printf "%s" "${GITHUB_PAT}"
    ;;
  *)
    printf "%s" "${GITHUB_PAT}"
    ;;
esac
SH

  export GIT_ASKPASS="$ASKPASS"
  export GIT_TERMINAL_PROMPT=0
  export GITHUB_USER
  export GITHUB_PAT

  set +e
  out="$(git push -u "$REMOTE_NAME" "$BRANCH" 2>&1)"
  code=$?
  set -e
  rm -f "$ASKPASS"

  if [[ $code -ne 0 ]]; then
    say "$out" >&2
    die "git push failed (pat)"
  fi
  say "Backed up and pushed changes to $REPO_URL"
fi
