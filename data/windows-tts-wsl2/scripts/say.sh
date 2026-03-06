#!/usr/bin/env bash
set -euo pipefail

VOICE=""
RATE=""
VOLUME=""

usage() {
  cat <<'EOF'
Usage:
  say.sh [--voice "VOICE_NAME"] [--rate -10..10] [--volume 0..100] "TEXT..."

Examples:
  say.sh "你好，我是你的助手。"
  say.sh --voice "Microsoft Xiaoxiao - Chinese (Simplified, PRC)" "你好"
EOF
}

# Parse flags
while [[ $# -gt 0 ]]; do
  case "$1" in
    -h|--help)
      usage; exit 0 ;;
    --voice)
      VOICE=${2:-}; shift 2 ;;
    --rate)
      RATE=${2:-}; shift 2 ;;
    --volume)
      VOLUME=${2:-}; shift 2 ;;
    --)
      shift; break ;;
    *)
      break ;;
  esac
done

if [[ $# -lt 1 ]]; then
  usage >&2
  exit 1
fi

TEXT="$*"

PS="Add-Type -AssemblyName System.Speech; \$s=[System.Speech.Synthesis.SpeechSynthesizer]::new();"

if [[ -n "$VOICE" ]]; then
  VOICE_ESC=$(printf '%s' "$VOICE" | sed 's/"/`"/g')
  PS+=" \$s.SelectVoice(\"$VOICE_ESC\");"
fi

if [[ -n "$RATE" ]]; then
  PS+=" \$s.Rate=[int]$RATE;"
fi

if [[ -n "$VOLUME" ]]; then
  PS+=" \$s.Volume=[int]$VOLUME;"
fi

TEXT_ESC=$(printf '%s' "$TEXT" | sed 's/"/`"/g')
PS+=" \$s.Speak(\"$TEXT_ESC\");"

powershell.exe -NoProfile -Command "$PS" >/dev/null
