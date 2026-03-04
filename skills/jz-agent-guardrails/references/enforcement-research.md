# AI Agent Rules Enforcement Research

## TL;DR

**Prompts are advisory, code is mandatory.** You cannot rely on instructions alone to enforce standards. You need mechanical enforcement layers that run regardless of what the LLM decides to do.

## Enforcement Reliability Hierarchy

1. **Code-level enforcement** (hooks, pre-commit, linters) — 100% reliable
2. **Structural constraints** (API design, imports, module boundaries) — 95% reliable
3. **Self-verification loops** (agent checks own work) — 80% reliable
4. **Prompt instructions** (AGENTS.md, system prompts) — 60-70% reliable
5. **Written rules in markdown** — 40-50% reliable (degrades with context length)

## Key Findings

### Code Hooks Are the Gold Standard

IDE and agent frameworks support **hooks** — shell scripts that run at specific lifecycle points. These are deterministic, not advisory.

> "Unlike AGENTS.md instructions which are advisory, hooks are deterministic and guarantee the action happens."

**Hook lifecycle points:**
- **Pre-tool-use** — runs before a tool call, can block it
- **Post-tool-use** — runs after file edits, can reject changes
- **Pre-commit** — runs before git commits, can block them
- **Session start** — inject context at beginning of sessions

### Why Markdown Rules Degrade

From Anthropic's best practices:
> "If the agent keeps doing something you don't want despite having a rule against it, the file is probably too long and the rule is getting lost."

As context windows fill up, earlier instructions lose influence. Rules at the beginning of a long conversation have less effect than rules enforced mechanically at each step.

### Architectural Constraints

Design code so bypassing is structurally difficult:
- **Module registries** (`__init__.py`) that export all public functions
- **Import enforcement** — new scripts must import from registries
- **Single source of truth** — one implementation per function
- **Pipeline architecture** — data must flow through validated stages

### Self-Verification Loops

Have the agent self-check before finalizing:
1. Does this project have existing modules? (Check `__init__.py`)
2. Are there existing functions that do what I need?
3. Am I importing them or rewriting them?
4. If rewriting, why? Document the reason.

### Multi-Agent Patterns

Research from scaling autonomous agents:
- **Planner-worker separation** — plan specifies which modules to use, worker executes
- **Judge agents** — separate agent verifies compliance
- **Fresh starts combat drift** — long conversations cause agents to lose focus
- **Model choice affects compliance** — some models take more shortcuts than others

## Practical Implementation Tiers

### Tier 1: Immediate
- Pre-creation checklist script (run before new files)
- Post-creation validator (run after new files)
- Git pre-commit hook (block bypass patterns and secrets)

### Tier 2: Short-term
- Project-level import registries (`__init__.py`)
- Automated integration tests verifying import compliance

### Tier 3: Medium-term
- Self-review loops for all agent outputs
- Architectural constraints making bypassing structurally hard
- Automated evals detecting standard-bypass patterns

## Key Principle

> Don't add more markdown rules. Add mechanical enforcement.
> Rules in markdown are suggestions. Hooks, tests, and architectural constraints are laws.

## Sources

1. Cursor Blog — Agent best practices, hooks, scaling research
2. Anthropic — Claude Code best practices, hooks guide
3. Guardrails AI — Framework with 67+ validators
4. NVIDIA NeMo Guardrails — Open-source toolkit (5 rail types)
5. Constitutional AI — Self-critique and revision patterns
6. OpenAI — Prompt engineering guide
