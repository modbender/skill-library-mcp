---
name: omni-research
description: Multi-source deep research using your own browser. Queries Perplexity, Grok, and Gemini in parallel via CDP — zero API keys, uses your existing subscriptions.
metadata: {"clawdbot":{"emoji":"🔬","requires":{"bins":["python3"],"pip":["httpx","websockets"]}}}
---

# omni-research

Research any topic by querying multiple AI services through your own browser.
No API keys — uses your existing Perplexity Pro, X Premium, Gemini Advanced subscriptions.

## How It Works

1. Connects to your running browser via CDP (Chrome DevTools Protocol)
2. Opens parallel tabs to Perplexity, Grok, and Gemini (you're already logged in)
3. Submits your query, waits for response, extracts answer from each
4. Synthesizes all results into a unified summary

## Prerequisites

- Python 3.10+ with `httpx` and `websockets`
- Chrome, Edge, or any Chromium browser running with CDP:
  ```bash
  # Add to your browser shortcut or launch command (one-time)
  --remote-debugging-port=9222
  ```
- Logged into your AI services in the browser

## Usage

```bash
# All browser sources (Perplexity + Grok + Gemini)
python3 research.py "AIPC market trends 2026"

# Specific sources
python3 research.py --sources perplexity,grok "topic"

# API-only mode (no browser needed)
python3 research.py --sources gemini-api "quick question"

# JSON output
python3 research.py --json "query"
```

## Available Sources

| Source | Type | Requires |
|--------|------|----------|
| `perplexity` | Browser | Perplexity Pro login |
| `grok` | Browser | X Premium / Grok login |
| `gemini` | Browser | Google account login |
| `gemini-api` | API | OpenAI-compatible endpoint |

## Configuration

Optional `~/.config/omni-research/config.json`:

```json
{
  "cdp_port": 9222,
  "cliproxy_url": "http://127.0.0.1:8317/v1",
  "cliproxy_key": "your-key",
  "synthesis_model": "glm-4.7",
  "gemini_api_model": "gemini-2.5-flash"
}
```

## Architecture

```
User's Browser (Chrome/Edge/Comet/Arc, CDP :9222)
  ├── Tab: perplexity.ai     → user's Pro session
  ├── Tab: grok.com           → user's Premium session
  └── Tab: gemini.google.com  → user's Google session
        ↓ WebSocket (CDP Input.insertText + dispatchKeyEvent)
  BrowserBridge (browser.py — httpx + websockets)
        ↓  ← IrisGo runtime replaces this layer
  omni-research skill (parallel query + extract + synthesize)
        ↓
  Markdown output with per-source sections + synthesis
```

## For IrisGo

The `BrowserBridge` in `browser.py` is an abstract interface.
Current implementation uses direct CDP via WebSocket.
IrisGo runtime provides native browser APIs — just swap the bridge layer.

```python
# skill.json requirement
{ "requirements": { "tools": ["browser"] } }
```
