---
name: reelwords-captions
description: Generate captions for short-form videos using the ReelWords (reelwords.ai) Caption API. Use when a user asks to create caption jobs, render stylized subtitles for Reels/TikTok/Shorts, poll caption-job status, or download the rendered captioned video via the ReelWords REST API endpoints (/api/v1/caption-jobs) using an x-api-key (rw_...).
metadata: {"clawdbot":{"emoji":"📝","requires":{"bins":["python3"],"env":["REELWORDS_API_KEY"]}}}
---

# ReelWords Captions

Generate stylized captions for videos using the ReelWords Caption API: create a caption render job, poll until complete, then download the rendered output.

## Setup

### 1) Create a ReelWords account + API key

1. Sign up / log in: https://reelwords.ai
2. Open the **account menu (top-right)** → **API Keys** → **New key**
3. Copy the key (it will look like `rw_...`).

### 2) Provide the API key to OpenClaw

Provide the API key to the process as `REELWORDS_API_KEY`.

Common options:
- Set `REELWORDS_API_KEY` as an environment variable (best when running the script directly)
- If you run via OpenClaw/Clawdbot, store it in `~/.clawdbot/openclaw.json` under `skills.entries.reelwords-captions.env` so the runtime can populate env vars for the skill.

#### Option A: environment variable

```bash
export REELWORDS_API_KEY="rw_..."
```

#### Option B: openclaw.json (recommended)

Edit `~/.clawdbot/openclaw.json` and add an entry:

```json
{
  "skills": {
    "entries": {
      "reelwords-captions": {
        "enabled": true,
        "env": {
          "REELWORDS_API_KEY": "rw_..."
        }
      }
    }
  }
}
```

### Security note

Treat your API key like a password:
- don’t commit it to git
- don’t paste it into public chats
- rotate it in ReelWords if you suspect it leaked

## Usage

Base URL: `https://api.reelwords.ai`

You can use either the included helper script (simplest), or call the REST endpoints directly.

### Option 1: All-in-one helper script (create → poll → download)

From this skill directory:

```bash
python3 scripts/reelwords_caption_job.py \
  --video-url "https://cdn.reelwords.ai/sample.mp4" \
  --style-id "style1" \
  --add-emojis \
  --max-words-per-line 6 \
  --position-y 82 \
  --font-size 54 \
  --highlight-color "#FFD803" \
  --hook-color "#FF5CAA" \
  --out captioned.mp4
```

Notes:
- The script prints the final job JSON to stdout.
- Download logic:
  - prefers `result.downloadUrl` when present
  - otherwise falls back to `GET /api/v1/caption-jobs/{id}/video` (which typically redirects to a signed URL)

### Option 2: Raw API examples (curl)

#### 1) Create job

```bash
curl -sS https://api.reelwords.ai/api/v1/caption-jobs \
  -H "x-api-key: $REELWORDS_API_KEY" \
  -H "content-type: application/json" \
  -d '{
    "videoUrl": "https://cdn.reelwords.ai/sample.mp4",
    "preferences": {
      "style": {
        "styleId": "style1"
      }
    }
  }'
```

Response includes an `id` (save it as `$JOB_ID`).

#### 2) Poll status

```bash
curl -sS https://api.reelwords.ai/api/v1/caption-jobs/$JOB_ID \
  -H "x-api-key: $REELWORDS_API_KEY" \
  -H "accept: application/json"
```

Poll until `status` becomes `completed` (or the response includes `failureReason`/`failureMessage`).

#### 3) Download rendered video

Preferred (when present):
- download from `result.downloadUrl`

Fallback (works in most tenants):

```bash
curl -L https://api.reelwords.ai/api/v1/caption-jobs/$JOB_ID/video \
  -H "x-api-key: $REELWORDS_API_KEY" \
  -o captioned.mp4
```

## Workflow (high level)

1. **Create caption job**: `POST /api/v1/caption-jobs`
   - `videoUrl` (required)
   - `preferences.style.styleId` (required)
   - optional preferences (emojis, max words per line, colors, font sizing, etc.)
2. **Poll job status**: `GET /api/v1/caption-jobs/{id}` until:
   - completed: `result.downloadUrl` is usually present (downloadable)
   - failed: `failureReason` / `failureMessage` present
3. **Download**:
   - `result.downloadUrl`, or
   - `GET /api/v1/caption-jobs/{id}/video` (redirects to a signed URL)

## References

- API summary + curl examples: `references/api.md`

## Notes

- Auth header is `x-api-key: <token>`.
- If you hit usage limits, treat HTTP `402` as “out of credits / limit reached” and surface the response cleanly.
- If ReelWords adds new fields, prefer passing them through in the JSON payload rather than hardcoding assumptions.
