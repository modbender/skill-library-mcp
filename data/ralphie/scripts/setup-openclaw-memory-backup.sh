#!/usr/bin/env bash
set -euo pipefail

# setup-openclaw-memory-backup.sh
#
# Interactive setup:
# - Detect OpenClaw workspace path from ~/.openclaw/openclaw.json
# - (Optional) Create a new private GitHub repo via `gh` (if available/auth'd)
# - Prefer GitHub Deploy Key (SSH) for auth (recommended)
#   - Generates a dedicated SSH keypair
#   - Prints instructions to add it as a Deploy Key (WRITE access reminder)
#   - Saves key path in ~/.openclaw/credentials/clawboard-memory-backup.env
# - Writes config to ~/.openclaw/credentials/clawboard-memory-backup.json (0600)
# - Optionally includes full Clawboard state export + attachment files in each backup run
# - Optionally installs an OpenClaw cron job (agentTurn) to run backup every 15m

say() { printf "%s\n" "$*"; }
die() { say "ERROR: $*" >&2; exit 2; }

OPENCLAW_DIR="${OPENCLAW_DIR:-$HOME/.openclaw}"
OPENCLAW_JSON="$OPENCLAW_DIR/openclaw.json"
CRED_DIR="$OPENCLAW_DIR/credentials"
CRED_JSON="$CRED_DIR/clawboard-memory-backup.json"
CRED_ENV="$CRED_DIR/clawboard-memory-backup.env"

need_cmd() { command -v "$1" >/dev/null 2>&1 || die "Missing required command: $1"; }
need_cmd python3
need_cmd mkdir
need_cmd chmod
need_cmd cat
need_cmd ssh-keygen

has_cmd() { command -v "$1" >/dev/null 2>&1; }

# bash 3.2 compatibility (macOS default /bin/bash): no ${var,,}
lc() { tr '[:upper:]' '[:lower:]' <<<"${1:-}"; }

workspace_from_config() {
  [[ -f "$OPENCLAW_JSON" ]] || return 1
  python3 - <<'PY' "$OPENCLAW_JSON"
import json,sys
p=sys.argv[1]
try:
  d=json.load(open(p))
  print(d.get('agents',{}).get('defaults',{}).get('workspace','') or '')
except Exception:
  print('')
PY
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

detect_clawboard_dir() {
  local script_dir candidate
  script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
  candidate="$(cd "$script_dir/../../.." >/dev/null 2>&1 && pwd || true)"
  if [[ -n "$candidate" && -f "$candidate/deploy.sh" && -f "$candidate/docker-compose.yaml" ]]; then
    printf "%s" "$candidate"
    return 0
  fi

  for candidate in \
    "${CLAWBOARD_DIR:-}" \
    "$WORKSPACE_PATH/projects/clawboard" \
    "$WORKSPACE_PATH/project/clawboard" \
    "$HOME/clawboard"
  do
    [[ -n "$candidate" ]] || continue
    if [[ -f "$candidate/deploy.sh" && -f "$candidate/docker-compose.yaml" ]]; then
      printf "%s" "$candidate"
      return 0
    fi
  done
  return 1
}

prompt() {
  local var="$1"; shift
  local msg="$1"; shift
  local silent="${1:-0}"
  local val=""
  if [[ "$silent" == "1" ]]; then
    read -r -s -p "$msg" val; echo ""
  else
    read -r -p "$msg" val
  fi
  printf -v "$var" "%s" "$val"
}

say "== Clawboard: OpenClaw curated memory backup setup =="

WORKSPACE_PATH="$(workspace_from_config || true)"
if [[ -z "$WORKSPACE_PATH" ]]; then
  say "Could not find workspace in: $OPENCLAW_JSON"
  prompt WORKSPACE_PATH "Enter your OpenClaw workspace path (e.g. /Users/<you>/clawd): "
fi
[[ -d "$WORKSPACE_PATH" ]] || die "Workspace path does not exist: $WORKSPACE_PATH"

mkdir -p "$CRED_DIR"

say ""
say "Step 1: GitHub repo"
say "We can create a *private* repo automatically if you have the GitHub CLI (gh) installed and authenticated."

CREATE_REPO=""
if has_cmd gh; then
  # Check auth status quickly
  if gh auth status -h github.com >/dev/null 2>&1; then
    prompt CREATE_REPO "Create a new private repo now via gh? [y/N]: "
  else
    say "(gh found, but not authenticated. Run: gh auth login)"
    CREATE_REPO="n"
  fi
else
  say "(gh not found. We'll print browser instructions instead.)"
  CREATE_REPO="n"
fi

REPO_URL=""
REPO_SSH_URL=""

case "$(lc "${CREATE_REPO:-}")" in
  y|yes)
    prompt REPO_OWNER "Repo owner (user or org): "
    prompt REPO_NAME "Repo name [default: openclaw-memories-backup]: "
    REPO_NAME="${REPO_NAME:-openclaw-memories-backup}"

    say "Creating private repo: $REPO_OWNER/$REPO_NAME"
    gh repo create "$REPO_OWNER/$REPO_NAME" --private --confirm >/dev/null

    REPO_URL="https://github.com/$REPO_OWNER/$REPO_NAME.git"
    REPO_SSH_URL="git@github.com:$REPO_OWNER/$REPO_NAME.git"

    say "Created: $REPO_URL"
    ;;
  *)
    say "Create a *private* GitHub repo for backups (do this in your browser)."
    say "  - Repo name suggestion: openclaw-memories-backup"
    say "  - Keep it private"
    say "  - You can leave it empty (no README needed)"
    say ""
    prompt REPO_URL "Paste the repo HTTPS URL (like https://github.com/OWNER/REPO.git): "
    [[ "$REPO_URL" == https://github.com/*/*.git ]] || die "Repo URL must look like: https://github.com/OWNER/REPO.git"
    REPO_SSH_URL="${REPO_URL/https:\/\/github.com\//git@github.com:}"
    ;;
esac

say ""
say "Step 2: Auth method"
say "Recommended: GitHub Deploy Key (SSH)."
say " - You must enable *Allow write access* when adding the key (reminder: otherwise pushes will fail)."

prompt AUTH_METHOD "Use Deploy Key (SSH) instead of PAT? [Y/n]: "
case "$(lc "${AUTH_METHOD:-}")" in n|no) AUTH_METHOD="pat" ;; *) AUTH_METHOD="ssh" ;; esac

GITHUB_USER=""
GITHUB_PAT=""
DEPLOY_KEY_PATH=""
DEPLOY_PUB_PATH=""

if [[ "$AUTH_METHOD" == "pat" ]]; then
  say ""
  say "PAT mode (legacy)"
  say "Create a fine-grained PAT (GitHub Settings → Developer settings → Fine-grained tokens)."
  say "  - Resource owner: your account/org"
  say "  - Repository access: ONLY the backup repo"
  say "  - Permissions: Contents = Read and write"
  say ""
  prompt GITHUB_USER "GitHub username (used for HTTPS auth): "
  prompt GITHUB_PAT "Paste the fine-grained PAT (input hidden): " 1
else
  say ""
  say "Deploy key (SSH) mode"
  say "We'll generate a dedicated SSH keypair and then you add the *public* key as a Deploy Key on the repo."

  DEFAULT_KEY_PATH="$OPENCLAW_DIR/credentials/clawboard-memory-backup-deploy-key"
  prompt DEPLOY_KEY_PATH "Deploy key path [default: $DEFAULT_KEY_PATH]: "
  DEPLOY_KEY_PATH="${DEPLOY_KEY_PATH:-$DEFAULT_KEY_PATH}"
  DEPLOY_PUB_PATH="$DEPLOY_KEY_PATH.pub"

  mkdir -p "$(dirname "$DEPLOY_KEY_PATH")"

  if [[ -f "$DEPLOY_KEY_PATH" && -f "$DEPLOY_PUB_PATH" ]]; then
    prompt REUSE_KEY "Key already exists at $DEPLOY_KEY_PATH. Reuse it? [Y/n]: "
    REUSE_KEY="${REUSE_KEY:-Y}"
    case "$(lc "${REUSE_KEY:-}")" in
      y|yes)
        say "Reusing existing deploy key."
        ;;
      *)
        prompt OVERWRITE "Overwrite existing keypair at $DEPLOY_KEY_PATH? [y/N]: "
        case "$(lc "${OVERWRITE:-}")" in
          y|yes)
            rm -f "$DEPLOY_KEY_PATH" "$DEPLOY_PUB_PATH"
            ssh-keygen -t ed25519 -C "clawboard-memory-backup" -f "$DEPLOY_KEY_PATH" -N "" >/dev/null
            chmod 600 "$DEPLOY_KEY_PATH"
            chmod 644 "$DEPLOY_PUB_PATH"
            ;;
          *)
            say "Keeping existing keypair (no changes)."
            ;;
        esac
        ;;
    esac
  else
    ssh-keygen -t ed25519 -C "clawboard-memory-backup" -f "$DEPLOY_KEY_PATH" -N "" >/dev/null
    chmod 600 "$DEPLOY_KEY_PATH"
    chmod 644 "$DEPLOY_PUB_PATH"
  fi

  say ""
  say "Deploy Key reminder (GitHub):"
  say "  Repo → Settings → Deploy keys → Add deploy key"
  say "  Title: clawboard-memory-backup"
  say "  Key: (paste the PUBLIC key below)"
  say "  IMPORTANT: check 'Allow write access' so backups can push."
  say ""
  cat "$DEPLOY_PUB_PATH"
  say ""
  prompt CONFIRM_DEPLOY_KEY "Press Enter once you've added the key (or Ctrl+C to abort): "
fi

say ""
say "Step 3: Choose what to back up (Option B buckets)."
prompt INCLUDE_OPENCLAW_CONFIG "Include ~/.openclaw/openclaw.json* ? [Y/n]: "
prompt INCLUDE_OPENCLAW_SKILLS "Include ~/.openclaw/skills/ ? [Y/n]: "

# defaults
case "$(lc "${INCLUDE_OPENCLAW_CONFIG:-}")" in n|no) INCLUDE_OPENCLAW_CONFIG=false ;; *) INCLUDE_OPENCLAW_CONFIG=true ;; esac
case "$(lc "${INCLUDE_OPENCLAW_SKILLS:-}")" in n|no) INCLUDE_OPENCLAW_SKILLS=false ;; *) INCLUDE_OPENCLAW_SKILLS=true ;; esac

say ""
say "Step 4: Clawboard state backup"
say "Recommended: include full Clawboard state export (config/topics/tasks/logs)."
prompt INCLUDE_CLAWBOARD_STATE "Include Clawboard state export? [Y/n]: "
case "$(lc "${INCLUDE_CLAWBOARD_STATE:-}")" in
  n|no)
    INCLUDE_CLAWBOARD_STATE=false
    CLAWBOARD_DIR=""
    CLAWBOARD_API_URL=""
    INCLUDE_CLAWBOARD_ATTACHMENTS=false
    INCLUDE_CLAWBOARD_ENV=false
    CLAWBOARD_BACKUP_TOKEN=""
    ;;
  *)
    INCLUDE_CLAWBOARD_STATE=true
    DETECTED_CLAWBOARD_DIR="$(detect_clawboard_dir || true)"
    if [[ -n "$DETECTED_CLAWBOARD_DIR" ]]; then
      prompt CLAWBOARD_DIR "Clawboard install path [default: $DETECTED_CLAWBOARD_DIR]: "
      CLAWBOARD_DIR="${CLAWBOARD_DIR:-$DETECTED_CLAWBOARD_DIR}"
    else
      prompt CLAWBOARD_DIR "Clawboard install path (contains deploy.sh): "
    fi
    [[ -d "$CLAWBOARD_DIR" ]] || die "Clawboard path does not exist: $CLAWBOARD_DIR"
    [[ -f "$CLAWBOARD_DIR/deploy.sh" ]] || die "Clawboard path does not look valid (missing deploy.sh): $CLAWBOARD_DIR"

    DEFAULT_CLAWBOARD_API_URL="http://localhost:8010"
    if [[ -f "$CLAWBOARD_DIR/.env" ]]; then
      DEFAULT_CLAWBOARD_API_URL="$(read_env_value "$CLAWBOARD_DIR/.env" "CLAWBOARD_PUBLIC_API_BASE" || true)"
      if [[ -z "$DEFAULT_CLAWBOARD_API_URL" ]]; then
        DEFAULT_CLAWBOARD_API_URL="http://localhost:8010"
      fi
    fi
    prompt CLAWBOARD_API_URL "Clawboard API base URL [default: $DEFAULT_CLAWBOARD_API_URL]: "
    CLAWBOARD_API_URL="${CLAWBOARD_API_URL:-$DEFAULT_CLAWBOARD_API_URL}"

    prompt INCLUDE_CLAWBOARD_ATTACHMENTS "Include Clawboard attachment files? [Y/n]: "
    prompt INCLUDE_CLAWBOARD_ENV "Include Clawboard .env (contains secrets)? [y/N]: "
    prompt CLAWBOARD_BACKUP_TOKEN "Optional Clawboard token override (hidden, blank=read CLAWBOARD_TOKEN from .env): " 1

    case "$(lc "${INCLUDE_CLAWBOARD_ATTACHMENTS:-}")" in n|no) INCLUDE_CLAWBOARD_ATTACHMENTS=false ;; *) INCLUDE_CLAWBOARD_ATTACHMENTS=true ;; esac
    case "$(lc "${INCLUDE_CLAWBOARD_ENV:-}")" in y|yes) INCLUDE_CLAWBOARD_ENV=true ;; *) INCLUDE_CLAWBOARD_ENV=false ;; esac
    ;;
esac

say ""
prompt BACKUP_DIR "Local backup repo directory [default: $OPENCLAW_DIR/memory-backup-repo]: "
BACKUP_DIR="${BACKUP_DIR:-$OPENCLAW_DIR/memory-backup-repo}"

REMOTE_NAME="origin"
BRANCH="main"

# Write env file for future use (esp. SSH key path)
# NOTE: This stores only the *path* to the private key, not the key material.
cat >"$CRED_ENV" <<ENV
# Clawboard memory backup auth/env
# This file is sourced by backup_openclaw_curated_memories.sh (set -a)

AUTH_METHOD="$AUTH_METHOD"
REPO_URL="$REPO_URL"
REPO_SSH_URL="$REPO_SSH_URL"
DEPLOY_KEY_PATH="${DEPLOY_KEY_PATH:-}"
GITHUB_USER="$GITHUB_USER"
GITHUB_PAT="$GITHUB_PAT"
CLAWBOARD_BACKUP_DIR="${CLAWBOARD_DIR}"
CLAWBOARD_BACKUP_API_URL="${CLAWBOARD_API_URL}"
CLAWBOARD_BACKUP_TOKEN="${CLAWBOARD_BACKUP_TOKEN:-}"
ENV
chmod 600 "$CRED_ENV"

# Write JSON config (0600)
cat >"$CRED_JSON" <<JSON
{
  "workspacePath": "${WORKSPACE_PATH}",
  "backupDir": "${BACKUP_DIR}",
  "repoUrl": "${REPO_URL}",
  "repoSshUrl": "${REPO_SSH_URL}",
  "authMethod": "${AUTH_METHOD}",
  "deployKeyPath": "${DEPLOY_KEY_PATH}",
  "githubUser": "${GITHUB_USER}",
  "githubPat": "${GITHUB_PAT}",
  "remoteName": "${REMOTE_NAME}",
  "branch": "${BRANCH}",
  "includeOpenclawConfig": ${INCLUDE_OPENCLAW_CONFIG},
  "includeOpenclawSkills": ${INCLUDE_OPENCLAW_SKILLS},
  "includeClawboardState": ${INCLUDE_CLAWBOARD_STATE},
  "clawboardDir": "${CLAWBOARD_DIR}",
  "clawboardApiUrl": "${CLAWBOARD_API_URL}",
  "includeClawboardAttachments": ${INCLUDE_CLAWBOARD_ATTACHMENTS},
  "includeClawboardEnv": ${INCLUDE_CLAWBOARD_ENV}
}
JSON

chmod 600 "$CRED_JSON"

say "Wrote config: $CRED_JSON"
say "Wrote env:    $CRED_ENV"

say ""
say "Running one backup now to validate..."
"$(cd "$(dirname "$0")" && pwd)/backup_openclaw_curated_memories.sh"

say ""
say "Optional: install an OpenClaw cron job to run every 15 minutes."
say "If you say yes, we will create a Gateway cron job (isolated agent turn) that runs the backup script."

prompt INSTALL_CRON "Install OpenClaw cron (every 15m)? [Y/n]: "
# default: yes
INSTALL_CRON="${INSTALL_CRON:-Y}"
case "$(lc "${INSTALL_CRON:-}")" in
  y|yes)
    need_cmd openclaw
    say ""
    say "Creating cron job via OpenClaw CLI..."

    JOB_NAME="Clawboard: backup continuity + state"
    JOB_EVERY="15m"
    JOB_SESSION="isolated"
    JOB_MESSAGE="Run the continuity + Clawboard state backup now (automated 15-minute backup). Execute: $HOME/.openclaw/skills/clawboard/scripts/backup_openclaw_curated_memories.sh . IMPORTANT: Only notify me if (a) there were changes pushed, or (b) the backup failed. If there were no changes and the script exited 0 without output, respond with NO_REPLY."

    # Idempotent cron install: update existing job by name (or backup script match); otherwise add.
    existing_id=""
    if openclaw cron list --json >/dev/null 2>&1; then
      existing_id="$(
        openclaw cron list --json | python3 -c '
import json
import sys

data = json.load(sys.stdin)
jobs = data.get("jobs") if isinstance(data, dict) else []
jobs = jobs or []

name = "Clawboard: backup continuity + state"
needle = "backup_openclaw_curated_memories.sh"

cands = [
  j
  for j in jobs
  if isinstance(j, dict)
  and str(j.get("sessionTarget") or "").strip() == "isolated"
  and (
    str(j.get("name") or "") == name
    or needle in str(((j.get("payload") if isinstance(j.get("payload"), dict) else {}) or {}).get("message") or "")
  )
]

print((cands[0].get("id") or cands[0].get("jobId") or "") if cands else "", end="")
' || true
      )"
    fi

    cron_ok=0
    if [[ -n "$existing_id" ]]; then
      say "Found existing cron job ($existing_id). Updating it..."
      if openclaw cron edit "$existing_id" \
        --name "$JOB_NAME" \
        --every "$JOB_EVERY" \
        --session "$JOB_SESSION" \
        --no-deliver \
        --message "$JOB_MESSAGE" \
        --enable; then
        cron_ok=1
      fi
    else
      say "No existing cron job found. Creating it..."
      if openclaw cron add \
        --name "$JOB_NAME" \
        --every "$JOB_EVERY" \
        --session "$JOB_SESSION" \
        --no-deliver \
        --message "$JOB_MESSAGE"; then
        cron_ok=1
      fi
    fi

    if [[ "$cron_ok" -ne 1 ]]; then
      say "If cron setup failed, create it manually with these settings:"
      say "  name: $JOB_NAME"
      say "  schedule: every $JOB_EVERY"
      say "  session: $JOB_SESSION"
      say "  delivery: none"
      say "  message: $JOB_MESSAGE"
    else
      say "Cron job installed/updated successfully."
    fi
    ;;
  *)
    say "Skipped cron install. You can run this script anytime to push updates."
    ;;
esac

say "Done."
