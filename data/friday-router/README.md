# IntentRouter

**Your AI's Smart Traffic Director: Precisely Matching Your OpenClaw Tasks to the Perfect LLM.**

**v1.7.0 — This version is tested and working.** COMPLEX tier, absolute paths for TUI delegation. **Security-focused release:** Removed gateway auth secret exposure and gateway management functionality for improved security rating.

IntentRouter is the intelligent LLM orchestration skill for OpenClaw. It precisely analyzes your tasks and directs them to the best LLM for the job—MiniMax 2.5 for code, Kimi k2.5 for creative prose, Grok Fast for web research. Route with purpose; stop wasting resources.

**Security improvements in v1.7.0:** Removed gateway auth token/password exposure from router output. Gateway management functionality has been removed - use the separate [gateway-guard](https://clawhub.ai/skills/gateway-guard) skill if gateway auth management is needed. FACEPALM troubleshooting integration has been removed - use the separate [FACEPALM](https://github.com/RuneweaverStudios/FACEPALM) skill if troubleshooting is needed.

## Requirements

- **OpenRouter** — All model delegation uses OpenRouter (`openrouter/...` prefix). Configure OpenClaw with an OpenRouter API key so one auth profile covers every model.

## Default behavior

**Session default / orchestrator:** Gemini 2.5 Flash (`openrouter/google/gemini-2.5-flash`) — fast, cheap, reliable at tool-calling.

The router delegates tasks to tier-specific sub-agents (Kimi for creative, MiniMax 2.5 for code, etc.) via `sessions_spawn`. Simple tasks (check, status, list) down-route to Gemini 2.5 Flash.

---

## Orchestrator flow (task delegation)

The **main agent (Gemini 2.5 Flash)** does not do user tasks itself. For every user **task** (code, research, write, build, etc.):

1. Run IntentRouter: `python scripts/router.py spawn --json "<user message>"` and parse the JSON.
2. Call **sessions_spawn** with the `task` and `model` from the router output (use the exact `model` value).
3. Forward the sub-agent's result to the user.

**Example:**
```
router: {"task":"write a poem","model":"openrouter/moonshotai/kimi-k2.5","sessionTarget":"isolated"}
→ sessions_spawn(task="write a poem", model="openrouter/moonshotai/kimi-k2.5", sessionTarget="isolated")
→ Forward Kimi k2.5's poem to user. Say "Using: Kimi k2.5".
```

**Exception:** Meta-questions ("what model are you?") you answer yourself.

---

## Quick start

```bash
npm install -g clawhub
clawhub install friday-router

python scripts/router.py default
python scripts/router.py classify "your task description"
```

---

## Features

- **Orchestrator** — Gemini 2.5 Flash delegates to tier-specific sub-agents via `sessions_spawn`
- Fixed scoring bugs from original intelligent-router
- 7 tiers: FAST, REASONING, CREATIVE, RESEARCH, CODE, QUALITY, VISION
- All models via OpenRouter (single API key)
- Config-driven: `config.json` for models and routing rules
- **Security-focused** — No gateway auth secret exposure, no process management

---

## Models

| Tier | Model | Cost/M (in/out) |
|------|-------|-----------------|
| **Default / orchestrator** | Gemini 2.5 Flash | $0.30 / $2.50 |
| FAST | Gemini 2.5 Flash | $0.30 / $2.50 |
| REASONING | GLM-5 | $0.10 / $0.10 |
| CREATIVE | Kimi k2.5 | $0.20 / $0.20 |
| RESEARCH | Grok Fast | $0.10 / $0.10 |
| CODE | MiniMax 2.5 | $0.10 / $0.10 |
| QUALITY | GLM 4.7 Flash | $0.06 / $0.40 |
| VISION | GPT-4o | $2.50 / $10.00 |

**Fallbacks:** FAST → Gemini 1.5 Flash, Haiku; QUALITY → GLM 4.7, Sonnet 4, GPT-4o; CODE → Qwen Coder; REASONING → Minimax 2.5.

---

## CLI usage

```bash
python scripts/router.py default                          # Show default model
python scripts/router.py classify "fix lint errors"        # Classify → tier + model
python scripts/router.py score "build a React auth system" # Detailed scoring
python scripts/router.py cost "design a landing page"      # Cost estimate
python scripts/router.py spawn "research best LLMs"        # Spawn params (human)
python scripts/router.py spawn --json "research best LLMs" # JSON for sessions_spawn (no gateway secrets)
python scripts/router.py models                            # List all models
```

**Note:** Gateway auth management is not included in this skill. Use the separate `gateway-guard` skill if you need gateway auth checking or management.

---

## In-code usage

```python
from scripts.router import FridayRouter

router = FridayRouter()

default = router.get_default_model()
tier = router.classify_task("check server status")        # → "FAST"
result = router.recommend_model("build auth system")       # → {tier, model, fallback, reasoning}
spawn = router.spawn_agent("fix this bug", label="bugfix") # → {params: {task, model, sessionTarget}}
cost = router.estimate_cost("design landing page")         # → {tier, model, cost, currency}
```

---

## Tier detection

| Tier | Example keywords |
|------|------------------|
| **FAST** | check, get, list, show, status, monitor, fetch, simple |
| **REASONING** | prove, logic, analyze, derive, math, step by step |
| **CREATIVE** | creative, write, story, design, UI, UX, frontend, website (website projects → Kimi k2.5 only) |
| **RESEARCH** | research, find, search, lookup, web, information |
| **CODE** | code, function, debug, fix, implement, refactor, test, React, JWT (not website builds) |
| **QUALITY** | complex, architecture, design, system, comprehensive |
| **VISION** | image, picture, photo, screenshot, visual |

- **Vision** has priority: if vision keywords are present, task is VISION regardless of other keywords.
- **Agentic** tasks (multi-step) are bumped to at least CODE.

---

---

## Changelog

### v1.7.0 (Security-focused release)

**Removed functionality (for improved security rating):**
- **Gateway guard integration** — Removed `gateway_watchdog.py` and gateway auth management functionality. Use the separate [gateway-guard](https://clawhub.ai/skills/gateway-guard) skill for gateway auth checking and management.
- **Gateway auth secret exposure** — Removed `get_openclaw_gateway_config()` function that exposed gateway tokens/passwords in router output. Router spawn output no longer includes `gatewayToken`, `gatewayPassword`, `gatewayAuthMode`, or `gatewayPort`.
- **FACEPALM troubleshooting integration** — Removed troubleshooting loop detection and automatic FACEPALM invocation. Use the separate [FACEPALM](https://github.com/RuneweaverStudios/FACEPALM) skill if intelligent troubleshooting is needed.

**Security improvements:**
- Router now only handles model routing with no credential exposure
- No process management capabilities (no gateway restart/kill operations)
- Clean separation of concerns: routing vs. gateway management vs. troubleshooting

**Migration:**
- If you need gateway auth management: `clawhub install gateway-guard`
- If you need troubleshooting: Install [FACEPALM](https://github.com/RuneweaverStudios/FACEPALM) separately

---

## Configuration

- **`config.json`** — Model list and `routing_rules` per tier; `default_model` (e.g. `openrouter/google/gemini-2.5-flash`) for session default and orchestrator.
- Router loads `config.json` from the parent of `scripts/` (skill root).

---

## Related skills

- **[gateway-guard](https://clawhub.ai/skills/gateway-guard)** — Gateway auth management (use separately if needed)
- **[FACEPALM](https://github.com/RuneweaverStudios/FACEPALM)** — Intelligent troubleshooting (use separately if needed)
- **[what-just-happened](https://clawhub.ai/skills/what-just-happened)** — Summarizes gateway restarts

---

## License / author

Austin. Part of the OpenClaw skills ecosystem.
