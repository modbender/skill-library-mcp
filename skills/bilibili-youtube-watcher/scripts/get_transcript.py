#!/usr/bin/env python3
"""
Video Watcher - Universal transcript fetcher for YouTube and Bilibili
Supports: YouTube (youtube.com, youtu.be) and Bilibili (bilibili.com, b23.tv)
"""
import argparse
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from urllib.parse import urlparse

def detect_platform(url: str) -> str:
    """Detect video platform from URL."""
    domain = urlparse(url).netloc.lower()
    
    if any(d in domain for d in ['youtube.com', 'youtu.be', 'youtube-nocookie.com']):
        return 'youtube'
    elif any(d in domain for d in ['bilibili.com', 'b23.tv']):
        return 'bilibili'
    else:
        return 'unknown'

def clean_vtt(content: str) -> str:
    """
    Clean WebVTT content to plain text.
    Removes headers, timestamps, and duplicate lines.
    """
    lines = content.splitlines()
    text_lines = []
    seen = set()
    
    timestamp_pattern = re.compile(r'\d{2}:\d{2}:\d{2}\.\d{3}\s-->\s\d{2}:\d{2}:\d{2}\.\d{3}')
    
    for line in lines:
        line = line.strip()
        if not line or line == 'WEBVTT' or line.isdigit():
            continue
        if timestamp_pattern.match(line):
            continue
        if line.startswith('NOTE') or line.startswith('STYLE'):
            continue
            
        if text_lines and text_lines[-1] == line:
            continue
            
        line = re.sub(r'<[^>]+>', '', line)
        
        text_lines.append(line)
        
    return '\n'.join(text_lines)

def clean_srt(content: str) -> str:
    """
    Clean SRT content to plain text.
    Removes sequence numbers and timestamps.
    """
    lines = content.splitlines()
    text_lines = []
    
    timestamp_pattern = re.compile(r'\d{2}:\d{2}:\d{2},\d{3}\s-->\s\d{2}:\d{2}:\d{2},\d{3}')
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if line.isdigit():
            continue
        if timestamp_pattern.match(line):
            continue
        if text_lines and text_lines[-1] == line:
            continue
            
        line = re.sub(r'<[^>]+>', '', line)
        text_lines.append(line)
        
    return '\n'.join(text_lines)

def get_transcript(url: str, language: str = None):
    platform = detect_platform(url)
    
    if platform == 'unknown':
        print(f"Error: Unsupported URL format. Please use YouTube or Bilibili URLs.", file=sys.stderr)
        sys.exit(1)
    
    # Set default language based on platform
    if language is None:
        language = 'zh-CN' if platform == 'bilibili' else 'en'
    
    with tempfile.TemporaryDirectory() as temp_dir:
        cmd = [
            "yt-dlp",
            "--write-subs",
            "--write-auto-subs",
            "--skip-download",
            "--sub-lang", language,
            "--output", "subs",
        ]
        
        # Add Bilibili-specific headers to bypass anti-scraping
        if platform == 'bilibili':
            cmd.extend([
                "--add-header", "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "--add-header", "Referer: https://www.bilibili.com/",
            ])
        
        cmd.append(url)
        
        try:
            result = subprocess.run(cmd, cwd=temp_dir, check=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr.decode()
            if "unavailable" in error_msg.lower() or "not available" in error_msg.lower():
                print(f"Error: Video not available or region-restricted.", file=sys.stderr)
            elif "no subtitles" in error_msg.lower():
                print(f"Error: No subtitles available for this video.", file=sys.stderr)
            else:
                print(f"Error running yt-dlp: {error_msg}", file=sys.stderr)
            sys.exit(1)
        except FileNotFoundError:
            print("Error: yt-dlp not found. Please install it:\n  pip install yt-dlp\n  or: brew install yt-dlp", file=sys.stderr)
            sys.exit(1)

        temp_path = Path(temp_dir)
        
        # Try VTT first, then SRT
        subtitle_files = list(temp_path.glob("*.vtt")) + list(temp_path.glob("*.srt"))
        
        if not subtitle_files:
            print("Error: No subtitles found. The video may not have subtitles available.", file=sys.stderr)
            sys.exit(1)
            
        subtitle_file = subtitle_files[0]
        content = subtitle_file.read_text(encoding='utf-8')
        
        # Use appropriate cleaner based on file extension
        if subtitle_file.suffix.lower() == '.vtt':
            clean_text = clean_vtt(content)
        else:
            clean_text = clean_srt(content)
        
        # Add metadata header
        print(f"# Platform: {platform.title()}")
        print(f"# Language: {language}")
        print(f"# URL: {url}")
        print()
        print(clean_text)

def main():
    parser = argparse.ArgumentParser(
        description="Fetch video transcripts from YouTube or Bilibili."
    )
    parser.add_argument("url", help="Video URL (YouTube or Bilibili)")
    parser.add_argument(
        "--lang", "-l",
        help="Subtitle language code (default: zh-CN for Bilibili, en for YouTube)",
        default=None
    )
    args = parser.parse_args()
    
    get_transcript(args.url, args.lang)

if __name__ == "__main__":
    main()
