#!/bin/bash
# backup_to_proton.sh — Sync critical data to Proton Drive for cloud backup
# Run periodically (daily via cron or heartbeat)
# Safe to run multiple times — uses rsync/cp with overwrites

set -euo pipefail

PROTON="$HOME/Library/CloudStorage/ProtonDrive-user@proton.me-folder"
WORKSPACE="$HOME/.openclaw/workspace"
TIMESTAMP=$(date +%Y-%m-%d_%H%M)

echo "[$TIMESTAMP] Starting Proton Drive backup..."

# ── Ensure directories ────────────────────────────────────────────────────────
mkdir -p "$PROTON/Vault/config/launchagents"
mkdir -p "$PROTON/Vault/daily"
mkdir -p "$PROTON/Artifacts/avatars"
mkdir -p "$PROTON/Artifacts/audio"
mkdir -p "$PROTON/Artifacts/videos"
mkdir -p "$PROTON/Artifacts/docker-backups"

# ── 1. LaunchAgent plists (critical — no other backup) ────────────────────────
cp ~/Library/LaunchAgents/com.openclaw.*.plist "$PROTON/Vault/config/launchagents/" 2>/dev/null || true
cp ~/Library/LaunchAgents/ai.openclaw.*.plist "$PROTON/Vault/config/launchagents/" 2>/dev/null || true
echo "  ✅ LaunchAgent plists synced"

# ── 2. OpenClaw config ────────────────────────────────────────────────────────
cp "$HOME/.openclaw/openclaw.json" "$PROTON/Vault/config/openclaw.json"
echo "  ✅ openclaw.json synced"

# ── 3. Memory files → Vault/daily ─────────────────────────────────────────────
rsync -a --update "$WORKSPACE/memory/"*.md "$PROTON/Vault/daily/" 2>/dev/null || true
echo "  ✅ Memory files synced to Vault/daily"

# ── 4. MEMORY.md (long-term memory) ──────────────────────────────────────────
cp "$WORKSPACE/MEMORY.md" "$PROTON/Vault/MEMORY.md"
echo "  ✅ MEMORY.md synced"

# ── 5. Avatars ────────────────────────────────────────────────────────────────
cp "$WORKSPACE/content/avatar-"*.png "$PROTON/Artifacts/avatars/" 2>/dev/null || true
echo "  ✅ Avatars synced"

# ── 6. Content drafts (markdown only — small) ────────────────────────────────
mkdir -p "$PROTON/Vault/content-drafts"
rsync -a --update --include="*.md" --exclude="*" "$WORKSPACE/content/" "$PROTON/Vault/content-drafts/" 2>/dev/null || true
echo "  ✅ Content drafts synced"

# ── 6b. Generated media (images + videos from content/) ──────────────────────
# Sync non-avatar images and videos to Proton Drive with date-based structure
TODAY_DIR="$PROTON/Artifacts/images/$(date +%Y/%m/%d)"
mkdir -p "$TODAY_DIR"
mkdir -p "$PROTON/Artifacts/videos"
# Images (non-avatar PNGs + JPGs)
for f in "$WORKSPACE/content/"*.png "$WORKSPACE/content/"*.jpg; do
    [ -f "$f" ] || continue
    fname=$(basename "$f")
    [[ "$fname" == avatar-* ]] && continue  # avatars handled separately
    cp -n "$f" "$TODAY_DIR/" 2>/dev/null || true
done
# Videos
for f in "$WORKSPACE/content/"*.mp4; do
    [ -f "$f" ] || continue
    cp -n "$f" "$PROTON/Artifacts/videos/" 2>/dev/null || true
done
echo "  ✅ Generated media synced"

# ── 7. Agent OUTBOX/ROLE files ────────────────────────────────────────────────
mkdir -p "$PROTON/Vault/agents"
for agent_dir in "$WORKSPACE/agents"/*/; do
    agent=$(basename "$agent_dir")
    mkdir -p "$PROTON/Vault/agents/$agent"
    cp "$agent_dir"*.md "$PROTON/Vault/agents/$agent/" 2>/dev/null || true
done
echo "  ✅ Agent files synced"

# ── 8. Docker volume backup (weekly — large, slow) ───────────────────────────
# Only run if --docker flag is passed
if [[ "${1:-}" == "--docker" ]]; then
    echo "  🐳 Backing up Docker volumes (this takes a while)..."
    for vol in langfuse_postgres_data langfuse_clickhouse_data qdrant_data weaviate_data pgvector_data; do
        full="hybrid-control-plane_${vol}"
        docker volume inspect "$full" >/dev/null 2>&1 || continue
        echo "    Backing up $vol..."
        docker run --rm -v "${full}:/data" -v "$PROTON/Artifacts/docker-backups:/backup" \
            alpine tar czf "/backup/${vol}_${TIMESTAMP}.tar.gz" -C /data . 2>/dev/null || \
            echo "    ⚠️ Failed to backup $vol"
    done
    # Keep only last 3 backups per volume
    for vol in langfuse_postgres_data langfuse_clickhouse_data qdrant_data weaviate_data pgvector_data; do
        ls -t "$PROTON/Artifacts/docker-backups/${vol}_"*.tar.gz 2>/dev/null | tail -n +4 | xargs rm -f 2>/dev/null || true
    done
    echo "  ✅ Docker volumes backed up"
else
    echo "  ⏭️  Docker volumes skipped (use --docker to include)"
fi

# ── 9. Truncation — keep Proton Drive lean ────────────────────────────────────
echo "  🧹 Running truncation..."

# Docker backups: keep last 3 per volume (already handled above)

# Images: keep last 90 days of generated images
find "$PROTON/Artifacts/images" -name "*.png" -mtime +90 -delete 2>/dev/null || true
find "$PROTON/Artifacts/images" -name "*.json" -mtime +90 -delete 2>/dev/null || true
# Remove empty date directories
find "$PROTON/Artifacts/images" -type d -empty -delete 2>/dev/null || true

# Audio: keep last 30 days
find "$PROTON/Artifacts/audio" -name "*.wav" -mtime +30 -delete 2>/dev/null || true
find "$PROTON/Artifacts/audio" -name "*.mp3" -mtime +30 -delete 2>/dev/null || true

# Videos: keep last 60 days
find "$PROTON/Artifacts/videos" -name "*.mp4" -mtime +60 -delete 2>/dev/null || true

# Daily memory files in Vault: keep last 60 days
find "$PROTON/Vault/daily" -name "*.md" -mtime +60 -delete 2>/dev/null || true

# Docker volume backups: keep last 3 per volume type
for pattern in langfuse_postgres langfuse_clickhouse qdrant weaviate pgvector grafana; do
    ls -t "$PROTON/Artifacts/docker-backups/${pattern}"*.tar.gz 2>/dev/null | tail -n +4 | xargs rm -f 2>/dev/null || true
done

echo "  ✅ Truncation complete"

# ── 10. Space report ──────────────────────────────────────────────────────────
echo ""
echo "Backup complete at $(date)"
TOTAL=$(du -sh "$PROTON" | awk '{print $1}')
echo "Proton Drive total: $TOTAL"

# Warn if over 500MB
SIZE_KB=$(du -sk "$PROTON" | awk '{print $1}')
if [ "$SIZE_KB" -gt 512000 ]; then
    echo "⚠️  WARNING: Proton Drive over 500MB ($TOTAL) — review large files"
fi
