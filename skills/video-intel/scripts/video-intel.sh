#!/usr/bin/env bash
# video-intel.sh — Download, transcribe, and summarize videos from YouTube/TikTok/Instagram/X
# Usage: video-intel.sh <command> <url> [options]
#
# Commands:
#   transcript <url>          — Get transcript (YouTube captions or audio transcription)
#   summary <url>             — Download transcript and print it (agent summarizes)
#   download <url> [format]   — Download video (format: best/audio/720p, default: best)
#   info <url>                — Show video metadata (title, duration, description)
#   captions <url>            — List available caption tracks
#
# Options:
#   --lang <lang>   Caption language (default: en, pt)
#   --out <dir>     Output directory (default: /tmp/video-intel)

set -e

YT_DLP="${HOME}/bin/yt-dlp"
command -v yt-dlp &>/dev/null && YT_DLP="yt-dlp"
OUTDIR="${OUTDIR:-/tmp/video-intel}"
mkdir -p "$OUTDIR"

CMD="${1:-help}"
URL="${2:-}"
shift 2 2>/dev/null || true

LANG="en"
FORMAT="best"
while [[ $# -gt 0 ]]; do
  case "$1" in
    --lang) LANG="$2"; shift 2 ;;
    --out)  OUTDIR="$2"; shift 2 ;;
    --format) FORMAT="$2"; shift 2 ;;
    *) shift ;;
  esac
done

if [[ -z "$URL" && "$CMD" != "help" ]]; then
  echo "ERROR: URL required" >&2
  exit 1
fi

case "$CMD" in

  info)
    "$YT_DLP" --no-download --print "%(title)s\nDuration: %(duration_string)s\nUploader: %(uploader)s\nURL: %(webpage_url)s\n\n%(description)s" "$URL"
    ;;

  captions)
    "$YT_DLP" --list-subs "$URL" 2>&1 | grep -v "^\[" || true
    ;;

  transcript)
    SLUG=$(echo "$URL" | md5sum | cut -c1-8)
    CAPDIR="$OUTDIR/caps_${SLUG}"
    mkdir -p "$CAPDIR"

    # Try YouTube auto/manual captions first (fast, no audio download needed)
    # Run yt-dlp and ignore exit code — it may fail for one language but succeed for another
    "$YT_DLP" \
      --skip-download \
      --write-auto-subs \
      --write-subs \
      --sub-langs "${LANG},${LANG}-*,en,en-*,pt,pt-*" \
      --sub-format "vtt/srt/best" \
      --convert-subs srt \
      --output "$CAPDIR/%(title)s.%(ext)s" \
      "$URL" 2>/dev/null || true

    # Find first non-empty caption file (prefer explicit lang, then any)
    SRT=$(find "$CAPDIR" \( -name "*.${LANG}.vtt" -o -name "*.${LANG}.srt" \) -size +0c | head -1)
    [[ -s "$SRT" ]] || SRT=$(find "$CAPDIR" -name "*.en.vtt" -o -name "*.en.srt" | xargs -I{} sh -c '[ -s "{}" ] && echo "{}"' | head -1)
    [[ -s "$SRT" ]] || SRT=$(find "$CAPDIR" \( -name "*.vtt" -o -name "*.srt" \) -size +0c | head -1)
    if [[ -n "$SRT" && -s "$SRT" ]]; then
        echo "=== TRANSCRIPT (captions) ==="
        python3 "$(dirname "$0")/parse-vtt.py" "$SRT"
        echo ""
        exit 0
    fi

    # Fallback: download audio and transcribe with OpenAI Whisper API
    if [[ -z "$OPENAI_API_KEY" ]]; then
      echo "ERROR: No captions found and OPENAI_API_KEY not set for audio transcription." >&2
      exit 1
    fi

    echo "No captions found, downloading audio for transcription..." >&2
    AUDIO="$OUTDIR/audio_${SLUG}.mp3"
    "$YT_DLP" \
      --extract-audio \
      --audio-format mp3 \
      --audio-quality 3 \
      --output "$AUDIO" \
      "$URL" >&2

    echo "Transcribing via OpenAI Whisper..." >&2
    RESULT=$(curl -s https://api.openai.com/v1/audio/transcriptions \
      -H "Authorization: Bearer $OPENAI_API_KEY" \
      -F model="gpt-4o-mini-transcribe" \
      -F file="@${AUDIO}")

    echo "=== TRANSCRIPT (whisper) ==="
    echo "$RESULT" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('text','ERROR: '+str(d)))"
    ;;

  download)
    "$YT_DLP" \
      --format "${FORMAT}" \
      --output "$OUTDIR/%(title)s.%(ext)s" \
      "$URL"
    echo "Saved to: $OUTDIR"
    ;;

  help|*)
    cat << 'HELP'
video-intel.sh — Video transcript & download tool

Commands:
  transcript <url>        Get transcript (captions or Whisper fallback)
  info <url>              Show video title, duration, description
  captions <url>          List available caption tracks
  download <url>          Download video

Options:
  --lang <lang>           Preferred caption language (default: en)
  --out <dir>             Output directory (default: /tmp/video-intel)
  --format <fmt>          Download format: best/audio/720p

Examples:
  video-intel.sh transcript https://youtu.be/dQw4w9WgXcQ
  video-intel.sh info https://www.tiktok.com/@user/video/123
  video-intel.sh download https://youtu.be/abc --format audio
HELP
    ;;
esac
