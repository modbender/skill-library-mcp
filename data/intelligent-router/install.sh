#!/usr/bin/env bash
# Intelligent Router - Core Skill Installer
# Patches AGENTS.md with the mandatory enforcement protocol.
# Run once: bash skills/intelligent-router/install.sh

set -e
AGENTS_FILE="$(git rev-parse --show-toplevel 2>/dev/null || echo $HOME/clawd)/AGENTS.md"
MARKER="## Sub-Agent Spawning Protocol"

if grep -q "$MARKER" "$AGENTS_FILE"; then
    echo "✅ Sub-Agent Spawning Protocol already present in AGENTS.md"
    echo "   Update manually if needed."
else
    echo "📝 Injecting enforcement protocol into AGENTS.md..."
    cat >> "$AGENTS_FILE" << 'BLOCK'

## Sub-Agent Spawning Protocol

**Before spawning sub-agents, classify the task for optimal model selection:**

1. **Run classification:**
   ```bash
   python3 skills/intelligent-router/scripts/router.py classify "task description"
   ```

2. **Use recommended model in sessions_spawn:**
   ```python
   sessions_spawn(
       task="task description",
       model="<recommended-model-id>",
       label="descriptive-label"
   )
   ```

3. **Or use the spawn helper (shows command, doesn't execute):**
   ```bash
   python3 skills/intelligent-router/scripts/spawn_helper.py "task description"
   ```

**Why this matters:**
- Saves 80-95% on costs by using cheaper models for simple tasks
- Preserves quality by using premium models for complex work
- Automatic fallback chains if primary model fails

**Tier guidelines:**
- **SIMPLE** (monitoring, checks, summaries) → `ollama/glm-4.7-flash` (FREE local), fallback: GLM-4.7 via proxy
- **MEDIUM** (code fixes, research, patches) → DeepSeek V3.2, Llama 3.3 70B
- **COMPLEX** (features, architecture, debugging) → Sonnet 4.5, Gemini 3 Pro
- **REASONING** (proofs, formal logic) → DeepSeek R1 32B, QwQ 32B
- **CRITICAL** (security, production) → Opus 4.6

⚠️ **MANDATORY: Always set `model` in cron job payloads.** No model = Sonnet default = expensive waste.
Sonnet must NEVER be used for monitoring or simple tasks.

**Don't guess** — let the router classify. It uses weighted 15-dimension scoring.
BLOCK
    echo "✅ Protocol injected."
fi

echo ""
echo "🧪 Testing router..."
python3 "$(dirname "$0")/scripts/router.py" classify "check server health" | grep -E "Classification:|Recommended"
echo ""
echo "✅ Intelligent Router core skill installed."
