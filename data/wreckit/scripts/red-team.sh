#!/usr/bin/env bash
# wreckit — Adversarial Red-Team Scanner
# Usage: ./red-team.sh [project-path]
# Scans for security vulnerabilities, injection vectors, auth bypasses, and more.
# For regex analysis, use regex-complexity.sh
# Outputs structured JSON report.

set -euo pipefail

PROJECT="${1:-.}"
PROJECT="$(cd "$PROJECT" && pwd)"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FINDINGS_FILE=$(mktemp /tmp/wreckit-redteam-XXXXXX.json)
FINDING_COUNT=0
BLOCKER_COUNT=0
WARNING_COUNT=0
INFO_COUNT=0

# ─── Helpers ────────────────────────────────────────────────────────────────
add_finding() {
  local id="$1" category="$2" pattern="$3" severity="$4" file="$5" line="$6" evidence="$7" recommendation="$8"
  FINDING_COUNT=$((FINDING_COUNT + 1))
  case "$severity" in
    blocker) BLOCKER_COUNT=$((BLOCKER_COUNT + 1)) ;;
    warning) WARNING_COUNT=$((WARNING_COUNT + 1)) ;;
    info)    INFO_COUNT=$((INFO_COUNT + 1)) ;;
  esac
  # Append to findings array (using a temp file with newline-delimited JSON)
  python3 -c "
import json, sys
finding = {
    'id': sys.argv[1],
    'category': sys.argv[2],
    'pattern': sys.argv[3],
    'severity': sys.argv[4],
    'file': sys.argv[5],
    'line': int(sys.argv[6]) if sys.argv[6].isdigit() else 0,
    'evidence': sys.argv[7][:200],
    'recommendation': sys.argv[8]
}
print(json.dumps(finding))
" "$id" "$category" "$pattern" "$severity" "$file" "$line" "$evidence" "$recommendation" >> "$FINDINGS_FILE"
}

scan_pattern() {
  local id="$1" category="$2" pattern_desc="$3" severity="$4" recommendation="$5" grep_pattern="$6"
  
  # Search source files (exclude .git, node_modules, __pycache__, .wreckit, vendor)
  while IFS=: read -r file line_num match; do
    [ -z "$file" ] && continue
    [ -z "$match" ] && continue
    add_finding "$id" "$category" "$pattern_desc" "$severity" "$file" "$line_num" "$match" "$recommendation"
  done < <(grep -rn --include="*.js" --include="*.ts" --include="*.py" --include="*.rb" \
    --include="*.go" --include="*.java" --include="*.php" --include="*.sh" \
    --include="*.jsx" --include="*.tsx" --include="*.mjs" --include="*.cjs" \
    --exclude-dir=".git" --exclude-dir="node_modules" --exclude-dir="__pycache__" \
    --exclude-dir=".wreckit" --exclude-dir="vendor" --exclude-dir="dist" \
    --exclude-dir=".venv" --exclude-dir="venv" --exclude-dir="build" \
    -E "$grep_pattern" "$PROJECT" 2>/dev/null | head -20 || true)
}

log() { echo "  [red-team] $*" >&2; }

echo "================================================" >&2
echo "  wreckit Red-Team Scanner" >&2
echo "  Project: $PROJECT" >&2
echo "================================================" >&2
echo "" >&2

# ─── Initialize findings file ───────────────────────────────────────────────
> "$FINDINGS_FILE"

# ─── 1. INJECTION: SQL string concatenation ──────────────────────────────────
log "Scanning: SQL injection patterns..."
scan_pattern "SQL_CONCAT" "injection" "SQL string concatenation (possible SQLi)" "blocker" \
  "Use parameterized queries / prepared statements" \
  "\"SELECT .*(\" *\+|\.format\(|f\".*\$|%s.*%)" 

scan_pattern "SQL_CONCAT_2" "injection" "SQL query built with string concat" "blocker" \
  "Use parameterized queries" \
  "(query|sql|SQL)\s*[+\.]=\s*[\"']"

scan_pattern "SQL_RAW" "injection" "Raw SQL execution with variable" "blocker" \
  "Use parameterized queries" \
  "(execute|query|raw)\([\"']?(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE)"

# ─── 2. INJECTION: Command injection ─────────────────────────────────────────
log "Scanning: Command injection patterns..."
scan_pattern "CMD_EXEC_EVAL" "injection" "eval() with non-literal argument" "blocker" \
  "Never use eval with user input. Use safe alternatives." \
  "(^|[^a-zA-Z])(eval|Function)\s*\("

scan_pattern "CMD_SHELL_TRUE" "injection" "Python subprocess with shell=True" "blocker" \
  "Use shell=False and pass args as list" \
  "shell\s*=\s*True"

scan_pattern "CMD_OS_SYSTEM" "injection" "os.system() call" "blocker" \
  "Use subprocess with shell=False instead" \
  "os\.(system|popen|execv|execve)\s*\("

scan_pattern "CMD_SPAWN" "injection" "child_process.exec with dynamic command" "blocker" \
  "Use execFile or spawn with array args instead" \
  "(exec|execSync)\s*\([^)]*[+\`]"

# ─── 3. INJECTION: Path traversal ────────────────────────────────────────────
log "Scanning: Path traversal patterns..."
scan_pattern "PATH_TRAVERSAL" "injection" "Path constructed from user input without normalization" "blocker" \
  "Use path.resolve() + verify result starts with allowed base dir" \
  "join\s*\(.*req\.(params|query|body)"

scan_pattern "PATH_DOTDOT" "injection" "Literal ../ in path construction" "warning" \
  "Validate and normalize all user-supplied paths" \
  "\.\.\/"

# ─── 4. AUTHENTICATION: Hardcoded secrets ────────────────────────────────────
log "Scanning: Hardcoded secrets..."
scan_pattern "HARDCODED_PASSWORD" "auth" "Hardcoded password in source" "blocker" \
  "Move to environment variables or secrets manager" \
  "(password|passwd|pwd)\s*=\s*[\"'][^\"']{4,}[\"']"

scan_pattern "HARDCODED_SECRET" "auth" "Hardcoded secret/token in source" "blocker" \
  "Move to environment variables or secrets manager" \
  "(secret|token|api_key|apikey|auth_token)\s*=\s*[\"'][a-zA-Z0-9+/]{16,}[\"']"

scan_pattern "HARDCODED_AWS" "auth" "Hardcoded AWS key" "blocker" \
  "Use IAM roles or secrets manager" \
  "AKIA[0-9A-Z]{16}"

scan_pattern "HARDCODED_JWT_SECRET" "auth" "Hardcoded JWT secret" "blocker" \
  "Load JWT secret from environment" \
  "(jwt|JWT).*(sign|verify)\s*\([^,)]+,\s*[\"'][^\"']{8,}"

# ─── 5. AUTHENTICATION: Missing auth checks ───────────────────────────────────
log "Scanning: Authentication gaps..."
scan_pattern "JWT_NONE_ALG" "auth" "JWT algorithm set to none" "blocker" \
  "Always verify JWT algorithm explicitly. Reject 'none'." \
  "algorithm[s]?\s*[=:]\s*[\"']none[\"']"

scan_pattern "CERT_VERIFY_FALSE" "auth" "SSL certificate verification disabled" "blocker" \
  "Never disable cert verification in production" \
  "(verify\s*=\s*False|checkServerIdentity\s*:\s*(null|undefined|\(\s*\)\s*=>|false))"

scan_pattern "CORS_WILDCARD" "auth" "CORS wildcard origin" "warning" \
  "Restrict CORS to known origins in production" \
  "Access-Control-Allow-Origin.*\*|origin\s*:\s*[\"']\*[\"']"

# ─── 6. CRYPTO: Weak algorithms ──────────────────────────────────────────────
log "Scanning: Weak cryptography..."
scan_pattern "WEAK_HASH_MD5" "crypto" "MD5 used for security purpose" "warning" \
  "Use SHA-256 or stronger for security hashing" \
  "md5\s*\(|MD5\s*\(|createHash\s*\(\s*[\"']md5[\"']\)"

scan_pattern "WEAK_HASH_SHA1" "crypto" "SHA1 used for security purpose" "warning" \
  "Use SHA-256 or stronger" \
  "sha1\s*\(|SHA1\s*\(|createHash\s*\(\s*[\"']sha1[\"']\)"

scan_pattern "WEAK_CIPHER_DES" "crypto" "DES/3DES cipher used" "warning" \
  "Use AES-256 instead" \
  "(DES|3DES|TripleDES|des-ede|des-cbc)"

scan_pattern "WEAK_CIPHER_ECB" "crypto" "ECB mode cipher (deterministic, insecure)" "warning" \
  "Use CBC or GCM mode" \
  "(AES-ECB|ecb|ECB|mode.*ECB)"

scan_pattern "MATH_RANDOM_CRYPTO" "crypto" "Math.random() for security-sensitive value" "warning" \
  "Use crypto.randomBytes() or secrets module instead" \
  "Math\.random\s*\(\s*\).*(token|secret|key|session|nonce|salt)"

# ─── 7. ERROR HANDLING: Info leaks ────────────────────────────────────────────
log "Scanning: Information leaks..."
scan_pattern "STACK_TRACE_RESPONSE" "error_handling" "Stack trace sent to HTTP response" "warning" \
  "Sanitize error responses in production; log internally only" \
  "res\.(send|json|write)\s*\([^)]*\.(stack|message|trace)"

scan_pattern "VERBOSE_DEBUG" "error_handling" "Debug mode flag" "info" \
  "Ensure debug=False or DEBUG=False in production" \
  "(DEBUG\s*=\s*True|debug\s*=\s*true|app\.debug\s*=\s*True)"

scan_pattern "CONSOLE_LOG_SENSITIVE" "error_handling" "Logging potentially sensitive data" "warning" \
  "Redact passwords/tokens before logging" \
  "(console\.log|print|logger\.)\s*\([^)]*\b(password|token|secret|key|auth)"

# ─── 8. DESERIALIZATION ────────────────────────────────────────────────────────
log "Scanning: Unsafe deserialization..."
scan_pattern "PICKLE_LOADS" "deserialization" "pickle.loads() on untrusted data" "blocker" \
  "Never unpickle untrusted data. Use JSON instead." \
  "pickle\.loads?\s*\("

scan_pattern "YAML_UNSAFE_LOAD" "deserialization" "yaml.load() without Loader (unsafe)" "blocker" \
  "Use yaml.safe_load() instead of yaml.load()" \
  "yaml\.load\s*\([^)]*\)" 

scan_pattern "PROTO_POLLUTION" "deserialization" "Possible prototype pollution" "warning" \
  "Validate that user input doesn't contain __proto__ or constructor keys" \
  "__proto__|constructor\s*\[|prototype\s*\["

# ─── 9. RESOURCE: Unchecked allocation ───────────────────────────────────────
log "Scanning: Resource exhaustion patterns..."
scan_pattern "ALLOC_USER_SIZE" "resource_exhaustion" "Buffer allocation size from user input" "warning" \
  "Validate and cap user-controlled sizes before allocation" \
  "(Buffer\.alloc|new Array|malloc|calloc)\s*\([^)]*req\."

# ─── 10. Check for .env files committed ──────────────────────────────────────
log "Checking for committed secret files..."
if git -C "$PROJECT" ls-files --error-unmatch .env 2>/dev/null; then
  add_finding "ENV_COMMITTED" "auth" ".env file committed to git" "blocker" ".env" "0" \
    ".env file is tracked by git" "Add .env to .gitignore and rotate all secrets"
fi

if git -C "$PROJECT" ls-files 2>/dev/null | grep -qE "\.(pem|key|p12|pfx|jks)$"; then
  KEYFILES=$(git -C "$PROJECT" ls-files | grep -E "\.(pem|key|p12|pfx|jks)$" | head -3 | tr '\n' ',')
  add_finding "KEY_COMMITTED" "auth" "Private key/cert file committed to git" "blocker" "$KEYFILES" "0" \
    "Private key file tracked in git" "Remove file, rotate keys, add to .gitignore"
fi

# ─── 11. Check git history for secrets (last 3 commits only, fast) ───────────
log "Checking recent git history for secrets..."
if git -C "$PROJECT" log --oneline -3 2>/dev/null > /dev/null 2>&1; then
  GIT_SECRETS=$(git -C "$PROJECT" log -3 -p --no-merges 2>/dev/null | \
    grep -E "^\+.*(password|secret|token)\s*=\s*[\"'][a-zA-Z0-9+/]{12,}" | head -3 || true)
  if [ -n "$GIT_SECRETS" ]; then
    add_finding "GIT_HISTORY_SECRETS" "auth" "Possible secrets in recent git history" "blocker" \
      ".git" "0" "${GIT_SECRETS:0:200}" "Rotate all exposed secrets. Rewrite git history."
  fi
fi

# ─── Build JSON report ─────────────────────────────────────────────────────────
log ""
log "Building report..."

VERDICT="PASS"
if [ "$BLOCKER_COUNT" -gt 0 ]; then
  VERDICT="FAIL"
elif [ "$WARNING_COUNT" -gt 0 ]; then
  VERDICT="WARN"
fi

# Convert newline-delimited findings to JSON array
python3 << PYEOF
import json, sys

findings = []
try:
    with open("$FINDINGS_FILE") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    findings.append(json.loads(line))
                except:
                    pass
except:
    pass

report = {
    "project": "$PROJECT",
    "scanner": "wreckit-red-team",
    "findings": findings,
    "summary": {
        "total": len(findings),
        "blockers": $BLOCKER_COUNT,
        "warnings": $WARNING_COUNT,
        "info": $INFO_COUNT
    },
    "verdict": "$VERDICT"
}

hardcoded_ids = {
    "HARDCODED_PASSWORD",
    "HARDCODED_SECRET",
    "HARDCODED_AWS",
    "HARDCODED_JWT_SECRET",
    "ENV_COMMITTED",
    "KEY_COMMITTED",
    "GIT_HISTORY_SECRETS",
}
hardcoded_found = any(f.get("id") in hardcoded_ids for f in findings)
if hardcoded_found:
    confidence = 1.0
elif len(findings) > 0:
    confidence = 0.7
else:
    confidence = 0.0

report["status"] = "$VERDICT"
report["confidence"] = confidence
report["hardcoded_secrets"] = hardcoded_found

print(json.dumps(report, indent=2))
PYEOF

# Cleanup
rm -f "$FINDINGS_FILE"

# Print summary to stderr
echo "" >&2
echo "Results:" >&2
echo "  Total findings: $FINDING_COUNT" >&2
echo "  Blockers: $BLOCKER_COUNT" >&2
echo "  Warnings: $WARNING_COUNT" >&2
echo "  Info: $INFO_COUNT" >&2
echo "  Verdict: $VERDICT" >&2
