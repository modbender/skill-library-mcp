#!/bin/bash
# Secret Scanner — detect accidentally committed secrets
# Usage: bash secret-scan.sh [directory]
# Exit 0 = clean, Exit 1 = secrets found

set -euo pipefail

TARGET="${1:-$HOME/.openclaw/workspace}"
FOUND=0

echo "🔍 Scanning for secrets in: $TARGET"
echo "─────────────────────────────────────"

# Patterns to search for
declare -a PATTERNS=(
    'sk-[a-zA-Z0-9]{20,}'           # OpenAI keys
    'sk-ant-[a-zA-Z0-9]{20,}'       # Anthropic keys  
    'am_[a-f0-9]{40,}'              # AgentMail keys
    'ghp_[a-zA-Z0-9]{36}'           # GitHub PATs
    'gho_[a-zA-Z0-9]{36}'           # GitHub OAuth
    'glpat-[a-zA-Z0-9\-]{20,}'     # GitLab PATs
    'xox[bporas]-[a-zA-Z0-9\-]+'   # Slack tokens
    'AKIA[0-9A-Z]{16}'             # AWS access keys
    'AIza[0-9A-Za-z\-_]{35}'       # Google API keys
    'pk_live_[a-zA-Z0-9]+'         # Stripe live keys
    'sk_live_[a-zA-Z0-9]+'         # Stripe secret keys
    'discord\.[a-zA-Z0-9_-]{24}\.[a-zA-Z0-9_-]{6}\.[a-zA-Z0-9_-]{27}' # Discord tokens
)

declare -a DESCRIPTIONS=(
    "OpenAI API key"
    "Anthropic API key"
    "AgentMail API key"
    "GitHub PAT"
    "GitHub OAuth token"
    "GitLab PAT"
    "Slack token"
    "AWS access key"
    "Google API key"
    "Stripe live key"
    "Stripe secret key"
    "Discord token"
)

# Files to skip
EXCLUDE="--exclude-dir=node_modules --exclude-dir=.git --exclude-dir=__pycache__ --exclude=*.jsonl --exclude=*.log --exclude=secret-scan.sh --exclude=auth-profiles.json"

for i in "${!PATTERNS[@]}"; do
    pattern="${PATTERNS[$i]}"
    desc="${DESCRIPTIONS[$i]}"
    
    # Search, suppressing errors
    matches=$(grep -rn $EXCLUDE -E "$pattern" "$TARGET" 2>/dev/null || true)
    
    if [ -n "$matches" ]; then
        echo "⚠️  Possible $desc found:"
        echo "$matches" | head -5 | while read -r line; do
            # Mask the actual secret value
            file=$(echo "$line" | cut -d: -f1)
            lineno=$(echo "$line" | cut -d: -f2)
            echo "   📄 $file:$lineno"
        done
        count=$(echo "$matches" | wc -l | tr -d ' ')
        if [ "$count" -gt 5 ]; then
            echo "   ... and $((count - 5)) more"
        fi
        echo ""
        FOUND=1
    fi
done

# Check for common secret file patterns
echo "📁 Checking for sensitive files..."
sensitive_files=$(find "$TARGET" -maxdepth 4 \
    \( -name ".env" -o -name ".env.local" -o -name "*.pem" -o -name "*.key" \
    -o -name "id_rsa" -o -name "id_ed25519" -o -name "credentials.json" \) \
    -not -path "*/node_modules/*" -not -path "*/.git/*" 2>/dev/null || true)

if [ -n "$sensitive_files" ]; then
    echo "⚠️  Sensitive files found:"
    echo "$sensitive_files" | while read -r f; do
        echo "   📄 $f"
    done
    echo ""
    FOUND=1
fi

echo "─────────────────────────────────────"
if [ "$FOUND" -eq 1 ]; then
    echo "🔴 Secrets detected — review and clean up!"
    exit 1
else
    echo "✅ No secrets found — workspace is clean"
    exit 0
fi
