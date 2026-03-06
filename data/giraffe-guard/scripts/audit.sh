#!/bin/bash
set -uo pipefail

# ============================================================
# 🦒 Giraffe Guard v3.1.0 — 长颈鹿卫士
# OpenClaw Skill Security Auditor
# Scan skill directories for supply chain attacks and malicious code
# Compatible with macOS (BSD) and Linux (GNU)
# Zero dependencies: only uses bash, grep, sed, find, file, awk, readlink, perl
# ============================================================

VERSION="3.1.0"

# --- Color definitions ---
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
BOLD='\033[1m'
DIM='\033[2m'
NC='\033[0m'

# --- Parameters ---
VERBOSE=false
JSON_OUTPUT=false
SARIF_OUTPUT=false
STRICT_MODE=false
PRE_INSTALL=false
QUIET=false
WHITELIST_FILE=""
TARGET_DIR=""
CONTEXT_LINES=2  # context lines for --verbose
MIN_SEVERITY=""      # "", "WARNING", "CRITICAL"
FAIL_ON=""           # "", "WARNING", "CRITICAL"
declare -a SKIP_DIRS=()
declare -a SKIP_RULES=()
PRE_INSTALL_TMPDIR=""

SELF_PATH="$(cd "$(dirname "$0")" && pwd)/$(basename "$0")"

# Detect Python 3 for AST deep analysis (optional, zero-dependency fallback)
PYTHON3_PATH=""
if command -v python3 &>/dev/null; then
    PYTHON3_PATH=$(command -v python3)
fi

# Temp files for counter passing across subshells
TMPDIR_AUDIT=$(mktemp -d)
echo 0 > "$TMPDIR_AUDIT/findings"
echo 0 > "$TMPDIR_AUDIT/critical"
echo 0 > "$TMPDIR_AUDIT/warning"
echo 0 > "$TMPDIR_AUDIT/info"
echo 0 > "$TMPDIR_AUDIT/whitelisted"
echo 0 > "$TMPDIR_AUDIT/files"
FINDINGS_FILE="$TMPDIR_AUDIT/findings_json"
touch "$FINDINGS_FILE"
trap 'rm -rf "$TMPDIR_AUDIT"; [[ -n "$PRE_INSTALL_TMPDIR" ]] && rm -rf "$PRE_INSTALL_TMPDIR"' EXIT

usage() {
    cat <<EOF
Usage: $(basename "$0") [OPTIONS] <target-directory>

🦒 Giraffe Guard v${VERSION} — OpenClaw Skill Security Auditor
Scan skill directories for supply chain attacks and malicious code.

Options:
  --verbose         Show detailed findings with context lines
  --json            Output JSON report
  --sarif           Output SARIF format (for GitHub Code Scanning)
  --strict          Enable strict mode (high entropy detection)
  --quiet           Quiet mode: only output summary and exit code
  --whitelist F     Specify whitelist file
  --context N       Context lines (default: 2, used with --verbose)
  --skip-dir D      Skip directory name (repeatable)
  --skip-rule R     Skip a specific rule (repeatable, use --list-rules to see names)
  --min-severity S  Minimum severity to report: INFO, WARNING, CRITICAL
  --fail-on S       Set exit code threshold: WARNING (default) or CRITICAL
  --pre-install     Pre-install mode: scan BEFORE npm/pip install (accepts git URL or local dir)
  --list-rules      List all available detection rules and exit
  --version         Show version
  -h, --help        Show help

Examples:
  $(basename "$0") /path/to/skills
  $(basename "$0") --verbose --json /path/to/skills
  $(basename "$0") --quiet --fail-on CRITICAL /path/to/skills
  $(basename "$0") --skip-rule pipe-execution --min-severity WARNING /path/to/skills
  $(basename "$0") --sarif /path/to/skills > results.sarif
  $(basename "$0") --pre-install https://github.com/user/skill-repo.git
  $(basename "$0") --list-rules

Exit codes:
  0  Clean (no findings above threshold)
  1  Warnings found (or above --fail-on threshold)
  2  Critical findings found
EOF
    exit 0
}

list_rules() {
    cat <<EOF
🦒 Giraffe Guard v${VERSION} — Detection Rules

Grep-based rules (always active):
  RULE NAME                   SEVERITY    DESCRIPTION
  pipe-execution              CRITICAL    curl/wget piped to shell (curl|bash)
  base64-decode-pipe          CRITICAL    Base64 decoded and piped to execution
  base64-echo-decode          CRITICAL    Echo piped to base64 decode
  long-base64-string          WARNING     Suspiciously long Base64 encoded string
  security-bypass             CRITICAL    macOS Gatekeeper / quarantine bypass
  dangerous-permissions       WARNING     chmod 777, setuid, chown root
  suspicious-network-ip       WARNING     Direct IP connection (non-private)
  tor-onion-address           CRITICAL    .onion domain usage
  reverse-shell               CRITICAL    Reverse shell patterns (nc -e, /dev/tcp)
  netcat-listener             WARNING     Netcat listener
  covert-exec-python          WARNING     os.system() / subprocess in unexpected context
  covert-exec-eval            WARNING     eval() in shell/JS/TS files
  file-disguise               WARNING     Double extensions (.pdf.exe, .jpg.sh)
  sensitive-data-access       WARNING     /etc/passwd, /etc/shadow access
  anti-sandbox                CRITICAL    Anti-debug techniques (ptrace, LD_PRELOAD)
  covert-downloader-python    CRITICAL    Python one-liner downloader
  covert-downloader-node      CRITICAL    Node one-liner downloader
  covert-downloader-powershell CRITICAL   PowerShell download cradles
  cron-injection              WARNING     Crontab / LaunchAgent modification
  persistence-launchagent     CRITICAL    LaunchAgent/Daemon creation
  encoding-obfuscation        WARNING     Hex/octal/unicode escape sequences
  suspicious-npm-package      WARNING     Known malicious npm packages
  postinstall-script          WARNING     npm lifecycle scripts with network/exec
  skillmd-injection           WARNING     Skill.md with embedded code injection
  dockerfile-privileged       WARNING     Dockerfile privileged / ADD from URL
  zero-width-chars            WARNING     Zero-width unicode characters
  hardcoded-aws-key           CRITICAL    AWS access key (AKIA...)
  hardcoded-github-token      CRITICAL    GitHub personal access token (ghp_...)
  hardcoded-stripe-key        CRITICAL    Stripe live secret key (sk_live_...)
  hardcoded-slack-token       CRITICAL    Slack token (xoxb-/xoxp-/xoxs-)
  hardcoded-slack-webhook     WARNING     Slack webhook URL
  hardcoded-generic-secret    WARNING     password/secret/api_key = "..."
  hardcoded-private-key       CRITICAL    Embedded private key (BEGIN.*PRIVATE KEY)
  actions-unpinned            WARNING     GitHub Actions not pinned to SHA
  actions-script-injection    CRITICAL    Untrusted input in workflow expression
  actions-excessive-permissions  WARNING  Workflow with write-all permissions
  build-script-download       WARNING     Download in Makefile/configure
  build-script-obfuscation    WARNING     Encoded content in build scripts
  pyproject-suspicious-hook   CRITICAL    Suspicious code in pyproject.toml
  npm-obfuscated-lifecycle    WARNING     Obfuscated npm lifecycle scripts
  gemfile-untrusted-source    WARNING     Gem from non-standard git source

AST-based rules (Python files, requires python3):
  ast-eval-dynamic            CRITICAL    eval/exec with non-literal argument
  ast-compile-exec            WARNING     compile() with exec/eval mode
  ast-dynamic-import          CRITICAL    __import__/importlib with dynamic name
  ast-dangerous-import        WARNING     __import__ of os/subprocess/ctypes
  ast-getattr-dynamic         WARNING     getattr() with dynamic attribute
  ast-getattr-dangerous       CRITICAL    getattr(obj, 'system'/'Popen'/etc)
  ast-command-concat          CRITICAL    os.system/subprocess with string concat
  ast-command-fstring         CRITICAL    os.system/subprocess with f-string
  ast-suspicious-command      WARNING     Static command with curl/wget/nc/base64
  ast-b64-exec                CRITICAL    base64.b64decode() passed to exec
  ast-codec-obfuscation       WARNING     codecs.decode with rot13/hex
  ast-system-write            CRITICAL    open() writing to system paths
  ast-system-read             INFO        open() reading system paths
  ast-env-access              INFO        Accessing sensitive env vars
  ast-high-entropy-string     WARNING     High Shannon entropy string assignment
  ast-string-concat-cmd       CRITICAL    String concatenation builds shell command
  ast-bare-except-pass        INFO        Bare except:pass silences all errors
EOF
    exit 0
}

# --- Argument parsing ---
while [[ $# -gt 0 ]]; do
    case "$1" in
        --verbose) VERBOSE=true; shift ;;
        --json) JSON_OUTPUT=true; shift ;;
        --sarif) SARIF_OUTPUT=true; JSON_OUTPUT=true; shift ;;
        --strict) STRICT_MODE=true; shift ;;
        --pre-install) PRE_INSTALL=true; shift ;;
        --quiet) QUIET=true; shift ;;
        --whitelist) WHITELIST_FILE="$2"; shift 2 ;;
        --context) CONTEXT_LINES="$2"; shift 2 ;;
        --skip-dir) SKIP_DIRS+=("$2"); shift 2 ;;
        --skip-rule) SKIP_RULES+=("$2"); shift 2 ;;
        --min-severity) MIN_SEVERITY="$2"; shift 2 ;;
        --fail-on) FAIL_ON="$2"; shift 2 ;;
        --list-rules) list_rules ;;
        --version) echo "giraffe-guard v${VERSION}"; exit 0 ;;
        -h|--help) usage ;;
        -*) echo "Unknown option: $1"; exit 1 ;;
        *) TARGET_DIR="$1"; shift ;;
    esac
done

if [[ -z "$TARGET_DIR" ]]; then
    echo "Error: Please specify a target directory (or git URL with --pre-install) to scan"
    usage
fi

# --- Pre-install: clone git URL to temp dir ---
if [[ "$PRE_INSTALL" == true && "$TARGET_DIR" == http* || "$TARGET_DIR" == git@* || "$TARGET_DIR" == *.git ]]; then
    PRE_INSTALL_TMPDIR=$(mktemp -d)
    echo "Pre-install mode: cloning $TARGET_DIR ..."
    if ! git clone --depth 1 --config core.hooksPath=/dev/null "$TARGET_DIR" "$PRE_INSTALL_TMPDIR/repo" 2>/dev/null; then
        echo "Error: Failed to clone $TARGET_DIR"
        rm -rf "$PRE_INSTALL_TMPDIR"
        exit 1
    fi
    TARGET_DIR="$PRE_INSTALL_TMPDIR/repo"
    echo "Cloned to temp dir. Scanning WITHOUT running install..."
    echo ""
fi

if [[ ! -d "$TARGET_DIR" ]]; then
    echo "Error: Directory does not exist: $TARGET_DIR"
    exit 1
fi

# --- Whitelist loading ---
declare -a WHITELIST_ENTRIES
load_whitelist() {
    if [[ -n "$WHITELIST_FILE" && -f "$WHITELIST_FILE" ]]; then
        while IFS= read -r line; do
            [[ -z "$line" || "$line" == \#* ]] && continue
            WHITELIST_ENTRIES+=("$line")
        done < "$WHITELIST_FILE"
    fi
}

is_whitelisted() {
    local filepath="$1"
    local lineno="$2"
    local rule="$3"
    for entry in "${WHITELIST_ENTRIES[@]+"${WHITELIST_ENTRIES[@]}"}"; do
        if [[ "$entry" == "${filepath}:${lineno}" || "$entry" == "${filepath}:${rule}" || "$entry" == "$filepath" ]]; then
            return 0
        fi
    done
    return 1
}

# --- JSON helpers ---
json_escape() {
    local s="$1"
    s="${s//\\/\\\\}"
    s="${s//\"/\\\"}"
    s="${s//$'\n'/\\n}"
    s="${s//$'\r'/\\r}"
    s="${s//$'\t'/\\t}"
    printf '%s' "$s"
}

# --- Context fetching (for --verbose) ---
get_context() {
    local file="$1"
    local lineno="$2"
    local ctx_lines="$CONTEXT_LINES"
    local start=$((lineno - ctx_lines))
    [[ $start -lt 1 ]] && start=1
    local end=$((lineno + ctx_lines))
    sed -n "${start},${end}p" "$file" 2>/dev/null | while IFS= read -r ctx_line; do
        if [[ $start -eq $lineno ]]; then
            echo "  >>> ${start}: ${ctx_line}"
        else
            echo "      ${start}: ${ctx_line}"
        fi
        start=$((start + 1))
    done
}

# --- Doc context detection (reduce false positives) ---
# Returns 0 = doc context (likely false positive), 1 = not doc context
is_doc_context() {
    local file="$1"
    local lineno="$2"
    local ext="${file##*.}"

    # Markdown / text files: tables, comments, list items are likely documentation
    if [[ "$ext" == "md" || "$ext" == "txt" || "$ext" == "rst" ]]; then
        local line
        line=$(sed -n "${lineno}p" "$file" 2>/dev/null)
        # Table row
        if echo "$line" | grep -qE '^\s*\|'; then
            return 0
        fi
        # Comment line (# or // or <!--)
        if echo "$line" | grep -qE '^\s*(#|//|<!--)'; then
            return 0
        fi
        # Descriptive list item
        if echo "$line" | grep -qE '^\s*[-*]\s+.*\b(example|示例|说明|description|e\.g\.|如|用于|for|about)\b'; then
            return 0
        fi
    fi
    return 1
}

# --- Safe context detection (reduce false positives in code files) ---
# Returns 0 = safe context (likely false positive), 1 = not safe context
is_safe_context() {
    local file="$1"
    local lineno="$2"
    local ext="${file##*.}"

    local line
    line=$(sed -n "${lineno}p" "$file" 2>/dev/null)
    [[ -z "$line" ]] && return 1

    # 1. Shell/Python/Ruby comment lines (# ...)
    if [[ "$ext" == "sh" || "$ext" == "bash" || "$ext" == "zsh" || "$ext" == "py" || "$ext" == "rb" || "$ext" == "yaml" || "$ext" == "yml" || "$ext" == "toml" || "$ext" == "cfg" || "$ext" == "conf" ]]; then
        if echo "$line" | grep -qE '^\s*#'; then
            return 0
        fi
    fi

    # 2. JS/TS/C/Java single-line comment (// ...)
    if [[ "$ext" == "js" || "$ext" == "ts" || "$ext" == "c" || "$ext" == "cpp" || "$ext" == "java" || "$ext" == "go" || "$ext" == "rs" || "$ext" == "swift" || "$ext" == "kt" ]]; then
        if echo "$line" | grep -qE '^\s*//'; then
            return 0
        fi
    fi

    # 3. Inside a grep/sed/awk regex pattern (the line IS a detection rule, not malicious code)
    if echo "$line" | grep -qE '^\s*(grep|egrep|fgrep|sed|awk|perl)\s+(-[a-zA-Z]+\s+)*'; then
        return 0
    fi

    # 4. Echo/printf string literal (remediation text, documentation, etc.)
    if echo "$line" | grep -qE '^\s*(echo|printf|log|warn|error|info|debug)\s'; then
        return 0
    fi

    # 5. Case pattern or variable assignment with descriptive text
    if echo "$line" | grep -qE '^\s*[a-z_-]+\)\s+echo\s+"'; then
        return 0
    fi

    # 6. String variable assignment (remediation/message/description)
    if echo "$line" | grep -qE '^\s*(local\s+|export\s+)?(msg|message|desc|description|hint|help|usage|error_msg|warn_msg|remediation|fix_hint)\s*='; then
        return 0
    fi

    return 1
}

# --- Remediation map ---
get_remediation() {
    local rule="$1"
    case "$rule" in
        pipe-execution*) echo "Download file first, verify checksum, then execute" ;;
        base64-decode-pipe|base64-echo-decode) echo "Avoid piping decoded base64 to shell; decode to file and inspect first" ;;
        security-bypass*) echo "Remove Gatekeeper/SIP bypass; use proper code signing" ;;
        dangerous-permissions) echo "Use least-privilege permissions; avoid chmod 777 or setuid" ;;
        tor-onion-address) echo "Remove .onion addresses; use standard domains" ;;
        reverse-shell) echo "Remove reverse shell patterns; use proper remote access tools" ;;
        suspicious-network-ip) echo "Use domain names instead of direct IP addresses" ;;
        netcat-listener) echo "Remove netcat listeners; use proper service management" ;;
        covert-exec-eval) echo "Replace eval() with safer alternatives (arrays, parameter expansion)" ;;
        covert-exec-python) echo "Use subprocess with explicit args list instead of os.system()" ;;
        covert-exec-child-process) echo "Validate and sanitize all input before passing to child_process" ;;
        file-type-disguise) echo "Remove or rename file to match its actual binary type" ;;
        ssh-key-exfiltration) echo "Never transmit SSH keys over network; use ssh-agent forwarding" ;;
        cloud-credential-access) echo "Use IAM roles/service accounts instead of credential files" ;;
        env-exfiltration|env-dump-exfiltration) echo "Never send env vars over network; use secret managers" ;;
        anti-sandbox) echo "Remove anti-debug techniques; they indicate malicious intent" ;;
        covert-downloader*) echo "Use package managers instead of one-liner downloaders" ;;
        persistence-launchagent) echo "Remove LaunchAgent creation; use proper installation methods" ;;
        cron-injection) echo "Document scheduled tasks; avoid injecting cron entries silently" ;;
        hidden-executable) echo "Remove hidden executable files or document their purpose" ;;
        hex-obfuscation|unicode-obfuscation) echo "Replace encoded strings with readable code" ;;
        string-concat-bypass) echo "Remove string concatenation used to evade detection" ;;
        symlink-*) echo "Remove symlinks to sensitive locations; use proper file references" ;;
        env-file-leak) echo "Add .env to .gitignore; use .env.example with placeholders" ;;
        typosquat-*) echo "Verify package name spelling against official registry" ;;
        custom-registry|custom-pip-source) echo "Use official registries (npmjs.org, pypi.org)" ;;
        malicious-postinstall|malicious-setup-py) echo "Review lifecycle scripts; remove network/exec calls from install hooks" ;;
        git-hooks) echo "Review hook content; remove if not intentional" ;;
        sensitive-file-leak) echo "Add to .gitignore; rotate compromised credentials immediately" ;;
        skillmd-prompt-injection) echo "Remove prompt injection patterns from SKILL.md" ;;
        skillmd-dangerous-command) echo "Remove destructive commands from SKILL.md" ;;
        skillmd-privilege-escalation) echo "Remove sudo/root requirements from SKILL.md" ;;
        dockerfile-privileged) echo "Remove --privileged; use specific capabilities instead" ;;
        dockerfile-sensitive-mount) echo "Avoid mounting host /etc, /root, /home into containers" ;;
        dockerfile-host-network) echo "Use bridge networking instead of --net=host" ;;
        zero-width-chars|embedded-bom) echo "Remove hidden Unicode characters; they may conceal malicious content" ;;
        hardcoded-aws-key) echo "Use IAM roles or AWS Secrets Manager instead of hardcoded keys" ;;
        hardcoded-github-token) echo "Use GITHUB_TOKEN from Actions or GitHub App tokens" ;;
        hardcoded-stripe-key) echo "Use environment variables for Stripe keys" ;;
        hardcoded-slack-*) echo "Use environment variables for Slack tokens/webhooks" ;;
        hardcoded-generic-secret) echo "Move secrets to environment variables or a secret manager" ;;
        hardcoded-private-key) echo "Store private keys in secure key management systems" ;;
        actions-unpinned) echo "Pin action to specific commit SHA: uses: owner/action@<sha>" ;;
        actions-script-injection) echo "Use intermediate env variable instead of direct expression injection" ;;
        actions-excessive-permissions) echo "Use least-privilege: set specific read/write per scope" ;;
        high-entropy-string) echo "Verify if this is a hardcoded secret; move to env var if so" ;;
        build-script-download) echo "Vendor dependencies; avoid downloading during build" ;;
        build-script-obfuscation) echo "Remove obfuscated code from build scripts" ;;
        lifecycle-hook-obfuscated) echo "Remove obfuscated commands from lifecycle hooks" ;;
        gemfile-untrusted-source) echo "Use official RubyGems or well-known git hosts" ;;
        pyproject-suspicious-hook) echo "Review build hooks in pyproject.toml for suspicious commands" ;;
        *) echo "" ;;
    esac
}

# --- Skip-rule check ---
is_rule_skipped() {
    local rule="$1"
    for sr in "${SKIP_RULES[@]+"${SKIP_RULES[@]}"}"; do
        if [[ "$rule" == "$sr" || "$rule" == "${sr}"* ]]; then
            return 0
        fi
    done
    return 1
}

# --- Severity filter ---
severity_rank() {
    case "$1" in
        INFO) echo 0 ;;
        WARNING) echo 1 ;;
        CRITICAL) echo 2 ;;
        *) echo 0 ;;
    esac
}

passes_severity_filter() {
    local level="$1"
    if [[ -z "$MIN_SEVERITY" ]]; then return 0; fi
    local level_rank min_rank
    level_rank=$(severity_rank "$level")
    min_rank=$(severity_rank "$MIN_SEVERITY")
    [[ $level_rank -ge $min_rank ]]
}

# --- Finding recorder ---
add_finding() {
    local level="$1"      # CRITICAL / WARNING / INFO
    local filepath="$2"
    local lineno="$3"
    local rule="$4"
    local content="$5"

    # Skip-rule check
    if is_rule_skipped "$rule"; then return 0; fi

    # Severity filter
    if ! passes_severity_filter "$level"; then return 0; fi

    # Whitelist check
    local wl_status=""
    if is_whitelisted "$filepath" "$lineno" "$rule"; then
        wl_status="WHITELISTED"
        echo $(( $(cat "$TMPDIR_AUDIT/whitelisted") + 1 )) > "$TMPDIR_AUDIT/whitelisted"
    else
        echo $(( $(cat "$TMPDIR_AUDIT/findings") + 1 )) > "$TMPDIR_AUDIT/findings"
        case "$level" in
            CRITICAL) echo $(( $(cat "$TMPDIR_AUDIT/critical") + 1 )) > "$TMPDIR_AUDIT/critical" ;;
            WARNING)  echo $(( $(cat "$TMPDIR_AUDIT/warning") + 1 )) > "$TMPDIR_AUDIT/warning" ;;
            INFO)     echo $(( $(cat "$TMPDIR_AUDIT/info") + 1 )) > "$TMPDIR_AUDIT/info" ;;
        esac
        # Track per-file findings for top offenders
        echo "$filepath" >> "$TMPDIR_AUDIT/file_hits"
    fi

    # Get remediation hint
    local fix_hint
    fix_hint=$(get_remediation "$rule")

    if [[ "$JSON_OUTPUT" == true ]]; then
        local json_fix=""
        [[ -n "$fix_hint" ]] && json_fix=",\"remediation\":\"$(json_escape "$fix_hint")\""
        echo "{\"level\":\"$(json_escape "$level")\",\"file\":\"$(json_escape "$filepath")\",\"line\":$lineno,\"rule\":\"$(json_escape "$rule")\",\"content\":\"$(json_escape "$content")\",\"whitelisted\":$([ "$wl_status" = "WHITELISTED" ] && echo true || echo false)${json_fix}}" >> "$FINDINGS_FILE"
    else
        local color tag
        case "$level" in
            CRITICAL) color="$RED"; tag="CRIT" ;;
            WARNING)  color="$YELLOW"; tag="WARN" ;;
            INFO)     color="$CYAN"; tag="INFO" ;;
        esac
        if [[ "$QUIET" == true ]]; then
            : # suppress per-finding output in quiet mode
        elif [[ "$wl_status" == "WHITELISTED" ]]; then
            echo -e "  ${DIM}[WHITELISTED] ${level} | ${filepath}:${lineno} | ${rule}${NC}"
        else
            echo -e "  ${color}[${tag}]${NC} | ${BOLD}${filepath}:${lineno}${NC} | ${CYAN}${rule}${NC}"
            echo -e "     ${DIM}${content}${NC}"
            if [[ -n "$fix_hint" ]]; then
                echo -e "     ${GREEN}>> FIX: ${fix_hint}${NC}"
            fi
            if [[ "$VERBOSE" == true && "$lineno" != "0" ]]; then
                echo -e "${DIM}$(get_context "$filepath" "$lineno")${NC}"
                echo ""
            fi
        fi
    fi
}

# ============================================================
# Detection Rules
# ============================================================

# Rule 1: Pipe execution (CRITICAL)
check_pipe_execution() {
    local file="$1"
    grep -n -E '(curl|wget)\s+.*\|\s*(bash|sh|zsh|dash|ksh|python[23]?|perl|ruby|node)(\s|$)' "$file" 2>/dev/null | while IFS=: read -r lineno content; do
        if is_doc_context "$file" "$lineno"; then
            add_finding "WARNING" "$file" "$lineno" "pipe-execution-doc" "$content"
        else
            add_finding "CRITICAL" "$file" "$lineno" "pipe-execution" "$content"
        fi
    done
}

# Rule 2: Base64 obfuscation (CRITICAL / WARNING)
check_base64_obfuscation() {
    local file="$1"
    # base64 -d piped to execution
    grep -n -E 'base64\s+(-d|--decode)\s*\|' "$file" 2>/dev/null | while IFS=: read -r lineno content; do
        if is_safe_context "$file" "$lineno"; then continue; fi
        add_finding "CRITICAL" "$file" "$lineno" "base64-decode-pipe" "$content"
    done
    # echo ... | base64 -d variant
    grep -n -E 'echo\s+.*\|\s*base64\s+(-d|--decode)' "$file" 2>/dev/null | while IFS=: read -r lineno content; do
        if is_safe_context "$file" "$lineno"; then continue; fi
        add_finding "CRITICAL" "$file" "$lineno" "base64-echo-decode" "$content"
    done
    # Suspiciously long base64 strings (>100 chars)
    grep -n -E '[A-Za-z0-9+/]{100,}={0,2}' "$file" 2>/dev/null | while IFS=: read -r lineno content; do
        # Exclude legitimate long strings (JWT examples, SSH keys, etc.)
        case "$content" in
            *"ssh-"*|*"BEGIN "*|*"example"*|*"示例"*|*"token"*) continue ;;
        esac
        add_finding "WARNING" "$file" "$lineno" "long-base64-string" "Suspiciously long Base64 encoded string detected"
    done
}

# Rule 3: Security bypass (CRITICAL)
check_security_bypass() {
    local file="$1"
    grep -n -E 'xattr\s+-(c|d\s+com\.apple\.quarantine)|spctl\s+--master-disable|csrutil\s+disable' "$file" 2>/dev/null | while IFS=: read -r lineno content; do
        if is_doc_context "$file" "$lineno"; then
            add_finding "WARNING" "$file" "$lineno" "security-bypass-doc" "$content"
        else
            add_finding "CRITICAL" "$file" "$lineno" "security-bypass" "$content"
        fi
    done
}

# Rule 4: Dangerous permissions (WARNING)
check_dangerous_permissions() {
    local file="$1"
    grep -n -E 'chmod\s+(777|\+x\s+/tmp|4[0-7]{3}|u\+s)|chown\s+root|chgrp\s+root' "$file" 2>/dev/null | while IFS=: read -r lineno content; do
        case "$content" in
            *"chmod +x scripts/"*|*"chmod +x audit"*|*"chmod +x ./"*) continue ;;
        esac
        if is_doc_context "$file" "$lineno"; then continue; fi
        if is_safe_context "$file" "$lineno"; then continue; fi
        add_finding "WARNING" "$file" "$lineno" "dangerous-permissions" "$content"
    done
}

# Rule 5: Suspicious network behavior
check_suspicious_network() {
    local file="$1"
    # Direct IP connection (exclude local/private addresses)
    grep -n -E 'https?://[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+' "$file" 2>/dev/null | while IFS=: read -r lineno content; do
        if echo "$content" | grep -qE '127\.0\.0\.1|0\.0\.0\.0|192\.168\.|10\.[0-9]+\.|172\.(1[6-9]|2[0-9]|3[01])\.'; then
            continue
        fi
        add_finding "WARNING" "$file" "$lineno" "suspicious-network-ip" "$content"
    done
    # .onion domain
    grep -n -E '[a-z2-7]{16,56}\.onion\b' "$file" 2>/dev/null | while IFS=: read -r lineno content; do
        add_finding "CRITICAL" "$file" "$lineno" "tor-onion-address" "$content"
    done
    # Reverse shell patterns
    grep -n -E 'nc\s+(-e|--exec)|ncat\s+(-e|--exec)|bash\s+-i\s+>\&\s*/dev/tcp|/dev/udp/' "$file" 2>/dev/null | while IFS=: read -r lineno content; do
        if is_safe_context "$file" "$lineno"; then continue; fi
        add_finding "CRITICAL" "$file" "$lineno" "reverse-shell" "$content"
    done
    # Netcat listener
    grep -n -E '\bnc\s+-[lp]|\bncat\s+-[lp]|\bnetcat\s+-[lp]' "$file" 2>/dev/null | while IFS=: read -r lineno content; do
        if is_doc_context "$file" "$lineno"; then continue; fi
        add_finding "WARNING" "$file" "$lineno" "netcat-listener" "$content"
    done
}

# Rule 6: Covert execution (context-aware)
check_covert_execution() {
    local file="$1"
    local ext="${file##*.}"

    # Python dangerous calls: WARNING in .py, CRITICAL in other script files
    if [[ "$ext" == "py" ]]; then
        grep -n -E 'os\.system\s*\(|subprocess\.(call|Popen|run)\s*\(|__import__\s*\(' "$file" 2>/dev/null | while IFS=: read -r lineno content; do
            if is_doc_context "$file" "$lineno"; then continue; fi
            if is_safe_context "$file" "$lineno"; then continue; fi
            add_finding "WARNING" "$file" "$lineno" "covert-exec-python" "$content"
        done
    elif [[ "$ext" != "md" && "$ext" != "txt" && "$ext" != "rst" ]]; then
        grep -n -E 'os\.system\s*\(|subprocess\.(call|Popen|run)\s*\(|__import__\s*\(' "$file" 2>/dev/null | while IFS=: read -r lineno content; do
            if is_doc_context "$file" "$lineno"; then continue; fi
            if is_safe_context "$file" "$lineno"; then continue; fi
            add_finding "WARNING" "$file" "$lineno" "covert-exec-python" "$content"
        done
    fi

    # eval() in markdown/shell/js/ts files
    if [[ "$ext" == "md" || "$ext" == "txt" || "$ext" == "sh" || "$ext" == "js" || "$ext" == "ts" ]]; then
        grep -n -E '\beval\s*\(' "$file" 2>/dev/null | while IFS=: read -r lineno content; do
            # Exclude common safe shell eval patterns
            if [[ "$ext" == "sh" ]]; then
                case "$content" in
                    *'eval "$(ssh-agent'*|*'eval "$(brew'*|*'eval "$(pyenv'*|*'eval "$(rbenv'*|*'eval "$(nodenv'*|*'eval "$(direnv'*) continue ;;
                esac
            fi
            if is_doc_context "$file" "$lineno"; then continue; fi
            if is_safe_context "$file" "$lineno"; then continue; fi
            add_finding "WARNING" "$file" "$lineno" "covert-exec-eval" "$content"
        done
    fi

    # child_process in markdown
    if [[ "$ext" == "md" || "$ext" == "txt" ]]; then
        grep -n -E "require\s*\(\s*['\"]child_process['\"]" "$file" 2>/dev/null | while IFS=: read -r lineno content; do
            add_finding "WARNING" "$file" "$lineno" "covert-exec-child-process" "$content"
        done
    fi
}

# Rule 7: File type disguise (CRITICAL)
check_file_disguise() {
    local file="$1"
    local ext="${file##*.}"
    if [[ "$ext" == "md" || "$ext" == "txt" || "$ext" == "json" || "$ext" == "yaml" || "$ext" == "yml" || "$ext" == "cfg" || "$ext" == "ini" || "$ext" == "conf" || "$ext" == "csv" || "$ext" == "xml" || "$ext" == "log" ]]; then
        local filetype
        filetype=$(file -b "$file" 2>/dev/null)
        case "$filetype" in
            *"Mach-O"*|*"ELF"*|*"PE32"*|*"shared object"*|*"dynamically linked"*)
                add_finding "CRITICAL" "$file" "0" "file-type-disguise" "Extension .$ext but actual type: ${filetype}"
                ;;
        esac
    fi
}

# Rule 8: Sensitive data exfiltration (context-aware)
check_sensitive_data_access() {
    local file="$1"
    local ext="${file##*.}"

    # SSH key access - CRITICAL in script files
    grep -n -E '(cat|cp|scp|tar|zip|curl.*-d|POST).*~/\.ssh/|\.ssh/id_(rsa|ed25519|ecdsa)' "$file" 2>/dev/null | while IFS=: read -r lineno content; do
        case "$content" in
            *"#"*|*"注意"*|*"warning"*|*"caution"*|*"never"*|*"不要"*|*"do not"*|*"example"*|*"示例"*) continue ;;
        esac
        if [[ "$ext" == "sh" || "$ext" == "py" || "$ext" == "rb" || "$ext" == "js" ]]; then
            add_finding "CRITICAL" "$file" "$lineno" "ssh-key-exfiltration" "$content"
        else
            if is_doc_context "$file" "$lineno"; then continue; fi
            add_finding "WARNING" "$file" "$lineno" "ssh-key-reference" "$content"
        fi
    done

    # AWS/Cloud credential theft
    grep -n -E '(cat|cp|curl.*-d|POST).*~/\.(aws|config/gcloud|azure)/' "$file" 2>/dev/null | while IFS=: read -r lineno content; do
        if is_doc_context "$file" "$lineno"; then continue; fi
        add_finding "CRITICAL" "$file" "$lineno" "cloud-credential-access" "$content"
    done

    # Environment variable exfiltration
    grep -n -E '(curl|wget|nc|http).*\$\{?(GITHUB_TOKEN|GH_TOKEN|AWS_SECRET_ACCESS_KEY|OPENAI_API_KEY|NPM_TOKEN|PRIVATE_KEY|DATABASE_URL)' "$file" 2>/dev/null | while IFS=: read -r lineno content; do
        add_finding "CRITICAL" "$file" "$lineno" "env-exfiltration" "Sending env vars over network: $content"
    done

    # Bulk env dump
    grep -n -E '\benv\b\s*\|\s*(curl|wget|nc|base64)|printenv\s*\|\s*(curl|wget|nc)' "$file" 2>/dev/null | while IFS=: read -r lineno content; do
        add_finding "CRITICAL" "$file" "$lineno" "env-dump-exfiltration" "$content"
    done
}

# Rule 9: Anti-sandbox / Anti-debug (CRITICAL)
check_anti_sandbox() {
    local file="$1"
    grep -n -E 'ptrace\s*\(|PTRACE_TRACEME|DYLD_INSERT_LIBRARIES|DYLD_FORCE_FLAT|LD_PRELOAD\s*=' "$file" 2>/dev/null | while IFS=: read -r lineno content; do
        if is_doc_context "$file" "$lineno"; then continue; fi
        if is_safe_context "$file" "$lineno"; then continue; fi
        add_finding "CRITICAL" "$file" "$lineno" "anti-sandbox" "$content"
    done
}

# Rule 10: Covert downloader (CRITICAL)
check_covert_downloader() {
    local file="$1"
    # Python one-liner downloader
    grep -n -E 'python[23]?\s+-c\s+.*\b(urllib|requests\.(get|post)|urlopen|urlretrieve)\b' "$file" 2>/dev/null | while IFS=: read -r lineno content; do
        if is_doc_context "$file" "$lineno"; then
            add_finding "WARNING" "$file" "$lineno" "covert-downloader-python-doc" "$content"
        else
            add_finding "CRITICAL" "$file" "$lineno" "covert-downloader-python" "$content"
        fi
    done
    # Node one-liner downloader
    grep -n -E "node\s+-e\s+.*require\s*\(\s*['\"]https?['\"]" "$file" 2>/dev/null | while IFS=: read -r lineno content; do
        add_finding "CRITICAL" "$file" "$lineno" "covert-downloader-node" "$content"
    done
    # Ruby/Perl one-liner downloader
    grep -n -E '(ruby|perl)\s+-e\s+.*(Net::HTTP|open-uri|LWP|HTTP::Tiny)' "$file" 2>/dev/null | while IFS=: read -r lineno content; do
        add_finding "CRITICAL" "$file" "$lineno" "covert-downloader" "$content"
    done
    # PowerShell downloader
    grep -n -iE 'powershell.*downloadstring|iex\s*\(.*webclient|invoke-webrequest.*\|\s*iex' "$file" 2>/dev/null | while IFS=: read -r lineno content; do
        if is_safe_context "$file" "$lineno"; then continue; fi
        add_finding "CRITICAL" "$file" "$lineno" "covert-downloader-powershell" "$content"
    done
}

# Rule 11: Scheduled task injection (WARNING)
check_cron_injection() {
    local file="$1"
    grep -n -E 'crontab\s+(-l|-e|-r|/)|launchctl\s+(load|submit|start|bootstrap)|systemctl\s+(enable|start)\s' "$file" 2>/dev/null | while IFS=: read -r lineno content; do
        if is_doc_context "$file" "$lineno"; then continue; fi
        add_finding "WARNING" "$file" "$lineno" "cron-injection" "$content"
    done
    # LaunchAgent/Daemon creation
    grep -n -E 'LaunchAgents|LaunchDaemons|\.plist' "$file" 2>/dev/null | while IFS=: read -r lineno content; do
        if echo "$content" | grep -qE '(cp|mv|tee|cat\s*>|>>)\s.*(LaunchAgents|LaunchDaemons)'; then
            add_finding "CRITICAL" "$file" "$lineno" "persistence-launchagent" "$content"
        fi
    done
}

# Rule 12: Hidden executables (WARNING)
check_hidden_executables() {
    local dir="$1"
    local perm_flag="+0111"
    if find --version 2>/dev/null | grep -q "GNU"; then
        perm_flag="/111"
    fi
    find "$dir" -name ".*" -type f -perm $perm_flag 2>/dev/null | while read -r file; do
        local bname
        bname=$(basename "$file")
        case "$bname" in
            .gitignore|.gitkeep|.gitattributes|.editorconfig|.eslintrc*|.prettierrc*|.DS_Store|.env*|.npmrc|.yarnrc*) continue ;;
        esac
        add_finding "WARNING" "$file" "0" "hidden-executable" "Hidden executable file: $bname"
    done
}

# Rule 13: Hex/Unicode obfuscation detection
check_encoding_obfuscation() {
    local file="$1"
    # Consecutive hex escapes (\x41\x42...)
    grep -n -E '(\\x[0-9a-fA-F]{2}){6,}' "$file" 2>/dev/null | while IFS=: read -r lineno content; do
        add_finding "WARNING" "$file" "$lineno" "hex-obfuscation" "Hex escape sequence detected"
    done
    # Consecutive Unicode escapes (\u0041\u0042...)
    grep -n -E '(\\u[0-9a-fA-F]{4}){4,}' "$file" 2>/dev/null | while IFS=: read -r lineno content; do
        add_finding "WARNING" "$file" "$lineno" "unicode-obfuscation" "Unicode escape sequence detected"
    done
    # String concatenation bypass: variable concat to build commands
    grep -n -E '[a-z]+=.*["\\x27](cu|ba|we|py|ru|no|pe)["\\x27];\s*[a-z]+\+=' "$file" 2>/dev/null | while IFS=: read -r lineno content; do
        add_finding "CRITICAL" "$file" "$lineno" "string-concat-bypass" "Suspicious string concatenation (may be constructing a command): $content"
    done
}

# Rule 14: Symlink detection
check_symlinks() {
    local dir="$1"
    find "$dir" -type l 2>/dev/null | while read -r link; do
        local target
        target=$(readlink "$link" 2>/dev/null || echo "unknown")

        # Pointing to sensitive system locations
        case "$target" in
            /etc/passwd|/etc/shadow|*/.ssh/*|*/.gnupg/*|*/.aws/*|/private/etc/*)
                add_finding "CRITICAL" "$link" "0" "symlink-sensitive" "Symlink points to sensitive location: $target"
                ;;
            /tmp/*|/var/tmp/*)
                add_finding "WARNING" "$link" "0" "symlink-tmp" "Symlink points to temp directory: $target"
                ;;
            ../*|../../*)
                # Deep directory traversal
                local depth
                depth=$(echo "$target" | grep -o '\.\.\/' | wc -l)
                if [[ $depth -ge 3 ]]; then
                    add_finding "WARNING" "$link" "0" "symlink-traversal" "Symlink has ${depth} levels of directory traversal: $target"
                fi
                ;;
        esac
    done
}

# Rule 15: .env file leak detection (per-line analysis)
check_env_files() {
    local dir="$1"
    find "$dir" -type f -name ".env*" ! -name ".env.example" ! -name ".env.sample" ! -name ".env.template" 2>/dev/null | while read -r envfile; do
        local has_real_secret=false
        while IFS= read -r line; do
            # Skip comments and empty lines
            [[ -z "$line" || "$line" == \#* ]] && continue
            # Check if this line looks like a real secret (KEY=value with 8+ chars, not a placeholder)
            if echo "$line" | grep -qE '^[A-Z_]+=.{8,}'; then
                if ! echo "$line" | grep -qiE '(your_|xxx|placeholder|changeme|TODO|REPLACE|example|sample|<|>)'; then
                    has_real_secret=true
                    break
                fi
            fi
        done < "$envfile"
        if [[ "$has_real_secret" == true ]]; then
            add_finding "CRITICAL" "$envfile" "0" "env-file-leak" ".env file may contain real secrets"
        fi
    done
}

# Rule 16: npm/pip suspicious package name detection
check_suspicious_packages() {
    local file="$1"
    # npm install with suspicious package names (typosquatting)
    grep -n -E 'npm\s+i(nstall)?\s+' "$file" 2>/dev/null | while IFS=: read -r lineno content; do
        if echo "$content" | grep -qiE '(loadsh|loddash|axois|axio|requets|reqeusts|expresss|reacct|colros|chacl|coffe-script|crossenv|event-stream|flatmap-stream|eslint-scope|ua-parser-jss|coa-utils)'; then
            add_finding "CRITICAL" "$file" "$lineno" "typosquat-npm" "Suspicious npm package name (possible typosquatting): $content"
        fi
    done
    # pip install with suspicious packages
    grep -n -E 'pip3?\s+install\s' "$file" 2>/dev/null | while IFS=: read -r lineno content; do
        if echo "$content" | grep -qiE '(python-sqlite|python3-dateutil|python-mongo|py-requests|python-openssl|python-jwt|python-crypto|python-dateutil-2|djang0|djanGo|requestes)'; then
            add_finding "CRITICAL" "$file" "$lineno" "typosquat-pip" "Suspicious pip package name (possible typosquatting): $content"
        fi
    done
    # Non-official npm registry
    grep -n -E 'npm\s.*--registry\s+https?://(?!registry\.npmjs\.org)' "$file" 2>/dev/null | while IFS=: read -r lineno content; do
        add_finding "WARNING" "$file" "$lineno" "custom-registry" "Non-official npm registry: $content"
    done
    # Non-official pip source
    grep -n -E 'pip3?\s+install\s+.*-i\s+https?://(?!pypi\.org|files\.pythonhosted\.org)' "$file" 2>/dev/null | while IFS=: read -r lineno content; do
        add_finding "WARNING" "$file" "$lineno" "custom-pip-source" "Non-official pip source: $content"
    done
}

# Rule 17: Malicious post-install scripts
check_postinstall_scripts() {
    local file="$1"
    local bname
    bname=$(basename "$file")
    # package.json lifecycle scripts with suspicious commands
    if [[ "$bname" == "package.json" ]]; then
        grep -n -E '"(pre|post)install"\s*:\s*".*\b(curl|wget|node\s+-e|python|bash|sh\s+-c)\b' "$file" 2>/dev/null | while IFS=: read -r lineno content; do
            add_finding "CRITICAL" "$file" "$lineno" "malicious-postinstall" "Suspicious lifecycle script in package.json: $content"
        done
    fi
    # setup.py with suspicious runtime code
    if [[ "$bname" == "setup.py" ]]; then
        grep -n -E '(os\.system|subprocess|urllib|urlopen)\s*\(' "$file" 2>/dev/null | while IFS=: read -r lineno content; do
            add_finding "CRITICAL" "$file" "$lineno" "malicious-setup-py" "Suspicious runtime code in setup.py: $content"
        done
    fi
}

# Rule 18: Git hooks detection (CRITICAL)
check_git_hooks() {
    local dir="$1"
    find "$dir" -path "*/.git/hooks/*" -type f ! -name "*.sample" 2>/dev/null | while read -r hook; do
        if [[ -x "$hook" ]] || file -b "$hook" 2>/dev/null | grep -qiE '(script|text|executable)'; then
            local bname
            bname=$(basename "$hook")
            add_finding "CRITICAL" "$hook" "0" "git-hooks" "Active git hook detected: $bname (auto-executes on git operations)"
        fi
    done
}

# Rule 19: Sensitive file leak detection (CRITICAL)
check_sensitive_file_leak() {
    local dir="$1"
    # Private keys
    find "$dir" -type f \( -name "id_rsa" -o -name "id_ed25519" -o -name "id_ecdsa" -o -name "id_dsa" \) ! -path "*/.git/*" 2>/dev/null | while read -r f; do
        add_finding "CRITICAL" "$f" "0" "sensitive-file-leak" "Private key file found: $(basename "$f")"
    done
    # TLS/SSL private keys
    find "$dir" -type f \( -name "*.pem" -o -name "*.key" -o -name "*.p12" -o -name "*.pfx" -o -name "*.keystore" -o -name "*.jks" \) ! -path "*/.git/*" 2>/dev/null | while read -r f; do
        # Check if it actually contains a private key (not just a cert)
        if grep -qlE 'PRIVATE KEY|ENCRYPTED' "$f" 2>/dev/null; then
            add_finding "CRITICAL" "$f" "0" "sensitive-file-leak" "Private key file found: $(basename "$f")"
        fi
    done
    # Credential files
    find "$dir" -type f \( -name "credentials.json" -o -name "service-account*.json" -o -name ".pypirc" \) ! -path "*/.git/*" 2>/dev/null | while read -r f; do
        add_finding "CRITICAL" "$f" "0" "sensitive-file-leak" "Credential file found: $(basename "$f")"
    done
    # .npmrc with auth token
    find "$dir" -type f -name ".npmrc" ! -path "*/.git/*" 2>/dev/null | while read -r f; do
        if grep -qE '_authToken|_auth\s*=' "$f" 2>/dev/null; then
            add_finding "CRITICAL" "$f" "0" "sensitive-file-leak" ".npmrc contains auth token"
        fi
    done
}

# Rule 20: SKILL.md injection detection (CRITICAL)
check_skillmd_injection() {
    local file="$1"
    local bname
    bname=$(basename "$file")
    [[ "$bname" != "SKILL.md" ]] && return 0

    # Prompt injection patterns
    grep -n -iE '(ignore\s+(previous|above|all)\s+(instructions?|prompts?)|disregard\s+(previous|above|all)|you\s+are\s+now\s+|new\s+instructions?\s*:|system\s+prompt\s*:)' "$file" 2>/dev/null | while IFS=: read -r lineno content; do
        add_finding "CRITICAL" "$file" "$lineno" "skillmd-prompt-injection" "Potential prompt injection in SKILL.md: $content"
    done

    # Dangerous tool call patterns (requesting destructive actions)
    grep -n -iE '(rm\s+-rf\s+[/~]|sudo\s+|mkfs\s|dd\s+if=|:\(\)\s*\{\s*:\|:\s*&\s*\};|fork\s*bomb)' "$file" 2>/dev/null | while IFS=: read -r lineno content; do
        if is_doc_context "$file" "$lineno"; then continue; fi
        add_finding "CRITICAL" "$file" "$lineno" "skillmd-dangerous-command" "Dangerous command in SKILL.md: $content"
    done

    # Privilege escalation requests
    grep -n -iE '(run\s+as\s+root|requires?\s+sudo|needs?\s+root\s+access|chmod\s+[47][0-7]{2}\s+/)' "$file" 2>/dev/null | while IFS=: read -r lineno content; do
        add_finding "WARNING" "$file" "$lineno" "skillmd-privilege-escalation" "Privilege escalation in SKILL.md: $content"
    done
}

# Rule 21: Dockerfile security (WARNING / CRITICAL)
check_dockerfile_security() {
    local file="$1"
    local bname
    bname=$(basename "$file")
    # Only check Dockerfile / docker-compose files
    case "$bname" in
        Dockerfile*|docker-compose*) ;;
        *) return 0 ;;
    esac

    # Privileged mode
    grep -n -iE '\-\-privileged' "$file" 2>/dev/null | while IFS=: read -r lineno content; do
        add_finding "CRITICAL" "$file" "$lineno" "dockerfile-privileged" "Container running in privileged mode: $content"
    done

    # Sensitive volume mounts
    grep -n -E '(-v|volumes:)\s*.*\b(/etc|/root|/home|/var/run/docker.sock|/private)\b' "$file" 2>/dev/null | while IFS=: read -r lineno content; do
        add_finding "WARNING" "$file" "$lineno" "dockerfile-sensitive-mount" "Sensitive host directory mounted: $content"
    done

    # Host network mode
    grep -n -iE '(--net=host|--network=host|network_mode:\s*host)' "$file" 2>/dev/null | while IFS=: read -r lineno content; do
        add_finding "WARNING" "$file" "$lineno" "dockerfile-host-network" "Container using host network mode: $content"
    done
}

# Rule 22: Zero-width character detection (CRITICAL)
check_zero_width_chars() {
    local file="$1"
    # Detect zero-width characters using perl (cross-platform, grep -P not available on macOS)
    if command -v perl >/dev/null 2>&1; then
        perl -ne 'if (/[\x{200B}\x{200C}\x{200D}\x{2060}\x{2062}\x{2063}\x{2064}]/) { print "$.:$_"; }' "$file" 2>/dev/null | head -5 | while IFS=: read -r lineno content; do
            add_finding "CRITICAL" "$file" "$lineno" "zero-width-chars" "Zero-width Unicode characters detected (may hide malicious content)"
        done
        # Check for BOM in middle of file
        local fsize
        fsize=$(wc -c < "$file" 2>/dev/null | tr -d ' ')
        if [[ "$fsize" -gt 3 && "$fsize" -lt 1000000 ]]; then
            if tail -c +4 "$file" 2>/dev/null | perl -ne 'exit 0 if /\xEF\xBB\xBF|\xFE\xFF|\xFF\xFE/; END { exit 1 }' 2>/dev/null; then
                add_finding "WARNING" "$file" "0" "embedded-bom" "BOM character found in middle of file (may indicate content splicing)"
            fi
        fi
    fi
}

# Rule 23: Hardcoded secret detection (CRITICAL)
check_hardcoded_secrets() {
    local file="$1"
    local ext="${file##*.}"
    # Skip binary-like extensions and doc files
    case "$ext" in
        md|txt|rst) return 0 ;;
    esac

    # AWS Access Key (always starts with AKIA)
    grep -n -E 'AKIA[0-9A-Z]{16}' "$file" 2>/dev/null | while IFS=: read -r lineno content; do
        add_finding "CRITICAL" "$file" "$lineno" "hardcoded-aws-key" "AWS access key detected: $content"
    done

    # GitHub Token (ghp_, gho_, ghs_, ghr_, github_pat_)
    grep -n -E '(ghp|gho|ghs|ghr)_[A-Za-z0-9_]{36,}|github_pat_[A-Za-z0-9_]{22,}' "$file" 2>/dev/null | while IFS=: read -r lineno content; do
        add_finding "CRITICAL" "$file" "$lineno" "hardcoded-github-token" "GitHub token detected"
    done

    # Stripe secret/restricted key
    grep -n -E '(sk|rk)_live_[A-Za-z0-9]{20,}' "$file" 2>/dev/null | while IFS=: read -r lineno content; do
        add_finding "CRITICAL" "$file" "$lineno" "hardcoded-stripe-key" "Stripe live key detected"
    done

    # Slack bot token / webhook
    grep -n -E 'xox[baprs]-[0-9]{10,}-[A-Za-z0-9]{20,}' "$file" 2>/dev/null | while IFS=: read -r lineno content; do
        add_finding "CRITICAL" "$file" "$lineno" "hardcoded-slack-token" "Slack token detected"
    done
    grep -n -E 'hooks\.slack\.com/services/T[A-Z0-9]+/B[A-Z0-9]+/[A-Za-z0-9]+' "$file" 2>/dev/null | while IFS=: read -r lineno content; do
        add_finding "WARNING" "$file" "$lineno" "hardcoded-slack-webhook" "Slack webhook URL detected"
    done

    # Generic password/secret/api_key assignments in code
    grep -n -E '(password|passwd|secret|api_key|apikey|access_token|auth_token|private_key)\s*[=:]\s*["\x27][A-Za-z0-9+/=_-]{16,}["\x27]' "$file" 2>/dev/null | while IFS=: read -r lineno content; do
        # Exclude common patterns
        case "$content" in
            *placeholder*|*example*|*changeme*|*your_*|*TODO*|*REPLACE*|*xxx*|*sample*) continue ;;
            *test*|*mock*|*fake*|*dummy*) continue ;;
        esac
        if is_doc_context "$file" "$lineno"; then continue; fi
        add_finding "WARNING" "$file" "$lineno" "hardcoded-generic-secret" "Possible hardcoded secret: $content"
    done

    # Private key content in non-key files
    local bname
    bname=$(basename "$file")
    case "$bname" in
        *.pem|*.key|*.p12|*.pfx) ;; # Skip actual key files (covered by rule 19)
        *)
            grep -n -E 'BEGIN (RSA|DSA|EC|OPENSSH) PRIVATE KEY' "$file" 2>/dev/null | while IFS=: read -r lineno content; do
                add_finding "CRITICAL" "$file" "$lineno" "hardcoded-private-key" "Private key embedded in source file"
            done
            ;;
    esac
}

# Rule 24: GitHub Actions workflow injection (WARNING / CRITICAL)
check_github_actions() {
    local file="$1"
    local bname
    bname=$(basename "$file")
    local ext="${file##*.}"
    # Only check YAML files under .github
    [[ "$ext" != "yml" && "$ext" != "yaml" ]] && return 0
    case "$file" in
        */.github/workflows/*|*/.github/actions/*) ;;
        *) return 0 ;;
    esac

    # Unpinned third-party actions (uses tag rather than SHA)
    grep -n -E 'uses:\s+[^/]+/[^@]+@(main|master|latest|v[0-9]+(\.[0-9x]+)*)(\s|$)' "$file" 2>/dev/null | while IFS=: read -r lineno content; do
        # Exclude official actions
        case "$content" in
            *actions/checkout*|*actions/setup-*|*actions/upload-*|*actions/download-*|*actions/cache*|*actions/github-script*) continue ;;
        esac
        add_finding "WARNING" "$file" "$lineno" "actions-unpinned" "Third-party action not pinned to SHA: $content"
    done

    # Script injection via untrusted PR/issue context
    grep -n -E '\$\{\{\s*github\.(event\.(pull_request|issue|comment|discussion)\.(body|title|head\.ref)|head_ref)' "$file" 2>/dev/null | while IFS=: read -r lineno content; do
        add_finding "CRITICAL" "$file" "$lineno" "actions-script-injection" "Untrusted input in workflow expression: $content"
    done

    # Overly permissive token
    grep -n -iE 'permissions:\s*write-all' "$file" 2>/dev/null | while IFS=: read -r lineno content; do
        add_finding "WARNING" "$file" "$lineno" "actions-excessive-permissions" "Overly permissive token: $content"
    done
}

# Rule 25: High entropy string detection (INFO, strict mode only)
check_high_entropy() {
    local file="$1"
    [[ "$STRICT_MODE" != true ]] && return 0
    local ext="${file##*.}"
    # Only check source code files
    case "$ext" in
        sh|py|js|ts|rb|go|rs|java|c|cpp|h|hpp|swift|kt|lua|pl|cfg|ini|conf|toml|yaml|yml|json) ;;
        *) return 0 ;;
    esac

    # Find strings of 20+ alphanumeric chars that look random (using awk for entropy)
    grep -noE '[A-Za-z0-9+/=_-]{20,}' "$file" 2>/dev/null | head -20 | while IFS=: read -r lineno str; do
        # Skip known non-secret patterns
        case "$str" in
            *AKIA*|*ghp_*|*sk_live*|*xox*) continue ;; # Already caught by rule 23
            *abcdef*|*ABCDEF*|*12345*|*00000*) continue ;; # Sequential
        esac
        # Simple entropy check: count unique chars / total chars
        local ucount tcount
        tcount=${#str}
        ucount=$(echo "$str" | fold -w1 | sort -u | wc -l | tr -d ' ')
        # If unique chars > 60% of total and length >= 24, flag as high entropy
        if [[ $tcount -ge 24 && $((ucount * 100 / tcount)) -ge 60 ]]; then
            add_finding "INFO" "$file" "$lineno" "high-entropy-string" "High entropy string (${ucount}/${tcount} unique chars): ${str:0:40}..."
        fi
    done
}

# Rule 26: Obfuscated build scripts (WARNING)
check_build_script_obfuscation() {
    local file="$1"
    local bname
    bname=$(basename "$file")
    case "$bname" in
        Makefile|makefile|GNUmakefile|CMakeLists.txt|configure|configure.ac|meson.build) ;;
        *) return 0 ;;
    esac

    # Downloads during build
    grep -n -E '(curl|wget|fetch)\s+.*https?://' "$file" 2>/dev/null | while IFS=: read -r lineno content; do
        add_finding "WARNING" "$file" "$lineno" "build-script-download" "Build script downloads remote content: $content"
    done

    # Obfuscated code in build files
    grep -n -E '(\\x[0-9a-fA-F]{2}){4,}|eval\s+\$|xargs\s+sh|base64.*-d' "$file" 2>/dev/null | while IFS=: read -r lineno content; do
        add_finding "WARNING" "$file" "$lineno" "build-script-obfuscation" "Obfuscated code in build script: $content"
    done
}

# Rule 27: Enhanced lifecycle hooks (CRITICAL)
check_enhanced_lifecycle() {
    local file="$1"
    local bname
    bname=$(basename "$file")

    # pyproject.toml: suspicious build hooks
    if [[ "$bname" == "pyproject.toml" ]]; then
        grep -n -iE '(exec|system|subprocess|urllib|urlopen|os\.system)\s*\(' "$file" 2>/dev/null | while IFS=: read -r lineno content; do
            add_finding "CRITICAL" "$file" "$lineno" "pyproject-suspicious-hook" "Suspicious code in pyproject.toml: $content"
        done
    fi

    # package.json: obfuscated lifecycle scripts
    if [[ "$bname" == "package.json" ]]; then
        grep -n -E '"(pre|post)(install|publish|test|version)"\s*:\s*".*\\\\x|base64|eval' "$file" 2>/dev/null | while IFS=: read -r lineno content; do
            add_finding "CRITICAL" "$file" "$lineno" "lifecycle-hook-obfuscated" "Obfuscated lifecycle script: $content"
        done
    fi

    # Gemfile: untrusted git source
    if [[ "$bname" == "Gemfile" ]]; then
        grep -n -E "git.*://[^\"']*" "$file" 2>/dev/null | while IFS=: read -r lineno content; do
            if ! echo "$content" | grep -qE '(github\.com|gitlab\.com|bitbucket\.org)'; then
                add_finding "WARNING" "$file" "$lineno" "gemfile-untrusted-source" "Gem from non-standard git source: $content"
            fi
        done
    fi
}

# ============================================================
# Main Scan Logic
# ============================================================

print_banner() {
    if [[ "$JSON_OUTPUT" != true && "$QUIET" != true ]]; then
        echo ""
        echo -e "${BOLD}╔═══════════════════════════════════════════════╗${NC}"
        echo -e "${BOLD}║   🦒 Giraffe Guard v${VERSION} — 长颈鹿卫士       ║${NC}"
        echo -e "${BOLD}╚═══════════════════════════════════════════════╝${NC}"
        echo ""
        echo -e "  ${CYAN}Target:${NC}  $TARGET_DIR"
        if [[ -n "$PYTHON3_PATH" ]]; then
            echo -e "  ${CYAN}AST:${NC}     ${GREEN}enabled${NC} (deep Python analysis)"
        else
            echo -e "  ${CYAN}AST:${NC}     ${DIM}disabled (python3 not found)${NC}"
        fi
        [[ -n "$WHITELIST_FILE" ]] && echo -e "  ${CYAN}Whitelist:${NC} $WHITELIST_FILE (${#WHITELIST_ENTRIES[@]} entries)"
        [[ "$VERBOSE" == true ]] && echo -e "  ${CYAN}Verbose:${NC}  context ${CONTEXT_LINES} lines"
        [[ "$STRICT_MODE" == true ]] && echo -e "  ${CYAN}Strict:${NC}  high entropy detection enabled"
        if [[ ${#SKIP_DIRS[@]} -gt 0 ]]; then
            echo -e "  ${CYAN}Skipping dirs:${NC}  ${SKIP_DIRS[*]}"
        fi
        if [[ ${#SKIP_RULES[@]} -gt 0 ]]; then
            echo -e "  ${CYAN}Skipping rules:${NC} ${SKIP_RULES[*]}"
        fi
        [[ -n "$MIN_SEVERITY" ]] && echo -e "  ${CYAN}Min severity:${NC}  $MIN_SEVERITY"
        [[ -n "$FAIL_ON" ]] && echo -e "  ${CYAN}Fail on:${NC}  $FAIL_ON"
        echo ""
        echo -e "${BOLD}-----------------------------------------------${NC}"
    fi
}

scan_file() {
    local file="$1"
    # Exclude self and companion scripts
    local realfile
    realfile="$(cd "$(dirname "$file")" && pwd)/$(basename "$file")"
    [[ "$realfile" == "$SELF_PATH" ]] && return 0
    local self_dir
    self_dir="$(dirname "$SELF_PATH")"
    [[ "$realfile" == "$self_dir/ast_analyzer.py" ]] && return 0

    echo $(( $(cat "$TMPDIR_AUDIT/files") + 1 )) > "$TMPDIR_AUDIT/files"

    # Progress indicator (every 50 files)
    if [[ "$JSON_OUTPUT" != true && "$QUIET" != true ]]; then
        local fsc
        fsc=$(cat "$TMPDIR_AUDIT/files")
        if [[ $((fsc % 50)) -eq 0 ]]; then
            echo -e "  ${DIM}Scanned ${fsc} files...${NC}"
        fi
    fi

    check_pipe_execution "$file"
    check_base64_obfuscation "$file"
    check_security_bypass "$file"
    check_dangerous_permissions "$file"
    check_suspicious_network "$file"
    check_covert_execution "$file"
    check_file_disguise "$file"
    check_sensitive_data_access "$file"
    check_anti_sandbox "$file"
    check_covert_downloader "$file"
    check_cron_injection "$file"
    check_encoding_obfuscation "$file"
    check_suspicious_packages "$file"
    check_postinstall_scripts "$file"
    check_skillmd_injection "$file"
    check_dockerfile_security "$file"
    check_zero_width_chars "$file"
    check_hardcoded_secrets "$file"
    check_github_actions "$file"
    check_high_entropy "$file"
    check_build_script_obfuscation "$file"
    check_enhanced_lifecycle "$file"

    # AST deep analysis for Python files (if python3 available)
    local ext="${file##*.}"
    if [[ "$ext" == "py" && -n "$PYTHON3_PATH" ]]; then
        local ast_script
        ast_script="$(cd "$(dirname "$0")" && pwd)/ast_analyzer.py"
        if [[ -f "$ast_script" ]]; then
            local ast_output
            ast_output=$("$PYTHON3_PATH" "$ast_script" --json "$file" 2>/dev/null)
            if [[ -n "$ast_output" ]]; then
                while IFS= read -r ast_line; do
                    [[ -z "$ast_line" ]] && continue
                    local a_level a_file a_lineno a_rule a_content a_fix
                    a_level=$(echo "$ast_line" | sed 's/.*"level": *"\([^"]*\)".*/\1/')
                    a_lineno=$(echo "$ast_line" | sed 's/.*"line": *\([0-9]*\).*/\1/')
                    a_rule=$(echo "$ast_line" | sed 's/.*"rule": *"\([^"]*\)".*/\1/')
                    a_content=$(echo "$ast_line" | sed 's/.*"content": *"\([^"]*\)".*/\1/')
                    a_fix=$(echo "$ast_line" | sed 's/.*"remediation": *"\([^"]*\)".*/\1/')
                    add_finding "$a_level" "$file" "$a_lineno" "$a_rule" "$a_content"
                done <<< "$ast_output"
            fi
        fi
    fi
}

main() {
    load_whitelist
    touch "$TMPDIR_AUDIT/file_hits"
    print_banner

    # Build find arguments including --skip-dir exclusions (safe array, no eval)
    local -a find_args=("$TARGET_DIR"
        -type f
        '!' -path '*/.git/*'
        '!' -path '*/__pycache__/*'
        '!' -path '*/test/*' '!' -path '*/tests/*' '!' -path '*/__tests__/*'
        '!' -path '*/spec/*' '!' -path '*/fixtures/*' '!' -path '*/testdata/*'
        '!' -name '*.png' '!' -name '*.jpg' '!' -name '*.jpeg' '!' -name '*.gif'
        '!' -name '*.ico' '!' -name '*.woff' '!' -name '*.woff2' '!' -name '*.ttf'
        '!' -name '*.zip' '!' -name '*.tar' '!' -name '*.gz' '!' -name '*.bz2'
        '!' -name '*.pyc' '!' -name '*.o' '!' -name '*.so' '!' -name '*.dylib'
        '!' -name '*.mp3' '!' -name '*.mp4' '!' -name '*.wav' '!' -name '*.ogg'
    )
    for sd in "${SKIP_DIRS[@]+"${SKIP_DIRS[@]}"}"; do
        find_args+=('!' -path "*/${sd}/*")
    done

    # Collect all scannable files
    local file_list
    file_list=$(find "${find_args[@]}" 2>/dev/null)

    if [[ -z "$file_list" ]]; then
        if [[ "$JSON_OUTPUT" == true ]]; then
            echo '{"version":"'"${VERSION}"'","timestamp":"'"$(date -u +%Y-%m-%dT%H:%M:%SZ)"'","filesScanned":0,"totalFindings":0,"critical":0,"warning":0,"info":0,"findings":[]}'
        else
            echo "  No scannable files found"
        fi
        exit 0
    fi

    # Scan text files
    while IFS= read -r file; do
        local ext="${file##*.}"
        case "$ext" in
            md|txt|json|yaml|yml|sh|bash|zsh|py|rb|js|ts|pl|cfg|ini|conf|toml|xml|html|css|csv|env|makefile|dockerfile|rst|go|rs|c|h|cpp|hpp|java|swift|kt|r|lua|sql|Makefile|Dockerfile)
                scan_file "$file"
                ;;
            *)
                # No extension or uncommon extension - use file command
                local ftype
                ftype=$(file -b --mime-type "$file" 2>/dev/null)
                case "$ftype" in
                    text/*|application/json|application/xml|application/javascript|application/x-shellscript|inode/x-empty)
                        scan_file "$file"
                        ;;
                esac
                ;;
        esac
    done <<< "$file_list"

    # Directory-level detection
    check_hidden_executables "$TARGET_DIR"
    check_symlinks "$TARGET_DIR"
    check_env_files "$TARGET_DIR"
    check_git_hooks "$TARGET_DIR"
    check_sensitive_file_leak "$TARGET_DIR"

    # --- Read final counters ---
    local fc cc wc ic wlc fsc
    fc=$(cat "$TMPDIR_AUDIT/findings")
    cc=$(cat "$TMPDIR_AUDIT/critical")
    wc=$(cat "$TMPDIR_AUDIT/warning")
    ic=$(cat "$TMPDIR_AUDIT/info")
    wlc=$(cat "$TMPDIR_AUDIT/whitelisted")
    fsc=$(cat "$TMPDIR_AUDIT/files")

    # --- SARIF output ---
    if [[ "$SARIF_OUTPUT" == true ]]; then
        echo '{'
        echo '  "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/main/sarif-2.1/schema/sarif-schema-2.1.0.json",'
        echo '  "version": "2.1.0",'
        echo '  "runs": [{'
        echo '    "tool": {"driver": {"name": "Giraffe Guard", "version": "'"${VERSION}"'", "informationUri": "https://github.com/lida408/openclaw-skill-security-pro"}},'
        echo '    "results": ['
        if [[ -s "$FINDINGS_FILE" ]]; then
            local first=true idx=0
            while IFS= read -r jline; do
                local sep=""
                [[ "$first" != true ]] && sep=","
                first=false
                # Parse fields from JSON line
                local s_level s_file s_line s_rule s_msg
                s_level=$(echo "$jline" | sed 's/.*"level":"\([^"]*\)".*/\1/')
                s_file=$(echo "$jline" | sed 's/.*"file":"\([^"]*\)".*/\1/')
                s_line=$(echo "$jline" | sed 's/.*"line":\([0-9]*\).*/\1/')
                s_rule=$(echo "$jline" | sed 's/.*"rule":"\([^"]*\)".*/\1/')
                s_msg=$(echo "$jline" | sed 's/.*"content":"\([^"]*\)".*/\1/')
                local sarif_level="warning"
                [[ "$s_level" == "CRITICAL" ]] && sarif_level="error"
                [[ "$s_level" == "INFO" ]] && sarif_level="note"
                echo "${sep}      {\"ruleId\":\"${s_rule}\",\"level\":\"${sarif_level}\",\"message\":{\"text\":\"${s_msg}\"},\"locations\":[{\"physicalLocation\":{\"artifactLocation\":{\"uri\":\"${s_file}\"},\"region\":{\"startLine\":${s_line}}}}]}"
            done < "$FINDINGS_FILE"
        fi
        echo '    ]'
        echo '  }]'
        echo '}'
    elif [[ "$JSON_OUTPUT" == true ]]; then
        echo "{"
        echo "  \"version\": \"${VERSION}\","
        echo "  \"timestamp\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\","
        echo "  \"target\": \"$(json_escape "$TARGET_DIR")\","
        echo "  \"filesScanned\": ${fsc},"
        echo "  \"totalFindings\": ${fc},"
        echo "  \"critical\": ${cc},"
        echo "  \"warning\": ${wc},"
        echo "  \"info\": ${ic},"
        echo "  \"whitelisted\": ${wlc},"
        echo "  \"findings\": ["
        if [[ -s "$FINDINGS_FILE" ]]; then
            local first=true
            while IFS= read -r line; do
                if [[ "$first" == true ]]; then
                    echo "    $line"
                    first=false
                else
                    echo "    ,$line"
                fi
            done < "$FINDINGS_FILE"
        fi
        echo "  ]"
        echo "}"
    else
        echo ""
        echo -e "${BOLD}===============================================${NC}"
        echo -e "${BOLD}  Scan Report${NC}"
        echo -e "${BOLD}===============================================${NC}"
        echo -e "  Files scanned: ${BOLD}${fsc}${NC}"
        echo -e "  Total findings: ${BOLD}${fc}${NC}"
        if [[ $cc -gt 0 ]]; then
            echo -e "  ${RED}Critical:  ${BOLD}${cc}${NC}"
        else
            echo -e "  Critical:  ${GREEN}0${NC}"
        fi
        if [[ $wc -gt 0 ]]; then
            echo -e "  ${YELLOW}Warning:   ${BOLD}${wc}${NC}"
        else
            echo -e "  Warning:   ${GREEN}0${NC}"
        fi
        if [[ $ic -gt 0 ]]; then
            echo -e "  ${CYAN}Info:      ${ic}${NC}"
        fi
        if [[ $wlc -gt 0 ]]; then
            echo -e "  ${DIM}Whitelisted: ${wlc}${NC}"
        fi
        echo ""

        # Top offenders (C5)
        if [[ $fc -gt 0 && -s "$TMPDIR_AUDIT/file_hits" ]]; then
            echo -e "${BOLD}  Top files by findings:${NC}"
            sort "$TMPDIR_AUDIT/file_hits" | uniq -c | sort -rn | head -5 | while read -r count filepath; do
                echo -e "    ${YELLOW}${count}${NC} findings: ${filepath}"
            done
            echo ""
        fi

        if [[ $fc -eq 0 ]]; then
            echo -e "  ${GREEN}${BOLD}PASS - No security issues found.${NC}"
        elif [[ $cc -gt 0 ]]; then
            echo -e "  ${RED}${BOLD}FAIL - Critical security issues detected! Immediate review required.${NC}"
        elif [[ $wc -gt 0 ]]; then
            echo -e "  ${YELLOW}${BOLD}WARN - Potential risks found. Manual review recommended.${NC}"
        else
            echo -e "  ${CYAN}INFO - Only informational findings.${NC}"
        fi

        # Pre-install verdict
        if [[ "$PRE_INSTALL" == true ]]; then
            echo ""
            echo -e "${BOLD}-----------------------------------------------${NC}"
            echo -e "${BOLD}  Pre-Install Verdict${NC}"
            echo -e "${BOLD}-----------------------------------------------${NC}"
            if [[ $cc -gt 0 ]]; then
                echo -e "  ${RED}${BOLD}DO NOT INSTALL${NC}"
                echo -e "  ${RED}Critical security issues found. This skill may contain malicious code.${NC}"
                echo -e "  ${RED}Running npm/pip install is NOT safe.${NC}"
            elif [[ $wc -gt 0 ]]; then
                echo -e "  ${YELLOW}${BOLD}INSTALL WITH CAUTION${NC}"
                echo -e "  ${YELLOW}Warnings found. Review the findings above before installing.${NC}"
                echo -e "  ${YELLOW}If you trust the source, you may proceed with: npm install / pip install${NC}"
            else
                echo -e "  ${GREEN}${BOLD}SAFE TO INSTALL${NC}"
                echo -e "  ${GREEN}No security issues found. You may safely run: npm install / pip install${NC}"
            fi
        fi
        echo ""
    fi

    # Exit codes (respect --fail-on)
    if [[ -n "$FAIL_ON" ]]; then
        local fail_rank
        fail_rank=$(severity_rank "$FAIL_ON")
        if [[ $cc -gt 0 && $(severity_rank "CRITICAL") -ge $fail_rank ]]; then
            exit 2
        elif [[ $wc -gt 0 && $(severity_rank "WARNING") -ge $fail_rank ]]; then
            exit 1
        else
            exit 0
        fi
    else
        if [[ $cc -gt 0 ]]; then
            exit 2
        elif [[ $wc -gt 0 ]]; then
            exit 1
        else
            exit 0
        fi
    fi
}

main

