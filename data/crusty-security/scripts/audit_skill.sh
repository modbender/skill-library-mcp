#!/usr/bin/env bash
set -euo pipefail

# audit_skill.sh — Static analysis of an OpenClaw skill directory for security risks
# Usage: audit_skill.sh [OPTIONS] <skill_directory>

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/dashboard.sh" 2>/dev/null || true

# Cross-platform millisecond timestamp (macOS date doesn't support %N)
get_ms() {
  if [[ "$OSTYPE" == darwin* ]]; then
    python3 -c "import time; print(int(time.time()*1000))"
  else
    date +%s%3N
  fi
}
AUDIT_START_MS=$(get_ms)

show_help() {
    cat <<'EOF'
Usage: audit_skill.sh [OPTIONS] <skill_directory>

Perform static security analysis on an OpenClaw skill directory.

Options:
  --verbose       Show matched lines for each finding
  --json          JSON output (default)
  -h, --help      Show this help

Checks:
  - Suspicious exec patterns (curl|sh, base64 decode, eval)
  - Data exfiltration patterns (outbound HTTP to unknown domains)
  - File system access outside workspace
  - Obfuscated code (hex/base64 encoded strings, minified scripts)
  - Hidden files (dotfiles, dot-directories)
  - Unexpected binary files
  - Reverse shell patterns
  - Credential harvesting patterns
  - Crypto mining indicators

Output: JSON with risk_score (low/medium/high/critical), findings array
Exit codes: 0 = low/medium risk, 1 = high/critical risk, 2 = error
EOF
    exit 0
}

VERBOSE=false
TARGET=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --verbose) VERBOSE=true; shift ;;
        --json) shift ;;
        -h|--help) show_help ;;
        -*) echo "Unknown option: $1" >&2; show_help ;;
        *) TARGET="$1"; shift ;;
    esac
done

if [[ -z "$TARGET" ]]; then
    echo '{"status":"error","message":"No skill directory specified. Use --help."}' >&2
    exit 2
fi

if [[ ! -d "$TARGET" ]]; then
    echo "{\"status\":\"error\",\"message\":\"Not a directory: $TARGET\"}" >&2
    exit 2
fi

TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
SKILL_NAME=$(basename "$TARGET")

# Score tracking
CRITICAL_COUNT=0
HIGH_COUNT=0
MEDIUM_COUNT=0
LOW_COUNT=0
INFO_COUNT=0
FINDINGS=""

add_finding() {
    local severity="$1" category="$2" message="$3" evidence="${4:-}"
    case "$severity" in
        critical) ((CRITICAL_COUNT++)) || true ;;
        high) ((HIGH_COUNT++)) || true ;;
        medium) ((MEDIUM_COUNT++)) || true ;;
        low) ((LOW_COUNT++)) || true ;;
        info) ((INFO_COUNT++)) || true ;;
    esac

    # Escape for JSON
    message_esc=$(printf '%s' "$message" | sed 's/\\/\\\\/g; s/"/\\"/g')
    evidence_esc=$(printf '%s' "$evidence" | head -10 | sed 's/\\/\\\\/g; s/"/\\"/g; s/	/\\t/g' | tr '\n' '|' | sed 's/|/\\n/g')

    if [[ -n "$FINDINGS" ]]; then
        FINDINGS+=","
    fi
    FINDINGS+="{\"severity\":\"$severity\",\"category\":\"$category\",\"message\":\"$message_esc\",\"evidence\":\"$evidence_esc\"}"
}

# Collect all text files for analysis
TEXT_FILES=()
BINARY_FILES=()
HIDDEN_FILES=()
ALL_FILES=()

while IFS= read -r -d '' f; do
    ALL_FILES+=("$f")
    rel="${f#$TARGET/}"

    # Hidden files check
    if [[ "$rel" =~ (^|/)\. ]] && [[ "$rel" != ".gitignore" ]] && [[ "$rel" != ".gitkeep" ]]; then
        HIDDEN_FILES+=("$rel")
    fi

    # Binary vs text
    if file -b --mime-type "$f" 2>/dev/null | grep -qE '^(text/|application/json|application/xml|application/javascript|application/x-sh)'; then
        TEXT_FILES+=("$f")
    elif file -b --mime-type "$f" 2>/dev/null | grep -qE '^(image/|application/pdf)'; then
        : # expected file types, skip
    else
        mime=$(file -b --mime-type "$f" 2>/dev/null || echo "unknown")
        if echo "$mime" | grep -qE '(executable|octet-stream|x-mach|x-elf|x-dosexec|x-pie-executable)'; then
            BINARY_FILES+=("$rel")
        fi
    fi
done < <(find "$TARGET" -type f -not -path '*/__pycache__/*' -not -path '*/.git/*' -not -path '*/node_modules/*' -print0 2>/dev/null)

# --- CHECK: Hidden files ---
if [[ ${#HIDDEN_FILES[@]} -gt 0 ]]; then
    evidence=$(printf '%s\n' "${HIDDEN_FILES[@]}" | head -10)
    add_finding "medium" "hidden_files" "Hidden files detected (${#HIDDEN_FILES[@]} found)" "$evidence"
fi

# --- CHECK: Unexpected binary files ---
if [[ ${#BINARY_FILES[@]} -gt 0 ]]; then
    evidence=$(printf '%s\n' "${BINARY_FILES[@]}" | head -10)
    add_finding "high" "binary_files" "Unexpected binary/executable files (${#BINARY_FILES[@]} found)" "$evidence"
fi

# Skip text analysis if no text files
if [[ ${#TEXT_FILES[@]} -eq 0 ]]; then
    add_finding "info" "empty" "No text files found in skill directory" ""
fi

# Grep helper — search all text files
grep_files() {
    local pattern="$1"
    grep -rnlE "$pattern" "${TEXT_FILES[@]}" 2>/dev/null || true
}

grep_files_with_lines() {
    local pattern="$1"
    grep -rnE "$pattern" "${TEXT_FILES[@]}" 2>/dev/null | head -20 || true
}

# --- CHECK: Curl/wget piped to shell (CRITICAL) ---
matches=$(grep_files_with_lines 'curl\s+.*\|\s*(ba)?sh|wget\s+.*\|\s*(ba)?sh|curl\s+.*\|\s*python|wget\s+.*\|\s*python')
if [[ -n "$matches" ]]; then
    add_finding "critical" "pipe_to_shell" "Download-and-execute pattern found (curl/wget piped to shell)" "$matches"
fi

# --- CHECK: Reverse shell patterns (CRITICAL) ---
matches=$(grep_files_with_lines '/dev/tcp/|/dev/udp/|mkfifo.*nc|ncat\s+-[elc]|bash\s+-i\s+>&')
if [[ -n "$matches" ]]; then
    add_finding "critical" "reverse_shell" "Reverse shell pattern detected" "$matches"
fi

# --- CHECK: eval/exec with dynamic input (HIGH) ---
matches=$(grep_files_with_lines 'eval\s*\(|eval\s+"?\$|exec\s*\(.*\$|child_process|subprocess\.call.*shell.*True|os\.system\s*\(')
if [[ -n "$matches" ]]; then
    add_finding "high" "dynamic_exec" "Dynamic code execution pattern (eval/exec/os.system)" "$matches"
fi

# --- CHECK: Base64 decode + execute (HIGH) ---
matches=$(grep_files_with_lines 'base64\s+(--)?-?d|atob\s*\(|b64decode|base64\.decode|echo.*\|.*base64.*-d.*\|')
if [[ -n "$matches" ]]; then
    add_finding "high" "base64_exec" "Base64 decoding pattern (potential obfuscated payload)" "$matches"
fi

# --- CHECK: Data exfiltration indicators (HIGH) ---
matches=$(grep_files_with_lines 'webhook\.site|requestbin|pipedream\.net|ngrok\.io|pastebin\.com|hookbin|burpcollaborator|interact\.sh|canarytokens')
if [[ -n "$matches" ]]; then
    add_finding "high" "exfil_endpoints" "Known data exfiltration endpoint references" "$matches"
fi

# --- CHECK: Credential harvesting (HIGH) ---
matches=$(grep_files_with_lines '\.ssh/id_rsa|\.ssh/id_ed25519|authorized_keys|\.env\b|process\.env|os\.environ|/etc/shadow|AWS_SECRET|PRIVATE_KEY|api[_-]?key|secret[_-]?key')
if [[ -n "$matches" ]]; then
    # Filter out references in documentation/markdown
    non_doc=$(echo "$matches" | grep -vE '\.(md|txt|rst):' || true)
    if [[ -n "$non_doc" ]]; then
        add_finding "high" "credential_access" "Credential/secret access patterns detected" "$non_doc"
    else
        add_finding "low" "credential_docs" "Credential references in documentation (likely benign)" ""
    fi
fi

# --- CHECK: File access outside workspace (MEDIUM) ---
matches=$(grep_files_with_lines '/etc/passwd|/etc/cron|/var/spool|/usr/bin|/usr/local/bin|/root/')
if [[ -n "$matches" ]]; then
    non_doc=$(echo "$matches" | grep -vE '\.(md|txt|rst):' || true)
    if [[ -n "$non_doc" ]]; then
        add_finding "medium" "system_access" "System file access patterns outside workspace" "$non_doc"
    fi
fi

# --- CHECK: Network calls to hardcoded IPs (MEDIUM) ---
matches=$(grep_files_with_lines '[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}')
if [[ -n "$matches" ]]; then
    # Filter out localhost, common private ranges in comments
    suspicious=$(echo "$matches" | grep -vE '(127\.0\.0\.1|0\.0\.0\.0|192\.168\.|10\.|172\.(1[6-9]|2[0-9]|3[01])\.)' | grep -vE '\.(md|txt|rst):' || true)
    if [[ -n "$suspicious" ]]; then
        add_finding "medium" "hardcoded_ips" "Hardcoded IP addresses found" "$suspicious"
    fi
fi

# --- CHECK: Crypto mining indicators (CRITICAL) ---
matches=$(grep_files_with_lines 'stratum\+tcp://|xmrig|monero|cryptonight|pool\.mine|hashrate|--coin\b')
if [[ -n "$matches" ]]; then
    add_finding "critical" "crypto_mining" "Cryptocurrency mining indicators detected" "$matches"
fi

# --- CHECK: Obfuscated code (MEDIUM) ---
# Look for very long lines (likely minified/obfuscated)
long_lines=""
for f in "${TEXT_FILES[@]}"; do
    result=$(awk 'length > 500 {print FILENAME":"NR": (line length: "length")"; exit}' "$f" 2>/dev/null || true)
    if [[ -n "$result" ]]; then
        long_lines+="$result\n"
    fi
done
if [[ -n "$long_lines" ]]; then
    add_finding "medium" "obfuscation" "Potentially obfuscated code (very long lines >500 chars)" "$(echo -e "$long_lines" | head -5)"
fi

# Look for hex-encoded strings
matches=$(grep_files_with_lines '\\x[0-9a-fA-F]{2}\\x[0-9a-fA-F]{2}\\x[0-9a-fA-F]{2}|\\u[0-9a-fA-F]{4}\\u[0-9a-fA-F]{4}')
if [[ -n "$matches" ]]; then
    add_finding "medium" "hex_encoding" "Hex/unicode encoded strings detected" "$matches"
fi

# --- CHECK: Modifying agent config files (HIGH) ---
matches=$(grep_files_with_lines 'AGENTS\.md|SOUL\.md|MEMORY\.md|TOOLS\.md')
if [[ -n "$matches" ]]; then
    # Writing/modifying (not just reading/referencing)
    write_matches=$(echo "$matches" | grep -iE '(write|>>|>|sed\s|mv\s|cp\s|echo.*>)' || true)
    if [[ -n "$write_matches" ]]; then
        add_finding "high" "config_modification" "Skill may modify agent configuration files" "$write_matches"
    fi
fi

# --- CHECK: Scheduled task creation (MEDIUM) ---
matches=$(grep_files_with_lines 'crontab|systemctl\s+enable|launchctl\s+load|at\s+\d|schtasks')
if [[ -n "$matches" ]]; then
    non_doc=$(echo "$matches" | grep -vE '\.(md|txt|rst):' || true)
    if [[ -n "$non_doc" ]]; then
        add_finding "medium" "persistence" "Scheduled task / persistence mechanism patterns" "$non_doc"
    fi
fi

# --- CHECK: Skill size / file count (INFO) ---
file_count=${#ALL_FILES[@]}
total_size=$(du -sb "$TARGET" 2>/dev/null | awk '{print $1}' || echo "0")
total_size_mb=$((total_size / 1048576))

if [[ $file_count -gt 100 ]]; then
    add_finding "low" "size" "Large skill: $file_count files, ${total_size_mb}MB" ""
fi

# --- Determine overall risk score ---
if [[ $CRITICAL_COUNT -gt 0 ]]; then
    RISK_SCORE="critical"
elif [[ $HIGH_COUNT -gt 0 ]]; then
    RISK_SCORE="high"
elif [[ $MEDIUM_COUNT -gt 0 ]]; then
    RISK_SCORE="medium"
else
    RISK_SCORE="low"
fi

# Output JSON
cat <<EOF
{
  "skill": "$SKILL_NAME",
  "directory": "$TARGET",
  "timestamp": "$TIMESTAMP",
  "risk_score": "$RISK_SCORE",
  "summary": {
    "critical": $CRITICAL_COUNT,
    "high": $HIGH_COUNT,
    "medium": $MEDIUM_COUNT,
    "low": $LOW_COUNT,
    "info": $INFO_COUNT
  },
  "file_stats": {
    "total_files": $file_count,
    "text_files": ${#TEXT_FILES[@]},
    "binary_files": ${#BINARY_FILES[@]},
    "hidden_files": ${#HIDDEN_FILES[@]},
    "total_size_bytes": $total_size
  },
  "findings": [$FINDINGS]
}
EOF

# Push to dashboard
AUDIT_DURATION=$(($(get_ms) - AUDIT_START_MS))
DASH_STATUS="clean"
DASH_SEVERITY="none"
case "$RISK_SCORE" in
    critical) DASH_STATUS="malicious"; DASH_SEVERITY="critical" ;;
    high) DASH_STATUS="suspicious"; DASH_SEVERITY="high" ;;
    medium) DASH_SEVERITY="medium" ;;
esac
SKILL_RESULTS="{\"risk_score\":\"$RISK_SCORE\",\"critical\":$CRITICAL_COUNT,\"high\":$HIGH_COUNT,\"medium\":$MEDIUM_COUNT,\"low\":$LOW_COUNT}"
cg_push_scan "skill_audit" "${SKILL_DIR:-unknown}" "$DASH_STATUS" "Crusty Security Skill Audit" "$DASH_SEVERITY" "$AUDIT_DURATION" "$SKILL_RESULTS" 2>/dev/null || true

# Exit code
case "$RISK_SCORE" in
    critical|high) exit 1 ;;
    *) exit 0 ;;
esac
