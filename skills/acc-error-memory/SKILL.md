---
name: acc-error-memory
description: "Error pattern tracking for AI agents. Detects corrections, escalates recurring mistakes, learns mitigations. The 'something's off' detector from the AI Brain series."
metadata:
  openclaw:
    emoji: "⚡"
    version: "1.0.0"
    author: "ImpKind"
    repo: "https://github.com/ImpKind/acc-error-memory"
    requires:
      os: ["darwin", "linux"]
      bins: ["python3", "jq"]
    tags: ["memory", "monitoring", "ai-brain", "error-detection"]
---

# Anterior Cingulate Memory ⚡

**Conflict detection and error monitoring for AI agents.** Part of the AI Brain series.

The anterior cingulate cortex (ACC) monitors for errors and conflicts. This skill gives your AI agent the ability to learn from mistakes — tracking error patterns over time and becoming more careful in contexts where it historically fails.

## The Problem

AI agents make mistakes:
- Misunderstand user intent
- Give wrong information
- Use the wrong tone
- Miss context from earlier in conversation

Without tracking, the same mistakes repeat. The ACC detects and logs these errors, building awareness that persists across sessions.

## The Solution

Track error patterns with:
- **Pattern detection** — recurring error types get escalated
- **Severity levels** — normal (1x), warning (2x), critical (3+)
- **Resolution tracking** — patterns clear after 30+ days
- **Watermark system** — incremental processing, no re-analysis

## Configuration

### ACC_MODELS (Model Agnostic)

The LLM screening and calibration scripts are model-agnostic. Set `ACC_MODELS` to use any CLI-accessible model:

```bash
# Default (Anthropic Claude via CLI)
export ACC_MODELS="claude --model haiku -p,claude --model sonnet -p"

# Ollama (local)
export ACC_MODELS="ollama run llama3,ollama run mistral"

# OpenAI
export ACC_MODELS="openai chat -m gpt-4o-mini,openai chat -m gpt-4o"

# Single model (no fallback)
export ACC_MODELS="claude --model haiku -p"
```

**Format:** Comma-separated CLI commands. Each command is invoked with the prompt appended as the final argument. Models are tried in order — if the first fails/times out (45s), the next is used as fallback.

**Scripts that use ACC_MODELS:**
- `haiku-screen.sh` — LLM confirmation of regex-filtered error candidates
- `calibrate-patterns.sh` — Pattern calibration via LLM classification

## Quick Start

### 1. Install

```bash
cd ~/.openclaw/workspace/skills/anterior-cingulate-memory
./install.sh --with-cron
```

This will:
- Create `memory/acc-state.json` with empty patterns
- Generate `ACC_STATE.md` for session context
- Set up cron for analysis 3x daily (4 AM, 12 PM, 8 PM)

### 2. Check current state

```bash
./scripts/load-state.sh
# ⚡ ACC State Loaded:
# Active patterns: 2
# - tone_mismatch: 2x (warning)
# - missed_context: 1x (normal)
```

### 3. Manual error logging

```bash
./scripts/log-error.sh \
  --pattern "factual_error" \
  --context "Stated Python 3.9 was latest when it's 3.12" \
  --mitigation "Always web search for version numbers"
```

### 4. Check for resolved patterns

```bash
./scripts/resolve-check.sh
# Checks patterns not seen in 30+ days
```

## Scripts

| Script | Purpose |
|--------|---------|
| `preprocess-errors.sh` | Extract user+assistant exchanges since watermark |
| `encode-pipeline.sh` | Run full preprocessing pipeline |
| `log-error.sh` | Log an error with pattern, context, mitigation |
| `load-state.sh` | Human-readable state for session context |
| `resolve-check.sh` | Check for patterns ready to resolve (30+ days) |
| `update-watermark.sh` | Update processing watermark |
| `sync-state.sh` | Generate ACC_STATE.md from acc-state.json |
| `log-event.sh` | Log events for brain analytics |

## How It Works

### 1. Preprocessing Pipeline

The `encode-pipeline.sh` extracts exchanges from session transcripts:

```bash
./scripts/encode-pipeline.sh --no-spawn
# ⚡ ACC Encode Pipeline
# Step 1: Extracting exchanges...
# Found 47 exchanges to analyze
```

Output: `pending-errors.json` with user+assistant pairs:
```json
[
  {
    "assistant_text": "The latest Python version is 3.9",
    "user_text": "Actually it's 3.12 now",
    "timestamp": "2026-02-11T10:00:00Z"
  }
]
```

### 2. Error Analysis (via Cron Agent)

An LLM (configured via `ACC_MODELS`) analyzes each exchange for:
- Direct corrections ("no", "wrong", "that's not right")
- Implicit corrections ("actually...", "I meant...")
- Frustration signals ("you're not understanding")
- User confusion caused by the agent

### 3. Pattern Tracking

Errors are logged with pattern names:
```bash
./scripts/log-error.sh --pattern "factual_error" --context "..." --mitigation "..."
```

Patterns escalate with repetition:
- **1x** → normal (noted)
- **2x** → warning (watch for this)
- **3+** → critical (actively avoid!)

### 4. Resolution

Patterns not seen for 30+ days move to resolved:
```bash
./scripts/resolve-check.sh
# ✓ Resolved: version_numbers (32 days clear)
```

## Cron Schedule

Default: 3x daily for faster feedback loop

```bash
# Add to cron
openclaw cron add --name acc-analysis \
  --cron "0 4,12,20 * * *" \
  --session isolated \
  --agent-turn "Run ACC analysis pipeline..."
```

## State File Format

```json
{
  "version": "2.0",
  "lastUpdated": "2026-02-11T12:00:00Z",
  "activePatterns": {
    "factual_error": {
      "count": 3,
      "severity": "critical",
      "firstSeen": "2026-02-01T10:00:00Z",
      "lastSeen": "2026-02-10T15:00:00Z",
      "context": "Stated outdated version numbers",
      "mitigation": "Always verify versions with web search"
    }
  },
  "resolved": {
    "tone_mismatch": {
      "count": 2,
      "resolvedAt": "2026-02-11T04:00:00Z",
      "daysClear": 32
    }
  },
  "stats": {
    "totalErrorsLogged": 15
  }
}
```

## Event Logging

Track ACC activity over time:

```bash
./scripts/log-event.sh analysis errors_found=2 patterns_active=3 patterns_resolved=1
```

Events append to `~/.openclaw/workspace/memory/brain-events.jsonl`:
```json
{"ts":"2026-02-11T12:00:00Z","type":"acc","event":"analysis","errors_found":2,"patterns_active":3}
```

## Integration with OpenClaw

### Add to session startup (AGENTS.md)

```markdown
## Every Session
1. Load hippocampus: `./scripts/load-core.sh`
2. Load emotional state: `./scripts/load-emotion.sh`
3. **Load error patterns:** `~/.openclaw/workspace/skills/anterior-cingulate-memory/scripts/load-state.sh`
```

### Behavior Guidelines

When you see patterns in ACC state:
- 🔴 **Critical (3+)** — actively verify before responding in this area
- ⚠️ **Warning (2x)** — be extra careful
- ✅ **Resolved** — lesson learned, don't repeat

## Future: Amygdala Integration

*Planned:* Connect ACC to amygdala so errors affect emotional state:
- Errors → lower valence, higher alertness
- Clean runs → maintain positive state
- Pattern resolution → sense of accomplishment

## AI Brain Series

| Part | Function | Status |
|------|----------|--------|
| [hippocampus](https://www.clawhub.ai/skills/hippocampus) | Memory formation, decay, reinforcement | ✅ Live |
| [amygdala-memory](https://www.clawhub.ai/skills/amygdala-memory) | Emotional processing | ✅ Live |
| [vta-memory](https://www.clawhub.ai/skills/vta-memory) | Reward and motivation | ✅ Live |
| **anterior-cingulate-memory** | Conflict detection, error monitoring | ✅ Live |
| [basal-ganglia-memory](https://www.clawhub.ai/skills/basal-ganglia-memory) | Habit formation | 🚧 Development |
| [insula-memory](https://www.clawhub.ai/skills/insula-memory) | Internal state awareness | 🚧 Development |

## Philosophy

The ACC in the human brain creates that "something's off" feeling — the pre-conscious awareness that you've made an error. This skill gives AI agents a similar capability: persistent awareness of mistake patterns that influences future behavior.

Mistakes aren't failures. They're data. The ACC turns that data into learning.

---

*Built with ⚡ by the OpenClaw community*
