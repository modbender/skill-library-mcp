# Grago

**Delegate research and data-fetch tasks to a free local LLM. Save tokens. Use your machine.**

Grago bridges the gap between your OpenClaw agent and local LLMs (Ollama, llama.cpp, etc.) that can't use tools natively. It runs shell scripts to fetch live data from the web, APIs, and local files — then pipes the results into your local model with a focused prompt.

Your cloud model stays sharp. Your local machine does the grunt work. Your token bill drops.

## ⚠️ Security Model

**Grago executes shell commands.** This is intentional — it's the only way to give tool-less local LLMs access to external data.

**Safe for:** Trusted, single-user environments (your own Mac Mini, VPS, workstation)  
**NOT safe for:** Multi-tenant systems, public APIs, untrusted agents

If your OpenClaw agent is compromised via prompt injection, Grago can execute arbitrary commands. This is the trade-off for free local compute. Read `SECURITY.md` in the repo for full details.

## When to Use This Skill

Use Grago when:
- You need live data fetched (web pages, APIs, RSS feeds, logs)
- The task is research-heavy and doesn't need your primary model
- You want to keep data on your own machine (privacy)
- You want to save tokens by offloading analysis to a local LLM

## How It Works

1. **Fetch** — Shell scripts pull live data (curl, jq, grep, etc.)
2. **Analyze** — Results are piped to your local Ollama model with a prompt
3. **Return** — Structured analysis comes back to your OpenClaw agent

## Usage

```bash
# Fetch a URL and analyze locally
grago fetch "https://example.com" \
  --analyze "Summarize the key points" \
  --model gemma2

# Multi-source research from a YAML config
grago research \
  --sources sources.yaml \
  --prompt "What are the main themes across these sources?"

# Pipe any shell command into your local model
grago pipe \
  --fetch "curl -s https://api.example.com/data" \
  --transform "jq .results" \
  --analyze "Identify trends and flag outliers"
```

## Configuration

Config file: `~/.grago/config.yaml`

```yaml
default_model: gemma2        # Your preferred Ollama model
timeout: 30                  # Seconds per fetch
max_input_chars: 16000       # Input truncation limit
output_format: markdown      # markdown | json | text
```

## Requirements

- Ollama installed and running locally (install.sh handles this)
- At least one model pulled in Ollama (gemma2, mistral, llama3, etc.)
- bash, curl, jq

## Installation

```bash
git clone https://github.com/solsuk/grago.git
cd grago && ./install.sh
```

## Notes for the Agent

- Prefer `pipe` mode over `fetch --analyze` for reliability (avoids Ollama TTY spinner issues)
- Default model is whatever is set in `~/.grago/config.yaml`; override per-call with `--model`
- Input is truncated to `max_input_chars` before being sent to the local model
- Local model responses can be slow (5–30s depending on hardware and model size) — this is expected
- Grago is for **research and fetch delegation** — not for tasks requiring your primary model's reasoning
