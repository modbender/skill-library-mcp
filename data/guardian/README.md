# 🛡️ Guardian — Security scanner for OpenClaw agents

Detects prompt injection, credential exfiltration, tool abuse, and social engineering in real time. Runs locally with bundled signatures.

---
## Install

```bash
clawhub install guardian
cd ~/.openclaw/skills/guardian && ./install.sh
```

## Install & safety note
This package includes executable scripts (`install.sh`, optional onboarding/API/webhook helpers).
Review `install.sh` before running in production environments.

## Onboarding checklist (fast)
1) Optional: `python3 scripts/onboard.py --setup-crons` (scanner/report/digest crons)
2) `python3 scripts/admin.py status` (confirm running)
3) `python3 scripts/admin.py threats` (confirm signatures loaded; should show 0/blocked)
4) Optional: review `config.json` scan paths and thresholds

## Scan scope
Guardian scans configured workspace paths and may read other skill/config files under those paths for detection. Use narrow `scan_paths` in `config.json` if needed.

## Quick commands
```bash
python3 scripts/admin.py status          # running?
python3 scripts/admin.py threats         # list detected threats
python3 scripts/admin.py report          # full summary
python3 scripts/admin.py update-defs     # update signatures (bundled by default)
```
Add `--json` to any command for machine-readable output.

## Dashboard
```bash
cd skills/guardian/dashboard && python3 -m http.server 8091
# http://localhost:8091/guardian.html
```

## Optional components
- **Cron helper**: `scripts/onboard.py --setup-crons` (scanner/report/digest crons)

## Python API
```python
from core.realtime import RealtimeGuard

guard = RealtimeGuard()
result = guard.scan_message("test payload", channel="telegram")
if guard.should_block(result):
    print(result.top_threat)
```

## What it protects against
- Prompt injection / indirect injection
- Credential patterns / exfiltration attempts
- Tool abuse patterns (read → send)
- Social engineering / fake authority

## How it works
- Bundled signatures in `definitions/*.json` (regex-based)
- Real-time pre-scan + batch scan
- Logs to SQLite (`guardian.db`)

## Permissions (declared)
- `read_workspace`, `write_workspace`
- `shell_optional` (cron helper)
- `network_optional` (webhook/HTTP API — opt-in)

MIT License. Questions? [clawhub.ai/bluemax30001/guardian](https://clawhub.ai/bluemax30001/guardian)
