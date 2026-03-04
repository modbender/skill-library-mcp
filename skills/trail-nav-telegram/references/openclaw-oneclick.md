# OpenClaw one-click setup (outsideclaw via trail-nav-telegram)

Goal: make it easy for developers to integrate the full outsideclaw repo/CLI into OpenClaw with minimal steps.

## What it does
1) Install/update outsideclaw repo to `~/.outsideclaw/app/outsideclaw`
2) Patch an OpenClaw config JSON to load the installed skill path
3) Optional: restart OpenClaw gateway

## Usage
```bash
bash scripts/openclaw_oneclick_setup.sh --config /path/to/openclaw.config.json --restart
```

## Safety
- Creates a backup: `<config>.bak`
- Only appends the skill entry if not already present

## Notes
- If `openclaw` CLI isn't on PATH, restart the gateway manually.
