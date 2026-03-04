#!/bin/bash
# Self-Improvement Activator Hook
# Triggers on UserPromptSubmit to remind Claude about learning capture
# Keep output minimal (~50-100 tokens) to minimize overhead

set -e

# Output reminder as system context
cat << 'EOF'
<self-improvement-reminder>
After completing this task, evaluate if extractable knowledge emerged:
- Non-obvious solution discovered through investigation?
- Workaround for unexpected behavior?
- Project-specific pattern learned?
- Error required debugging to resolve?

If yes: Record with mulch: \`mulch record <domain> --type failure|convention|decision|pattern|guide\` (see self-improvement skill).
If high-value (recurring, broadly applicable): Promote to CLAUDE.md/AGENTS.md or extract as a skill.
</self-improvement-reminder>
EOF
