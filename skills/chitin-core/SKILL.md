# chitin-core

Route tasks to the cheapest capable model. Never crash on rate limits.

## Activation

When spawning sub-agents or delegating tasks, use ModelRouter to select the optimal model.

**Trigger phrases:** "route this", "spawn a sub-agent", "delegate", or any time you need to choose a model for a task.

## Usage

### Route a Task
```bash
node ~/.openclaw/workspace/skills/chitin-core/scripts/router.js route "task description here"
```

Returns JSON:
```json
{"tier":"MEDIUM","model":"google-antigravity/gemini-3.1-pro","confidence":0.85,"estimatedCost":0.005,"signals":["codeSignals:2×1.2=2.4"]}
```

Use the returned `model` value in `sessions_spawn`.

### Handle Failures
If a spawned session fails with a rate limit or error:
```bash
node ~/.openclaw/workspace/skills/chitin-core/scripts/router.js fail "provider/model" "error message"
```

Then re-route — the failed model will be skipped:
```bash
node ~/.openclaw/workspace/skills/chitin-core/scripts/router.js route "same task"
```

### Check Health
```bash
node ~/.openclaw/workspace/skills/chitin-core/scripts/router.js health
```

### View Costs
```bash
node ~/.openclaw/workspace/skills/chitin-core/scripts/router.js costs
```

### Validate Config
```bash
node ~/.openclaw/workspace/skills/chitin-core/scripts/router.js validate
```

## Workflow

1. Receive task from user
2. Run `router.js route "<task>"` to get optimal model
3. `sessions_spawn` with returned model
4. If spawn fails → `router.js fail "<model>" "<error>"` → retry route
5. Return result to user

## Tiers

| Tier | Use Case | Models |
|------|----------|--------|
| LIGHT | Greetings, simple Q&A, status checks | Flash, DeepSeek, gpt-5-mini, Groq, Ollama |
| MEDIUM | Code, summaries, standard tasks | Gemini Pro, gpt-5.2, DeepSeek Reasoner |
| HEAVY | Architecture, complex reasoning, agentic | gpt-5.2-pro, o3, Codex |

## Override Tags

Include in task text to force a tier:
- `@light` — force cheapest model
- `@medium` — force mid-tier
- `@heavy` — force most capable

## Graceful Degradation

If all models in a tier are rate-limited, the router automatically:
1. Tries adjacent tiers (escalate or downgrade)
2. Falls back to local Ollama if configured
3. Returns structured error with retry time (never crashes)

## Configuration

Edit `config.json` in the skill directory to:
- Add/remove models per tier
- Adjust cost figures
- Tune classification boundaries
