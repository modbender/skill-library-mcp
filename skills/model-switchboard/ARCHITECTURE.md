# Model Switchboard — Architecture & Vision

## Mission

**No OpenClaw agent should ever go completely dead because of a model configuration error.**

Every OpenClaw user — from solo hobbyists to enterprise deployments — deserves:
1. **Per-task model routing** — right model for the right job
2. **3-deep fallback chains** — if A fails, B catches it, if B fails, C catches it
3. **One-command recovery** — never spend hours rebuilding
4. **Visual management** — see your entire model tree at a glance
5. **Fail-closed safety** — bad config is rejected before it can crash anything

## The Problem We're Solving

Today, OpenClaw users face these failure modes:

1. **Wrong model in wrong slot** → Gateway crash → Hours of manual recovery
2. **Single model dependency** → Provider outage → Complete system death
3. **No task-level routing** → Expensive models doing cheap jobs → Wasted money
4. **No backup strategy** → Config corruption → Start from scratch
5. **Agent self-modification** → AI edits config wrong → Cascading failure

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    USER / AGENT                          │
│           "Set Gemini for images"                        │
└───────────────────┬─────────────────────────────────────┘
                    │
┌───────────────────▼─────────────────────────────────────┐
│              MODEL SWITCHBOARD                           │
│                                                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐              │
│  │ Validate  │  │  Backup  │  │  Route   │              │
│  │  Engine   │→ │  Engine  │→ │  Engine  │              │
│  └──────────┘  └──────────┘  └──────────┘              │
│       │                            │                     │
│  ┌────▼────┐                 ┌─────▼─────┐              │
│  │Registry │                 │  OpenClaw  │              │
│  │  JSON   │                 │    CLI     │              │
│  └─────────┘                 └─────┬─────┘              │
│                                    │                     │
└────────────────────────────────────┼─────────────────────┘
                                     │
┌────────────────────────────────────▼─────────────────────┐
│                   openclaw.json                           │
│                                                           │
│  model.primary ──→ model.fallbacks[0] ──→ fallbacks[1]   │
│       │                    │                    │         │
│   Anthropic            OpenAI              Google         │
│   Claude Opus         GPT-5.2          Gemini 3 Pro      │
│                                                           │
│  imageModel.primary ──→ imageFallbacks[0]                │
│       │                       │                           │
│   Claude Opus            Gemini 3 Pro                    │
│                                                           │
│  Per-agent / Per-cron model overrides                    │
│       │                                                   │
│   heartbeat → Haiku/Flash (cheap)                        │
│   coding → Opus/Codex (powerful)                         │
│   research → Grok (search-enabled)                       │
└───────────────────────────────────────────────────────────┘
```

## Task-Model Routing Matrix

| Task | Priority | Why | Cost Tier |
|------|----------|-----|-----------|
| **Conversation** | Highest quality | User-facing, needs best reasoning | High |
| **Coding** | High quality + tools | Needs code generation, file editing | High |
| **Image/Vision** | Vision capability | Must process images/screenshots | Medium-High |
| **Research/Search** | Search-enabled | Web search, data gathering | Medium |
| **Heartbeat** | Lowest cost | Simple polling, status checks | Very Low |
| **Cron Jobs** | Varies by job | Some need quality, some just run scripts | Low-Medium |
| **Sub-agents** | Task-dependent | Spawn with appropriate model | Varies |

## Redundancy Strategy: "Never Dead"

### Tier 1: Primary Chain (3 deep minimum)
```
Primary → Fallback 1 → Fallback 2 → [Fallback 3...]
```
Every role has AT LEAST 3 models. If all paid models fail, the system falls through to free OpenRouter models as last resort.

### Tier 2: Provider Diversity
Never stack the same provider in a fallback chain. If Anthropic is primary, fallbacks should be OpenAI and Google — not another Anthropic model.

### Tier 3: API Key Rotation
OpenClaw supports multiple keys per provider:
```
ANTHROPIC_API_KEY, ANTHROPIC_API_KEY_1, ANTHROPIC_API_KEY_2
```
Rate limit on key 1? Automatically rotates to key 2.

### Tier 4: Config Backup Mesh
- Auto-backup before every change (30 rolling)
- Daily backup to external drive
- Export/import for portable configs
- One-command restore: `switchboard.sh restore latest`

## Deployment Phases

### Phase 1: Core Safety (COMPLETE ✅)
- Validation engine with fail-closed design
- Auto-backup before changes
- Role compatibility checking
- Canvas UI dashboard

### Phase 2: Full Redundancy (IN PROGRESS)
- 3-deep fallback chains for all roles
- Per-task model routing config
- Provider diversity enforcement
- Auto-discovery of available models

### Phase 3: Smart Routing (PLANNED)
- Cost-aware model selection
- Latency-aware failover
- Usage tracking per model
- Budget limits per task type

### Phase 4: Community Features (PLANNED)
- Shareable model configs ("presets")
- Community-voted optimal configurations
- Provider status dashboard
- Model benchmark integration

## Open Source Strategy

This skill will be published to ClawHub as free, open-source software:
- MIT License
- Zero external dependencies
- Works on macOS, Linux, Windows (WSL)
- Python 3.8+ and Bash only
- No API keys required for the tool itself
- Comprehensive documentation

**Goal: Become the standard model management tool for every OpenClaw installation.**
