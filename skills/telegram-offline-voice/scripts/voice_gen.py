#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "edge-tts",
#     "aiofiles",
# ]
# ///

import asyncio
import edge_tts
import re
import os
import subprocess
import uuid
import argparse
import sys
from pathlib import Path

def clean_text(text):
    # Remove Markdown symbols
    text = re.sub(r'\*\*|\*|__|_|`|#+\s+|\[.*?\]\(.*?\)', '', text)
    # Remove URLs
    text = re.sub(r'https?://\S+', '', text)
    # Remove common technical symbols/headers
    text = re.sub(r'---|\*\*\*|>>>', ' ', text)
    # Collapse multiple spaces/newlines
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def split_text(text, max_chars=300):
    """Splits text into chunks by punctuation."""
    if len(text) <= max_chars:
        return [text]
    
    # Split by common sentence enders
    parts = re.split(r'([。！？；.!?;])', text)
    chunks = []
    current_chunk = ""
    
    for i in range(0, len(parts)-1, 2):
        sentence = parts[i] + parts[i+1]
        if len(current_chunk) + len(sentence) <= max_chars:
            current_chunk += sentence
        else:
            if current_chunk:
                chunks.append(current_chunk)
            current_chunk = sentence
            
    if current_chunk:
        chunks.append(current_chunk)
    
    # Handle the last part if it doesn't end with punctuation
    if len(parts) % 2 != 0 and parts[-1]:
        if chunks and len(chunks[-1]) + len(parts[-1]) <= max_chars:
            chunks[-1] += parts[-1]
        else:
            chunks.append(parts[-1])
            
    return chunks

async def generate_voice(text, voice, rate, output_path):
    communicate = edge_tts.Communicate(text, voice, rate=rate)
    await communicate.save(output_path)

def convert_to_ogg(input_path, output_path):
    cmd = [
        "ffmpeg", "-y", "-i", str(input_path),
        "-c:a", "libopus", "-b:a", "48k",
        "-ac", "1", "-ar", "48000",
        "-application", "voip", str(output_path)
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

async def main():
    parser = argparse.ArgumentParser(description="Smart Voice Generator for Telegram")
    parser.add_argument("--text", "-t", required=True, help="Text to convert")
    parser.add_argument("--voice", default="zh-CN-XiaoxiaoNeural", help="Voice to use")
    parser.add_argument("--rate", default="+5%", help="Speed rate")
    parser.add_argument("--outdir", default="/tmp", help="Output directory")
    
    args = parser.parse_args()
    
    cleaned = clean_text(args.text)
    if not cleaned:
        print("Error: No text left after cleaning.", file=sys.stderr)
        sys.exit(1)
        
    chunks = split_text(cleaned)
    output_files = []
    
    for chunk in chunks:
        session_id = str(uuid.uuid4())
        raw_mp3 = Path(args.outdir) / f"{session_id}.mp3"
        final_ogg = Path(args.outdir) / f"{session_id}.ogg"
        
        try:
            await generate_voice(chunk, args.voice, args.rate, raw_mp3)
            convert_to_ogg(raw_mp3, final_ogg)
            output_files.append(str(final_ogg))
        finally:
            if raw_mp3.exists():
                os.remove(raw_mp3)
                
    # Print results for OpenClaw to pick up
    for f in output_files:
        print(f"MEDIA: {f}")

if __name__ == "__main__":
    asyncio.run(main())
