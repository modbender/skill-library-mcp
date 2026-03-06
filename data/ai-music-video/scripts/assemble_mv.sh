#!/usr/bin/env bash
# assemble_mv.sh — Combine audio + visuals into final music video with ffmpeg
# Usage: assemble_mv.sh [options]
#   --audio /path/to/audio.mp3
#   --outdir /path  (where images/videos + meta live)
#   --output /path/to/final.mp4
#   --mode slideshow|video|hybrid  (auto-detect from visuals_meta.json)
#   --slide-duration 8   (seconds per image, default: auto from audio/count)
#   --transition fade|none  (default: fade)
#   --subtitle /path/to/lyrics.srt  (optional SRT subtitles)
#   --no-subtitle    (disable auto-detected lyrics.srt overlay)
#   --resolution 1920x1080  (default: 1920x1080)
#   --dry-run

set -euo pipefail

# Helper: safely write ffmpeg concat list entry (escapes single quotes in filenames)
safe_concat_entry() {
  local filepath="$1"
  # ffmpeg concat format escapes ' as '\'' inside single-quoted strings
  local escaped="${filepath//\'/\'\\\'\'}"
  echo "file '${escaped}'"
}

# Helper: escape path for ffmpeg subtitle filter (escapes : ' \)
escape_subtitle_path() {
  local p="$1"
  p="${p//\\/\\\\}"
  p="${p//:/\\:}"
  p="${p//\'/\\'}"
  echo "$p"
}

AUDIO=""
OUTDIR="./output"
OUTPUT=""
MODE=""
SLIDE_DUR=0
TRANSITION="fade"
SUBTITLE=""
RESOLUTION="1920x1080"
DRY_RUN=false
NO_SUBTITLE=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --audio) AUDIO="$2"; shift 2 ;;
    --outdir) OUTDIR="$2"; shift 2 ;;
    --output) OUTPUT="$2"; shift 2 ;;
    --mode) MODE="$2"; shift 2 ;;
    --slide-duration) SLIDE_DUR="$2"; shift 2 ;;
    --transition) TRANSITION="$2"; shift 2 ;;
    --subtitle) SUBTITLE="$2"; shift 2 ;;
    --no-subtitle) NO_SUBTITLE=true; shift ;;
    --resolution) RESOLUTION="$2"; shift 2 ;;
    --dry-run) DRY_RUN=true; shift ;;
    *) echo "Unknown: $1" >&2; exit 1 ;;
  esac
done

# Auto-detect lyrics.srt if no subtitle specified and not disabled
if [[ -z "$SUBTITLE" && "$NO_SUBTITLE" != true ]]; then
  AUTO_SRT="$OUTDIR/lyrics.srt"
  if [[ -f "$AUTO_SRT" ]]; then
    SUBTITLE="$AUTO_SRT"
    echo "📝 Auto-detected lyrics: $AUTO_SRT"
  fi
fi

# Validate
if [[ -z "$AUDIO" || ! -f "$AUDIO" ]]; then
  echo "ERROR: --audio required (path to audio file)" >&2; exit 1
fi

if [[ -z "$OUTPUT" ]]; then
  OUTPUT="$OUTDIR/music_video.mp4"
fi

# Check ffmpeg
if ! command -v ffmpeg &>/dev/null; then
  echo "ERROR: ffmpeg not found. Install with: apt install ffmpeg" >&2; exit 1
fi

# Get audio duration
AUDIO_DUR=$(ffprobe -v quiet -show_entries format=duration -of csv=p=0 "$AUDIO" 2>/dev/null | cut -d. -f1)
echo "🎵 Audio: $AUDIO (${AUDIO_DUR}s)"

IFS='x' read -r OUT_W OUT_H <<< "$RESOLUTION"

# Auto-detect mode from visuals_meta.json
if [[ -z "$MODE" && -f "$OUTDIR/visuals_meta.json" ]]; then
  MODE=$(python3 -c "
import json, sys
m = json.load(open(sys.argv[1]))
print(m.get('mode', 'slideshow'))
" "$OUTDIR/visuals_meta.json")
fi
MODE="${MODE:-slideshow}"
echo "📽 Mode: $MODE"

# Collect files (use find to avoid pipefail issues with ls on missing dirs)
mapfile -t IMAGES < <(find "$OUTDIR/images" -name "scene_*.png" 2>/dev/null | sort)
mapfile -t VIDEOS < <(find "$OUTDIR/videos" -name "scene_*.mp4" 2>/dev/null | sort)

echo "  Images: ${#IMAGES[@]}, Videos: ${#VIDEOS[@]}"

if [[ "$DRY_RUN" = true ]]; then
  echo "DRY_RUN: would assemble ${#IMAGES[@]} images + ${#VIDEOS[@]} videos → $OUTPUT"
  exit 0
fi

# ── Slideshow mode ──
assemble_slideshow() {
  local num_imgs=${#IMAGES[@]}
  if [[ $num_imgs -eq 0 ]]; then
    echo "ERROR: No images found" >&2; exit 1
  fi

  # Calculate duration per slide
  local dur=$SLIDE_DUR
  if [[ $dur -eq 0 ]]; then
    dur=$((AUDIO_DUR / num_imgs))
    [[ $dur -lt 3 ]] && dur=3
  fi
  echo "  Slide duration: ${dur}s each"

  local FADE_DUR=1

  if [[ "$TRANSITION" == "fade" && $num_imgs -gt 1 ]]; then
    # Complex filter with crossfades — build args array
    local -a ffargs=( ffmpeg -y )

    for i in "${!IMAGES[@]}"; do
      ffargs+=( -loop 1 -t "$((dur + FADE_DUR))" -i "${IMAGES[$i]}" )
    done
    ffargs+=( -i "$AUDIO" )

    # Build filter chain
    local FILTER=""
    for i in "${!IMAGES[@]}"; do
      FILTER="${FILTER}[$i:v]scale=${OUT_W}:${OUT_H}:force_original_aspect_ratio=decrease,pad=${OUT_W}:${OUT_H}:(ow-iw)/2:(oh-ih)/2:black,setsar=1,fps=30[v$i];"
    done

    # Chain crossfades
    if [[ $num_imgs -eq 1 ]]; then
      FILTER="${FILTER}[v0]trim=0:${AUDIO_DUR}[outv]"
    else
      local prev="v0"
      local offset=$((dur))
      for ((i=1; i<num_imgs; i++)); do
        if ((i == num_imgs - 1)); then
          local next="outv"
        else
          local next="cf$i"
        fi
        FILTER="${FILTER}[$prev][v$i]xfade=transition=fade:duration=${FADE_DUR}:offset=${offset}[$next];"
        prev="$next"
        offset=$((offset + dur - FADE_DUR))
      done
      FILTER="${FILTER%;}"
    fi

    if [[ -n "$SUBTITLE" && -f "$SUBTITLE" ]]; then
      local esc_sub
      esc_sub=$(escape_subtitle_path "$SUBTITLE")
      ffargs+=( -filter_complex "${FILTER};[outv]subtitles='${esc_sub}'[finalv]" -map "[finalv]" -map "$((num_imgs)):a" )
    else
      ffargs+=( -filter_complex "${FILTER}" -map "[outv]" -map "$((num_imgs)):a" )
    fi
    ffargs+=( -c:v libx264 -preset medium -crf 20 -c:a aac -b:a 192k -shortest "$OUTPUT" )

    echo "  Running ffmpeg (crossfade slideshow)..."
    "${ffargs[@]}" 2>/dev/null
  else
    # Simple concat (no transitions)
    local LISTFILE="$OUTDIR/images_list.txt"
    > "$LISTFILE"
    for img in "${IMAGES[@]}"; do
      safe_concat_entry "$img" >> "$LISTFILE"
      echo "duration $dur" >> "$LISTFILE"
    done

    local -a ffargs=( ffmpeg -y -f concat -safe 0 -i "$LISTFILE" -i "$AUDIO" )
    if [[ -n "$SUBTITLE" && -f "$SUBTITLE" ]]; then
      local esc_sub2
      esc_sub2=$(escape_subtitle_path "$SUBTITLE")
      ffargs+=( -vf "scale=${OUT_W}:${OUT_H}:force_original_aspect_ratio=decrease,pad=${OUT_W}:${OUT_H}:(ow-iw)/2:(oh-ih)/2:black,fps=30,subtitles='${esc_sub2}'" )
    else
      ffargs+=( -vf "scale=${OUT_W}:${OUT_H}:force_original_aspect_ratio=decrease,pad=${OUT_W}:${OUT_H}:(ow-iw)/2:(oh-ih)/2:black,fps=30" )
    fi
    ffargs+=( -c:v libx264 -preset medium -crf 20 -c:a aac -b:a 192k -shortest "$OUTPUT" )

    echo "  Running ffmpeg (simple slideshow)..."
    "${ffargs[@]}" 2>/dev/null
  fi
}

# ── Video mode ──
assemble_video() {
  local num_vids=${#VIDEOS[@]}
  if [[ $num_vids -eq 0 ]]; then
    echo "ERROR: No video clips found" >&2; exit 1
  fi

  # Create concat list
  local LISTFILE="$OUTDIR/videos_list.txt"
  > "$LISTFILE"
  for vid in "${VIDEOS[@]}"; do
    safe_concat_entry "$vid" >> "$LISTFILE"
  done

  # Concat videos, replace audio
  local -a ffargs=( ffmpeg -y -f concat -safe 0 -i "$LISTFILE" -i "$AUDIO" )
  if [[ -n "$SUBTITLE" && -f "$SUBTITLE" ]]; then
    local esc_sub
    esc_sub=$(escape_subtitle_path "$SUBTITLE")
    ffargs+=( -filter_complex "[0:v]scale=${OUT_W}:${OUT_H}:force_original_aspect_ratio=decrease,pad=${OUT_W}:${OUT_H}:(ow-iw)/2:(oh-ih)/2:black,subtitles='${esc_sub}'[v]" -map "[v]" -map "1:a" )
  else
    ffargs+=( -filter_complex "[0:v]scale=${OUT_W}:${OUT_H}:force_original_aspect_ratio=decrease,pad=${OUT_W}:${OUT_H}:(ow-iw)/2:(oh-ih)/2:black[v]" -map "[v]" -map "1:a" )
  fi
  ffargs+=( -c:v libx264 -preset medium -crf 20 -c:a aac -b:a 192k -shortest "$OUTPUT" )

  echo "  Running ffmpeg (video concat)..."
  "${ffargs[@]}" 2>/dev/null
}

# ── Hybrid mode ──
assemble_hybrid() {
  # Normalize all clips to same format, then concat
  local TMPDIR="$OUTDIR/tmp_hybrid"
  mkdir -p "$TMPDIR"
  local LISTFILE="$OUTDIR/hybrid_list.txt"
  > "$LISTFILE"

  # Calculate image duration
  local img_dur=$SLIDE_DUR
  if [[ $img_dur -eq 0 ]]; then
    img_dur=$((AUDIO_DUR / (${#IMAGES[@]} + ${#VIDEOS[@]})))
    [[ $img_dur -lt 3 ]] && img_dur=3
  fi

  # Convert images to video segments
  local idx=0
  for img in "${IMAGES[@]}"; do
    local tmpvid="$TMPDIR/img_$(printf '%03d' $idx).mp4"
    ffmpeg -y -loop 1 -i "$img" -t "$img_dur" \
      -vf "scale=${OUT_W}:${OUT_H}:force_original_aspect_ratio=decrease,pad=${OUT_W}:${OUT_H}:(ow-iw)/2:(oh-ih)/2:black,fps=30" \
      -c:v libx264 -preset fast -crf 20 -pix_fmt yuv420p "$tmpvid" 2>/dev/null
    safe_concat_entry "$tmpvid" >> "$LISTFILE"
    idx=$((idx + 1))
  done

  # Add video segments (re-encode to same format)
  for vid in "${VIDEOS[@]}"; do
    local tmpvid="$TMPDIR/vid_$(printf '%03d' $idx).mp4"
    ffmpeg -y -i "$vid" \
      -vf "scale=${OUT_W}:${OUT_H}:force_original_aspect_ratio=decrease,pad=${OUT_W}:${OUT_H}:(ow-iw)/2:(oh-ih)/2:black,fps=30" \
      -c:v libx264 -preset fast -crf 20 -pix_fmt yuv420p -an "$tmpvid" 2>/dev/null
    safe_concat_entry "$tmpvid" >> "$LISTFILE"
    idx=$((idx + 1))
  done

  # Final assembly
  local -a ffargs=( ffmpeg -y -f concat -safe 0 -i "$LISTFILE" -i "$AUDIO" )
  if [[ -n "$SUBTITLE" && -f "$SUBTITLE" ]]; then
    local esc_sub
    esc_sub=$(escape_subtitle_path "$SUBTITLE")
    ffargs+=( -vf "subtitles='${esc_sub}'" )
  fi
  ffargs+=( -c:v libx264 -preset medium -crf 20 -c:a aac -b:a 192k -shortest "$OUTPUT" )

  echo "  Running ffmpeg (hybrid assembly)..."
  "${ffargs[@]}" 2>/dev/null

  rm -rf "$TMPDIR"
}

# ── Execute ──
echo ""
case "$MODE" in
  slideshow) assemble_slideshow ;;
  video) assemble_video ;;
  hybrid) assemble_hybrid ;;
  *) echo "ERROR: Unknown mode: $MODE" >&2; exit 1 ;;
esac

if [[ -f "$OUTPUT" ]]; then
  FSIZE=$(du -h "$OUTPUT" | cut -f1)
  echo ""
  echo "🎬 Music Video Complete!"
  echo "━━━━━━━━━━━━━━━━━━━━━━"
  echo "  📁 File: $OUTPUT"
  echo "  📏 Size: $FSIZE"
  echo "  ⏱ Duration: ~${AUDIO_DUR}s"
  echo "━━━━━━━━━━━━━━━━━━━━━━"
else
  echo "❌ Assembly failed — check ffmpeg output" >&2
  exit 1
fi
