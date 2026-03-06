# War/Den Governance Skill for OpenClaw

### Govern your OpenClaw bot in 5 minutes. Zero external dependencies.

[![ClawHub](https://img.shields.io/badge/ClawHub-an2b%2Fwarden--governance-dc2626)](https://clawhub.com/an2b/warden-governance)
[![MIT License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-passing-brightgreen)](https://github.com/jcools1977/warden-governance-skill/actions)

> **Find this skill on ClawHub:** [clawhub.com/an2b/warden-governance](https://clawhub.com/an2b/warden-governance)

---

## The Problem

On February 14, 2026, a Meta AI security researcher asked her OpenClaw agent to triage her inbox. It deleted 200 emails. She had explicitly told it to confirm before acting.

OpenClaw has no governance layer. War/Den fixes that.

## What This Skill Does

Every action your OpenClaw bot tries to take is evaluated by War/Den before it executes:

```
Your Bot -> War/Den check -> ALLOW  -> action executes
                          -> DENY   -> action blocked + logged
                          -> REVIEW -> waits for your approval
```

No more deleted emails. No more data exfiltration. No more ungoverned agents.

## The Meta Inbox Test

This isn't a theoretical concern. We ship a test that simulates the exact incident:

```python
def test_meta_researcher_inbox_protection(self, tmp_path):
    """Simulate the exact Meta inbox incident. All 200 emails blocked."""
    skill = _make_skill(tmp_path, WARDEN_POLICY_FILE=policy_path)

    blocked_count = 0
    for i in range(200):
        result = skill.before_action(
            {
                "type": "email.delete",
                "data": {"email_id": f"msg_{i}", "subject": f"Meeting notes #{i}"},
            },
            {"agent_id": "meta-researcher-bot", "env": "prod", "user": "researcher@meta.com"},
        )
        if not result["proceed"]:
            blocked_count += 1

    # Every single email.delete must be blocked
    assert blocked_count == 200
```

**200 emails. 200 blocked. Every time.** The policy engine returns REVIEW for `email.delete`, which means the agent cannot proceed without human approval.

## Install

### From ClawHub (recommended)

```bash
openclaw skill install an2b/warden-governance
```

### From pip

```bash
pip install warden-governance-skill
```

Both install to: `~/.openclaw/skills/warden-governance/`

### Add to your OpenClaw config

```yaml
skills:
  - name: warden-governance
    config:
      SENTINEL_API_KEY: ""       # optional -- leave blank for community mode
      ENGRAMPORT_API_KEY: ""     # optional -- leave blank for local memory
      WARDEN_FAIL_OPEN: "false"  # block on governance failure (default)
```

### Restart

```bash
openclaw restart
```

You'll see:

```
🦞 War/Den governance active.
   Your OpenClaw bot is now governed.

   Governance: Local
   Memory:     SQLite
   Synthesis:  Basic
   Mode:       Full Community
   Upgrade:    getsentinelos.com
```

## 30 Second Proof

Run this single command to prove governance works:

```bash
python -m pytest tests/test_skill.py::TestMetaResearcherInboxProtection -v
```

Expected output:

```
test_meta_researcher_inbox_protection PASSED
200/200 email deletes blocked.
============================== 1 passed ==============================
```

## What Gets Protected

All 15 OpenClaw action types are mapped to War/Den governance types:

| OpenClaw Action | Default Protection |
|-----------------|-------------------|
| `email.delete` | **Requires human review** |
| `shell.execute` | **Blocked in production** |
| `file.delete` | **Requires human review** |
| `payment.create` | **Requires human review** |
| `code.execute` | **Blocked in production** |
| `calendar.delete` | **Requires human review** |
| `api.call` | Monitored and logged |
| `email.send` | Monitored and logged |
| `browser.navigate` | Monitored and logged |
| `email.read` | Allowed |
| `file.read` | Allowed |
| `file.write` | Monitored and logged |
| `browser.click` | Monitored and logged |
| `message.send` | Monitored and logged |
| `calendar.create` | Monitored and logged |

## Policy Engine

Policies are YAML files with priority-based evaluation:

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

**Evaluation:** Active policies sorted by priority (lower = first). First match wins. Monitor mode logs but allows. Enforce mode blocks or reviews.

### Pre-built Policy Packs

| Pack | What It Does |
|------|-------------|
| `basic_safety` | Blocks code execution in prod, monitors writes and API calls |
| `phi_guard` | Denies PHI access in dev, requires review for memory export |
| `payments_guard` | Denies payment actions in dev, requires review in prod |

Load via config: `WARDEN_POLICY_PACKS: "basic_safety,phi_guard"`

## Audit Trail

Every governance decision is written to a tamper-evident SHA-256 hash chain in local SQLite:

```
Event N:  hash = SHA256(prev_hash + agent_id + action_type + decision + timestamp)
```

Verify at any time:

```python
valid, bad_event_id = skill.sentinel.audit_log.verify_chain()
assert valid is True
```

## Decision Cache

ALLOW decisions are cached for 5 minutes. DENY and REVIEW are **never cached** -- they always hit the policy engine fresh.

Performance proof: 100 identical `api.call` actions result in 1 policy evaluation + 99 cache hits.

## Community vs Enterprise

**Community (free, zero dependencies):**
- Local YAML policy enforcement
- Local SQLite audit log with SHA-256 hash chain
- Local SQLite memory with text search
- Basic synthesis
- Zero external dependencies -- just `pyyaml`

**Enterprise (API keys set):**
- [Sentinel_OS](https://getsentinelos.com) cloud governance with real-time policy evaluation
- [EngramPort](https://engram.eideticlab.com) cloud memory with 3072-dim vector search (MandelDB backend)
- AEGIS cryptographic provenance (SHA-256 + RSA per memory)
- Eidetic AI synthesis across memories
- Multi-agent orchestration via EngramPortOrchestra
- Signed PDF compliance exports (SOC2/HIPAA)

### Mode Matrix

| `SENTINEL_API_KEY` | `ENGRAMPORT_API_KEY` | Mode |
|--------------------|----------------------|------|
| -- | -- | Full Community |
| Set | -- | Governed Community |
| -- | Set | Memory Enterprise |
| Set | Set | Full Enterprise |

All four modes work with **zero code changes**. Just set environment variables.

## Enterprise Upgrade Path

### Sentinel_OS (Governance)

Set `SENTINEL_API_KEY` to upgrade from local YAML to cloud governance:

- Real-time policy evaluation via `/api/v1/check` (2000 req/min)
- Action logging via `/api/v1/ingest` with hash chain integrity
- Run management, alerting, AI-powered insights
- Python and Node.js SDKs
- Get your key: [getsentinelos.com](https://getsentinelos.com)

### EngramPort (Memory via MandelDB)

Set `ENGRAMPORT_API_KEY` to upgrade from local SQLite to cloud memory:

- 5 endpoints: `/register`, `/remember`, `/recall`, `/reflect`, `/stats`
- 3072-dim OpenAI embeddings via Pinecone for semantic search
- AEGIS cryptographic provenance per memory
- Namespace-isolated storage (`bot:{slug}:{uid}`)
- Multi-agent orchestration with `EngramPortOrchestra`
- Get your key: [engram.eideticlab.com](https://engram.eideticlab.com)

## Configuration

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `SENTINEL_API_KEY` | No | `""` | Sentinel_OS key. Blank = community governance |
| `ENGRAMPORT_API_KEY` | No | `""` | EngramPort key. Blank = local memory |
| `WARDEN_FAIL_OPEN` | No | `false` | Allow on governance failure |
| `WARDEN_AGENT_ID` | No | `openclaw-agent` | Bot identifier |
| `WARDEN_POLICY_FILE` | No | built-in | Path to custom YAML policy file |
| `WARDEN_POLICY_PACKS` | No | `""` | Comma-separated pack names |

### Fail-Open Behavior

| `WARDEN_FAIL_OPEN` | War/Den reachable | War/Den unreachable |
|---------------------|-------------------|---------------------|
| `false` (default) | Normal governance | Action **BLOCKED** |
| `true` | Normal governance | Action **ALLOWED** + warning |

Default is `false` because a governance failure should never silently allow dangerous actions.

## Running Tests

```bash
pip install pytest pyyaml
python -m pytest tests/ -v
```

The test suite validates:
- All 15 OpenClaw action type mappings
- Policy engine evaluation (priority, dot-path matching, mode handling)
- SHA-256 hash chain integrity and tamper detection
- Decision cache (ALLOW cached, DENY/REVIEW never cached)
- Governed memory operations (every read/write checked by Sentinel)
- Fail-open and fail-closed behavior
- Mode matrix (all 4 combinations)
- **The Meta inbox test (200 emails, 200 blocked)**
- High-frequency cache performance (100 actions, 1 evaluation)

## Skill Structure

```
warden-governance-skill/
├── SKILL.md                        # ClawHub primary file
├── clawhub.json                    # ClawHub registry metadata
├── README.md                       # This file
├── pyproject.toml                  # Python package config
├── policies/
│   ├── openclaw_default.yaml       # Default governance policies
│   └── policy_packs.py            # Pre-built policy packs
├── warden_governance/
│   ├── __init__.py
│   ├── skill.py                    # Main skill class (hooks)
│   ├── action_bridge.py            # OpenClaw <-> War/Den translation
│   ├── policy_engine.py            # Community policy engine
│   ├── audit_log.py                # SHA-256 hash chain audit
│   ├── memory_client.py            # Governed memory operations
│   ├── local_store.py              # Local SQLite memory
│   ├── sentinel_client.py          # Enterprise Sentinel_OS client
│   ├── engramport_client.py        # Enterprise EngramPort client
│   ├── upgrade_manager.py          # Mode detection + banner
│   ├── health_check.py             # Enterprise health validation
│   └── settings.py                 # Configuration
└── tests/
    ├── test_skill.py               # Skill + Meta inbox tests
    ├── test_policy_engine.py       # Policy engine tests
    ├── test_audit_log.py           # Audit trail tests
    ├── test_action_bridge.py       # Action bridge tests
    ├── test_memory.py              # Memory client tests
    └── test_enterprise.py          # Enterprise upgrade tests
```

---

Built on [Sentinel_OS](https://getsentinelos.com) and [EngramPort](https://engram.eideticlab.com) by [AN2B Technologies](https://an2b.com)

Docs: [warden.an2b.com/docs](https://warden.an2b.com/docs) | ClawHub: [clawhub.com/an2b/warden-governance](https://clawhub.com/an2b/warden-governance)

*The lobster protects the inbox.*
