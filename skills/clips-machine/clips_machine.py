#!/usr/bin/env python3
"""
Clips Machine - Transform long videos into viral short-form clips
100% Free tools - Whisper + FFmpeg (self-contained, no external modules)

Usage:
    python clips_machine.py "https://youtube.com/watch?v=VIDEO_ID"
    python clips_machine.py /path/to/video.mp4 --clips 10
    python clips_machine.py VIDEO --style hormozi

Homepage: https://github.com/Mayank8290/openclaw-video-skills
"""

import os
import json
import argparse
import tempfile
import subprocess
import re
from pathlib import Path
from datetime import datetime
from typing import List, Dict
from urllib.parse import urlparse

# =============================================================================
# CONFIGURATION
# =============================================================================

OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", "~/Videos/OpenClaw")).expanduser()
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_DOMAINS = [
    "youtube.com", "youtu.be", "www.youtube.com", "m.youtube.com",
    "tiktok.com", "www.tiktok.com",
    "twitter.com", "x.com",
    "twitch.tv", "www.twitch.tv",
    "instagram.com", "www.instagram.com",
]


# =============================================================================
# SECURITY UTILITIES
# =============================================================================

def secure_tempfile(suffix: str = "") -> str:
    """Create a secure temporary file (no race condition)"""
    fd, path = tempfile.mkstemp(suffix=suffix)
    os.close(fd)
    return path


def validate_url(url: str) -> bool:
    """Validate URL is from allowed domains (prevents SSRF)"""
    try:
        parsed = urlparse(url)
        if parsed.scheme not in ("http", "https"):
            return False
        return any(
            parsed.netloc == d or parsed.netloc.endswith("." + d)
            for d in ALLOWED_DOMAINS
        )
    except Exception:
        return False


# =============================================================================
# VIDEO UTILITIES (inlined - no external dependencies)
# =============================================================================

def get_video_duration(video_path: str) -> float:
    """Get video duration in seconds"""
    result = subprocess.run([
        "ffprobe", "-v", "quiet",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        video_path
    ], capture_output=True, text=True)
    return float(result.stdout.strip() or "0")


def download_video(url: str, output_path: str) -> str:
    """Download video from YouTube, TikTok, Twitter, etc."""
    if not validate_url(url):
        raise ValueError(f"URL not from allowed domain: {url}")

    cmd = [
        "yt-dlp",
        "--no-exec",
        "--no-playlist",
        "-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
        "-o", output_path,
        url
    ]
    subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    return output_path


def transcribe_with_timestamps(video_path: str) -> List[Dict]:
    """Extract audio and transcribe with Whisper.cpp"""
    audio_path = secure_tempfile(suffix=".wav")
    subprocess.run([
        "ffmpeg", "-y", "-i", video_path,
        "-ar", "16000", "-ac", "1", "-c:a", "pcm_s16le",
        audio_path
    ], capture_output=True)

    output_base = secure_tempfile(suffix="")

    # Find whisper binary
    whisper_cmd = "whisper-cpp"
    whisper_model = "/usr/local/share/whisper-cpp/models/ggml-base.en.bin"

    if subprocess.run(["which", whisper_cmd], capture_output=True).returncode != 0:
        whisper_cpp_dir = Path.home() / ".whisper-cpp"
        whisper_cmd = str(whisper_cpp_dir / "main")
        whisper_model = str(whisper_cpp_dir / "models" / "ggml-base.en.bin")

    subprocess.run([
        whisper_cmd, "-m", whisper_model,
        "-f", audio_path, "-oj", "-of", output_base
    ], capture_output=True)

    # Clean up audio
    try:
        os.unlink(audio_path)
    except OSError:
        pass

    # Parse results
    json_path = output_base + ".json"
    if os.path.exists(json_path):
        with open(json_path) as f:
            data = json.load(f)
        try:
            os.unlink(json_path)
        except OSError:
            pass
        return data.get("segments", [])

    return []


def cut_video(input_path: str, output_path: str, start: float, end: float) -> str:
    """Cut a segment from a video"""
    subprocess.run([
        "ffmpeg", "-y",
        "-ss", str(start),
        "-i", input_path,
        "-t", str(end - start),
        "-c:v", "libx264", "-c:a", "aac",
        output_path
    ], capture_output=True)
    return output_path


def crop_to_vertical(input_path: str, output_path: str) -> str:
    """Crop horizontal video to vertical 9:16 (center crop)"""
    subprocess.run([
        "ffmpeg", "-y",
        "-i", input_path,
        "-vf", "crop=ih*9/16:ih",
        "-c:v", "libx264", "-c:a", "aac",
        output_path
    ], capture_output=True)
    return output_path


# =============================================================================
# VIRAL MOMENT DETECTION
# =============================================================================

VIRAL_DETECTION_PROMPT = """Analyze this transcript and find the most viral-worthy moments for short-form video clips (TikTok, YouTube Shorts, Reels).

TRANSCRIPT:
{transcript}

Find moments that have:
1. HOOK POTENTIAL - Strong opening that grabs attention in first 3 seconds
2. EMOTIONAL PEAKS - Passion, excitement, surprise, humor
3. QUOTABLE LINES - Memorable statements people would share
4. CONTROVERSIAL TAKES - Opinions that spark debate
5. SURPRISING FACTS - "I didn't know that" moments
6. STORY CLIMAXES - Resolution of tension or conflict
7. ACTIONABLE ADVICE - Clear, specific takeaways

For each moment, return JSON:
[{{"start_time": 125.5, "end_time": 172.3, "score": 95, "hook": "First 10 words...", "reason": "Why it's viral"}}]

Return the top {num_clips} moments."""


def detect_viral_moments(
    transcript: List[Dict],
    num_clips: int = 5,
    min_score: int = 50
) -> List[Dict]:
    """
    Analyze transcript to find viral-worthy moments.
    Uses pattern matching + heuristics in standalone mode.
    In OpenClaw, the LLM handles smarter detection.
    """
    moments = []

    full_text = ""
    for seg in transcript:
        start = seg.get("start", 0)
        text = seg.get("text", "")
        full_text += f"[{start:.1f}s] {text}\n"

    viral_patterns = [
        (r"here'?s the thing|the truth is|nobody tells you|secret is|what if i told you", 30),
        (r"i'm going to (show|tell|reveal|share)", 25),
        (r"the (biggest|number one|most important|real) (mistake|problem|issue|secret)", 28),
        (r"(have you ever|did you know|what if|why do|how (do|can|does))[^.?]*\?", 20),
        (r"(absolutely|literally|honestly|seriously|actually) (insane|crazy|wild|incredible|unbelievable)", 25),
        (r"this (changed|blew|shocked|surprised) (my|everything)", 22),
        (r"i (couldn'?t believe|was shocked|never expected)", 20),
        (r"(everyone|most people|nobody) (is wrong|gets this wrong|misses this)", 28),
        (r"(stop|don'?t|never|always) (doing|saying|believing)", 22),
        (r"(controversial|unpopular) (opinion|take|thought)", 30),
        (r"(and then|suddenly|that'?s when|at that moment)", 15),
        (r"(the turning point|everything changed|that'?s when i realized)", 25),
        (r"(step (one|two|three|1|2|3)|first thing|here'?s (how|what))", 20),
        (r"(you (need to|should|must|have to)|the key is|the trick is)", 18),
        (r"(three|four|five|3|4|5|10) (things|ways|tips|secrets|mistakes|reasons)", 22),
    ]

    text_lower = full_text.lower()

    for pattern, base_score in viral_patterns:
        for match in re.finditer(pattern, text_lower):
            match_pos = match.start()
            lines_before = text_lower[:match_pos].count('\n')

            if lines_before < len(transcript):
                seg = transcript[lines_before]
                start_time = seg.get("start", 0)
                end_time = start_time + 45

                hook_text = match.group(0)[:50]
                position_bonus = max(0, 10 - (lines_before / max(len(transcript), 1)) * 10)

                moments.append({
                    "start_time": max(0, start_time - 2),
                    "end_time": end_time,
                    "score": min(100, base_score + position_bonus + 20),
                    "hook": hook_text.strip(),
                    "reason": f"Matched pattern: {pattern[:30]}...",
                })

    # Deduplicate overlapping clips
    filtered = []
    for moment in sorted(moments, key=lambda x: x["score"], reverse=True):
        overlaps = any(
            moment["start_time"] < ex["end_time"] and moment["end_time"] > ex["start_time"]
            for ex in filtered
        )
        if not overlaps and moment["score"] >= min_score:
            filtered.append(moment)
        if len(filtered) >= num_clips:
            break

    # Fill with evenly spaced clips if not enough
    if len(filtered) < num_clips and transcript:
        total_duration = transcript[-1].get("end", 60)
        interval = total_duration / (num_clips + 1)
        for i in range(num_clips - len(filtered)):
            start = interval * (i + 1)
            filtered.append({
                "start_time": start,
                "end_time": min(start + 45, total_duration),
                "score": 40,
                "hook": f"Segment at {start:.0f}s",
                "reason": "Evenly distributed segment",
            })

    return filtered[:num_clips]


# =============================================================================
# CAPTION STYLES
# =============================================================================

CAPTION_STYLES = {
    "hormozi": {
        "fontname": "Arial Black", "fontsize": 60,
        "primary": "&H00FFFFFF", "highlight": "&H0000FFFF",
        "outline": "&H00000000", "outline_width": 4,
        "shadow": 3, "alignment": 2, "marginv": 100,
    },
    "minimal": {
        "fontname": "Helvetica Neue", "fontsize": 48,
        "primary": "&H00FFFFFF", "outline": "&H40000000",
        "outline_width": 2, "shadow": 0, "alignment": 2, "marginv": 80,
    },
    "karaoke": {
        "fontname": "Arial Black", "fontsize": 54,
        "primary": "&H00FFFFFF", "highlight": "&H0000FF00",
        "outline": "&H00000000", "outline_width": 3,
        "shadow": 2, "alignment": 2, "marginv": 90,
    },
    "news": {
        "fontname": "Arial", "fontsize": 42,
        "primary": "&H00FFFFFF", "outline": "&H00000000",
        "outline_width": 0, "shadow": 0, "alignment": 1, "marginv": 50,
    },
    "meme": {
        "fontname": "Impact", "fontsize": 70,
        "primary": "&H00FFFFFF", "outline": "&H00000000",
        "outline_width": 5, "shadow": 0, "alignment": 2, "marginv": 30,
        "all_caps": True,
    },
}


def format_ass_time(seconds: float) -> str:
    """Convert seconds to ASS timestamp (H:MM:SS.cc)"""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    c = int((seconds % 1) * 100)
    return f"{h}:{m:02d}:{s:02d}.{c:02d}"


def create_styled_captions(
    video_path: str, output_path: str,
    segments: List[Dict], style: str = "hormozi"
) -> str:
    """Burn animated captions into video"""
    sc = CAPTION_STYLES.get(style, CAPTION_STYLES["hormozi"])

    ass_file = secure_tempfile(suffix=".ass")

    header = f"""[Script Info]
Title: Clips Machine Captions
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,{sc['fontname']},{sc['fontsize']},{sc['primary']},{sc.get('highlight', sc['primary'])},{sc['outline']},&H80000000,1,0,0,0,100,100,0,0,1,{sc['outline_width']},{sc.get('shadow', 2)},{sc['alignment']},10,10,{sc['marginv']},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

    events = ""
    for seg in segments:
        start = format_ass_time(seg.get("start", 0))
        end = format_ass_time(seg.get("end", 0))
        text = seg.get("text", "")
        if sc.get("all_caps"):
            text = text.upper()
        # Sanitize ASS text
        text = text.replace("{", "\\{").replace("}", "\\}")
        text = text.replace("\n", "\\N")
        text = re.sub(r'[\x00-\x1f\x7f]', '', text)
        events += f"Dialogue: 0,{start},{end},Default,,0,0,0,,{text}\n"

    with open(ass_file, "w") as f:
        f.write(header + events)

    subprocess.run([
        "ffmpeg", "-y", "-i", video_path,
        "-vf", f"ass={ass_file}",
        "-c:v", "libx264", "-preset", "fast", "-c:a", "aac",
        output_path
    ], capture_output=True)

    try:
        os.unlink(ass_file)
    except OSError:
        pass
    return output_path


# =============================================================================
# MAIN PROCESSING
# =============================================================================

def process_video(
    source: str, num_clips: int = 5, style: str = "hormozi",
    no_captions: bool = False, start_time: float = None,
    end_time: float = None, min_score: int = 50, output_name: str = None
) -> Dict:
    """Process a video into viral clips"""
    print(f"\nClips Machine: Processing video")
    print("=" * 60)

    if output_name is None:
        if source.startswith("http"):
            output_name = f"clips-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        else:
            output_name = f"clips-{Path(source).stem}"

    output_dir = OUTPUT_DIR / output_name
    output_dir.mkdir(parents=True, exist_ok=True)
    results = {"directory": str(output_dir), "clips": []}

    # Step 1: Download/Load
    print("\nStep 1/5: Loading video...")
    if source.startswith("http"):
        print(f"   Downloading from: {source[:50]}...")
        video_path = str(output_dir / "source.mp4")
        download_video(source, video_path)
    else:
        video_path = source

    if not os.path.exists(video_path):
        print(f"   Video not found: {video_path}")
        return results

    duration = get_video_duration(video_path)
    print(f"   Done - Video loaded ({duration:.1f}s)")
    results["source"] = video_path
    results["duration"] = duration

    # Step 2: Transcribe
    print("\nStep 2/5: Transcribing audio...")
    transcript = transcribe_with_timestamps(video_path)
    transcript_path = output_dir / "transcript.json"
    with open(transcript_path, "w") as f:
        json.dump(transcript, f, indent=2)
    results["transcript"] = str(transcript_path)
    print(f"   Done - Transcribed {len(transcript)} segments")

    # Step 3: Detect Viral Moments
    print("\nStep 3/5: Detecting viral moments...")
    if start_time or end_time:
        transcript = [
            s for s in transcript
            if (start_time is None or s.get("start", 0) >= start_time)
            and (end_time is None or s.get("end", 0) <= end_time)
        ]

    moments = detect_viral_moments(transcript, num_clips=num_clips, min_score=min_score)
    moments_path = output_dir / "viral_moments.json"
    with open(moments_path, "w") as f:
        json.dump(moments, f, indent=2)
    results["viral_moments"] = str(moments_path)
    print(f"   Done - Found {len(moments)} viral moments")
    for i, m in enumerate(moments):
        print(f"      {i+1}. [score:{m['score']}] {m['hook'][:40]}...")

    # Step 4: Cut Clips
    print("\nStep 4/5: Cutting clips...")
    clip_paths = []
    for i, moment in enumerate(moments):
        clip_path = str(output_dir / f"clip_{i+1:03d}.mp4")
        temp_clip = str(output_dir / f"temp_{i}.mp4")

        cut_video(video_path, temp_clip, moment["start_time"], moment["end_time"])
        vertical_clip = str(output_dir / f"vertical_{i}.mp4")
        crop_to_vertical(temp_clip, vertical_clip)

        clip_paths.append({"path": vertical_clip, "moment": moment, "final_path": clip_path})
        print(f"   Done - Cut clip {i+1}/{len(moments)}")

        if os.path.exists(temp_clip):
            os.unlink(temp_clip)

    # Step 5: Add Captions
    if not no_captions:
        print(f"\nStep 5/5: Adding {style} captions...")
        for i, clip_info in enumerate(clip_paths):
            moment = clip_info["moment"]
            clip_segments = [
                {
                    "start": max(0, s.get("start", 0) - moment["start_time"]),
                    "end": s.get("end", 0) - moment["start_time"],
                    "text": s.get("text", ""),
                }
                for s in transcript
                if s.get("start", 0) < moment["end_time"]
                and s.get("end", 0) > moment["start_time"]
            ]

            create_styled_captions(clip_info["path"], clip_info["final_path"], clip_segments, style=style)
            results["clips"].append(clip_info["final_path"])
            print(f"   Done - Captioned clip {i+1}/{len(clip_paths)}")

            if os.path.exists(clip_info["path"]):
                os.unlink(clip_info["path"])
    else:
        print("\nStep 5/5: Skipping captions...")
        for clip_info in clip_paths:
            os.rename(clip_info["path"], clip_info["final_path"])
            results["clips"].append(clip_info["final_path"])

    # Summary
    summary = f"# Clips Machine Output\n\nSource: {source}\nDuration: {duration:.1f}s\nClips: {len(results['clips'])}\nStyle: {style}\n\n"
    for i, moment in enumerate(moments):
        summary += f"### Clip {i+1} (Score: {moment['score']})\n"
        summary += f"- Time: {moment['start_time']:.1f}s - {moment['end_time']:.1f}s\n"
        summary += f"- Hook: {moment['hook']}\n- File: clip_{i+1:03d}.mp4\n\n"

    with open(output_dir / "summary.md", "w") as f:
        f.write(summary)
    results["summary"] = str(output_dir / "summary.md")

    print("\n" + "=" * 60)
    print("CLIPS GENERATION COMPLETE!")
    print("=" * 60)
    print(f"\nOutput folder: {output_dir}")
    for clip in results["clips"]:
        print(f"   - {Path(clip).name}")
    print(f"\nReady to upload to TikTok, Reels, and Shorts!")
    return results


# =============================================================================
# CLI
# =============================================================================

def parse_timestamp(ts: str) -> float:
    """Parse MM:SS or HH:MM:SS to seconds"""
    parts = ts.split(":")
    if len(parts) == 2:
        return int(parts[0]) * 60 + float(parts[1])
    elif len(parts) == 3:
        return int(parts[0]) * 3600 + int(parts[1]) * 60 + float(parts[2])
    return float(ts)


def main():
    parser = argparse.ArgumentParser(description="Clips Machine - Turn long videos into viral clips")
    parser.add_argument("source", help="YouTube URL or local video path")
    parser.add_argument("--clips", type=int, default=5, help="Number of clips to generate")
    parser.add_argument("--style", default="hormozi",
                        choices=["hormozi", "minimal", "karaoke", "news", "meme"],
                        help="Caption style")
    parser.add_argument("--no-captions", action="store_true", help="Skip caption generation")
    parser.add_argument("--start", type=str, help="Start timestamp (MM:SS)")
    parser.add_argument("--end", type=str, help="End timestamp (MM:SS)")
    parser.add_argument("--min-score", type=int, default=50, help="Minimum virality score")
    parser.add_argument("--output", help="Custom output folder name")
    args = parser.parse_args()

    process_video(
        source=args.source,
        num_clips=args.clips,
        style=args.style,
        no_captions=args.no_captions,
        start_time=parse_timestamp(args.start) if args.start else None,
        end_time=parse_timestamp(args.end) if args.end else None,
        min_score=args.min_score,
        output_name=args.output,
    )


if __name__ == "__main__":
    main()
