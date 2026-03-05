# War/Den Upgrade Guide

### Community to Enterprise in 5 minutes.

---

## Where You Are Now

Community mode is running. Your bot is governed locally:

```
🦞 War/Den governance active.
   Governance: Local
   Memory:     SQLite
   Mode:       Full Community
```

This is real governance. YAML policies enforce every action. Every decision is logged to a tamper-evident SHA-256 hash chain. Zero external dependencies.

But there are ceilings:
- Text search only (no semantic recall)
- 3 namespace max
- No cross-bot memory sharing
- No signed compliance exports
- Basic synthesis only

---

## Step 1: Add Sentinel_OS (Governance Cloud)

**What you get:** Cloud policy evaluation, real-time alerting, AI-powered insights, signed PDF audit exports, multi-tenant RBAC.

**How:**

1. Get your API key at [getsentinelos.com](https://getsentinelos.com)
2. Add to your skill config:

```yaml
skills:
  - name: warden-governance
    config:
      SENTINEL_API_KEY: "snos_your_key_here"
```

3. Restart: `openclaw restart`

You'll see:

```
🦞 War/Den governance active.
   Governance: Sentinel_OS
   Memory:     SQLite
   Mode:       Governed Community
```

**API surface you unlock:**

| Endpoint | Rate Limit | Purpose |
|----------|-----------|---------|
| `POST /api/v1/check` | 2000/min | Pre-flight policy evaluation |
| `POST /api/v1/ingest` | 1000/min | Action submission + audit |
| `GET /api/v1/runs` | -- | Run management |
| `GET /api/v1/integrity` | -- | Hash chain verification |
| `GET /api/v1/export/pdf` | -- | Signed compliance reports |
| `POST /api/v1/insights/ask` | 10/min | AI-powered Q&A |
| `POST /api/v1/insights/suggest-policies` | 10/min | Policy suggestions |

**SDKs:** Python (`sentinel-client`) and Node.js (`@sentinel-os/client`)

---

## Step 2: Add EngramPort (Memory Cloud via MandelDB)

**What you get:** Vector search (3072-dim), AEGIS cryptographic provenance, Eidetic AI synthesis, multi-agent orchestration, unlimited namespaces.

**How:**

1. Register at [engram.eideticlab.com](https://engram.eideticlab.com) or via API:

```bash
curl -X POST https://mandeldb.com/api/v1/portal/register \
  -H "Content-Type: application/json" \
  -d '{"bot_name": "my-openclaw-bot", "bot_type": "assistant"}'
```

2. Add to your skill config:

```yaml
skills:
  - name: warden-governance
    config:
      ENGRAMPORT_API_KEY: "ek_bot_your_key_here"
```

3. Restart: `openclaw restart`

You'll see:

```
🦞 War/Den governance active.
   Governance: Local
   Memory:     EngramPort
   Mode:       Memory Enterprise
```

**Memory endpoints you unlock:**

| Endpoint | Purpose |
|----------|---------|
| `/remember` | Store memory with vector embedding + AEGIS hash |
| `/recall` | Semantic search across memories |
| `/reflect` | LLM-powered insight synthesis |
| `/stats` | Memory count, insights, activity |
| `/orchestrate` | Cross-agent synthesis (conductor key) |

**AEGIS Provenance:** Every memory gets a cryptographic proof:
```
strand_a = SHA-256(content)
strand_b = SHA-256(embedding_metadata)
provenance = SHA-256(strand_a + strand_b + timestamp)
signature = RSA(provenance, private_key)
```

---

## Step 3: Full Enterprise (Both Keys)

Set both keys for the complete governed memory pipeline:

```yaml
skills:
  - name: warden-governance
    config:
      SENTINEL_API_KEY: "snos_your_key_here"
      ENGRAMPORT_API_KEY: "ek_bot_your_key_here"
```

```
🦞 War/Den governance active.
   Governance: Sentinel_OS
   Memory:     EngramPort
   Synthesis:  Eidetic AI
   Mode:       Full Enterprise
```

**Full enterprise pipeline:**

```
OpenClaw action
    |
    v
Action Bridge (15 types -> 9 War/Den types)
    |
    v
Sentinel_OS /api/v1/check
    |
    +-- ALLOW --> action executes --> EngramPort /remember
    |
    +-- DENY  --> blocked + audit log + alert
    |
    +-- REVIEW --> held for human approval
```

---

## Mode Matrix

| `SENTINEL_API_KEY` | `ENGRAMPORT_API_KEY` | Mode | Governance | Memory |
|--------------------|----------------------|------|-----------|--------|
| -- | -- | Full Community | Local YAML | SQLite |
| Set | -- | Governed Community | Sentinel_OS | SQLite |
| -- | Set | Memory Enterprise | Local YAML | EngramPort |
| Set | Set | Full Enterprise | Sentinel_OS | EngramPort |

All four modes: zero code changes. Just environment variables.

---

## Pricing

| Tier | What You Get | Price |
|------|-------------|-------|
| Community | Local YAML + SQLite + hash chain | **Free forever** |
| Sentinel_OS | Cloud governance + alerting + insights | [getsentinelos.com/pricing](https://getsentinelos.com/pricing) |
| EngramPort Starter | 10,000 memories, 3 namespaces | $29/mo |
| EngramPort Pro | 100,000 memories, 10 namespaces | $99/mo |
| EngramPort Enterprise | Unlimited | Custom |

All plans include AEGIS cryptographic provenance.

---

## Install Enterprise Dependencies

Community mode has zero dependencies (just `pyyaml`).
Enterprise mode needs `httpx`:

```bash
pip install warden-governance-skill[enterprise]
```

Or manually:

```bash
pip install httpx>=0.24
```

---

## Verify Your Setup

```bash
python -c "
from warden_governance.settings import Settings
from warden_governance.upgrade_manager import UpgradeManager

config = Settings.from_env()
mode = UpgradeManager(config).detect_mode()
print(f'Mode: {mode[\"mode\"]}')
print(f'Governance: {mode[\"governance\"]}')
print(f'Memory: {mode[\"memory\"]}')
"
```

---

Built on [Sentinel_OS](https://getsentinelos.com) and [EngramPort](https://engram.eideticlab.com) by [AN2B Technologies](https://an2b.com)
