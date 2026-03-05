#!/bin/bash
# Skill Auditor v2.0.0 - Benchmark
# Run the auditor against a corpus of skills and report aggregate stats
# Usage: bash benchmark.sh [skills-directory] [--json]

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
AUDIT="$SCRIPT_DIR/audit.sh"
TRUST="$SCRIPT_DIR/trust_score.py"

SKILLS_DIR="${1:-$(dirname "$SCRIPT_DIR")}"
JSON_MODE=false
[ "$2" = "--json" ] && JSON_MODE=true

RED='\033[0;31m'; YELLOW='\033[1;33m'; GREEN='\033[0;32m'; BLUE='\033[0;34m'; NC='\033[0m'

TOTAL=0
PASS=0
REVIEW=0
FAIL=0
ERRORS=0
TOTAL_SCORE=0
RESULTS=""

for skill_dir in "$SKILLS_DIR"/*/; do
    [ ! -d "$skill_dir" ] && continue
    skill_name=$(basename "$skill_dir")
    
    # Skip hidden dirs
    [[ "$skill_name" == .* ]] && continue
    
    ((TOTAL++))
    
    RESULT=$(bash "$AUDIT" "$skill_dir" --json 2>/dev/null)
    VERDICT=$(echo "$RESULT" | python3 -c "import json,sys;print(json.load(sys.stdin).get('verdict','error'))" 2>/dev/null)
    CRITS=$(echo "$RESULT" | python3 -c "import json,sys;print(json.load(sys.stdin).get('criticals',0))" 2>/dev/null)
    WARNS=$(echo "$RESULT" | python3 -c "import json,sys;print(json.load(sys.stdin).get('warnings',0))" 2>/dev/null)
    
    SCORE=$(python3 "$TRUST" "$skill_dir" --json 2>/dev/null | python3 -c "import json,sys;print(json.load(sys.stdin).get('trust_score',0))" 2>/dev/null)
    SCORE=${SCORE:-0}
    TOTAL_SCORE=$((TOTAL_SCORE + SCORE))
    
    case "$VERDICT" in
        pass) ((PASS++)) ;;
        review) ((REVIEW++)) ;;
        fail) ((FAIL++)) ;;
        *) ((ERRORS++)) ;;
    esac
    
    if [ -n "$RESULTS" ]; then RESULTS="$RESULTS,"; fi
    RESULTS="${RESULTS}{\"skill\":\"$skill_name\",\"verdict\":\"$VERDICT\",\"criticals\":$CRITS,\"warnings\":$WARNS,\"trust_score\":$SCORE}"
    
    if ! $JSON_MODE; then
        case "$VERDICT" in
            pass) echo -e "${GREEN}✓${NC} $skill_name (score: $SCORE, ${GREEN}PASS${NC})" ;;
            review) echo -e "${YELLOW}⚠${NC} $skill_name (score: $SCORE, ${YELLOW}REVIEW${NC} - ${CRITS}C/${WARNS}W)" ;;
            fail) echo -e "${RED}✗${NC} $skill_name (score: $SCORE, ${RED}FAIL${NC} - ${CRITS}C/${WARNS}W)" ;;
            *) echo -e "${RED}?${NC} $skill_name (error)" ;;
        esac
    fi
done

AVG_SCORE=0
[ $TOTAL -gt 0 ] && AVG_SCORE=$((TOTAL_SCORE / TOTAL))

if $JSON_MODE; then
    echo "{\"total\":$TOTAL,\"pass\":$PASS,\"review\":$REVIEW,\"fail\":$FAIL,\"errors\":$ERRORS,\"avg_trust_score\":$AVG_SCORE,\"skills\":[$RESULTS]}"
else
    echo ""
    echo "========================================="
    echo "  Benchmark Results"
    echo "========================================="
    echo -e "  Total skills:   $TOTAL"
    echo -e "  Pass:           ${GREEN}$PASS${NC}"
    echo -e "  Review:         ${YELLOW}$REVIEW${NC}"
    echo -e "  Fail:           ${RED}$FAIL${NC}"
    echo -e "  Errors:         $ERRORS"
    echo -e "  Avg trust score: $AVG_SCORE/100"
    echo ""
    PASS_RATE=0
    [ $TOTAL -gt 0 ] && PASS_RATE=$(( (PASS * 100) / TOTAL ))
    echo "  Pass rate: ${PASS_RATE}%"
fi
