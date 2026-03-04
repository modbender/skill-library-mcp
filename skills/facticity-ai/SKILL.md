---
name: facticity-ai
description: Complete Facticity.AI integration - fact-check claims, extract claims from content, transcribe links, check link reliability, check credits, and monitor task status
user-invocable: true
command-dispatch: tool
command-tool: http.request
command-arg-mode: raw
metadata:
  {
    "openclaw": {
      "emoji": "🔍",
      "homepage": "https://app.facticity.ai",
      "requires": {
        "env": ["FACTICITY_API_KEY"]
      },
      "primaryEnv": "FACTICITY_API_KEY"
    }
  }
---

# Facticity.AI Complete Integration

A comprehensive skill for interacting with the Facticity.AI API. Supports fact-checking claims, extracting claims from text/video, transcribing links, checking link reliability using MediaBias data, checking API credits, and monitoring async task status.

## API Base URL

**Base URL:** `https://api.facticity.ai`

All API endpoints use this base URL. References to `{BASE_URL}`.

## Behavior

**First, check if `FACTICITY_API_KEY` is set and not empty. If it is missing or empty, return this onboarding message:**

```
⚠️ API Key Not Configured

To use this skill, you need to set up your Facticity.AI API key:

1. Visit https://app.facticity.ai/api to get your API key
2. Set the key as an environment variable:
   export FACTICITY_API_KEY=your_api_key_here
   
   Or add it to your OpenClaw config (~/.openclaw/openclaw.json):
   {
     "skills": {
       "entries": {
         "facticity-ai": {
           "enabled": true,
           "apiKey": "your_api_key_here"
         }
       }
     }
   }

3. Restart OpenClaw after configuration

Get your API key at: https://app.facticity.ai/api
```

**If the API key is present, determine the operation based on the command and proceed:**

### 1. Fact-Check (`/fact-check`)

When the command starts with `/fact-check` or the input is a claim to fact-check:

**Endpoint:** `POST {BASE_URL}/fact-check`

**Headers:**
- `X-API-KEY: ${FACTICITY_API_KEY}`
- `Content-Type: application/json`

**Body:**
```json
{
  "query": "<raw command input (remove /fact-check prefix if present)>",
  "timeout": 60,
  "mode": "sync"
}
```

Return the JSON response verbatim. The response includes:
- `Classification`: "True" or "False"
- `overall_assessment`: Detailed assessment text
- `evidence`: Array of evidence sources
- `sources`: Detailed source assessments
- `bias`: Bias metrics (if available)
- `task_id`: Task ID for async tracking

**Usage:**
```
/fact-check "Vaccines contain microchips"
/fact-check "The unemployment rate dropped in 2023"
```

**Async Mode:** For long-running fact-checks, set `mode: "async"` in the request body. The API will return a `task_id` that can be checked with `/check-task-status`.

### 2. Extract Claims (`/extract-claim`)

When the command starts with `/extract-claim` or the input is a URL or text to extract claims from:

**Endpoint:** `POST {BASE_URL}/extract-claim`

**Headers:**
- `X-API-KEY: ${FACTICITY_API_KEY}`
- `Content-Type: application/json`

**Body:**
```json
{
  "input": "<raw command input (remove /extract-claim prefix if present)>",
  "content_type": "text",
  "timestamp": false,
  "audio_transcript_enabled": false,
  "language_code": "en"
}
```

**Note:** For video URLs (YouTube, TikTok, Instagram), the API will auto-detect and transcribe. If you need transcription explicitly enabled, set `audio_transcript_enabled: true` in the request body.

Return the JSON response verbatim.

**Usage:**
```
/extract-claim "The Earth is flat and NASA is lying about it"
/extract-claim https://youtube.com/watch?v=abc123
/extract-claim https://tiktok.com/@user/video/123
/extract-claim https://instagram.com/p/abc123
```

**Supported Content Types:**
- **Text**: Direct text input
- **Video URLs**: YouTube, TikTok, Instagram (auto-transcribes)
- **Language**: Set `language_code` for non-English content (default: "en")

**Response Format:**
- `status`: "ok" on success
- `transcript`: Transcribed content (for video URLs)
- `title`: Video/article title (if available)
- `description`: Content description (if available)
- `claims`: Array of extracted claim strings
- `overall_assessment`: Summary of extraction

### 3. Get Credits (`/get-credits`)

When the command is `/get-credits` or user wants to check API credits:

**Endpoint:** `GET {BASE_URL}/get-credits`

**Headers:**
- `X-API-KEY: ${FACTICITY_API_KEY}`

No request body required.

Return the JSON response verbatim. The response includes:
- `email`: User email associated with the API key
- `api_key`: The API key (masked)
- `credits_left`: Number of credits remaining
- `duration_seconds`: Duration period (typically 3600 seconds)

**Usage:**
```
/get-credits
```

**Response Format:**
```json
{
  "email": "user@example.com",
  "api_key": "your_api_key_here",
  "credits_left": 1482,
  "duration_seconds": 3600
}
```

### 4. Check Task Status (`/check-task-status`)

When the command starts with `/check-task-status` or the input is a task ID:

**Endpoint:** `GET {BASE_URL}/check-task-status?task_id=<task_id>`

**Headers:**
- `X-API-KEY: ${FACTICITY_API_KEY}`

The raw command input should be the task_id from a previous async fact-check request (remove `/check-task-status` prefix if present).

**Query Parameter:**
- `task_id`: The unique ID of the task to check (from the raw command input)

Return the JSON response verbatim.

**Usage:**
```
/check-task-status 1234567890abcdef
```

Or with the task_id from a previous async fact-check:
```
/fact-check "Long claim..." --mode async
# Returns task_id: abc123
/check-task-status abc123
```

**Response Format:**

For completed tasks:
```json
{
  "status": "Completed",
  "input_query": "Original Input query",
  "classification": "False",
  "overall_assessment": "This claim is inaccurate.",
  "evidence_sources": ["Source 1", "Source 2"],
  "disambiguation": "Clarifies the context...",
  "detailed_source_reports": ["Detailed source report 1", "Detailed source report 2"],
  "task_id": "1234567...",
  "bias_quality_metrics": [
    {
      "source": "https://www.politico.com",
      "bias": -5.238666666666666,
      "quality": 46.45
    }
  ]
}
```

For in-progress tasks, returns current status and progress information.

### 5. Transcribe Link (`/transcribe-link`)

When the command starts with `/transcribe-link` or the input is a URL to transcribe:

**Endpoint:** `POST {BASE_URL}/transcribe-link`

**Headers:**
- `X-API-KEY: ${FACTICITY_API_KEY}`
- `Content-Type: application/json`

**Body:**
```json
{
  "url": "<raw command input (remove /transcribe-link prefix if present)>"
}
```

The raw command input should be the URL to transcribe (remove `/transcribe-link` prefix if present).

Return the JSON response verbatim.

**Usage:**
```
/transcribe-link https://youtube.com/watch?v=abc123
/transcribe-link https://tiktok.com/@user/video/123
/transcribe-link https://instagram.com/p/abc123
```

**Response Format:**
- `status`: "ok" on success
- `transcript`: Transcribed content from the link
- `title`: Video/article title (if available)
- `description`: Content description (if available)
- `duration`: Duration of the content (if available)

### 6. Check Link Reliability (`/link-reliability/check`)

When the command starts with `/link-reliability/check` or `/check-link-reliability` or the input is a URL to check for source reliability:

**Endpoint:** `POST {BASE_URL}/link-reliability/check`

**Headers:**
- `X-API-KEY: ${FACTICITY_API_KEY}`
- `Content-Type: application/json`

**Body:**
```json
{
  "url": "<raw command input (remove /link-reliability/check or /check-link-reliability prefix if present)>"
}
```

The raw command input should be the URL to check (remove `/link-reliability/check` or `/check-link-reliability` prefix if present).

Return the JSON response verbatim. The response includes:
- `url`: The processed URL
- `bias`: Bias score (-42 to +42)
- `quality`: Quality score (0 to 64)
- `bias_label`: Human-readable bias category
- `quality_label`: Human-readable quality category
- `found`: Whether the URL was found in MediaBias database

**Usage:**
```
/link-reliability/check https://www.example.com/article
/check-link-reliability https://www.bbc.com/news
/link-reliability/check https://www.politico.com/story
```

**Response Format:**
```json
{
  "url": "https://www.example.com/article",
  "bias": -5.24,
  "quality": 46.45,
  "bias_label": "Left-Center Bias",
  "quality_label": "High Quality",
  "found": true
}
```

**Note:** If the URL is not found in the MediaBias database, `found` will be `false` and bias/quality scores may be null or default values.

## Command Routing

Determine which operation to perform based on the command prefix:
- `/fact-check` or input looks like a claim → Fact-Check endpoint
- `/extract-claim` or input is a URL → Extract Claims endpoint
- `/get-credits` → Get Credits endpoint
- `/check-task-status` or input is a task ID → Check Task Status endpoint
- `/transcribe-link` or input is a URL → Transcribe Link endpoint
- `/link-reliability/check` or `/check-link-reliability` or input is a URL → Check Link Reliability endpoint

## API Token Usage

- **Fact-Check**: Each request consumes 1 API token
- **Extract Claims**: Consumes 1 API token per 1 million characters processed
- **Get Credits**: Free, does not consume tokens
- **Check Task Status**: Free, does not consume tokens
- **Transcribe Link**: Consumes 1 API token per transcription request
- **Check Link Reliability**: Consumes 1 API token per request

Monitor usage with `/get-credits`.

## Configuration

Set `FACTICITY_API_KEY` in your OpenClaw config under `skills.entries.facticity-ai.apiKey` or as an environment variable.

**Example config:**
```json
{
  "skills": {
    "entries": {
      "facticity-ai": {
        "enabled": true,
        "apiKey": "YOUR_API_KEY_HERE"
      }
    }
  }
}
```

Or set as environment variable:
```bash
export FACTICITY_API_KEY=your_api_key_here
```
