#!/usr/bin/env python3
"""Cut clips from video with ffmpeg. Handles vertical conversion."""

import argparse
import json
import subprocess
import sys
from pathlib import Path

def get_video_info(input_path: str) -> dict:
    """Get video dimensions and duration."""
    cmd = [
        "ffprobe", "-v", "quiet",
        "-show_entries", "stream=width,height,duration",
        "-show_entries", "format=duration",
        "-of", "json", input_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    data = json.loads(result.stdout)
    
    width = height = 0
    for stream in data.get("streams", []):
        if "width" in stream:
            width = stream["width"]
            height = stream["height"]
            break
    
    duration = float(data.get("format", {}).get("duration", 0))
    return {"width": width, "height": height, "duration": duration}

def time_to_seconds(time_str: str) -> float:
    """Convert MM:SS or HH:MM:SS to seconds."""
    parts = time_str.split(":")
    if len(parts) == 2:
        return int(parts[0]) * 60 + float(parts[1])
    elif len(parts) == 3:
        return int(parts[0]) * 3600 + int(parts[1]) * 60 + float(parts[2])
    return float(time_str)

def clip_video(input_path: str, start: str, end: str, output_path: str, 
               vertical: bool = True, mode: str = "crop"):
    """Cut and optionally convert to vertical."""
    info = get_video_info(input_path)
    start_s = time_to_seconds(start)
    end_s = time_to_seconds(end)
    duration = end_s - start_s
    
    print(f"Cutting: {start} → {end} ({duration:.0f}s)")
    print(f"Source: {info['width']}x{info['height']}")
    
    filter_parts = []
    
    if vertical and info["width"] > info["height"]:
        if mode == "crop":
            # Center crop to 9:16
            target_w = int(info["height"] * 9 / 16)
            x_offset = (info["width"] - target_w) // 2
            filter_parts.append(f"crop={target_w}:{info['height']}:{x_offset}:0")
            filter_parts.append("scale=1080:1920")
            print(f"Cropping to vertical: {target_w}x{info['height']} → 1080x1920")
        elif mode == "blur":
            # Blurred background with video centered
            filter_parts = []
            vf = (
                f"split[bg][fg];"
                f"[bg]scale=1080:1920:force_original_aspect_ratio=increase,"
                f"crop=1080:1920,boxblur=20:20[bg2];"
                f"[fg]scale=1080:-2:force_original_aspect_ratio=decrease[fg2];"
                f"[bg2][fg2]overlay=(W-w)/2:(H-h)/2"
            )
            filter_parts = [vf]
            print("Blur-background vertical mode")
        elif mode == "none":
            print("Keeping original aspect ratio")
    
    cmd = [
        "ffmpeg", "-y",
        "-ss", str(start_s),
        "-i", input_path,
        "-t", str(duration),
        "-c:v", "libx264", "-preset", "fast", "-crf", "23",
        "-c:a", "aac", "-b:a", "128k",
        "-movflags", "+faststart",
    ]
    
    if filter_parts:
        if mode == "blur":
            cmd.extend(["-filter_complex", filter_parts[0]])
        else:
            cmd.extend(["-vf", ",".join(filter_parts)])
    
    cmd.append(output_path)
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"ffmpeg error: {result.stderr[-500:]}")
        sys.exit(1)
    
    print(f"Clip saved: {output_path}")

def main():
    parser = argparse.ArgumentParser(description="Cut video clips")
    parser.add_argument("--input", "-i", required=True, help="Input video")
    parser.add_argument("--start", "-s", required=True, help="Start time (MM:SS)")
    parser.add_argument("--end", "-e", required=True, help="End time (MM:SS)")
    parser.add_argument("--output", "-o", required=True, help="Output clip path")
    parser.add_argument("--vertical", action="store_true", default=True, help="Convert to 9:16")
    parser.add_argument("--no-vertical", dest="vertical", action="store_false")
    parser.add_argument("--mode", choices=["crop", "blur", "none"], default="crop",
                       help="Vertical conversion mode")
    args = parser.parse_args()
    
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    clip_video(args.input, args.start, args.end, args.output, args.vertical, args.mode)

if __name__ == "__main__":
    main()
