#!/usr/bin/env bash
# suno_music.sh — Generate music via sunoapi.org, poll until done, download audio
# Usage: suno_music.sh [options]
#   --prompt "lyrics or description"
#   --style "genre/style tags"
#   --title "song title"
#   --model V4_5ALL|V5|V4_5PLUS|V4_5|V4  (default: V4_5ALL)
#   --instrumental   (flag, no vocals)
#   --custom         (flag, enable custom mode — requires style+title)
#   --vocal-gender m|f  (optional, vocal gender hint)
#   --negative-tags "tags to avoid"  (optional)
#   --outdir /path   (output directory, default: ./output)
#   --timeout 600    (max wait seconds, default: 600)
#   --music-video    (flag, generate Suno native music video after music)
#   --persona-id ID  (use existing persona for consistent style)
#   --create-persona (create persona from generated track)
#   --persona-name "name"  (name for new persona)
#   --persona-desc "desc"  (description for new persona)
#   --persona-style "style" (style label for persona)
#   --dry-run        (show cost estimate only, don't generate)
#
# Env: SUNO_API_KEY (required)
# Output: Downloads .mp3 + writes metadata to outdir/music_meta.json
#         + lyrics.srt (if non-instrumental)
#         + music_video.mp4 (if --music-video)
#         + persona.json (if --create-persona)

set -euo pipefail

API_BASE="https://api.sunoapi.org/api/v1"
MODEL="V4_5ALL"
INSTRUMENTAL=false
CUSTOM_MODE=false
OUTDIR="./output"
TIMEOUT=600
DRY_RUN=false
PROMPT=""
STYLE=""
TITLE=""
VOCAL_GENDER=""
NEGATIVE_TAGS=""
MUSIC_VIDEO=false
PERSONA_ID=""
CREATE_PERSONA=false
PERSONA_NAME=""
PERSONA_DESC=""
PERSONA_STYLE=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --prompt) PROMPT="$2"; shift 2 ;;
    --style) STYLE="$2"; shift 2 ;;
    --title) TITLE="$2"; shift 2 ;;
    --model) MODEL="$2"; shift 2 ;;
    --instrumental) INSTRUMENTAL=true; shift ;;
    --custom) CUSTOM_MODE=true; shift ;;
    --vocal-gender) VOCAL_GENDER="$2"; shift 2 ;;
    --negative-tags) NEGATIVE_TAGS="$2"; shift 2 ;;
    --outdir) OUTDIR="$2"; shift 2 ;;
    --timeout) TIMEOUT="$2"; shift 2 ;;
    --music-video) MUSIC_VIDEO=true; shift ;;
    --persona-id) PERSONA_ID="$2"; shift 2 ;;
    --create-persona) CREATE_PERSONA=true; shift ;;
    --persona-name) PERSONA_NAME="$2"; shift 2 ;;
    --persona-desc) PERSONA_DESC="$2"; shift 2 ;;
    --persona-style) PERSONA_STYLE="$2"; shift 2 ;;
    --dry-run) DRY_RUN=true; shift ;;
    *) echo "Unknown option: $1" >&2; exit 1 ;;
  esac
done

if [[ -z "${SUNO_API_KEY:-}" ]]; then
  echo "ERROR: SUNO_API_KEY not set" >&2; exit 1
fi
if [[ -z "$PROMPT" ]]; then
  echo "ERROR: --prompt required" >&2; exit 1
fi

AUTH="Authorization: Bearer $SUNO_API_KEY"
CT="Content-Type: application/json"

# Check credits (may not be supported by all sunoapi instances)
echo "🔍 Checking Suno credits..."
CREDITS_RESP=$(curl -s -H "$AUTH" "${API_BASE}/get-credits" 2>/dev/null)
CREDITS=$(echo "$CREDITS_RESP" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('data',0))" 2>/dev/null || echo "unknown")
if [[ "$CREDITS" == "unknown" || "$CREDITS" == "0" ]]; then
  CREDITS="N/A (credit API not available)"
fi
echo "💰 Credits: $CREDITS"

# Cost estimate
echo ""
echo "📊 Cost Estimate"
echo "━━━━━━━━━━━━━━━━━━━"
echo "  Model: $MODEL"
echo "  Mode: $([ "$CUSTOM_MODE" = true ] && echo 'Custom' || echo 'Simple')"
echo "  Instrumental: $INSTRUMENTAL"
echo "  Music Video: $MUSIC_VIDEO"
if [[ -n "$PERSONA_ID" ]]; then
  echo "  Persona: $PERSONA_ID"
fi
echo "  Create Persona: $CREATE_PERSONA"
echo "  Est. credits: ~10 per generation (2 tracks)"
echo "  Credits: $CREDITS"
echo "━━━━━━━━━━━━━━━━━━━"

if [[ "$DRY_RUN" = true ]]; then
  echo "DRY_RUN: exiting without generation"
  exit 0
fi

mkdir -p "$OUTDIR"

# Build request body using temp files for safe prompt handling
PROMPT_FILE=$(mktemp)
echo -n "$PROMPT" > "$PROMPT_FILE"
STYLE_FILE=$(mktemp)
echo -n "$STYLE" > "$STYLE_FILE"
TITLE_FILE=$(mktemp)
echo -n "$TITLE" > "$TITLE_FILE"
NEGTAGS_FILE=$(mktemp)
echo -n "$NEGATIVE_TAGS" > "$NEGTAGS_FILE"

BODY=$(python3 -c "
import json, os

with open('$PROMPT_FILE') as f: prompt = f.read()
with open('$STYLE_FILE') as f: style = f.read()
with open('$TITLE_FILE') as f: title = f.read()
with open('$NEGTAGS_FILE') as f: neg_tags = f.read()

body = {
    'prompt': prompt,
    'model': '$MODEL',
    'instrumental': $( [ "$INSTRUMENTAL" = true ] && echo 'True' || echo 'False'),
    'customMode': $( [ "$CUSTOM_MODE" = true ] && echo 'True' || echo 'False'),
}
if $( [ "$CUSTOM_MODE" = true ] && echo 'True' || echo 'False'):
    if style: body['style'] = style
    if title: body['title'] = title
vocal = '$VOCAL_GENDER'
if vocal:
    body['vocalGender'] = vocal
if neg_tags:
    body['negativeTags'] = neg_tags
persona_id = '$PERSONA_ID'
if persona_id:
    body['personaId'] = persona_id
    body['personaModel'] = 'style_persona'
cb_url = os.environ.get('SUNO_CALLBACK_URL', 'https://localhost/noop')
# Validate callback URL scheme (only https allowed to prevent exfiltration)
if cb_url and not cb_url.startswith('https://'):
    cb_url = 'https://localhost/noop'
body['callBackUrl'] = cb_url
print(json.dumps(body, ensure_ascii=False))
")
rm -f "$PROMPT_FILE" "$STYLE_FILE" "$TITLE_FILE" "$NEGTAGS_FILE"

echo ""
echo "🎵 Generating music..."
GEN_RESP=$(curl -s -X POST "${API_BASE}/generate" \
  -H "$AUTH" -H "$CT" \
  -d "$BODY")

TASK_ID=$(echo "$GEN_RESP" | python3 -c "
import sys, json
d = json.load(sys.stdin)
if d.get('code') != 200:
    print('ERROR:' + d.get('msg','unknown'), file=sys.stderr)
    sys.exit(1)
print(d['data']['taskId'])
")

if [[ -z "$TASK_ID" || "$TASK_ID" == ERROR* ]]; then
  echo "ERROR: Failed to start generation: $GEN_RESP" >&2
  exit 1
fi

echo "  Task ID: $TASK_ID"
echo "  Polling for completion (timeout: ${TIMEOUT}s)..."

# Poll loop
START=$(date +%s)
STATUS="PENDING"
while [[ "$STATUS" != "SUCCESS" && "$STATUS" != "FAILED" && "$STATUS" != "ERROR" ]]; do
  NOW=$(date +%s)
  ELAPSED=$((NOW - START))
  if [[ $ELAPSED -ge $TIMEOUT ]]; then
    echo "ERROR: Timeout after ${TIMEOUT}s" >&2
    exit 1
  fi

  sleep 15
  POLL_RESP=$(curl -s -H "$AUTH" "${API_BASE}/generate/record-info?taskId=${TASK_ID}")
  STATUS=$(echo "$POLL_RESP" | python3 -c "
import sys, json
d = json.load(sys.stdin)
print(d.get('data',{}).get('status','UNKNOWN'))
" 2>/dev/null || echo "UNKNOWN")
  echo "  [$((ELAPSED))s] Status: $STATUS"
done

if [[ "$STATUS" == "FAILED" ]]; then
  ERR=$(echo "$POLL_RESP" | python3 -c "import sys,json; print(json.load(sys.stdin).get('data',{}).get('errorMessage','unknown'))" 2>/dev/null)
  echo "ERROR: Generation failed: $ERR" >&2
  exit 1
fi

# Extract results and download
echo ""
echo "✅ Generation complete! Downloading..."

# Save poll response to temp file for safe parsing
RESP_FILE=$(mktemp)
echo "$POLL_RESP" > "$RESP_FILE"

python3 -c "
import json, sys, urllib.request, os

with open('$RESP_FILE') as f:
    resp = json.load(f)
outdir = '$OUTDIR'
data = resp.get('data',{})
response = data.get('response',{}) or {}
tracks = response.get('sunoData', [])
if not tracks:
    tracks = response.get('data', [])

meta = {
    'taskId': '$TASK_ID',
    'model': '$MODEL',
    'tracks': []
}

for i, track in enumerate(tracks):
    audio_url = track.get('audioUrl') or track.get('audio_url', '')
    title = track.get('title', f'track_{i}')
    duration = track.get('duration', 0)
    tags = track.get('tags', '')
    image_url = track.get('imageUrl') or track.get('image_url', '')
    track_id = track.get('id', f'track_{i}')

    # Download audio
    if audio_url:
        fname = f'track_{i}_{track_id}.mp3'
        fpath = os.path.join(outdir, fname)
        print(f'  ⬇ Downloading {title} ({duration:.0f}s)...')
        try:
            req = urllib.request.Request(audio_url, headers={
                'User-Agent': 'Mozilla/5.0 (compatible; MusicBot/1.0)',
                'Accept': '*/*',
            })
            with urllib.request.urlopen(req, timeout=120) as resp_dl:
                with open(fpath, 'wb') as out:
                    out.write(resp_dl.read())
            print(f'    Saved: {fpath}')
        except Exception as e:
            print(f'    ❌ Download failed ({e}): {audio_url}', file=sys.stderr)
            fname = ''
            fpath = ''
    else:
        fname = ''
        fpath = ''

    # Download cover image
    img_fname = ''
    if image_url:
        img_fname = f'cover_{i}_{track_id}.jpg'
        img_path = os.path.join(outdir, img_fname)
        try:
            req = urllib.request.Request(image_url, headers={
                'User-Agent': 'Mozilla/5.0 (compatible; MusicBot/1.0)',
            })
            with urllib.request.urlopen(req, timeout=60) as resp_dl:
                with open(img_path, 'wb') as out:
                    out.write(resp_dl.read())
        except Exception:
            img_fname = ''

    meta['tracks'].append({
        'id': track_id,
        'title': title,
        'duration': duration,
        'tags': tags,
        'audio_file': fname,
        'audio_url': audio_url,
        'image_url': image_url,
        'image_file': img_fname,
        'prompt': track.get('prompt', ''),
    })

# Write metadata
meta_path = os.path.join(outdir, 'music_meta.json')
with open(meta_path, 'w') as f:
    json.dump(meta, f, indent=2, ensure_ascii=False)
print(f'\n📄 Metadata: {meta_path}')
print(f'🎵 Tracks: {len(meta[\"tracks\"])}')
for t in meta['tracks']:
    dur = t['duration']
    print(f'   • {t[\"title\"]} ({dur:.0f}s) — {t[\"tags\"]}')
"
rm -f "$RESP_FILE"

# ── Timestamped Lyrics ──
# 비instrumental 트랙인 경우 자동으로 가사 타임스탬프를 가져와 SRT로 저장
if [[ "$INSTRUMENTAL" != true ]]; then
  echo ""
  echo "📝 Fetching timestamped lyrics..."

  # music_meta.json에서 첫 번째 트랙의 audioId 추출
  AUDIO_ID=$(python3 -c "
import json, os
meta = json.load(open(os.path.join('$OUTDIR', 'music_meta.json')))
tracks = meta.get('tracks', [])
if tracks:
    print(tracks[0].get('id', ''))
else:
    print('')
")

  if [[ -n "$AUDIO_ID" ]]; then
    LYRICS_BODY=$(python3 -c "
import json
print(json.dumps({'taskId': '$TASK_ID', 'audioId': '$AUDIO_ID'}))
")
    LYRICS_RESP=$(curl -s -X POST "${API_BASE}/generate/get-timestamped-lyrics" \
      -H "$AUTH" -H "$CT" \
      -d "$LYRICS_BODY")

    # Parse response and convert to SRT format
    python3 -c "
import json, sys, os

resp = json.loads('''$(echo "$LYRICS_RESP" | python3 -c "import sys; print(sys.stdin.read().replace(\"'\",\"\\\\'\"))")''')
outdir = '$OUTDIR'

if resp.get('code') != 200:
    print(f'  ⚠ Lyrics API returned: {resp.get(\"msg\", \"unknown error\")}', file=sys.stderr)
    sys.exit(0)

data = resp.get('data', {})
lyrics_data = data.get('lyrics', [])

if not lyrics_data:
    print('  ⚠ No lyrics data returned (might be instrumental)')
    sys.exit(0)

# Convert to SRT format
srt_lines = []
for i, item in enumerate(lyrics_data, 1):
    start_sec = item.get('startTime', item.get('start', 0))
    end_sec = item.get('endTime', item.get('end', start_sec + 3))
    text = item.get('text', item.get('words', ''))
    if not text or not text.strip():
        continue

    def fmt_time(s):
        h = int(s // 3600)
        m = int((s % 3600) // 60)
        sec = int(s % 60)
        ms = int((s % 1) * 1000)
        return f'{h:02d}:{m:02d}:{sec:02d},{ms:03d}'

    srt_lines.append(str(i))
    srt_lines.append(f'{fmt_time(start_sec)} --> {fmt_time(end_sec)}')
    srt_lines.append(text.strip())
    srt_lines.append('')

if srt_lines:
    srt_path = os.path.join(outdir, 'lyrics.srt')
    with open(srt_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(srt_lines))
    print(f'  ✅ Lyrics saved: {srt_path} ({len([l for l in srt_lines if l.strip() and not l.strip().isdigit() and \"-->\" not in l])} lines)')
else:
    print('  ⚠ No lyric lines to save')
" || echo "  ⚠ Lyrics fetch failed (non-fatal)"
  else
    echo "  ⚠ No audio ID found, skipping lyrics"
  fi
fi

# ── Suno Native Music Video ──
if [[ "$MUSIC_VIDEO" = true ]]; then
  echo ""
  echo "🎬 Requesting Suno native music video..."

  AUDIO_ID=$(python3 -c "
import json, os
meta = json.load(open(os.path.join('$OUTDIR', 'music_meta.json')))
tracks = meta.get('tracks', [])
if tracks:
    print(tracks[0].get('id', ''))
else:
    print('')
")

  if [[ -z "$AUDIO_ID" ]]; then
    echo "  ❌ No audio ID found, cannot create music video" >&2
  else
    MV_BODY=$(python3 -c "
import json
print(json.dumps({
    'taskId': '$TASK_ID',
    'audioId': '$AUDIO_ID',
    'callBackUrl': 'https://localhost/noop',
}))
")
    MV_RESP=$(curl -s -X POST "${API_BASE}/mp4/generate" \
      -H "$AUTH" -H "$CT" \
      -d "$MV_BODY")

    MV_CODE=$(echo "$MV_RESP" | python3 -c "import sys,json; print(json.load(sys.stdin).get('code',0))" 2>/dev/null || echo "0")

    if [[ "$MV_CODE" != "200" ]]; then
      MV_MSG=$(echo "$MV_RESP" | python3 -c "import sys,json; print(json.load(sys.stdin).get('msg','unknown'))" 2>/dev/null || echo "unknown")
      echo "  ❌ Music video request failed: $MV_MSG" >&2
    else
      echo "  ✅ Music video generation started"
      echo "  ⏳ Polling for music video completion..."

      # Poll for music video using /mp4/record-info
      MV_TASK_ID=$(echo "$MV_RESP" | python3 -c "import sys,json; print(json.load(sys.stdin).get('data',{}).get('taskId',''))" 2>/dev/null || echo "")
      if [[ -z "$MV_TASK_ID" ]]; then
        MV_TASK_ID="$TASK_ID"
      fi
      MV_START=$(date +%s)
      MV_STATUS="PENDING"
      while [[ "$MV_STATUS" != "SUCCESS" && "$MV_STATUS" != "COMPLETED" && "$MV_STATUS" != "FAILED" ]]; do
        MV_NOW=$(date +%s)
        MV_ELAPSED=$((MV_NOW - MV_START))
        if [[ $MV_ELAPSED -ge $TIMEOUT ]]; then
          echo "  ❌ Music video timeout after ${TIMEOUT}s" >&2
          break
        fi
        sleep 20

        MV_POLL=$(curl -s -H "$AUTH" "${API_BASE}/mp4/record-info?taskId=${MV_TASK_ID}")
        MV_STATUS=$(echo "$MV_POLL" | python3 -c "import sys,json; print(json.load(sys.stdin).get('data',{}).get('successFlag','PENDING'))" 2>/dev/null || echo "PENDING")
        MV_VIDEO_URL=$(echo "$MV_POLL" | python3 -c "
import sys, json
d = json.load(sys.stdin)
data = d.get('data',{})
resp = data.get('response',{}) or {}
url = resp.get('videoUrl') or resp.get('video_url') or data.get('videoUrl', '')
print(url)
" 2>/dev/null || echo "")

        if [[ "$MV_STATUS" == "SUCCESS" && -n "$MV_VIDEO_URL" ]]; then
          echo "  [$((MV_ELAPSED))s] Music video ready!"
        elif [[ "$MV_STATUS" == "FAILED" ]]; then
          echo "  [$((MV_ELAPSED))s] Music video failed!"
        else
          echo "  [$((MV_ELAPSED))s] Status: $MV_STATUS"
        fi
      done

      # Download the music video
      if [[ -n "${MV_VIDEO_URL:-}" ]]; then
        MV_OUTPUT="$OUTDIR/suno_music_video.mp4"
        echo "  ⬇ Downloading music video..."
        if curl -sL -o "$MV_OUTPUT" "$MV_VIDEO_URL" && [[ -f "$MV_OUTPUT" ]] && [[ $(stat -c%s "$MV_OUTPUT" 2>/dev/null || echo 0) -gt 1000 ]]; then
          echo "  ✅ Suno music video saved: $MV_OUTPUT"
        else
          echo "  ❌ Music video download failed" >&2
        fi
      fi
    fi
  fi
fi

# ── Create Persona ──
if [[ "$CREATE_PERSONA" = true ]]; then
  echo ""
  echo "🎭 Creating Persona from generated track..."

  AUDIO_ID_P=$(python3 -c "
import json, os
meta = json.load(open(os.path.join('$OUTDIR', 'music_meta.json')))
tracks = meta.get('tracks', [])
if tracks:
    print(tracks[0].get('id', ''))
else:
    print('')
")

  if [[ -z "$AUDIO_ID_P" ]]; then
    echo "  ❌ No audio ID found, cannot create persona" >&2
  else
    # 기본값: 이름과 설명이 없으면 프롬프트/스타일에서 유추
    P_NAME="${PERSONA_NAME:-$(echo "$TITLE" | head -c 50)}"
    P_NAME="${P_NAME:-Dev BGM Singer}"
    P_DESC="${PERSONA_DESC:-Generated from: $(echo "$PROMPT" | head -c 100)}"
    P_STYLE_VAL="${PERSONA_STYLE:-$STYLE}"

    PERSONA_BODY_FILE=$(mktemp)
    python3 -c "
import json
body = {
    'taskId': '$TASK_ID',
    'audioId': '$AUDIO_ID_P',
    'name': '''$P_NAME''',
    'description': '''$P_DESC''',
}
style = '''$P_STYLE_VAL'''
if style:
    body['style'] = style
print(json.dumps(body, ensure_ascii=False))
" > "$PERSONA_BODY_FILE"

    PERSONA_RESP=$(curl -s -X POST "${API_BASE}/generate/generate-persona" \
      -H "$AUTH" -H "$CT" \
      -d @"$PERSONA_BODY_FILE")
    rm -f "$PERSONA_BODY_FILE"

    PERSONA_CODE=$(echo "$PERSONA_RESP" | python3 -c "import sys,json; print(json.load(sys.stdin).get('code',0))" 2>/dev/null || echo "0")

    if [[ "$PERSONA_CODE" == "200" ]]; then
      PERSONA_DATA=$(echo "$PERSONA_RESP" | python3 -c "
import sys, json
d = json.load(sys.stdin).get('data', {})
pid = d.get('personaId', d.get('id', 'unknown'))
print(pid)
" 2>/dev/null || echo "unknown")

      echo "  ✅ Persona created! ID: $PERSONA_DATA"
      echo "  💡 다음 생성 시 --persona-id $PERSONA_DATA 로 일관된 스타일 유지 가능"

      # Save persona info
      python3 -c "
import json, os
persona = {
    'personaId': '$PERSONA_DATA',
    'name': '''$P_NAME''',
    'description': '''$P_DESC''',
    'style': '''$P_STYLE_VAL''',
    'sourceTaskId': '$TASK_ID',
    'sourceAudioId': '$AUDIO_ID_P',
}
path = os.path.join('$OUTDIR', 'persona.json')
with open(path, 'w') as f:
    json.dump(persona, f, indent=2, ensure_ascii=False)
print(f'  📄 Persona info: {path}')
"
    else
      PERSONA_MSG=$(echo "$PERSONA_RESP" | python3 -c "import sys,json; print(json.load(sys.stdin).get('msg','unknown'))" 2>/dev/null || echo "unknown")
      echo "  ❌ Persona creation failed: $PERSONA_MSG" >&2
    fi
  fi
fi

# Done
echo ""
echo "🎵 Music generation complete!"
