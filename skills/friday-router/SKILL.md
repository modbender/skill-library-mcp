---
name: friday-router
displayName: IntentRouter
description: Your AI's Smart Traffic Director—precisely matching OpenClaw tasks to the perfect LLM. Intelligent orchestration with OpenRouter. Security-focused: no gateway auth exposure.
version: 1.7.0
---

# IntentRouter

**Your AI's Smart Traffic Director: Precisely Matching Your OpenClaw Tasks to the Perfect LLM.**

**v1.7.0 — Security-focused release.** COMPLEX tier, absolute paths. Tested and working with OpenClaw TUI delegation. **Removed gateway auth secret exposure and gateway management for improved security.**

IntentRouter analyzes your tasks and directs them to the best LLM—MiniMax 2.5 for code, Kimi k2.5 for creative, Grok Fast for research. Eliminate guesswork; route with purpose.

**Security improvements in v1.7.0:** Removed gateway auth token/password from router output. Gateway management removed - use [gateway-guard](https://clawhub.ai/skills/gateway-guard) skill separately. FACEPALM integration removed - use [FACEPALM](https://github.com/RuneweaverStudios/FACEPALM) skill separately.

**Requirements:** **OpenRouter** — All model IDs use the `openrouter/...` prefix. Configure OpenClaw with an OpenRouter API key so one auth profile covers every tier.

**Config access:** This skill reads ONLY its own `config.json` file (located in the skill directory) for model configuration and routing rules. It does NOT read `openclaw.json`, does NOT access gateway tokens/passwords, and does NOT perform any gateway management operations. Router output contains only: `task`, `model`, `sessionTarget`, and optional `label` — no secrets or credentials.

**Default / orchestrator model:** Gemini 2.5 Flash (`openrouter/google/gemini-2.5-flash`) — fast, cheap, reliable at tool-calling. The router delegates tasks to tier-specific sub-agents (Kimi for creative, MiniMax 2.5 for code, etc.).

## Orchestrator flow (mandatory for task requests)

When you are the **main agent** (Gemini 2.5 Flash) and the user gives you a **task** (code, research, write, create, design, poem, story, fix, build, etc.), you must **delegate** it. You do **not** perform the task yourself; a sub-agent does.

**Steps (all three required):**

1. **Run IntentRouter** to get spawn params:
   ```bash
   python3 workspace/skills/friday-router/scripts/router.py spawn --json "<user message>"
   ```
   Example output: `{"task":"write a poem about Mai","model":"openrouter/moonshotai/kimi-k2.5","sessionTarget":"isolated"}`

2. **Immediately call `sessions_spawn`** with the router's output. Use the **exact `model`** from the JSON. Example:
   ```
   sessions_spawn(task="write a poem about Mai", model="openrouter/moonshotai/kimi-k2.5", sessionTarget="isolated")
   ```
   Do **not** change the `model` value. If the router said `openrouter/moonshotai/kimi-k2.5`, pass exactly that.

3. **Forward the sub-agent's reply** to the user. That reply IS the task output. Say "Using: Kimi k2.5" (the model that actually ran). Never say "Using: Claude Sonnet 4" or any model that didn't run. **Output hygiene:** If the sub-agent result contains internal text ("A subagent task … completed", "Findings:", "Stats:", "sessionKey", "Summarize this naturally"), strip that block and show only the final user-facing content to the user.

**If `sessions_spawn` returns an error** (e.g. `device_token_mismatch`): tell the user delegation failed and suggest checking gateway status or using the `gateway-guard` skill. Do **not** do the task yourself.

**Hard-stop rule:** If `sessions_spawn` fails or is skipped, return only the delegation error and next-step fix. Do not write the requested output directly.

**No-classify execution rule:** For real user tasks, do not execute via `classify`. `classify` is diagnostics only. Execution must use `spawn --json` -> `sessions_spawn`.

**Label gate:** Only print `Using: <model>` after successful spawn. If no successful spawn, do not print a `Using:` label.

**Output hygiene:** Never return internal orchestration metadata to the user (no session keys/IDs, transcript paths, runtime/token stats, or internal "summarize this" instructions). Forward only clean user-facing content.

**Exception:** Meta-questions ("what model are you?", "how does routing work?") you answer yourself.

**Security note:** This skill does NOT expose gateway auth secrets (tokens/passwords) in its output. Gateway management functionality has been removed. Use the separate `gateway-guard` skill if gateway auth management is needed.

## Model Selection (Austin's Prefs)

| Use Case | Primary (OpenRouter) | Fallback |
|----------|---------------------|----------|
| **Default / orchestrator** | Gemini 2.5 Flash | — |
| **Fast/cheap** | Gemini 2.5 Flash | Gemini 1.5 Flash, Haiku |
| **Reasoning** | GLM-5 | Minimax 2.5 |
| **Creative/Frontend** | Kimi k2.5 | — |
| **Research** | Grok Fast | — |
| **Code/Engineering** | MiniMax 2.5 | Qwen2.5-Coder |
| **Quality/Complex** | GLM 4.7 Flash | GLM 4.7, Sonnet 4, GPT-4o |
| **Vision/Images** | GPT-4o | — |

All model IDs use `openrouter/` prefix (e.g. `openrouter/moonshotai/kimi-k2.5`).

## Usage

### CLI

```bash
python scripts/router.py default                          # Show default model
python scripts/router.py classify "fix lint errors"        # Classify → tier + model
python scripts/router.py spawn --json "write a poem"       # JSON for sessions_spawn (no gateway secrets)
python scripts/router.py models                            # List all models
```

**Note:** Gateway auth management is not included. Use `gateway-guard` skill separately if needed.

### sessions_spawn examples

**Creative task (poem):**
```
router output: {"task":"write a poem","model":"openrouter/moonshotai/kimi-k2.5","sessionTarget":"isolated"}
→ sessions_spawn(task="write a poem", model="openrouter/moonshotai/kimi-k2.5", sessionTarget="isolated")
```

**Code task (bug fix):**
```
router output: {"task":"fix the login bug","model":"openrouter/minimax/minimax-m2.5","sessionTarget":"isolated"}
→ sessions_spawn(task="fix the login bug", model="openrouter/minimax/minimax-m2.5", sessionTarget="isolated")
```

**Research task:**
```
router output: {"task":"research best LLMs","model":"openrouter/x-ai/grok-4.1-fast","sessionTarget":"isolated"}
→ sessions_spawn(task="research best LLMs", model="openrouter/x-ai/grok-4.1-fast", sessionTarget="isolated")
```

## Tier Detection

- **FAST**: check, get, list, show, status, monitor, fetch, simple
- **REASONING**: prove, logic, analyze, derive, math, step by step
- **CREATIVE**: creative, write, story, design, UI, UX, frontend, website (website/frontend/landing projects → Kimi k2.5 only; do not use CODE tier)
- **RESEARCH**: research, find, search, lookup, web, information
- **CODE**: code, function, debug, fix, implement, refactor, test, React, JWT (code/API only; not website builds)
- **QUALITY**: complex, architecture, design, system, comprehensive
- **VISION**: image, picture, photo, screenshot, visual

## What Changed from Original

| Bug | Fix |
|-----|-----|
| Simple indicators inverted (high match = complex) | Now correctly: high simple keyword match = FAST tier |
| Agentic tasks not bumping tier | Multi-step tasks now properly bump to CODE tier |
| Vision tasks misclassified | Vision keywords now take priority over other classifications |
| Code keywords not detected | Added React, JWT, API, and other common code terms |
| Confidence always low | Now varies appropriately based on keyword match strength |

