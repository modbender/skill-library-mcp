---
name: adaptive-routing
description: "Routes LLM requests to a local model first (Ollama, LM Studio, llamafile), validates the response quality, and escalates to cloud only when the local result fails. Tracks local vs escalated vs cloud outcomes in a persistent dashboard. Use when: (1) user asks to run a task with a local model first, (2) user wants to reduce cloud API costs or keep requests private, (3) user wants post-outcome quality validation before committing to a local result, (4) user asks to see token savings or the routing dashboard, (5) any request where local-vs-cloud routing should be decided automatically with a quality gate. Supports Ollama, LM Studio, and llamafile as local providers."
metadata: { "openclaw": { "emoji": "🔀", "requires": { "bins": ["python3"] }, "install": [] } }
---

# Adaptive Routing

Route requests to a local LLM first. Validate the response quality. Escalate to cloud only when the local result fails the quality check. Track every outcome in a persistent dashboard.

## Quick Start

### 1. Check if a local LLM is running

```bash
python3 skills/adaptive-routing/scripts/check_local.py
```

Returns JSON: `{ "any_available": true, "best": { "provider": "ollama", "models": [...] } }`

### 2. Route a request

```bash
python3 skills/adaptive-routing/scripts/route_request.py \
  --prompt "Summarize this meeting transcript" \
  --tokens 800 \
  --local-available \
  --local-provider ollama
```

Returns: `{ "decision": "local", "reason": "...", "complexity_score": -1, "complexity_threshold": 3 }`

### 3. Execute with the chosen provider

Send the request to your local provider (Ollama, LM Studio, or llamafile).  
See [references/local-providers.md](references/local-providers.md) for curl examples.

### 4. Validate the response

```bash
python3 skills/adaptive-routing/scripts/validate_result.py \
  --response "The meeting covered three topics..." \
  --exit-code 0
```

Returns: `{ "passed": true, "score": 1.0, "reason": "ok", "should_escalate": false }`

If `should_escalate: true`, re-run step 3 with your cloud provider instead.

### 5. Log the outcome

```bash
# Local success (no escalation needed)
python3 skills/adaptive-routing/scripts/track_savings.py log \
  --kind local_success --tokens 800 --model gpt-4o

# Escalated (local failed validation, used cloud)
python3 skills/adaptive-routing/scripts/track_savings.py log \
  --kind escalated --tokens 800 --model gpt-4o
```

### 6. Show the dashboard

```bash
python3 skills/adaptive-routing/scripts/dashboard.py
```

---

## Full Routing Workflow

```
┌──────────────────────────────────────────────────────────┐
│  1. check_local.py  →  is a local provider running?      │
│                                                           │
│  2. route_request.py  →  local or cloud?                  │
│     · sensitivity check  (private data → local)          │
│     · complexity score   (high score → cloud)            │
│     · availability gate  (no local → cloud)              │
│                                                           │
│  3. Execute with local provider                          │
│                                                           │
│  4. validate_result.py  →  did the response pass?        │
│     · passed=true   → use result   (kind=local_success)  │
│     · passed=false  → re-run cloud (kind=escalated)      │
│                                                           │
│  5. track_savings.py log  →  record the outcome          │
│                                                           │
│  6. dashboard.py  →  show cumulative savings             │
└──────────────────────────────────────────────────────────┘
```

---

## Routing Rules (Summary)

| Condition                                                                     | Route    |
| ----------------------------------------------------------------------------- | -------- |
| No local provider available                                                   | ☁️ Cloud |
| Prompt contains sensitive data (`password`, `secret`, `api key`, `ssn`, etc.) | 🏠 Local |
| Complexity score ≥ threshold (default 3)                                      | ☁️ Cloud |
| Complexity score < threshold                                                  | 🏠 Local |

After routing locally, `validate_result.py` applies a second gate:

| Signal                       | Escalate? |
| ---------------------------- | --------- |
| Empty response               | Yes       |
| Process exit code != 0       | Yes       |
| Timed out                    | Yes       |
| Tool error                   | Yes       |
| Clean response, score ≥ 0.75 | No        |

For full scoring details, see [references/routing-logic.md](references/routing-logic.md).

---

## Configuration

Create `~/.openclaw/adaptive-routing/config.json` to tune thresholds:

```json
{
  "complexity_threshold": 3,
  "token_high_watermark": 4000,
  "token_low_watermark": 500,
  "redact_output": true
}
```

Pass `--config /path/to/config.json` to `route_request.py` to use a custom path.

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

The dashboard reads from `~/.openclaw/adaptive-routing/savings.json` (auto-created).

```
┌───────────────────────────────────────────────┐
│      🔀  Adaptive Routing  ·  Dashboard       │
├───────────────────────────────────────────────┤
│  Local LLM:  ✅  ollama (llama3.2...)         │
├───────────────────────────────────────────────┤
│  Total requests:                           42  │
│  Local (passed):               31  (73.8%)    │
│  Escalated to cloud:                        4  │
│  Cloud (direct):                            7  │
│  Escalation rate:                       11.4%  │
├───────────────────────────────────────────────┤
│  Tokens (local):                       84,200  │
│  Tokens (cloud):                        9,600  │
│  Cost saved (USD):                     $0.4210 │
└───────────────────────────────────────────────┘
```

Reset savings data:

```bash
python3 skills/adaptive-routing/scripts/track_savings.py reset
```

---

## Additional References

- **Routing & validation logic**: [references/routing-logic.md](references/routing-logic.md)
- **Local provider setup** (Ollama, LM Studio, llamafile): [references/local-providers.md](references/local-providers.md)
- **Token estimation & cloud cost table**: [references/token-estimation.md](references/token-estimation.md)
