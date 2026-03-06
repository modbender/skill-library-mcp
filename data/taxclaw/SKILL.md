---
name: taxclaw
version: "0.1.0-beta"
description: "Extract, store, and export tax documents (W-2, 1099-DA, all 1099 variants, K-1) using AI. Local-first — your documents never leave your machine. Web UI at localhost:8421."
argument-hint: "open TaxClaw, extract my 1099, parse this tax form, process my W-2"
allowed-tools: Bash, Read, Write
requires: python3, pip
optional: ollama (for local model mode)
---

# taxclaw

Local-first AI tax document extraction skill for OpenClaw.

## 🔐 Security & Permissions Manifest

TaxClaw declares the following permissions transparently. Review before installing.

| Permission | What & Why | Default |
|---|---|---|
| **Read filesystem** | Reads uploaded PDF/image files you provide | Required |
| **Write filesystem** | Stores extracted data at `~/.local/share/taxclaw/` and config at `~/.config/taxclaw/` | Required |
| **Network (local only)** | Binds to `localhost:8421` only — no external network access in default mode | Required |
| **Network (cloud AI)** | Only if you explicitly enable cloud mode in config + acknowledge privacy warning | Opt-in only |
| **Credentials** | None read or stored — no API keys required in local-only mode | N/A |
| **Sensitive data** | Tax documents stay on your machine. Nothing is sent externally in default (Ollama) mode | Local-only |

**TaxClaw does NOT:**
- Exfiltrate documents, fields, or extracted data
- Read files outside of paths you explicitly provide to ingest
- Phone home, send telemetry, or contact external servers (default mode)
- Store or transmit SSN, EIN, or account numbers to any third party

**If you enable cloud mode (Claude):** A mandatory privacy warning is displayed. You must explicitly set `cloud_acknowledged: true` in config before processing begins.

**Audit this skill:** Source code is fully open at [github.com/DougButdorf/TaxClaw](https://github.com/DougButdorf/TaxClaw) (MIT License). Read it before you install it.

## Setup

```bash
bash ~/.openclaw/workspace/skills/taxclaw/setup.sh
```

## Config

Config lives at:
- `~/.config/taxclaw/config.yaml`

Default is local-first (Ollama on your machine). If you enable cloud mode, TaxClaw will refuse to run until you explicitly acknowledge the privacy warning in config.

## Start web UI

```bash
bash ~/.openclaw/workspace/skills/taxclaw/start.sh
# Open: http://localhost:8421
```

## CLI usage

```bash
# Ingest a document
~/.openclaw/workspace/skills/taxclaw/bin/taxclaw \
  ingest path/to/document.pdf --filer doug --year 2025

# List documents
~/.openclaw/workspace/skills/taxclaw/bin/taxclaw list

# Export (wide CSV by default)
~/.openclaw/workspace/skills/taxclaw/bin/taxclaw export --id <doc-id>

# Export long CSV
~/.openclaw/workspace/skills/taxclaw/bin/taxclaw export --id <doc-id> --format long

# Export JSON
~/.openclaw/workspace/skills/taxclaw/bin/taxclaw export --id <doc-id> --format json

# Start server
~/.openclaw/workspace/skills/taxclaw/bin/taxclaw serve
```

## Trigger phrases (OpenClaw agent)

- "extract my tax document"
- "parse this 1099" / "read this W-2"
- "open TaxClaw" / "start taxclaw"
- "process my tax forms"
- "show my tax documents"
