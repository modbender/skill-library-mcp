#!/usr/bin/env bash
set -euo pipefail

ROOT="/Users/mlo/.openclaw/workspace/maylo-voice-assistant"
cd "$ROOT"

source "$ROOT/venv/bin/activate"

# Kill any previous copies (best-effort)
pkill -f "python .*bridge/milo_responder_stub.py" 2>/dev/null || true
pkill -f "python .*bridge/milo_responder_openclaw.py" 2>/dev/null || true
pkill -f "python .*main.py --mode full" 2>/dev/null || true

# Start OpenClaw responder (real Milo, embedded local)
export PYTHONUNBUFFERED=1

nohup python -u "$ROOT/bridge/milo_responder_openclaw.py" >"$ROOT/recordings/responder.log" 2>&1 &

# Start full assistant (wake word + record + whisper + say)
# Optional: set MAYLO_INPUT_DEVICE to force a specific input.
# export MAYLO_INPUT_DEVICE="1"

# Lower threshold a bit for real-world pickup
export MAYLO_WAKE_THRESHOLD="0.35"

# Print wake scores periodically for debugging
export MAYLO_WAKE_DEBUG="1"

nohup python -u "$ROOT/main.py" --mode full >"$ROOT/recordings/assistant.log" 2>&1 &

echo "Started: openclaw-responder + assistant. Logs: recordings/responder.log, recordings/assistant.log"
