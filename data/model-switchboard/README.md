# 🔀 Model Switchboard

**Never crash your OpenClaw gateway again.**

Safe, redundant AI model configuration with automatic fallback chains, validation, and one-command recovery. Built for every OpenClaw user — from first install to production deployment.

## The Problem

Editing `openclaw.json` directly for model changes is the #1 cause of OpenClaw gateway crashes:

- Put an image model as primary LLM → **gateway dead**
- Typo in model reference → **gateway dead**
- Provider goes down, no fallback → **gateway dead**
- No config backup → **hours rebuilding from scratch**

## The Solution

Model Switchboard gives you:

- **3-deep fallback chains** — if Model A fails, B catches it, then C
- **Provider diversity** — never stack the same provider in a chain
- **Pre-flight validation** — blocks unsafe assignments before they touch config
- **Auto-backup** — snapshots config before every change (30 rolling)
- **One-command recovery** — `restore latest` = 2 seconds, not 5 hours
- **Per-task routing** — right model for the right job (conversation, coding, images, heartbeat)
- **Visual dashboard** — see your entire model tree at a glance
- **Setup wizard** — guided first-time configuration

## Quick Start

```bash
# First time? Run the setup wizard:
./scripts/switchboard.sh setup

# See current model assignments:
./scripts/switchboard.sh status

# Auto-generate 3-deep redundant config:
./scripts/switchboard.sh redundancy-apply

# Change a model (validates + backs up first):
./scripts/switchboard.sh set-primary anthropic/claude-opus-4-6

# Something broke? Instant recovery:
./scripts/switchboard.sh restore latest
```

## All Commands

**Getting Started**
- `setup` / `init` — First-time setup wizard with provider detection

**Model Assignment**
- `status` — Show current model tree + health
- `set-primary <model>` — Set primary LLM
- `set-image <model>` — Set image/vision model
- `add-fallback <model>` — Add LLM fallback
- `remove-fallback <model>` — Remove LLM fallback
- `add-image-fallback <model>` — Add image fallback
- `remove-image-fallback <model>` — Remove image fallback

**Redundancy**
- `redundancy [depth]` — Assess current redundancy (default: 3-deep)
- `redundancy-deploy [depth]` — Preview optimal redundant config
- `redundancy-apply [depth]` — Apply redundant config to live gateway

**Discovery & Planning**
- `discover` — List all available models
- `recommend` — Suggest optimal assignments per role
- `dry-run <action> <model>` — Preview changes without applying
- `validate <model> <role>` — Test model-role compatibility

**Backup & Restore**
- `backup` — Manual config backup
- `list-backups` — Show available backups (30 rolling)
- `restore <file|latest>` — Instant restore from any backup

**Import / Export**
- `export [file]` — Export model config as portable JSON
- `import <file>` — Import config (validates all models before applying)

**Diagnostics**
- `health` — Gateway + provider auth status
- `ui` — Generate Canvas dashboard data

## How Redundancy Works

Model Switchboard builds fallback chains with three rules:

1. **Minimum 3 models deep** per critical role
2. **Provider diversity** — never use the same provider twice in a chain
3. **Cost-appropriate** — expensive models for conversation, cheap ones for heartbeat

```
Primary LLM:  anthropic/claude-opus → openai/gpt-5.2 → google/gemini-3-pro
Image:         anthropic/claude-opus → google/gemini-3-pro → openai/gpt-5.1
Heartbeat:     google/gemini-flash → minimax/m1 → groq/llama-4
Coding:        anthropic/claude-opus → openai/gpt-5.2 → google/gemini-3-pro
```

If Anthropic goes down → OpenAI catches it.
If OpenAI goes down → Google catches it.
**Your agent never dies.**

## Task-Model Routing

Different tasks need different models. The dashboard shows two types of roles:

### Core Roles (auto-wired)
These map directly to `openclaw.json` and work immediately:
- **Primary LLM** — Your main conversational model
- **LLM Fallbacks** — Ordered backup chain for primary
- **Image Model** — Vision/image processing
- **Image Fallbacks** — Backup chain for vision

### Extended Roles (planning & reference)
These show as "(not set)" by default. They're a **visual planner** for assigning models to task types. Click any role to assign a model — the assignment is saved to `task-routing.json` and can be referenced when configuring cron jobs and sub-agent spawns.

- **Research** — Deep analysis, web search (e.g., Grok for native search)
- **Coding Pass 1/2/3** — Multi-pass code generation with provider diversity enforcement
- **Social Media** — Creative content generation
- **Web Ops** — Search/scrape capable models
- **Heartbeat** — Cheapest model for periodic polling (e.g., Haiku, Flash)

Extended roles don't auto-wire into OpenClaw's routing yet — they're a reference for how you want to assign models across your automation. Use them to plan your cron job model assignments and sub-agent configurations, then set the actual model param on each job accordingly.

**Example workflow:**
1. Set Research role → `xai/grok-4-fast` in the dashboard
2. When creating research cron jobs, use `model: "xai/grok-4-fast"` in the job config
3. The `validate-cron-models` command checks that all your cron jobs use valid, allowed models

## Supported Providers

Works with every OpenClaw-compatible provider:

- **Anthropic** — Claude Opus, Sonnet, Haiku
- **OpenAI** — GPT-5.x family, Codex
- **Google** — Gemini 3 Pro, 2.5 Flash, Vertex AI
- **OpenCode Zen** — Multi-model proxy
- **Z.AI** — GLM family
- **xAI** — Grok (search-enabled)
- **OpenRouter** — 300+ models from all providers
- **Groq** — Ultra-fast inference
- **Cerebras** — Fast inference
- **MiniMax** — Cost-effective LLM
- **Vercel AI Gateway** — Enterprise proxy

## Safety Guarantees

1. **Fail-closed** — if validation can't run, changes are blocked (not allowed through)
2. **Type enforcement** — image-gen models (DALL-E) can never be set as primary LLM
3. **Atomic writes** — config written to temp file, validated, then renamed (no corruption)
4. **Operation-specific rollback** — each change tracks its own backup (not just "latest")
5. **XSS-safe dashboard** — all data rendered via textContent/createElement, never raw innerHTML
6. **Opus-audited** — full security audit by Claude Opus, all findings fixed

## Requirements

- **OpenClaw** — any recent version
- **Python 3.8+** — pre-installed on macOS and most Linux
- **Bash 3.2+** — pre-installed on macOS, Linux, WSL
- **No external dependencies** — no npm, no pip, no network required

## File Structure

```
model-switchboard/
├── SKILL.md                 — Agent instructions (read by OpenClaw agents)
├── README.md                — This file
├── ARCHITECTURE.md          — Vision and design docs
├── model-registry.json      — Known model capabilities (22 models, 14 providers)
├── scripts/
│   ├── switchboard.sh       — Main CLI (21 commands)
│   ├── validate.py          — Fail-closed validation engine
│   ├── redundancy.py        — Auto-generates optimal fallback chains
│   └── setup.sh             — First-time setup wizard
└── ui/
    └── index.html           — Canvas dashboard (XSS-safe)
```

## For OpenClaw Agents

If you're an AI agent reading this: **NEVER edit `openclaw.json` model fields directly.** Always use this skill's commands. Read `SKILL.md` for complete operating instructions.

## Contributing

- **Add models:** Edit `model-registry.json` with new model capabilities
- **Add providers:** Add to the providers section with auth env vars
- **Report bugs:** Open an issue with your OS, Python version, and error output
- **Share configs:** Use `export` to share your optimal model setup

## License

MIT — Free and open source for every OpenClaw user.

---

*Built with love for the OpenClaw community. No agent should ever go dark because of a config mistake.*
