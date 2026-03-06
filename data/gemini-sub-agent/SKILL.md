---
name: gemini-sub-agent
description: >
  Use Google Gemini as a free sub-agent via a Google One / Gemini Advanced subscription (no API key or API credits needed).
  Use when: (1) delegating tasks that would normally cost Sonnet/Haiku credits, (2) processing large documents or long-context tasks (1M token window),
  (3) running agentic coding tasks autonomously, (4) any text analysis, summarization, or Q&A task.
  Replaces paid cloud models for medium-complexity tasks.
  NOT for: tasks needing OpenClaw-native tools (web_search, sessions_spawn, Telegram), real-time data, or tasks requiring OpenClaw context.
---

# gemini-sub-agent

Use Google Gemini (via subscription, $0 API cost) as a sub-agent inside OpenClaw workflows.

## Setup

Run once on a fresh machine:
```bash
bash skills/gemini-sub-agent/scripts/setup.sh
```

Then authenticate (headless VPS flow):
1. On VPS: `gcloud auth application-default login --no-browser` → copy the `--remote-bootstrap` URL
2. On laptop: `gcloud auth application-default login --remote-bootstrap="<URL>"` → copy the `localhost:8085` output
3. Paste `localhost:8085` output back into VPS prompt
4. Complete Gemini CLI OAuth: `GOOGLE_GENAI_USE_GCA=true gemini -p "hello"` → paste auth code

Credentials are cached indefinitely and auto-refresh.

## Available Models

| Model | Use for |
|---|---|
| `gemini-3.1-pro-preview` | **Default** — latest flagship, best reasoning |
| `gemini-2.5-pro` | Stable coding tasks, multi-file edits |
| `gemini-3-flash-preview` | Fast summaries, quick Q&A |
| `gemini-3-pro-preview` | Previous gen Pro, reliable fallback |
| `gemini-2.5-flash` | Lightweight fallback |

## Usage Patterns

### 1. Simple text task (exec)
```bash
ask-gemini "your prompt here"
ask-gemini -m gemini-2.5-pro "your prompt"
```

### 2. Pipe large content (long-context)
```bash
cat large_file.txt | ask-gemini "summarize this in 5 bullets"
cat report.md | ask-gemini "extract all action items"
```

### 3. Agentic coding (replaces Swift/Sonnet for 30-200 line tasks)
```bash
cd /path/to/project
GOOGLE_GENAI_USE_GCA=true gemini -m gemini-2.5-pro -y -p "write a script that..."
```
`-y` = yolo mode (auto-approves all file writes and shell commands). Gemini reads/writes files autonomously.

### 4. Pipe files directly into agentic session
```bash
cat existing_script.py | GOOGLE_GENAI_USE_GCA=true gemini -m gemini-2.5-pro -y -p "refactor this to add error handling"
```

## Routing Rules (when to use Gemini vs others)

| Task | Use |
|---|---|
| Text, analysis, summarization | `ask-gemini` |
| Medium coding (30–200 lines) | Gemini agentic (`-y`) instead of Swift/Sonnet |
| Large file / long-context | `ask-gemini` (1M token window) |
| Web search / research | Research agent (Grok) — Gemini has no web access |
| Multi-agent orchestration | OpenClaw native (sessions_spawn) |
| Complex architecture / debugging | Codex (Opus) — escalate if Gemini fails twice |

## Escalation

If Gemini returns wrong output twice on the same task → escalate to Swift (Sonnet) or Codex (Opus).
Log the failure in `failures/hot_antipatterns.md` with the task type.

## Scripts

- `scripts/setup.sh` — Full install: gemini-cli + gcloud + ask-gemini wrapper
- `scripts/ask-gemini` — The wrapper script itself (copy to `/usr/local/bin/`)
