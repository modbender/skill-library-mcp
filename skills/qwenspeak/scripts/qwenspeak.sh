#!/bin/bash
# SSH wrapper for qwenspeak commands.
# Requires QWENSPEAK_HOST and QWENSPEAK_PORT env vars.
#
# Usage:
#   qwenspeak <command> [args]           Run a command
#   qwenspeak <command> [args] < file    Pipe stdin (e.g. YAML config, file upload)
#   qwenspeak <command> [args] > file    Capture stdout (e.g. file download)

: "${QWENSPEAK_HOST:?QWENSPEAK_HOST not set}"
: "${QWENSPEAK_PORT:?QWENSPEAK_PORT not set}"

exec ssh -p "$QWENSPEAK_PORT" \
    -o StrictHostKeyChecking=accept-new \
    -o LogLevel=ERROR \
    "tts@$QWENSPEAK_HOST" "$*"
