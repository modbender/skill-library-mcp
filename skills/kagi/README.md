# kagi-skill

OpenClaw skill: Kagi API (Search + FastGPT)

## What’s here

- `SKILL.md` — skill metadata + usage notes
- `scripts/` — tiny Python (no deps) wrappers for Kagi API
- `references/` — quick API/auth notes

## Setup

Create a Kagi API token: https://kagi.com/settings/api

Make it available to the scripts:

```bash
export KAGI_API_TOKEN='...'
```

## Usage

```bash
python3 scripts/kagi_search.py "steve jobs" --limit 5
python3 scripts/kagi_fastgpt.py "Summarize Python 3.11" 
```
