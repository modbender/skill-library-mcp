#!/bin/bash
# COBRACLAW TEST SUITE

PASS=0
TESTS=0

count_test() {
    TESTS=$((TESTS+1))
    if eval "$1"; then
        PASS=$((PASS+1))
        echo "  OK $2"
    else
        echo "  FAIL $2"
    fi
}

echo "COBRACLAW Tests"

count_test "[ -f SKILL.md ]" "SKILL.md"
count_test "[ -f README.md ]" "README.md"
count_test "[ -f cobraclaw.sh ]" "cobraclaw.sh"
count_test "[ -f test-skill.sh ]" "test-skill.sh"
count_test "[ -f cobra-mode.sh ]" "cobra-mode.sh"
count_test "[ -f patrol.sh ]" "patrol.sh"
count_test "[ -f trophies.sh ]" "trophies.sh"
count_test "[ -f quotes.sh ]" "quotes.sh"

for k in strike-first hard-shell cobra-strike no-mercy evolve wax-on-wax-off sweep-the-leg; do
    count_test "[ -x katas/${k}.sh ]" "katas/${k}.sh"
done

for s in doctrine-quick-ref pillars-reference patterns-lookup quotes-collection victories trophies.json; do
    if [[ "$s" == *.json ]]; then
        count_test "[ -f scrolls/${s} ]" "scrolls/${s}"
    else
        count_test "[ -f scrolls/${s}.md ]" "scrolls/${s}.md"
    fi
done

echo "$PASS / $TESTS passed"

[ $PASS -eq $TESTS ] && exit 0 || exit 1
