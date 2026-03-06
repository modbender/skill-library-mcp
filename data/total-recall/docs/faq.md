# Frequently Asked Questions

## "OpenClaw already fixed post-compaction amnesia. Why do we need this?"

OpenClaw's fix (#12283) repaired a bug where the compaction summary was malformed. That's important — but compaction is still lossy by design. It takes 200k tokens and crushes them to ~10-20k. Specifics get lost.

Our system pre-empts compaction. Before it fires, the observer has already saved every durable fact to permanent files. OpenClaw's fix makes the exam notes legible. Our system is the friend who took notes during the entire lecture.

## "Does this conflict with OpenClaw's native compaction?"

No — everything is completely complementary. Our files live outside the conversation context. Compaction never touches them. The flow works together: observer saves facts → compaction summarises conversation → new session loads both the summary AND our files.

## "Aren't we inflating the context by loading saved memory?"

Yes, by about 4.5% (~9,000 tokens out of 200k). But without the system, you'd spend 20-30% of context re-explaining things after compaction. It's a net win. The Reflector prevents unbounded growth by consolidating when observations exceed ~8,000 words.

## "What LLM should I use for the observer?"

Any cheap, fast model works. We recommend Gemini Flash via OpenRouter (~$0.001 per run, ~$0.05/day). The observer doesn't need deep reasoning — just fact extraction.

## "Can I use a local model instead of OpenRouter?"

Absolutely. The observer uses any OpenAI-compatible API endpoint. Set these environment variables before running the scripts:

```bash
export OBSERVER_API_URL="http://localhost:8080/v1/chat/completions"
export OPENROUTER_API_KEY="not-needed"  # Still required by the script, any value works
export OBSERVER_MODEL="your-model-name"
```

This works with **llama.cpp** (built-in server), **Ollama** (`http://localhost:11434/v1/chat/completions`), **vLLM**, **LM Studio**, or any server that exposes the `/v1/chat/completions` endpoint.

**Recommended local models:** GLM 4.7 Flash, Qwen 2.5 7B, Gemma 3 12B — anything that can summarise text reliably. You don't need a frontier model for fact extraction.

**Note:** These variables go in your `.env` file or are exported in your shell before running the scripts. They are **not** OpenClaw config (`openclaw.json`) settings — the observer is a standalone script that runs independently of your main agent.

## "Where does OPENAI_BASE_URL / OBSERVER_API_URL go?"

The observer scripts are **standalone bash scripts** — they don't read from OpenClaw's config file (`openclaw.json`) or its `.env`. You configure them via environment variables:

- **`OBSERVER_API_URL`** — The full chat completions endpoint (e.g., `https://openrouter.ai/api/v1/chat/completions`)
- **`OPENROUTER_API_KEY`** — Your API key (or any dummy value for local models)
- **`OBSERVER_MODEL`** — The model name (default: `google/gemini-2.5-flash`)

You can either:
1. Export them in your shell profile (`~/.bashrc`)
2. Add them to a `.env` file in your workspace and `source` it
3. Set them in the cron job environment

The scripts are completely decoupled from your main OpenClaw agent — they just need an LLM endpoint to compress transcripts.

## "Does this work on macOS?"

Yes. The watcher uses `fswatch` instead of `inotifywait`. Everything else is standard bash/jq/curl.
