#!/usr/bin/env bash
# Count quality rubric checks in SKILL.md and verify total
set -euo pipefail

SKILL_MD="$1"

if [[ ! -f "$SKILL_MD" ]]; then
    echo "ERROR: SKILL.md not found: $SKILL_MD"
    exit 1
fi

# Count SQ-A checks
sq_a=$(grep -c '^| SQ-A' "$SKILL_MD" || echo 0)
echo "SQ-A checks: $sq_a"

# Count SQ-B checks
sq_b=$(grep -c '^| SQ-B' "$SKILL_MD" || echo 0)
echo "SQ-B checks: $sq_b"

# Count SQ-C checks
sq_c=$(grep -c '^| SQ-C' "$SKILL_MD" || echo 0)
echo "SQ-C checks: $sq_c"

# Count SQ-D checks
sq_d=$(grep -c '^| SQ-D' "$SKILL_MD" || echo 0)
echo "SQ-D checks: $sq_d"

# Count additional checks (SCOPE, OPSEC, REF, ARCH) - only from rubric tables
scope=$(grep -E '^\| SCOPE-' "$SKILL_MD" | wc -l | tr -d ' ')
echo "SCOPE checks: $scope"

opsec=$(grep -E '^\| OPSEC-' "$SKILL_MD" | wc -l | tr -d ' ')
echo "OPSEC checks: $opsec"

ref=$(grep -E '^\| REF-' "$SKILL_MD" | wc -l | tr -d ' ')
echo "REF checks: $ref"

arch=$(grep -E '^\| ARCH-' "$SKILL_MD" | wc -l | tr -d ' ')
echo "ARCH checks: $arch"

total=$((sq_a + sq_b + sq_c + sq_d + scope + opsec + ref + arch))
expected=33

echo ""
echo "Total checks found: $total"
echo "Expected: $expected"

if [[ $total -ne $expected ]]; then
    echo "ERROR: Rubric check count mismatch! Found $total, expected $expected"
    exit 1
fi

echo "✓ Rubric check count is correct"
exit 0
