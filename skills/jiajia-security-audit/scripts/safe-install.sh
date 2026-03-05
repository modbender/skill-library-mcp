#!/usr/bin/env bash
# Safe Skill Install - 安装前强制安全审计
# Usage: safe-install.sh <skill-slug> [clawdhub options...]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AUDIT_SCRIPT="$SCRIPT_DIR/audit.sh"
WORKDIR="${CLAWDHUB_WORKDIR:-$(pwd)}"
SKILLS_DIR="$WORKDIR/skills"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m'

usage() {
    echo "Usage: $0 <skill-slug> [--version X.Y.Z] [--force] [--skip-audit]"
    echo ""
    echo "Options:"
    echo "  --version X.Y.Z   Install specific version"
    echo "  --force           Force install even with security warnings (HIGH/MEDIUM)"
    echo "  --skip-audit      Skip security audit entirely (not recommended)"
    echo "  --allow-critical  Allow install even with CRITICAL issues (dangerous!)"
    echo ""
    echo "Environment:"
    echo "  CLAWDHUB_WORKDIR  Working directory (default: cwd)"
    exit 1
}

if [[ $# -lt 1 ]]; then
    usage
fi

SKILL_SLUG="$1"
shift

# Parse options
FORCE=false
SKIP_AUDIT=false
ALLOW_CRITICAL=false
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
        --allow-critical)
            ALLOW_CRITICAL=true
            shift
            ;;
        *)
            CLAWDHUB_OPTS+=("$1")
            shift
            ;;
    esac
done

echo -e "${BLUE}📦 Installing skill: $SKILL_SLUG${NC}"

# Create temp directory for staging
TEMP_DIR=$(mktemp -d)
TEMP_SKILLS="$TEMP_DIR/skills"
mkdir -p "$TEMP_SKILLS"

cleanup() {
    rm -rf "$TEMP_DIR"
}
trap cleanup EXIT

# Step 1: Download to temp directory
echo -e "${BLUE}⬇️  Downloading to staging area...${NC}"
if ! clawdhub install "$SKILL_SLUG" --workdir "$TEMP_DIR" "${CLAWDHUB_OPTS[@]}" 2>&1; then
    echo -e "${RED}❌ Failed to download skill${NC}"
    exit 1
fi

SKILL_PATH="$TEMP_SKILLS/$SKILL_SLUG"

if [[ ! -d "$SKILL_PATH" ]]; then
    echo -e "${RED}❌ Skill not found at $SKILL_PATH${NC}"
    exit 1
fi

# Step 2: Security audit
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
    
    # Check results
    if [[ "$CRITICAL" -gt 0 ]]; then
        echo -e "${RED}🚨 CRITICAL security issues found!${NC}"
        if ! $ALLOW_CRITICAL; then
            echo -e "${RED}❌ Installation blocked. Use --allow-critical to override (dangerous!)${NC}"
            exit 1
        else
            echo -e "${YELLOW}⚠️  Proceeding despite CRITICAL issues (--allow-critical)${NC}"
        fi
    fi
    
    if [[ "$HIGH" -gt 0 || "$MEDIUM" -gt 0 ]]; then
        echo -e "${YELLOW}⚠️  Security warnings found (HIGH: $HIGH, MEDIUM: $MEDIUM)${NC}"
        if ! $FORCE; then
            echo -e "${YELLOW}Use --force to install anyway${NC}"
            read -p "Continue with installation? [y/N] " -n 1 -r
            echo
            if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                echo -e "${RED}❌ Installation cancelled${NC}"
                exit 1
            fi
        fi
    fi
    
    if [[ "$CRITICAL" -eq 0 && "$HIGH" -eq 0 && "$MEDIUM" -eq 0 ]]; then
        echo -e "${GREEN}✅ Security audit passed!${NC}"
    fi
fi

# Step 3: Move to final location
echo -e "${BLUE}📁 Installing to $SKILLS_DIR/$SKILL_SLUG${NC}"

# Remove existing if present
if [[ -d "$SKILLS_DIR/$SKILL_SLUG" ]]; then
    echo -e "${YELLOW}Replacing existing installation...${NC}"
    rm -rf "$SKILLS_DIR/$SKILL_SLUG"
fi

mv "$SKILL_PATH" "$SKILLS_DIR/"

# Copy lockfile entry if exists
if [[ -f "$TEMP_DIR/clawdhub-lock.json" ]]; then
    if [[ -f "$WORKDIR/clawdhub-lock.json" ]]; then
        # Merge lockfile entries
        jq -s '.[0] * .[1]' "$WORKDIR/clawdhub-lock.json" "$TEMP_DIR/clawdhub-lock.json" > "$WORKDIR/clawdhub-lock.json.tmp"
        mv "$WORKDIR/clawdhub-lock.json.tmp" "$WORKDIR/clawdhub-lock.json"
    else
        cp "$TEMP_DIR/clawdhub-lock.json" "$WORKDIR/"
    fi
fi

echo -e "${GREEN}✅ Successfully installed $SKILL_SLUG${NC}"
