#!/bin/bash
# Trust & Escalation System CLI
# Provides convenient interface to the trust system

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

usage() {
    echo "Trust & Escalation System CLI"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo
    echo "Usage: $0 COMMAND [OPTIONS]"
    echo
    echo "Commands:"
    echo "  check DESCRIPTION --category CATEGORY [--risk LEVEL]"
    echo "      Check if an action should be escalated"
    echo "      Categories: file_operations, messaging, external_api, system_changes, web_operations, code_execution"
    echo "      Risk levels: low, medium, high, critical (auto-detected if not specified)"
    echo
    echo "  log-success DESCRIPTION --category CATEGORY"
    echo "      Log a successful action"
    echo
    echo "  log-failure DESCRIPTION --category CATEGORY [--details DETAILS]"
    echo "      Log a failed action"
    echo
    echo "  log-escalation DESCRIPTION --category CATEGORY --response \"HUMAN_RESPONSE\""
    echo "      Log an escalation and human response"
    echo
    echo "  stats"
    echo "      Show trust statistics and category breakdowns"
    echo
    echo "  history [--limit N]"
    echo "      Show recent action history (default: 20 items)"
    echo
    echo "  adjust --category CATEGORY --delta AMOUNT --reason \"REASON\""
    echo "      Manually adjust trust levels (-1.0 to 1.0)"
    echo
    echo "  reset [--confirm]"
    echo "      Reset all trust data to defaults"
    echo
    echo "Examples:"
    echo "  $0 check \"send tweet about project update\" --category messaging --risk high"
    echo "  $0 log-success \"wrote config file\" --category file_operations"
    echo "  $0 log-failure \"API call failed\" --category external_api --details \"timeout error\""
    echo "  $0 stats"
    echo "  $0 history --limit 10"
    echo
}

# Parse command line arguments
COMMAND=""
DESCRIPTION=""
CATEGORY=""
RISK=""
DETAILS=""
RESPONSE=""
LIMIT="20"
DELTA=""
REASON=""
CONFIRM=""

while [[ $# -gt 0 ]]; do
    case $1 in
        check|log-success|log-failure|log-escalation|stats|history|adjust|reset)
            COMMAND="$1"
            shift
            ;;
        --category)
            CATEGORY="$2"
            shift 2
            ;;
        --risk)
            RISK="$2"
            shift 2
            ;;
        --details)
            DETAILS="$2"
            shift 2
            ;;
        --response)
            RESPONSE="$2"
            shift 2
            ;;
        --limit)
            LIMIT="$2"
            shift 2
            ;;
        --delta)
            DELTA="$2"
            shift 2
            ;;
        --reason)
            REASON="$2"
            shift 2
            ;;
        --confirm)
            CONFIRM="yes"
            shift
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            if [[ -z "$DESCRIPTION" && "$COMMAND" != "stats" && "$COMMAND" != "history" && "$COMMAND" != "reset" ]]; then
                DESCRIPTION="$1"
            else
                echo -e "${RED}Unknown option: $1${NC}"
                usage
                exit 1
            fi
            shift
            ;;
    esac
done

# Validate command
if [[ -z "$COMMAND" ]]; then
    echo -e "${RED}Error: No command specified${NC}"
    usage
    exit 1
fi

# Execute commands
case "$COMMAND" in
    "check")
        if [[ -z "$DESCRIPTION" || -z "$CATEGORY" ]]; then
            echo -e "${RED}Error: check requires DESCRIPTION and --category${NC}"
            usage
            exit 1
        fi
        
        echo -e "${BLUE}🔍 Checking action...${NC}"
        echo "Description: $DESCRIPTION"
        echo "Category: $CATEGORY"
        [[ -n "$RISK" ]] && echo "Suggested Risk: $RISK"
        echo
        
        # Create a temporary Python script to handle the check
        python3 -c "
import sys
sys.path.append('$SCRIPT_DIR')
from trust_system import TrustSystem

trust = TrustSystem()
context = {'description': '$DESCRIPTION'}
if '$RISK':
    context['suggested_risk'] = '$RISK'

assessment = trust.get_risk_assessment('$CATEGORY', context)

print(f'Risk Level: {assessment[\"risk_level\"]}')
print(f'Recommendation: {assessment[\"recommendation\"].upper()}')
print(f'Confidence: {assessment[\"confidence\"]:.2f}')
print(f'Category Trust: {assessment[\"category_trust\"]:.2f}')
print(f'Global Trust: {assessment[\"global_trust\"]:.2f}')
if assessment['mood_modifier'] != 0:
    print(f'Mood Modifier: {assessment[\"mood_modifier\"]:+.2f}')
print(f'Reasoning: {assessment[\"reasoning\"]}')

# Color the recommendation
if assessment['recommendation'] == 'escalate':
    print('\n🚨 ESCALATE: Ask for permission before proceeding')
else:
    print('\n✅ PROCEED: Safe to act autonomously')
"
        ;;
        
    "log-success")
        if [[ -z "$DESCRIPTION" || -z "$CATEGORY" ]]; then
            echo -e "${RED}Error: log-success requires DESCRIPTION and --category${NC}"
            usage
            exit 1
        fi
        
        python3 -c "
import sys
sys.path.append('$SCRIPT_DIR')
from trust_system import TrustSystem

trust = TrustSystem()
trust.log_action('$CATEGORY', '$DESCRIPTION', 'success')
print('✅ Success logged: $DESCRIPTION')

# Show updated trust level
stats = trust.get_stats()
print(f'Updated trust - Global: {stats[\"global_trust\"]:.2f}, Category: {stats[\"category_trust\"][\"$CATEGORY\"]:.2f}')
"
        ;;
        
    "log-failure")
        if [[ -z "$DESCRIPTION" || -z "$CATEGORY" ]]; then
            echo -e "${RED}Error: log-failure requires DESCRIPTION and --category${NC}"
            usage
            exit 1
        fi
        
        FULL_DESC="$DESCRIPTION"
        [[ -n "$DETAILS" ]] && FULL_DESC="$DESCRIPTION - $DETAILS"
        
        python3 -c "
import sys
sys.path.append('$SCRIPT_DIR')
from trust_system import TrustSystem

trust = TrustSystem()
trust.log_action('$CATEGORY', '$FULL_DESC', 'failure')
print('❌ Failure logged: $DESCRIPTION')

# Show updated trust level
stats = trust.get_stats()
print(f'Updated trust - Global: {stats[\"global_trust\"]:.2f}, Category: {stats[\"category_trust\"][\"$CATEGORY\"]:.2f}')
"
        ;;
        
    "log-escalation")
        if [[ -z "$DESCRIPTION" || -z "$CATEGORY" || -z "$RESPONSE" ]]; then
            echo -e "${RED}Error: log-escalation requires DESCRIPTION, --category, and --response${NC}"
            usage
            exit 1
        fi
        
        python3 -c "
import sys
sys.path.append('$SCRIPT_DIR')
from trust_system import TrustSystem

trust = TrustSystem()
trust.log_escalation('$CATEGORY', '$DESCRIPTION', '$RESPONSE')
print('⬆️ Escalation logged: $DESCRIPTION')
print('Human response: $RESPONSE')

# Show updated trust level
stats = trust.get_stats()
print(f'Updated trust - Global: {stats[\"global_trust\"]:.2f}, Category: {stats[\"category_trust\"][\"$CATEGORY\"]:.2f}')
"
        ;;
        
    "stats")
        python3 -c "
import sys
sys.path.append('$SCRIPT_DIR')
from trust_system import show_stats
show_stats()
"
        ;;
        
    "history")
        python3 -c "
import sys
sys.path.append('$SCRIPT_DIR')
from trust_system import show_history
show_history($LIMIT)
"
        ;;
        
    "adjust")
        if [[ -z "$CATEGORY" || -z "$DELTA" || -z "$REASON" ]]; then
            echo -e "${RED}Error: adjust requires --category, --delta, and --reason${NC}"
            usage
            exit 1
        fi
        
        # Validate delta is a number between -1.0 and 1.0
        if ! python3 -c "
delta = float('$DELTA')
if not -1.0 <= delta <= 1.0:
    exit(1)
" 2>/dev/null; then
            echo -e "${RED}Error: delta must be a number between -1.0 and 1.0${NC}"
            exit 1
        fi
        
        echo -e "${YELLOW}⚙️ Adjusting trust level...${NC}"
        python3 -c "
import sys
sys.path.append('$SCRIPT_DIR')
from trust_system import TrustSystem

trust = TrustSystem()
old_trust = trust.get_trust_level('$CATEGORY' if '$CATEGORY' != 'global' else None)
trust.adjust_trust('$CATEGORY', float('$DELTA'), '$REASON')
new_trust = trust.get_trust_level('$CATEGORY' if '$CATEGORY' != 'global' else None)

print(f'Trust adjusted: {old_trust:.2f} → {new_trust:.2f} (Δ{float(\"$DELTA\"):+.2f})')
print(f'Reason: $REASON')
"
        ;;
        
    "reset")
        if [[ "$CONFIRM" != "yes" ]]; then
            echo -e "${YELLOW}⚠️  This will reset ALL trust data to defaults!${NC}"
            echo "Use --confirm to proceed: $0 reset --confirm"
            exit 1
        fi
        
        rm -f trust_store/trust_data.json
        mkdir -p trust_store
        echo -e "${GREEN}🔄 Trust data reset to defaults${NC}"
        
        # Show fresh stats
        python3 -c "
import sys
sys.path.append('$SCRIPT_DIR')
from trust_system import show_stats
show_stats()
"
        ;;
        
    *)
        echo -e "${RED}Unknown command: $COMMAND${NC}"
        usage
        exit 1
        ;;
esac