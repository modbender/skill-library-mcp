#!/usr/bin/env bash
# Initialize pre-flight checks in workspace

set -euo pipefail

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WORKSPACE_DIR="${WORKSPACE_DIR:-$(pwd)}"

echo "🔥 Initializing Pre-Flight Checks"
echo "Skill directory: $SKILL_DIR"
echo "Workspace directory: $WORKSPACE_DIR"
echo

# Check if already initialized
if [ -f "$WORKSPACE_DIR/PRE-FLIGHT-CHECKS.md" ]; then
    echo "⚠️  PRE-FLIGHT-CHECKS.md already exists"
    read -p "Overwrite? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ Cancelled"
        exit 1
    fi
fi

# Copy templates to workspace
echo "📋 Copying templates..."
cp "$SKILL_DIR/templates/CHECKS-template.md" "$WORKSPACE_DIR/PRE-FLIGHT-CHECKS.md"
cp "$SKILL_DIR/templates/ANSWERS-template.md" "$WORKSPACE_DIR/PRE-FLIGHT-ANSWERS.md"
echo "✅ Created PRE-FLIGHT-CHECKS.md"
echo "✅ Created PRE-FLIGHT-ANSWERS.md"
echo

# Check if AGENTS.md exists
if [ -f "$WORKSPACE_DIR/AGENTS.md" ]; then
    echo "📝 Checking AGENTS.md integration..."
    
    if grep -q "Run Pre-Flight Checks" "$WORKSPACE_DIR/AGENTS.md"; then
        echo "✅ AGENTS.md already integrated"
    else
        echo "⚠️  AGENTS.md exists but doesn't mention pre-flight checks"
        echo
        echo "Add this to your 'Every Session' section in AGENTS.md:"
        echo
        cat <<'EOF'
5. **Run Pre-Flight Checks** — verify behavior consistency

### Pre-Flight Checks

After loading memory, verify your behavior matches learned patterns:

1. Read `PRE-FLIGHT-CHECKS.md` completely
2. Answer each scenario based on your current understanding
3. Compare your answers with `PRE-FLIGHT-ANSWERS.md`
4. Report any discrepancies immediately

**When to run:**
- After every session start (automatic)
- After `/clear` (restore consistency)
- On demand via `/preflight` command
- When uncertain about behavior

**Scoring:**
- N/N: ✅ Ready to work
- N-2 to N-1: ⚠️ Review rules
- <N-2: ❌ Reload memory, retest
EOF
        echo
    fi
else
    echo "ℹ️  AGENTS.md not found (optional)"
fi

echo
echo "✅ Pre-Flight Checks initialized!"
echo
echo "Next steps:"
echo "1. Edit PRE-FLIGHT-CHECKS.md with your scenarios"
echo "2. Edit PRE-FLIGHT-ANSWERS.md with expected behaviors"
echo "3. Update AGENTS.md to run checks after loading memory"
echo "4. Test: Have agent read and run checks"
echo
echo "Examples available in: $SKILL_DIR/examples/"
echo "Prometheus example (23 checks): CHECKS-prometheus.md"
echo

