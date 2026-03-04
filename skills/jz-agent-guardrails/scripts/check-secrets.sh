#!/bin/bash
# check-secrets.sh — Scan files for hardcoded secrets
# Usage: bash check-secrets.sh [directory_or_file]
# Returns exit code 1 if secrets found, 0 if clean.

set -euo pipefail

TARGET="${1:-.}"
ERRORS=0

echo "🔐 Scanning for hardcoded secrets..."
echo "  Target: $TARGET"
echo ""

# Determine files to scan
if [ -f "$TARGET" ]; then
    FILES="$TARGET"
elif [ -d "$TARGET" ]; then
    FILES=$(find "$TARGET" -type f \( -name "*.py" -o -name "*.sh" -o -name "*.js" -o -name "*.ts" -o -name "*.yaml" -o -name "*.yml" -o -name "*.json" -o -name "*.env" -o -name "*.toml" -o -name "*.cfg" -o -name "*.ini" \) \
        -not -path "*/.git/*" -not -path "*/node_modules/*" -not -path "*/__pycache__/*" -not -path "*/venv/*" 2>/dev/null || true)
else
    echo "❌ Target not found: $TARGET"
    exit 1
fi

if [ -z "$FILES" ]; then
    echo "ℹ️  No scannable files found."
    exit 0
fi

# Secret patterns (PCRE)
SECRET_PATTERNS=(
    'token\s*=\s*["\x27][A-Za-z0-9_\-]{20,}'
    'api_key\s*=\s*["\x27][A-Za-z0-9_\-]{20,}'
    'secret\s*=\s*["\x27][A-Za-z0-9_\-]{20,}'
    'password\s*=\s*["\x27][^\x27"]{8,}'
    'Bearer [A-Za-z0-9_\-]{20,}'
    'sk-[A-Za-z0-9]{20,}'
    'ghp_[A-Za-z0-9]{20,}'
    'xoxb-[A-Za-z0-9\-]{20,}'
    'AKIA[0-9A-Z]{16}'
    'eyJ[A-Za-z0-9_\-]{20,}\.[A-Za-z0-9_\-]{20,}'
)

for pattern in "${SECRET_PATTERNS[@]}"; do
    while IFS= read -r file; do
        [ -z "$file" ] && continue
        MATCH=$(grep -Pn "$pattern" "$file" 2>/dev/null || true)
        if [ -n "$MATCH" ]; then
            echo "  🚨 POSSIBLE SECRET in $file:"
            echo "$MATCH" | head -3 | sed 's/^/     /'
            ERRORS=$((ERRORS + 1))
        fi
    done <<< "$FILES"
done

# Check for os.getenv with suspicious defaults
while IFS= read -r file; do
    [ -z "$file" ] && continue
    [[ "$file" != *.py ]] && continue
    MATCH=$(grep -n 'os\.getenv.*,.*["\x27]' "$file" 2>/dev/null | grep -iv 'default\|localhost\|http\|utf\|\.json\|\.txt\|\.log' || true)
    if [ -n "$MATCH" ]; then
        echo "  ⚠️  os.getenv() with fallback in $file:"
        echo "$MATCH" | head -3 | sed 's/^/     /'
        ERRORS=$((ERRORS + 1))
    fi
done <<< "$FILES"

# OWASP Injection Detection
echo "🧪 Checking for OWASP injection patterns..."

# SQL injection: string concatenation in SQL queries (not URLs)
while IFS= read -r file; do
    [ -z "$file" ] && continue
    [[ "$file" =~ \.(py|js|ts|go|java|rb)$ ]] || continue
    MATCH=$(grep -n "\.execute\|cursor\|SELECT\|INSERT\|UPDATE\|DELETE" "$file" 2>/dev/null | \
        grep -i "f\"\|format(\|%s\|sprintf\|+ \"\|concat" | \
        grep -iv "parameterized\|placeholder\|prepared\|https\|http" || true)
    if [ -n "$MATCH" ]; then
        echo "  ⚠️  SQL injection risk in $file:"
        echo "$MATCH" | head -3 | sed 's/^/     /'
        ERRORS=$((ERRORS + 1))
    fi
done <<< "$FILES"

# Command injection: user input in shell commands
while IFS= read -r file; do
    [ -z "$file" ] && continue
    [[ "$file" =~ \.(py|js|ts|go|java|rb)$ ]] || continue
    MATCH=$(grep -n "exec(\|spawn(\|system(\|popen(\|subprocess\|os\.system\|child_process" "$file" 2>/dev/null | \
        grep -i "f\"\|format(\|%s\|sprintf\|\${\|+ \"\|concat" || true)
    if [ -n "$MATCH" ]; then
        echo "  ⚠️  Command injection risk in $file:"
        echo "$MATCH" | head -3 | sed 's/^/     /'
        ERRORS=$((ERRORS + 1))
    fi
done <<< "$FILES"

# Dependency vulnerability check
echo "🔍 Checking dependency vulnerabilities..."

# npm audit (if package.json exists)
if [ -f "package.json" ] && command -v npm >/dev/null 2>&1; then
    echo "   Running npm audit..."
    NPM_RESULT=$(npm audit --audit-level=high --json 2>/dev/null || echo '{"vulnerabilities":{}}')
    HIGH_VULNS=$(echo "$NPM_RESULT" | grep -o '"severity":"high"\|"severity":"critical"' | wc -l)
    if [ "$HIGH_VULNS" -gt 0 ]; then
        echo "  🚨 npm audit found $HIGH_VULNS high/critical vulnerabilities"
        ERRORS=$((ERRORS + 1))
    else
        echo "  ✅ npm audit: no high/critical vulnerabilities"
    fi
elif [ -f "package.json" ]; then
    echo "  ⚠️  package.json found but npm not available"
fi

# pip-audit (if requirements.txt exists or venv detected)
if ([ -f "requirements.txt" ] || [ -f "pyproject.toml" ] || [ -d "venv" ]) && command -v pip-audit >/dev/null 2>&1; then
    echo "   Running pip-audit..."
    if pip-audit --format json >/dev/null 2>&1; then
        echo "  ✅ pip-audit: no known vulnerabilities"
    else
        echo "  🚨 pip-audit found vulnerabilities"
        ERRORS=$((ERRORS + 1))
    fi
elif [ -f "requirements.txt" ] || [ -f "pyproject.toml" ]; then
    echo "  ⚠️  Python project detected but pip-audit not available"
fi

# .gitignore audit
echo "🗂️  Checking .gitignore coverage..."

if [ ! -f ".gitignore" ]; then
    echo "  ⚠️  No .gitignore file found"
    ERRORS=$((ERRORS + 1))
else
    MISSING_PATTERNS=()
    for pattern in '.env' '.env.*' '*.key' '*.pem' '*.p12' '*.pfx' 'id_rsa' 'id_ed25519' 'credentials.json'; do
        if ! grep -q "$pattern" .gitignore 2>/dev/null; then
            MISSING_PATTERNS+=("$pattern")
        fi
    done
    
    if [ ${#MISSING_PATTERNS[@]} -gt 0 ]; then
        echo "  ⚠️  .gitignore missing sensitive patterns: ${MISSING_PATTERNS[*]}"
        ERRORS=$((ERRORS + 1))
    else
        echo "  ✅ .gitignore has common sensitive patterns"
    fi
fi

# Check if sensitive files are tracked in git
if [ -d ".git" ]; then
    TRACKED_SENSITIVE=()
    for pattern in '.env' '.env.*' '*.pem' '*.key' '*.p12' '*.pfx' 'credentials.json' 'service-account*.json' '*.keystore' 'id_rsa' 'id_ed25519'; do
        FOUND=$(git ls-files "$pattern" 2>/dev/null || true)
        if [ -n "$FOUND" ]; then
            TRACKED_SENSITIVE+=("$FOUND")
        fi
    done
    
    if [ ${#TRACKED_SENSITIVE[@]} -gt 0 ]; then
        echo "  🚨 Sensitive files tracked in git: ${TRACKED_SENSITIVE[*]}"
        ERRORS=$((ERRORS + 1))
    else
        echo "  ✅ No sensitive files tracked in git"
    fi
fi

echo ""
if [ "$ERRORS" -gt 0 ]; then
    echo "╔══════════════════════════════════════════════════╗"
    echo "║  🚨 $ERRORS security issue(s) found!                 ║"
    echo "║  Fix before committing changes.                  ║"
    echo "╚══════════════════════════════════════════════════╝"
    exit 1
else
    echo "╔══════════════════════════════════════════════════╗"
    echo "║  ✅ Security scan passed                         ║"
    echo "╚══════════════════════════════════════════════════╝"
    exit 0
fi
