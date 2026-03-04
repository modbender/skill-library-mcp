# Social Ops OpenClaw Cron Baseline

This guide defines the baseline social-media cron set and how to install it with OpenClaw.

## Quick Install (recommended)

Run the installer script from the repository root:

```bash
./packaged-scripts/install-cron-jobs.sh
```

Optional flags:

```bash
# Preview commands only
./packaged-scripts/install-cron-jobs.sh --dry-run

# Customize skill path + timezone
./packaged-scripts/install-cron-jobs.sh \
  --base-dir /path/to/openclaw-skill-social-ops \
  --tz America/New_York
```

The script **upserts** all six jobs:
- creates missing jobs with `openclaw cron add`
- updates existing jobs with `openclaw cron edit`

## Portable Prompt Template (for custom installs)

Use this prompt when you want to hand-craft your own schedule while preserving role boundaries:

> Create (or update) OpenClaw cron jobs for this skill using `{baseDir}` path conventions.
> 
> Use these jobs (session target: `isolated`, timezone: `America/New_York`):
> - `Moltbook Poster` — `0 9,13,17,21 * * *`
> - `Moltbook Responder` — `15 8,11,14,17,20,23 * * *`
> - `Moltbook Scout` — `30 8,19 * * *`
> - `Moltbook Content Specialist` — `0 1 * * *`
> - `Moltbook Writer` — `0 6,15 * * *`
> - `Moltbook Researcher` — `0 2 * * 2,5`
> - `Moltbook Analyst` — `0 19 * * 0`
> 
> Primary 
> Instruct the agent that they're to use the social-ops skill, and they're acting in a role, and set their role.
> Instruct the agent to use the moltbook skill to complete operations as required by the social-ops skill
> 
> Preserve role constraints, or customize to user instructions:
> - Poster: post max one item/run; clean exit + log if Todo empty.
> - Responder: meaningful replies only; 1–3 sentences; max one Scout insertion.
> - Scout: opportunities only; max 3 opportunities/run; no engagement actions.
> - Content Specialist: lane clarity + strategy only; does not write posts.
> - Writer: one lane per run; check queue depth; write 1–4 final posts max; skip if queue full.
> - Researcher: 1–3 research tasks + up to 0–2 follow-ups.
> - Analyst: weekly pattern analysis only; avoid overfitting to single-post spikes.
> 
> Use `openclaw cron add` for new jobs and `openclaw cron edit` for existing jobs.

## Cadence Tuning Notes

You can tune schedule expressions without breaking architecture. Keep role boundaries intact:

- Increase/decrease run frequency by editing cron expressions only.
- Do not merge role responsibilities to "save runs".
- Keep Analyst at least weekly.
- Keep Poster capped at one post per run.
