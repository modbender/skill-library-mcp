---
name: sinkron
version: "1.0.7"
description: >
  Provide AI agents with permanent email identities using Sinkron CLI and Python SDK.
  Requires SINKRON_TOKEN (self-issued by the Sinkron backend via `sinkron register`) —
  this is the primary credential and must be set as an environment variable before use.
  No third-party OAuth involved. Agents register once to receive the token; existing
  agents reuse their prior token. Supports inbox management, message search, deletion,
  and health monitoring. The PyPI package name is `sinkron` (latest: 1.0.2).
homepage: https://www.sinkron.id
source_repository: https://github.com/zororaka00/sinkron
pypi_package: https://pypi.org/project/sinkron/
pypi_package_version: "1.0.2"
install: "pip install sinkron==1.0.2"
author:
  username: "@zororaka00"
  name: Web3 Hungry
  x_account: https://x.com/web3hungry
category: utilities
tags:
  - email
  - api
  - sinkron
  - cli
  - automation
required_env_vars:
  - name: SINKRON_TOKEN
    required: true
    origin: self-issued
    how_obtained: >
      Generated and printed once by the Sinkron backend in response to
      `sinkron register --username USER --name NAME`. This is the only source
      of the token. No third-party service, no OAuth, no external dashboard.
      Existing agents reuse the token from their prior registration.
    storage: "secret manager or restricted environment variable — never source code or logs"
    rotation: "rotate periodically or after any suspected exposure"
primary_credential: SINKRON_TOKEN
---

# Sinkron

Sinkron enables AI agents to own permanent email addresses and manage inboxes programmatically via a CLI and Python SDK.

**Authentication model:** `SINKRON_TOKEN` is **self-issued by the Sinkron platform** — generated once by the Sinkron backend when `sinkron register` is run, printed to the CLI, and never again retrievable. There is no third-party OAuth, no external credential service. Existing agents reuse their token from a prior registration.

Official Website: [https://www.sinkron.id](https://www.sinkron.id)\
Source: [https://github.com/zororaka00/sinkron](https://github.com/zororaka00/sinkron)\
PyPI: [https://pypi.org/project/sinkron/](https://pypi.org/project/sinkron/)

---

## ⚠️ Security Pre-flight Checklist

**Complete every item before installation. Do not skip.**

### 1. Verify Provenance

- [ ] Open [https://www.sinkron.id](https://www.sinkron.id) and confirm it matches the expected project.
- [ ] Visit [https://github.com/zororaka00/sinkron](https://github.com/zororaka00/sinkron) and review the source code.
- [ ] Open [https://pypi.org/project/sinkron/](https://pypi.org/project/sinkron/) and confirm the package owner matches the author (`@zororaka00`).
- [ ] Pin to a specific version (`sinkron==X.Y.Z`) — never install without a version pin.
- [ ] If provenance cannot be confirmed, **treat this skill as untrusted and do not install**.

### 2. Inspect the Package Before Installing

```bash
# Download wheel/tarball without installing, then inspect contents
pip download sinkron==X.Y.Z --no-deps -d /tmp/sinkron-inspect
ls /tmp/sinkron-inspect/
# Unzip the .whl (it's a zip) and review .py source files for
# unexpected network callbacks, obfuscated code, or telemetry
```

### 3. Install in an Isolated Environment First

```bash
# Preferred: use a container or VM for initial testing
docker run --rm -it python:3.11-slim bash
# Inside container:
pip install sinkron==X.Y.Z
sinkron --help
```

### 4. Understand Token Origin Before Use

**`SINKRON_TOKEN` is self-issued — here is exactly where it comes from:**

| Scenario | How to obtain the token |
|---|---|
| **New agent** | Run `sinkron register --username USER --name NAME`. The Sinkron backend generates the token and prints it **once** in the CLI response. Copy it immediately. |
| **Existing agent** | Token was issued during a prior `sinkron register`. Set it directly via `SINKRON_TOKEN` env var. |

The token never comes from a URL fetch, a third-party service, or this skill itself — only from the Sinkron backend's `register` response.

**After obtaining the token:**

- [ ] Store it immediately in a secret manager or restricted `.env` file.
- [ ] Clear terminal / shell history after the token is displayed.
- [ ] Confirm it is not present in logs, CI output, or version-controlled files.
- [ ] Rotate periodically or after any suspected exposure.

---

## Installation

### Step 1 — Check the latest pinned version on PyPI

```bash
pip index versions sinkron
```

### Step 2 — Install with a pinned version

```bash
# Preferred (pinned version)
pip install sinkron==X.Y.Z

# Alternative via uv (also pin version)
uv tool install sinkron==X.Y.Z
```

> ⚠️ Never install without a pinned version. Unpinned installs may pull unreviewed future versions.

### Step 3 — Validate installation

```bash
sinkron --help
```

---

## Best Practice Usage Model

### 1. Installation Policy

Before performing any Sinkron operation:

* Verify `sinkron` is installed.
* If not, follow the **Installation** section above (provenance check first).
* Validate with `sinkron --help` — do not assume success without this step.

---

### 2. Token Lifecycle & Management

#### Where `SINKRON_TOKEN` comes from

```
New agent   → sinkron register --username USER --name NAME
                ↳ Sinkron backend responds with: token: <YOUR_TOKEN>
                ↳ Copy this token immediately — it is shown only once
                ↳ Store in secret manager or restricted env var

Existing agent → token was issued during prior registration
                ↳ Set SINKRON_TOKEN directly from secure storage
```

No third-party service, no OAuth flow, no external dashboard — the token is exclusively generated by the Sinkron backend.

#### Using the token safely

```bash
# After registration: store token (clear shell history after)
export SINKRON_TOKEN="token-from-sinkron-register-output"
sinkron config --token "$SINKRON_TOKEN"

# In CI/CD: inject via secret manager — never hard-code
sinkron config --token "$SINKRON_TOKEN"
```

* **Never** log, print, or expose tokens in shell history, logs, or CI artifacts.
* Use `sinkron health` to check if Sinkron platform is active.
* Rotate tokens periodically and immediately after any suspected exposure.

---

### 3. Idempotent Agent Registration

Before registering, check if the username already exists:

```bash
sinkron agent USERNAME
```

Only register if it does not exist:

```bash
sinkron register --username USER --name NAME
```

This prevents duplication and ensures predictable automation flows.

---

### 4. Safe Inbox Handling

* Use pagination — avoid fetching large inboxes at once.
* Prefer `--search` for filtered access.
* Never delete blindly — always review IDs first.

Safe flow:

1. `sinkron inbox --search KEYWORD`
2. Review IDs
3. `sinkron delete-messages --ids 1,2,3`

---

### 5. Automation Strategy

Always start with a health check:

```bash
sinkron health || exit 1
```

* Log non-sensitive outputs only.
* Implement retry logic on API failures.
* Inject `SINKRON_TOKEN` via CI secret manager — never hard-code in pipeline files.

---

### 6. Python SDK Best Practices

```python
import os
from sinkron import SinkronClient

token = os.getenv("SINKRON_TOKEN")
if not token:
    raise EnvironmentError(
        "SINKRON_TOKEN is not set. "
        "Obtain it from `sinkron register` output and store in a secret manager."
    )

client = SinkronClient(token=token)
messages = client.inbox(page=1)
```

* Initialize client once per runtime.
* Never hardcode tokens — use environment variables exclusively.
* Implement exponential backoff on failures.

---

## Architecture

Sinkron exposes two operational layers:

1. **CLI** — operational / DevOps workflows
2. **Python SDK** — programmatic / application integration

Both communicate with the same Sinkron backend API.

---

## Operational Requirements

* Python 3.8+
* Internet connectivity
* `SINKRON_TOKEN` environment variable (self-issued via `sinkron register`)
* Isolated environment (container/VM) recommended for first-time setup

---

## Security Guidelines

* Verify package provenance and inspect source code before installing.
* Pin to a specific package version — never install unpinned.
* Store `SINKRON_TOKEN` in a secret manager or restricted env var — never in source code.
* Use `sinkron health` to check if Sinkron platform is active instead of viewing config.
* Rotate tokens periodically and after any suspected exposure.
* Restrict shell history after setting tokens (`HISTCONTROL=ignorespace` or `read -s`).
* Test in an isolated environment before production deployment.

---

## Observability Recommendations

**Log:** health status, message counts, deletion results.

**Do NOT log:** tokens, email contents, sensitive metadata.

---

## CLI Commands

### Health Check

```bash
sinkron health
```

### Register New Agent

```bash
sinkron register --username USER --name NAME
```

> **`SINKRON_TOKEN` is issued here.** The Sinkron backend generates and prints the token once in the response. Copy it immediately and store securely. Do not run in logged or shared environments.
>
> ```
> Registration successful.
> username: myagent
> email:    myagent@sinkron.id
> token:    snk_xxxxxxxxxxxxxxxxxxxxxxxx   ← copy immediately, store securely
> ```
>
> Existing agents with a prior token: skip this step, set `SINKRON_TOKEN` directly.

### Get Inbox

```bash
sinkron inbox [--page N] [--search KEYWORD]
```

### Check Email Exists

```bash
sinkron check ADDRESS
```

### Get Message

```bash
sinkron message ID
```

### Delete Messages

```bash
sinkron delete-messages --ids 1,2,3
```

### Delete Inbox

```bash
sinkron delete-inbox [--force]
```

### Get Agent Info

```bash
sinkron agent USERNAME
```

### Check Platform Status

```bash
# Use this command to check if Sinkron platform is active
sinkron health
```

### Set Token

```bash
# Always load from environment variable
sinkron config --token "$SINKRON_TOKEN"
```

### Clear Token

```bash
sinkron config --clear-token
```

---

## Automation Patterns

### Minimal Safe Workflow

```bash
sinkron health || exit 1
sinkron inbox --page 1
```

### Safe Deletion Pattern

```bash
sinkron inbox --search "alert"
# Review IDs before deleting
sinkron delete-messages --ids 10,11
```

---

## Failure Handling Strategy

1. Authentication error → prompt token reconfiguration via `SINKRON_TOKEN` env var.
2. Network error → retry with exponential backoff.
3. Empty inbox → return structured empty response.
4. Invalid ID → prompt verification.

Fail predictably. Avoid silent errors.

---

## Production Readiness Checklist

- [ ] Provenance verified: homepage, GitHub repo, PyPI owner all confirmed
- [ ] Package source code inspected (no unexpected network callbacks or telemetry)
- [ ] Pinned version used during install
- [ ] Tested in isolated environment (container/VM) first
- [ ] `sinkron --help` confirms installation
- [ ] `SINKRON_TOKEN` obtained from `sinkron register` output (new) or prior registration (existing)
- [ ] Token stored in secret manager or restricted env var immediately after registration
- [ ] Shell history cleared after token was displayed
- [ ] Token not present in logs, CI output, or version-controlled files
- [ ] `sinkron health` integrated at workflow start (check if platform is active)
- [ ] `sinkron health || exit 1` integrated at workflow start
- [ ] Logging sanitized (no tokens, no sensitive metadata)
- [ ] Retry strategy implemented
- [ ] Safe deletion logic confirmed (no blind bulk deletes)

---

## Conclusion

This skill provides permanent email identity and inbox automation for AI agents via the Sinkron platform.

`SINKRON_TOKEN` is self-issued by the Sinkron backend at registration — not by any third party. When used with verified provenance, pinned versions, secure token handling, and controlled deletion flows, this skill is production-safe and automation-ready.

**If package provenance cannot be confirmed, do not install. Treat the skill as untrusted until source verification is complete.**