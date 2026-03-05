# Grago

**Stop burning tokens. Start using your machine.**

An OpenClaw skill that lets your agent delegate research and data-fetch tasks to a free local LLM running on your own hardware — 24/7, no cloud costs.

---

## ⚠️ Security Notice

**Grago executes shell commands by design.** This is intentional and necessary — local LLMs can't use tools natively, so Grago bridges the gap by running commands on your behalf.

**Risk:** If your OpenClaw agent is compromised or prompt-injected, Grago can execute arbitrary commands on your machine.

**Safe for:**
- ✅ Personal Mac Mini / VPS running your own OpenClaw agent
- ✅ Trusted, single-user environments
- ✅ Developers who understand the security model

**NOT safe for:**
- ❌ Multi-tenant systems
- ❌ Public-facing agent APIs
- ❌ Environments with untrusted agents

Read [SECURITY.md](SECURITY.md) for the full explanation of why "vulnerabilities" are actually features.

If this security model doesn't work for you, stick with paid API services instead.

---

## The Problem

You're running OpenClaw. Your agent is sharp. But every research task, every web fetch, every "go look that up" burns tokens. Cloud models are expensive.

Meanwhile, you've got a Mac Mini (or any capable machine) sitting there doing nothing. It could be running a local LLM for **free**. But there's a catch:

> Small local LLMs can't use tools. They can't browse the web, call APIs, or fetch live data. They're powerful — but blind.

So your expensive cloud model keeps doing all the heavy lifting, and your hardware collects dust.

## The Fix

Grago bridges that gap. It's an OpenClaw skill that lets your agent delegate research and fetch tasks to your local machine — for free.

Grago handles the tool work that local LLMs can't: it fetches URLs, hits APIs, reads files, and transforms data using shell scripts. Then it pipes the results directly into your local model with a focused prompt.

**Your OpenClaw agent stays sharp. Your local machine does the legwork. Your token bill drops.**

---

## Who Is This For?

- You use OpenClaw and your token costs are real
- You have a Mac Mini, M-series Mac, or any machine capable of running Ollama
- You want your agent doing 24/7 research without a cloud bill
- You want your local models earning their keep
- You keep your data on your own hardware

**Requirements:**
- OpenClaw (any plan)
- A machine capable of running Ollama (Mac Mini M2+, MacBook Pro M-series, or equivalent)
- Tested with: Gemma, Mistral, Llama, Qwen, GLM, and more

---

## Installation

```bash
# Clone the repo
git clone https://github.com/solsuk/grago.git
cd grago

# Run the installer (sets up Ollama + a default model if not already installed)
./install.sh
```

The installer will:
1. Check for Ollama — install it if missing
2. Pull a recommended local model (Gemma 2 9B by default)
3. Copy `SKILL.md` to your OpenClaw workspace skills folder
4. Create `~/.grago/config.yaml` with sensible defaults

---

## Usage

### Fetch a URL and analyze with your local model

```bash
grago fetch "https://news.ycombinator.com/" \
  --analyze "Summarize the top 5 stories" \
  --model gemma2
```

### Multi-source research

```bash
grago research \
  --sources sources.yaml \
  --prompt "What are competitors charging for similar tools?"
```

### Chain any shell command into your local model

```bash
grago pipe \
  --fetch "curl -s https://api.example.com/stats" \
  --transform "jq .results" \
  --analyze "Flag anything unusual or worth noting"
```

---

## As an OpenClaw Skill

Once installed, your OpenClaw agent can call Grago directly:

1. Agent receives a research task from you
2. Instead of burning cloud tokens, it calls `grago`
3. Grago fetches the data locally using shell/curl
4. Passes results to your local Ollama model with a focused prompt
5. Returns the analysis back to your OpenClaw agent

Your cloud model handles the thinking. Your local machine handles the fetching and grunt analysis. Best of both worlds.

---

## Configuration

Config lives at `~/.grago/config.yaml`:

```yaml
default_model: gemma2        # Ollama model to use
timeout: 30                  # Seconds per fetch
max_input_chars: 16000       # Truncate input to fit context window
output_format: markdown      # markdown | json | text
```

### sources.yaml Example

```yaml
sources:
  - name: hacker_news
    type: web
    url: "https://news.ycombinator.com/"

  - name: competitor_pricing
    type: web
    url: "https://competitor.com/pricing"

  - name: local_logs
    type: file
    path: "/var/log/myapp/*.log"
    transform: "tail -100"

  - name: live_api
    type: api
    url: "https://api.example.com/v1/stats"
    headers:
      Authorization: "Bearer ${API_KEY}"
```

---

## Commands

| Command | Description |
|---------|-------------|
| `grago fetch <url>` | Fetch a URL, optionally analyze |
| `grago research --sources <yaml>` | Multi-source fetch + analysis |
| `grago pipe --fetch <cmd>` | Chain shell command → local model |
| `grago version` | Show version |
| `grago help` | Show help |

---

## Dependencies

- `bash`, `curl`, `jq` (standard on macOS)
- [Ollama](https://ollama.ai) (installed automatically by `install.sh`)
- Optional: `yq` for YAML sources file parsing, `pup` for HTML parsing

---

## Purchase

Grago is available for **$5 one-time** at [underclassic.com](https://underclassic.com).

No subscription. No cloud fees. Lifetime updates.

---

## License

Single-user license. One purchase, one person. Don't redistribute.

---

*Built for [OpenClaw](https://openclaw.ai) — the personal AI agent platform.*
