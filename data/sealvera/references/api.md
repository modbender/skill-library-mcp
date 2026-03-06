# SealVera SDK — API Reference

## Init

```javascript
const SealVera = require('sealvera');

SealVera.init({
  endpoint:      'https://app.sealvera.com',  // required
  apiKey:        process.env.SEALVERA_API_KEY, // required
  autoReasoning: true,    // default: true — injects reasoning prompt
  traceId:       null,    // optional: shared trace ID for multi-agent chains
});
```

## Log a decision

```javascript
await SealVera.log({
  agent:    'agent-name',       // required
  action:   'what happened',    // required — e.g. 'loan_underwriting'
  decision: 'APPROVED',         // required — APPROVED | REJECTED | FLAGGED | HOLD | etc.
  input:    { ...inputData },   // the data the agent saw
  output:   { ...outputData },  // what the agent produced
  reasoning_steps: [            // optional but strongly recommended
    {
      factor:      'credit_score',
      value:       '748',
      signal:      'safe',        // 'safe' | 'risk'
      explanation: 'Above minimum threshold of 680'
    }
  ],
  traceId:  'req_abc123',       // optional — links to a multi-agent trace
  userId:   'user_456',         // optional — for GDPR right-to-explanation
  metadata: { ... },            // optional — any extra fields
});
```

## Wrap an existing client (auto-intercept all calls)

```javascript
// OpenAI
const { OpenAI } = require('openai');
const openai = new OpenAI();
const auditedClient = SealVera.createClient(openai, { agent: 'my-agent' });
// Use auditedClient exactly like openai — all calls are logged automatically

// Anthropic
const Anthropic = require('@anthropic-ai/sdk');
const anthropic = new Anthropic();
SealVera.patchAnthropic(anthropic, { agent: 'my-agent' });
// anthropic is now patched in-place

// OpenRouter
const openrouter = new OpenAI({ baseURL: 'https://openrouter.ai/api/v1', apiKey: process.env.OPENROUTER_API_KEY });
SealVera.patchOpenRouter(openrouter, { agent: 'my-agent' });
```

## Trace context (AsyncLocalStorage)

```javascript
await SealVera.trace({ traceId: 'req_abc', agent: 'orchestrator' }, async () => {
  // All SealVera.log() calls inside here are automatically linked to this trace
  await doSomething();
});
```

## Verify a record

```javascript
const result = await SealVera.verify(logId);
// { valid: true, logId, hash, signature }
```

## Chain integrity check

```javascript
const result = await SealVera.verifyChain(agentName);
// { valid: true, count: 1234, gaps: [] }
```

---

## Decision values (standard set)

Use these consistently so dashboard filters and alert rules work correctly:

| Value | Meaning |
|---|---|
| `APPROVED` | Positive outcome — application/request approved |
| `REJECTED` | Negative outcome — denied |
| `FLAGGED` | Needs human review |
| `HOLD` | Temporarily paused |
| `PENDING_REVIEW` | Queued for manual review |
| `ADVANCE` | Move to next stage |
| `DECLINE` | Soft rejection |
| `SCALE_UP` | Increase resource/limit |
| `PAUSE` | Temporarily stop |
| `MAINTAIN` | No change — continue as-is |

---

## Environment variables

```
SEALVERA_API_KEY        Required — your org API key (sv_...)
SEALVERA_ENDPOINT       Default: https://app.sealvera.com
SEALVERA_AGENT          Agent name shown in dashboard (default: openclaw-agent)
SEALVERA_AUTO_REASONING Set to 'false' to disable auto-reasoning injection
```

---

## REST API (direct, no SDK)

```bash
# Ingest a decision
curl -X POST $SEALVERA_ENDPOINT/api/ingest \
  -H "x-api-key: $SEALVERA_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "agent": "my-agent",
    "action": "loan_decision",
    "decision": "APPROVED",
    "input": { "amount": 50000 },
    "output": { "result": "approved" }
  }'

# Get recent logs
curl "$SEALVERA_ENDPOINT/api/logs?agent=my-agent&limit=10" \
  -H "x-api-key: $SEALVERA_API_KEY"

# Chain integrity
curl "$SEALVERA_ENDPOINT/api/agents/my-agent/chain-verify" \
  -H "x-api-key: $SEALVERA_API_KEY"

# Compliance report
curl "$SEALVERA_ENDPOINT/api/compliance-report?from=2026-01-01&to=2026-03-01" \
  -H "x-api-key: $SEALVERA_API_KEY"
```
