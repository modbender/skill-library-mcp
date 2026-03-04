#!/usr/bin/env bash
# Safe Skill Publish - 发布前强制安全审计
# Usage: safe-publish.sh <skill-path> [clawdhub options...]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AUDIT_SCRIPT="$SCRIPT_DIR/audit.sh"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m'

usage() {
    echo "Usage: $0 <skill-path> [--slug name] [--name \"Display Name\"] [--version X.Y.Z] [--force]"
    echo ""
    echo "Options:"
    echo "  --slug name       Skill slug for registry"
    echo "  --name \"Name\"     Display name"
    echo "  --version X.Y.Z   Version to publish"
    echo "  --changelog \"...\" Changelog message"
    echo "  --force           Force publish even with security warnings"
    echo "  --skip-audit      Skip security audit (not recommended)"
    exit 1
}

if [[ $# -lt 1 ]]; then
    usage
fi

SKILL_PATH="$1"
shift

if [[ ! -d "$SKILL_PATH" ]]; then
    echo -e "${RED}❌ Skill path not found: $SKILL_PATH${NC}"
    exit 1
fi

# Parse options
FORCE=false
SKIP_AUDIT=false
CLAWDHUB_OPTS=()

while [[ $# -gt 0 ]]; do
    case $1 in
        --force)
            FORCE=true
            shift
            ;;
        --skip-audit)
            SKIP_AUDIT=true
            shift
            ;;
        *)
            CLAWDHUB_OPTS+=("$1")
            shift
            ;;
    esac
done

SKILL_NAME=$(basename "$SKILL_PATH")
echo -e "${BLUE}📤 Publishing skill: $SKILL_NAME${NC}"

# Step 1: Security audit
if $SKIP_AUDIT; then
    echo -e "${YELLOW}⚠️  Skipping security audit (--skip-audit)${NC}"
else
    echo -e "${BLUE}🔍 Running security audit...${NC}"
    echo ""
    
    # Run audit and capture output
    AUDIT_OUTPUT=$("$AUDIT_SCRIPT" "$SKILL_PATH" --json 2>&1) || true
    
    # Parse results
    CRITICAL=$(echo "$AUDIT_OUTPUT" | jq -r '.summary.critical // 0' 2>/dev/null || echo "0")
    HIGH=$(echo "$AUDIT_OUTPUT" | jq -r '.summary.high // 0' 2>/dev/null || echo "0")
    MEDIUM=$(echo "$AUDIT_OUTPUT" | jq -r '.summary.medium // 0' 2>/dev/null || echo "0")
    LOW=$(echo "$AUDIT_OUTPUT" | jq -r '.summary.low // 0' 2>/dev/null || echo "0")
    
    # Also show human-readable output
    "$AUDIT_SCRIPT" "$SKILL_PATH" 2>&1 || true
    echo ""
    
    # Block on CRITICAL issues - no override for publishing
    if [[ "$CRITICAL" -gt 0 ]]; then
        echo -e "${RED}🚨 CRITICAL security issues found!${NC}"
        echo -e "${RED}❌ Cannot publish skills with CRITICAL issues.${NC}"
        echo -e "${RED}   Please fix these issues before publishing.${NC}"
        exit 1
    fi
    
    if [[ "$HIGH" -gt 0 ]]; then
        echo -e "${YELLOW}⚠️  HIGH severity issues found ($HIGH)${NC}"
        if ! $FORCE; then
            echo -e "${YELLOW}Publishing with HIGH issues is discouraged.${NC}"
            read -p "Continue anyway? [y/N] " -n 1 -r
            echo
            if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                echo -e "${RED}❌ Publish cancelled${NC}"
                exit 1
            fi
        fi
    fi
    
    if [[ "$MEDIUM" -gt 0 ]]; then
        echo -e "${YELLOW}⚠️  MEDIUM severity issues found ($MEDIUM)${NC}"
        if ! $FORCE; then
            read -p "Continue with publish? [Y/n] " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Nn]$ ]]; then
                echo -e "${RED}❌ Publish cancelled${NC}"
                exit 1
            fi
        fi
    fi
    
    if [[ "$CRITICAL" -eq 0 && "$HIGH" -eq 0 && "$MEDIUM" -eq 0 ]]; then
        echo -e "${GREEN}✅ Security audit passed!${NC}"
    fi
fi

# Step 2: Publish
echo -e "${BLUE}📤 Publishing to ClawdHub...${NC}"
if clawdhub publish "$SKILL_PATH" "${CLAWDHUB_OPTS[@]}"; then
    echo -e "${GREEN}✅ Successfully published $SKILL_NAME${NC}"
else
    echo -e "${RED}❌ Publish failed${NC}"
    exit 1
fi
