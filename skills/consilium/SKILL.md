---
name: council
description: "Your personal board of AI advisors — the only skill that uses truly different AI models (not one model role-playing). Get better answers to hard questions by having 3-5 models from different providers analyze independently, then synthesizing consensus, disagreements, and action items. Each model brings genuinely different training and reasoning — catching blind spots that same-model approaches miss. Zero external dependencies: uses native OpenClaw sub-agents, no Python scripts, no API keys beyond your existing model config. Use when: user says /council, or asks for multi-model analysis of a decision, architecture, strategy, or any complex problem."
---

# Consilium — True Multi-Model Deliberation

Ask a hard question → 3-5 AI models from **different providers** analyze it independently → you get a synthesis with consensus, disagreements, action items, and minority opinions.

**Unlike other council skills:** this uses genuinely different models (Anthropic + OpenAI + Google + others), not one model playing multiple roles. Different training data = different blind spots = better coverage.

**Always respond in the same language as the user's question.**

## Examples

- `/council Should we migrate from monolith to microservices given our 4-person team?`
- `/council --profile fast Evaluate the risks of this investment strategy`
- `/council How to resolve a complex equity dispute with my co-founder?`
- After results: *"Tell me more about what Gemini said on point 3"* (follow-up with specific panelist)

## Requirements

- **Minimum 3 models** from different providers in `agents.defaults.models` allowlist
- Tools: `sessions_spawn`, `subagents`, `sessions_history` (enabled by default)
- Each council run = 3-5 API calls (one per model) + synthesis
- No additional API keys, Python scripts, or external dependencies

## Privacy & Data

- Your question is sent to each model provider in your panel. Only use models/providers you trust.
- `council-panel.json` (saved to workspace root) contains only model names and slot assignments, not queries or responses.
- Panelist responses exist only in sub-agent session memory and are auto-archived per your OpenClaw settings.
- No data is sent to external services beyond your configured model providers.

## Panel

On first use, check available models and ask the user to confirm the panel. Save to workspace root as `council-panel.json` for reuse. User can re-run panel selection anytime with `--models`.

### Slot roles (fill from available models)

| Slot | Role | Good candidates |
|------|------|-----------------|
| Deep thinker | Nuance, system thinking | Claude Opus, GPT-5, Gemini Pro |
| Pragmatist | Concise, actionable | Claude Sonnet, GPT-mini, Gemini Flash |
| Broad analyst | Wide knowledge, structure | GPT-5, Gemini Pro, Claude Opus |
| Technical | Rigor, edge cases | Gemini Pro, Claude Sonnet, GLM |
| Contrarian | Challenge assumptions | GLM, any model with contrarian lens |

**Rules:** Each slot = different model. Prefer different providers. Min 3 models to run. If fewer than 3 available, inform user.

### Example `council-panel.json`

```json
{
  "panel": [
    { "slot": "deep_thinker", "model": "anthropic/claude-opus-4-6", "lens": "Deep analysis" },
    { "slot": "pragmatist", "model": "anthropic/claude-sonnet-4-5", "lens": "Pragmatic" },
    { "slot": "broad_analyst", "model": "github-copilot/gpt-5.2", "lens": "Broad knowledge" }
  ],
  "confirmed": "2026-02-24"
}
```

## Profiles

- **thorough** (default): All panel slots, quorum = max(slots - 2, 2)
- **balanced**: 3 strongest slots, quorum 2
- **fast**: 2 fastest slots, quorum 2

## Workflow

1. **Dispatch** — spawn panelists in parallel (`sessions_spawn`, mode=run, timeout 120s). Assign unique lens per slot. Detect question language, hardcode in prompt. Tell user: "Panel dispatched, ~60s. Send a follow-up when ready."
2. **Collect** — on user's follow-up: `subagents list` → `sessions_history`. Synthesize when quorum met.
3. **Debate** (only if `--rounds 2`) — anonymized digest → rebuttals. See `references/PROTOCOL.md`.
4. **Synthesize** — produce output below.

## Output Format

```
## Council of Experts
**Question:** ... | **Panel:** ... | **Profile:** ...
---
### Positions
**{Model}** ({lens}) — {2-3 sentence summary}

### ✅ Consensus
### ⚡ Disagreements
### 🗣️ Minority opinions

### 🎯 Synthesis
Agreement: 🟢 strong (4-5) | 🟡 mixed (3) | 🔴 split

### 📋 Action Items
1. **{Highest priority}** — {effort/time estimate}
2. **{Next action}** — {estimate}
3. **{Next action}** — {estimate}
```

Randomize position order. Quote with attribution. Preserve minority views. Never fabricate consensus. Section headers and content in user's language.

## Follow-up

After synthesis, the user can drill deeper with a specific panelist:
- *"Tell me more about what GPT said on point 2"*
- *"I want the contrarian's take on the action items"*

Use `sessions_history` to retrieve that panelist's full response, then expand on the specific point in that model's perspective.

## Flags

`--profile thorough|balanced|fast` · `--models <list>` · `--skip <model>` · `--rounds 2` · `--quorum N` · `--timeout N` · `--lens "..."` · `--lenses "a,b,c"`

Prompt templates, debate mechanics, error handling → `references/PROTOCOL.md`
