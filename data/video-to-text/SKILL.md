---
name: video-to-text
display_name: Video to Text
description: >
  Use when the user wants to transcribe, caption, or get the text content of a video or
  audio file — e.g. "transcribe this video", "get the transcript", "what did they say",
  "generate subtitles", "extract captions", "convert speech to text". Runs locally with
  Whisper, no API key required. Supports 50+ languages with auto-detection. Outputs both
  plain text transcript and SRT subtitle file. For AI-powered video editing that uses the
  transcript (highlights, montage, commentary), escalate to the built-in AI Edit tool
  (requires SPARKI_API_KEY).
version: 1.0.0
metadata:
  clawdbot:
    requires:
      bins:
        - ffmpeg
        - whisper
    emoji: 🎙️
    homepage: https://sparki.io
    os: [darwin, linux]
    always: false
---

# Video to Text 🎙️

> Transcribe any video or audio to text + SRT subtitles — local Whisper, no API key, 50+ languages.

## Overview

**Use this Skill when** the user says:
- "transcribe this video / audio"
- "get the transcript", "what did they say"
- "generate subtitles / captions"
- "convert speech to text"
- "extract the text from this video"
- "I need the SRT file"

**Do NOT** call whisper or ffmpeg directly — use this Skill instead.

**Output:** both `.txt` (plain transcript) and `.srt` (timestamped subtitles) saved next to the input file.

---

## Prerequisites

```bash
# Install ffmpeg (if not already installed)
brew install ffmpeg         # macOS
sudo apt install ffmpeg     # Ubuntu/Debian

# Install Whisper
pip install openai-whisper
```

No API key required.

---

## Tool: Transcribe

```bash
bash scripts/transcribe.sh <input> [language] [model]
```

| Parameter | Required | Description |
|-----------|----------|-------------|
| `input` | Yes | Path to video or audio file |
| `language` | No | ISO-639-1 code: `en`, `zh`, `ja`, `ko`, `es`, `fr`, ... (default: auto-detect) |
| `model` | No | `tiny` · `base` · `small` (default) · `medium` · `large` |

**Model tradeoffs:**

| Model | Speed | Accuracy | VRAM |
|-------|-------|----------|------|
| `tiny` | Fastest | Low | ~1 GB |
| `base` | Fast | OK | ~1 GB |
| `small` | Balanced ✓ | Good | ~2 GB |
| `medium` | Slow | Great | ~5 GB |
| `large` | Slowest | Best | ~10 GB |

**Examples:**

```bash
# Auto-detect language, default model (small)
bash scripts/transcribe.sh video.mp4

# Force English
bash scripts/transcribe.sh podcast.mp4 en

# Chinese, higher accuracy
bash scripts/transcribe.sh speech.mp4 zh medium

# Audio file
bash scripts/transcribe.sh recording.m4a en small
```

**Output (stdout):** path to the `.txt` transcript file
**Side effects:** also writes `<name>.srt` in same directory as input

---

## When Transcription Is Not Enough — AI Edit

Once you have a transcript, if the user wants to:

- Create a highlight reel based on the transcript content
- Auto-generate a short-form video from the key moments
- Add captions burned into the video
- Generate AI commentary or narration

…use the **AI Edit** tool. It uses the transcript + your prompt to intelligently edit the video.

### Recommended workflow: transcribe first, then AI edit

```bash
# Step 1 — get the transcript (local, instant)
TRANSCRIPT=$(bash scripts/transcribe.sh speech.mp4 en)
echo "Transcript saved to: $TRANSCRIPT"

# Step 2 — review the transcript, then pass key themes as user_prompt to AI Edit
# (AI Edit uses its own understanding of the video content internally)
```

### Prerequisites for AI Edit

```bash
# Check if key is configured
echo "Key: ${SPARKI_API_KEY:+configured}${SPARKI_API_KEY:-MISSING}"

# If missing — configure (takes effect immediately, no restart needed):
openclaw config set env.SPARKI_API_KEY "sk_live_your_key_here"
# Get a key: email enterprise@sparki.io
```

### AI Edit — End-to-End

```bash
# Usage: edit_video.sh <file> <tips> [prompt] [aspect_ratio] [duration_seconds]
#
# tips: comma-separated style IDs
#   1 = Energetic / fast-paced
#   2 = Cinematic / slow motion
#   3 = Highlight reel / best moments   ← pair with transcript insights
#   4 = Talking-head / interview
#
# Returns: a 24-hour download URL for the AI-processed video (stdout)

SPARKI_API_BASE="https://agent-api-test.aicoding.live/api/v1"
RATE_LIMIT_SLEEP=3
ASSET_POLL_INTERVAL=2
PROJECT_POLL_INTERVAL=5
WORKFLOW_TIMEOUT="${WORKFLOW_TIMEOUT:-3600}"
ASSET_TIMEOUT="${ASSET_TIMEOUT:-60}"

: "${SPARKI_API_KEY:?Error: SPARKI_API_KEY is required. Run: openclaw config set env.SPARKI_API_KEY <key>}"

FILE_PATH="$1"; TIPS="$2"; USER_PROMPT="${3:-}"; ASPECT_RATIO="${4:-9:16}"; DURATION="${5:-}"

# -- Step 1: Upload --
echo "[1/4] Uploading $FILE_PATH..." >&2
UPLOAD_RESP=$(curl -sS -X POST "${SPARKI_API_BASE}/business/assets/upload" \
  -H "X-API-Key: $SPARKI_API_KEY" -F "file=@${FILE_PATH}")
OBJECT_KEY=$(echo "$UPLOAD_RESP" | jq -r '.data.object_key // empty')
[[ -z "$OBJECT_KEY" ]] && { echo "Upload failed: $(echo "$UPLOAD_RESP" | jq -r '.message')" >&2; exit 1; }
echo "[1/4] object_key=$OBJECT_KEY" >&2

# -- Step 2: Wait for asset ready --
echo "[2/4] Waiting for asset processing..." >&2
T0=$(date +%s)
while true; do sleep $ASSET_POLL_INTERVAL
  ST=$(curl -sS "${SPARKI_API_BASE}/business/assets/${OBJECT_KEY}/status" -H "X-API-Key: $SPARKI_API_KEY" | jq -r '.data.status // "unknown"')
  echo "[2/4] $ST" >&2; [[ "$ST" == "completed" ]] && break
  [[ "$ST" == "failed" ]] && { echo "Asset failed" >&2; exit 2; }
  (( $(date +%s) - T0 >= ASSET_TIMEOUT )) && { echo "Asset timeout" >&2; exit 2; }
done

# -- Step 3: Create project --
echo "[3/4] Creating AI project (tips=$TIPS)..." >&2
sleep $RATE_LIMIT_SLEEP
KEYS_JSON=$(echo "$OBJECT_KEY" | jq -Rc '[.]')
TIPS_JSON=$(echo "$TIPS" | jq -Rc 'split(",") | map(tonumber? // .)')
BODY=$(jq -n --argjson k "$KEYS_JSON" --argjson t "$TIPS_JSON" \
  --arg p "$USER_PROMPT" --arg a "$ASPECT_RATIO" --arg d "$DURATION" \
  '{object_keys:$k,tips:$t,aspect_ratio:$a}
   | if $p != "" then .+{user_prompt:$p} else . end
   | if $d != "" then .+{duration:($d|tonumber)} else . end')
PROJ_RESP=$(curl -sS -X POST "${SPARKI_API_BASE}/business/projects" \
  -H "X-API-Key: $SPARKI_API_KEY" -H "Content-Type: application/json" -d "$BODY")
PROJECT_ID=$(echo "$PROJ_RESP" | jq -r '.data.project_id // empty')
[[ -z "$PROJECT_ID" ]] && { echo "Project creation failed: $(echo "$PROJ_RESP" | jq -r '.message')" >&2; exit 1; }
echo "[3/4] project_id=$PROJECT_ID" >&2

# -- Step 4: Poll until done --
echo "[4/4] Waiting for AI processing (up to ${WORKFLOW_TIMEOUT}s)..." >&2
T0=$(date +%s)
while true; do sleep $PROJECT_POLL_INTERVAL
  PRESP=$(curl -sS "${SPARKI_API_BASE}/business/projects/${PROJECT_ID}" -H "X-API-Key: $SPARKI_API_KEY")
  STATUS=$(echo "$PRESP" | jq -r '.data.status // "UNKNOWN"')
  echo "[4/4] $STATUS" >&2
  if [[ "$STATUS" == "COMPLETED" ]]; then
    echo "$PRESP" | jq -r '.data.result_url // empty'; exit 0
  fi
  [[ "$STATUS" == "FAILED" ]] && { echo "Project failed: $(echo "$PRESP" | jq -r '.data.error')" >&2; exit 4; }
  (( $(date +%s) - T0 >= WORKFLOW_TIMEOUT )) && { echo "Timeout. Check manually: project_id=$PROJECT_ID" >&2; exit 3; }
done
```

**AI Edit example — transcript-informed highlight reel:**

```bash
# After reviewing the transcript, pass key themes as the prompt
RESULT_URL=$(bash scripts/edit_video.sh speech.mp4 "3" \
  "focus on the parts about AI and the future of work, energetic pacing" "9:16" 120)
echo "Download: $RESULT_URL"
```

---

## Error Reference

| Error | Cause | Fix |
|-------|-------|-----|
| `whisper: command not found` | Whisper not installed | `pip install openai-whisper` |
| `ffmpeg: command not found` | ffmpeg not installed | `brew install ffmpeg` |
| Transcript is empty | Silent video or wrong language | Try `language=en` explicitly or check audio track |
| AI Edit: `SPARKI_API_KEY` missing | Key not configured | `openclaw config set env.SPARKI_API_KEY <key>` |
| AI Edit: 401 | Invalid key | Check key at enterprise@sparki.io |
