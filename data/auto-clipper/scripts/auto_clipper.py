#!/usr/bin/env python3
"""
AutoClipper - Automatic video clip generator
Main entry point for the skill
"""

import argparse
import json
import os
import sys
import subprocess
from pathlib import Path
from datetime import datetime

SKILL_DIR = Path(__file__).parent.parent
CONFIG_PATH = SKILL_DIR / "config.json"
PROCESSED_LOG = SKILL_DIR / "logs" / "processed.json"


def load_config():
    """Load configuration from config.json"""
    with open(CONFIG_PATH) as f:
        return json.load(f)


def get_processed():
    """Get list of already processed files"""
    if PROCESSED_LOG.exists():
        with open(PROCESSED_LOG) as f:
            return json.load(f).get("processed", [])
    return []


def save_processed(processed):
    """Save processed file list"""
    PROCESSED_LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(PROCESSED_LOG, "w") as f:
        json.dump({"processed": processed, "last_updated": datetime.now().isoformat()}, f, indent=2)


def get_watch_folder(config):
    """Resolve watch folder path"""
    return Path(os.path.expanduser(config["watchFolder"]))


def get_output_folder(config):
    """Resolve and create output folder"""
    output = Path(os.path.expanduser(config["outputFolder"]))
    output.mkdir(parents=True, exist_ok=True)
    # Date-based subfolder
    dated = output / datetime.now().strftime("%Y-%m-%d")
    dated.mkdir(parents=True, exist_ok=True)
    return dated


def scan_folder(config):
    """Scan watch folder for new media files"""
    watch = get_watch_folder(config)
    if not watch.exists():
        print(f"Watch folder does not exist: {watch}")
        return []
    
    extensions = config.get("fileExtensions", [".mp4", ".mov", ".mkv"])
    processed = get_processed()
    
    files = []
    for ext in extensions:
        for f in watch.glob(f"*{ext}"):
            if str(f) not in processed:
                files.append(f)
    
    return files


def get_duration(filepath):
    """Get video duration using ffprobe"""
    try:
        result = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration", 
             "-of", "default=noprint_wrappers=1:nokey=1", str(filepath)],
            capture_output=True, text=True, timeout=30
        )
        return float(result.stdout.strip()) if result.stdout.strip() else 0
    except Exception as e:
        print(f"Error getting duration: {e}")
        return 0


def create_clip(config, input_file, start=0, duration=None):
    """Create a clip using ffmpeg"""
    output_dir = get_output_folder(config)
    stem = input_file.stem
    timestamp = datetime.now().strftime("%H%M%S")
    output_file = output_dir / f"{stem}_{timestamp}.mp4"
    
    settings = config.get("clipSettings", {})
    
    # Build ffmpeg command
    cmd = ["ffmpeg", "-y", "-i", str(input_file)]
    
    if start > 0:
        cmd.extend(["-ss", str(start)])
    
    if duration:
        cmd.extend(["-t", str(duration)])
    elif settings.get("defaultDuration"):
        cmd.extend(["-t", str(settings["defaultDuration"])])
    
    # Fast trim if enabled (no re-encode)
    if settings.get("fastTrim", True):
        cmd.extend(["-c", "copy"])
    
    cmd.extend(["-avoid_negative_ts", "make_zero", str(output_file)])
    
    print(f"Running: {' '.join(cmd)}")
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0 and output_file.exists():
        print(f"✓ Created: {output_file}")
        return output_file
    else:
        print(f"✗ Failed: {result.stderr}")
        return None


def run_analysis(config, media_file):
    """Analyze media using Agent Swarm (placeholder - requires gateway)"""
    if not config.get("intentRouter", {}).get("enabled", False):
        return None
    
    # This would use Agent Swarm to determine clip strategy
    # For now, return None to use default clip settings
    print(f"Agent Swarm analysis not yet implemented for {media_file.name}")
    return None


def run(dry_run=False, force=False):
    """Main run function"""
    config = load_config()
    
    print("=" * 50)
    print("AutoClipper - Video Clip Generator")
    print("=" * 50)
    
    files = scan_folder(config)
    
    if not files:
        print("No new files to process.")
        return
    
    print(f"Found {len(files)} new file(s)")
    
    processed = get_processed()
    
    for f in files:
        print(f"\nProcessing: {f.name}")
        
        duration = get_duration(f)
        print(f"  Duration: {duration:.1f}s")
        
        # Analyze (if Agent Swarm enabled)
        clip_plan = run_analysis(config, f)
        
        if clip_plan:
            for i, clip in enumerate(clip_plan):
                create_clip(config, f, clip.get("start"), clip.get("duration"))
        else:
            # Default: create one clip of default duration
            clip_settings = config.get("clipSettings", {})
            default_dur = clip_settings.get("defaultDuration", 60)
            create_clip(config, f, duration=min(default_dur, duration))
        
        if not force:
            processed.append(str(f))
    
    if not force:
        save_processed(processed)
    
    print(f"\n✓ Processed {len(files)} file(s)")


def watch_mode():
    """Continuous watcher mode (placeholder)"""
    print("Watch mode not yet implemented")
    print("Use cron instead: 0 * * * * /path/to/run.sh")


def show_status():
    """Show current status"""
    config = load_config()
    processed = get_processed()
    
    print("AutoClipper Status")
    print("=" * 30)
    print(f"Watch folder: {get_watch_folder(config)}")
    print(f"Output folder: {get_output_folder(config)}")
    print(f"Files processed: {len(processed)}")
    print(f"Pending: {len(scan_folder(config))}")


def main():
    parser = argparse.ArgumentParser(description="AutoClipper - Automatic video clip generator")
    parser.add_argument("command", choices=["run", "watch", "status"], default="run")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be processed")
    parser.add_argument("--force", action="store_true", help="Force reprocess all files")
    parser.add_argument("--output", help="Output subfolder name (for cron)")
    
    args = parser.parse_args()
    
    if args.command == "run":
        run(dry_run=args.dry_run, force=args.force)
    elif args.command == "watch":
        watch_mode()
    elif args.command == "status":
        show_status()


if __name__ == "__main__":
    main()