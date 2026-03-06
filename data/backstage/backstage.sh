#!/bin/bash
# backstage.sh - Minimal orchestrator for backstage protocol
# All intelligence lives in checks/

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Run all checks
run_enforcement() {
    local script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    
    if bash "$script_dir/checks.sh" "." "start"; then
        return 0
    else
        return 1
    fi
}

# Prompt user
prompt_push() {
    echo -e "\n${BLUE}🚦 Pre-Push Validation:${NC}"
    echo -e "${GREEN}✅ All checks passed${NC}"
    echo -e "\n${GREEN}🚦 Status: SAFE TO PUSH${NC}"
    
    read -p "Ready to commit and push? (y/n): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${GREEN}✅ Proceeding with commit${NC}"
        return 0
    else
        echo -e "${YELLOW}⏸️  Paused - no commit${NC}"
        return 1
    fi
}

# Main
main() {
    echo -e "${BLUE}╔════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║  Backstage - Pre-commit Check     ║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════╝${NC}\n"
    
    # Run all checks (checks.sh handles everything)
    if ! run_enforcement; then
        echo -e "\n${RED}❌ Checks failed - fix issues above${NC}"
        exit 1
    fi
    
    # Prompt user
    if prompt_push; then
        echo -e "${GREEN}✅ Ready for git commit${NC}"
    fi
    
    echo -e "\n${GREEN}✅ Backstage complete${NC}"
}

main "$@"
