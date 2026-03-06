# SealVera Integrations

SealVera works with any framework that can make an HTTP POST or run Python/Node.
No vendor lock-in. No proprietary protocol.

---

## Quick comparison

| Platform | Method | Code changes? |
|---|---|---|
| **Any Python agent** | `SEALVERA_AUTOLOAD=1` | Zero |
| **LangChain** | `SealVeraCallbackHandler` | One line |
| **CrewAI / AutoGen** | `sealvera.log()` | 3 lines |
| **OpenClaw (Node)** | Native skill | Zero |
| **Any Node.js agent** | `NODE_OPTIONS=--require autoload.js` | Zero |
| **n8n / Make** | HTTP Request node | Zero |
| **Any language** | `curl` / raw HTTP POST | Zero |

---

## Python — zero-touch

```bash
pip install sealvera

export SEALVERA_API_KEY=sv_...
export SEALVERA_AGENT=my-agent
export SEALVERA_AUTOLOAD=1

python your_agent.py
# Every OpenAI/Anthropic call is logged — no code changes
```

Intercepts: `openai.ChatCompletion` (sync + async), `anthropic.Messages.create` (sync + async).

---

## Python — manual log

```python
import sealvera

sealvera.init(api_key="sv_...", agent="my-agent")
sealvera.log(
    action="evaluate_transaction",
    decision="APPROVED",
    input={"tx_id": "123", "amount": 150},
    output={"risk_score": 0.12},
    reasoning=[{"factor": "risk", "value": "0.12", "signal": "safe",
                "explanation": "Below 0.5 threshold"}]
)
```

---

## LangChain

```python
from sealvera.callbacks import SealVeraCallbackHandler
import sealvera

sealvera.init(api_key="sv_...", agent="my-langchain-agent")
handler = SealVeraCallbackHandler()

from langchain_openai import ChatOpenAI
llm = ChatOpenAI(callbacks=[handler])
# Every LLM call, chain run, and tool use is now logged
```

Captures: model, prompt preview, response text, token usage, latency, errors.
Works with: LangChain, LangGraph, any chain/agent that accepts callbacks.

Install extra: `pip install sealvera[langchain]`

---

## CrewAI

```python
import sealvera
from crewai import Crew

sealvera.init(api_key="sv_...", agent="research-crew")

result = crew.kickoff()
sealvera.log(
    action="crew_run",
    decision="COMPLETED",
    input={"task": "market research"},
    output={"result": str(result)[:500]},
    reasoning=[{"factor": "outcome", "value": "success",
                "signal": "safe", "explanation": "All agents completed"}]
)
```

---

## AutoGen

```python
import sealvera

sealvera.init(api_key="sv_...", agent="autogen-pipeline")

# Wrap your GroupChat.run():
with sealvera.trace("autogen-run-001") as t:
    chat_result = groupchat.run(task)
    t.log(
        action="groupchat_run",
        decision="COMPLETED",
        output={"messages": len(chat_result.chat_history),
                "summary": chat_result.summary[:300]}
    )
```

---

## Python decorator

```python
@sealvera.audit(action="process_payment")
def process_payment(amount, customer_id):
    return {"status": "ok"}

# COMPLETED on success, FAILED on exception — automatic
```

---

## Node.js — zero-touch

```bash
npm install sealvera

export SEALVERA_API_KEY=sv_...
export SEALVERA_AGENT=my-agent
export NODE_OPTIONS="--require sealvera/autoload"

node your_agent.js
# Every OpenAI/Anthropic call is logged — no code changes
```

---

## OpenClaw

```bash
clawhub install sealvera
# Agent reads SKILL.md, runs setup.js, done
# Every sub-agent spawned is now audited automatically
```

---

## n8n

Use the **HTTP Request** node at the end of any AI workflow:

- Method: `POST`
- URL: `https://app.sealvera.com/api/ingest`
- Header: `x-sealvera-key: sv_...`
- Body (JSON):
```json
{
  "agent":    "n8n-workflow",
  "action":   "={{ $workflow.name }}",
  "decision": "COMPLETED",
  "input":    {"trigger": "={{ $json }}"},
  "output":   {"result": "={{ $json.output }}"}
}
```

---

## Make (Integromat)

Use **HTTP → Make a request**:
- URL: `https://app.sealvera.com/api/ingest`
- Method: POST
- Header: `x-sealvera-key` → your key
- Body: JSON with same shape as above, using `{{variable}}` syntax

---

## Raw HTTP (any language)

```bash
curl -X POST https://app.sealvera.com/api/ingest \
  -H "x-sealvera-key: sv_..." \
  -H "Content-Type: application/json" \
  -d '{
    "agent":    "my-agent",
    "action":   "classify_document",
    "decision": "APPROVED",
    "input":    {"doc_id": "abc123"},
    "output":   {"category": "safe", "confidence": 0.94},
    "reasoning_steps": [
      {"factor": "confidence", "value": "0.94", "signal": "safe",
       "explanation": "Above 0.9 threshold"}
    ]
  }'
```

Response: `{"ok": true, "id": "uuid"}`

---

## Payload schema

| Field | Type | Required | Notes |
|---|---|---|---|
| `agent` | string | ✓ | Agent/system name |
| `action` | string | ✓ | What it did |
| `decision` | string | ✓ | See vocabulary |
| `input` | object | ✓ | Input data |
| `output` | object | ✓ | Output/result |
| `reasoning_steps` | array | recommended | Evidence trail |
| `id` | string | — | UUID (auto if omitted) |
| `timestamp` | ISO string | — | Server time if omitted |
| `model` | string | — | e.g. `gpt-4o` |
| `traceId` | string | — | Group into one trace |
| `traceName` | string | — | Trace label |

---

## Decision vocabulary

| Context | Decisions |
|---|---|
| Task agent | `COMPLETED` `RESPONDED` `FAILED` `ERROR` `ESCALATED` `SKIPPED` `PARTIAL` |
| Test runner | `PASSED` `FAILED` `SKIPPED` `ERROR` |
| Approval gate | `APPROVED` `REJECTED` `FLAGGED` |

---

## Trace linking

Group related decisions from multiple agents into one audit trail:

```python
# Python
with sealvera.trace("order-123", "Order Processing") as t:
    t.log(action="validate",  decision="COMPLETED", ...)
    t.log(action="fraud_check", decision="APPROVED", ...)
    t.log(action="fulfil",    decision="COMPLETED", ...)
```

```js
// Node.js
await SealVera.trace('order-123', async () => {
  await validateAgent.run(order);
  await fraudAgent.evaluate(order);
  await fulfilAgent.process(order);
});
```

All entries appear as one linked trace on the dashboard with full timeline view.

---

## Rate limits

| Plan | Decisions/month | Agents |
|---|---|---|
| Free | 1,000 | 1 |
| Pro | 50,000 | 10 |
| Business | Unlimited | Unlimited |

`HTTP 429` on limit with `{ error, limit, used, upgradeUrl }`.
