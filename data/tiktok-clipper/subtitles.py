#!/usr/bin/env python3
"""Add TikTok-style animated subtitles using ffmpeg ASS filter."""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

# ═══════════════════════════════════════════
# ASS SUBTITLE STYLES
# ═══════════════════════════════════════════

STYLES = {
    "bold-center": {
        "desc": "White bold, black outline, centered (classic TikTok)",
        "style": (
            "Style: Default,Arial,22,&H00FFFFFF,&H000000FF,&H00000000,&H80000000,"
            "1,0,0,0,100,100,0,0,1,3,1.5,2,10,10,35,1"
        ),
        # Bold, no italic, no underline, no strike, scaleX, scaleY, spacing, angle,
        # borderStyle(1=outline), outline(3), shadow(1.5), alignment(2=center-bottom),
        # marginL, marginR, marginV, encoding
    },
    "word-highlight": {
        "desc": "Word-by-word yellow highlight (CapCut style)",
        "style": (
            "Style: Default,Arial,22,&H00FFFFFF,&H000000FF,&H00000000,&H80000000,"
            "1,0,0,0,100,100,0,0,1,3,1.5,2,10,10,35,1\n"
            "Style: Highlight,Arial,22,&H0000FFFF,&H000000FF,&H00000000,&H80000000,"
            "1,0,0,0,100,100,0,0,1,3,1.5,2,10,10,35,1"
        ),
    },
    "karaoke": {
        "desc": "Word scales up + color change (Hormozi style)",
        "style": (
            "Style: Default,Impact,24,&H00FFFFFF,&H000000FF,&H00000000,&H80000000,"
            "1,0,0,0,100,100,0,0,1,4,2,2,10,10,35,1\n"
            "Style: Active,Impact,28,&H0000FFFF,&H000000FF,&H00000000,&H80000000,"
            "1,0,0,0,100,100,0,0,1,4,2,2,10,10,35,1"
        ),
    },
    "box": {
        "desc": "Text with colored background box (MrBeast style)",
        "style": (
            "Style: Default,Arial,20,&H00FFFFFF,&H000000FF,&H00000000,&HB4000000,"
            "1,0,0,0,100,100,0,0,3,0,12,2,15,15,35,1"
        ),
        # borderStyle=3 means box/opaque background, shadow=12 for box padding
    },
}

def format_ass_time(seconds: float) -> str:
    """Convert seconds to ASS time format H:MM:SS.cc"""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = seconds % 60
    return f"{h}:{m:02d}:{s:05.2f}"

def group_words_into_lines(words: list, max_words: int = 5, max_chars: int = 35) -> list:
    """Group words into subtitle lines (max N words or M chars per line)."""
    lines = []
    current_words = []
    current_chars = 0
    
    for w in words:
        word_text = w["word"].strip()
        if not word_text:
            continue
            
        if current_words and (len(current_words) >= max_words or current_chars + len(word_text) > max_chars):
            lines.append({
                "start": current_words[0]["start"],
                "end": current_words[-1]["end"],
                "text": " ".join(cw["word"].strip() for cw in current_words),
                "words": current_words
            })
            current_words = []
            current_chars = 0
        
        current_words.append(w)
        current_chars += len(word_text) + 1
    
    if current_words:
        lines.append({
            "start": current_words[0]["start"],
            "end": current_words[-1]["end"],
            "text": " ".join(cw["word"].strip() for cw in current_words),
            "words": current_words
        })
    
    return lines

def generate_ass_bold_center(lines: list, clip_start: float) -> str:
    """Generate simple bold centered subtitles."""
    events = []
    for line in lines:
        start = format_ass_time(line["start"] - clip_start)
        end = format_ass_time(line["end"] - clip_start)
        text = line["text"].upper()
        events.append(f"Dialogue: 0,{start},{end},Default,,0,0,0,,{text}")
    return "\n".join(events)

def generate_ass_word_highlight(lines: list, clip_start: float) -> str:
    """Generate word-by-word highlight subtitles."""
    events = []
    for line in lines:
        line_start = format_ass_time(line["start"] - clip_start)
        line_end = format_ass_time(line["end"] - clip_start)
        
        # Build text with karaoke tags for word highlighting
        tagged_text = ""
        for w in line["words"]:
            word = w["word"].strip().upper()
            w_duration = int((w["end"] - w["start"]) * 100)  # centiseconds
            tagged_text += f"{{\\kf{w_duration}}}{word} "
        
        events.append(f"Dialogue: 0,{line_start},{line_end},Default,,0,0,0,,{tagged_text.strip()}")
    return "\n".join(events)

def generate_ass_karaoke(lines: list, clip_start: float) -> str:
    """Generate Hormozi-style word emphasis subtitles."""
    events = []
    for line in lines:
        # Show full line in default style
        line_start = format_ass_time(line["start"] - clip_start)
        line_end = format_ass_time(line["end"] - clip_start)
        
        full_text = " ".join(w["word"].strip().upper() for w in line["words"])
        events.append(f"Dialogue: 0,{line_start},{line_end},Default,,0,0,0,,{full_text}")
        
        # Overlay each word with Active style when spoken
        for i, w in enumerate(line["words"]):
            word = w["word"].strip().upper()
            w_start = format_ass_time(w["start"] - clip_start)
            w_end = format_ass_time(w["end"] - clip_start)
            
            # Calculate position offset for this word
            before = " ".join(ww["word"].strip().upper() for ww in line["words"][:i])
            after_words = " ".join(ww["word"].strip().upper() for ww in line["words"][i+1:])
            
            # Use alpha tags to show only active word
            invisible = "{\\alpha&HFF&}"
            visible = "{\\alpha&H00&}"
            
            display = ""
            if before:
                display += f"{invisible}{before} "
            display += f"{visible}{word}"
            if after_words:
                display += f" {invisible}{after_words}"
            
            events.append(f"Dialogue: 1,{w_start},{w_end},Active,,0,0,0,,{display}")
    
    return "\n".join(events)

def generate_ass_box(lines: list, clip_start: float) -> str:
    """Generate MrBeast-style box subtitles."""
    events = []
    for line in lines:
        start = format_ass_time(line["start"] - clip_start)
        end = format_ass_time(line["end"] - clip_start)
        text = line["text"].upper()
        events.append(f"Dialogue: 0,{start},{end},Default,,0,0,0,,{text}")
    return "\n".join(events)

GENERATORS = {
    "bold-center": generate_ass_bold_center,
    "word-highlight": generate_ass_word_highlight,
    "karaoke": generate_ass_karaoke,
    "box": generate_ass_box,
}

def create_ass_file(transcript: dict, clip_start: float, clip_end: float,
                    style: str, output_path: str, width: int = 1080, height: int = 1920):
    """Create ASS subtitle file for a clip."""
    
    # Filter words within clip range
    words = [w for w in transcript["words"] 
             if w["start"] >= clip_start - 0.1 and w["end"] <= clip_end + 0.1]
    
    if not words:
        # Fallback to segments
        print("No word-level data, falling back to segments...")
        segments = [s for s in transcript["segments"]
                   if s["start"] >= clip_start - 0.5 and s["end"] <= clip_end + 0.5]
        # Create fake word entries from segments
        for seg in segments:
            for word in seg["text"].split():
                words.append({"start": seg["start"], "end": seg["end"], "word": word})
    
    lines = group_words_into_lines(words)
    
    style_def = STYLES[style]["style"]
    generator = GENERATORS[style]
    events = generator(lines, clip_start)
    
    ass_content = f"""[Script Info]
Title: TikTok Subtitles
ScriptType: v4.00+
WrapStyle: 0
ScaledBorderAndShadow: yes
YCbCr Matrix: None
PlayResX: {width}
PlayResY: {height}

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
{style_def}

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
{events}
"""
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(ass_content)
    
    print(f"ASS file created: {output_path} ({len(lines)} subtitle lines)")

def burn_subtitles(video_path: str, ass_path: str, output_path: str):
    """Burn ASS subtitles into video with ffmpeg."""
    # Need to escape special chars in path for ffmpeg filter
    escaped_ass = ass_path.replace("\\", "\\\\").replace(":", "\\:").replace("'", "\\'")
    
    cmd = [
        "ffmpeg", "-y",
        "-i", video_path,
        "-vf", f"ass='{escaped_ass}'",
        "-c:v", "libx264", "-preset", "fast", "-crf", "23",
        "-c:a", "copy",
        "-movflags", "+faststart",
        output_path
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        # Try without escaping
        cmd[5] = f"ass={ass_path}"
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"ffmpeg error: {result.stderr[-500:]}")
            sys.exit(1)
    
    print(f"Subtitled video: {output_path}")

def main():
    parser = argparse.ArgumentParser(description="Add TikTok-style subtitles")
    parser.add_argument("--input", "-i", required=True, help="Input video clip")
    parser.add_argument("--transcript", "-t", required=True, help="Transcript JSON file")
    parser.add_argument("--start", type=float, required=True, help="Clip start time in source (seconds)")
    parser.add_argument("--end", type=float, required=True, help="Clip end time in source (seconds)")
    parser.add_argument("--style", "-s", choices=list(STYLES.keys()), default="bold-center",
                       help="Subtitle style")
    parser.add_argument("--output", "-o", required=True, help="Output video with subtitles")
    parser.add_argument("--list-styles", action="store_true", help="List available styles")
    args = parser.parse_args()
    
    if args.list_styles:
        for name, info in STYLES.items():
            print(f"  {name}: {info['desc']}")
        return
    
    with open(args.transcript, "r", encoding="utf-8") as f:
        transcript = json.load(f)
    
    ass_path = args.output.rsplit(".", 1)[0] + ".ass"
    
    create_ass_file(transcript, args.start, args.end, args.style, ass_path)
    burn_subtitles(args.input, ass_path, args.output)

if __name__ == "__main__":
    main()
