---
name: Groq API Inference
slug: groq-api
version: 1.0.0
homepage: https://clawic.com/skills/groq-api
description: Build and debug Groq API chat and speech workflows with low-latency routing, structured outputs, and production-safe patterns.
changelog: Initial release with Groq API workflows, model routing guidance, and troubleshooting playbooks for chat and speech.
metadata: {"clawdbot":{"emoji":"⚡","requires":{"bins":["curl","jq"],"env":["GROQ_API_KEY"]},"os":["linux","darwin","win32"]}}
---

## Setup

On first use, read `setup.md` for activation preferences, credential verification, and default workflow setup.

## When to Use

User needs to build, integrate, or troubleshoot Groq API inference for chat, tool calling, or speech transcription. Agent handles request shaping, model routing, failure recovery, and safe production patterns.

## Architecture

Memory lives in `~/groq-api/`. See `memory-template.md` for structure.

```
~/groq-api/
├── memory.md           # Status, activation preference, and defaults
├── requests/           # Reusable payload snippets
├── logs/               # Optional debug snapshots
└── experiments/        # Prompt/model A-B notes
```

## Quick Reference

Use these files as decision aids, not as static docs: pick the smallest file that resolves the current blocker.

| Topic | File |
|-------|------|
| Setup process | `setup.md` |
| Memory template | `memory-template.md` |
| Request patterns | `api-patterns.md` |
| Model routing | `model-selection.md` |
| Failures and recovery | `troubleshooting.md` |

## Core Rules

### 1. Verify Auth and Endpoint Before Any Work
Check `GROQ_API_KEY` first and use `Authorization: Bearer $GROQ_API_KEY` for every request. Use `https://api.groq.com/openai/v1` as the base URL and confirm access with `/models`.

```bash
curl -s https://api.groq.com/openai/v1/models \
  -H "Authorization: Bearer $GROQ_API_KEY" | jq '.data[0].id'
```

### 2. Start with a Minimal Deterministic Payload
Begin with small prompts and explicit format instructions. Add complexity only after the baseline call is stable.

### 3. Route by Task, Not by Habit
Use separate model choices for:
- Fast interactive chat
- High-accuracy reasoning
- Speech transcription

Choose from live `/models` output instead of hardcoding assumptions.

### 4. Design for Retry and Degradation
For `429` and `5xx`, retry with exponential backoff and capped attempts. If a model is overloaded, fail over to a compatible backup model and log the swap.

### 5. Validate Output Before Downstream Actions
If output feeds code execution or data writes, enforce JSON schema or strict parsing before acting. Reject malformed output early.

### 6. Treat Speech as a Separate Reliability Path
Speech uploads have different failure modes than chat. Validate input format, check file size, and surface transcription confidence when available.

### 7. Keep Secrets and User Data Scoped
Never store API keys in files. Keep request logs sanitized and avoid persisting full sensitive prompts unless the user explicitly asks.

## Common Traps

- Using stale model IDs copied from old examples -> call `/models` and select available IDs at runtime.
- Sending giant prompts without truncation -> latency spikes and timeout risk.
- Ignoring `429` backoff guidance -> repeated failures under load.
- Mixing chat and transcription assumptions -> wrong endpoint and payload format.
- Trusting free-form text for automation -> parse and validate before executing.

## External Endpoints

All network traffic should be limited to these Groq endpoints for explicit inference tasks requested by the user.

| Endpoint | Data Sent | Purpose |
|----------|-----------|---------|
| https://api.groq.com/openai/v1/models | None (GET) | Discover available models |
| https://api.groq.com/openai/v1/chat/completions | Prompt messages and options | Chat completions |
| https://api.groq.com/openai/v1/audio/transcriptions | Audio file and transcription params | Speech-to-text |

No other data is sent externally.

## Security & Privacy

**Data that leaves your machine:**
- Prompt content sent to Groq inference endpoints
- Audio content sent to Groq transcription endpoint when requested

**Data that stays local:**
- Workflow preferences in `~/groq-api/memory.md`
- Optional local debug notes in `~/groq-api/logs/`

**This skill does NOT:**
- Store `GROQ_API_KEY` in project files
- Access files outside `~/groq-api/` for persistence
- Call undeclared third-party endpoints
- Modify itself or other skills

## Trust

By using this skill, prompts and optional audio content are sent to Groq.
Only install if you trust Groq with that data.

## Related Skills
Install with `clawhub install <slug>` if user confirms:
- `api` — reusable REST patterns, auth, and error handling
- `models` — model comparison and selection heuristics
- `ai` — current AI landscape checks before implementation decisions
- `fine-tuning` — adaptation workflows when prompting is not enough
- `langchain` — orchestration patterns for multi-step LLM pipelines

## Feedback

- If useful: `clawhub star groq-api`
- Stay updated: `clawhub sync`
