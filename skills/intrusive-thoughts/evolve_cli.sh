#!/bin/bash
# 🧬 Evolution CLI - Easy access to the self-evolving learning system

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
EVOLUTION_SCRIPT="$SCRIPT_DIR/self_evolution.py"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

usage() {
    echo -e "${CYAN}🧬 Evolution CLI - Self-Learning System${NC}"
    echo
    echo "Usage: $0 <command>"
    echo
    echo -e "${GREEN}Available commands:${NC}"
    echo "  run          - Run full evolution cycle (analyze → learn → adjust)"
    echo "  reflect      - Generate text reflection on recent patterns"
    echo "  diagnose     - Identify current problems and issues"
    echo "  recommendations - Get actionable suggestions"
    echo "  weights      - Show learned weight adjustments"
    echo "  history      - Show evolution history"
    echo "  stats        - Show evolution statistics"
    echo "  status       - Quick status check"
    echo
    echo -e "${YELLOW}Examples:${NC}"
    echo "  $0 run                    # Run full learning cycle"
    echo "  $0 reflect               # Get self-reflection summary"
    echo "  $0 weights               # See current weight adjustments"
    echo
}

ensure_evolution_system() {
    if [[ ! -f "$EVOLUTION_SCRIPT" ]]; then
        echo -e "${RED}Error: Evolution system not found at $EVOLUTION_SCRIPT${NC}"
        exit 1
    fi
    
    # Make sure it's executable
    chmod +x "$EVOLUTION_SCRIPT"
}

run_with_header() {
    local command="$1"
    local header="$2"
    local color="$3"
    
    echo -e "${color}${header}${NC}"
    python3 "$EVOLUTION_SCRIPT" "$command"
}

quick_status() {
    echo -e "${CYAN}🧬 EVOLUTION SYSTEM STATUS${NC}"
    echo "================================"
    
    if [[ ! -d "$SCRIPT_DIR/evolution" ]]; then
        echo -e "${YELLOW}⚠️ Evolution directory not found - system not initialized${NC}"
        echo -e "${GREEN}💡 Run: $0 run${NC}"
        return
    fi
    
    local learnings_file="$SCRIPT_DIR/evolution/learnings.json"
    local weights_file="$SCRIPT_DIR/evolution/learned_weights.json"
    
    if [[ -f "$learnings_file" ]]; then
        local last_evolution
        last_evolution=$(python3 -c "
import json
try:
    data = json.load(open('$learnings_file'))
    print(data.get('last_evolution', 'Never')[:10])
except:
    print('Never')
")
        
        local pattern_count
        pattern_count=$(python3 -c "
import json
try:
    data = json.load(open('$learnings_file'))
    print(len(data.get('patterns', [])))
except:
    print(0)
")
        
        echo -e "${GREEN}✅ Evolution system active${NC}"
        echo "📅 Last evolution: $last_evolution"
        echo "🧠 Patterns learned: $pattern_count"
        
        if [[ -f "$weights_file" ]]; then
            local mood_weights
            mood_weights=$(python3 -c "
import json
try:
    data = json.load(open('$weights_file'))
    print(len(data.get('moods', {})))
except:
    print(0)
")
            echo "⚖️ Active mood adjustments: $mood_weights"
        fi
    else
        echo -e "${YELLOW}⚠️ No evolution data found - run first cycle${NC}"
        echo -e "${GREEN}💡 Run: $0 run${NC}"
    fi
}

show_history() {
    local learnings_file="$SCRIPT_DIR/evolution/learnings.json"
    
    if [[ ! -f "$learnings_file" ]]; then
        echo -e "${RED}No evolution history found${NC}"
        return 1
    fi
    
    echo -e "${PURPLE}📜 EVOLUTION HISTORY${NC}"
    echo "==================="
    
    python3 -c "
import json
from datetime import datetime

try:
    with open('$learnings_file') as f:
        data = json.load(f)
    
    history = data.get('evolution_history', [])
    
    if not history:
        print('No evolution cycles run yet')
        exit()
    
    print(f'Total evolution cycles: {len(history)}\n')
    
    # Show last 5 cycles
    for event in history[-5:]:
        timestamp = event['timestamp'][:16].replace('T', ' ')
        print(f'🗓️ {timestamp}')
        print(f'   📈 {event[\"new_patterns_discovered\"]} new patterns discovered')
        print(f'   ⚖️ {event[\"weight_adjustments_made\"]} weight adjustments made')
        print(f'   ⚠️ {event[\"ruts_detected\"]} behavioral ruts detected')
        print()
        
except Exception as e:
    print(f'Error reading history: {e}')
"
}

main() {
    ensure_evolution_system
    
    if [[ $# -eq 0 ]]; then
        usage
        exit 1
    fi
    
    local command="$1"
    
    case "$command" in
        "run"|"evolve")
            run_with_header "evolve" "🚀 RUNNING EVOLUTION CYCLE" "$GREEN"
            ;;
        "reflect"|"reflection")
            run_with_header "reflect" "🤔 SELF-REFLECTION" "$BLUE"
            ;;
        "diagnose"|"diagnosis")
            run_with_header "diagnose" "🔍 SYSTEM DIAGNOSIS" "$YELLOW"
            ;;
        "recommendations"|"recommend"|"prescribe")
            run_with_header "recommendations" "💊 RECOMMENDATIONS" "$GREEN"
            ;;
        "weights"|"weight")
            run_with_header "weights" "⚖️ LEARNED WEIGHTS" "$PURPLE"
            ;;
        "stats"|"statistics")
            run_with_header "stats" "📊 EVOLUTION STATISTICS" "$CYAN"
            ;;
        "history"|"log")
            show_history
            ;;
        "status"|"check")
            quick_status
            ;;
        "help"|"-h"|"--help")
            usage
            ;;
        *)
            echo -e "${RED}Unknown command: $command${NC}"
            echo
            usage
            exit 1
            ;;
    esac
}

main "$@"