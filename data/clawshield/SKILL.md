---
name: clawshield
display_name: ClawShield
version: 1.1.0
description: "OpenClaw security audit + prompt injection detector. Scans gateway/vulns/cron/PI patterns. Use for frenzy-proofing installs."
category: security
author: Jeffrey Coleman (smallbizailab79@gmail.com)
price: 9.99
inputs: []
outputs:
  - JSON report printed to stdout
---

# ClawShield

## Purpose
Audit a local OpenClaw install for security posture and common prompt-injection indicators. Produces a JSON report for review and alerting.

## Workflow
1. **Canvas present**: Launch the panel server and present the UI.
2. **User config**: Update `config.yaml` (scan frequency, alerts, sensitivity).
3. **Cron setup**: Schedule `scripts/audit.sh` at the chosen cadence.
4. **Report/Alert**: Review JSON output and alert if prompt-injection hits or unexpected open ports are found.

## Usage
### Panel (recommended)
```bash
node scripts/panel-server.js
```
Then present the UI:
- `canvas.present` → `http://localhost:8133` (Scan / Settings / Logs)

### Config (CLI)
```bash
node scripts/config.js get
node scripts/config.js set Scan_freq daily alerts telegram sensitivity high
```

### Audit (CLI)
```bash
bash scripts/audit.sh > report.json
```

## Notes
- Local-only scans; no network calls outside localhost.
- Panel server is local and stores the last report at `logs/last-report.json`.
- `config.yaml` defaults: Scan_freq=daily, alerts=telegram, sensitivity=high.
- Safe for routine security checks and “frenzy-proofing”.

Contact: Jeffrey Coleman | smallbizailab79@gmail.com | Custom audits/enterprise.
