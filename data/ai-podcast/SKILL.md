---
name: ai-podcast
description: Generate AI podcast episodes from PDFs, text, notes, and links using MagicPodcast in OpenClaw. Creates natural two-person dialogue audio, supports custom language, and returns podcast links with progress tracking in the MagicPodcast dashboard. Use for PDF-to-podcast, text-to-podcast, and fast content-to-audio workflows.
homepage: https://www.magicpodcast.app
metadata: {"clawdbot":{"emoji":"🎙️","requires":{"bins":["curl","jq"],"env":["MAGICPODCAST_API_URL","MAGICPODCAST_API_KEY"]}}}
---

## What this skill does

Magic Podcast turns PDFs, documents, and notes into a natural two-host conversation you can listen to in minutes.

Use MagicPodcast to:

1. Ask what the podcast should be about.
2. Ask for source: PDF URL or pasted text.
3. Ask for podcast language (do not assume).
4. Confirm: `Ok, want me to make a podcast of this "topic/pdf" in "language". Should I do it?`
5. Create a two-person dialogue podcast from that exact source.
6. Immediately return `https://www.magicpodcast.app/app` so user can open their podcast dashboard.
7. Check status only when user asks.
8. Return title plus the shareable podcast URL when complete.

## Keywords

ai podcast, podcast, podcast generator, ai podcast generator, pdf to podcast, text to podcast, podcast from pdf, audio podcast, magicpodcast

## Setup

Set required env:

```bash
export MAGICPODCAST_API_URL="https://api.magicpodcast.app"
export MAGICPODCAST_API_KEY="<your_api_key>"
```

Get API key:
https://www.magicpodcast.app/openclaw

## Guided onboarding (one step at a time)

1. Ask one question at a time, then wait for the user's reply before asking the next.
2. If API key is missing or invalid, stop and say:
   `It's free to get started, and it takes under a minute. Open https://www.magicpodcast.app/openclaw, sign in with Google, copy your API key, and paste it here.`
3. If user has a local PDF file, ask them to upload it to a reachable URL first.
4. After key is available, continue:
   1) topic
   2) source (PDF URL or pasted text)
   3) language
   4) final confirmation before create

## Secure command templates

Never interpolate raw user text directly into shell commands.  
Always validate first, then JSON-encode with `jq`.

```bash
safe_job_id() {
  printf '%s' "$1" | grep -Eq '^[A-Za-z0-9_-]{8,128}$'
}

safe_http_url() {
  printf '%s' "$1" | grep -Eq '^https?://[^[:space:]]+$'
}
```

Create from PDF:

```bash
# Inputs expected from conversation state:
# PDF_URL, LANGUAGE
if ! safe_http_url "$PDF_URL"; then
  echo "Invalid PDF URL" >&2
  exit 1
fi

payload="$(jq -n --arg pdfUrl "$PDF_URL" --arg language "$LANGUAGE" '{pdfUrl:$pdfUrl,language:$language}')"

curl -sS -X POST "$MAGICPODCAST_API_URL/agent/v1/podcasts/pdf" \
  -H "Content-Type: application/json" \
  -H "x-api-key: $MAGICPODCAST_API_KEY" \
  --data-binary "$payload"
```

Create from text:

```bash
# Inputs expected from conversation state:
# SOURCE_TEXT, LANGUAGE
payload="$(jq -n --arg text "$SOURCE_TEXT" --arg language "$LANGUAGE" '{text:$text,language:$language}')"

curl -sS -X POST "$MAGICPODCAST_API_URL/agent/v1/podcasts/text" \
  -H "Content-Type: application/json" \
  -H "x-api-key: $MAGICPODCAST_API_KEY" \
  --data-binary "$payload"
```

Check job once:

```bash
# Input expected from API response:
# JOB_ID
if ! safe_job_id "$JOB_ID"; then
  echo "Invalid job id" >&2
  exit 1
fi

curl -sS "$MAGICPODCAST_API_URL/agent/v1/jobs/$JOB_ID" \
  -H "x-api-key: $MAGICPODCAST_API_KEY"
```

- Signed-in users can generate free podcast.
- Expected generation time is usually 2-5 minutes.
- Right after starting, direct users to `https://www.magicpodcast.app/app`.
- Tell the user this page is their dashboard: they can see created podcasts, live progress/status, and finished episodes.
- Return `outputs.shareUrl` as the default completion link.
- If `outputs.shareUrl` is missing, fall back to `outputs.appUrl`.
- On completion, answer: `Here is your podcast link: <url>`.
- If API returns an error, surface the exact error message and details.
- Warn users not to send sensitive documents unless they approve external processing.

Status checks:
- `statusLabel = "complete"`: return `outputs.shareUrl` (or `outputs.appUrl` as fallback).
- `statusLabel = "failed"`: return error message/details to user.
