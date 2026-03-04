---
name: openclaw-skill-scanner
description: Security gate for OpenClaw AgentSkills. Scans folder/ClawHub skills with cisco-ai-defense/skill-scanner before installation. Supports manual scans, staged installs, and auto-quarantine of high-risk skills via systemd.
binaries:
  - uv
  - npx
  - git
  - systemctl
env:
  - OPENCLAW_STATE_DIR
  - OPENCLAW_WORKSPACE_DIR
---

# Skill Scanner Guard

Harden OpenClaw’s skill supply chain:
- Scan skills with **cisco-ai-defense/skill-scanner**
- Block only on **High/Critical**
- Allow **Medium/Low/Info** but warn
- Auto-scan on changes to `~/.openclaw/skills`
- Quarantine failing skills to `~/.openclaw/skills-quarantine`

## Quick start

### Install skill-scanner (repo + uv env)

```bash
cd "$HOME/.openclaw/workspace"
# or wherever you keep repos

git clone https://github.com/cisco-ai-defense/skill-scanner
cd skill-scanner
CC=gcc uv sync --all-extras
```

Note: some environments try `gcc-12` while building `yara-python`; forcing `CC=gcc` avoids that.

## Workflows

### 1) Scan all user skills (manual)

User skills live at:
- `~/.openclaw/skills`

Run:
```bash
$HOME/.openclaw/skills/skill-scanner-guard/scripts/scan_openclaw_skills.sh
```

Outputs go to:
- `/home/rev/.openclaw/workspace/skill_scans/`

### 2) Install a folder skill with scan gate (copy/clone workflow)

Use the wrapper instead of copying directly:
```bash
$HOME/.openclaw/skills/skill-scanner-guard/scripts/scan_and_add_skill.sh /path/to/skill-dir
```

Policy:
- Block only if **High/Critical** exist (unless `--force`)
- Still installs if only Medium/Low/Info exist, but prints a warning summary

### 3) Install from ClawHub with scan gate (staging install)

Install to a staging dir, scan, then copy into `~/.openclaw/skills` only if allowed:
```bash
$HOME/.openclaw/skills/skill-scanner-guard/scripts/clawhub_scan_install.sh <slug>
# optionally
$HOME/.openclaw/skills/skill-scanner-guard/scripts/clawhub_scan_install.sh <slug> --version <version>
```

### 4) Auto-scan + quarantine on change (systemd user units)

Install the units (templates are in `references/`):
```bash
mkdir -p ~/.config/systemd/user
cp -a "$HOME/.openclaw/skills/skill-scanner-guard/references/openclaw-skill-scan."* ~/.config/systemd/user/

systemctl --user daemon-reload
systemctl --user enable --now openclaw-skill-scan.path
```

Behavior:
- Any change under `~/.openclaw/skills/` triggers `scripts/auto_scan_user_skills.sh`
- If High/Critical findings exist, the script moves failing skill directories to:
  `~/.openclaw/skills-quarantine/<skillname>-<timestamp>`
- Reports are written to:
  `/home/rev/.openclaw/workspace/skill_scans/auto/`

Inspect:
```bash
systemctl --user status openclaw-skill-scan.path
journalctl --user -u openclaw-skill-scan.service -n 100 --no-pager
ls -la ~/.openclaw/skills-quarantine
```

## Bundled resources

### scripts/
- `scan_openclaw_skills.sh`: generate markdown reports for user + bundled skills
- `scan_and_add_skill.sh`: scan candidate folder skill; install only if allowed
- `clawhub_scan_install.sh`: stage-install from ClawHub, scan, then install
- `auto_scan_user_skills.sh`: scan-all on `~/.openclaw/skills` changes; quarantine High/Critical failures

### references/
- `openclaw-skill-scan.path` / `openclaw-skill-scan.service`: systemd --user path trigger units
