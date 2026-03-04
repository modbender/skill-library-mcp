#!/bin/bash
# Cron job setup for automated video downloads
# Usage: setup_cron.sh [install|remove|status]

SKILL_DIR="/root/.openclaw/workspace/skills/video-news-downloader"
WORKSPACE="/root/.openclaw/workspace"

# Beijing Time 20:00 = UTC 12:00
VIDEO_CRON="0 12 * * * cd $SKILL_DIR && python3 scripts/video_download.py --cbs --bbc --proofread >> $WORKSPACE/logs/video-download.log 2>&1"

# Beijing Time 20:30 = UTC 12:30  
PROOFREAD_CRON="30 12 * * * cd $SKILL_DIR && python3 scripts/subtitle_proofreader.py --all >> $WORKSPACE/logs/proofread.log 2>&1"

# Ensure log directory exists
mkdir -p "$WORKSPACE/logs"

case "${1:-status}" in
    install)
        echo "Installing video download cron jobs..."
        
        # Add video download job
        (crontab -l 2>/dev/null | grep -v "video_download.py"; echo "$VIDEO_CRON") | crontab -
        
        # Add proofreading job  
        (crontab -l 2>/dev/null | grep -v "subtitle_proofreader.py"; echo "$PROOFREAD_CRON") | crontab -
        
        echo "✅ Cron jobs installed!"
        echo ""
        echo "Schedule (Beijing Time):"
        echo "  20:00 - Download latest CBS + BBC videos"
        echo "  20:30 - DeepSeek proofread subtitles"
        echo ""
        crontab -l | grep -E "(video_download|subtitle_proofreader)"
        ;;
        
    remove)
        echo "Removing video download cron jobs..."
        crontab -l 2>/dev/null | grep -v "video_download.py" | grep -v "subtitle_proofreader.py" | crontab -
        echo "✅ Cron jobs removed!"
        ;;
        
    status)
        echo "Current video download cron jobs:"
        echo "================================="
        crontab -l 2>/dev/null | grep -E "(video_download|subtitle_proofreader)" || echo "No jobs found"
        ;;
        
    *)
        echo "Usage: $0 [install|remove|status]"
        exit 1
        ;;
esac
