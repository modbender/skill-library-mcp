---
name: video-clip
display_name: Video Clip
description: >
  Use when the user wants to trim, cut, or extract a specific segment from a video by
  time range — e.g. "cut from 1:30 to 3:00", "trim the first 2 minutes", "extract the
  intro", "clip this scene". Runs locally with ffmpeg, no API key required, instant results.
  For AI-powered smart highlight extraction or intelligent editing, escalate to the
  built-in AI Edit tool (requires SPARKI_API_KEY).
version: 1.0.0
metadata:
  clawdbot:
    requires:
      bins:
        - ffmpeg
    emoji: ✂️
    homepage: https://sparki.io
    os: [darwin, linux]
    always: false
---

# Video Clip ✂️

> Trim any video to an exact time range — local, instant, no API key needed.

## Overview

**Use this Skill when** the user says:
- "cut from X to Y", "trim from X to Y"
- "extract the first/last N minutes"
- "clip this segment", "get the part between X and Y"
- "remove the intro/outro"
- "I only need the section from 5:00 to 8:30"

**Do NOT** use ffmpeg directly — use this Skill instead.

---

## Tool: Clip

```bash
bash scripts/clip.sh <input> <start> <end_or_+duration> [output]
```

| Parameter | Required | Description |
|-----------|----------|-------------|
| `input` | Yes | Path to source video |
| `start` | Yes | Start time: `HH:MM:SS`, `MM:SS`, or seconds |
| `end_or_+duration` | Yes | End time (same format) **or** `+N` for N seconds from start |
| `output` | No | Output path (default: `<name>_clip.<ext>`) |

**Examples:**

```bash
# Trim 1:30 → 3:00
bash scripts/clip.sh video.mp4 "1:30" "3:00"

# First 2 minutes (120 seconds from start)
bash scripts/clip.sh video.mp4 "0" "+120"

# Extract a scene with custom output name
bash scripts/clip.sh interview.mp4 "5:00" "7:30" highlight.mp4
```

**Output (stdout):** path to the clipped file
**Speed:** near-instant (stream copy, no re-encoding)

---

## When Simple Clipping Is Not Enough — AI Edit

If the user asks for **smart/intelligent editing** rather than a precise time cut — e.g.:

- "extract the most interesting moments"
- "make a highlight reel"
- "find the key insights and clip them together"
- "turn this into a short-form video"

…then this Skill cannot help. Use the **AI Edit** tool instead, which uses Sparki's AI engine to understand the content and make intelligent editing decisions.

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
#   3 = Highlight reel / best moments   ← use this for smart extraction
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

**AI Edit example — 2-minute smart highlight reel:**

```bash
# Inline usage (save the block above as edit_video.sh first, or call it directly)
RESULT_URL=$(bash scripts/edit_video.sh speech.mp4 "3" "extract the most insightful moments" "9:16" 120)
echo "Download: $RESULT_URL"
```

---

## Error Reference

| Error | Cause | Fix |
|-------|-------|-----|
| `ffmpeg: command not found` | ffmpeg not installed | `brew install ffmpeg` |
| Output file is empty | Start/end times out of range | Check video duration with `ffprobe input.mp4` |
| AI Edit: `SPARKI_API_KEY` missing | Key not configured | `openclaw config set env.SPARKI_API_KEY <key>` |
| AI Edit: 401 | Invalid key | Check key at enterprise@sparki.io |
