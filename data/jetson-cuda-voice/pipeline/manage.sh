#!/usr/bin/env bash
# Jetson CUDA Voice Pipeline — management script

WHISPER_SVC="whisper-server"
VOICE_SVC="voice-pipeline"
MIC="${VOICE_MIC:-hw:Array,0}"
SPEAKER="${VOICE_SPEAKER:-hw:C2c,0}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

usage() {
    echo "Usage: $0 {install|start|stop|restart|status|logs|test-mic|test-tts|test-stt}"
    exit 1
}

cmd="${1:-status}"

case "$cmd" in
  install)
    bash "$SCRIPT_DIR/setup.sh"
    ;;
  start)
    systemctl --user start "$WHISPER_SVC" "$VOICE_SVC"
    echo "✅ Services started"
    ;;
  stop)
    systemctl --user stop "$VOICE_SVC" "$WHISPER_SVC"
    echo "⚫ Services stopped"
    ;;
  restart)
    systemctl --user restart "$WHISPER_SVC"
    sleep 2
    systemctl --user restart "$VOICE_SVC"
    echo "🔄 Services restarted"
    ;;
  status)
    echo "=== Whisper Server ==="
    systemctl --user status "$WHISPER_SVC" --no-pager || true
    echo ""
    echo "=== Voice Pipeline ==="
    systemctl --user status "$VOICE_SVC" --no-pager || true
    ;;
  logs)
    echo "--- Whisper Server ---"
    tail -n 20 /tmp/whisper-server.log 2>/dev/null || echo "(no log yet)"
    echo ""
    echo "--- Voice Pipeline ---"
    tail -f /tmp/voice-pipeline.log
    ;;
  test-mic)
    echo "Recording 4s from $MIC ... speak now"
    arecord -D "$MIC" -f S24_3LE -r 16000 -c 2 -d 4 /tmp/test-mic.wav
    echo "Playing back..."
    aplay -D "plughw:${SPEAKER#hw:}" /tmp/test-mic.wav
    ;;
  test-tts)
    TEXT="${2:-Hello, I am your Jetson voice assistant.}"
    echo "Speaking: $TEXT"
    python3 -c "
import sys; sys.path.insert(0, '$SCRIPT_DIR')
import os; os.environ.setdefault('VOICE_SPEAKER', '$SPEAKER')
from voice_pipeline import speak, load_piper; load_piper(); speak('$TEXT')
"
    ;;
  test-stt)
    echo "Recording 4s from $MIC ... speak now"
    arecord -D "$MIC" -f S24_3LE -r 16000 -c 2 -d 4 /tmp/test-stt.wav
    echo "Transcribing..."
    curl -s http://127.0.0.1:8181/inference \
        -F "file=@/tmp/test-stt.wav" \
        -F "language=auto" \
        -F "response_format=json" \
    | python3 -c "import sys,json; print(json.load(sys.stdin).get('text','(empty)'))"
    ;;
  *)
    usage
    ;;
esac
