#!/usr/bin/env bash
set -euo pipefail
# /strudel command dispatcher
# Called by the agent to execute slash command subcommands.
#
# Usage:
#   dispatch.sh render <composition.js> [cycles] [bpm]
#   dispatch.sh play <name> [channel-id]
#   dispatch.sh list
#   dispatch.sh samples <subcommand> [args...]
#   dispatch.sh concert <name1> [name2] [name3] ...

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
COMP_DIR="$ROOT_DIR/assets/compositions"
TMP_DIR="${STRUDEL_TMP:-${OPENCLAW_WORKSPACE:-${HOME}/.openclaw/workspace}/strudel-renders}"

mkdir -p "$TMP_DIR"

_render() {
  local INPUT="$1"
  local CYCLES="${2:-16}"
  local BPM="${3:-120}"
  local BASENAME
  BASENAME=$(basename "$INPUT" .js)
  local WAV="$TMP_DIR/${BASENAME}.wav"
  local MP3="$TMP_DIR/${BASENAME}.mp3"

  echo "🎵 Rendering $BASENAME (${CYCLES} cycles, ${BPM} BPM)..."
  node "$ROOT_DIR/src/runtime/offline-render-v2.mjs" "$INPUT" "$WAV" "$CYCLES" "$BPM"

  if command -v ffmpeg &>/dev/null; then
    echo "Converting to MP3..."
    ffmpeg -i "$WAV" -c:a libmp3lame -q:a 2 "$MP3" -y -loglevel error
    echo "✅ $MP3"
  else
    echo "✅ $WAV (ffmpeg not available for MP3 conversion)"
  fi
}

_play() {
  local NAME="$1"
  local CHANNEL="${2:-}"
  local COMP="$COMP_DIR/${NAME}.js"

  if [ ! -f "$COMP" ]; then
    echo "❌ Composition not found: $NAME"
    echo "Available: $(ls "$COMP_DIR"/*.js 2>/dev/null | xargs -I{} basename {} .js | tr '\n' ', ')"
    exit 1
  fi

  local WAV="$TMP_DIR/${NAME}-48k.wav"
  _render "$COMP" 16 120
  echo "Converting for VC (48kHz stereo)..."
  ffmpeg -i "$TMP_DIR/${NAME}.wav" -ar 48000 -ac 2 "$WAV" -y -loglevel error
  echo "Streaming to VC..."
  if [ -n "$CHANNEL" ]; then
    DISCORD_CHANNEL_ID="$CHANNEL" node "$ROOT_DIR/scripts/vc-play.mjs" "$WAV"
  else
    node "$ROOT_DIR/scripts/vc-play.mjs" "$WAV"
  fi
}

_list() {
  echo "🎵 Available Compositions"
  echo "========================="
  for f in "$COMP_DIR"/*.js; do
    [ -f "$f" ] || continue
    local name title mood tempo
    name=$(basename "$f" .js)
    title=$(grep -oP '@title\s+\K.*' "$f" 2>/dev/null || echo "$name")
    mood=$(grep -oP '@mood\s+\K.*' "$f" 2>/dev/null || echo "—")
    tempo=$(grep -oP '@tempo\s+\K.*' "$f" 2>/dev/null || echo "—")
    printf "  %-25s %s (mood: %s, tempo: %s)\n" "$name" "$title" "$mood" "$tempo"
  done
  echo ""
  echo "$(ls "$COMP_DIR"/*.js 2>/dev/null | wc -l) compositions available"
}

_concert() {
  local TRACKS=("$@")
  echo "🎵 Concert: ${#TRACKS[@]} tracks"
  echo "========================="
  for name in "${TRACKS[@]}"; do
    local comp="$COMP_DIR/${name}.js"
    if [ ! -f "$comp" ]; then
      echo "⚠️ Skipping $name (not found)"
      continue
    fi
    echo ""
    echo "▶ Now playing: $name"
    _play "$name"
    echo "✅ Finished: $name"
    # Brief pause between tracks for VC settling
    sleep 2
  done
  echo ""
  echo "🎵 Concert complete!"
}

case "${1:-help}" in
  render)
    shift
    _render "${1:?Usage: dispatch.sh render <file.js> [cycles] [bpm]}" "${2:-16}" "${3:-120}"
    ;;
  play)
    shift
    _play "${1:?Usage: dispatch.sh play <name> [channel-id]}" "${2:-}"
    ;;
  list)
    _list
    ;;
  samples)
    shift
    exec bash "$SCRIPT_DIR/samples-manage.sh" "$@"
    ;;
  concert)
    shift
    if [ $# -eq 0 ]; then
      echo "Usage: dispatch.sh concert <name1> [name2] [name3] ..."
      exit 1
    fi
    _concert "$@"
    ;;
  help|*)
    echo "strudel-music dispatch"
    echo ""
    echo "Usage: dispatch.sh <command> [args]"
    echo ""
    echo "Commands:"
    echo "  render <file.js> [cycles] [bpm]  — Render a composition to WAV/MP3"
    echo "  play <name> [channel-id]         — Render + stream to Discord VC"
    echo "  list                              — Show available compositions"
    echo "  samples <subcommand> [args]       — Manage sample packs"
    echo "  concert <name1> [name2] ...       — Play a setlist in Discord VC"
    ;;
esac
