# ragflow-runbook

Runtime operations runbook for RAGFlow: deploy, operate, troubleshoot, monitor.

Version: 0.1.4

---

## Scope

This skill is **ops-only**. It focuses on keeping RAGFlow running and observable.

Included:
- Deployment (git-clone first, download fallback)
- Health checks (liveness/readiness)
- Smoke checks (system endpoints only)
- Alerting helper (via OpenClaw messaging)
- Copy/paste scheduling templates (cron + launchd)

Not included:
- Any application-layer design or content workflows

---

## Requirements

- Required: `python3`, `docker`, `curl`
- Optional: `git` (recommended for deploy)

---

## Quick Start

Deploy (preferred path: git clone).

By default, `deploy.sh` will NOT start containers unless you opt in:

```bash
# Prepare files (git clone path may still run; starting containers is disabled by default)
bash skills/ragflow-runbook/scripts/deploy.sh /opt/ragflow

# Explicitly allow starting containers
RAGFLOW_RUNBOOK_ALLOW_START=1 bash skills/ragflow-runbook/scripts/deploy.sh /opt/ragflow

# If git is not available and you want to allow runtime downloads
RAGFLOW_RUNBOOK_ALLOW_DOWNLOAD=1 RAGFLOW_RUNBOOK_ALLOW_START=1 bash skills/ragflow-runbook/scripts/deploy.sh /opt/ragflow
```

Set env vars (adjust host/port):

```bash
export RAGFLOW_BASE_URL="http://127.0.0.1:9380"
export RAGFLOW_API_KEY="ragflow-..."  # do not paste into chat / do not commit
```

Run checks:

```bash
python3 skills/ragflow-runbook/scripts/ragflow_ping.py
python3 skills/ragflow-runbook/scripts/ragflow_smoke.py
bash skills/ragflow-runbook/scripts/healthcheck.sh
```

---

## File Layout

```
ragflow-runbook/
├── SKILL.md              # Full runbook (ops playbook)
├── README.md             # This file
├── CHANGELOG.md
├── package.json
├── scripts/
│   ├── deploy.sh         # Deploy helper (git clone preferred)
│   ├── healthcheck.sh    # Healthcheck wrapper (calls skill-local scripts)
│   ├── ragflow_ping.py   # Liveness + readiness
│   ├── ragflow_smoke.py  # Ops smoke (system endpoints only)
│   ├── ragflow_status.py # Compact status summary
│   └── ragflow_alert.py  # Alert via OpenClaw messaging
└── examples/
    ├── api-examples.sh   # Ops API examples (system endpoints only)
    └── troubleshooting.md
```

---

## Common Docker Commands

| Action | Command |
|---|---|
| Start | `docker compose up -d` |
| Stop | `docker compose down` |
| Restart | `docker compose restart` |
| Logs | `docker compose logs -f` |
| Status | `docker compose ps` |

---

## References

- RAGFlow docs: https://ragflow.io/docs/
- Upstream repo: https://github.com/infiniflow/ragflow
