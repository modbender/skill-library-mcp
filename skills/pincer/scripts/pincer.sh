#!/usr/bin/env bash
# pincer - Security-first wrapper for clawhub install
# https://github.com/panzacoder/pincer
#
# v1.0.0 - Initial release

set -euo pipefail

VERSION="1.0.0"
CONFIG_DIR="${HOME}/.config/pincer"
CONFIG_FILE="${CONFIG_DIR}/config.json"
HISTORY_FILE="${CONFIG_DIR}/history.json"
CACHE_DIR="${CONFIG_DIR}/cache"
TEMP_DIR=""

# Colors (disable if NO_COLOR set or not a tty)
if [[ -t 1 ]] && [[ -z "${NO_COLOR:-}" ]]; then
  RED='\033[0;31m'
  GREEN='\033[0;32m'
  YELLOW='\033[0;33m'
  BLUE='\033[0;34m'
  CYAN='\033[0;36m'
  BOLD='\033[1m'
  DIM='\033[2m'
  NC='\033[0m'
else
  RED='' GREEN='' YELLOW='' BLUE='' CYAN='' BOLD='' DIM='' NC=''
fi

# Emojis
SHIELD="🦞"
CHECK="✅"
WARN="⚠️"
DANGER="🚨"
SKULL="☠️"

# Output mode
JSON_OUTPUT=false

#-----------------------------------------------------------------------------
# Helpers
#-----------------------------------------------------------------------------

log() { [[ "$JSON_OUTPUT" == "true" ]] || echo -e "${SHIELD} ${BOLD}pincer${NC} $1"; }
info() { [[ "$JSON_OUTPUT" == "true" ]] || echo -e "  ${BLUE}→${NC} $1"; }
ok() { [[ "$JSON_OUTPUT" == "true" ]] || echo -e "  ${GREEN}${CHECK}${NC} $1"; }
warn() { [[ "$JSON_OUTPUT" == "true" ]] || echo -e "  ${YELLOW}${WARN}${NC} $1"; }
danger() { [[ "$JSON_OUTPUT" == "true" ]] || echo -e "  ${RED}${DANGER}${NC} $1"; }
error() { echo -e "  ${RED}${SKULL}${NC} $1" >&2; }
debug() { [[ -z "${DEBUG:-}" ]] || echo -e "  ${DIM}[debug] $1${NC}" >&2; }

ensure_deps() {
  local missing=()
  command -v clawhub &>/dev/null || missing+=("clawhub")
  command -v jq &>/dev/null || missing+=("jq")
  command -v uvx &>/dev/null || missing+=("uvx (brew install uv)")
  
  if [[ ${#missing[@]} -gt 0 ]]; then
    error "Missing dependencies: ${missing[*]}"
    exit 1
  fi
}

ensure_config() {
  mkdir -p "$CONFIG_DIR" "$CACHE_DIR"
  if [[ ! -f "$CONFIG_FILE" ]]; then
    cat > "$CONFIG_FILE" << 'EOF'
{
  "trustedPublishers": ["openclaw", "steipete", "invariantlabs-ai"],
  "blockedSkills": [],
  "blockedPublishers": [],
  "autoApprove": "clean",
  "logInstalls": true,
  "minDownloads": 0,
  "minAgeDays": 0
}
EOF
  fi
  if [[ ! -f "$HISTORY_FILE" ]]; then
    echo "[]" > "$HISTORY_FILE"
  fi
}

cleanup() {
  if [[ -n "$TEMP_DIR" && -d "$TEMP_DIR" ]]; then
    rm -rf "$TEMP_DIR"
  fi
}
trap cleanup EXIT

human_time_ago() {
  local ts="$1"
  # Handle empty or non-numeric input
  [[ ! "$ts" =~ ^[0-9]+$ ]] && { echo "unknown"; return; }
  
  local now
  now=$(date +%s)
  local diff=$((now - ts / 1000))
  
  if [[ $diff -lt 3600 ]]; then
    echo "$((diff / 60)) minutes ago"
  elif [[ $diff -lt 86400 ]]; then
    echo "$((diff / 3600)) hours ago"
  elif [[ $diff -lt 2592000 ]]; then
    echo "$((diff / 86400)) days ago"
  elif [[ $diff -lt 31536000 ]]; then
    echo "$((diff / 2592000)) months ago"
  else
    echo "$((diff / 31536000)) years ago"
  fi
}

#-----------------------------------------------------------------------------
# Pattern Detection
#-----------------------------------------------------------------------------

SAFE_URL_PATTERNS=(
  'github\.com'
  'githubusercontent\.com'
  'npmjs\.(com|org)'
  'brew\.sh'
  'formulae\.brew\.sh'
  'pypi\.(org|python\.org)'
  'crates\.io'
  'rubygems\.org'
  'packagist\.org'
  'nuget\.org'
  'docs\.rs'
  'gitlab\.com'
  'bitbucket\.org'
  'registry\.npmmirror\.com'
  'yarnpkg\.com'
  'deno\.land'
  'jsr\.io'
)

check_suspicious_patterns() {
  local file="$1"
  local issues=()
  local content
  content=$(cat "$file" 2>/dev/null || echo "")
  
  # Base64 encoded commands
  if echo "$content" | grep -qE 'base64\s+(-d|--decode)|echo\s+[A-Za-z0-9+/=]{20,}\s*\|\s*(base64|sh|bash)'; then
    issues+=("base64_encoded_command")
  fi
  
  # Hex encoded content (long sequences)
  if echo "$content" | grep -qE '\\x[0-9a-fA-F]{2}(\\x[0-9a-fA-F]{2}){10,}'; then
    issues+=("hex_encoded_content")
  fi
  
  # macOS quarantine removal
  if echo "$content" | grep -qE 'xattr\s+(-d|-c).*quarantine'; then
    issues+=("quarantine_removal")
  fi
  
  # Pipe to shell
  if echo "$content" | grep -qE '(curl|wget)\s+[^|]*\|\s*(sh|bash|zsh|python|perl|ruby)'; then
    issues+=("pipe_to_shell")
  fi
  
  # Process substitution with curl
  if echo "$content" | grep -qE '(bash|sh|zsh)\s+<\s*\(\s*(curl|wget)'; then
    issues+=("process_substitution_curl")
  fi
  
  # Password-protected archives
  if echo "$content" | grep -qiE 'unzip\s+-P|7z\s+x\s+-p|password.*archive|archive.*password'; then
    issues+=("password_protected_archive")
  fi
  
  # Download + chmod + execute in sequence
  if echo "$content" | grep -qE 'chmod\s+\+x[^&;|]*&&[^&;|]*\.\/'; then
    issues+=("download_and_execute")
  fi
  
  # Eval with variable expansion
  if echo "$content" | grep -qE 'eval\s+["'"'"']?\$'; then
    issues+=("eval_variable")
  fi
  
  # Hidden file creation
  if echo "$content" | grep -qE '>\s*\.[a-zA-Z]|touch\s+\.[a-zA-Z]'; then
    issues+=("hidden_file_creation")
  fi
  
  # Cron/launchd persistence
  if echo "$content" | grep -qiE 'crontab|launchctl\s+load|LaunchAgents|LaunchDaemons'; then
    issues+=("persistence_mechanism")
  fi
  
  echo "${issues[*]:-}"
}

check_external_urls() {
  local file="$1"
  local unsafe_urls=()
  local content
  content=$(cat "$file" 2>/dev/null || echo "")
  
  # Extract URLs (improved regex)
  local urls
  urls=$(echo "$content" | grep -oE 'https?://[a-zA-Z0-9./?=_&%-]+' | sort -u || true)
  
  for url in $urls; do
    local is_safe=false
    for pattern in "${SAFE_URL_PATTERNS[@]}"; do
      if echo "$url" | grep -qE "$pattern"; then
        is_safe=true
        break
      fi
    done
    if [[ "$is_safe" == "false" ]]; then
      # Skip very short URLs (likely truncated)
      [[ ${#url} -gt 15 ]] && unsafe_urls+=("$url")
    fi
  done
  
  echo "${unsafe_urls[*]:-}"
}

check_bundled_binaries() {
  local dir="$1"
  local binaries=()
  
  while IFS= read -r -d '' file; do
    # Skip known safe extensions
    local ext="${file##*.}"
    case "$ext" in
      md|txt|json|yaml|yml|toml|js|mjs|cjs|ts|mts|tsx|jsx|py|sh|bash|zsh|rb|go|rs|java|c|cpp|h|hpp|css|scss|less|html|htm|xml|svg|png|jpg|jpeg|gif|ico|webp|woff|woff2|ttf|eot|otf|map|lock|log|env|example|sample|template|d.ts)
        continue ;;
    esac
    
    # Check if actually binary
    if file "$file" 2>/dev/null | grep -qE 'executable|binary|Mach-O|ELF|PE32'; then
      binaries+=("${file#$dir/}")
    fi
  done < <(find "$dir" -type f -print0 2>/dev/null)
  
  echo "${binaries[*]:-}"
}

#-----------------------------------------------------------------------------
# ClawHub Integration
#-----------------------------------------------------------------------------

fetch_skill_info() {
  local skill_slug="$1"
  local version="${2:-}"
  local dest_file="${3:-/tmp/pincer-info.json}"
  
  local output
  if [[ -n "$version" ]]; then
    output=$(clawhub inspect "$skill_slug" --version "$version" --json 2>&1)
  else
    output=$(clawhub inspect "$skill_slug" --json 2>&1)
  fi
  
  # Extract JSON (skip lines starting with -) and write to file
  echo "$output" | sed '/^-/d' | jq '.' > "$dest_file" 2>/dev/null || echo "{}" > "$dest_file"
  echo "$dest_file"
}

read_skill_info() {
  local file="$1"
  local key="$2"
  local default="$3"
  jq -r "$key // \"$default\"" "$file" 2>/dev/null || echo "$default"
}

fetch_skill_files() {
  local skill_slug="$1"
  local dest_dir="$2"
  local version="${3:-}"
  
  mkdir -p "$dest_dir"
  
  # Get file list
  local files_output
  files_output=$(clawhub inspect "$skill_slug" --files ${version:+--version "$version"} 2>&1)
  
  # Parse files from output (format: "filename  size  hash  type")
  local files
  files=$(echo "$files_output" | grep -E '^\S+\s+[0-9]+[BKM]' | awk '{print $1}' || true)
  
  if [[ -z "$files" ]]; then
    debug "No files found for $skill_slug"
    return 1
  fi
  
  # Download each file
  for file in $files; do
    local file_dir
    file_dir=$(dirname "$dest_dir/$file")
    mkdir -p "$file_dir"
    
    # Fetch file and strip any prefix lines (like "- Fetching skill")
    clawhub inspect "$skill_slug" --file "$file" ${version:+--version "$version"} 2>/dev/null | sed '/^- /d' > "$dest_dir/$file" || {
      debug "Failed to fetch $file"
    }
  done
  
  return 0
}

is_publisher_trusted() {
  local publisher="$1"
  local trusted
  trusted=$(jq -r '.trustedPublishers[]' "$CONFIG_FILE" 2>/dev/null || echo "")
  
  for tp in $trusted; do
    [[ "$tp" == "$publisher" ]] && return 0
  done
  return 1
}

is_publisher_blocked() {
  local publisher="$1"
  local blocked
  blocked=$(jq -r '.blockedPublishers[]' "$CONFIG_FILE" 2>/dev/null || echo "")
  
  for bp in $blocked; do
    [[ "$bp" == "$publisher" ]] && return 0
  done
  return 1
}

is_skill_blocked() {
  local skill="$1"
  local blocked
  blocked=$(jq -r '.blockedSkills[]' "$CONFIG_FILE" 2>/dev/null || echo "")
  
  for bs in $blocked; do
    [[ "$bs" == "$skill" ]] && return 0
  done
  return 1
}

#-----------------------------------------------------------------------------
# mcp-scan Integration
#-----------------------------------------------------------------------------

run_mcp_scan() {
  local target="$1"
  
  if ! command -v uvx &>/dev/null; then
    echo '{"error": "uvx not installed"}'
    return 1
  fi
  
  # Run mcp-scan and capture output
  local output
  output=$(uvx mcp-scan@latest --skills "$target" 2>&1) || true
  
  echo "$output"
}

parse_mcp_scan_result() {
  local output="$1"
  
  # Check for critical warnings
  if echo "$output" | grep -qiE 'malware|malicious|reverse.?shell|exfiltrat'; then
    echo "malware"
  elif echo "$output" | grep -qE '\[W00[789]\]|\[W01[012]\]'; then
    # W007: credential handling, W008: machine state, W009+: various high-risk
    echo "high_risk"
  elif echo "$output" | grep -qE '\[W0[0-9]{2}\]'; then
    echo "warnings"
  else
    echo "clean"
  fi
}

extract_mcp_warnings() {
  local output="$1"
  echo "$output" | grep -oE '\[W[0-9]{3}\][^│]*' | head -5 || true
}

#-----------------------------------------------------------------------------
# Scanning
#-----------------------------------------------------------------------------

scan_skill() {
  local skill_path="$1"
  local skill_name="${2:-$(basename "$skill_path")}"
  local skill_info="${3:-}"
  
  local risk_level="clean"
  local issues=()
  local warnings=()
  local scan_results=()
  
  [[ "$JSON_OUTPUT" != "true" ]] && {
    echo ""
    log "Scanning ${BOLD}$skill_name${NC}..."
    echo ""
  }
  
  # --- Publisher info ---
  local publisher downloads stars created_at age_str is_trusted
  if [[ -f "$skill_info" ]]; then
    publisher=$(read_skill_info "$skill_info" '.owner.handle' "unknown")
    downloads=$(read_skill_info "$skill_info" '.skill.stats.downloads' "0")
    stars=$(read_skill_info "$skill_info" '.skill.stats.stars' "0")
    created_at=$(read_skill_info "$skill_info" '.skill.createdAt' "0")
  else
    publisher="unknown"
    downloads="0"
    stars="0"
    created_at="0"
  fi
  
  if [[ "$created_at" != "0" && "$created_at" != "null" ]]; then
    age_str=$(human_time_ago "$created_at")
  else
    age_str="unknown"
  fi
  
  is_trusted=false
  is_publisher_trusted "$publisher" && is_trusted=true
  
  [[ "$JSON_OUTPUT" != "true" ]] && {
    local trust_badge=""
    $is_trusted && trust_badge=" ${GREEN}(trusted)${NC}" || trust_badge=" ${DIM}(unknown)${NC}"
    echo -e "  ${CYAN}Publisher:${NC} ${BOLD}$publisher${NC}$trust_badge"
    echo -e "  ${CYAN}Stats:${NC} $downloads downloads · $stars ★ · created $age_str"
    echo ""
  }
  
  # Check blocked
  if is_skill_blocked "$skill_name"; then
    risk_level="blocked"
    issues+=("Skill is on blocklist")
    [[ "$JSON_OUTPUT" != "true" ]] && danger "Skill is BLOCKED in your config"
  fi
  
  if is_publisher_blocked "$publisher"; then
    risk_level="blocked"
    issues+=("Publisher is on blocklist")
    [[ "$JSON_OUTPUT" != "true" ]] && danger "Publisher is BLOCKED in your config"
  fi
  
  # Check minimum requirements
  local min_downloads min_age_days
  min_downloads=$(jq -r '.minDownloads // 0' "$CONFIG_FILE")
  min_age_days=$(jq -r '.minAgeDays // 0' "$CONFIG_FILE")
  
  if [[ "$downloads" -lt "$min_downloads" ]]; then
    [[ "$risk_level" == "clean" ]] && risk_level="caution"
    warnings+=("Downloads ($downloads) below minimum ($min_downloads)")
  fi
  
  if [[ "$created_at" != "0" && "$created_at" != "null" && "$min_age_days" -gt 0 ]]; then
    local age_days=$(( ($(date +%s) - created_at / 1000) / 86400 ))
    if [[ "$age_days" -lt "$min_age_days" ]]; then
      [[ "$risk_level" == "clean" ]] && risk_level="caution"
      warnings+=("Age ($age_days days) below minimum ($min_age_days)")
    fi
  fi
  
  # --- mcp-scan ---
  [[ "$JSON_OUTPUT" != "true" ]] && info "Running mcp-scan..."
  local mcp_output mcp_result mcp_warnings
  mcp_output=$(run_mcp_scan "$skill_path" 2>&1)
  mcp_result=$(parse_mcp_scan_result "$mcp_output")
  mcp_warnings=$(extract_mcp_warnings "$mcp_output")
  
  scan_results+=("mcp_scan:$mcp_result")
  
  case "$mcp_result" in
    malware)
      risk_level="malware"
      issues+=("mcp-scan: potential malware detected")
      [[ "$JSON_OUTPUT" != "true" ]] && danger "mcp-scan: ${RED}MALWARE DETECTED${NC}"
      ;;
    high_risk)
      [[ "$risk_level" =~ ^(clean|caution)$ ]] && risk_level="danger"
      issues+=("mcp-scan: high-risk patterns detected")
      [[ "$JSON_OUTPUT" != "true" ]] && danger "mcp-scan: high-risk warnings"
      ;;
    warnings)
      [[ "$risk_level" == "clean" ]] && risk_level="caution"
      warnings+=("mcp-scan: some warnings (review recommended)")
      [[ "$JSON_OUTPUT" != "true" ]] && warn "mcp-scan: warnings (likely benign)"
      ;;
    clean)
      [[ "$JSON_OUTPUT" != "true" ]] && ok "mcp-scan: passed"
      ;;
  esac
  
  [[ -n "$mcp_warnings" && "$JSON_OUTPUT" != "true" ]] && {
    echo "$mcp_warnings" | while read -r w; do
      echo -e "    ${DIM}$w${NC}"
    done
  }
  
  # --- Pattern checks ---
  [[ "$JSON_OUTPUT" != "true" ]] && info "Checking for suspicious patterns..."
  local all_issues=""
  
  # Scan SKILL.md
  [[ -f "$skill_path/SKILL.md" ]] && all_issues+=" $(check_suspicious_patterns "$skill_path/SKILL.md")"
  
  # Scan all scripts
  while IFS= read -r -d '' script; do
    all_issues+=" $(check_suspicious_patterns "$script")"
  done < <(find "$skill_path" -type f \( -name "*.sh" -o -name "*.bash" -o -name "*.py" -o -name "*.js" \) -print0 2>/dev/null)
  
  all_issues=$(echo "$all_issues" | tr ' ' '\n' | sort -u | grep -v '^$' | tr '\n' ' ' || true)
  
  if [[ -n "${all_issues// /}" ]]; then
    [[ "$risk_level" =~ ^(clean|caution)$ ]] && risk_level="danger"
    for issue in $all_issues; do
      case "$issue" in
        base64_encoded_command) issues+=("Base64 encoded command") ;;
        hex_encoded_content) issues+=("Hex encoded content") ;;
        quarantine_removal) issues+=("macOS quarantine removal (xattr)") ;;
        pipe_to_shell) issues+=("curl/wget piped to shell") ;;
        process_substitution_curl) issues+=("Process substitution with curl") ;;
        password_protected_archive) issues+=("Password-protected archive") ;;
        download_and_execute) issues+=("Download and execute pattern") ;;
        eval_variable) issues+=("Eval with variable expansion") ;;
        hidden_file_creation) issues+=("Hidden file creation") ;;
        persistence_mechanism) issues+=("Persistence mechanism (cron/launchd)") ;;
      esac
    done
    [[ "$JSON_OUTPUT" != "true" ]] && {
      danger "Pattern check: suspicious patterns found"
      for issue in "${issues[@]}"; do
        echo -e "    ${RED}•${NC} $issue"
      done
    }
  else
    scan_results+=("patterns:clean")
    [[ "$JSON_OUTPUT" != "true" ]] && ok "Pattern check: passed"
  fi
  
  # --- URL checks ---
  [[ "$JSON_OUTPUT" != "true" ]] && info "Checking external URLs..."
  local unsafe_urls=""
  [[ -f "$skill_path/SKILL.md" ]] && unsafe_urls=$(check_external_urls "$skill_path/SKILL.md")
  
  if [[ -n "$unsafe_urls" ]]; then
    [[ "$risk_level" == "clean" ]] && risk_level="caution"
    warnings+=("External URLs not on allowlist")
    scan_results+=("urls:external")
    [[ "$JSON_OUTPUT" != "true" ]] && {
      warn "URL check: external URLs found"
      for url in $unsafe_urls; do
        echo -e "    ${YELLOW}•${NC} $url"
      done
    }
  else
    scan_results+=("urls:clean")
    [[ "$JSON_OUTPUT" != "true" ]] && ok "URL check: passed"
  fi
  
  # --- Binary checks ---
  [[ "$JSON_OUTPUT" != "true" ]] && info "Checking for bundled binaries..."
  local binaries
  binaries=$(check_bundled_binaries "$skill_path")
  
  if [[ -n "$binaries" ]]; then
    [[ "$risk_level" =~ ^(clean|caution)$ ]] && risk_level="danger"
    issues+=("Bundled binary executables")
    scan_results+=("binaries:found")
    [[ "$JSON_OUTPUT" != "true" ]] && {
      danger "Binary check: executables found"
      for bin in $binaries; do
        echo -e "    ${RED}•${NC} $bin"
      done
    }
  else
    scan_results+=("binaries:clean")
    [[ "$JSON_OUTPUT" != "true" ]] && ok "Binary check: passed"
  fi
  
  # --- Summary ---
  if [[ "$JSON_OUTPUT" == "true" ]]; then
    jq -n \
      --arg name "$skill_name" \
      --arg risk "$risk_level" \
      --arg publisher "$publisher" \
      --argjson downloads "$downloads" \
      --argjson stars "$stars" \
      --arg age "$age_str" \
      --argjson trusted "$is_trusted" \
      --argjson issues "$(printf '%s\n' "${issues[@]}" | jq -R . | jq -s .)" \
      --argjson warnings "$(printf '%s\n' "${warnings[@]}" | jq -R . | jq -s .)" \
      '{
        skill: $name,
        riskLevel: $risk,
        publisher: {handle: $publisher, trusted: $trusted},
        stats: {downloads: $downloads, stars: $stars, age: $age},
        issues: $issues,
        warnings: $warnings
      }'
  else
    echo ""
    echo -e "${BOLD}Risk Assessment:${NC}"
    case "$risk_level" in
      clean)
        echo -e "  ${GREEN}${CHECK} CLEAN${NC} — No issues detected"
        ;;
      caution)
        echo -e "  ${YELLOW}${WARN} CAUTION${NC} — Review recommended"
        for w in "${warnings[@]}"; do
          echo -e "    ${YELLOW}•${NC} $w"
        done
        ;;
      danger)
        echo -e "  ${RED}${DANGER} DANGER${NC} — Suspicious patterns detected"
        for i in "${issues[@]}"; do
          echo -e "    ${RED}•${NC} $i"
        done
        ;;
      malware)
        echo -e "  ${RED}${SKULL} MALWARE${NC} — Known malicious patterns detected"
        for i in "${issues[@]}"; do
          echo -e "    ${RED}•${NC} $i"
        done
        ;;
      blocked)
        echo -e "  ${RED}⛔ BLOCKED${NC} — Skill or publisher is blocked"
        for i in "${issues[@]}"; do
          echo -e "    ${RED}•${NC} $i"
        done
        ;;
    esac
    echo ""
  fi
  
  # Store result for caller
  echo "$risk_level" > /tmp/pincer-risk-level
}

#-----------------------------------------------------------------------------
# Commands
#-----------------------------------------------------------------------------

cmd_install() {
  local skill_spec="$1"
  local force=false
  shift || true
  
  for arg in "$@"; do
    [[ "$arg" == "--force" ]] && force=true
  done
  
  # Parse skill@version
  local skill_name="${skill_spec%@*}"
  local skill_version=""
  [[ "$skill_spec" == *"@"* ]] && skill_version="${skill_spec#*@}"
  
  [[ "$JSON_OUTPUT" != "true" ]] && {
    log "v$VERSION"
    echo ""
    info "Fetching ${BOLD}$skill_name${NC} from ClawHub..."
  }
  
  # Fetch skill info
  local skill_info_file
  skill_info_file=$(fetch_skill_info "$skill_name" "$skill_version")
  
  if [[ ! -s "$skill_info_file" ]]; then
    error "Could not fetch skill info for: $skill_name"
    exit 1
  fi
  
  # Create temp directory and fetch files
  TEMP_DIR=$(mktemp -d)
  local skill_dir="$TEMP_DIR/$skill_name"
  
  [[ "$JSON_OUTPUT" != "true" ]] && info "Downloading for security scan..."
  
  if ! fetch_skill_files "$skill_name" "$skill_dir" "$skill_version"; then
    warn "Could not download skill files. Attempting install-based scan..."
    # Fallback: install to temp and scan
    mkdir -p "$skill_dir"
    if ! clawhub install "$skill_spec" --dir "$TEMP_DIR" --no-input 2>/dev/null; then
      error "Could not download skill for scanning."
      exit 1
    fi
  fi
  
  # Run scan
  scan_skill "$skill_dir" "$skill_name" "$skill_info_file"
  
  local risk_level
  risk_level=$(cat /tmp/pincer-risk-level 2>/dev/null || echo "unknown")
  rm -f /tmp/pincer-risk-level
  
  # Decision
  if [[ "$JSON_OUTPUT" == "true" ]]; then
    # In JSON mode, just output the scan result
    return 0
  fi
  
  case "$risk_level" in
    clean)
      local auto_approve
      auto_approve=$(jq -r '.autoApprove // "clean"' "$CONFIG_FILE")
      if [[ "$auto_approve" == "clean" ]]; then
        info "Auto-approved (clean + trusted config)."
      else
        echo -n "Proceed with install? [Y/n] "
        read -r response
        [[ "$response" =~ ^[Nn] ]] && { log "Cancelled."; exit 0; }
      fi
      ;;
    caution)
      echo -n "Warnings detected. Proceed? [y/N] "
      read -r response
      [[ ! "$response" =~ ^[Yy] ]] && { log "Cancelled."; exit 0; }
      ;;
    danger)
      if [[ "$force" != "true" ]]; then
        error "Install blocked. Use --force to override (not recommended)."
        exit 1
      fi
      warn "Force flag set. Proceeding despite risks..."
      ;;
    malware|blocked)
      error "Install blocked. This skill has been flagged as dangerous."
      [[ "$force" == "true" ]] && error "--force cannot override malware/blocked status."
      exit 1
      ;;
  esac
  
  # Install
  echo ""
  info "Installing $skill_name..."
  if clawhub install "$skill_spec" --no-input; then
    ok "Installed successfully!"
    
    # Log
    if jq -e '.logInstalls == true' "$CONFIG_FILE" >/dev/null 2>&1; then
      local entry
      entry=$(jq -n \
        --arg name "$skill_name" \
        --arg version "${skill_version:-latest}" \
        --arg risk "$risk_level" \
        --arg publisher "$(read_skill_info "$skill_info_file" '.owner.handle' "unknown")" \
        --arg time "$(date -u +"%Y-%m-%dT%H:%M:%SZ")" \
        '{name: $name, version: $version, risk: $risk, publisher: $publisher, installedAt: $time}')
      jq ". += [$entry]" "$HISTORY_FILE" > "${HISTORY_FILE}.tmp" && mv "${HISTORY_FILE}.tmp" "$HISTORY_FILE"
    fi
  else
    error "Installation failed."
    exit 1
  fi
}

cmd_scan() {
  local target="${1:-}"
  
  [[ -z "$target" ]] && { error "Usage: pincer scan <skill|path>"; exit 1; }
  
  [[ "$JSON_OUTPUT" != "true" ]] && log "v$VERSION"
  
  if [[ -d "$target" ]]; then
    # Local directory
    scan_skill "$target" "$(basename "$target")" "{}"
  else
    # ClawHub skill
    TEMP_DIR=$(mktemp -d)
    local skill_dir="$TEMP_DIR/$target"
    
    [[ "$JSON_OUTPUT" != "true" ]] && info "Fetching $target from ClawHub..."
    
    local skill_info_file
    skill_info_file=$(fetch_skill_info "$target")
    
    if fetch_skill_files "$target" "$skill_dir"; then
      scan_skill "$skill_dir" "$target" "$skill_info_file"
    else
      error "Could not fetch skill: $target"
      exit 1
    fi
  fi
}

cmd_audit() {
  [[ "$JSON_OUTPUT" != "true" ]] && {
    log "v$VERSION"
    echo ""
    info "Auditing installed skills..."
    echo ""
  }
  
  local skills_dir="/opt/homebrew/lib/node_modules/openclaw/skills"
  [[ ! -d "$skills_dir" ]] && skills_dir="/usr/local/lib/node_modules/openclaw/skills"
  
  if [[ ! -d "$skills_dir" ]]; then
    error "Skills directory not found"
    exit 1
  fi
  
  local total=0 clean=0 caution=0 danger_count=0
  local results=()
  
  for skill_path in "$skills_dir"/*/; do
    [[ -d "$skill_path" ]] || continue
    local skill_name
    skill_name=$(basename "$skill_path")
    ((total++))
    
    # Quick scan (pattern + binary checks, skip mcp-scan for speed)
    local issues=""
    [[ -f "$skill_path/SKILL.md" ]] && issues=$(check_suspicious_patterns "$skill_path/SKILL.md")
    
    local binaries
    binaries=$(check_bundled_binaries "$skill_path")
    
    local status="clean"
    if [[ -n "$issues" || -n "$binaries" ]]; then
      status="danger"
      ((danger_count++))
    elif [[ -n "$(check_external_urls "$skill_path/SKILL.md" 2>/dev/null)" ]]; then
      status="caution"
      ((caution++))
    else
      ((clean++))
    fi
    
    if [[ "$JSON_OUTPUT" == "true" ]]; then
      results+=("{\"name\":\"$skill_name\",\"status\":\"$status\"}")
    else
      case "$status" in
        clean) ok "$skill_name" ;;
        caution) warn "$skill_name (external URLs)" ;;
        danger) danger "$skill_name" ;;
      esac
    fi
  done
  
  if [[ "$JSON_OUTPUT" == "true" ]]; then
    echo "{\"total\":$total,\"clean\":$clean,\"caution\":$caution,\"danger\":$danger_count,\"skills\":[$(IFS=,; echo "${results[*]}")]}"
  else
    echo ""
    echo -e "${BOLD}Summary:${NC} $total skills"
    echo -e "  ${GREEN}${CHECK}${NC} Clean: $clean"
    echo -e "  ${YELLOW}${WARN}${NC} Caution: $caution"
    echo -e "  ${RED}${DANGER}${NC} Danger: $danger_count"
    
    [[ $danger_count -gt 0 ]] && {
      echo ""
      warn "Run 'pincer scan <skill>' for detailed analysis."
    }
  fi
}

cmd_trust() {
  local action="${1:-list}"
  local value="${2:-}"
  
  case "$action" in
    add)
      [[ -z "$value" ]] && { error "Usage: pincer trust add <publisher>"; exit 1; }
      jq --arg v "$value" '.trustedPublishers += [$v] | .trustedPublishers |= unique' "$CONFIG_FILE" > "${CONFIG_FILE}.tmp"
      mv "${CONFIG_FILE}.tmp" "$CONFIG_FILE"
      ok "Added '$value' to trusted publishers."
      ;;
    remove)
      [[ -z "$value" ]] && { error "Usage: pincer trust remove <publisher>"; exit 1; }
      jq --arg v "$value" '.trustedPublishers -= [$v]' "$CONFIG_FILE" > "${CONFIG_FILE}.tmp"
      mv "${CONFIG_FILE}.tmp" "$CONFIG_FILE"
      ok "Removed '$value' from trusted publishers."
      ;;
    list)
      if [[ "$JSON_OUTPUT" == "true" ]]; then
        jq '{trustedPublishers, blockedPublishers, blockedSkills}' "$CONFIG_FILE"
      else
        echo -e "${BOLD}Trusted Publishers:${NC}"
        jq -r '.trustedPublishers[]' "$CONFIG_FILE" 2>/dev/null | while read -r p; do
          echo -e "  ${GREEN}✓${NC} $p"
        done
        echo ""
        echo -e "${BOLD}Blocked Publishers:${NC}"
        jq -r '.blockedPublishers[]' "$CONFIG_FILE" 2>/dev/null | while read -r p; do
          echo -e "  ${RED}✗${NC} $p"
        done || echo "  (none)"
        echo ""
        echo -e "${BOLD}Blocked Skills:${NC}"
        jq -r '.blockedSkills[]' "$CONFIG_FILE" 2>/dev/null | while read -r s; do
          echo -e "  ${RED}✗${NC} $s"
        done || echo "  (none)"
      fi
      ;;
    block)
      [[ -z "$value" ]] && { error "Usage: pincer trust block <publisher|skill>"; exit 1; }
      if [[ "$value" == *"/"* ]]; then
        jq --arg v "$value" '.blockedSkills += [$v] | .blockedSkills |= unique' "$CONFIG_FILE" > "${CONFIG_FILE}.tmp"
      else
        jq --arg v "$value" '.blockedPublishers += [$v] | .blockedPublishers |= unique' "$CONFIG_FILE" > "${CONFIG_FILE}.tmp"
      fi
      mv "${CONFIG_FILE}.tmp" "$CONFIG_FILE"
      ok "Blocked '$value'."
      ;;
    unblock)
      [[ -z "$value" ]] && { error "Usage: pincer trust unblock <publisher|skill>"; exit 1; }
      jq --arg v "$value" '.blockedPublishers -= [$v] | .blockedSkills -= [$v]' "$CONFIG_FILE" > "${CONFIG_FILE}.tmp"
      mv "${CONFIG_FILE}.tmp" "$CONFIG_FILE"
      ok "Unblocked '$value'."
      ;;
    *)
      error "Unknown trust action: $action"
      echo "Usage: pincer trust <add|remove|list|block|unblock> [value]"
      exit 1
      ;;
  esac
}

cmd_history() {
  if [[ ! -s "$HISTORY_FILE" ]] || [[ "$(cat "$HISTORY_FILE")" == "[]" ]]; then
    [[ "$JSON_OUTPUT" == "true" ]] && echo "[]" || info "No installation history."
    return 0
  fi
  
  if [[ "$JSON_OUTPUT" == "true" ]]; then
    cat "$HISTORY_FILE"
  else
    echo -e "${BOLD}Installation History:${NC}"
    echo ""
    jq -r '.[-20:] | reverse | .[] | "  \(.installedAt | split("T")[0]) │ \(.name) │ \(.publisher // "?") │ \(.risk)"' "$HISTORY_FILE"
  fi
}

cmd_config() {
  local action="${1:-show}"
  
  case "$action" in
    show)
      if [[ "$JSON_OUTPUT" == "true" ]]; then
        cat "$CONFIG_FILE"
      else
        echo -e "${BOLD}Configuration:${NC} $CONFIG_FILE"
        echo ""
        cat "$CONFIG_FILE" | jq .
      fi
      ;;
    edit)
      ${EDITOR:-nano} "$CONFIG_FILE"
      ;;
    reset)
      rm -f "$CONFIG_FILE"
      ensure_config
      ok "Config reset to defaults."
      ;;
    *)
      error "Unknown config action: $action"
      exit 1
      ;;
  esac
}

cmd_help() {
  cat << EOF
${SHIELD} pincer v$VERSION — Security-first skill installation

${BOLD}Usage:${NC}
  pincer install <skill[@version]>   Install with security scan
  pincer scan <skill|path>           Scan without installing
  pincer audit                        Quick-scan all installed skills
  pincer trust <action> [value]      Manage trust/block lists
  pincer history                      View installation history
  pincer config [show|edit|reset]    Manage configuration
  pincer help                         Show this help

${BOLD}Options:${NC}
  --json       Output JSON (for scripting)
  --force      Override security blocks (not for malware)

${BOLD}Trust Actions:${NC}
  add <publisher>      Add to trusted list
  remove <publisher>   Remove from trusted list
  block <name>         Block a publisher or skill
  unblock <name>       Remove from blocklist
  list                 Show all trust settings

${BOLD}Examples:${NC}
  pincer install bird
  pincer scan ./my-skill --json
  pincer trust add steipete
  pincer trust block suspicious-dev
  pincer audit

${BOLD}Config:${NC} ~/.config/pincer/config.json
EOF
}

#-----------------------------------------------------------------------------
# Main
#-----------------------------------------------------------------------------

main() {
  # Parse global flags
  local args=()
  for arg in "$@"; do
    case "$arg" in
      --json) JSON_OUTPUT=true ;;
      *) args+=("$arg") ;;
    esac
  done
  set -- "${args[@]}"
  
  ensure_config
  
  local cmd="${1:-help}"
  shift || true
  
  case "$cmd" in
    install) ensure_deps; cmd_install "$@" ;;
    scan) ensure_deps; cmd_scan "$@" ;;
    audit) cmd_audit ;;
    trust) cmd_trust "$@" ;;
    history) cmd_history ;;
    config) cmd_config "$@" ;;
    help|--help|-h) cmd_help ;;
    version|--version|-v) echo "pincer v$VERSION" ;;
    *) error "Unknown command: $cmd"; cmd_help; exit 1 ;;
  esac
}

main "$@"
