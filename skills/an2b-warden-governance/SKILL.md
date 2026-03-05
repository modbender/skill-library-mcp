---
name: warden-governance
version: 1.0.0
author: AN2B Technologies
license: MIT
category: governance
clawhub: an2b/warden-governance
hooks:
  - before_action
  - after_action
  - on_error
config:
  SENTINEL_API_KEY:
    required: false
    description: Sentinel_OS API key for enterprise governance
  ENGRAMPORT_API_KEY:
    required: false
    description: EngramPort API key for enterprise memory
  WARDEN_FAIL_OPEN:
    required: false
    default: "false"
    description: Allow actions when governance engine fails
  WARDEN_AGENT_ID:
    required: false
    default: openclaw-agent
    description: Bot identifier for audit trail
  WARDEN_POLICY_FILE:
    required: false
    description: Path to custom YAML policy file
  WARDEN_POLICY_PACKS:
    required: false
    description: Comma-separated built-in policy pack names
install: openclaw skill install an2b/warden-governance
---

# War/Den Governance Skill

> **ClawHub Package:** `an2b/warden-governance`
> **Version:** 1.0.0
> **Category:** Governance & Security
> **License:** MIT

---

## What This Skill Does

Every action your OpenClaw bot tries to take is evaluated by War/Den before it executes.

```
Your Bot -> War/Den check -> ALLOW  -> action executes
                          -> DENY   -> action blocked + logged
                          -> REVIEW -> waits for your approval
```

No more deleted emails. No more data exfiltration. No more ungoverned agents.

**Community mode works with zero external dependencies.** No API keys. No cloud.
Just YAML policies, a local SQLite audit log, and a hash chain you can verify.

---

## Install

### From ClawHub (recommended)

```bash
openclaw skill install an2b/warden-governance
```

### From pip

```bash
pip install warden-governance-skill
```

Both methods install to: `~/.openclaw/skills/warden-governance/`

On successful install you'll see:

```
🦞 War/Den governance active.
   Your OpenClaw bot is now governed.
```

### Add to your OpenClaw config

```yaml
skills:
  - name: warden-governance
    config:
      SENTINEL_API_KEY: ""       # optional -- leave blank for community mode
      ENGRAMPORT_API_KEY: ""     # optional -- leave blank for local memory
      WARDEN_FAIL_OPEN: "false"  # block on governance failure (default)
```

### Restart your bot

```bash
openclaw restart
```

That's it. Your bot is now governed.

---

## How It Works

### Hooks

This skill registers three OpenClaw hooks:

| Hook | Purpose |
|------|---------|
| `before_action` | Evaluate every action against policy before execution |
| `after_action` | Write action result to governed memory |
| `on_error` | Log errors to tamper-evident audit trail |

### Action Bridge

All 15 OpenClaw action types are mapped to War/Den governance types:

| OpenClaw Action | War/Den Type | Default Protection |
|-----------------|--------------|-------------------|
| `email.send` | `message.send` | Monitored |
| `email.delete` | `data.write` | **Requires human review** |
| `email.read` | `data.read` | Monitored |
| `file.write` | `data.write` | Monitored |
| `file.delete` | `data.write` | **Requires human review** |
| `file.read` | `data.read` | Monitored |
| `browser.navigate` | `api.call` | Monitored |
| `browser.click` | `api.call` | Monitored |
| `shell.execute` | `code.execute` | **Blocked in production** |
| `api.call` | `api.call` | Monitored |
| `calendar.create` | `data.write` | Monitored |
| `calendar.delete` | `data.write` | **Requires human review** |
| `message.send` | `message.send` | Monitored |
| `code.execute` | `code.execute` | **Blocked in production** |
| `payment.create` | `api.call` | **Requires human review** |

### Policy Engine

Policies are YAML files evaluated in priority order:

```yaml
policies:
  - name: protect-email-delete
    match:
      action.type: data.write
      action.data.openclaw_original: email.delete
    decision: review
    mode: enforce
    priority: 1
    active: true
    reason: "Email deletion requires human review."
```

**Evaluation rules:**
1. Filter to active policies only
2. Sort by priority ascending (lower number = higher priority)
3. First match wins
4. `mode: monitor` -- log but return ALLOW
5. `mode: enforce` -- return the matched decision
6. No match -- default ALLOW

### Pre-built Policy Packs

Load governance instantly with built-in packs:

| Pack | What It Does |
|------|-------------|
| `basic_safety` | Blocks code execution in prod, monitors writes and API calls |
| `phi_guard` | Denies PHI access in dev, requires review for memory export |
| `payments_guard` | Denies payment actions in dev, requires review in prod |

### Audit Trail

Every governance decision is written to a tamper-evident SHA-256 hash chain:

```
Event N:  hash = SHA256(prev_hash + agent_id + action_type + decision + timestamp)
Event N+1: prev_hash = Event N hash
```

Verify the chain at any time:

```python
valid, bad_event_id = audit_log.verify_chain()
```

### Decision Cache

ALLOW decisions are cached for 5 minutes (configurable). DENY and REVIEW are **never** cached -- they always hit the governance engine fresh.

---

## Community vs Enterprise

| Feature | Community (Free) | Enterprise |
|---------|-----------------|------------|
| Policy enforcement | Local YAML | Sentinel_OS cloud |
| Audit trail | Local SQLite + hash chain | Cloud + signed PDF |
| Memory storage | Local SQLite | EngramPort cloud (MandelDB) |
| Memory search | Text search (LIKE) | Vector search (3072-dim) |
| Synthesis | Basic recall | Eidetic AI synthesis |
| Cross-bot memory | -- | Orchestra multi-agent |
| Multi-namespace | 3 max | Unlimited |
| Compliance export | -- | SOC2/HIPAA PDF |
| Cryptographic provenance | Local hash chain | AEGIS (SHA-256 + RSA) |
| Dependencies | **Zero** | `sentinel-client`, `engramport-langchain` |

### Mode Matrix

| `SENTINEL_API_KEY` | `ENGRAMPORT_API_KEY` | Mode |
|--------------------|----------------------|------|
| -- | -- | Full Community |
| Set | -- | Governed Community |
| -- | Set | Memory Enterprise |
| Set | Set | Full Enterprise |

All four modes work with zero code changes. Just environment variables.

---

## Enterprise Upgrade Path

### Sentinel_OS (Governance)

Set `SENTINEL_API_KEY` to upgrade governance from local YAML to Sentinel_OS cloud:

- Real-time policy evaluation via `/api/v1/check`
- Pre-flight checks via `/api/v1/check` (read-only, no side effects)
- Action logging via `/api/v1/ingest` with hash chain integrity
- Run management, alerting, and AI-powered insights
- Python and Node.js SDKs
- Rate limiting: 2000 checks/min, 1000 ingests/min per API key

Get your key at [getsentinelos.com](https://getsentinelos.com)

### EngramPort (Memory via MandelDB)

Set `ENGRAMPORT_API_KEY` to upgrade memory from local SQLite to EngramPort cloud:

- **5 endpoints:** `/register`, `/remember`, `/recall`, `/reflect`, `/stats`
- 3072-dimensional OpenAI embeddings via Pinecone
- AEGIS cryptographic provenance (SHA-256 + RSA signature per memory)
- Namespace-isolated storage (`bot:{slug}:{uid}`)
- Eidetic cross-memory pattern synthesis via GPT-4o-mini
- Multi-agent orchestration with `EngramPortOrchestra`
- Background synthesis with `DreamState`
- LangChain drop-in integration

API keys use format `ek_bot_*` with SHA-256 hashed storage.

Get your key at [engram.eideticlab.com](https://engram.eideticlab.com)

---

## Configuration

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `SENTINEL_API_KEY` | No | `""` | Sentinel_OS key. Blank = community governance |
| `ENGRAMPORT_API_KEY` | No | `""` | EngramPort key. Blank = local memory |
| `WARDEN_FAIL_OPEN` | No | `false` | Allow on governance failure |
| `WARDEN_AGENT_ID` | No | `openclaw-agent` | Bot identifier |
| `WARDEN_POLICY_FILE` | No | built-in | Path to custom YAML policy file |
| `WARDEN_POLICY_PACKS` | No | `""` | Comma-separated pack names |
| `WARDEN_MEMORY_DB` | No | `~/.warden/memory.db` | Local memory path |
| `WARDEN_AUDIT_DB` | No | `~/.warden/audit.db` | Local audit log path |
| `WARDEN_CACHE_TTL` | No | `300` | ALLOW cache TTL in seconds |

### Fail-Open Behavior

| `WARDEN_FAIL_OPEN` | War/Den reachable | War/Den unreachable |
|---------------------|-------------------|---------------------|
| `false` (default) | Normal governance | Action **BLOCKED** |
| `true` | Normal governance | Action **ALLOWED** + warning |

Default is `false` because a governance failure should never silently allow dangerous actions.

---

## Test Proof

This skill ships with a comprehensive test suite. Run it:

```bash
python -m pytest tests/ -v
```

Key test: **The Meta inbox test** simulates the exact incident where an OpenClaw agent deleted 200 emails. With War/Den, all 200 are blocked:

```python
def test_meta_researcher_inbox_protection(self, tmp_path):
    """Simulate the exact Meta inbox incident. All 200 emails blocked."""
    skill = _make_skill(tmp_path, WARDEN_POLICY_FILE=policy_path)
    blocked = 0
    for i in range(200):
        result = skill.before_action(
            {"type": "email.delete", "data": {"email_id": f"msg_{i}"}},
            {"agent_id": "meta-researcher-bot", "env": "prod"},
        )
        if not result["proceed"]:
            blocked += 1
    assert blocked == 200
```

---

## Skill Files

```
warden-governance-skill/
├── SKILL.md                          # This file (ClawHub primary)
├── clawhub.json                      # ClawHub registry metadata
├── README.md                         # Full documentation
├── pyproject.toml                    # Python package config
├── policies/
│   ├── openclaw_default.yaml         # Default governance policies
│   └── policy_packs.py              # Pre-built policy packs
├── warden_governance/
│   ├── __init__.py
│   ├── skill.py                      # Main skill class (hooks)
│   ├── action_bridge.py              # OpenClaw <-> War/Den translation
│   ├── policy_engine.py              # Community policy engine
│   ├── audit_log.py                  # SHA-256 hash chain audit
│   ├── memory_client.py              # Governed memory operations
│   ├── local_store.py                # Local SQLite memory
│   ├── sentinel_client.py            # Enterprise Sentinel_OS client
│   ├── engramport_client.py          # Enterprise EngramPort client
│   ├── upgrade_manager.py            # Mode detection + banner
│   ├── health_check.py               # Enterprise health validation
│   └── settings.py                   # Configuration
└── tests/
    ├── __init__.py
    ├── test_skill.py                 # Skill + Meta inbox tests
    ├── test_policy_engine.py         # Policy engine tests
    ├── test_audit_log.py             # Audit trail tests
    ├── test_action_bridge.py         # Action bridge tests
    ├── test_memory.py                # Memory client tests
    └── test_enterprise.py            # Enterprise upgrade tests
```

---

Built on [Sentinel_OS](https://getsentinelos.com) and [EngramPort](https://engram.eideticlab.com) by [AN2B Technologies](https://an2b.com)

*The lobster protects the inbox.*
