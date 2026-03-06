#!/usr/bin/env bash
#
# Clawdhub validation script
# Validates the skill structure before publishing
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

ERRORS=0
WARNINGS=0

log_info() {
    echo -e "${GREEN}✓${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}⚠${NC} $1"
    ((WARNINGS++)) || true
}

log_error() {
    echo -e "${RED}✗${NC} $1"
    ((ERRORS++)) || true
}

echo "Clawdhub Validation"
echo "==================="
echo ""

# Check required files
echo "Checking required files..."
required_files=(
    "README.md"
    "SKILL.md"
    "LICENSE"
    "scripts/cursor-api.sh"
    "skill.json"
)

for file in "${required_files[@]}"; do
    if [[ -f "$file" ]]; then
        log_info "Found $file"
    else
        log_error "Missing required file: $file"
    fi
done
echo ""

# Check script is executable
echo "Checking script permissions..."
if [[ -x "scripts/cursor-api.sh" ]]; then
    log_info "cursor-api.sh is executable"
else
    log_error "cursor-api.sh is not executable (run: chmod +x scripts/cursor-api.sh)"
fi
echo ""

# Check script syntax
echo "Checking script syntax..."
if bash -n scripts/cursor-api.sh 2>/dev/null; then
    log_info "Script syntax is valid"
else
    log_error "Script has syntax errors"
fi
echo ""

# Check for secrets
echo "Checking for secrets..."
found_secret=false
if grep -rE '(password|secret|key|token)\s*=\s*"[a-zA-Z0-9]{20,}"' scripts/ --include="*.sh" 2>/dev/null; then
    found_secret=true
fi

if [[ "$found_secret" == "false" ]]; then
    log_info "No hardcoded secrets found"
else
    log_error "Potential hardcoded secrets found in code"
fi
echo ""

# Check skill.json
echo "Checking skill.json..."
if [[ -f "skill.json" ]]; then
    if jq empty skill.json 2>/dev/null; then
        log_info "skill.json is valid JSON"
        
        # Check required fields
        required_fields=("name" "version" "type" "entryPoint")
        for field in "${required_fields[@]}"; do
            if jq -e ".$field" skill.json >/dev/null 2>&1; then
                log_info "skill.json has $field"
            else
                log_error "skill.json missing required field: $field"
            fi
        done
    else
        log_error "skill.json is not valid JSON"
    fi
else
    log_error "skill.json not found"
fi
echo ""

# Check documentation
echo "Checking documentation..."
if grep -q "## Overview" SKILL.md 2>/dev/null; then
    log_info "SKILL.md has Overview section"
else
    log_warn "SKILL.md missing Overview section"
fi

if grep -q "## Commands" SKILL.md 2>/dev/null || grep -q "## Usage" SKILL.md 2>/dev/null; then
    log_info "SKILL.md has usage documentation"
else
    log_warn "SKILL.md missing usage documentation"
fi

if grep -q "installation" README.md 2>/dev/null || grep -q "## Installation" README.md 2>/dev/null; then
    log_info "README.md has installation instructions"
else
    log_warn "README.md missing installation instructions"
fi
echo ""

# Check test files
echo "Checking tests..."
if [[ -d "tests" ]] && [[ -n "$(ls -A tests/*.bats 2>/dev/null)" ]]; then
    log_info "Test files found"
else
    log_warn "No test files found"
fi
echo ""

# Check CI/CD
echo "Checking CI/CD configuration..."
if [[ -d ".github/workflows" ]]; then
    workflow_count=$(find .github/workflows -name "*.yml" -o -name "*.yaml" | wc -l)
    if [[ $workflow_count -gt 0 ]]; then
        log_info "Found $workflow_count workflow(s)"
    else
        log_warn "No workflow files found"
    fi
else
    log_warn "No .github/workflows directory"
fi
echo ""

# Summary
echo "====================="
if [[ $ERRORS -eq 0 ]]; then
    echo -e "${GREEN}Validation passed!${NC} ($WARNINGS warnings)"
    echo ""
    echo "Ready to publish to clawdhub with:"
    echo "  clawhub publish"
    exit 0
else
    echo -e "${RED}Validation failed!${NC} ($ERRORS errors, $WARNINGS warnings)"
    echo ""
    echo "Please fix the errors above before publishing."
    exit 1
fi
