---
name: Agent Audit Trail Skill
description: Tamper-evident, hash-chained audit logging for AI agents. EU AI Act compliant.
---

# Agent Audit Trail Skill

Tamper-evident, hash-chained audit logging for AI agents. EU AI Act compliant.

## Why

AI agents act on your behalf. From **2 August 2026**, the EU AI Act requires automatic logging, tamper-evident records, and human oversight capability for AI systems. This skill provides all three with zero dependencies.

## Quick Start

### 1. Add to your agent's workspace

```bash
cp scripts/auditlog.py /path/to/your/workspace/scripts/
chmod +x /path/to/your/workspace/scripts/auditlog.py
```

### 2. Log an action

```bash
./scripts/auditlog.py append \
  --kind "file-write" \
  --summary "Created config.yaml" \
  --target "config.yaml" \
  --domain "personal"
```

### 3. Verify integrity

```bash
./scripts/auditlog.py verify
# Output: OK (N entries verified)
```

## Compliance Mapping

| EU AI Act Article | Requirement | How This Skill Helps |
|-------------------|-------------|---------------------|
| **Art. 12** Record-Keeping | Automatic event logging | Every action logged with timestamp, actor, domain, target |
| **Art. 12** Integrity | Tamper-evident records | SHA-256 hash chaining — modification breaks the chain |
| **Art. 14** Human Oversight | Human approval linkage | `--gate` flag links actions to human approval references |
| **Art. 50** Transparency | Auditable records | Human-readable NDJSON, one-command verification |
| **Art. 12** Traceability | Chronological ordering | Monotonic `ord` tokens |

## Event Kinds

Use these standardised event types for consistent audit trails:

| Kind | When to Use |
|------|------------|
| `file-write` | Agent creates or modifies files |
| `exec` | Agent runs a command |
| `api-call` | External API interaction |
| `decision` | AI makes or recommends a decision |
| `credential-access` | Secrets or credentials accessed |
| `external-write` | Agent writes to external systems |
| `human-override` | Human overrides an AI decision |
| `disclosure` | AI identity disclosed to user |

## Full Documentation

See [README.md](README.md) for complete usage, integration examples, security model, and EU AI Act compliance guide.

## Log Format

```json
{
  "ts": "2026-02-24T07:15:00+00:00",
  "kind": "exec",
  "actor": "atlas",
  "domain": "ops",
  "plane": "action",
  "target": "pg_dump production",
  "summary": "Ran database backup",
  "gate": "approval-123",
  "ord": 42,
  "chain": {"prev": "abc...", "hash": "def...", "algo": "sha256(prev\\nline_c14n)"}
}
```

## OpenClaw Integration

Add to `HEARTBEAT.md`:

```markdown
## Audit integrity check
- Run: `./scripts/auditlog.py verify`
  - If fails: alert with line number + hash mismatch
  - If OK: silent
```

## Requirements

- Python 3.9+ (zero external dependencies)
- MIT License

---

Built with 🔐 by [Roosch](https://github.com/roosch269) and [Atlas](https://github.com/roosch269/agent-audit-trail)
