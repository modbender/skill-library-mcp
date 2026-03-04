#!/bin/bash
# Security scanner for Postman collections and environments
# Detects hardcoded secrets, weak configurations, and security issues

set -e

RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m'

ISSUES_FOUND=0

print_error() {
    echo -e "${RED}[CRITICAL]${NC} $1"
    ((ISSUES_FOUND++))
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_ok() {
    echo -e "${GREEN}[OK]${NC} $1"
}

if [ $# -eq 0 ]; then
    echo "Usage: $0 <collection.json> [environment.json]"
    exit 1
fi

COLLECTION="$1"
ENVIRONMENT="${2:-}"

echo "🔒 Newman Security Audit"
echo "======================="
echo ""

# Check collection file
if [ ! -f "$COLLECTION" ]; then
    print_error "Collection file not found: $COLLECTION"
    exit 1
fi

echo "Scanning: $COLLECTION"
if [ -n "$ENVIRONMENT" ] && [ -f "$ENVIRONMENT" ]; then
    echo "Environment: $ENVIRONMENT"
fi
echo ""

# 1. Check for hardcoded API keys/tokens
echo "[1/8] Checking for hardcoded secrets..."
if grep -qiE '"(apikey|api_key|token|password|secret)"[[:space:]]*:[[:space:]]*"[a-zA-Z0-9_-]{8,}"' "$COLLECTION"; then
    print_error "Hardcoded secrets detected in collection!"
    echo "       Found in lines:"
    grep -niE '"(apikey|api_key|token|password|secret)"[[:space:]]*:[[:space:]]*"[a-zA-Z0-9_-]{8,}"' "$COLLECTION" | head -5
else
    print_ok "No hardcoded secrets found"
fi

# 2. Check for Basic Auth credentials
echo "[2/8] Checking for Basic Auth credentials..."
if grep -qiE '"username"[[:space:]]*:[[:space:]]*"[^{]' "$COLLECTION"; then
    print_warning "Basic Auth credentials found (ensure they use variables)"
    grep -niE '"username"[[:space:]]*:[[:space:]]*"[^{]' "$COLLECTION" | head -3
else
    print_ok "No hardcoded Basic Auth found"
fi

# 3. Check for insecure HTTP URLs
echo "[3/8] Checking for insecure HTTP URLs..."
if grep -qE '"url"[[:space:]]*:[[:space:]]*"http://' "$COLLECTION"; then
    print_warning "HTTP (non-HTTPS) URLs detected!"
    grep -nE '"url"[[:space:]]*:[[:space:]]*"http://' "$COLLECTION" | head -5
else
    print_ok "All URLs use HTTPS"
fi

# 4. Check SSL verification settings
echo "[4/8] Checking SSL verification settings..."
if grep -qiE '"disableStrictSSL"[[:space:]]*:[[:space:]]*true' "$COLLECTION"; then
    print_error "SSL verification is disabled!"
    echo "       This is a critical security risk in production."
else
    print_ok "SSL verification enabled"
fi

# 5. Check for exposed PII patterns
echo "[5/8] Checking for potential PII exposure..."
if grep -qiE '"(ssn|social_security|credit_card|passport)"[[:space:]]*:[[:space:]]*"[0-9]' "$COLLECTION"; then
    print_error "Potential PII data found in collection!"
else
    print_ok "No obvious PII patterns detected"
fi

# 6. Check environment file (if provided)
if [ -n "$ENVIRONMENT" ] && [ -f "$ENVIRONMENT" ]; then
    echo "[6/8] Checking environment file..."
    
    # Check for secrets in environment
    if grep -qiE '"(password|secret|apikey)"[[:space:]]*:[[:space:]]*"[a-zA-Z0-9_-]{8,}"' "$ENVIRONMENT"; then
        print_error "Hardcoded secrets in environment file!"
        echo "       Use {{$processEnvironment.VAR_NAME}} instead"
    fi
    
    # Check for production credentials
    if grep -qiE '"BASE_URL"[[:space:]]*:[[:space:]]*"https?://.*production' "$ENVIRONMENT"; then
        print_warning "Production URL detected in environment file"
        echo "       Ensure this file is not committed to public repositories"
    fi
else
    echo "[6/8] Skipping environment check (no file provided)"
fi

# 7. Check for variable usage best practices
echo "[7/8] Checking variable usage..."
VAR_COUNT=$(grep -oE '\{\{[^}]+\}\}' "$COLLECTION" | wc -l)
if [ "$VAR_COUNT" -lt 3 ]; then
    print_warning "Low variable usage detected (found: $VAR_COUNT)"
    echo "       Consider using variables for URLs, auth, and common values"
else
    print_ok "Good variable usage (found: $VAR_COUNT variables)"
fi

# 8. Check for timeout configurations
echo "[8/8] Checking timeout configurations..."
if ! grep -qE '"timeout"[[:space:]]*:[[:space:]]*[0-9]+' "$COLLECTION"; then
    print_warning "No timeout configuration found"
    echo "       Set timeouts to prevent hanging requests"
else
    print_ok "Timeout configuration present"
fi

echo ""
echo "======================="

if [ $ISSUES_FOUND -gt 0 ]; then
    echo -e "${RED}❌ Security audit failed: $ISSUES_FOUND critical issue(s) found${NC}"
    echo ""
    echo "Recommendations:"
    echo "1. Remove all hardcoded secrets"
    echo "2. Use environment variables: {{$processEnvironment.VAR_NAME}}"
    echo "3. Enable SSL verification in production"
    echo "4. Use HTTPS for all endpoints"
    echo "5. Store sensitive environments in secure vaults"
    exit 1
else
    echo -e "${GREEN}✅ Security audit passed!${NC}"
    exit 0
fi
