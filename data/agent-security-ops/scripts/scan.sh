#!/usr/bin/env bash
set -euo pipefail

# agent-security-ops: Full security scan
# MARKER:agent-security-ops
# stdout: JSON report | stderr: human-readable summary

SCRIPT_VERSION="1.1.0"

export PATH="$HOME/.local/bin:$PATH"

# Portable timeout: use coreutils timeout/gtimeout if available, otherwise perl
run_timeout() {
  local secs="$1"; shift
  if command -v timeout >/dev/null 2>&1; then
    timeout "$secs" "$@"
  elif command -v gtimeout >/dev/null 2>&1; then
    gtimeout "$secs" "$@"
  else
    # Perl-based fallback (available on macOS and most Linux)
    perl -e 'alarm shift; exec @ARGV' "$secs" "$@"
  fi
}

if [ -t 2 ]; then
  GREEN='\033[0;32m'; YELLOW='\033[0;33m'; RED='\033[0;31m'; BLUE='\033[0;34m'; NC='\033[0m'; BOLD='\033[1m'
else
  GREEN=''; YELLOW=''; RED=''; BLUE=''; NC=''; BOLD=''
fi

log()     { printf "${GREEN}✓${NC} %s\n" "$1" >&2; }
warn()    { printf "${YELLOW}⚠${NC} %s\n" "$1" >&2; }
info()    { printf "${BLUE}→${NC} %s\n" "$1" >&2; }
section() { printf "\n${BOLD}--- %s ---${NC}\n" "$1" >&2; }

# Parse flags
for arg in "$@"; do
  case "$arg" in
    --help|-h)
      cat >&2 <<'USAGE'
Usage: scan.sh [OPTIONS] [/path/to/repo]

Full security scan. JSON report to stdout, human summary to stderr.

Options:
  --help, -h    Show this help
  --version     Show version

Note: Open port scan may require sudo on macOS for full process info.
Note: $HOME .env file check scans outside repo scope (warns only, not counted as repo findings).
USAGE
      exit 0
      ;;
    --version)
      echo "agent-security-ops scan.sh v${SCRIPT_VERSION}" >&2
      exit 0
      ;;
  esac
done

count_lines() {
  local input="${1:-}"
  if [ -z "$input" ]; then echo 0; return; fi
  echo "$input" | grep -c . 2>/dev/null || echo 0
}

# [M1] Improved JSON escaping — handles newlines, CRs, tabs, backslashes, quotes
json_escape_str() {
  printf '%s' "$1" | sed -e 's/\\/\\\\/g' -e 's/"/\\"/g' -e 's/	/\\t/g' | tr -d '\r' | tr '\n' ' '
}

REPO="${1:-.}"
REPO="$(cd "$REPO" && pwd)"

if [ ! -d "$REPO/.git" ]; then
  printf "${RED}✗${NC} Not a git repository: %s\n" "$REPO" >&2
  exit 1
fi

cd "$REPO"

if ! command -v jq >/dev/null 2>&1; then
  warn "jq not found — JSON output may be malformed on unusual content. Install: https://jqlang.github.io/jq/"
fi

trufflehog_count=0
trufflehog_verified=0
fs_count=0
grep_count=0
grep_out=""
gitignore_missing_arr=()
perm_count=0
perm_out=""

# --- 1. TruffleHog ---
# [C3] Scan ALL secrets, mark verified ones specially
section "TruffleHog Secret Scan"
if command -v trufflehog >/dev/null 2>&1; then
  trufflehog_out=$(run_timeout 300 trufflehog git "file://$REPO" --no-update --json 2>/dev/null) || true
  if [ -n "$trufflehog_out" ]; then
    trufflehog_count=$(echo "$trufflehog_out" | grep -c '"SourceMetadata"' || true)
    trufflehog_count=$((trufflehog_count + 0))
    trufflehog_verified=$(echo "$trufflehog_out" | grep -c '"Verified":true' || true)
    trufflehog_verified=$((trufflehog_verified + 0))
  fi
  if [ "$trufflehog_count" -gt 0 ]; then
    warn "Found $trufflehog_count secret(s) ($trufflehog_verified verified)"
  else
    log "No secrets found"
  fi

  # [M5] Filesystem scan for untracked files
  section "TruffleHog Filesystem Scan"
  fs_out=$(run_timeout 120 trufflehog filesystem "$REPO" --no-update --json 2>/dev/null) || true
  if [ -n "$fs_out" ]; then
    fs_count=$(echo "$fs_out" | grep -c '"SourceMetadata"' || true)
    fs_count=$((fs_count + 0))
  fi
  if [ "$fs_count" -gt 0 ]; then
    warn "Found $fs_count secret(s) in filesystem (untracked files)"
  else
    log "No secrets in untracked files"
  fi
else
  warn "TruffleHog not installed — run setup.sh first"
fi

# --- 2. Grep patterns (synced with patterns.md) ---
# [B2] --exclude-dir=.git everywhere
# [H3] Telegram bot token moved to reference-only (too many false positives)
# [H4] Added: AWS secret keys, password=/secret=, bearer tokens, database URLs, Firebase, Supabase
# [B4] Exclude .env.example files
section "Pattern Grep Scan"

# High-confidence patterns
GREP_PAT='AKIA[0-9A-Z]{16}'
GREP_PAT="$GREP_PAT"'|ghp_[A-Za-z0-9]{36}|github_pat_[A-Za-z0-9_]{82}'
GREP_PAT="$GREP_PAT"'|gho_[A-Za-z0-9]{36}|ghu_[A-Za-z0-9]{36}|ghs_[A-Za-z0-9]{36}|ghr_[A-Za-z0-9]{36}'
GREP_PAT="$GREP_PAT"'|xoxb-[0-9]{10,}-[0-9]{10,}|xoxp-[0-9]{10,}'
GREP_PAT="$GREP_PAT"'|sk-proj-[A-Za-z0-9_-]{80,}'
GREP_PAT="$GREP_PAT"'|sk_live_[A-Za-z0-9]{24,}|pk_live_[A-Za-z0-9]{24,}|rk_live_[A-Za-z0-9]{24,}'
GREP_PAT="$GREP_PAT"'|AIza[0-9A-Za-z_-]{35}|GOCSPX-[A-Za-z0-9_-]{28}'
GREP_PAT="$GREP_PAT"'|-----BEGIN [A-Z ]*PRIVATE KEY-----'
GREP_PAT="$GREP_PAT"'|sk-ant-[A-Za-z0-9_-]{20,}'
GREP_PAT="$GREP_PAT"'|https://hooks\.slack\.com/services/T[A-Z0-9]{8,}'
GREP_PAT="$GREP_PAT"'|SK[a-f0-9]{32}'
GREP_PAT="$GREP_PAT"'|SG\.[A-Za-z0-9_-]{22}\.[A-Za-z0-9_-]{43}'
GREP_PAT="$GREP_PAT"'|npm_[A-Za-z0-9]{36}'
GREP_PAT="$GREP_PAT"'|hvs\.[A-Za-z0-9_-]{24,}'

# [H4] Low-confidence patterns (added)
LOW_PAT='(mongodb|postgres|postgresql|mysql|redis)://[^ ]{10,}'
LOW_PAT="$LOW_PAT"'|(password|passwd|secret)\s*[=:]\s*['\''"][^\s'\''\"]{8,}['\''"]'
LOW_PAT="$LOW_PAT"'|[Bb]earer\s+[A-Za-z0-9_.~+/-]{20,}'
LOW_PAT="$LOW_PAT"'|AKIA[0-9A-Z]{16}[^A-Za-z0-9][A-Za-z0-9/+=]{40}'
LOW_PAT="$LOW_PAT"'|FIREBASE_[A-Z_]*=.{10,}'
LOW_PAT="$LOW_PAT"'|sbp_[A-Za-z0-9]{40,}'
LOW_PAT="$LOW_PAT"'|eyJhbGciOi[A-Za-z0-9_-]{20,}'

# [M3] Self-exclusion: exclude by marker and multiple path patterns
grep_out=$(grep -rEn --exclude-dir=.git --exclude-dir=node_modules --exclude-dir=.venv \
  --exclude-dir=venv --exclude-dir=__pycache__ --exclude-dir=.security-ops \
  --exclude='*.example' --exclude='.env.example' --exclude='.env.*.example' \
  "$GREP_PAT" \
  --include='*.js' --include='*.ts' --include='*.py' --include='*.rb' \
  --include='*.go' --include='*.java' --include='*.yaml' --include='*.yml' \
  --include='*.json' --include='*.toml' --include='*.ini' --include='*.cfg' \
  --include='*.conf' --include='*.sh' --include='*.env' --include='*.env.local' \
  --include='*.tf' --include='*.tfvars' --include='*.properties' --include='*.xml' \
  --include='*.md' --include='*.txt' \
  --include='Makefile' --include='Procfile' --include='Vagrantfile' \
  . 2>/dev/null | \
  grep -v 'MARKER:agent-security-ops' | \
  grep -v 'patterns\.md' || true)

grep_count=$(count_lines "$grep_out")

# Low-confidence scan
low_grep_out=$(grep -rEn --exclude-dir=.git --exclude-dir=node_modules --exclude-dir=.venv \
  --exclude-dir=venv --exclude-dir=__pycache__ --exclude-dir=.security-ops \
  --exclude='*.example' --exclude='.env.example' --exclude='.env.*.example' \
  "$LOW_PAT" \
  --include='*.js' --include='*.ts' --include='*.py' --include='*.rb' \
  --include='*.go' --include='*.java' --include='*.yaml' --include='*.yml' \
  --include='*.json' --include='*.toml' --include='*.ini' --include='*.cfg' \
  --include='*.conf' --include='*.sh' --include='*.env' --include='*.env.local' \
  --include='*.tf' --include='*.tfvars' \
  . 2>/dev/null | \
  grep -v 'MARKER:agent-security-ops' | \
  grep -v 'patterns\.md' || true)

low_grep_count=$(count_lines "$low_grep_out")

if [ "$grep_count" -gt 0 ]; then
  warn "Found $grep_count high-confidence secret pattern(s)"
  echo "$grep_out" | head -20 >&2
else
  log "No high-confidence secret patterns in source"
fi

if [ "$low_grep_count" -gt 0 ]; then
  warn "Found $low_grep_count low-confidence pattern(s) (review manually)"
  echo "$low_grep_out" | head -10 >&2
else
  log "No low-confidence patterns"
fi

# --- 3. .gitignore audit ---
# [M6] Use git check-ignore
section ".gitignore Audit"
REQUIRED=('.env' '.env.local' 'test.pem' 'test.key' 'id_rsa' 'test.p12' 'test.pfx' 'credentials.json' 'token.json' 'service-account-test.json' 'test.keystore' '.terraform/')
REQUIRED_LABELS=('.env*' '*.pem' '*.key' 'id_rsa*' '*.p12' '*.pfx' 'credentials.json' 'token.json' 'service-account*.json' '*.keystore' '.terraform/')

if [ -f .gitignore ]; then
  idx=0
  for testfile in "${REQUIRED[@]}"; do
    if ! git check-ignore -q "$testfile" 2>/dev/null; then
      gitignore_missing_arr+=("${REQUIRED_LABELS[$idx]}")
    fi
    idx=$((idx + 1))
  done
  if [ "${#gitignore_missing_arr[@]}" -gt 0 ]; then
    warn "Missing from .gitignore: ${gitignore_missing_arr[*]}"
  else
    log ".gitignore covers all recommended patterns"
  fi
else
  warn "No .gitignore found"
  gitignore_missing_arr=("${REQUIRED_LABELS[@]}")
fi

# --- 4. Dependency audit ---
section "Dependency Audit"
npm_vulns=0
pip_vulns=0

if [ -f package.json ] && command -v npm >/dev/null 2>&1; then
  info "Running npm audit..."
  npm_json=$(npm audit --json 2>/dev/null || true)
  npm_vulns_raw=$(echo "$npm_json" | grep -o '"total":[0-9]*' | head -1 | cut -d: -f2 || true)
  npm_vulns=$((${npm_vulns_raw:-0} + 0))
  if [ "$npm_vulns" -gt 0 ]; then
    warn "npm: $npm_vulns vulnerability(ies)"
  else
    log "npm audit: clean"
  fi
fi

if [ -f requirements.txt ] && command -v pip-audit >/dev/null 2>&1; then
  info "Running pip audit..."
  pip_json=$(pip-audit -r requirements.txt --format json 2>/dev/null || true)
  pip_vulns_raw=$(echo "$pip_json" | grep -c '"name"' || true)
  pip_vulns=$((${pip_vulns_raw:-0} + 0))
  if [ "$pip_vulns" -gt 0 ]; then
    warn "pip: $pip_vulns vulnerability(ies)"
  else
    log "pip audit: clean"
  fi
fi

# --- 5. File permissions ---
section "File Permissions"
perm_out=$(find . -maxdepth 3 \
  \( -name '*.pem' -o -name '*.key' -o -name '*.p12' -o -name '*.pfx' \
     -o -name 'id_rsa*' -o -name '*.keystore' -o -name '.env*' \
     -o -name 'credentials.json' -o -name 'token.json' \) \
  -not -name '*.example' \
  -perm -o+r 2>/dev/null || true)

perm_count=$(count_lines "$perm_out")

if [ "$perm_count" -gt 0 ]; then
  warn "$perm_count world-readable sensitive file(s)"
  echo "$perm_out" >&2
else
  log "No world-readable sensitive files"
fi

# --- 6. Open Port Scan ---
# [B3] Note: on macOS, lsof may need sudo for full process info on ports owned by other users
section "Open Port Scan"
open_ports_out=""
open_ports_count=0
open_ports_unexpected=""
unexpected_arr=()
COMMON_PORTS="22 80 443 3000 5173 8080"

if [ "$(uname -s)" = "Darwin" ]; then
  info "(Note: some port info may require sudo on macOS)"
  open_ports_out=$(lsof -i -P -n 2>/dev/null | grep LISTEN || true)
elif command -v ss >/dev/null 2>&1; then
  open_ports_out=$(ss -tlnp 2>/dev/null || true)
else
  warn "No port scan tool available (need lsof or ss)"
fi

if [ -n "$open_ports_out" ]; then
  open_ports_count=$(count_lines "$open_ports_out")
  if [ "$(uname -s)" = "Darwin" ]; then
    port_list=$(echo "$open_ports_out" | awk '{print $9}' | grep -oE '[0-9]+$' | sort -un || true)
  else
    port_list=$(echo "$open_ports_out" | grep -oE ':([0-9]+)' | sed 's/://' | sort -un || true)
  fi
  for port in $port_list; do
    is_common=0
    for cp in $COMMON_PORTS; do
      if [ "$port" = "$cp" ]; then is_common=1; break; fi
    done
    if [ "$is_common" -eq 0 ]; then
      unexpected_arr+=("$port")
    fi
  done
  if [ "${#unexpected_arr[@]}" -gt 0 ]; then
    open_ports_unexpected=$(printf '%s,' "${unexpected_arr[@]}" | sed 's/,$//')
    warn "Unexpected listening ports: $open_ports_unexpected"
  else
    log "All listening ports are common"
  fi
  if [ "$(uname -s)" = "Darwin" ]; then
    echo "$open_ports_out" | awk '{printf "  %s → %s\n", $1, $9}' | sort -u | head -20 >&2
  else
    echo "$open_ports_out" | head -20 >&2
  fi
else
  log "No listening ports detected"
fi

# --- 7. Environment Variable Audit ---
# [POLISH] $HOME .env scan is outside repo scope — warn only, don't count as repo findings
section "Environment Variable Audit"
env_secrets_out=""
env_files_out=""
env_secrets_count=0
env_files_warning_count=0

ENV_SECRET_PAT='export[[:space:]]+([-_A-Za-z0-9]*(KEY|TOKEN|SECRET|PASSWORD))[[:space:]]*='
for rcfile in "$HOME/.bashrc" "$HOME/.zshrc" "$HOME/.bash_profile" "$HOME/.profile"; do
  if [ -f "$rcfile" ]; then
    hits=$(grep -En "$ENV_SECRET_PAT" "$rcfile" 2>/dev/null || true)
    if [ -n "$hits" ]; then
      env_secrets_out="${env_secrets_out}${rcfile}:${hits}
"
    fi
  fi
done

for dir in "$HOME" "$HOME/Desktop" "$HOME/Downloads"; do
  if [ -d "$dir" ]; then
    found=$(find "$dir" -maxdepth 1 -name '.env*' -not -name '*.example' -type f 2>/dev/null || true)
    if [ -n "$found" ]; then
      env_files_out="${env_files_out}${found}
"
    fi
  fi
done

env_secrets_count=$(count_lines "$env_secrets_out")
env_files_warning_count=$(count_lines "$env_files_out")

if [ "$env_secrets_count" -gt 0 ]; then
  warn "Found $env_secrets_count hardcoded secret(s) in shell profiles"
  echo "$env_secrets_out" | head -10 >&2
fi
if [ "$env_files_warning_count" -gt 0 ]; then
  warn "Found $env_files_warning_count loose .env file(s) outside repo (warning only, not counted as repo findings)"
  echo "$env_files_out" | head -10 >&2
fi
if [ "$env_secrets_count" -eq 0 ] && [ "$env_files_warning_count" -eq 0 ]; then
  log "No hardcoded secrets in shell profiles or loose .env files"
fi

# --- 8. Docker Secret Check ---
section "Docker Secret Check"
docker_secrets_out=""
docker_secrets_count=0

DOCKER_SECRET_PAT='ENV[[:space:]]+([-_A-Za-z0-9]*(SECRET|KEY|TOKEN|PASSWORD))[[:space:]]*='
dockerfiles=$(find "$REPO" -maxdepth 3 -name 'Dockerfile*' -type f 2>/dev/null || true)
compose_files=$(find "$REPO" -maxdepth 3 \( -name 'docker-compose*.yml' -o -name 'docker-compose*.yaml' \) -type f 2>/dev/null || true)

if [ -n "$dockerfiles" ] || [ -n "$compose_files" ]; then
  if [ -n "$dockerfiles" ]; then
    while IFS= read -r df; do
      hits=$(grep -En "$DOCKER_SECRET_PAT" "$df" 2>/dev/null || true)
      if [ -n "$hits" ]; then
        docker_secrets_out="${docker_secrets_out}${df}:${hits}
"
      fi
    done <<< "$dockerfiles"
  fi

  if [ -n "$compose_files" ]; then
    while IFS= read -r cf; do
      hits=$(grep -En '(SECRET|KEY|TOKEN|PASSWORD)[[:space:]]*:[[:space:]]*[^${\s]' "$cf" 2>/dev/null | grep -v '\${' || true)
      if [ -n "$hits" ]; then
        docker_secrets_out="${docker_secrets_out}${cf}:${hits}
"
      fi
    done <<< "$compose_files"
  fi

  docker_secrets_count=$(count_lines "$docker_secrets_out")
  if [ "$docker_secrets_count" -gt 0 ]; then
    warn "Found $docker_secrets_count Docker secret issue(s)"
    echo "$docker_secrets_out" | head -10 >&2
  else
    log "No hardcoded secrets in Docker files"
  fi
else
  log "No Docker files found — skipping"
fi

# --- 9. SSH Config Check ---
section "SSH Config Audit"
ssh_issues=""
ssh_issue_count=0

if [ -d "$HOME/.ssh" ]; then
  ssh_dir_perms=$(stat -f '%Lp' "$HOME/.ssh" 2>/dev/null || stat -c '%a' "$HOME/.ssh" 2>/dev/null || true)
  if [ -n "$ssh_dir_perms" ] && [ "$ssh_dir_perms" != "700" ] && [ "$ssh_dir_perms" != "600" ]; then
    ssh_issues="${ssh_issues}~/.ssh has permissions $ssh_dir_perms (should be 700)
"
  fi

  if [ -f "$HOME/.ssh/config" ]; then
    cfg_perms=$(stat -f '%Lp' "$HOME/.ssh/config" 2>/dev/null || stat -c '%a' "$HOME/.ssh/config" 2>/dev/null || true)
    if [ -n "$cfg_perms" ] && [ "$cfg_perms" != "600" ] && [ "$cfg_perms" != "644" ]; then
      ssh_issues="${ssh_issues}~/.ssh/config has permissions $cfg_perms (should be 600)
"
    fi
  fi

  for keyfile in "$HOME/.ssh"/id_*; do
    [ -f "$keyfile" ] || continue
    case "$keyfile" in *.pub) continue ;; esac
    key_perms=$(stat -f '%Lp' "$keyfile" 2>/dev/null || stat -c '%a' "$keyfile" 2>/dev/null || true)
    if [ -n "$key_perms" ] && [ "$key_perms" != "600" ]; then
      ssh_issues="${ssh_issues}$keyfile has permissions $key_perms (should be 600)
"
    fi
  done

  if [ -f "$HOME/.ssh/authorized_keys" ]; then
    ak_count=$(wc -l < "$HOME/.ssh/authorized_keys" | tr -d ' ')
    if [ "$ak_count" -gt 0 ]; then
      info "authorized_keys has $ak_count key(s)"
    fi
  fi

  ssh_issue_count=$(count_lines "$ssh_issues")
  if [ "$ssh_issue_count" -gt 0 ]; then
    warn "Found $ssh_issue_count SSH permission issue(s) — run setup.sh --fix-ssh to fix"
    echo "$ssh_issues" >&2
  else
    log "SSH config and permissions OK"
  fi
else
  log "No ~/.ssh directory found"
fi

# --- 10. Git Remote Audit ---
section "Git Remote Audit"
git_remote_issues=""
git_remote_count=0
git_remotes_raw=$(git -C "$REPO" remote -v 2>/dev/null || true)

if [ -n "$git_remotes_raw" ]; then
  http_remotes=$(echo "$git_remotes_raw" | grep -E 'http://' || true)
  if [ -n "$http_remotes" ]; then
    git_remote_issues="${git_remote_issues}Insecure HTTP remotes:
${http_remotes}
"
  fi

  if command -v gh >/dev/null 2>&1; then
    public_repos=""
    repo_slugs=$(echo "$git_remotes_raw" | grep -oE 'github\.com[:/]([^/]+/[^/.]+)' | sed 's|github.com[:/]||' | sort -u || true)
    for slug in $repo_slugs; do
      visibility=$(gh api "repos/$slug" --jq '.visibility' 2>/dev/null || true)
      if [ "$visibility" = "public" ]; then
        public_repos="${public_repos}$slug (public)
"
      fi
    done
    if [ -n "$public_repos" ]; then
      git_remote_issues="${git_remote_issues}Public repos:
${public_repos}"
    fi
  fi

  git_remote_count=$(count_lines "$git_remote_issues")
  if [ "$git_remote_count" -gt 0 ]; then
    warn "Found $git_remote_count git remote issue(s)"
    echo "$git_remote_issues" >&2
  else
    log "Git remotes look clean"
  fi
  echo "$git_remotes_raw" | awk '/(fetch)/' | head -10 >&2
else
  log "No git remotes configured"
fi

# --- JSON report (stdout) ---
# [M1] Use jq for all JSON construction where available

build_json_array() {
  local input="$1"
  local max="${2:-50}"
  if [ -z "$input" ]; then echo "[]"; return; fi
  if command -v jq >/dev/null 2>&1; then
    echo "$input" | grep -v '^$' | head -"$max" | jq -R . | jq -s .
  else
    local result="["
    local first=1
    while IFS= read -r line; do
      [ -z "$line" ] && continue
      local escaped
      escaped=$(json_escape_str "$line")
      if [ "$first" -eq 1 ]; then
        result="${result}\"${escaped}\""
        first=0
      else
        result="${result},\"${escaped}\""
      fi
    done <<< "$(echo "$input" | head -"$max")"
    echo "${result}]"
  fi
}

missing_json="[]"
if [ "${#gitignore_missing_arr[@]}" -gt 0 ]; then
  if command -v jq >/dev/null 2>&1; then
    missing_json=$(printf '%s\n' "${gitignore_missing_arr[@]}" | jq -R . | jq -s .)
  else
    missing_json=$(printf '"%s",' "${gitignore_missing_arr[@]}" | sed 's/,$//')
    missing_json="[$missing_json]"
  fi
fi

grep_json=$(build_json_array "$grep_out" 50)
low_grep_json=$(build_json_array "$low_grep_out" 50)
perm_json=$(build_json_array "$perm_out" 50)
open_ports_json=$(build_json_array "$open_ports_out" 50)
env_secrets_json=$(build_json_array "${env_secrets_out}" 20)
env_files_json=$(build_json_array "${env_files_out}" 20)
docker_secrets_json=$(build_json_array "$docker_secrets_out" 20)
ssh_audit_json=$(build_json_array "$ssh_issues" 20)
git_remotes_json=$(build_json_array "$git_remotes_raw" 20)
git_remote_issues_json=$(build_json_array "$git_remote_issues" 20)

unexpected_ports_json="[]"
if [ "${#unexpected_arr[@]}" -gt 0 ]; then
  unexpected_ports_json="[$(printf '%s,' "${unexpected_arr[@]}" | sed 's/,$//')]"
fi

# env_files_warning_count NOT included in total (outside repo scope)
total_findings=$((trufflehog_count + fs_count + grep_count + ${#gitignore_missing_arr[@]} + perm_count + ssh_issue_count + git_remote_count + docker_secrets_count + env_secrets_count))

if command -v jq >/dev/null 2>&1; then
  jq -n \
    --arg repo "$REPO" \
    --arg ts "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
    --argjson th_count "$trufflehog_count" \
    --argjson th_verified "$trufflehog_verified" \
    --argjson fs_count "$fs_count" \
    --argjson grep_count "$grep_count" \
    --argjson grep_findings "$grep_json" \
    --argjson low_grep_count "$low_grep_count" \
    --argjson low_grep_findings "$low_grep_json" \
    --argjson missing "$missing_json" \
    --argjson perm_count "$perm_count" \
    --argjson perm_files "$perm_json" \
    --argjson ports_count "$open_ports_count" \
    --argjson ports_unexpected "$unexpected_ports_json" \
    --argjson ports_listeners "$open_ports_json" \
    --argjson env_count "$env_secrets_count" \
    --argjson env_findings "$env_secrets_json" \
    --argjson env_files_warnings "$env_files_json" \
    --argjson docker_count "$docker_secrets_count" \
    --argjson docker_findings "$docker_secrets_json" \
    --argjson ssh_count "$ssh_issue_count" \
    --argjson ssh_issues "$ssh_audit_json" \
    --argjson remotes "$git_remotes_json" \
    --argjson remote_issues "$git_remote_issues_json" \
    --argjson npm_vulns "$npm_vulns" \
    --argjson pip_vulns "$pip_vulns" \
    --argjson total "$total_findings" \
    '{
      repo: $repo, timestamp: $ts,
      trufflehog: {total_secrets: $th_count, verified_secrets: $th_verified},
      filesystem_scan: {secrets: $fs_count},
      grep_patterns: {high_confidence: {count: $grep_count, findings: $grep_findings}, low_confidence: {count: $low_grep_count, findings: $low_grep_findings}},
      gitignore: {missing_patterns: $missing},
      dependencies: {npm_vulns: $npm_vulns, pip_vulns: $pip_vulns},
      permissions: {world_readable_sensitive: $perm_count, files: $perm_files},
      open_ports: {count: $ports_count, unexpected: $ports_unexpected, listeners: $ports_listeners},
      env_secrets: {count: $env_count, findings: $env_findings, loose_env_files_warning: $env_files_warnings},
      docker_secrets: {count: $docker_count, findings: $docker_findings},
      ssh_audit: {issue_count: $ssh_count, issues: $ssh_issues},
      git_remotes: {remotes: $remotes, issues: $remote_issues},
      total_findings: $total
    }'
else
  cat <<EOF
{
  "repo": "$(json_escape_str "$REPO")",
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "trufflehog": {"total_secrets": $trufflehog_count, "verified_secrets": $trufflehog_verified},
  "filesystem_scan": {"secrets": $fs_count},
  "grep_patterns": {"high_confidence": {"count": $grep_count, "findings": $grep_json}, "low_confidence": {"count": $low_grep_count, "findings": $low_grep_json}},
  "gitignore": {"missing_patterns": $missing_json},
  "dependencies": {"npm_vulns": $npm_vulns, "pip_vulns": $pip_vulns},
  "permissions": {"world_readable_sensitive": $perm_count, "files": $perm_json},
  "open_ports": {"count": $open_ports_count, "unexpected": $unexpected_ports_json, "listeners": $open_ports_json},
  "env_secrets": {"count": $env_secrets_count, "findings": $env_secrets_json, "loose_env_files_warning": $env_files_json},
  "docker_secrets": {"count": $docker_secrets_count, "findings": $docker_secrets_json},
  "ssh_audit": {"issue_count": $ssh_issue_count, "issues": $ssh_audit_json},
  "git_remotes": {"remotes": $git_remotes_json, "issues": $git_remote_issues_json},
  "total_findings": $total_findings
}
EOF
fi

# Summary
section "Summary"
if [ "$total_findings" -eq 0 ]; then
  log "All clear — no findings"
else
  warn "Total: $total_findings (secrets=$trufflehog_count[$trufflehog_verified verified], fs=$fs_count, patterns=$grep_count[+$low_grep_count low], gitignore=${#gitignore_missing_arr[@]}, perms=$perm_count, env=${env_secrets_count}, docker=${docker_secrets_count}, ssh=${ssh_issue_count}, remotes=${git_remote_count})"
fi
