# Boosta Long to Shorts Skill for OpenClaw

Create viral short clips from long-form video using the Boosta API directly from OpenClaw workflows.

[![Boosta](https://img.shields.io/badge/Boosta-API-0ea5e9)](https://boosta.pro)
[![Docs](https://img.shields.io/badge/Docs-boosta.pro%2Fapi-22c55e)](https://docs.boosta.pro/api/getting-started)
[![OpenClaw Skill](https://img.shields.io/badge/OpenClaw-Skill-f59e0b)](https://docs.openclaw.ai/tools/skills)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](./LICENSE)

## Quick Links

- Website: [boosta.pro](https://boosta.pro)
- API Docs: [API Getting Started](https://docs.boosta.pro/api/getting-started)
- Auth: [Authentication](https://docs.boosta.pro/api/authentication)
- Endpoints: [API Endpoints](https://docs.boosta.pro/api/endpoints)
- Video Types: [Video Types (API)](https://docs.boosta.pro/api/video-types)
- Errors: [API Errors](https://docs.boosta.pro/api/errors)

## Table of Contents

- [What This Skill Does](#what-this-skill-does)
- [Who This Skill Is For](#who-this-skill-is-for)
- [Features](#features)
- [Project Structure](#project-structure)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [Install as a Skill (skills.sh)](#install-as-a-skill-skillssh)
- [Install from ClawHub](#install-from-clawhub)
- [API Flow](#api-flow)
- [Error Handling](#error-handling)
- [Video Type Mapping](#video-type-mapping)
- [Release Process](#release-process)
- [SEO Keywords](#seo-keywords)
- [License](#license)

## What This Skill Does

`boosta-long-to-shorts` is an OpenClaw-compatible skill that helps agents:

- Submit a new Boosta job from a source video URL
- Poll and track job status
- Return final `clip_urls` once processing is complete
- Handle API errors, retries, and one-active-job constraints
- Map content to the correct Boosta `video_type`

This is designed for production-style automation where reliability and clear status reporting matter.

## Who This Skill Is For

- Creators building short-form clips from YouTube/long videos
- Automation engineers integrating Boosta into AI workflows
- Teams using OpenClaw to orchestrate video generation pipelines
- Agencies scaling clip production across many channels

## Features

- OpenClaw skill with proper `SKILL.md` frontmatter and workflow instructions
- Reusable Python CLI utility: submit, status, list, usage
- `--wait` mode to poll until completion
- `429` retry behavior with `retry_after`
- Handling of `active_job_exists` response
- Reference docs bundled in `references/` for API, errors, and video type selection

## Project Structure

```text
boosta-long-to-shorts/
├── SKILL.md
├── README.md
├── .gitignore
├── agents/
│   └── openai.yaml
├── references/
│   ├── api-reference.md
│   ├── errors.md
│   └── video-types.md
└── scripts/
    └── boosta_job.py
```

## Requirements

- Python 3.9+
- Boosta API key (`BOOSTA_API_KEY`)
- Access to Boosta API endpoints (`https://boosta.pro/api/v1`)

## Installation

### 1) Clone repository

```bash
git clone https://github.com/hundevmode/boosta-long-to-shorts-openclaw-skill.git
cd boosta-long-to-shorts
```

### 2) Set API key

```bash
export BOOSTA_API_KEY="sk_live_..."
```

### 3) Test CLI help

```bash
python3 scripts/boosta_job.py --help
```

## Install as a Skill (skills.sh)

Install directly from GitHub with Vercel skills CLI:

```bash
npx skills add hundevmode/boosta-long-to-shorts-openclaw-skill --skill boosta-long-to-shorts
```

List skills in this repo before install:

```bash
npx skills add https://github.com/hundevmode/boosta-long-to-shorts-openclaw-skill --list
```

## Install from ClawHub

Published package:

```bash
clawhub install boosta-long-to-shorts
```

Search:

```bash
clawhub search boosta-long-to-shorts
```

## Usage

### Submit a job and wait for clips

```bash
python3 scripts/boosta_job.py submit \
  --video-url "https://youtube.com/watch?v=xxx" \
  --video-type "conversation" \
  --config-name "My Config" \
  --wait
```

### Check one job status

```bash
python3 scripts/boosta_job.py status --job-id "job_1234567890_abc123"
```

### List jobs

```bash
python3 scripts/boosta_job.py list
```

### Check credits/usage

```bash
python3 scripts/boosta_job.py usage
```

## API Flow

1. `POST /api/v1/jobs` to create processing job  
2. Receive `job_id` and queue/processing status  
3. Poll `GET /api/v1/jobs/:job_id`  
4. On `status=completed`, return `clip_urls`  

## Error Handling

The skill and CLI are prepared for common Boosta API cases:

- `401 Unauthorized`: missing or invalid key
- `400 Bad Request`: missing/invalid payload
- `403 No Credits`: exhausted credits
- `429 Rate Limited`: retry with `retry_after`
- `active_job_exists`: reuse existing `job_id` and continue polling

Detailed playbook: `references/errors.md`.

## Video Type Mapping

Supported `video_type` values:

- `conversation`
- `gaming`
- `faceless`
- `solo`
- `vlog`
- `movies`

Selection rules and heuristics: `references/video-types.md`.

## Release Process

1. Update files (`SKILL.md`, scripts, references).
2. Bump version when publishing to ClawHub:
```bash
clawhub publish . --slug boosta-long-to-shorts --name "Boosta Long to Shorts" --version <next-semver> --tags latest
```
3. Push to GitHub:
```bash
git add .
git commit -m "chore: release <version>"
git push
```
4. Verify install paths:
```bash
npx skills add hundevmode/boosta-long-to-shorts-openclaw-skill --skill boosta-long-to-shorts
clawhub install boosta-long-to-shorts
```

## SEO Keywords

Boosta API, OpenClaw skill, AI video automation, viral clip generation, Boosta video API integration, short-form video automation, YouTube clip generator, API video processing pipeline.

## License

MIT. See `LICENSE`.
