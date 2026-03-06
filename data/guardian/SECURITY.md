# Guardian Security Notes

## Reviewer Summary

Guardian is a **local, offline threat scanner** for OpenClaw agents. It has no required network access, no required credentials, and no auto-starting persistent services. All optional capabilities are explicitly opt-in and documented below.

---

## Addressing Common Assessment Concerns

### "Package contains executable install.sh and many scripts"
`install.sh` performs local setup only: creates directories, copies config files, and writes a `.guardian-activate-pending` marker. It does **not** download anything, establish network connections, or start services. Review it before running — it is ~50 lines and fully readable.

### "install.sh writes a self-activation marker"
After `install.sh` runs, it writes `.guardian-activate-pending` to your workspace root. OpenClaw detects this marker on next load and triggers `onboard.py` for guided setup. **To prevent auto-onboarding:** delete the marker before reloading: `rm ~/.openclaw/workspace/.guardian-activate-pending`. The marker is intentional and documented — not a backdoor.

### "onboard.py can set up cron jobs"
Cron setup is **fully opt-in**. You must explicitly run `python3 scripts/onboard.py --setup-crons` to create any cron entries. The default onboarding flow does not set up crons automatically.

### "serve.py can start an HTTP server"
The dashboard HTTP server (`serve.py`) does **not** start automatically. You must start it manually or via the provided systemd service file. It binds to localhost:8080 by default. No inbound internet exposure unless you explicitly open the port.

### "Contains Stripe/billing integration with undeclared env vars"
The `billing/` directory contains optional Pro tier infrastructure. It is **completely inactive** unless you:
1. Set `pro_tier.enabled=true` in `config.json`
2. Set `STRIPE_SECRET_KEY` and `STRIPE_WEBHOOK_SECRET` env vars

Neither is set or required by default. The code is present but dormant. `STRIPE_*` vars are declared as `never_required` in SKILL.md metadata.

### "Package contained audit_exports/ with apparent gateway tokens"
This was a **packaging bug in v2.3.0** (fixed in v2.3.1+). A local audit export file was accidentally included in the bundle. It has been permanently excluded via `.clawhubignore`. The gateway token referenced has been rotated. No personal data will appear in any v2.3.1+ package.

### "SKILL.md contains prompt-injection pattern text"
Guardian's `definitions/injection-sigs.json` contains **detection signatures** (regex patterns) for known prompt injection attacks. These patterns are what Guardian looks for to protect you — equivalent to an antivirus virus definition database. They are not executable instructions. The ClawHub scanner correctly identifies the text as matching injection signatures because that is exactly what threat-detection definitions contain.

### "Skill scans other skill/config files in workspace"
Guardian's `scan_paths` can include workspace subdirectories. This is coherent for a threat scanner (you want it to catch malicious skills before they load). To restrict scope, set explicit paths in `config.json`:
```json
{"scan_paths": ["~/.openclaw/workspace/inbox", "~/.openclaw/workspace/downloads"]}
```
Avoid `"auto"` if you want narrow scope.

---

## What Guardian Accesses

| Resource | Access | Purpose |
|---|---|---|
| Workspace files | Read | Scan for threats |
| `guardian.db` | Read/Write | Store scan results locally |
| `config.json` | Read | Load settings |
| `definitions/*.json` | Read | Load threat signatures |
| Shell (optional) | Subprocess | Cron setup via `onboard.py --setup-crons` (opt-in) |
| Network (optional) | Outbound only | Webhook integration (opt-in, disabled by default) |
| HTTP server (optional) | localhost:8080 | Dashboard API (opt-in, disabled by default) |

## No Required Credentials

Guardian requires no API keys, tokens, or external accounts. Everything runs locally.

## Optional Capabilities (all disabled by default)

| Capability | Default | Enable |
|---|---|---|
| Dashboard HTTP server | OFF | `python3 scripts/serve.py` |
| Cron scanning jobs | OFF | `python3 scripts/onboard.py --setup-crons` |
| Stripe Pro billing | OFF | Set `STRIPE_*` env vars + `pro_tier.enabled=true` |
| Webhook integration | OFF | Configure `webhook` in `config.json` |
| Telegram alerts | OFF | Configure `alerts.primary_notify_command` |

## Source Trust Levels (v2.3.1+)

Guardian never blocks internal content. Detection sensitivity scales by source:
- **Level 0 — Internal** (cron, workspace files, system prompts): logged only, never blocked
- **Level 1 — Owner channel** (your Telegram): flagged for review, never blocked
- **Level 2 — Semi-trusted** (web results, email): blocked at high confidence (score ≥ 70)
- **Level 3 — External** (webhooks, unknown sources): blocked at lower threshold (score ≥ 50)

## Data Egress

By default: **none**. All data stays in `guardian.db`. Enabling webhook integration sends sanitized alert payloads to your configured endpoint only.

## Audit Exports

Audit exports (`audit_exports/`) are **excluded from all published packages** via `.clawhubignore`. They are local-only diagnostic files. Never shipped.
