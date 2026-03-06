#!/usr/bin/env bash
# skill-audit.sh — Security scanner for ClawHub skills
# Usage: skill-audit.sh [--json] [--sarif] [--summary] [--verbose] [--exclude-self] [--max-file-size N] [--max-depth N] <skill-directory>
# Returns: 0 = clean, 1 = warnings only, 2 = critical findings
#
# Detection patterns are base64-encoded in patterns.b64 to prevent
# antivirus false positives (security tools that detect malware often
# get flagged AS malware because they contain the signatures).

set -uo pipefail

SCAN_START=$(date +%s)

# --- Pattern Loading (AV-safe) ---
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PATTERNS_FILE="$SCRIPT_DIR/patterns.b64"

load_pattern() {
  local name="$1"
  if [ -f "$PATTERNS_FILE" ]; then
    grep "^${name}:" "$PATTERNS_FILE" 2>/dev/null | cut -d: -f2 | base64 -d 2>/dev/null
  fi
}

# Pre-load encoded patterns
P_REVSHELL=$(load_pattern "REVSHELL")
P_EXFIL_CURL=$(load_pattern "EXFIL_CURL")
P_PIPE_SHELL=$(load_pattern "PIPE_SHELL")
P_B64_EXEC=$(load_pattern "B64_EXEC")
P_SUBPROCESS_NET=$(load_pattern "SUBPROCESS_NET")
P_GATEKEEPER=$(load_pattern "GATEKEEPER")
P_CLICKFIX=$(load_pattern "CLICKFIX")
P_SUS_PKG=$(load_pattern "SUS_PKG")
P_KNOWN_IPS=$(load_pattern "KNOWN_IPS")
P_EXFIL_ENDPOINTS=$(load_pattern "EXFIL_ENDPOINTS")
P_BAD_ACTORS=$(load_pattern "BAD_ACTORS")
P_FAKE_UPDATE=$(load_pattern "FAKE_UPDATE")
P_DEVTCP_SHELL=$(load_pattern "DEVTCP_SHELL")
P_NOHUP_NET=$(load_pattern "NOHUP_NET")
P_PY_REVSHELL=$(load_pattern "PY_REVSHELL")
P_TMPDIR_STAGE=$(load_pattern "TMPDIR_STAGE")
P_GITHUB_RAW=$(load_pattern "GITHUB_RAW")
P_ECHO_B64=$(load_pattern "ECHO_B64")

# Fallbacks if patterns file missing
[ -z "$P_REVSHELL" ] && P_REVSHELL='(mkfifo|ncat\s)'
[ -z "$P_EXFIL_CURL" ] && P_EXFIL_CURL='(curl.*--data)'
[ -z "$P_PIPE_SHELL" ] && P_PIPE_SHELL='(curl.*\|.*sh)'
[ -z "$P_B64_EXEC" ] && P_B64_EXEC='(base64.*-d.*\|.*sh)'
[ -z "$P_SUBPROCESS_NET" ] && P_SUBPROCESS_NET='(os\.system.*curl)'
[ -z "$P_GATEKEEPER" ] && P_GATEKEEPER='(xattr.*curl)'
[ -z "$P_CLICKFIX" ] && P_CLICKFIX='(chmod.*&&.*\.\/)'
[ -z "$P_SUS_PKG" ] && P_SUS_PKG='(npm.*--registry)'
[ -z "$P_KNOWN_IPS" ] && P_KNOWN_IPS='(0\.0\.0\.0)'
[ -z "$P_EXFIL_ENDPOINTS" ] && P_EXFIL_ENDPOINTS='(webhook\.site|ngrok\.io)'
[ -z "$P_BAD_ACTORS" ] && P_BAD_ACTORS='(zaycv|Ddoy233)'
[ -z "$P_FAKE_UPDATE" ] && P_FAKE_UPDATE='(apple software update|microsoft update)'
[ -z "$P_DEVTCP_SHELL" ] && P_DEVTCP_SHELL='(/dev/tcp/)'
[ -z "$P_NOHUP_NET" ] && P_NOHUP_NET='(nohup.*curl)'
[ -z "$P_PY_REVSHELL" ] && P_PY_REVSHELL='(socket\.socket.*connect.*dup2)'
[ -z "$P_TMPDIR_STAGE" ] && P_TMPDIR_STAGE='(\$TMPDIR/[a-z])'
[ -z "$P_GITHUB_RAW" ] && P_GITHUB_RAW='(raw\.githubusercontent)'
[ -z "$P_ECHO_B64" ] && P_ECHO_B64='(echo.*base64)'

# --- Portable grep -P replacement ---
# macOS stock grep doesn't support -P (Perl regex). Use ggrep if available, else fall back to LC_ALL trick.
GREP_CMD="grep"
if ! grep -P '.' /dev/null 2>/dev/null; then
  if command -v ggrep &>/dev/null; then
    GREP_CMD="ggrep"
  fi
fi

# Test if our grep supports -P
GREP_HAS_P=0
if echo "test" | $GREP_CMD -P 'test' &>/dev/null; then
  GREP_HAS_P=1
fi

grep_p() {
  # Portable grep -P: uses $GREP_CMD -P if available, else falls back to perl
  if [ $GREP_HAS_P -eq 1 ]; then
    $GREP_CMD -Pq "$@"
  else
    local pattern="$1"
    shift
    if command -v perl &>/dev/null; then
      perl -CSDA -0777 -ne "exit(/$pattern/ ? 0 : 1)" "$@" 2>/dev/null
      return $?
    fi
    return 1
  fi
}

# --- CLI Args ---
JSON_MODE=0
SARIF_MODE=0
SUMMARY_MODE=0
VERBOSE=0
EXCLUDE_SELF=0
MAX_FILE_SIZE=0  # 0 = unlimited
MAX_DEPTH=0      # 0 = unlimited
while [[ "${1:-}" == --* ]]; do
  case "$1" in
    --json) JSON_MODE=1; shift ;;
    --sarif) SARIF_MODE=1; shift ;;
    --summary) SUMMARY_MODE=1; shift ;;
    --verbose) VERBOSE=1; shift ;;
    --exclude-self) EXCLUDE_SELF=1; shift ;;
    --max-file-size) MAX_FILE_SIZE="${2:?--max-file-size requires a value (bytes)}"; shift 2 ;;
    --max-depth) MAX_DEPTH="${2:?--max-depth requires a value}"; shift 2 ;;
    *) echo "Unknown flag: $1" >&2; exit 2 ;;
  esac
done

SKILL_DIR_ARG="${1:?Usage: skill-audit.sh [--json] [--sarif] [--summary] [--verbose] [--exclude-self] [--max-file-size N] [--max-depth N] <skill-directory>}"

if [ ! -d "$SKILL_DIR_ARG" ]; then
  echo "Directory not found: $SKILL_DIR_ARG" >&2
  exit 2
fi

# Resolve to real path so grep -r works on symlinked directories (macOS quirk)
SKILL_DIR="$(cd "$SKILL_DIR_ARG" 2>/dev/null && pwd)"
SKILL_NAME="$(basename "$SKILL_DIR")"

# --- Self-detection ---
REAL_SCRIPT_DIR="$(cd "$SCRIPT_DIR/.." 2>/dev/null && pwd)"
REAL_SKILL_DIR="$SKILL_DIR"
if [ $EXCLUDE_SELF -eq 1 ] && [ "$REAL_SKILL_DIR" = "$REAL_SCRIPT_DIR" ]; then
  if [ $JSON_MODE -eq 1 ]; then
    printf '{"skill":%s,"path":%s,"files_scanned":"0","summary":{"critical":0,"warnings":0,"status":"clean","self_excluded":true},"findings":[]}\n' \
      "\"$SKILL_NAME\"" "\"$SKILL_DIR\""
  elif [ $SUMMARY_MODE -eq 1 ]; then
    echo "skillvet: $SKILL_NAME — clean (self-excluded)"
  else
    echo "Skipping self-scan (--exclude-self): $SKILL_NAME"
  fi
  exit 0
fi

# --- .skillvetrc config ---
DISABLED_CHECKS=""
SKILLVETRC="$SKILL_DIR/.skillvetrc"
if [ -f "$SKILLVETRC" ]; then
  while IFS= read -r rc_line; do
    rc_line="${rc_line%%#*}"         # strip comments
    rc_line="$(echo "$rc_line" | xargs 2>/dev/null)" # trim whitespace
    [ -z "$rc_line" ] && continue
    case "$rc_line" in
      disable:*) DISABLED_CHECKS+="${rc_line#disable:} " ;;
    esac
  done < "$SKILLVETRC"
fi

is_check_disabled() {
  local check_num="$1"
  [[ " $DISABLED_CHECKS " == *" $check_num "* ]]
}

RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
NC='\033[0m'

CRITICAL=0
WARNINGS=0
FINDINGS=""
JSON_FINDINGS=""
CHECKS_RUN=0
RISK_SCORE=0
SKIPPED_BINARY=0
SKIPPED_SIZE=0

# Severity weights for risk scoring (1-10 scale)
declare -A SEVERITY_WEIGHT=(
  [1]=7 [2]=9 [3]=8 [4]=7 [5]=8 [6]=9 [7]=10 [8]=8 [9]=7 [10]=8
  [11]=9 [12]=6 [13]=8 [14]=7 [15]=7 [16]=6 [17]=5 [18]=6 [19]=5 [20]=4
  [21]=9 [22]=7 [23]=9 [24]=8 [25]=10 [26]=7 [27]=6 [28]=7 [29]=9 [30]=8
  [31]=3 [32]=9 [33]=7 [34]=9 [35]=9 [36]=7 [37]=6
  [49]=9 [50]=8 [51]=9 [52]=7 [53]=9 [54]=7
  [W1]=2 [W2]=2 [W3]=2 [W4]=3 [W5]=2 [W6]=4 [W7]=3 [W8]=5
)

# Remediation hints per check
declare -A REMEDIATION=(
  [1]="Remove references to known exfiltration services. Use legitimate API endpoints instead."
  [2]="Do not bulk-harvest environment variables. Access only specific variables you need."
  [3]="Do not access credentials belonging to the host agent or platform. Declare needed keys in SKILL.md."
  [4]="Remove eval/Function constructors and base64/hex obfuscation. Write readable code."
  [5]="Do not access files outside the skill directory. Remove path traversal patterns."
  [6]="Do not send environment data or file contents to external servers via curl/wget."
  [7]="Remove reverse shell patterns. Skills must not open remote shell access."
  [8]="Do not read .env files programmatically. Use declared environment variables."
  [9]="Remove prompt injection text. Do not instruct LLMs to ignore rules."
  [10]="Do not instruct the LLM to send, email, or exfiltrate secrets."
  [11]="Do not modify agent config files (AGENTS.md, SOUL.md, etc.)."
  [12]="Remove zero-width and bidirectional Unicode characters from source."
  [13]="Do not include curl-pipe-to-bash in SKILL.md setup instructions."
  [14]="Do not instruct users to download external binaries. Use package managers."
  [15]="Remove .env files from the skill. Use .env.example templates instead."
  [16]="Replace Cyrillic lookalike characters with proper Latin equivalents."
  [17]="Remove raw ANSI escape sequences from data files."
  [18]="Replace punycode (xn--) domains with standard ASCII domains."
  [19]="Remove double-encoded percent sequences (%25XX)."
  [20]="Replace shortened URLs with full destination URLs."
  [21]="Do not pipe remote content to shell interpreters."
  [22]="Do not construct dangerous function names from string fragments."
  [23]="Separate secret-reading, encoding, and network code into different modules."
  [24]="Remove date-gated or long-delayed execution patterns."
  [25]="Remove references to known C2/malware IPs."
  [26]="Do not reference password-protected archives in documentation."
  [27]="Do not reference paste services for hosting code."
  [28]="Do not link to binary downloads from GitHub releases in docs."
  [29]="Do not pipe base64-decoded content to shell interpreters."
  [30]="Do not use subprocess calls to execute network commands."
  [31]="Remove decoy URLs that mislead about the actual destination."
  [32]="Do not combine background persistence (nohup/disown) with network access."
  [33]="Link prerequisites to official sources (npm, pip, brew, apt)."
  [34]="Do not bypass macOS Gatekeeper with xattr -c on downloaded files."
  [35]="Do not chain download+chmod+execute in a single command."
  [36]="Install packages from official registries only (npmjs.com, pypi.org)."
  [37]="Use well-known packages. Avoid suspicious -core/-base/-lib suffixed names."
  [49]="Replace Cyrillic/Greek lookalike characters in URLs with standard ASCII. This is a homograph attack."
  [50]="Remove zero-width and bidi override Unicode characters. These hide malicious content in plain sight."
  [51]="Replace punycode (xn--) domains with standard ASCII domains or explain their legitimate use."
  [52]="Remove credentials from URLs. Use environment variables or config files for authentication."
  [53]="Do not write to dotfiles (.bashrc, .ssh/authorized_keys, .gitconfig). Declare config requirements in SKILL.md."
  [54]="Replace shortened URLs with full destination URLs so the target can be verified."
)

json_escape() {
  local s="$1"
  s="${s//\\/\\\\}"
  s="${s//\"/\\\"}"
  s="${s//$'\n'/\\n}"
  s="${s//$'\t'/\\t}"
  printf '"%s"' "$s"
}

verbose() {
  if [ $VERBOSE -eq 1 ] && [ $JSON_MODE -eq 0 ] && [ $SARIF_MODE -eq 0 ] && [ $SUMMARY_MODE -eq 0 ]; then
    printf "${CYAN}  [verbose]${NC} %s\n" "$*"
  fi
}

add_finding() {
  local severity="$1" file="$2" line="$3" desc="$4" check_id="${5:-}" weight=0
  if [ -n "$check_id" ] && [ -n "${SEVERITY_WEIGHT[$check_id]:-}" ]; then
    weight=${SEVERITY_WEIGHT[$check_id]}
  fi
  if [ "$severity" = "CRITICAL" ]; then
    FINDINGS+="${RED}CRITICAL${NC} [$file:$line] $desc\n"
    CRITICAL=$((CRITICAL + 1))
    RISK_SCORE=$((RISK_SCORE + weight))
  else
    FINDINGS+="${YELLOW}WARNING${NC}  [$file:$line] $desc\n"
    WARNINGS=$((WARNINGS + 1))
    RISK_SCORE=$((RISK_SCORE + weight))
  fi
  local remediation_hint=""
  if [ -n "$check_id" ] && [ -n "${REMEDIATION[$check_id]:-}" ]; then
    remediation_hint="${REMEDIATION[$check_id]}"
  fi
  [ -n "$JSON_FINDINGS" ] && JSON_FINDINGS+=","
  JSON_FINDINGS+="{\"severity\":\"$severity\",\"file\":$(json_escape "$file"),\"line\":$(json_escape "$line"),\"description\":$(json_escape "$desc"),\"check_id\":\"$check_id\",\"weight\":$weight,\"remediation\":$(json_escape "$remediation_hint")}"
}

# Check if a line has a skillvet-ignore comment
has_ignore_comment() {
  local content="$1"
  echo "$content" | grep -q 'skillvet-ignore'
}

if [ $JSON_MODE -eq 0 ] && [ $SARIF_MODE -eq 0 ] && [ $SUMMARY_MODE -eq 0 ]; then
  echo "Auditing skill: $SKILL_NAME"
  echo "   Path: $SKILL_DIR"
  echo "---"
fi

# --- File collection ---
FIND_DEPTH_ARG=""
if [ "$MAX_DEPTH" -gt 0 ] 2>/dev/null; then
  FIND_DEPTH_ARG="-maxdepth $MAX_DEPTH"
fi

# Use -L to follow symlinks
# shellcheck disable=SC2086
FILES=$(find -L "$SKILL_DIR" $FIND_DEPTH_ARG -type f \( \
  -name "*.md" -o -name "*.js" -o -name "*.ts" -o -name "*.tsx" -o -name "*.jsx" \
  -o -name "*.py" -o -name "*.sh" -o -name "*.bash" \
  -o -name "*.rs" -o -name "*.go" -o -name "*.rb" -o -name "*.c" -o -name "*.cpp" \
  -o -name "*.json" -o -name "*.yaml" -o -name "*.yml" -o -name "*.toml" \
  -o -name "*.txt" -o -name "*.env*" -o -name "Dockerfile*" -o -name "Makefile" \
  -o -name "pom.xml" -o -name "*.gradle" \
\) 2>/dev/null || true)

if [ -z "$FILES" ]; then
  echo "No scannable files found"
  exit 0
fi

# Filter out binary files and oversized files
FILTERED_FILES=""
while IFS= read -r file; do
  [ -z "$file" ] && continue
  # Skip binary files (but not text-based scripts that `file` calls "executable")
  file_type=$(file "$file" 2>/dev/null)
  if echo "$file_type" | grep -q 'text'; then
    : # text file — keep it (even if also tagged "executable" like shebanged scripts)
  elif echo "$file_type" | grep -q 'binary\|executable\|archive\|image\|font\|data'; then
    SKIPPED_BINARY=$((SKIPPED_BINARY + 1))
    verbose "Skipping binary: ${file#$SKILL_DIR/}"
    continue
  fi
  # Skip oversized files
  if [ "$MAX_FILE_SIZE" -gt 0 ] 2>/dev/null; then
    file_size=$(wc -c < "$file" 2>/dev/null | tr -d ' ')
    if [ "$file_size" -gt "$MAX_FILE_SIZE" ]; then
      SKIPPED_SIZE=$((SKIPPED_SIZE + 1))
      verbose "Skipping oversized (${file_size}B): ${file#$SKILL_DIR/}"
      continue
    fi
  fi
  FILTERED_FILES+="$file"$'\n'
done <<< "$FILES"
FILES="$FILTERED_FILES"

FILE_COUNT=$(echo "$FILES" | grep -c . || echo 0)
if [ $JSON_MODE -eq 0 ] && [ $SARIF_MODE -eq 0 ] && [ $SUMMARY_MODE -eq 0 ]; then
  echo "   Scanning $FILE_COUNT files..."
  [ $SKIPPED_BINARY -gt 0 ] && echo "   Skipped $SKIPPED_BINARY binary files"
  [ $SKIPPED_SIZE -gt 0 ] && echo "   Skipped $SKIPPED_SIZE oversized files"
  echo ""
fi

# --- Include patterns for code files ---
CODE_INCLUDES="--include=*.js --include=*.ts --include=*.tsx --include=*.jsx --include=*.py --include=*.sh --include=*.rs --include=*.go --include=*.rb --include=*.c --include=*.cpp"
DOC_INCLUDES="--include=*.md --include=*.txt --include=*.yaml --include=*.yml --include=*.json"

# --- CRITICAL CHECKS ---

# 1. Known exfiltration endpoints
if ! is_check_disabled 1; then
  CHECKS_RUN=$((CHECKS_RUN + 1))
  verbose "Running check #1: Exfiltration endpoints"
  while IFS=: read -r file line content; do
    [ -z "$file" ] && continue
    has_ignore_comment "$content" && continue
    rel_file="${file#$SKILL_DIR/}"
    if echo "$content" | grep -qiE '(webhook\.site|ngrok\.io|pipedream|requestbin|burpcollaborator|interact\.sh|oastify|socifiapp\.com|hookbin\.com|postb\.in|webhook\.online)'; then
      add_finding "CRITICAL" "$rel_file" "$line" "Known exfiltration endpoint: $(echo "$content" | grep -oiE '(webhook\.site|ngrok\.io|pipedream|requestbin|burpcollaborator|interact\.sh|oastify|socifiapp\.com|hookbin\.com|postb\.in|webhook\.online)[^ "]*')" "1"
    fi
  # shellcheck disable=SC2086
  done < <(grep -rnE 'https?://' "$SKILL_DIR" $CODE_INCLUDES 2>/dev/null || true)
fi

# 2. Environment variable harvesting
if ! is_check_disabled 2; then
  CHECKS_RUN=$((CHECKS_RUN + 1))
  verbose "Running check #2: Env harvesting"
  while IFS=: read -r file line content; do
    [ -z "$file" ] && continue
    has_ignore_comment "$content" && continue
    rel_file="${file#$SKILL_DIR/}"
    add_finding "CRITICAL" "$rel_file" "$line" "Bulk env harvesting: ${content:0:120}" "2"
  # shellcheck disable=SC2086
  done < <(grep -rnE '(\$\{!.*@\}|printenv\s*$|printenv\s*\||env\s*\|)' "$SKILL_DIR" $CODE_INCLUDES 2>/dev/null || true)
fi

# 3. Foreign credential access
if ! is_check_disabled 3; then
  CHECKS_RUN=$((CHECKS_RUN + 1))
  verbose "Running check #3: Foreign credentials"
  OWN_KEYS=""
  if [ -f "$SKILL_DIR/SKILL.md" ]; then
    OWN_KEYS=$(grep -oE '[A-Z][A-Z_]*_API_KEY|[A-Z][A-Z_]*_TOKEN|[A-Z][A-Z_]*_SECRET|[A-Z][A-Z_]*_KEY' "$SKILL_DIR/SKILL.md" 2>/dev/null | sort -u | tr '\n' '|' | sed 's/|$//')
  fi
  if [ -z "$OWN_KEYS" ]; then
    OWN_KEYS=$(grep -roE '[A-Z][A-Z_]*_KEY' "$SKILL_DIR"/*.md 2>/dev/null | grep -oE '[A-Z][A-Z_]*_KEY' | sort -u | tr '\n' '|' | sed 's/|$//')
  fi

  FOREIGN_KEYS="ANTHROPIC_API_KEY|OPENAI_API_KEY|OPENROUTER_API_KEY|TELEGRAM.*BOT_TOKEN|CLAUDE.*TOKEN|ELEVENLABS.*KEY|AGENTMAIL_API_KEY|FIRECRAWL_API_KEY|BROWSER_USE_API_KEY|MEM0_API_KEY|GOOGLE_API_KEY|CLAWDHUB_TOKEN|OPENCLAW.*KEY|CLAWD.*KEY"
  while IFS=: read -r file line content; do
    [ -z "$file" ] && continue
    has_ignore_comment "$content" && continue
    rel_file="${file#$SKILL_DIR/}"
    [[ "$rel_file" == *.md ]] && continue
    matched_key=$(echo "$content" | grep -oE '[A-Z][A-Z_]*_API_KEY|[A-Z][A-Z_]*_KEY|[A-Z][A-Z_]*_TOKEN|[A-Z][A-Z_]*_SECRET' | head -1)
    if [ -n "$OWN_KEYS" ] && [ -n "$matched_key" ] && echo "$matched_key" | grep -qE "^($OWN_KEYS)$"; then
      continue
    fi
    add_finding "CRITICAL" "$rel_file" "$line" "Accesses foreign credentials: ${content:0:120}" "3"
  # shellcheck disable=SC2086
  done < <(grep -rnE "($FOREIGN_KEYS)" "$SKILL_DIR" $CODE_INCLUDES 2>/dev/null || true)
fi

# 4. Obfuscation patterns
if ! is_check_disabled 4; then
  CHECKS_RUN=$((CHECKS_RUN + 1))
  verbose "Running check #4: Obfuscation"
  while IFS=: read -r file line content; do
    [ -z "$file" ] && continue
    has_ignore_comment "$content" && continue
    rel_file="${file#$SKILL_DIR/}"
    add_finding "CRITICAL" "$rel_file" "$line" "Code obfuscation detected: ${content:0:120}" "4"
  # shellcheck disable=SC2086
  done < <(grep -rnE '(eval\s*\(|new\s+Function\s*\(|atob\s*\(|btoa\s*\(|Buffer\.from\s*\(.*(base64|hex)|\\x[0-9a-f]{2}\\x[0-9a-f]{2}\\x)' "$SKILL_DIR" $CODE_INCLUDES 2>/dev/null || true)
fi

# 5. Path traversal / sensitive file access
if ! is_check_disabled 5; then
  CHECKS_RUN=$((CHECKS_RUN + 1))
  verbose "Running check #5: Path traversal"
  while IFS=: read -r file line content; do
    [ -z "$file" ] && continue
    has_ignore_comment "$content" && continue
    rel_file="${file#$SKILL_DIR/}"
    add_finding "CRITICAL" "$rel_file" "$line" "Path traversal / sensitive file access: ${content:0:120}" "5"
  # shellcheck disable=SC2086
  done < <(grep -rnE '(\.\./\.\./|/etc/passwd|/etc/shadow|~\/\.bashrc|~\/\.ssh|~\/\.aws|~\/\.clawdbot|~\/\.config|\/home\/[a-z])' "$SKILL_DIR" $CODE_INCLUDES 2>/dev/null || true)
fi

# 6. Data exfiltration via curl/wget (ENCODED)
if ! is_check_disabled 6; then
  CHECKS_RUN=$((CHECKS_RUN + 1))
  verbose "Running check #6: Data exfil via curl/wget"
  while IFS=: read -r file line content; do
    [ -z "$file" ] && continue
    has_ignore_comment "$content" && continue
    rel_file="${file#$SKILL_DIR/}"
    add_finding "CRITICAL" "$rel_file" "$line" "Data exfiltration pattern: ${content:0:120}" "6"
  # shellcheck disable=SC2086
  done < <(grep -rnE "$P_EXFIL_CURL" "$SKILL_DIR" $CODE_INCLUDES 2>/dev/null || true)
fi

# 7. Reverse/bind shells (ENCODED)
if ! is_check_disabled 7; then
  CHECKS_RUN=$((CHECKS_RUN + 1))
  verbose "Running check #7: Reverse shells"
  while IFS=: read -r file line content; do
    [ -z "$file" ] && continue
    has_ignore_comment "$content" && continue
    rel_file="${file#$SKILL_DIR/}"
    add_finding "CRITICAL" "$rel_file" "$line" "Possible reverse/bind shell: ${content:0:120}" "7"
  # shellcheck disable=SC2086
  done < <(grep -rnE "$P_REVSHELL" "$SKILL_DIR" $CODE_INCLUDES 2>/dev/null || true)
fi

# 8. .env file theft
if ! is_check_disabled 8; then
  CHECKS_RUN=$((CHECKS_RUN + 1))
  verbose "Running check #8: .env file theft"
  while IFS=: read -r file line content; do
    [ -z "$file" ] && continue
    has_ignore_comment "$content" && continue
    rel_file="${file#$SKILL_DIR/}"
    [[ "$rel_file" == *.md ]] && continue
    add_finding "CRITICAL" "$rel_file" "$line" ".env file access: ${content:0:120}" "8"
  # shellcheck disable=SC2086
  done < <(grep -rnE '(dotenv|load_dotenv|\.env\.local|open\(.*\.env|read.*\.env|config\s*\(\s*\))' "$SKILL_DIR" $CODE_INCLUDES 2>/dev/null | grep -vE '(\.env\.example|\.env\.sample|#.*\.env)' || true)
fi

# 9. Prompt injection in markdown
if ! is_check_disabled 9; then
  CHECKS_RUN=$((CHECKS_RUN + 1))
  verbose "Running check #9: Prompt injection"
  while IFS=: read -r file line content; do
    [ -z "$file" ] && continue
    has_ignore_comment "$content" && continue
    rel_file="${file#$SKILL_DIR/}"
    if echo "$content" | grep -qiE '(example|never|attack|malicious|don.t|warning|avoid|block|detect|prevent|security)'; then
      continue
    fi
    add_finding "CRITICAL" "$rel_file" "$line" "Prompt injection attempt: ${content:0:120}" "9"
  # shellcheck disable=SC2086
  done < <(grep -rniE '(ignore (previous|prior|above|all) (instructions|rules|prompts)|disregard (your|all|previous)|forget (your|all|previous)|you are now|new persona|override (system|safety)|jailbreak|do not follow|pretend you|act as if you have no restrictions|reveal your (system|instructions|prompt))' "$SKILL_DIR" $DOC_INCLUDES 2>/dev/null || true)
fi

# 10. LLM tool exploitation
if ! is_check_disabled 10; then
  CHECKS_RUN=$((CHECKS_RUN + 1))
  verbose "Running check #10: LLM tool exploitation"
  while IFS=: read -r file line content; do
    [ -z "$file" ] && continue
    has_ignore_comment "$content" && continue
    rel_file="${file#$SKILL_DIR/}"
    add_finding "CRITICAL" "$rel_file" "$line" "LLM tool exploitation: ${content:0:120}" "10"
  done < <(grep -rniE '(send (this|the|all|my) (data|info|key|token|secret|config|env|password|credential)|exec.*curl.*api[_-]?key|write.*(api[_-]?key|token|secret|password).*to|post.*(credential|secret|token|key).*to|email.*(key|token|secret|credential)|forward.*(key|token|secret))' "$SKILL_DIR" --include='*.md' --include='*.txt' 2>/dev/null || true)
fi

# 11. Agent config tampering
if ! is_check_disabled 11; then
  CHECKS_RUN=$((CHECKS_RUN + 1))
  verbose "Running check #11: Agent config tampering"
  while IFS=: read -r file line content; do
    [ -z "$file" ] && continue
    has_ignore_comment "$content" && continue
    rel_file="${file#$SKILL_DIR/}"
    add_finding "CRITICAL" "$rel_file" "$line" "Agent config tampering: ${content:0:120}" "11"
  done < <(grep -rniE '(write|edit|modify|overwrite|replace|append).*(AGENTS\.md|SOUL\.md|IDENTITY\.md|USER\.md|HEARTBEAT\.md|MEMORY\.md|BOOTSTRAP\.md|clawdbot\.json|\.bashrc|\.profile)' "$SKILL_DIR" 2>/dev/null || true)
fi

# 12. Unicode obfuscation
if ! is_check_disabled 12; then
  CHECKS_RUN=$((CHECKS_RUN + 1))
  verbose "Running check #12: Unicode obfuscation"
  while IFS= read -r file; do
    [ -z "$file" ] && continue
    rel_file="${file#$SKILL_DIR/}"
    if grep_p '[\x{200B}\x{200C}\x{200D}\x{200E}\x{200F}\x{202A}\x{202B}\x{202C}\x{202D}\x{202E}\x{2060}\x{FEFF}]' "$file" 2>/dev/null; then
      add_finding "CRITICAL" "$rel_file" "?" "Unicode obfuscation -- hidden zero-width or directional chars detected" "12"
    fi
  done < <(find -L "$SKILL_DIR" -type f \( -name "*.md" -o -name "*.js" -o -name "*.ts" -o -name "*.py" -o -name "*.sh" \) 2>/dev/null || true)
fi

# 13. Suspicious setup commands
if ! is_check_disabled 13; then
  CHECKS_RUN=$((CHECKS_RUN + 1))
  verbose "Running check #13: Suspicious setup commands"
  if [ -f "$SKILL_DIR/SKILL.md" ]; then
    while IFS=: read -r file line content; do
      [ -z "$file" ] && continue
      has_ignore_comment "$content" && continue
      rel_file="${file#$SKILL_DIR/}"
      add_finding "CRITICAL" "$rel_file" "$line" "Suspicious setup command (exfil disguised as setup): ${content:0:120}" "13"
    done < <(grep -nE "$P_EXFIL_CURL" "$SKILL_DIR/SKILL.md" 2>/dev/null || true)
  fi
fi

# 14. Social engineering
if ! is_check_disabled 14; then
  CHECKS_RUN=$((CHECKS_RUN + 1))
  verbose "Running check #14: Social engineering"
  while IFS=: read -r file line content; do
    [ -z "$file" ] && continue
    has_ignore_comment "$content" && continue
    rel_file="${file#$SKILL_DIR/}"
    add_finding "CRITICAL" "$rel_file" "$line" "Social engineering -- instructs user to download/run external binary: ${content:0:120}" "14"
  done < <(grep -rniE '(download.*\.(exe|zip|dmg|pkg|msi|deb|rpm|appimage|sh|bat|cmd|ps1)|extract.*passw|run.*executable|execute.*command.*terminal|install.*from.*(glot\.io|pastebin|hastebin|ghostbin|paste\.|privatebin|dpaste|controlc|rentry)|run.*(before|first).*using|\.zip.*password)' "$SKILL_DIR" --include='*.md' --include='*.txt' 2>/dev/null || true)
fi

# 15. Shipped .env files
if ! is_check_disabled 15; then
  CHECKS_RUN=$((CHECKS_RUN + 1))
  verbose "Running check #15: Shipped .env files"
  while IFS= read -r file; do
    [ -z "$file" ] && continue
    rel_file="${file#$SKILL_DIR/}"
    if [[ "$rel_file" != *.example ]] && [[ "$rel_file" != *.sample ]]; then
      add_finding "CRITICAL" "$rel_file" "-" "Actual .env file shipped with skill -- may contain or harvest credentials" "15"
    fi
  done < <(find -L "$SKILL_DIR" -name ".env" -o -name ".env.local" -o -name ".env.production" 2>/dev/null || true)
fi

# 16. Homograph characters
if ! is_check_disabled 16; then
  CHECKS_RUN=$((CHECKS_RUN + 1))
  verbose "Running check #16: Homograph characters"
  while IFS= read -r file; do
    [ -z "$file" ] && continue
    rel_file="${file#$SKILL_DIR/}"
    if grep_p '[\x{0430}\x{0435}\x{043E}\x{0440}\x{0441}\x{0445}\x{0456}\x{0458}\x{0455}\x{0410}\x{0412}\x{0421}\x{0415}\x{041D}\x{041A}\x{041C}\x{041E}\x{0420}\x{0422}\x{0425}]' "$file" 2>/dev/null; then
      add_finding "CRITICAL" "$rel_file" "?" "Homograph characters -- Cyrillic lookalikes mimicking Latin letters (IDN attack)" "16"
    fi
  done < <(find -L "$SKILL_DIR" -type f \( -name "*.md" -o -name "*.js" -o -name "*.ts" -o -name "*.py" -o -name "*.sh" -o -name "*.json" -o -name "*.yaml" -o -name "*.yml" -o -name "*.toml" \) 2>/dev/null || true)
fi

# 17. ANSI escape injection
if ! is_check_disabled 17; then
  CHECKS_RUN=$((CHECKS_RUN + 1))
  verbose "Running check #17: ANSI escape injection"
  while IFS= read -r file; do
    [ -z "$file" ] && continue
    rel_file="${file#$SKILL_DIR/}"
    if grep_p '\x1b' "$file" 2>/dev/null; then
      add_finding "CRITICAL" "$rel_file" "?" "Raw ANSI escape sequences -- possible terminal display manipulation" "17"
    fi
  done < <(find -L "$SKILL_DIR" -type f \( -name "*.md" -o -name "*.txt" -o -name "*.json" -o -name "*.yaml" -o -name "*.yml" -o -name "*.toml" \) 2>/dev/null || true)
fi

# 18. Punycode domains
if ! is_check_disabled 18; then
  CHECKS_RUN=$((CHECKS_RUN + 1))
  verbose "Running check #18: Punycode domains"
  while IFS=: read -r file line content; do
    [ -z "$file" ] && continue
    has_ignore_comment "$content" && continue
    rel_file="${file#$SKILL_DIR/}"
    add_finding "CRITICAL" "$rel_file" "$line" "Punycode domain -- possible IDN homograph attack: ${content:0:120}" "18"
  # shellcheck disable=SC2086
  done < <(grep -rnE 'xn--[a-z0-9]+' "$SKILL_DIR" $CODE_INCLUDES --include='*.md' 2>/dev/null || true)
fi

# 19. Double-encoded paths
if ! is_check_disabled 19; then
  CHECKS_RUN=$((CHECKS_RUN + 1))
  verbose "Running check #19: Double-encoded paths"
  while IFS=: read -r file line content; do
    [ -z "$file" ] && continue
    has_ignore_comment "$content" && continue
    rel_file="${file#$SKILL_DIR/}"
    add_finding "CRITICAL" "$rel_file" "$line" "Double-encoded path -- percent-encoding bypass attempt: ${content:0:120}" "19"
  # shellcheck disable=SC2086
  done < <(grep -rnE '%25[0-9a-fA-F]{2}' "$SKILL_DIR" $CODE_INCLUDES 2>/dev/null || true)
fi

# 20. Shortened URLs
if ! is_check_disabled 20; then
  CHECKS_RUN=$((CHECKS_RUN + 1))
  verbose "Running check #20: Shortened URLs"
  while IFS=: read -r file line content; do
    [ -z "$file" ] && continue
    has_ignore_comment "$content" && continue
    rel_file="${file#$SKILL_DIR/}"
    add_finding "CRITICAL" "$rel_file" "$line" "Shortened URL -- hides true destination: ${content:0:120}" "20"
  # shellcheck disable=SC2086
  done < <(grep -rnE 'https?://(bit\.ly|t\.co|tinyurl\.com|goo\.gl|is\.gd|ow\.ly|rb\.gy|short\.io|cutt\.ly|tiny\.cc|buff\.ly)/' "$SKILL_DIR" $CODE_INCLUDES 2>/dev/null || true)
fi

# 21. Pipe-to-shell (ENCODED)
if ! is_check_disabled 21; then
  CHECKS_RUN=$((CHECKS_RUN + 1))
  verbose "Running check #21: Pipe-to-shell"
  while IFS=: read -r file line content; do
    [ -z "$file" ] && continue
    has_ignore_comment "$content" && continue
    rel_file="${file#$SKILL_DIR/}"
    add_finding "CRITICAL" "$rel_file" "$line" "Pipe-to-shell -- remote code piped to interpreter: ${content:0:120}" "21"
  # shellcheck disable=SC2086
  done < <(grep -rnE "$P_PIPE_SHELL" "$SKILL_DIR" $CODE_INCLUDES --include='*.md' 2>/dev/null || true)
fi

# 22. String construction evasion
if ! is_check_disabled 22; then
  CHECKS_RUN=$((CHECKS_RUN + 1))
  verbose "Running check #22: String construction evasion"
  while IFS=: read -r file line content; do
    [ -z "$file" ] && continue
    has_ignore_comment "$content" && continue
    rel_file="${file#$SKILL_DIR/}"
    add_finding "CRITICAL" "$rel_file" "$line" "String construction evasion -- assembling dangerous calls from fragments: ${content:0:120}" "22"
  done < <(grep -rnE "('[a-z]{1,4}'\s*\+\s*'[a-z]{1,4}'|\"[a-z]{1,4}\"\s*\+\s*\"[a-z]{1,4}\"|(window|global|globalThis|self)\[.{1,30}\]|String\.fromCharCode|\.split\(['\"].*['\"\)]\)\.reverse\(\)\.join|global\[.require.\]|getattr\s*\(\s*(os|sys|builtins)|const\s*\{[^}]*:\s*\w+\s*\}\s*=\s*require\s*\(\s*['\"]child_process)" "$SKILL_DIR" --include='*.js' --include='*.ts' --include='*.tsx' --include='*.jsx' --include='*.py' 2>/dev/null || true)
fi

# 23. Data flow chain analysis
if ! is_check_disabled 23; then
  CHECKS_RUN=$((CHECKS_RUN + 1))
  verbose "Running check #23: Data flow chain analysis"
  while IFS= read -r file; do
    [ -z "$file" ] && continue
    rel_file="${file#$SKILL_DIR/}"
    has_read=0
    has_encode=0
    has_send=0
    grep -qE '(process\.env|os\.environ|dotenv|load_dotenv|readFileSync|os\.getenv)' "$file" 2>/dev/null && has_read=1
    grep -qE '(btoa|atob|base64|Buffer\.from|encodeURIComponent|b64encode|b64decode)' "$file" 2>/dev/null && has_encode=1
    grep -qE '(fetch\(|axios\.|http\.request|requests\.(post|put|get)|urllib\.request|socket\.connect)' "$file" 2>/dev/null && has_send=1
    if [ $has_read -eq 1 ] && [ $has_encode -eq 1 ] && [ $has_send -eq 1 ]; then
      add_finding "CRITICAL" "$rel_file" "-" "Data flow chain -- file reads secrets/env, encodes data, AND sends network requests" "23"
    fi
  done < <(find -L "$SKILL_DIR" -type f \( -name "*.js" -o -name "*.ts" -o -name "*.tsx" -o -name "*.jsx" -o -name "*.py" \) 2>/dev/null || true)
fi

# 24. Time bomb detection
if ! is_check_disabled 24; then
  CHECKS_RUN=$((CHECKS_RUN + 1))
  verbose "Running check #24: Time bomb detection"
  while IFS=: read -r file line content; do
    [ -z "$file" ] && continue
    has_ignore_comment "$content" && continue
    rel_file="${file#$SKILL_DIR/}"
    add_finding "CRITICAL" "$rel_file" "$line" "Time bomb pattern -- delayed or date-gated execution: ${content:0:120}" "24"
  # shellcheck disable=SC2086
  done < <(grep -rnE '(Date\.now\(\)\s*>\s*[0-9]{12,}|new\s+Date\s*\(\s*['"'"'"][0-9]{4}-[0-9]{2}-[0-9]{2}|setTimeout\s*\([^,]+,\s*[0-9]{8,}|setInterval\s*\([^,]+,\s*[0-9]{8,}|time\.sleep\s*\(\s*[0-9]{5,}|datetime\.now\(\)\s*>|schedule\.every\s*\(\s*[0-9]+\s*\)\s*\.days)' "$SKILL_DIR" $CODE_INCLUDES 2>/dev/null || true)
fi

# --- CAMPAIGN-INSPIRED CHECKS ---

# 25. Known C2/IOC IP blocklist
if ! is_check_disabled 25; then
  CHECKS_RUN=$((CHECKS_RUN + 1))
  verbose "Running check #25: IOC blocklist"
  while IFS=: read -r file line content; do
    [ -z "$file" ] && continue
    has_ignore_comment "$content" && continue
    rel_file="${file#$SKILL_DIR/}"
    matched_ip=$(echo "$content" | grep -oE "$P_KNOWN_IPS")
    add_finding "CRITICAL" "$rel_file" "$line" "Known malicious C2 IP ($matched_ip) -- matches IOC blocklist: ${content:0:120}" "25"
  done < <(grep -rnE "$P_KNOWN_IPS" "$SKILL_DIR" 2>/dev/null || true)
fi

# 26. Password-protected archive references
if ! is_check_disabled 26; then
  CHECKS_RUN=$((CHECKS_RUN + 1))
  verbose "Running check #26: Password-protected archives"
  while IFS=: read -r file line content; do
    [ -z "$file" ] && continue
    has_ignore_comment "$content" && continue
    rel_file="${file#$SKILL_DIR/}"
    add_finding "CRITICAL" "$rel_file" "$line" "Password-protected archive -- AV evasion technique: ${content:0:120}" "26"
  done < <(grep -rniE '(extract.*(using|with)\s*(pass(word)?|pwd)|password[:\s]+.*(openclaw|extract|unzip|archive)|\.zip.*pass(word)?|pass(word)?.*\.zip|\.7z.*pass|\.rar.*pass)' "$SKILL_DIR" --include='*.md' --include='*.txt' --include='*.yaml' --include='*.yml' 2>/dev/null || true)
fi

# 27. Paste service payloads
if ! is_check_disabled 27; then
  CHECKS_RUN=$((CHECKS_RUN + 1))
  verbose "Running check #27: Paste service payloads"
  while IFS=: read -r file line content; do
    [ -z "$file" ] && continue
    has_ignore_comment "$content" && continue
    rel_file="${file#$SKILL_DIR/}"
    add_finding "CRITICAL" "$rel_file" "$line" "Paste service reference -- commonly used to host malicious payloads: ${content:0:120}" "27"
  # shellcheck disable=SC2086
  done < <(grep -rnE 'https?://(glot\.io|pastebin\.com|paste\.ee|hastebin\.com|ghostbin\.|privatebin\.|dpaste\.|controlc\.com|rentry\.(co|org)|paste\.mozilla\.org|ix\.io|sprunge\.us|cl1p\.net)' "$SKILL_DIR" $CODE_INCLUDES --include='*.md' 2>/dev/null || true)
fi

# 28. GitHub releases binary downloads
if ! is_check_disabled 28; then
  CHECKS_RUN=$((CHECKS_RUN + 1))
  verbose "Running check #28: GitHub releases binaries"
  while IFS=: read -r file line content; do
    [ -z "$file" ] && continue
    has_ignore_comment "$content" && continue
    rel_file="${file#$SKILL_DIR/}"
    add_finding "CRITICAL" "$rel_file" "$line" "GitHub releases binary download -- fake prerequisite pattern: ${content:0:120}" "28"
  done < <(grep -rnE 'github\.com/[^/]+/[^/]+/releases/download/[^"'"'"')]*\.(zip|exe|dmg|pkg|msi|deb|rpm|appimage|tar\.gz|bin)' "$SKILL_DIR" --include='*.md' --include='*.txt' 2>/dev/null || true)
fi

# 29. Base64 pipe-to-interpreter (ENCODED)
if ! is_check_disabled 29; then
  CHECKS_RUN=$((CHECKS_RUN + 1))
  verbose "Running check #29: Base64 pipe-to-interpreter"
  while IFS=: read -r file line content; do
    [ -z "$file" ] && continue
    has_ignore_comment "$content" && continue
    rel_file="${file#$SKILL_DIR/}"
    add_finding "CRITICAL" "$rel_file" "$line" "Base64 pipe-to-interpreter -- encoded payload execution: ${content:0:120}" "29"
  done < <(grep -rnE "$P_B64_EXEC" "$SKILL_DIR" 2>/dev/null || true)
fi

# 30. Subprocess executing network commands (ENCODED)
if ! is_check_disabled 30; then
  CHECKS_RUN=$((CHECKS_RUN + 1))
  verbose "Running check #30: Subprocess + network"
  while IFS=: read -r file line content; do
    [ -z "$file" ] && continue
    has_ignore_comment "$content" && continue
    rel_file="${file#$SKILL_DIR/}"
    add_finding "CRITICAL" "$rel_file" "$line" "Subprocess with network command -- hidden pipe-to-shell: ${content:0:120}" "30"
  done < <(grep -rnE "$P_SUBPROCESS_NET" "$SKILL_DIR" --include='*.py' --include='*.js' --include='*.ts' --include='*.tsx' --include='*.jsx' 2>/dev/null || true)
fi

# 31. Fake URL misdirection
if ! is_check_disabled 31; then
  CHECKS_RUN=$((CHECKS_RUN + 1))
  verbose "Running check #31: Fake URL misdirection"
  while IFS=: read -r file line content; do
    [ -z "$file" ] && continue
    has_ignore_comment "$content" && continue
    rel_file="${file#$SKILL_DIR/}"
    add_finding "WARNING" "$rel_file" "$line" "Fake URL misdirection -- decoy URL before real payload: ${content:0:120}" "31"
  done < <(grep -rnE 'echo\s+[\"'"'"'"].*https?://.*(apple\.com|microsoft\.com|google\.com|setup|install|download|update|cdn\.)' "$SKILL_DIR" --include='*.sh' --include='*.md' --include='*.py' 2>/dev/null || true)
fi

# 32. Process persistence mechanisms
if ! is_check_disabled 32; then
  CHECKS_RUN=$((CHECKS_RUN + 1))
  verbose "Running check #32: Process persistence + network"
  while IFS= read -r file; do
    [ -z "$file" ] && continue
    rel_file="${file#$SKILL_DIR/}"
    has_persist=0
    has_network=0
    grep -qE '(nohup|disown|setsid|&\s*>/dev/null|start-stop-daemon|launchctl|systemctl.*(enable|start))' "$file" 2>/dev/null && has_persist=1
    grep -qE '(curl|wget|nc |ncat|fetch\(|requests\.|http\.|socket\.)' "$file" 2>/dev/null && has_network=1
    if [ $has_persist -eq 1 ] && [ $has_network -eq 1 ]; then
      add_finding "CRITICAL" "$rel_file" "-" "Process persistence + network -- background process with network access (backdoor pattern)" "32"
    fi
  done < <(find -L "$SKILL_DIR" -type f \( -name "*.sh" -o -name "*.py" -o -name "*.js" -o -name "*.ts" \) 2>/dev/null || true)
fi

# 33. Fake prerequisite with external download
if ! is_check_disabled 33; then
  CHECKS_RUN=$((CHECKS_RUN + 1))
  verbose "Running check #33: Fake prerequisite"
  if [ -f "$SKILL_DIR/SKILL.md" ]; then
    while IFS=: read -r file line content; do
      [ -z "$file" ] && continue
      has_ignore_comment "$content" && continue
      rel_file="${file#$SKILL_DIR/}"
      add_finding "CRITICAL" "$rel_file" "$line" "Fake prerequisite -- external download requirement in docs: ${content:0:120}" "33"
    done < <(grep -niE '(prerequisite|require[sd]?|must install|needed|before (you|using|proceed)).*https?://' "$SKILL_DIR/SKILL.md" 2>/dev/null | grep -viE '(npm|pip|brew|apt|cargo|node|python|docker|git|ffmpeg|clawhub\.ai|github\.com/(openclaw|anthropic|google))' || true)
  fi
fi

# 34. xattr/chmod on downloaded files (ENCODED)
if ! is_check_disabled 34; then
  CHECKS_RUN=$((CHECKS_RUN + 1))
  verbose "Running check #34: xattr/chmod dropper"
  while IFS=: read -r file line content; do
    [ -z "$file" ] && continue
    has_ignore_comment "$content" && continue
    rel_file="${file#$SKILL_DIR/}"
    add_finding "CRITICAL" "$rel_file" "$line" "Download + xattr/chmod -- macOS Gatekeeper bypass (AMOS pattern): ${content:0:120}" "34"
  done < <(grep -rnE "$P_GATEKEEPER" "$SKILL_DIR" --include='*.sh' --include='*.py' --include='*.md' 2>/dev/null || true)
fi

# 35. Binary download+execute ClickFix (ENCODED)
if ! is_check_disabled 35; then
  CHECKS_RUN=$((CHECKS_RUN + 1))
  verbose "Running check #35: ClickFix download+execute"
  while IFS=: read -r file line content; do
    [ -z "$file" ] && continue
    has_ignore_comment "$content" && continue
    rel_file="${file#$SKILL_DIR/}"
    add_finding "CRITICAL" "$rel_file" "$line" "Binary download+execute chain -- ClickFix-style attack: ${content:0:120}" "35"
  # shellcheck disable=SC2086
  done < <(grep -rnE "$P_CLICKFIX" "$SKILL_DIR" $CODE_INCLUDES --include='*.md' 2>/dev/null || true)
fi

# 36. Suspicious package install sources (ENCODED)
if ! is_check_disabled 36; then
  CHECKS_RUN=$((CHECKS_RUN + 1))
  verbose "Running check #36: Suspicious package sources"
  while IFS=: read -r file line content; do
    [ -z "$file" ] && continue
    has_ignore_comment "$content" && continue
    rel_file="${file#$SKILL_DIR/}"
    add_finding "CRITICAL" "$rel_file" "$line" "Suspicious package source -- not from official registry: ${content:0:120}" "36"
  # shellcheck disable=SC2086
  done < <(grep -rnE "$P_SUS_PKG" "$SKILL_DIR" $CODE_INCLUDES --include='*.md' 2>/dev/null || true)
fi

# 37. Staged installer pattern
if ! is_check_disabled 37; then
  CHECKS_RUN=$((CHECKS_RUN + 1))
  verbose "Running check #37: Staged installer"
  if [ -f "$SKILL_DIR/SKILL.md" ]; then
    while IFS=: read -r file line content; do
      [ -z "$file" ] && continue
      has_ignore_comment "$content" && continue
      rel_file="${file#$SKILL_DIR/}"
      add_finding "CRITICAL" "$rel_file" "$line" "Suspicious dependency -- unknown package with 'core'/'base'/'lib' suffix: ${content:0:120}" "37"
    done < <(grep -nE '(npm\s+install|pip\s+install|gem\s+install)\s+[a-z]+-?(core|base|lib|helper|util|sdk)\b' "$SKILL_DIR/SKILL.md" 2>/dev/null | grep -vE '(react-core|vue-core|angular-core|webpack-core|babel-core|eslint-core|typescript-core)' || true)
  fi
fi

# --- FEB 2026 CAMPAIGN CHECKS (38-48) ---
# Based on Bitdefender, Snyk, and Koi Security research

# 38. Fake OS update social engineering (ClawHavoc pattern)
if ! is_check_disabled 38; then
  CHECKS_RUN=$((CHECKS_RUN + 1))
  verbose "Running check #38: Fake OS update"
  while IFS=: read -r file line content; do
    [ -z "$file" ] && continue
    has_ignore_comment "$content" && continue
    rel_file="${file#$SKILL_DIR/}"
    add_finding "CRITICAL" "$rel_file" "$line" "Fake OS update message -- social engineering (ClawHavoc pattern): ${content:0:120}" "38"
  done < <(grep -rniE '(apple\s+software\s+update|microsoft\s+update|system\s+update\s+(required|needed)|security\s+update\s+(required|needed)|update\s+your\s+(system|os|software)|verification\s+(required|needed).*install|install.*for\s+compatibility)' "$SKILL_DIR" --include='*.md' --include='*.txt' --include='*.sh' --include='*.py' 2>/dev/null || true)
fi

# 39. Known malicious ClawHub actors (from Bitdefender/Snyk/Koi research Feb 2026)
if ! is_check_disabled 39; then
  CHECKS_RUN=$((CHECKS_RUN + 1))
  verbose "Running check #39: Known bad actors"
  while IFS=: read -r file line content; do
    [ -z "$file" ] && continue
    has_ignore_comment "$content" && continue
    rel_file="${file#$SKILL_DIR/}"
    matched_actor=$(echo "$content" | grep -oiE 'zaycv|Ddoy233|Sakaen736jih|aslaep123|Hightower6eu|davidsmorais|clawdhub1' | head -1)
    add_finding "CRITICAL" "$rel_file" "$line" "Reference to known malicious actor ($matched_actor) -- ClawHavoc campaign: ${content:0:120}" "39"
  done < <(grep -rniE 'zaycv|Ddoy233|Sakaen736jih|aslaep123|Hightower6eu|davidsmorais|clawdhub1' "$SKILL_DIR" --include='*.md' --include='*.txt' --include='*.json' --include='*.yaml' --include='*.yml' 2>/dev/null || true)
fi

# 40. Bash reverse shell via /dev/tcp (AuthTool pattern)
if ! is_check_disabled 40; then
  CHECKS_RUN=$((CHECKS_RUN + 1))
  verbose "Running check #40: /dev/tcp reverse shell"
  while IFS=: read -r file line content; do
    [ -z "$file" ] && continue
    has_ignore_comment "$content" && continue
    rel_file="${file#$SKILL_DIR/}"
    add_finding "CRITICAL" "$rel_file" "$line" "Bash reverse shell via /dev/tcp: ${content:0:120}" "40"
  done < <(grep -rnE '(bash\s+-[ic].*>/dev/tcp|/dev/tcp/[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+/[0-9]+|0>&1|>&\s*/dev/tcp)' "$SKILL_DIR" $CODE_INCLUDES --include='*.md' 2>/dev/null || true)
fi

# 41. Nohup with network command (Hidden Backdoor pattern)
if ! is_check_disabled 41; then
  CHECKS_RUN=$((CHECKS_RUN + 1))
  verbose "Running check #41: Nohup backdoor"
  while IFS=: read -r file line content; do
    [ -z "$file" ] && continue
    has_ignore_comment "$content" && continue
    rel_file="${file#$SKILL_DIR/}"
    add_finding "CRITICAL" "$rel_file" "$line" "Nohup with network command -- persistent backdoor pattern: ${content:0:120}" "41"
  done < <(grep -rnE '(nohup.*(curl|wget|nc |ncat|bash -c|/dev/tcp)|disown.*(curl|wget|bash)|setsid.*(curl|wget|bash|nc))' "$SKILL_DIR" --include='*.sh' --include='*.py' --include='*.md' 2>/dev/null || true)
fi

# 42. Python reverse shell patterns
if ! is_check_disabled 42; then
  CHECKS_RUN=$((CHECKS_RUN + 1))
  verbose "Running check #42: Python reverse shell"
  while IFS=: read -r file line content; do
    [ -z "$file" ] && continue
    has_ignore_comment "$content" && continue
    rel_file="${file#$SKILL_DIR/}"
    add_finding "CRITICAL" "$rel_file" "$line" "Python reverse shell pattern: ${content:0:120}" "42"
  done < <(grep -rnE '(socket\.socket.*connect.*dup2|pty\.spawn.*bash|subprocess\.call.*shell=True.*socket|os\.dup2.*socket|import\s+pty.*spawn|exec\s*\(.*compile\s*\(.*socket)' "$SKILL_DIR" --include='*.py' 2>/dev/null || true)
fi

# 43. Terminal output disguise (decoy message before payload)
if ! is_check_disabled 43; then
  CHECKS_RUN=$((CHECKS_RUN + 1))
  verbose "Running check #43: Terminal disguise"
  while IFS=: read -r file line content; do
    [ -z "$file" ] && continue
    has_ignore_comment "$content" && continue
    rel_file="${file#$SKILL_DIR/}"
    add_finding "WARNING" "$rel_file" "$line" "Terminal disguise -- decoy message before command: ${content:0:120}" "43"
  done < <(grep -rnE '(echo\s+[\"'"'"'].*\.(com|io|org|net).*[\"'"'"']\s*;|print\s*\([\"'"'"'].*downloading.*[\"'"'"']\s*\)|printf.*install|echo.*verification|echo.*success.*&&)' "$SKILL_DIR" --include='*.sh' --include='*.py' --include='*.md' 2>/dev/null || true)
fi

# 44. Credential harvesting via file read
if ! is_check_disabled 44; then
  CHECKS_RUN=$((CHECKS_RUN + 1))
  verbose "Running check #44: Credential file access"
  while IFS=: read -r file line content; do
    [ -z "$file" ] && continue
    has_ignore_comment "$content" && continue
    rel_file="${file#$SKILL_DIR/}"
    add_finding "CRITICAL" "$rel_file" "$line" "Credential file access pattern: ${content:0:120}" "44"
  done < <(grep -rnE '(open\s*\([\"'"'"'].*\.(env|key|pem|credentials|aws|ssh|config)|read.*~/\.(bash|zsh|ssh|aws|config)|cat\s+.*\.(env|pem|key|credentials))' "$SKILL_DIR" --include='*.py' --include='*.js' --include='*.ts' --include='*.sh' 2>/dev/null || true)
fi

# 45. TMPDIR payload staging (AMOS pattern)
if ! is_check_disabled 45; then
  CHECKS_RUN=$((CHECKS_RUN + 1))
  verbose "Running check #45: TMPDIR staging"
  while IFS=: read -r file line content; do
    [ -z "$file" ] && continue
    has_ignore_comment "$content" && continue
    rel_file="${file#$SKILL_DIR/}"
    add_finding "CRITICAL" "$rel_file" "$line" "TMPDIR payload staging -- malware drop pattern: ${content:0:120}" "45"
  done < <(grep -rnE '(\$TMPDIR/[a-z0-9]+|/tmp/\.[a-z]|mktemp.*(curl|wget|chmod)|cd\s+/tmp\s*&&.*(curl|wget))' "$SKILL_DIR" --include='*.sh' --include='*.py' --include='*.md' 2>/dev/null || true)
fi

# 46. GitHub raw content execution
if ! is_check_disabled 46; then
  CHECKS_RUN=$((CHECKS_RUN + 1))
  verbose "Running check #46: GitHub raw execution"
  while IFS=: read -r file line content; do
    [ -z "$file" ] && continue
    has_ignore_comment "$content" && continue
    rel_file="${file#$SKILL_DIR/}"
    add_finding "CRITICAL" "$rel_file" "$line" "GitHub raw content piped to interpreter: ${content:0:120}" "46"
  done < <(grep -rnE '(raw\.githubusercontent\.com|gist\.githubusercontent\.com|github\.com/[^/]+/[^/]+/raw/).*(curl|wget).*\|.*(bash|sh|python|node)' "$SKILL_DIR" 2>/dev/null || true)
fi

# 47. Echo-encoded payload execution
if ! is_check_disabled 47; then
  CHECKS_RUN=$((CHECKS_RUN + 1))
  verbose "Running check #47: Echo-encoded payload"
  while IFS=: read -r file line content; do
    [ -z "$file" ] && continue
    has_ignore_comment "$content" && continue
    rel_file="${file#$SKILL_DIR/}"
    add_finding "CRITICAL" "$rel_file" "$line" "Echo-encoded payload -- obfuscated execution: ${content:0:120}" "47"
  done < <(grep -rnE "echo\s+['\"][A-Za-z0-9+/=]{40,}['\"]\s*\|\s*(base64|openssl|xxd)" "$SKILL_DIR" --include='*.sh' --include='*.md' 2>/dev/null || true)
fi

# 48. Typosquat skill name detection
if ! is_check_disabled 48; then
  CHECKS_RUN=$((CHECKS_RUN + 1))
  verbose "Running check #48: Typosquat name"
  if [ -f "$SKILL_DIR/SKILL.md" ]; then
    SKILL_YAML_NAME=$(grep -m1 '^name:' "$SKILL_DIR/SKILL.md" 2>/dev/null | sed 's/name:\s*//' | tr -d '"'"'"' ')
    if echo "$SKILL_YAML_NAME" | grep -qiE "^(clawhub|clawdhub|openclaw|clawdbot|moltbot|skillvet|anthropic|openai|google)[0-9]|^[0-9](clawhub|clawdhub|openclaw|clawdbot|moltbot|skillvet|anthropic|openai|google)|(clawhub|clawdhub|openclaw|clawdbot|moltbot|skillvet|anthropic|openai|google)-?(cli|tool|helper|util|sdk|core|base|lib)$"; then
      if ! echo "$SKILL_YAML_NAME" | grep -qiE "^(openclaw|clawhub|skillvet|clawdbot)$"; then
        add_finding "CRITICAL" "SKILL.md" "1" "Typosquat skill name -- mimics official tool: $SKILL_YAML_NAME" "48"
      fi
    fi
  fi
fi

# 49. Homograph URLs — Cyrillic/Greek lookalikes in hostnames (inspired by Tirith)
if ! is_check_disabled 49; then
  CHECKS_RUN=$((CHECKS_RUN + 1))
  verbose "Running check #49: Homograph URL detection"
  # Detect non-ASCII characters in URLs that look like Latin (Cyrillic а/е/о/с/р/і, Greek α/ε/ο etc.)
  while IFS=: read -r file line content; do
    [ -z "$file" ] && continue
    has_ignore_comment "$content" && continue
    rel_file="${file#$SKILL_DIR/}"
    add_finding "CRITICAL" "$rel_file" "$line" "Homograph URL -- non-ASCII characters in hostname may be impersonating a legitimate domain: ${content:0:120}" "49"
  done < <(grep -rnP 'https?://[^\s]*[\x{0400}-\x{04FF}\x{0370}-\x{03FF}\x{0500}-\x{052F}][^\s]*' "$SKILL_DIR" 2>/dev/null || true)
fi

# 50. Zero-width / invisible Unicode characters (inspired by Tirith)
if ! is_check_disabled 50; then
  CHECKS_RUN=$((CHECKS_RUN + 1))
  verbose "Running check #50: Zero-width / invisible Unicode"
  # Zero-width space (U+200B), zero-width joiner (U+200D), zero-width non-joiner (U+200C),
  # word joiner (U+2060), left/right-to-left marks (U+200E/F), bidi overrides (U+202A-202E, U+2066-2069)
  while IFS=: read -r file line content; do
    [ -z "$file" ] && continue
    has_ignore_comment "$content" && continue
    rel_file="${file#$SKILL_DIR/}"
    add_finding "CRITICAL" "$rel_file" "$line" "Invisible Unicode -- zero-width or bidi override characters that can hide malicious content: ${content:0:120}" "50"
  done < <(grep -rnP '[\x{200B}-\x{200F}\x{202A}-\x{202E}\x{2060}-\x{2069}\x{FEFF}]' "$SKILL_DIR" --include='*.sh' --include='*.py' --include='*.js' --include='*.md' 2>/dev/null || true)
fi

# 51. Punycode domain in URLs (inspired by Tirith)
if ! is_check_disabled 51; then
  CHECKS_RUN=$((CHECKS_RUN + 1))
  verbose "Running check #51: Punycode domain detection"
  while IFS=: read -r file line content; do
    [ -z "$file" ] && continue
    has_ignore_comment "$content" && continue
    rel_file="${file#$SKILL_DIR/}"
    add_finding "CRITICAL" "$rel_file" "$line" "Punycode domain -- xn-- encoded domain may be a homograph attack: ${content:0:120}" "51"
  done < <(grep -rnE 'https?://[^\s]*xn--[^\s]*' "$SKILL_DIR" 2>/dev/null || true)
fi

# 52. Credential in URL (user:pass@host) (inspired by Tirith)
if ! is_check_disabled 52; then
  CHECKS_RUN=$((CHECKS_RUN + 1))
  verbose "Running check #52: Credentials in URL"
  while IFS=: read -r file line content; do
    [ -z "$file" ] && continue
    has_ignore_comment "$content" && continue
    rel_file="${file#$SKILL_DIR/}"
    add_finding "CRITICAL" "$rel_file" "$line" "Credentials in URL -- http(s)://user:pass@host pattern exposes credentials or tricks URL parsers: ${content:0:120}" "52"
  done < <(grep -rnP 'https?://[^@/\s]+:[^@/\s]+@[^\s]+' "$SKILL_DIR" --include='*.sh' --include='*.py' --include='*.js' --include='*.md' 2>/dev/null || true)
fi

# 53. Dotfile targeting — downloads aimed at shell config, SSH keys, git config (inspired by Tirith)
if ! is_check_disabled 53; then
  CHECKS_RUN=$((CHECKS_RUN + 1))
  verbose "Running check #53: Dotfile targeting"
  while IFS=: read -r file line content; do
    [ -z "$file" ] && continue
    has_ignore_comment "$content" && continue
    rel_file="${file#$SKILL_DIR/}"
    add_finding "CRITICAL" "$rel_file" "$line" "Dotfile targeting -- writes to sensitive config files (.bashrc, .ssh, .gitconfig etc.): ${content:0:120}" "53"
  done < <(grep -rnE '(>|>>|tee|cp|mv|ln\s+-s).*(\$HOME|~)/\.(bashrc|zshrc|profile|bash_profile|ssh/(config|authorized_keys|id_)|gitconfig|npmrc|pypirc|netrc|gnupg)' "$SKILL_DIR" --include='*.sh' --include='*.py' --include='*.js' --include='*.md' 2>/dev/null || true)
fi

# 54. URL shortener hiding destination (inspired by Tirith)
if ! is_check_disabled 54; then
  CHECKS_RUN=$((CHECKS_RUN + 1))
  verbose "Running check #54: URL shortener obfuscation"
  while IFS=: read -r file line content; do
    [ -z "$file" ] && continue
    has_ignore_comment "$content" && continue
    rel_file="${file#$SKILL_DIR/}"
    add_finding "CRITICAL" "$rel_file" "$line" "URL shortener -- shortened URL hides true destination, often used in supply chain attacks: ${content:0:120}" "54"
  done < <(grep -rnE '(curl|wget|fetch)\s.*https?://(bit\.ly|t\.co|tinyurl\.com|is\.gd|rb\.gy|shorturl\.at|cutt\.ly|ow\.ly|goo\.gl|v\.gd)/' "$SKILL_DIR" 2>/dev/null || true)
fi

# --- WARNING CHECKS ---

# W1: Subprocess execution
if ! is_check_disabled W1; then
  CHECKS_RUN=$((CHECKS_RUN + 1))
  verbose "Running check W1: Subprocess execution"
  while IFS=: read -r file line content; do
    [ -z "$file" ] && continue
    has_ignore_comment "$content" && continue
    rel_file="${file#$SKILL_DIR/}"
    add_finding "WARNING" "$rel_file" "$line" "Subprocess execution: ${content:0:120}" "W1"
  done < <(grep -rnE '(child_process|execSync|spawn\(|subprocess\.|os\.system|os\.popen|Popen)' "$SKILL_DIR" --include='*.js' --include='*.ts' --include='*.tsx' --include='*.jsx' --include='*.py' 2>/dev/null || true)
fi

# W2: Network requests
if ! is_check_disabled W2; then
  CHECKS_RUN=$((CHECKS_RUN + 1))
  verbose "Running check W2: Network requests"
  while IFS=: read -r file line content; do
    [ -z "$file" ] && continue
    has_ignore_comment "$content" && continue
    rel_file="${file#$SKILL_DIR/}"
    add_finding "WARNING" "$rel_file" "$line" "Network request: ${content:0:120}" "W2"
  done < <(grep -rnE '(require\(.*(axios|node-fetch|got|request)\)|import.*(axios|fetch|requests|httpx|urllib)|XMLHttpRequest|\.fetch\s*\()' "$SKILL_DIR" --include='*.js' --include='*.ts' --include='*.tsx' --include='*.jsx' --include='*.py' 2>/dev/null || true)
fi

# W3: Minified/bundled files
if ! is_check_disabled W3; then
  CHECKS_RUN=$((CHECKS_RUN + 1))
  verbose "Running check W3: Minified files"
  while IFS= read -r file; do
    [ -z "$file" ] && continue
    rel_file="${file#$SKILL_DIR/}"
    line_len=$(head -1 "$file" 2>/dev/null | wc -c)
    if [ "$line_len" -gt 500 ]; then
      add_finding "WARNING" "$rel_file" "1" "Minified/bundled file (first line: ${line_len} chars) -- cannot audit" "W4"
    fi
  done < <(find -L "$SKILL_DIR" -name "*.js" -o -name "*.ts" 2>/dev/null || true)
fi

# W4: Filesystem write operations
if ! is_check_disabled W4; then
  CHECKS_RUN=$((CHECKS_RUN + 1))
  verbose "Running check W4: Filesystem writes"
  while IFS=: read -r file line content; do
    [ -z "$file" ] && continue
    has_ignore_comment "$content" && continue
    rel_file="${file#$SKILL_DIR/}"
    add_finding "WARNING" "$rel_file" "$line" "File write operation: ${content:0:120}" "W5"
  # shellcheck disable=SC2086
  done < <(grep -rnE '(writeFileSync|writeFile\(|open\(.*[\"'"'"']w|\.write\(|fs\.append|>> )' "$SKILL_DIR" $CODE_INCLUDES 2>/dev/null || true)
fi

# W5: Unknown external tool requirements
if ! is_check_disabled W5; then
  CHECKS_RUN=$((CHECKS_RUN + 1))
  verbose "Running check W5: Unknown external tools"
  while IFS=: read -r file line content; do
    [ -z "$file" ] && continue
    has_ignore_comment "$content" && continue
    rel_file="${file#$SKILL_DIR/}"
    if echo "$content" | grep -qiE '(npm|pip|brew|apt|cargo|go install|gem install|docker|node|python|jq|curl|git|ffmpeg|ollama|playwright|golang|gemini|rustc|make|gcc|java|mvn|gradle)'; then
      continue
    fi
    add_finding "WARNING" "$rel_file" "$line" "Requires unknown external tool: ${content:0:120}" "W1"
  done < <(grep -rniE '(requires?|must install|prerequisite|install.*first|download.*before).*\b[a-z][a-z0-9_-]+cli\b' "$SKILL_DIR" --include='*.md' 2>/dev/null || true)
fi

# W6: Insecure transport
if ! is_check_disabled W6; then
  CHECKS_RUN=$((CHECKS_RUN + 1))
  verbose "Running check W6: Insecure transport"
  while IFS=: read -r file line content; do
    [ -z "$file" ] && continue
    has_ignore_comment "$content" && continue
    rel_file="${file#$SKILL_DIR/}"
    add_finding "WARNING" "$rel_file" "$line" "Insecure transport -- TLS verification disabled: ${content:0:120}" "W6"
  # shellcheck disable=SC2086
  done < <(grep -rnE '(curl\s+.*(-k|--insecure)\b|wget\s+.*--no-check-certificate|NODE_TLS_REJECT_UNAUTHORIZED\s*=\s*.0.|verify\s*=\s*False)' "$SKILL_DIR" $CODE_INCLUDES 2>/dev/null || true)
fi

# W7: Raw IP URLs
if ! is_check_disabled W7; then
  CHECKS_RUN=$((CHECKS_RUN + 1))
  verbose "Running check W7: Raw IP URLs"
  while IFS=: read -r file line content; do
    [ -z "$file" ] && continue
    has_ignore_comment "$content" && continue
    rel_file="${file#$SKILL_DIR/}"
    if echo "$content" | grep -qE 'https?://(127\.|10\.|172\.(1[6-9]|2[0-9]|3[01])\.|192\.168\.|0\.0\.0\.0|localhost)'; then
      continue
    fi
    add_finding "CRITICAL" "$rel_file" "$line" "Raw IP URL -- bypasses domain-based trust: ${content:0:120}" "W8"
  # shellcheck disable=SC2086
  done < <(grep -rnE 'https?://[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+' "$SKILL_DIR" $CODE_INCLUDES --include='*.md' 2>/dev/null || true)
fi

# W8: Untrusted Docker registries
if ! is_check_disabled W8; then
  CHECKS_RUN=$((CHECKS_RUN + 1))
  verbose "Running check W8: Docker registries"
  while IFS=: read -r file line content; do
    [ -z "$file" ] && continue
    has_ignore_comment "$content" && continue
    rel_file="${file#$SKILL_DIR/}"
    add_finding "WARNING" "$rel_file" "$line" "Third-party Docker registry: ${content:0:120}" "W7"
  # shellcheck disable=SC2086
  done < <(grep -rnE '(docker\s+(pull|run)\s+[a-z0-9.-]+\.[a-z]{2,}/|FROM\s+[a-z0-9.-]+\.[a-z]{2,}/)' "$SKILL_DIR" $CODE_INCLUDES --include='Dockerfile*' --include='*.yaml' --include='*.yml' 2>/dev/null || true)
fi

# --- RESULTS ---

SCAN_END=$(date +%s)
SCAN_DURATION=$((SCAN_END - SCAN_START))

STATUS="clean"
EXIT_CODE=0
if [ $WARNINGS -gt 0 ]; then STATUS="caution"; EXIT_CODE=1; fi
if [ $CRITICAL -gt 0 ]; then STATUS="blocked"; EXIT_CODE=2; fi

if [ $JSON_MODE -eq 1 ]; then
  printf '{"skill":%s,"path":%s,"files_scanned":%s,"checks_run":%d,"scan_seconds":%d,"risk_score":%d,"summary":{"critical":%d,"warnings":%d,"status":"%s"},"findings":[%s]}\n' \
    "$(json_escape "$SKILL_NAME")" "$(json_escape "$SKILL_DIR")" "$FILE_COUNT" "$CHECKS_RUN" "$SCAN_DURATION" "$RISK_SCORE" "$CRITICAL" "$WARNINGS" "$STATUS" "$JSON_FINDINGS"
  exit $EXIT_CODE
fi

if [ $SARIF_MODE -eq 1 ]; then
  # SARIF v2.1.0 output for GitHub Code Scanning / VS Code
  SARIF_RESULTS=""
  SARIF_RULES=""
  SEEN_RULES=""
  idx=0
  # Parse JSON_FINDINGS to build SARIF
  while IFS= read -r finding; do
    [ -z "$finding" ] && continue
    sev=$(echo "$finding" | sed -n 's/.*"severity":"\([^"]*\)".*/\1/p')
    f=$(echo "$finding" | sed -n 's/.*"file":"\([^"]*\)".*/\1/p')
    l=$(echo "$finding" | sed -n 's/.*"line":"\([^"]*\)".*/\1/p')
    desc=$(echo "$finding" | sed -n 's/.*"description":"\([^"]*\)".*/\1/p')
    cid=$(echo "$finding" | sed -n 's/.*"check_id":"\([^"]*\)".*/\1/p')
    rem=$(echo "$finding" | sed -n 's/.*"remediation":"\([^"]*\)".*/\1/p')
    line_num="${l:-1}"
    [[ "$line_num" == "-" || "$line_num" == "?" ]] && line_num=1
    sarif_level="error"
    [ "$sev" = "WARNING" ] && sarif_level="warning"
    rule_id="skillvet/check-${cid:-unknown}"
    # Add rule if not seen
    if [[ " $SEEN_RULES " != *" $rule_id "* ]]; then
      [ -n "$SARIF_RULES" ] && SARIF_RULES+=","
      SARIF_RULES+="{\"id\":$(json_escape "$rule_id"),\"shortDescription\":{\"text\":$(json_escape "$desc")},\"helpUri\":\"https://github.com/nathangit/skillvet\",\"help\":{\"text\":$(json_escape "${rem:-Review this finding manually.}")}}"
      SEEN_RULES+=" $rule_id "
    fi
    [ -n "$SARIF_RESULTS" ] && SARIF_RESULTS+=","
    SARIF_RESULTS+="{\"ruleId\":$(json_escape "$rule_id"),\"level\":\"$sarif_level\",\"message\":{\"text\":$(json_escape "$desc")},\"locations\":[{\"physicalLocation\":{\"artifactLocation\":{\"uri\":$(json_escape "$f")},\"region\":{\"startLine\":$line_num}}}]}"
    idx=$((idx + 1))
  done <<< "$(echo "$JSON_FINDINGS" | sed 's/},{/}\n{/g')"
  printf '{"version":"2.1.0","$schema":"https://raw.githubusercontent.com/oasis-tcs/sarif-spec/main/sarif-2.1/schema/sarif-schema-2.1.0.json","runs":[{"tool":{"driver":{"name":"skillvet","version":"2.1.0","informationUri":"https://github.com/nathangit/skillvet","rules":[%s]}},"results":[%s]}]}\n' "$SARIF_RULES" "$SARIF_RESULTS"
  exit $EXIT_CODE
fi

if [ $SUMMARY_MODE -eq 1 ]; then
  if [ $EXIT_CODE -eq 0 ]; then
    echo "skillvet: $SKILL_NAME -- clean (${SCAN_DURATION}s)"
  else
    echo "skillvet: $SKILL_NAME -- $STATUS ($CRITICAL critical, $WARNINGS warnings, risk=$RISK_SCORE, ${SCAN_DURATION}s)"
  fi
  exit $EXIT_CODE
fi

echo ""
if [ $CRITICAL -eq 0 ] && [ $WARNINGS -eq 0 ]; then
  printf "${GREEN}CLEAN${NC} -- No issues found in %s\n" "$SKILL_NAME"
  printf "   %d files scanned, %d checks run in %ds\n" "$FILE_COUNT" "$CHECKS_RUN" "$SCAN_DURATION"
  exit 0
fi

printf "%b" "$FINDINGS"
echo "---"
printf "Summary: ${RED}%d critical${NC}, ${YELLOW}%d warnings${NC} | Risk score: %d | %d files, %d checks in %ds\n" \
  "$CRITICAL" "$WARNINGS" "$RISK_SCORE" "$FILE_COUNT" "$CHECKS_RUN" "$SCAN_DURATION"

if [ $CRITICAL -gt 0 ]; then
  printf "\n${RED}BLOCKED -- Critical issues found. Do NOT use this skill without manual review.${NC}\n"
  exit 2
else
  printf "\n${YELLOW}CAUTION -- Warnings found. Review before using.${NC}\n"
  exit 1
fi
