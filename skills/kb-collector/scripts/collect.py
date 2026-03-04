#!/usr/bin/env python3
"""
KB Collector - Save YouTube, URLs, Text to Obsidian with AI Summarization
"""

import os
import sys
import subprocess
import json
from datetime import datetime
import yfinance as yf

# Configuration
VAULT_PATH = os.path.expanduser("~/Documents/Georges/Knowledge")
NOTE_AUTHOR = "George"

def get_video_title(url):
    """Get YouTube video title"""
    try:
        result = subprocess.run(
            ['yt-dlp', '--get-title', url],
            capture_output=True, text=True, timeout=30
        )
        title = result.stdout.strip()
        # Clean filename
        title = ''.join(c for c in title if c.isalnum() or c in ' -_').strip()[:50]
        return title
    except:
        return f"Video-{datetime.now().strftime('%H%M%S')}"

def download_youtube_audio(url):
    """Download YouTube audio"""
    output = "/tmp/youtube_audio"
    subprocess.run(
        ['yt-dlp', '-f', 'bestaudio[ext=m4a]', '--extract-audio', 
         '--audio-format', 'm4a', '-o', f'{output}.%(ext)s', url],
        capture_output=True, timeout=120
    )
    return f"{output}.m4a"

def transcribe_audio(audio_path):
    """Transcribe audio with Whisper"""
    # Use faster-whisper if available
    try:
        from faster_whisper import WhisperModel
        model = WhisperModel("tiny", device="cpu", compute_type="int8")
        segments, info = model.transcribe(audio_path, language="zh")
        transcript = " ".join([seg.text for seg in segments])
        return transcript
    except:
        # Fallback to shell whisper
        result = subprocess.run(
            ['whisper', audio_path, '--model', 'tiny', '--output_format', 'txt', 
             '--output_dir', '/tmp', '--language', 'Chinese'],
            capture_output=True, timeout=300
        )
        txt_path = audio_path.replace('.m4a', '.txt')
        if os.path.exists(txt_path):
            with open(txt_path, 'r', encoding='utf-8') as f:
                return f.read()
    return None

def summarize_text(text, max_length=500):
    """AI Summarize text using MiniMax (if available) or return first N chars"""
    # For now, return first 500 chars as preview
    # In production, could integrate with LLM
    if len(text) > max_length:
        return text[:max_length] + "..."
    return text

def fetch_url(url):
    """Fetch URL content"""
    try:
        import requests
        from bs4 import BeautifulSoup
        
        headers = {'User-Agent': 'Mozilla/5.0'}
        r = requests.get(url, headers=headers, timeout=30)
        soup = BeautifulSoup(r.text, 'html.parser')
        
        # Remove scripts and styles
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Get text
        text = soup.get_text(separator='\n', strip=True)
        # Clean up
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        return '\n'.join(lines[:100])  # First 100 lines
    except Exception as e:
        return f"Error fetching: {e}"

def save_to_obsidian(content, title, url, tags, tldr=None):
    """Save note to Obsidian vault"""
    date = datetime.now().strftime('%Y-%m-%d')
    filename = f"{date}-{title}.md"
    filepath = os.path.join(VAULT_PATH, filename)
    
    # Ensure vault exists
    os.makedirs(VAULT_PATH, exist_ok=True)
    
    # Build frontmatter
    frontmatter = f"""---
created: {datetime.now().strftime('%Y-%m-%dT%H:%M:%S')}
source: {url or 'N/A'}
tags: [{tags}]
author: {NOTE_AUTHOR}
---

# {title}

> **TLDR:** {tldr or 'Summary pending...'}
"""

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(frontmatter)
        f.write("\n---\n\n")
        f.write(content)
        f.write(f"\n\n---\n*Saved: {datetime.now().strftime('%Y-%m-%d')}*\n")
    
    return filepath

def main():
    if len(sys.argv) < 3:
        print("Usage:")
        print("  collect.py youtube <url> <tags>")
        print("  collect.py url <url> <tags>")
        print("  collect.py text <content> <tags>")
        sys.exit(1)
    
    cmd = sys.argv[1].lower()
    content = sys.argv[2]
    tags = sys.argv[3] if len(sys.argv) > 3 else "untagged"
    
    date = datetime.now().strftime('%Y-%m-%d')
    
    if cmd == "youtube":
        print("=== YouTube Mode ===")
        url = content
        title = get_video_title(url)
        
        print(f"Title: {title}")
        print("Downloading audio...")
        audio_path = download_youtube_audio(url)
        
        print("Transcribing...")
        transcript = transcribe_audio(audio_path)
        
        if transcript:
            print("Summarizing...")
            summary = summarize_text(transcript)
            filepath = save_to_obsidian(transcript, title, url, tags, tldr=summary[:200])
            print(f"✅ Saved to: {filepath}")
        else:
            print("❌ Transcription failed")
        
        # Cleanup
        if os.path.exists(audio_path):
            os.remove(audio_path)
    
    elif cmd == "url":
        print("=== URL Mode ===")
        url = content
        title = url.split('/')[-1][:50] or "web-note"
        
        print(f"Fetching {url}...")
        text = fetch_url(url)
        
        summary = summarize_text(text)
        filepath = save_to_obsidian(text, title, url, tags, tldr=summary[:200])
        print(f"✅ Saved to: {filepath}")
    
    elif cmd == "text":
        print("=== Text Mode ===")
        text = content
        title = f"Note-{datetime.now().strftime('%H%M%S')}"
        
        filepath = save_to_obsidian(text, title, "", tags)
        print(f"✅ Saved to: {filepath}")
    
    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)

if __name__ == "__main__":
    main()
