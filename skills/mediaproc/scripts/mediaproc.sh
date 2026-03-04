#!/bin/bash
# SSH wrapper for mediaproc commands.
# Requires MEDIAPROC_HOST and MEDIAPROC_PORT env vars.
#
# Usage:
#   mediaproc <command> [args]           Run a command
#   mediaproc <command> [args] < file    Pipe stdin (e.g. file upload)
#   mediaproc <command> [args] > file    Capture stdout (e.g. file download)

: "${MEDIAPROC_HOST:?MEDIAPROC_HOST not set}"
: "${MEDIAPROC_PORT:?MEDIAPROC_PORT not set}"

exec ssh -p "$MEDIAPROC_PORT" \
    -o StrictHostKeyChecking=accept-new \
    -o LogLevel=ERROR \
    "mediaproc@$MEDIAPROC_HOST" "$*"
