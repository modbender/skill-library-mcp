---
name: local-first-llm
description: "Routes LLM requests to a local model (Ollama, LM Studio, llamafile) before falling back to cloud APIs. Tracks token savings and cost avoidance in a persistent dashboard. Use when: (1) user asks to run a task with a local model first, (2) user wants to reduce cloud API costs or keep requests private, (3) user asks to see their token savings or LLM routing dashboard, (4) any request where local-vs-cloud routing should be decided automatically. Supports Ollama, LM Studio, and llamafile as local providers."
metadata: { "openclaw": { "emoji": "🏠", "requires": { "bins": ["python3"] }, "install": [] } }
---

# Local-First LLM

Route requests to a local LLM first; fall back to cloud only when necessary. Track every decision to show real token and cost savings.

## Quick Start

### 1. Check if a local LLM is running

```bash
python3 skills/local-first-llm/scripts/check_local.py
```

Returns JSON: `{ "any_available": true, "best": { "provider": "ollama", "models": [...] } }`

### 2. Route a request

```bash
python3 skills/local-first-llm/scripts/route_request.py \
  --prompt "Summarize this meeting transcript" \
  --tokens 800 \
  --local-available \
  --local-provider ollama
```

Returns: `{ "decision": "local", "reason": "...", "complexity_score": -1 }`

### 3. Log the outcome

After executing the request, record it:

```bash
python3 skills/local-first-llm/scripts/track_savings.py log \
  --tokens 800 \
  --model gpt-4o \
  --routed-to local
```

### 4. Show the dashboard

```bash
python3 skills/local-first-llm/scripts/dashboard.py
```

---

## Full Routing Workflow

```
┌─────────────────────────────────────────────────────┐
│  1. check_local.py  →  is a local provider running? │
│                                                      │
│  2. route_request.py  →  local or cloud?             │
│     - sensitivity check  (private data → local)      │
│     - complexity score   (high score → cloud)        │
│     - availability gate  (no local → cloud)          │
│                                                      │
│  3. Execute with the chosen provider                 │
│                                                      │
│  4. track_savings.py log  →  record the outcome      │
│                                                      │
│  5. dashboard.py  →  show cumulative savings         │
└─────────────────────────────────────────────────────┘
```

---

## Routing Rules (Summary)

| Condition                                                                     | Route    |
| ----------------------------------------------------------------------------- | -------- |
| No local provider available                                                   | ☁️ Cloud |
| Prompt contains sensitive data (`password`, `secret`, `api key`, `ssn`, etc.) | 🏠 Local |
| Complexity score ≥ 3                                                          | ☁️ Cloud |
| Complexity score < 3                                                          | 🏠 Local |

For full scoring details, see [references/routing-logic.md](references/routing-logic.md).

---

## Executing with a Local Provider

Once `route_request.py` returns `"decision": "local"`, send the request:

### Ollama

```bash
curl http://localhost:11434/api/generate \
  -d '{"model": "llama3.2", "prompt": "YOUR_PROMPT", "stream": false}'
```

### LM Studio / llamafile (OpenAI-compatible)

```bash
curl http://localhost:1234/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model": "local-model", "messages": [{"role": "user", "content": "YOUR_PROMPT"}]}'
```

---

## Dashboard

The dashboard reads from `~/.openclaw/local-first-llm/savings.json` (auto-created).

```
┌─────────────────────────────────────────┐
│    🧠  Local-First LLM — Dashboard      │
├─────────────────────────────────────────┤
│  Local LLM:  ✅  ollama (llama3.2...)   │
├─────────────────────────────────────────┤
│  Total requests:         42             │
│  Routed locally:         31  (73.8%)    │
│  Routed to cloud:        11             │
├─────────────────────────────────────────┤
│  Tokens saved:       84,200             │
│  Cost saved:           $0.4210          │
└─────────────────────────────────────────┘
```

Reset savings data:

```bash
python3 skills/local-first-llm/scripts/track_savings.py reset
```

---

## Additional References

- **Routing scoring details**: [references/routing-logic.md](references/routing-logic.md)
- **Local provider setup** (Ollama, LM Studio, llamafile): [references/local-providers.md](references/local-providers.md)
- **Token estimation & cloud cost table**: [references/token-estimation.md](references/token-estimation.md)
