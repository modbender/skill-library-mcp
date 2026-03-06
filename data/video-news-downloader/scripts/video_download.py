#!/usr/bin/env python3
"""
Video News Downloader - Download CBS Evening News and BBC News at Ten
Usage: python3 video_download.py [--cbs] [--bbc] [--proofread]
"""

import argparse
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# Configuration
WORKSPACE = "/root/.openclaw/workspace"
CBS_DIR = f"{WORKSPACE}/cbs-live-local"
BBC_DIR = f"{WORKSPACE}/bbc-news-live"
TEMP_DIR = f"{WORKSPACE}/temp"

CBS_PLAYLIST = "https://www.youtube.com/playlist?list=PLotzEBRQdc0cMXjf4FKw6_1Pu8in6rzBQ"
BBC_SEARCH = "BBC News at Ten"

def ensure_dirs():
    """Ensure all required directories exist"""
    for d in [CBS_DIR, BBC_DIR, TEMP_DIR]:
        os.makedirs(d, exist_ok=True)

def download_cbs():
    """Download latest CBS Evening News"""
    print("📺 Downloading CBS Evening News...")
    
    # Get latest video URL from playlist
    cmd = [
        "yt-dlp", "--flat-playlist", "--playlist-end", "1",
        "--print", "%(url)s", CBS_PLAYLIST
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        video_url = result.stdout.strip()
        if not video_url:
            print("❌ Could not get CBS video URL")
            return False
    except Exception as e:
        print(f"❌ Error getting CBS URL: {e}")
        return False
    
    # Download video + auto subtitles
    output_template = f"{CBS_DIR}/cbs_latest.%(ext)s"
    
    cmd = [
        "yt-dlp",
        "-f", "18",  # 360p MP4 for smaller size
        "--write-auto-subs",
        "--sub-langs", "en",
        "--convert-subs", "vtt",
        "-o", output_template,
        video_url
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        if result.returncode == 0:
            print("✅ CBS download complete")
            # Backup original subtitle if exists
            backup_subtitle(f"{CBS_DIR}/cbs_latest.en.vtt")
            return True
        else:
            print(f"❌ CBS download failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error downloading CBS: {e}")
        return False

def download_bbc():
    """Download latest BBC News at Ten"""
    print("📺 Downloading BBC News at Ten...")
    
    # Search for latest BBC News at Ten
    cmd = [
        "yt-dlp", "--default-search", "ytsearch1",
        "--print", "%(url)s", f"ytsearch1:{BBC_SEARCH}"
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        video_url = result.stdout.strip()
        if not video_url:
            print("❌ Could not get BBC video URL")
            return False
    except Exception as e:
        print(f"❌ Error getting BBC URL: {e}")
        return False
    
    # Save source URL
    with open(f"{BBC_DIR}/source_url.txt", 'w') as f:
        f.write(video_url)
    
    # Download video + auto subtitles
    output_template = f"{BBC_DIR}/bbc_news_latest.%(ext)s"
    
    cmd = [
        "yt-dlp",
        "-f", "18",
        "--write-auto-subs",
        "--sub-langs", "en",
        "--convert-subs", "vtt",
        "-o", output_template,
        video_url
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        if result.returncode == 0:
            print("✅ BBC download complete")
            # Backup original subtitle
            backup_subtitle(f"{BBC_DIR}/bbc_news_latest.en.vtt")
            return True
        else:
            print(f"❌ BBC download failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error downloading BBC: {e}")
        return False

def backup_subtitle(vtt_path):
    """Create backup of original subtitle"""
    backup_path = vtt_path.replace('.vtt', '-backup.vtt')
    if os.path.exists(vtt_path) and not os.path.exists(backup_path):
        import shutil
        shutil.copy(vtt_path, backup_path)
        print(f"   📄 Backed up subtitle: {backup_path}")

def cleanup_old_files(days=2):
    """Remove video files older than specified days"""
    print(f"🗑️ Cleaning up files older than {days} days...")
    
    import time
    now = time.time()
    cutoff = now - (days * 24 * 3600)
    
    patterns = ['bbc_*.mp4', 'bbc_*.vtt', 'cbs_*.mp4', 'cbs_*.vtt']
    
    for pattern in patterns:
        for f in Path(WORKSPACE).glob(pattern):
            if f.stat().st_mtime < cutoff:
                try:
                    f.unlink()
                    print(f"   🗑️ Deleted: {f.name}")
                except Exception as e:
                    print(f"   ⚠️ Could not delete {f}: {e}")

def main():
    parser = argparse.ArgumentParser(description='Download news videos')
    parser.add_argument('--cbs', action='store_true', help='Download CBS Evening News')
    parser.add_argument('--bbc', action='store_true', help='Download BBC News at Ten')
    parser.add_argument('--proofread', action='store_true', help='Proofread subtitles after download')
    parser.add_argument('--cleanup', type=int, default=2, help='Days to keep old files (default: 2)')
    
    args = parser.parse_args()
    
    if not args.cbs and not args.bbc:
        print("Please specify --cbs and/or --bbc")
        parser.print_help()
        sys.exit(1)
    
    ensure_dirs()
    results = []
    
    if args.cbs:
        results.append(('CBS', download_cbs()))
    
    if args.bbc:
        results.append(('BBC', download_bbc()))
    
    # Cleanup old files
    cleanup_old_files(args.cleanup)
    
    # Summary
    print("\n" + "="*50)
    print("Download Summary:")
    for name, success in results:
        status = "✅" if success else "❌"
        print(f"   {status} {name}")
    print("="*50)
    
    # Trigger proofreading if requested
    if args.proofread:
        print("\n🤖 Starting subtitle proofreading...")
        import subprocess
        if args.cbs and os.path.exists(f"{CBS_DIR}/cbs_latest.en.vtt"):
            subprocess.run([sys.executable, "scripts/subtitle_proofreader.py", 
                          f"{CBS_DIR}/cbs_latest.en.vtt"])
        if args.bbc and os.path.exists(f"{BBC_DIR}/bbc_news_latest.en.vtt"):
            subprocess.run([sys.executable, "scripts/subtitle_proofreader.py",
                          f"{BBC_DIR}/bbc_news_latest.en.vtt"])
    
    return 0 if all(r[1] for r in results) else 1

if __name__ == '__main__':
    sys.exit(main())
