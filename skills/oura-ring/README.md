# Oura Ring — OpenClaw Skill

An [OpenClaw](https://openclaw.ai) skill that syncs your daily health data from Oura Ring into markdown files. OpenClaw can then reference your health and fitness data in conversation.

## What it syncs

- **Sleep** — duration, stages (deep/light/REM/awake), sleep score, bedtime/wake time
- **Readiness** — score, temperature deviation, HRV balance, recovery index
- **Activity** — steps, calories, distance, active minutes
- **Stress** — high stress minutes, recovery minutes
- **Heart Rate** — resting, min, max
- **SpO2** — blood oxygen percentage
- **Workouts** — type, duration, distance, calories

## Example output

```markdown
# Health — February 8, 2026

## Sleep: 7h 12m
Deep: 1h 30m | REM: 1h 57m | Light: 3h 45m | Awake: 0h 15m
Sleep Score: 82
Bedtime: 23:15 | Wake: 06:27
Efficiency: 92 | Restfulness: 85 | Timing: 78

## Readiness: 85
Temp Deviation: +0.3°C
HRV Balance: 90 | Resting HR: 88 | Recovery Index: 92
Sleep Balance: 78 | Activity Balance: 85

## Activity: 8,432 steps | 2,100 cal
Distance: 6.2 km | Active: 45 min

## Stress
High Stress: 120 min | Recovery: 340 min

## Heart Rate
Resting: 58 bpm | Min: 48 bpm | Max: 142 bpm

## SpO2: 96%

## Workouts
- **Running** — 28:15, 5.0 km, 320 cal
```

Sections are only included when data is available.

## Setup

### Requirements

- Python 3.10+
- [uv](https://docs.astral.sh/uv/) (no pip install needed — dependencies are inline)
- An Oura Ring account

### Environment variables

```bash
export OURA_TOKEN="your_personal_access_token"
```

Get your token at https://cloud.ouraring.com/personal-access-tokens

### Run it

```bash
# Sync today
uv run scripts/sync_oura.py

# Sync a specific date
uv run scripts/sync_oura.py --date 2026-02-07

# Sync the last 7 days
uv run scripts/sync_oura.py --days 7
```

Markdown files are written to `health/YYYY-MM-DD.md`.

### Install as an OpenClaw skill

```bash
ln -s /path/to/ouraskill ~/.openclaw/skills/oura-ring
```

### Cron

Schedule the sync to run every morning so your data stays up to date automatically. OpenClaw's `cron` tool can handle this, or use a system crontab:

```bash
0 7 * * * OURA_TOKEN="..." uv run /path/to/ouraskill/scripts/sync_oura.py
```

## Auth notes

Oura uses personal access tokens — no SSO, no Cloudflare, no token caching needed. The token doesn't expire unless you revoke it. Get yours at https://cloud.ouraring.com/personal-access-tokens.
