---
name: stravacli
description: Use the stravacli terminal tool to access Strava data (athlete profile, activities, streams, routes, segments, clubs, gear, uploads) and perform limited write actions (activity update/upload). Trigger when the user asks for Strava metrics/history/exports or wants Strava automation via CLI.
---

# stravacli

Use `stravacli` for Strava operations from terminal.

## Prerequisites

This skill depends on the external CLI project:
- Source: https://github.com/Brainsoft-Raxat/strava-cli

Install `stravacli` before using this skill:
- Recommended (release binary):
  - Download latest from: https://github.com/Brainsoft-Raxat/strava-cli/releases/latest
- Or with Go:
  - `go install github.com/Brainsoft-Raxat/strava-cli/cmd/stravacli@latest`

Then verify binary is available in PATH:
- `stravacli --version`

## Setup

- Authenticate before data commands:
  - Local: `stravacli auth login`
  - Headless/VPS: `stravacli auth login --remote`, then complete with `stravacli auth login --auth-url '<callback-url>'`
- Verify auth: `stravacli auth status`

## Read commands (preferred by default)

- Athlete profile: `stravacli athlete me --json`
- Athlete stats: `stravacli athlete stats --json`
- Athlete zones: `stravacli athlete zones --json`
- List activities: `stravacli activities list --per-page 10 --json`
- Activity details: `stravacli activities get <id> --json`
- Activity laps: `stravacli activities laps <id> --json`
- Activity streams: `stravacli activities streams <id> --json`
- Routes list/get: `stravacli routes list --json` / `stravacli routes get <id> --json`
- Export route file: `stravacli routes export <id> --format gpx --out ./route.gpx`
- Segments/starred/explore: `stravacli segments starred --json`, `stravacli segments explore --bounds <swlat,swlng,nelat,nelng> --json`
- Clubs: `stravacli clubs list --json`
- Gear: `stravacli gear get <id> --json`
- Upload status: `stravacli uploads get <uploadId> --json`

## Write commands (ask/confirm first)

- Update activity metadata: `stravacli activities update <id> --name 'New name' --description '...'`
- Upload activity file: `stravacli activities upload --file ./run.fit --yes --json`

Always confirm intent before write actions.

## Output conventions

- Use `--json` when results need parsing or reuse.
- Keep user summaries concise; include key metrics and IDs.
- If a command fails with auth errors, suggest `stravacli auth status` then re-login.
