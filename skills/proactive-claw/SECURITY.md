# 🔒 Proactive Claw — Security & Privacy Reference

This document is the authoritative source for all security and privacy properties of Proactive Claw. It is machine-readable by security scanners and human-readable for users.

---

## Data Stored Locally

All data stays on your machine. Nothing is uploaded to the skill author or any third party by default.

| File / DB | Contents | Location | Retention |
|-----------|----------|----------|-----------|
| `credentials.json` | Google OAuth client definition (client_id, client_secret) | `~/.openclaw/workspace/skills/proactive-claw/` | Until you delete it |
| `token.json` | Google OAuth access + refresh token | `~/.openclaw/workspace/skills/proactive-claw/` | Until you delete it or revoke at myaccount.google.com |
| `config.json` | Your settings, calendar IDs, feature flags | `~/.openclaw/workspace/skills/proactive-claw/` | Until you delete it |
| `memory.db` | Meeting outcomes, rules, policies, contacts, notification logs, energy scores, proactivity scores | `~/.openclaw/workspace/skills/proactive-claw/` | Configurable via `memory_decay_half_life_days` (default: 90 days) |
| `proactive_links.db` | Event UIDs, action event UIDs, link graph, suppression list, sent-actions log | `~/.openclaw/workspace/skills/proactive-claw/` | Configurable via `action_cleanup_days` (default: 30 days for canceled actions) |
| `daemon.log` | Daemon run logs | `~/.openclaw/workspace/skills/proactive-claw/` | Not auto-rotated; delete manually if large |

**Nothing is written outside `~/.openclaw/workspace/skills/proactive-claw/`.**

---

## Network Endpoints

### Default (no features enabled)

| Endpoint | When | What is sent | Protocol |
|----------|------|-------------|----------|
| `https://oauth2.googleapis.com` | Once during setup, then on token refresh | OAuth authorization code → access/refresh token | HTTPS |
| `https://www.googleapis.com/calendar/v3/` | Every daemon cycle + calendar scans | Calendar read requests (event list, calendar list), write requests to Actions calendar only | HTTPS |

### Optional (only when feature is explicitly enabled)

| Endpoint | Feature flag | What is sent |
|----------|-------------|-------------|
| `https://api.telegram.org` | `feature_telegram_notifications: true` | Nudge message text |
| `https://api.notion.com` | `feature_cross_skill: true` + `NOTION_API_KEY` | Event title (first 50 chars, search query) |
| GitHub via `gh` CLI | `feature_cross_skill: true` + authenticated `gh` | Read-only: PR/issue list |
| `https://api.openai.com` or other LLM | `feature_llm_rater: true` + cloud `base_url` | Meeting outcome notes + event title + sentiment |
| Your Nextcloud host | `calendar_backend: nextcloud` | CalDAV read/write |
| `https://clawhub.ai` | Only if you run `scripts/setup_clawhub_oauth.sh` manually | `clawhub_token` → receives `credentials.json` only |

### Never contacted

- No analytics servers
- No telemetry endpoints
- No skill author servers
- No package registries at runtime (pip only runs during setup)

---

## Google OAuth Scope

```
https://www.googleapis.com/auth/calendar
```

**Why full calendar scope?** Creating the "Proactive Claw — Actions" calendar requires the full calendar scope. Google does not provide a separate "create calendar" scope.

**Read-only enforcement for your calendars:** All write calls in `cal_backend.py` target only `config["openclaw_cal_id"]` (the Actions calendar ID set during setup). Your other calendars are accessed via read-only API calls (`calendarList().list()`, `events().list()`). This is enforced by code policy, not by OAuth scope restriction.

**To revoke access at any time:** Visit https://myaccount.google.com/permissions and remove "Proactive Claw".

---

## Install Mechanism

| Script | What it does | Network? | Privilege? |
|--------|-------------|----------|-----------|
| `scripts/setup.sh` | `pip3 install` from PyPI, OAuth flow, creates Actions calendar, writes `config.json` | Google OAuth + Calendar API, PyPI | User only, no sudo |
| `scripts/install_daemon.sh` | Writes launchd plist (macOS) or systemd user timer (Linux) | None | User only, no sudo |
| `scripts/setup_clawhub_oauth.sh` | Downloads `credentials.json` from clawhub.ai | clawhub.ai only | User only, no sudo |

**`setup_clawhub_oauth.sh` is NOT called by `setup.sh`.** It is a separate, explicit opt-in.

---

## Daemon Behavior

- **Not installed by default.** You must run `scripts/install_daemon.sh` explicitly.
- **Runs as your user only.** No root, no sudo, no system-level services.
- **Runs every 15 minutes** (configurable via `daemon_interval_minutes`).
- **Controlled by `daemon_enabled` config key** (default: `false` in generated config).
- **Kill switch:** Set `daemon_enabled: false` in `config.json` — daemon will exit on next run without modifying any data.
- **Uninstall:**

```bash
# macOS
launchctl unload ~/Library/LaunchAgents/ai.openclaw.proactive-claw.plist
rm ~/Library/LaunchAgents/ai.openclaw.proactive-claw.plist

# Linux
systemctl --user disable --now openclaw-proactive-claw.timer
rm ~/.config/systemd/user/openclaw-proactive-claw.*
```

---

## Feature Flags

All 27 feature flags default to `false` in the config generated by `scripts/setup.sh`. External features that contact third-party services:

| Flag | Service contacted | Default |
|------|-----------------|---------|
| `feature_cross_skill` | GitHub (via `gh` CLI), Notion API | `false` |
| `feature_telegram_notifications` | Telegram API | `false` |
| `feature_team_awareness` | Other users' shared Google calendars | `false` |
| `feature_llm_rater` | Local Ollama by default; cloud LLM if you change `base_url` | `false` |
| `feature_voice` | Local Whisper only | `false` |

All other feature flags control local-only behavior (SQLite, policy engine, notifications, etc.).

---

## Audit Commands

```bash
# Preview what the daemon WOULD do without writing anything
python3 scripts/daemon.py --simulate --days 3

# See what actions WOULD be planned
python3 scripts/action_planner.py --dry-run

# See what actions WOULD fire
python3 scripts/action_executor.py --dry-run

# System health (DB, daemon, config, calendar, flags, stale data, disk)
python3 scripts/health_check.py

# Export all local data (for inspection or backup)
python3 scripts/export_data.py --export --output ~/proactive-claw-backup --format json
```

---

## Threat Model

| Threat | Mitigation |
|--------|-----------|
| OAuth token exfiltration | `token.json` stays local; never uploaded |
| Unauthorized calendar writes | Write calls only target Actions calendar ID from `config.json`; code-level enforcement |
| Background daemon persistence | User-level only; `daemon_enabled: false` kill switch; explicit uninstall script |
| clawhub.ai credential brokering | `setup_clawhub_oauth.sh` is opt-in only, not called by `setup.sh`; fetches client definition only |
| Third-party data leakage | All external features default `false`; require explicit flag in `config.json` |
| Privilege escalation | No sudo, no root, no system services |
| Malicious package updates | Packages pinned to PyPI; no custom package indexes |
| Data retention | `action_cleanup_days` (default 30), `memory_decay_half_life_days` (default 90) |
