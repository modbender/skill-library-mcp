---
name: boosta-long-to-shorts
description: Create, monitor, and troubleshoot Boosta API video-processing jobs from natural-language requests. Use this skill when a user asks to generate clips from a video URL via Boosta, check job status, fetch completed clip URLs, inspect usage/credits, choose the correct video_type, or handle Boosta API errors and retry logic.
compatibility: Requires network access and valid Boosta API key
metadata:
  author: hundevmode
  version: "1.0"
  clawdbot:
    homepage: "https://boosta.pro"
    source: "https://github.com/hundevmode/boosta-long-to-shorts-openclaw-skill"
    requires:
      env:
        - BOOSTA_API_KEY
---

# Boosta Video Api

## Overview

Use this skill to execute end-to-end Boosta API workflows: submit job, poll until completion, return clip URLs, and handle common API failures.
Prefer the bundled script for deterministic execution and consistent error handling.

## Quick Start Workflow

1. Validate required inputs:
- `video_url` (required)
- `video_type` (required, see [references/video-types.md](references/video-types.md))
- `config_name` (optional)

2. Validate credentials:
- Require `BOOSTA_API_KEY` in environment.
- Never print or store raw API keys in output.

3. Submit job:
- Endpoint: `POST /api/v1/jobs`
- Base URL: `https://boosta.pro/api/v1`
- Body: `video_url`, `video_type`, optional `config_name`

4. Poll status:
- Endpoint: `GET /api/v1/jobs/:job_id`
- Stop when `status=completed` or `status=failed`.
- If completed, return `clip_urls`.

5. Handle API errors:
- `401`: invalid or missing key
- `400`: invalid payload (missing `video_url`, invalid `video_type`)
- `403`: no credits
- `429`: rate limited (respect `retry_after`)
- `active_job_exists`: reuse returned `job_id` and continue polling

## Commands

Use the bundled script:

```bash
python3 scripts/boosta_job.py --help
```

Submit and wait for completion:

```bash
export BOOSTA_API_KEY="sk_live_..."
python3 scripts/boosta_job.py submit \
  --video-url "https://youtube.com/watch?v=xxx" \
  --video-type "conversation" \
  --config-name "My Config" \
  --wait
```

Check status:

```bash
python3 scripts/boosta_job.py status --job-id "job_1234567890_abc123"
```

List completed jobs:

```bash
python3 scripts/boosta_job.py list
```

Check usage:

```bash
python3 scripts/boosta_job.py usage
```

## Output Contract

When user asks to create clips, return:
- `job_id`
- final `status`
- `clips_count` if present
- `clip_urls` when completed
- clear next step if processing/failed

When user asks only to check status, return:
- `job_id`
- current `status`
- `progress`/`step` if present

## Decision Rules

- If user does not provide `video_type`, infer it with [references/video-types.md](references/video-types.md) and state inference explicitly.
- If API returns `active_job_exists`, continue with provided `job_id` instead of creating another job.
- On `429`, wait `retry_after` seconds (fallback to 60 if missing) and retry.
- Keep polling interval between 10 and 20 seconds to avoid spam.
- Avoid parallel job submission per key because API allows one active job at a time.

## References

- API overview and endpoint contracts: [references/api-reference.md](references/api-reference.md)
- Video type selection: [references/video-types.md](references/video-types.md)
- Error handling playbook: [references/errors.md](references/errors.md)
