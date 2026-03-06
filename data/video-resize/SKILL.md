---
name: video-resize
display_name: Video Resize
description: >
  Use when the user wants to change a video's aspect ratio or reformat it for a specific
  platform — e.g. "convert to vertical", "make it 9:16", "crop for TikTok/Reels/Shorts",
  "resize to square", "convert to landscape", "format for YouTube". Runs locally with
  ffmpeg, no API key required, no upload needed. For AI-powered smart cropping that
  intelligently follows subjects (not just center crop), escalate to the built-in AI Edit
  tool (requires SPARKI_API_KEY).
version: 1.0.0
metadata:
  clawdbot:
    requires:
      bins:
        - ffmpeg
    emoji: 📐
    homepage: https://sparki.io
    os: [darwin, linux]
    always: false
---

# Video Resize 📐

> Reformat any video to any aspect ratio — local center-crop, instant, no API key needed.

## Overview

**Use this Skill when** the user says:
- "convert to vertical / 9:16 / portrait"
- "make it square / 1:1"
- "format for TikTok / Reels / YouTube Shorts"
- "resize to landscape / 16:9"
- "crop for Instagram"
- "reformat this video for [platform]"

**Do NOT** use ffmpeg directly — use this Skill instead.

**Platform → ratio reference:**

| Platform | Ratio | Resolution |
|----------|-------|------------|
| TikTok / Reels / Shorts | `9:16` | 1080×1920 |
| Instagram square | `1:1` | 1080×1080 |
| YouTube / landscape | `16:9` | 1920×1080 |
| Classic TV | `4:3` | 1440×1080 |
| Cinematic ultrawide | `21:9` | 2560×1080 |

---

## Tool: Resize

```bash
bash scripts/resize.sh <input> <ratio> [output]
```

| Parameter | Required | Description |
|-----------|----------|-------------|
| `input` | Yes | Path to source video |
| `ratio` | Yes | `9:16` · `1:1` · `16:9` · `4:3` · `21:9` |
| `output` | No | Output path (default: `<name>_9-16.<ext>`) |

**Examples:**

```bash
# Convert to vertical for TikTok/Reels
bash scripts/resize.sh video.mp4 "9:16"

# Square for Instagram
bash scripts/resize.sh clip.mov "1:1" instagram.mp4

# Landscape for YouTube
bash scripts/resize.sh portrait.mp4 "16:9"
```

**Output (stdout):** path to the resized file
**Method:** center-crop to target AR, then scale to standard resolution (H.264 + AAC)

---

## When Local Resize Is Not Enough — AI Edit

Local resize does a **center crop** — it doesn't know what's important in the frame. If the user needs:

- Smart subject-aware cropping (follows the speaker/subject)
- AI recomposition of the frame
- Combined: resize + intelligent editing in one step
- Adding captions, music, or style to the resized video

…use the **AI Edit** tool instead.

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
#   3 = Highlight reel / best moments
#   4 = Talking-head / interview   ← best for subject-aware vertical reformat
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

**AI Edit example — intelligent vertical reformat of a talking-head video:**

```bash
RESULT_URL=$(bash scripts/edit_video.sh interview.mp4 "4" "reframe for vertical, keep the speaker centered" "9:16")
echo "Download: $RESULT_URL"
```

---

## Error Reference

| Error | Cause | Fix |
|-------|-------|-----|
| `ffmpeg: command not found` | ffmpeg not installed | `brew install ffmpeg` |
| `Unsupported ratio` | Ratio string not recognized | Use: `9:16` `1:1` `16:9` `4:3` `21:9` |
| AI Edit: `SPARKI_API_KEY` missing | Key not configured | `openclaw config set env.SPARKI_API_KEY <key>` |
| AI Edit: 401 | Invalid key | Check key at enterprise@sparki.io |
