---
name: sealvera
description: "Tamper-evident audit trail for AI agent decisions. Use when logging LLM decisions, setting up AI compliance, auditing agents for EU AI Act, HIPAA, GDPR or SOC 2, or when a user asks about AI decision audit trails, explainability, or SealVera."
tags:
  - compliance
  - audit
  - ai-governance
  - llm
  - observability
  - eu-ai-act
  - hipaa
  - gdpr
  - soc2
  - fintech
  - tamper-evident
  - explainability
  - langchain
  - openai
  - anthropic
  - responsible-ai
---

# SealVera Skill for OpenClaw

**Cryptographically-sealed, tamper-evident audit trails for every AI decision your agents make.**

SealVera is AI Decision Audit Infrastructure. This skill wires any OpenClaw agent into SealVera
so every decision it makes is logged, cryptographically signed, chained, and monitored —
automatically. Built for teams shipping AI in finance, healthcare, legal, and insurance.

> EU AI Act · SOC 2 · HIPAA · GDPR · FINRA · ISO 42001

---

## Why SealVera?

- **Tamper-evident** — every decision is cryptographically hashed (RSA-2048) and chained; any alteration is detectable
- **Works in 2 lines** — `init()` + one patch call and every LLM decision is logged
- **Full explainability** — captures inputs, outputs, reasoning steps, confidence scores, model used
- **Real-time dashboard** — search, filter, export at [app.sealvera.com](https://app.sealvera.com)
- **Drift detection** — alerts when agent behaviour deviates from its baseline
- **Any LLM** — OpenAI, Anthropic, Gemini, Ollama, LangChain, CrewAI, AutoGen
- **Zero friction** — no new infrastructure, installs in seconds

---

## First time? Run setup

Check if SealVera is configured:

```javascript
const fs = require('fs');
const path = require('path');
const configured = fs.existsSync(path.join(process.env.OPENCLAW_WORKSPACE || process.cwd(), '.sealvera.json'));
```

If `.sealvera.json` does NOT exist, run setup:

```bash
node <skill_dir>/scripts/setup.js
```

Setup will:
1. Ask for your API key (get one free at [app.sealvera.com](https://app.sealvera.com))
2. Verify connectivity and show org/plan info
3. Copy `sealvera-log.js` into the workspace
4. Patch `AGENTS.md` with the mandatory sub-agent audit rule
5. Write `.sealvera.json` config
6. Fire a test log to confirm end-to-end

**One-time setup. After this, every sub-agent you spawn is audited automatically.**

If the user says "install SealVera", "set up SealVera", or "connect SealVera" — run setup, don't just describe it.

---

## How logging works

After setup, logging is automatic for sub-agents via the `AGENTS.md` convention.
For manual logging:

```javascript
const log = require('./sealvera-log');
await log({
  action: 'describe what happened',
  decision: 'COMPLETED',
  input:  { task: '...' },
  output: { result: '...' },
  reasoning: [{ factor: 'outcome', value: 'ok', signal: 'safe', explanation: '...' }]
});
```

Each log entry includes: input/output, reasoning steps, RSA-2048 signature, chain link, timestamp, model, and agent name.

---

## Decision vocabulary

**Task / agent execution:**

| Decision | Meaning |
|---|---|
| `COMPLETED` | Task finished successfully |
| `RESPONDED` | Answered a question / returned output |
| `FAILED` | Task failed |
| `ERROR` | Unexpected exception |
| `ESCALATED` | Handed off to human or higher-level agent |
| `SKIPPED` | Task intentionally not run |
| `PARTIAL` | Completed with caveats |

**Approval / gating:**

| Decision | Meaning |
|---|---|
| `APPROVED` | Request approved |
| `REJECTED` | Request blocked |
| `FLAGGED` | Needs human review |

**Tests:**

| Decision | Meaning |
|---|---|
| `PASSED` | Test passed |
| `FAILED` | Test failed |
| `SKIPPED` | Test skipped |

---

## Sub-agent audit rule

Append this footer to every `sessions_spawn` task:

```
---
MANDATORY: Before you finish, log your result to SealVera:
  const log = require('<workspace>/sealvera-log');
  await log({
    action: '<what you did>',
    decision: 'COMPLETED',
    input: { task: '<summary>' },
    output: { result: '<summary>' },
    reasoning: [{ factor: 'outcome', value: '<result>', signal: 'safe', explanation: '<why>' }]
  });
Vocabulary: task=COMPLETED/FAILED | test=PASSED/FAILED | gate=APPROVED/REJECTED | handoff=ESCALATED
```

---

## Check status

```bash
node <skill_dir>/scripts/status.js
```

---

## Get your API key

Sign up at **[app.sealvera.com](https://app.sealvera.com)** — free tier includes 10,000 decisions/month.

---

## Reference

See `references/api.md` for all SDK methods and log field schema.
See `references/compliance.md` for regulation mapping (EU AI Act, FINRA, HIPAA, GDPR, SOC 2).
