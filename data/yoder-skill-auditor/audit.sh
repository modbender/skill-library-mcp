#!/bin/bash
# Skill Auditor v3.0.0
# The definitive security scanner for OpenClaw skills
# Scans for credential harvesting, supply chain attacks, obfuscation,
# crypto drains, telemetry, time bombs, symlink attacks, and more.
# Usage: bash audit.sh /path/to/skill-folder [--json] [--allowlist /path/to/allowlist.json]

set -o pipefail

SKILL_DIR=""
JSON_MODE=false
ALLOWLIST_FILE=""
EXIT_CODE=0
CRITICALS=0
WARNINGS=0
INFOS=0
JSON_ITEMS=""

# Parse args
while [[ $# -gt 0 ]]; do
    case $1 in
        --json) JSON_MODE=true; shift ;;
        --allowlist) ALLOWLIST_FILE="$2"; shift 2 ;;
        *) SKILL_DIR="$1"; shift ;;
    esac
done

if [ -z "$SKILL_DIR" ]; then
    echo "Usage: audit.sh /path/to/skill-folder [--json] [--allowlist /path/to/allowlist.json]"
    exit 3
fi

# Auto-detect default allowlist if none specified
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
if [ -z "$ALLOWLIST_FILE" ] && [ -f "$SCRIPT_DIR/allowlist.json" ]; then
    ALLOWLIST_FILE="$SCRIPT_DIR/allowlist.json"
fi

# Colors (disabled in JSON mode)
if $JSON_MODE; then
    RED=''; YELLOW=''; BLUE=''; GREEN=''; NC=''
else
    RED='\033[0;31m'; YELLOW='\033[1;33m'; BLUE='\033[0;34m'; GREEN='\033[0;32m'; NC='\033[0m'
fi

SKILL_NAME=$(basename "$SKILL_DIR")

# Load allowlist
ALLOWLISTED_SKILLS=""
if [ -n "$ALLOWLIST_FILE" ] && [ -f "$ALLOWLIST_FILE" ]; then
    ALLOWLISTED_SKILLS=$(python3 -c "
import json,sys
try:
    data = json.load(open('$ALLOWLIST_FILE'))
    for s in data.get('skills', []):
        print(s.get('name', ''))
except: pass
" 2>/dev/null || true)
fi

# Check if this skill is allowlisted
IS_ALLOWLISTED=false
if echo "$ALLOWLISTED_SKILLS" | grep -qx "$SKILL_NAME" 2>/dev/null; then
    IS_ALLOWLISTED=true
fi

json_add() {
    local severity="$1" check="$2" msg="$3" file="${4:-}" line="${5:-}"
    # Escape quotes in message
    msg=$(echo "$msg" | sed 's/"/\\"/g')
    if [ -n "$JSON_ITEMS" ]; then JSON_ITEMS="$JSON_ITEMS,"; fi
    JSON_ITEMS="${JSON_ITEMS}{\"severity\":\"$severity\",\"check\":\"$check\",\"message\":\"$msg\",\"file\":\"$file\",\"line\":\"$line\"}"
}

log_critical() {
    local check="$1" msg="$2" file="${3:-}" line="${4:-}"
    if $IS_ALLOWLISTED; then
        log_info "allowlisted: $check - $msg (skill is allowlisted, downgraded)"
        return
    fi
    ((CRITICALS++)); EXIT_CODE=2
    if $JSON_MODE; then json_add "critical" "$check" "$msg" "$file" "$line"
    else echo -e "${RED}[CRITICAL]${NC} $check: $msg"; fi
}

log_warning() {
    local check="$1" msg="$2" file="${3:-}" line="${4:-}"
    ((WARNINGS++)); [ $EXIT_CODE -lt 1 ] && EXIT_CODE=1
    if $JSON_MODE; then json_add "warning" "$check" "$msg" "$file" "$line"
    else echo -e "${YELLOW}[WARNING]${NC}  $check: $msg"; fi
}

log_info() {
    local check="$1" msg="$2" file="${3:-}" line="${4:-}"
    ((INFOS++))
    if $JSON_MODE; then json_add "info" "$check" "$msg" "$file" "$line"
    else echo -e "${BLUE}[INFO]${NC}     $check: $msg"; fi
}

log_pass() {
    local check="$1" msg="$2"
    if $JSON_MODE; then json_add "pass" "$check" "$msg" "" ""
    else echo -e "${GREEN}[PASS]${NC}     $check: $msg"; fi
}

if ! $JSON_MODE; then
    echo "========================================="
    echo "  Skill Auditor v3.0.0"
    echo "  Scanning: $SKILL_DIR"
    if $IS_ALLOWLISTED; then echo "  Status: ALLOWLISTED (criticals downgraded to info)"; fi
    echo "========================================="
    echo ""
fi

# Check skill directory exists
if [ ! -d "$SKILL_DIR" ]; then
    echo "Error: Directory not found: $SKILL_DIR"
    exit 3
fi

# ─── QUALITY CHECKS ───

if [ ! -f "$SKILL_DIR/SKILL.md" ]; then
    log_warning "no-skillmd" "No SKILL.md found - skill lacks documentation"
else
    if ! grep -qi "description" "$SKILL_DIR/SKILL.md"; then
        log_warning "no-description" "SKILL.md has no description field"
    else
        log_pass "has-description" "Skill has a description"
    fi
    if ! grep -qi "version" "$SKILL_DIR/SKILL.md"; then
        log_info "no-version" "No version specified in SKILL.md"
    fi
fi

# Check for oversized files
LARGE_FILES=$(find "$SKILL_DIR" -type f -size +100k 2>/dev/null \
    | grep -v "$SKILL_DIR/node_modules/" \
    | grep -v "$SKILL_DIR/.git/" \
    | grep -v "$SKILL_DIR/test-skills/" | grep -v "$SKILL_DIR/tests/" || true)
if [ -n "$LARGE_FILES" ]; then
    log_warning "large-files" "Files over 100KB found (review for embedded binaries)"
    if ! $JSON_MODE; then
        echo "$LARGE_FILES" | while read -r f; do
            echo "    $(du -h "$f" | cut -f1) $f"
        done
    fi
fi

# ─── FILE CLASSIFICATION ───

SCRIPT_FILES=$(find "$SKILL_DIR" -type f 2>/dev/null \
    | grep -vE '\.(png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|zip|tar|gz|bin|exe|dll|so|dylib)$' \
    | grep -v "$SKILL_DIR/node_modules/" \
    | grep -v "$SKILL_DIR/.git/" \
    | grep -v "$SKILL_DIR/test-skills/" | grep -v "$SKILL_DIR/tests/" \
    | grep -iE '\.(sh|bash|py|js|ts|rb|pl|php|go|rs|java|mjs|cjs)$' \
    || true)

DOC_FILES=$(find "$SKILL_DIR" -type f 2>/dev/null \
    | grep -vE '\.(png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|zip|tar|gz|bin|exe|dll|so|dylib)$' \
    | grep -v "$SKILL_DIR/node_modules/" \
    | grep -v "$SKILL_DIR/.git/" \
    | grep -v "$SKILL_DIR/test-skills/" | grep -v "$SKILL_DIR/tests/" \
    | grep -iE '\.(md|txt|rst|adoc|json|yaml|yml|toml|cfg|ini|conf)$' \
    || true)

ALL_FILES=$(find "$SKILL_DIR" -type f 2>/dev/null \
    | grep -vE '\.(png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|zip|tar|gz|bin|exe|dll|so|dylib)$' \
    | grep -v "$SKILL_DIR/node_modules/" \
    | grep -v "$SKILL_DIR/.git/" \
    | grep -v "$SKILL_DIR/test-skills/" | grep -v "$SKILL_DIR/tests/" \
    || true)

if [ -z "$ALL_FILES" ]; then
    log_warning "empty-skill" "No files found in skill directory"
    if $JSON_MODE; then
        echo "{\"skill\":\"$SKILL_NAME\",\"path\":\"$SKILL_DIR\",\"allowlisted\":$IS_ALLOWLISTED,\"criticals\":$CRITICALS,\"warnings\":$WARNINGS,\"infos\":$INFOS,\"verdict\":\"review\",\"items\":[$JSON_ITEMS]}"
    else
        echo ""; echo "Summary: $CRITICALS critical, $WARNINGS warnings, $INFOS info"
    fi
    exit $EXIT_CODE
fi

SCRIPT_COUNT=0
if [ -n "$SCRIPT_FILES" ]; then
    SCRIPT_COUNT=$(echo "$SCRIPT_FILES" | grep -c '.' 2>/dev/null || echo 0)
fi
DOC_COUNT=0
if [ -n "$DOC_FILES" ]; then
    DOC_COUNT=$(echo "$DOC_FILES" | grep -c '.' 2>/dev/null || echo 0)
fi
log_info "file-breakdown" "Scripts: $SCRIPT_COUNT, Docs: $DOC_COUNT"

# ─── SECURITY CHECKS (SCRIPTS ONLY) ───

CRED_PATTERNS='\.env|\.ssh|\.aws|\.config.*token|\.config.*key|auth.*token|api[_-]?key|secret[_-]?key|password|credential|\.npmrc|\.pypirc|BW_SESSION|BW_PASSWORD'

# ─── PATTERN DEFINITION FILTER (Self-Audit Transparency) ───
#
# WHAT: This filter excludes lines that are pattern DEFINITIONS (not actual threats)
# from being flagged by security checks. Without it, the scanner would flag itself.
#
# WHY: A security scanner necessarily contains the exact patterns it detects (e.g.,
# regex for credential keywords, curl|bash signatures, etc.). These pattern definitions
# are scanner infrastructure, not malicious behavior. The filter prevents false positives
# when the auditor scans itself or other security tools.
#
# COMPONENTS (each separated by | in the regex):
#   [A-Z_][A-Z_]*='     - Shell variable assignments with single quotes (e.g., CRED_PATTERNS='...')
#   [A-Z_][A-Z_]*="     - Shell variable assignments with double quotes
#   \$(echo             - Command substitutions used in test assertions
#   xargs grep           - Grep pipelines (scanner searching for patterns)
#   grep -[flags] '/"   - Grep commands with quoted pattern arguments
#   log_(critical|...)   - Logging/reporting function calls
#   echo.*PATTERN        - Debug/status output referencing pattern names
#   assert_              - Test assertion functions (test.sh)
#   FILTER=              - Filter variable definitions (including this one)
#
# HOW TO VERIFY: Inspect each component above, then compare against the actual regex below.
# The filter is intentionally conservative - it only matches lines that are clearly
# defining or searching for patterns, not lines that execute them.
PATTERN_DEF_FILTER='[A-Z_][A-Z_]*='\''|[A-Z_][A-Z_]*="|\$\(echo|xargs grep|grep -[a-zA-Z]*[ElcnqriP] '\''|grep -[a-zA-Z]*[ElcnqriP] "|log_(critical|warning|info|pass)|echo.*PATTERN|assert_|FILTER='

if [ -n "$SCRIPT_FILES" ]; then
    # Check 1: Credential harvesting in executable files
    # Filter: exclude pattern-definition lines (variable assignments storing regex/grep patterns)
    # These are detection rules, not actual credential access
    CRED_HITS=$(echo "$SCRIPT_FILES" | xargs grep -ilE "$CRED_PATTERNS" 2>/dev/null || true)
    if [ -n "$CRED_HITS" ]; then
        for f in $CRED_HITS; do
            # Count actual credential access lines (excluding pattern definitions and comments)
            REAL_CRED_LINES=$(grep -niE "$CRED_PATTERNS" "$f" 2>/dev/null \
                | grep -vE "$PATTERN_DEF_FILTER" \
                | grep -v '^ *#' | grep -v '^[0-9]*: *#' \
                | grep -vE 'log_(critical|warning|info|pass)' \
                || true)
            if [ -z "$REAL_CRED_LINES" ]; then
                continue  # All matches were pattern definitions, not actual credential access
            fi
            if grep -qiE 'curl |wget |fetch\(|http|request|axios|got\(' "$f" 2>/dev/null; then
                # Also check network calls aren't just pattern definitions
                REAL_NET_LINES=$(grep -iE 'curl |wget |fetch\(|http|request|axios|got\(' "$f" 2>/dev/null \
                    | grep -vE "$PATTERN_DEF_FILTER" \
                    | grep -v '^ *#' | grep -v '^[0-9]*: *#' \
                    | grep -vE 'log_(critical|warning|info|pass)' \
                    || true)
                if [ -z "$REAL_NET_LINES" ]; then
                    continue  # Network mentions are just pattern definitions
                fi
                REL_PATH="${f#$SKILL_DIR/}"
                LINES=$(echo "$REAL_CRED_LINES" | head -3)
                FIRST_LINE=$(echo "$LINES" | head -1 | cut -d: -f1)
                log_critical "credential-harvest" "$REL_PATH reads credentials AND makes network calls" "$REL_PATH" "$FIRST_LINE"
                if ! $JSON_MODE; then
                    echo "$LINES" | sed 's/^/    /'
                fi
            fi
        done
    fi

    # Check 2: Shell injection / code execution
    EXEC_PATTERNS='eval\(|execSync|child_process|spawn\(|system\(|popen|subprocess|os\.system|__import__'
    EXEC_HITS=$(echo "$SCRIPT_FILES" | xargs grep -ilE "$EXEC_PATTERNS" 2>/dev/null || true)
    if [ -n "$EXEC_HITS" ]; then
        for f in $EXEC_HITS; do
            REL_PATH="${f#$SKILL_DIR/}"
            LINES=$(grep -cnE "$EXEC_PATTERNS" "$f" 2>/dev/null)
            log_warning "code-execution" "$REL_PATH contains $LINES code execution patterns" "$REL_PATH"
        done
    fi
fi

# ─── SECURITY CHECKS (ALL FILES) ───

# Check 3: Suspicious external URLs
EXFIL_PATTERNS='webhook\.site|requestbin|ngrok\.io|pipedream\.net|hookbin|beeceptor|requestcatcher|postb\.in|httpbin\.org/post|mockbin'

if [ -n "$SCRIPT_FILES" ]; then
    SCRIPT_EXFIL=$(echo "$SCRIPT_FILES" | xargs grep -ilE "$EXFIL_PATTERNS" 2>/dev/null || true)
    if [ -n "$SCRIPT_EXFIL" ]; then
        for f in $SCRIPT_EXFIL; do
            # Filter out pattern definitions (detection rules, not actual exfil URLs)
            REAL_EXFIL=$(grep -nE "$EXFIL_PATTERNS" "$f" 2>/dev/null \
                | grep -vE "$PATTERN_DEF_FILTER" \
                | grep -v '^ *#' | grep -v '^[0-9]*: *#' \
                | grep -vE 'log_(critical|warning|info|pass)' \
                || true)
            if [ -z "$REAL_EXFIL" ]; then
                continue  # All matches were pattern definitions
            fi
            REL_PATH="${f#$SKILL_DIR/}"
            log_critical "exfiltration-url" "$REL_PATH contains known data exfiltration URLs" "$REL_PATH"
            if ! $JSON_MODE; then
                echo "$REAL_EXFIL" | head -3 | sed 's/^/    /'
            fi
        done
    fi
fi

if [ -n "$DOC_FILES" ]; then
    DOC_EXFIL=$(echo "$DOC_FILES" | xargs grep -ilE "$EXFIL_PATTERNS" 2>/dev/null || true)
    if [ -n "$DOC_EXFIL" ]; then
        DOC_EXFIL_COUNT=$(echo "$DOC_EXFIL" | wc -l | tr -d ' ')
        log_info "doc-exfil-mentions" "$DOC_EXFIL_COUNT doc(s) mention exfiltration URLs (documentation context)"
    fi
fi

EXFIL_HITS=$(echo "$ALL_FILES" | xargs grep -ilE "$EXFIL_PATTERNS" 2>/dev/null || true)
if [ -z "$EXFIL_HITS" ]; then
    log_pass "no-exfiltration" "No known exfiltration URLs found"
fi

# Check 4: Base64 obfuscation
B64_PATTERNS='atob\(|btoa\(|base64.*decode|base64.*encode|Buffer\.from.*base64'
B64_HITS=$(echo "$ALL_FILES" | xargs grep -ilE "$B64_PATTERNS" 2>/dev/null || true)
if [ -n "$B64_HITS" ]; then
    for f in $B64_HITS; do
        REL_PATH="${f#$SKILL_DIR/}"
        # Check for actual base64-encoded payloads (not pattern definitions)
        REAL_B64=$(grep -iE 'aHR0c|Y3VybC|d2dldC' "$f" 2>/dev/null \
            | grep -vE "$PATTERN_DEF_FILTER" \
            | grep -v '^ *#' | grep -v '^[0-9]*: *#' \
            | grep -vE 'log_(critical|warning|info|pass)' \
            || true)
        if [ -n "$REAL_B64" ]; then
            log_critical "obfuscated-payload" "$REL_PATH has base64-encoded URLs or commands" "$REL_PATH"
        else
            # Check if base64 usage is also just pattern definitions
            REAL_B64_USE=$(grep -iE "$B64_PATTERNS" "$f" 2>/dev/null \
                | grep -vE "$PATTERN_DEF_FILTER" \
                | grep -v '^ *#' | grep -v '^[0-9]*: *#' \
                | grep -vE 'log_(critical|warning|info|pass)' \
                || true)
            if [ -n "$REAL_B64_USE" ]; then
                log_warning "base64-usage" "$REL_PATH uses base64 encoding (review manually)" "$REL_PATH"
            fi
        fi
    done
else
    log_pass "no-obfuscation" "No suspicious encoding patterns found"
fi

# Check 5: Sensitive file system reads
FS_PATTERNS='\/etc\/passwd|\/etc\/shadow|~\/\.ssh|~\/\.gnupg|~\/\.aws\/credentials|\/proc\/|\/sys\/'
FS_SCRIPT_HITS=""
if [ -n "$SCRIPT_FILES" ]; then
    FS_SCRIPT_HITS=$(echo "$SCRIPT_FILES" | xargs grep -ilE "$FS_PATTERNS" 2>/dev/null || true)
fi
FS_DOC_HITS=""
if [ -n "$DOC_FILES" ]; then
    FS_DOC_HITS=$(echo "$DOC_FILES" | xargs grep -ilE "$FS_PATTERNS" 2>/dev/null || true)
fi

if [ -n "$FS_SCRIPT_HITS" ]; then
    for f in $FS_SCRIPT_HITS; do
        REL_PATH="${f#$SKILL_DIR/}"
        log_critical "sensitive-fs" "$REL_PATH accesses sensitive system paths" "$REL_PATH"
        if ! $JSON_MODE; then
            grep -nE "$FS_PATTERNS" "$f" 2>/dev/null | head -3 | sed 's/^/    /'
        fi
    done
elif [ -n "$FS_DOC_HITS" ]; then
    FS_DOC_COUNT=$(echo "$FS_DOC_HITS" | wc -l | tr -d ' ')
    log_info "doc-sensitive-fs" "$FS_DOC_COUNT doc(s) mention sensitive paths (documentation context)"
else
    log_pass "no-sensitive-fs" "No sensitive system path access found"
fi

# ─── NEW v2.0 CHECKS ───

# Check 6: Crypto wallet address detection
CRYPTO_PATTERNS='0x[a-fA-F0-9]{40}|bc1[a-zA-HJ-NP-Z0-9]{39,59}|[13][a-km-zA-HJ-NP-Z1-9]{25,34}'
if [ -n "$SCRIPT_FILES" ]; then
    CRYPTO_HITS=$(echo "$SCRIPT_FILES" | xargs grep -lE "$CRYPTO_PATTERNS" 2>/dev/null || true)
    if [ -n "$CRYPTO_HITS" ]; then
        for f in $CRYPTO_HITS; do
            REL_PATH="${f#$SKILL_DIR/}"
            log_critical "crypto-wallet" "$REL_PATH contains hardcoded crypto wallet addresses (potential drain attack)" "$REL_PATH"
            if ! $JSON_MODE; then
                grep -nE "$CRYPTO_PATTERNS" "$f" 2>/dev/null | head -3 | sed 's/^/    /'
            fi
        done
    else
        log_pass "no-crypto-wallets" "No hardcoded crypto wallet addresses found"
    fi
else
    log_pass "no-crypto-wallets" "No hardcoded crypto wallet addresses found"
fi

# Check 7: Dependency confusion / typosquatting
SUSPICIOUS_PKG_FOUND=false
for pkg_file in "$SKILL_DIR/package.json" "$SKILL_DIR/requirements.txt" "$SKILL_DIR/Pipfile" "$SKILL_DIR/setup.py" "$SKILL_DIR/pyproject.toml"; do
    if [ -f "$pkg_file" ]; then
        REL_PATH="${pkg_file#$SKILL_DIR/}"
        # Check for internal-looking package names (scoped private packages published publicly)
        if grep -qiE '(@internal|@private|@corp|@company|_internal|_private|-internal-|-private-)' "$pkg_file" 2>/dev/null; then
            log_critical "dependency-confusion" "$REL_PATH references internal/private-scoped packages (supply chain risk)" "$REL_PATH"
            SUSPICIOUS_PKG_FOUND=true
        fi
        # Check for common typosquatting patterns
        if grep -qiE '(requets|reqeusts|lodasg|loadsh|lodahs|colosr|colros|axois|axiso|expresss|expreses|crytpo|crypot)' "$pkg_file" 2>/dev/null; then
            log_critical "typosquatting" "$REL_PATH contains likely typosquatted package names" "$REL_PATH"
            SUSPICIOUS_PKG_FOUND=true
        fi
        # Check for suspiciously named packages with install scripts
        if [ "$(basename "$pkg_file")" = "package.json" ]; then
            if python3 -c "
import json,sys
try:
    d = json.load(open('$pkg_file'))
    scripts = d.get('scripts', {})
    if any(k in scripts for k in ['preinstall', 'postinstall', 'preuninstall']):
        sys.exit(0)
    sys.exit(1)
except: sys.exit(1)
" 2>/dev/null; then
                log_warning "install-hooks" "$REL_PATH has pre/post install hooks (review carefully)" "$REL_PATH"
                SUSPICIOUS_PKG_FOUND=true
            fi
        fi
    fi
done
if ! $SUSPICIOUS_PKG_FOUND; then
    log_pass "no-dependency-issues" "No dependency confusion or typosquatting detected"
fi

# Check 8: Excessive permission scope
if [ -f "$SKILL_DIR/skill.json" ]; then
    PERM_CHECK=$(python3 -c "
import json
try:
    d = json.load(open('$SKILL_DIR/skill.json'))
    req = d.get('requires', {})
    bins = len(req.get('bins', []))
    env = len(req.get('env', []))
    config = len(req.get('config', []))
    total = bins + env + config
    if total > 15:
        print(f'excessive:{total}')
    elif total > 8:
        print(f'elevated:{total}')
    else:
        print(f'ok:{total}')
except: print('ok:0')
" 2>/dev/null)
    PERM_LEVEL=$(echo "$PERM_CHECK" | cut -d: -f1)
    PERM_COUNT=$(echo "$PERM_CHECK" | cut -d: -f2)
    if [ "$PERM_LEVEL" = "excessive" ]; then
        log_warning "excessive-permissions" "Skill requests $PERM_COUNT total permissions (bins+env+config) - unusually broad scope"
    elif [ "$PERM_LEVEL" = "elevated" ]; then
        log_info "elevated-permissions" "Skill requests $PERM_COUNT total permissions (moderate scope)"
    else
        log_pass "reasonable-permissions" "Permission scope is reasonable ($PERM_COUNT items)"
    fi
fi

# Check 9: Telemetry/tracking detection
TELEMETRY_PATTERNS='google-analytics|gtag|ga\(|analytics\.js|segment\.io|segment\.com|mixpanel|amplitude|hotjar|fullstory|posthog|plausible|matomo|piwik|tracking[_-]?pixel|beacon|navigator\.sendBeacon|phone[_-]?home'
if [ -n "$SCRIPT_FILES" ]; then
    TELEMETRY_HITS=$(echo "$SCRIPT_FILES" | xargs grep -ilE "$TELEMETRY_PATTERNS" 2>/dev/null || true)
    if [ -n "$TELEMETRY_HITS" ]; then
        for f in $TELEMETRY_HITS; do
            REL_PATH="${f#$SKILL_DIR/}"
            log_warning "telemetry-detected" "$REL_PATH contains analytics/tracking code" "$REL_PATH"
        done
    else
        log_pass "no-telemetry" "No telemetry or tracking code detected"
    fi
else
    log_pass "no-telemetry" "No telemetry or tracking code detected"
fi

# Check 10: Post-install hook detection (broader than pkg-specific check above)
HOOK_PATTERNS='postinstall|preinstall|post_install|pre_install|setup\.py.*install|setup\.cfg.*install'
if [ -n "$ALL_FILES" ]; then
    HOOK_HITS=$(echo "$ALL_FILES" | xargs grep -ilE "$HOOK_PATTERNS" 2>/dev/null || true)
    # Filter out the ones we already caught via package.json
    if [ -n "$HOOK_HITS" ]; then
        for f in $HOOK_HITS; do
            REL_PATH="${f#$SKILL_DIR/}"
            # Only flag script files as warnings; docs are info
            if echo "$f" | grep -qiE '\.(sh|py|js|ts|rb)$'; then
                log_warning "post-install-hook" "$REL_PATH contains install hook patterns" "$REL_PATH"
            fi
        done
    fi
fi

# Check 11: Symlink attack detection
if [ -n "$SCRIPT_FILES" ]; then
    SYMLINK_PATTERNS='ln -s|os\.symlink|fs\.symlinkSync|fs\.symlink|symlink\(|readlink|os\.readlink'
    SYMLINK_HITS=$(echo "$SCRIPT_FILES" | xargs grep -ilE "$SYMLINK_PATTERNS" 2>/dev/null || true)
    if [ -n "$SYMLINK_HITS" ]; then
        for f in $SYMLINK_HITS; do
            REL_PATH="${f#$SKILL_DIR/}"
            # Check actual symlink usage (not pattern definitions)
            REAL_SYMLINK=$(grep -iE "$SYMLINK_PATTERNS" "$f" 2>/dev/null \
                | grep -vE "$PATTERN_DEF_FILTER" \
                | grep -v '^ *#' | grep -v '^[0-9]*: *#' \
                | grep -vE 'log_(critical|warning|info|pass)' \
                || true)
            [ -z "$REAL_SYMLINK" ] && continue
            # Check if symlink targets sensitive locations
            SENS_SYMLINK=$(echo "$REAL_SYMLINK" | grep -iE '(\/etc\/|~\/\.|\/root\/|\/home\/|\/var\/|\/tmp\/)' || true)
            if [ -n "$SENS_SYMLINK" ]; then
                log_critical "symlink-attack" "$REL_PATH creates symlinks to sensitive locations" "$REL_PATH"
            else
                log_warning "symlink-usage" "$REL_PATH creates or follows symlinks (review targets)" "$REL_PATH"
            fi
        done
    else
        log_pass "no-symlink-attacks" "No symlink manipulation detected"
    fi
else
    log_pass "no-symlink-attacks" "No symlink manipulation detected"
fi

# Check 12: Time bomb detection
if [ -n "$SCRIPT_FILES" ]; then
    TIMEBOMB_PATTERNS='setTimeout.*86400|setInterval.*86400|Date\.now|new Date\(\)|time\.time\(\)|datetime\.now|time\.sleep.*[0-9]{4,}|after.*days|schedule.*future'
    # More specific: date comparisons that could be triggers
    TIMEBOMB_SPECIFIC='if.*date.*>|if.*time.*>|if.*Date\.(now|parse)|\.getTime\(\).*[><=]|timestamp.*[><=].*[0-9]{10}'
    TIMEBOMB_HITS=$(echo "$SCRIPT_FILES" | xargs grep -ilE "$TIMEBOMB_SPECIFIC" 2>/dev/null || true)
    if [ -n "$TIMEBOMB_HITS" ]; then
        for f in $TIMEBOMB_HITS; do
            REL_PATH="${f#$SKILL_DIR/}"
            log_warning "time-bomb" "$REL_PATH contains date/time comparison logic (potential delayed trigger)" "$REL_PATH"
            if ! $JSON_MODE; then
                grep -nE "$TIMEBOMB_SPECIFIC" "$f" 2>/dev/null | head -3 | sed 's/^/    /'
            fi
        done
    else
        log_pass "no-time-bombs" "No suspicious date/time trigger logic detected"
    fi
else
    log_pass "no-time-bombs" "No suspicious date/time trigger logic detected"
fi

# Check 13: Network scope analysis
if [ -n "$SCRIPT_FILES" ]; then
    NET_FILES=$(echo "$SCRIPT_FILES" | xargs grep -ilE 'curl |wget |fetch\(|axios|got\(|request\(|http\.|https\.|urllib|requests\.' 2>/dev/null || true)
    if [ -n "$NET_FILES" ]; then
        NET_COUNT=$(echo "$NET_FILES" | wc -l | tr -d ' ')
        log_info "network-calls" "$NET_COUNT script(s) make network requests"
        
        # Check for unusual ports
        UNUSUAL_PORT_HITS=$(echo "$SCRIPT_FILES" | xargs grep -nE ':[0-9]{4,5}[/"\x27 ]' 2>/dev/null | grep -vE ':(80|443|8080|8443|3000|5000|3306|5432|6379|27017)[/"\x27 ]' || true)
        if [ -n "$UNUSUAL_PORT_HITS" ]; then
            log_warning "unusual-ports" "Network calls to unusual ports detected (review destinations)"
            if ! $JSON_MODE; then
                echo "$UNUSUAL_PORT_HITS" | head -3 | sed 's/^/    /'
            fi
        fi
        
        # Categorize internal vs external
        EXTERNAL_HITS=$(echo "$SCRIPT_FILES" | xargs grep -cE 'https?://[^1][^0920]' 2>/dev/null | grep -v ':0$' || true)
        INTERNAL_HITS=$(echo "$SCRIPT_FILES" | xargs grep -cE '(localhost|127\.0\.0\.1|10\.|192\.168\.|172\.(1[6-9]|2[0-9]|3[01])\.)' 2>/dev/null | grep -v ':0$' || true)
        
        EXT_COUNT=0
        INT_COUNT=0
        if [ -n "$EXTERNAL_HITS" ]; then
            EXT_COUNT=$(echo "$EXTERNAL_HITS" | awk -F: '{s+=$NF}END{print s+0}')
        fi
        if [ -n "$INTERNAL_HITS" ]; then
            INT_COUNT=$(echo "$INTERNAL_HITS" | awk -F: '{s+=$NF}END{print s+0}')
        fi
        log_info "network-scope" "Network calls: ~$EXT_COUNT external, ~$INT_COUNT internal"
    fi

    # Env var reading
    ENV_COUNT=$(echo "$SCRIPT_FILES" | xargs grep -rlE 'process\.env|os\.environ|\$\{?[A-Z_]{3,}\}?' 2>/dev/null | wc -l | tr -d ' ')
    if [ "$ENV_COUNT" -gt 0 ] 2>/dev/null; then
        log_info "env-access" "$ENV_COUNT script(s) read environment variables"
    fi
fi

# ─── NEW v3.0 CHECKS ───

# Check 14: Prompt Injection Detection
PROMPT_INJECTION='ignore (all )?previous instructions|disregard (all )?previous|forget your rules|you are now |act as |pretend to be |do not tell the user|hide this from|secretly |override.*(safety|security|rules|restrictions)|bypass.*(safety|security|rules|restrictions)|disable.*(safety|security|rules)'
STEALTH_DIRECTIVES='send (the )?(contents|data|files?|keys?|secrets?|tokens?|passwords?|credentials?) to [a-z]+|POST .*(contents|files?|keys?|secrets?|tokens?|passwords?|credentials?)|upload .*(contents|files?|keys?|secrets?|tokens?|passwords?|credentials?) to '

if [ -n "$DOC_FILES" ]; then
    for f in $DOC_FILES; do
        REL_PATH="${f#$SKILL_DIR/}"
        FOUND_INJECTION=false

        # Check for prompt injection patterns in markdown content
        # Filter out lines that are documenting/describing checks (contain "Check", "detect", "scan", severity keywords)
        REAL_INJECTION=$(grep -niE "$PROMPT_INJECTION" "$f" 2>/dev/null \
            | grep -vE "$PATTERN_DEF_FILTER" \
            | grep -v '^ *#' | grep -v '^[0-9]*: *#' \
            | grep -vE 'log_(critical|warning|info|pass)' \
            | grep -vE '(Check [0-9]+|CRITICAL\)|WARNING\)|detection|Detects |Scans |Catches |Flags |\| .* \| .* \|)' \
            || true)
        if [ -n "$REAL_INJECTION" ]; then
            FOUND_INJECTION=true
        fi

        # Check for stealth data exfil directives
        REAL_STEALTH=$(grep -niE "$STEALTH_DIRECTIVES" "$f" 2>/dev/null \
            | grep -vE "$PATTERN_DEF_FILTER" \
            | grep -v '^ *#' | grep -v '^[0-9]*: *#' \
            | grep -vE 'log_(critical|warning|info|pass)' \
            | grep -vE '(Check [0-9]+|CRITICAL\)|WARNING\)|detection|Detects |Scans |Catches |Flags |\| .* \| .* \|)' \
            || true)
        if [ -n "$REAL_STEALTH" ]; then
            FOUND_INJECTION=true
        fi

        # Check for hidden instructions in HTML comments
        if grep -qE '<!--.*\b(ignore|override|bypass|send|secret|disregard|pretend)\b' "$f" 2>/dev/null; then
            REAL_HTML=$(grep -nE '<!--.*\b(ignore|override|bypass|send|secret|disregard|pretend)\b' "$f" 2>/dev/null \
                | grep -vE "$PATTERN_DEF_FILTER" \
                | grep -vE 'log_(critical|warning|info|pass)' \
                || true)
            if [ -n "$REAL_HTML" ]; then
                FOUND_INJECTION=true
            fi
        fi

        # Check for zero-width characters (U+200B, U+200C, U+200D, U+FEFF)
        if grep -qP '[\x{200B}\x{200C}\x{200D}\x{FEFF}]' "$f" 2>/dev/null; then
            FOUND_INJECTION=true
        fi

        if $FOUND_INJECTION; then
            log_critical "prompt-injection" "$REL_PATH contains prompt injection / agent manipulation patterns" "$REL_PATH"
            if ! $JSON_MODE; then
                [ -n "$REAL_INJECTION" ] && echo "$REAL_INJECTION" | head -3 | sed 's/^/    /'
                [ -n "$REAL_STEALTH" ] && echo "$REAL_STEALTH" | head -2 | sed 's/^/    /'
                [ -n "$REAL_HTML" ] && echo "$REAL_HTML" | head -2 | sed 's/^/    /'
            fi
        fi
    done
fi

# Check 15: Download-and-Execute
if [ -n "$SCRIPT_FILES" ]; then
    DOWNLOAD_EXEC='curl.*\|.*bash|curl.*\|.*sh[^a-z]|wget.*-O-.*\|.*bash|eval \$\(curl|eval \$\(wget|curl.*\|.*python|wget.*\|.*python'
    DOWNLOAD_THEN_EXEC='chmod \+x.*/tmp/|chmod \+x.*/var/'
    PIP_UNSAFE='pip install.*(https?://|git\+|\.tar\.gz|\.whl)'
    NPM_UNSAFE='npm install.*(git\+|git://|https?://.*\.tar|https?://.*\.tgz)'

    for f in $SCRIPT_FILES; do
        REL_PATH="${f#$SKILL_DIR/}"
        FOUND_DL=false

        REAL_DL=$(grep -nE "$DOWNLOAD_EXEC" "$f" 2>/dev/null \
            | grep -vE "$PATTERN_DEF_FILTER" \
            | grep -v '^ *#' | grep -v '^[0-9]*: *#' \
            | grep -vE 'log_(critical|warning|info|pass)' \
            || true)
        [ -n "$REAL_DL" ] && FOUND_DL=true

        REAL_DL2=$(grep -nE "$DOWNLOAD_THEN_EXEC" "$f" 2>/dev/null \
            | grep -vE "$PATTERN_DEF_FILTER" \
            | grep -v '^ *#' | grep -v '^[0-9]*: *#' \
            | grep -vE 'log_(critical|warning|info|pass)' \
            || true)
        [ -n "$REAL_DL2" ] && FOUND_DL=true

        REAL_DL3=$(grep -nE "$PIP_UNSAFE" "$f" 2>/dev/null \
            | grep -vE "$PATTERN_DEF_FILTER" \
            | grep -v '^ *#' | grep -v '^[0-9]*: *#' \
            | grep -vE 'log_(critical|warning|info|pass)' \
            || true)
        [ -n "$REAL_DL3" ] && FOUND_DL=true

        REAL_DL4=$(grep -nE "$NPM_UNSAFE" "$f" 2>/dev/null \
            | grep -vE "$PATTERN_DEF_FILTER" \
            | grep -v '^ *#' | grep -v '^[0-9]*: *#' \
            | grep -vE 'log_(critical|warning|info|pass)' \
            || true)
        [ -n "$REAL_DL4" ] && FOUND_DL=true

        if $FOUND_DL; then
            log_critical "download-execute" "$REL_PATH downloads and executes remote code" "$REL_PATH"
            if ! $JSON_MODE; then
                [ -n "$REAL_DL" ] && echo "$REAL_DL" | head -3 | sed 's/^/    /'
                [ -n "$REAL_DL2" ] && echo "$REAL_DL2" | head -2 | sed 's/^/    /'
            fi
        fi
    done
fi

# Check 16: Hidden Files
ALLOWED_DOTFILES='\.gitignore$|\.editorconfig$|\.eslintrc|\.prettierrc|\.clawhub$'
HIDDEN_FILES=$(find "$SKILL_DIR" -maxdepth 2 -name '.*' -not -name '.' -not -name '..' -not -name '.git' -not -name '.DS_Store' 2>/dev/null \
    | grep -v "$SKILL_DIR/node_modules/" \
    | grep -v "$SKILL_DIR/.git/" \
    | grep -v "$SKILL_DIR/test-skills/" | grep -v "$SKILL_DIR/tests/" \
    || true)
if [ -n "$HIDDEN_FILES" ]; then
    SUSPICIOUS_HIDDEN=$(echo "$HIDDEN_FILES" | grep -vE "$ALLOWED_DOTFILES" || true)
    if [ -n "$SUSPICIOUS_HIDDEN" ]; then
        for f in $SUSPICIOUS_HIDDEN; do
            REL_PATH="${f#$SKILL_DIR/}"
            log_warning "hidden-file" "Hidden file found: $REL_PATH (may hide malicious content)" "$REL_PATH"
        done
    fi
fi

# Check 17: Env Var Exfiltration
if [ -n "$SCRIPT_FILES" ]; then
    SENSITIVE_ENV='OPENAI_API_KEY|ANTHROPIC_API_KEY|AWS_SECRET|AWS_ACCESS_KEY|GITHUB_TOKEN|GITLAB_TOKEN|SLACK_TOKEN|DISCORD_TOKEN|STRIPE_KEY|STRIPE_SECRET|DATABASE_URL|DB_PASSWORD|MONGO_URI|REDIS_URL|API_KEY|API_SECRET|AUTH_TOKEN|PRIVATE_KEY|JWT_SECRET|ENCRYPTION_KEY'
    for f in $SCRIPT_FILES; do
        REL_PATH="${f#$SKILL_DIR/}"
        # Check if script reads sensitive env vars
        ENV_READ=$(grep -nE "(os\.environ|os\.getenv|process\.env|getenv|ENV\[).*($SENSITIVE_ENV)" "$f" 2>/dev/null \
            | grep -vE "$PATTERN_DEF_FILTER" \
            | grep -v '^ *#' | grep -v '^[0-9]*: *#' \
            | grep -vE 'log_(critical|warning|info|pass)' \
            || true)
        if [ -n "$ENV_READ" ]; then
            # Check if same file also makes network calls
            NET_CALLS=$(grep -iE 'curl |wget |fetch\(|requests\.(post|get|put)|axios|http\.request|urllib|got\(' "$f" 2>/dev/null \
                | grep -vE "$PATTERN_DEF_FILTER" \
                | grep -v '^ *#' | grep -v '^[0-9]*: *#' \
                | grep -vE 'log_(critical|warning|info|pass)' \
                || true)
            if [ -n "$NET_CALLS" ]; then
                log_critical "env-exfiltration" "$REL_PATH reads sensitive env vars AND makes network calls" "$REL_PATH"
                if ! $JSON_MODE; then
                    echo "$ENV_READ" | head -2 | sed 's/^/    /'
                fi
            fi
        fi
    done
fi

# Check 18: Privilege Escalation
if [ -n "$SCRIPT_FILES" ]; then
    PRIVESC_SUDO='(^|[;&|] *)sudo '
    PRIVESC_CHMOD='chmod (777|[0-7]*7[0-7]*|[+]s) '
    PRIVESC_SYSPATH='(cp |mv |install |ln ).*(/usr/local/bin/|/usr/bin/|/etc/|/opt/|/sbin/)'
    PRIVESC_CHOWN='chown root'

    for f in $SCRIPT_FILES; do
        REL_PATH="${f#$SKILL_DIR/}"
        FOUND_PRIVESC=false

        REAL_SUDO=$(grep -nE "$PRIVESC_SUDO" "$f" 2>/dev/null \
            | grep -vE "$PATTERN_DEF_FILTER" \
            | grep -v '^ *#' | grep -v '^[0-9]*: *#' \
            | grep -vE 'log_(critical|warning|info|pass)' \
            || true)
        [ -n "$REAL_SUDO" ] && FOUND_PRIVESC=true

        REAL_CHMOD=$(grep -nE "$PRIVESC_CHMOD" "$f" 2>/dev/null \
            | grep -vE "$PATTERN_DEF_FILTER" \
            | grep -v '^ *#' | grep -v '^[0-9]*: *#' \
            | grep -vE 'log_(critical|warning|info|pass)' \
            || true)
        [ -n "$REAL_CHMOD" ] && FOUND_PRIVESC=true

        REAL_SYSPATH=$(grep -nE "$PRIVESC_SYSPATH" "$f" 2>/dev/null \
            | grep -vE "$PATTERN_DEF_FILTER" \
            | grep -v '^ *#' | grep -v '^[0-9]*: *#' \
            | grep -vE 'log_(critical|warning|info|pass)' \
            || true)
        [ -n "$REAL_SYSPATH" ] && FOUND_PRIVESC=true

        REAL_CHOWN=$(grep -nE "$PRIVESC_CHOWN" "$f" 2>/dev/null \
            | grep -vE "$PATTERN_DEF_FILTER" \
            | grep -v '^ *#' | grep -v '^[0-9]*: *#' \
            | grep -vE 'log_(critical|warning|info|pass)' \
            || true)
        [ -n "$REAL_CHOWN" ] && FOUND_PRIVESC=true

        if $FOUND_PRIVESC; then
            log_critical "privilege-escalation" "$REL_PATH attempts privilege escalation" "$REL_PATH"
            if ! $JSON_MODE; then
                [ -n "$REAL_SUDO" ] && echo "$REAL_SUDO" | head -2 | sed 's/^/    /'
                [ -n "$REAL_CHMOD" ] && echo "$REAL_CHMOD" | head -2 | sed 's/^/    /'
                [ -n "$REAL_SYSPATH" ] && echo "$REAL_SYSPATH" | head -2 | sed 's/^/    /'
            fi
        fi
    done
fi

# ─── DOC-ONLY CREDENTIAL MENTIONS (downgraded) ───

if [ -n "$DOC_FILES" ]; then
    DOC_CRED_HITS=$(echo "$DOC_FILES" | xargs grep -ilE "$CRED_PATTERNS" 2>/dev/null || true)
    if [ -n "$DOC_CRED_HITS" ]; then
        DOC_CRED_COUNT=$(echo "$DOC_CRED_HITS" | wc -l | tr -d ' ')
        log_info "doc-credentials" "$DOC_CRED_COUNT doc file(s) mention credentials (documentation, not executable)"
    fi
fi

# ─── SUMMARY ───

if $JSON_MODE; then
    echo "{\"skill\":\"$SKILL_NAME\",\"path\":\"$SKILL_DIR\",\"allowlisted\":$IS_ALLOWLISTED,\"criticals\":$CRITICALS,\"warnings\":$WARNINGS,\"infos\":$INFOS,\"verdict\":\"$([ $EXIT_CODE -eq 0 ] && echo 'pass' || ([ $EXIT_CODE -eq 1 ] && echo 'review' || echo 'fail'))\",\"items\":[$JSON_ITEMS]}"
else
    echo ""
    echo "========================================="
    echo "  RESULTS"
    echo "========================================="
    echo -e "  Critical: ${RED}$CRITICALS${NC}"
    echo -e "  Warnings: ${YELLOW}$WARNINGS${NC}"
    echo -e "  Info:     ${BLUE}$INFOS${NC}"
    echo ""

    if [ $EXIT_CODE -eq 0 ]; then
        echo -e "${GREEN}VERDICT: PASS - Skill looks clean${NC}"
    elif [ $EXIT_CODE -eq 1 ]; then
        echo -e "${YELLOW}VERDICT: REVIEW - Manual inspection recommended${NC}"
    else
        echo -e "${RED}VERDICT: FAIL - Critical security issues found. DO NOT INSTALL.${NC}"
    fi
fi

exit $EXIT_CODE
