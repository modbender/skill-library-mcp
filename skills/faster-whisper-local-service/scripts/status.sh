#!/usr/bin/env bash
set -euo pipefail

systemctl --user is-active openclaw-transcribe.service
curl -s -o /tmp/fws-health.json -w 'http:%{http_code}\n' http://127.0.0.1:18790/transcribe -X POST -H 'Content-Type: application/octet-stream' --data-binary 'x'
head -c 200 /tmp/fws-health.json || true
echo
