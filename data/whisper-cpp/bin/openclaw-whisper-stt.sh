#!/usr/bin/env bash
set -euo pipefail

MEDIA_PATH="${1:?usage: openclaw-whisper-stt <audio-file>}"
MODEL_NAME="${OPENCLAW_WHISPER_MODEL:-base}"
LANG_NAME="${OPENCLAW_WHISPER_LANG:-auto}"

MODELS_DIR="$HOME/.cache/whisper"
WHISPER_CLI="$HOME/.local/bin/whisper-cli"

# ensure locally-installed whisper.cpp shared libs are discoverable
export LD_LIBRARY_PATH="$HOME/.local/lib:${LD_LIBRARY_PATH:-}"

case "$MODEL_NAME" in
  base|small) ;;
  *) echo "OPENCLAW_WHISPER_MODEL must be base|small (got: $MODEL_NAME)" >&2; exit 2;;
 esac

case "$LANG_NAME" in
  auto|en|es|pt|ru|fr|de|it|zh|ja|ko|ar|hi) ;;
  *) echo "OPENCLAW_WHISPER_LANG should be a Whisper language code like auto|en|ru (got: $LANG_NAME)" >&2;;
esac

MODEL_PATH="$MODELS_DIR/ggml-$MODEL_NAME.bin"
[ -f "$MODEL_PATH" ] || { echo "Model not found: $MODEL_PATH" >&2; exit 3; }

TMP_WAV=""
cleanup() {
  if [ -n "$TMP_WAV" ] && [ -f "$TMP_WAV" ]; then rm -f "$TMP_WAV"; fi
}
trap cleanup EXIT

INPUT="$MEDIA_PATH"
# Telegram voice notes are commonly OGG+Opus. Convert to 16kHz mono PCM wav for whisper-cli.
case "${MEDIA_PATH,,}" in
  *.ogg|*.opus|*.m4a|*.mp3|*.flac|*.webm)
    TMP_WAV="$(mktemp -t openclaw-whisper-XXXXXX.wav)"
    ffmpeg -hide_banner -loglevel error -y -i "$MEDIA_PATH" -ar 16000 -ac 1 -c:a pcm_s16le "$TMP_WAV"
    INPUT="$TMP_WAV"
    ;;
  *.wav) ;;
  *) ;;
esac

"$WHISPER_CLI" -m "$MODEL_PATH" -l "$LANG_NAME" -f "$INPUT" -nt -np
