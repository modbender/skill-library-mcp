#!/bin/bash
# DMAF Media Sync — uploads new WhatsApp media (photos + videos) to GCS staging bucket.
# Runs via system crontab — no LLM tokens, no OpenClaw agent involvement.
#
# Install:
#   cp dmaf-sync.sh ~/.openclaw/workspace/scripts/dmaf-sync.sh
#   chmod +x ~/.openclaw/workspace/scripts/dmaf-sync.sh
#
# Add to crontab:
#   */30 * * * * /home/openclaw/.openclaw/workspace/scripts/dmaf-sync.sh >> /tmp/dmaf-sync.log 2>&1

INBOUND_DIR="${HOME}/.openclaw/media/inbound"
GCS_BUCKET="gs://your-project-whatsapp-media"   # ← set this to your staging bucket
SYNCED=0
FAILED=0

# Images
for f in "${INBOUND_DIR}"/*.{jpg,jpeg,png,heic,webp}; do
    [ -f "$f" ] || continue
    basename=$(basename "$f")
    if gsutil -q cp "$f" "${GCS_BUCKET}/${basename}" 2>/dev/null; then
        rm "$f" && SYNCED=$((SYNCED + 1))
    else
        FAILED=$((FAILED + 1)) && echo "[$(date -Iseconds)] Failed: $basename" >&2
    fi
done

# Videos
for f in "${INBOUND_DIR}"/*.{mp4,mov,avi,3gp,mkv,webm}; do
    [ -f "$f" ] || continue
    basename=$(basename "$f")
    if gsutil -q cp "$f" "${GCS_BUCKET}/${basename}" 2>/dev/null; then
        rm "$f" && SYNCED=$((SYNCED + 1))
    else
        FAILED=$((FAILED + 1)) && echo "[$(date -Iseconds)] Failed: $basename" >&2
    fi
done

echo "[$(date -Iseconds)] Synced: $SYNCED | Failed: $FAILED"
