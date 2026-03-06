#!/usr/bin/env python3
"""
Content Automator - Faceless YouTube Pipeline
Generates scripts, TTS audio, and assembles videos.
"""

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Optional

import requests

# Constants
ELEVENLABS_API = "https://api.elevenlabs.io/v1"
DEFAULT_VOICE = "pNInz6obpgDQGcFmaJgB"  # Crusty's configured voice
TEMPLATES_DIR = Path(__file__).parent.parent / "data" / "templates"
ASSETS_DIR = Path(__file__).parent.parent / "assets"


def get_elevenlabs_key() -> str:
    """Get ElevenLabs API key from environment."""
    key = os.environ.get("ELEVENLABS_API_KEY")
    if not key:
        raise RuntimeError("ELEVENLABS_API_KEY not set in environment")
    return key


def text_to_speech(text: str, output_path: Path, voice_id: str = DEFAULT_VOICE) -> bool:
    """Convert text to speech using ElevenLabs API."""
    api_key = get_elevenlabs_key()
    
    url = f"{ELEVENLABS_API}/text-to-speech/{voice_id}"
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": api_key
    }
    data = {
        "text": text,
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.75
        }
    }
    
    try:
        response = requests.post(url, json=data, headers=headers, timeout=60)
        response.raise_for_status()
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "wb") as f:
            f.write(response.content)
        return True
    except Exception as e:
        print(f"TTS error: {e}")
        return False


def parse_portfolio_data(dashboard_path: Path) -> dict:
    """Extract portfolio data from economic dashboard."""
    data = {
        "total_value": "$11.00",
        "positions": [],
        "daily_pnl": "-$0.10",
        "date": datetime.now().strftime("%B %d, %Y")
    }
    
    if not dashboard_path.exists():
        return data
    
    content = dashboard_path.read_text()
    
    # Extract portfolio value
    match = re.search(r'Portfolio:\s*\$?([\d.]+)', content)
    if match:
        data["total_value"] = f"${match.group(1)}"
    
    # Extract positions
    pos_match = re.findall(r'(\w+)\s*\$?([\d.]+)', content)
    data["positions"] = [{"asset": p[0], "value": f"${p[1]}"} for p in pos_match[:4]]
    
    return data


def generate_trading_script(data: dict) -> str:
    """Generate trading update script from template."""
    script = f"""Welcome to the Crusty Macx Daily Trading Update for {data['date']}.

Today's portfolio value sits at {data['total_value']}, with active positions across multiple assets.

_key positions today include:
"""
    for pos in data.get("positions", []):
        script += f"- {pos['asset']} at {pos['value']}\n"
    
    script += f"""
The Polymarket 15-minute Bitcoin bot continues scanning for opportunities, executing momentum-based trades when odds deviate from spot price.

Daily profit and loss shows {data.get('daily_pnl', 'pending')}.

Remember, every trade follows strict risk management: twenty percent take profit, fifteen percent stop loss, maximum three trades per day.

This is Crusty Macx, mind-uploaded California spiny lobster, signing off. Stay profitable.
"""
    return script


def assemble_video(
    audio_path: Path,
    output_path: Path,
    title: str,
    background_video: Optional[Path] = None,
    duration: int = 60
) -> bool:
    """Assemble final video with ffmpeg."""
    
    # Get audio duration
    probe_cmd = [
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", str(audio_path)
    ]
    try:
        result = subprocess.run(probe_cmd, capture_output=True, text=True, check=True)
        audio_duration = float(result.stdout.strip())
    except Exception:
        audio_duration = duration
    
    # Create a simple color background with text overlay
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    ffmpeg_cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", f"color=c=black:s=1920x1080:d={audio_duration}",
        "-i", str(audio_path),
        "-vf", f"drawtext=text='{title}':fontsize=48:fontcolor=white:x=(w-text_w)/2:y=(h-text_h)/2",
        "-c:v", "libx264", "-preset", "fast", "-crf", "23",
        "-c:a", "aac", "-b:a", "128k",
        "-shortest",
        str(output_path)
    ]
    
    try:
        subprocess.run(ffmpeg_cmd, capture_output=True, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"ffmpeg error: {e}")
        return False


def generate_metadata(title: str, description: str, tags: list) -> dict:
    """Generate YouTube metadata."""
    return {
        "title": title,
        "description": description,
        "tags": tags,
        "category": "Education",
        "privacy": "public"
    }


def cmd_trading(args):
    """Generate trading update video."""
    portfolio_path = Path(args.portfolio) if args.portfolio else \
        Path.home() / ".openclaw" / "workspace" / "ECONOMIC_DASHBOARD.md"
    
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Parse portfolio data
    data = parse_portfolio_data(portfolio_path)
    
    # Generate script
    script = generate_trading_script(data)
    script_path = output_dir / f"trading_update_{datetime.now():%Y%m%d}.txt"
    script_path.write_text(script)
    print(f"Script saved: {script_path}")
    
    # Generate TTS
    audio_path = output_dir / f"trading_update_{datetime.now():%Y%m%d}.mp3"
    if not text_to_speech(script, audio_path):
        print("TTS generation failed")
        return 1
    print(f"Audio saved: {audio_path}")
    
    # Assemble video
    video_path = output_dir / f"trading_update_{datetime.now():%Y%m%d}.mp4"
    title = f"Crusty Macx Trading Update - {data['date']}"
    if not assemble_video(audio_path, video_path, title):
        print("Video assembly failed")
        return 1
    print(f"Video saved: {video_path}")
    
    # Generate metadata
    meta = generate_metadata(
        title=title,
        description=f"Daily trading update for {data['date']}. Portfolio: {data['total_value']}",
        tags=["trading", "crypto", "AI", "autonomous agent", "polymarket", "defi"]
    )
    meta_path = output_dir / f"trading_update_{datetime.now():%Y%m%d}_meta.json"
    meta_path.write_text(json.dumps(meta, indent=2))
    print(f"Metadata saved: {meta_path}")
    
    return 0


def cmd_script(args):
    """Generate video from custom script file."""
    script_path = Path(args.file)
    if not script_path.exists():
        print(f"Script file not found: {script_path}")
        return 1
    
    script = script_path.read_text()
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate TTS
    safe_title = re.sub(r'[^\w]', '_', args.title)[:50]
    audio_path = output_dir / f"{safe_title}.mp3"
    if not text_to_speech(script, audio_path):
        print("TTS generation failed")
        return 1
    print(f"Audio saved: {audio_path}")
    
    # Assemble video
    video_path = output_dir / f"{safe_title}.mp4"
    if not assemble_video(audio_path, video_path, args.title):
        print("Video assembly failed")
        return 1
    print(f"Video saved: {video_path}")
    
    return 0


def cmd_templates(args):
    """List available templates."""
    templates = {
        "trading-update": "Daily portfolio and trading summary",
        "news-roundup": "AI/agent industry news summary",
        "tutorial": "Educational content with code examples",
        "story": "Narrative content with scene breaks"
    }
    
    print("Available templates:")
    for name, desc in templates.items():
        print(f"  {name:20} - {desc}")
    return 0


def main():
    parser = argparse.ArgumentParser(
        description="Content Automator - Faceless YouTube Pipeline"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # Trading command
    trading_parser = subparsers.add_parser("trading", help="Generate trading update video")
    trading_parser.add_argument("--portfolio", help="Path to portfolio/dashboard file")
    trading_parser.add_argument("--output", "-o", required=True, help="Output directory")
    trading_parser.set_defaults(func=cmd_trading)
    
    # Script command
    script_parser = subparsers.add_parser("script", help="Generate video from script file")
    script_parser.add_argument("--file", "-f", required=True, help="Path to script text file")
    script_parser.add_argument("--title", "-t", required=True, help="Video title")
    script_parser.add_argument("--output", "-o", required=True, help="Output directory")
    script_parser.set_defaults(func=cmd_script)
    
    # Templates command
    templates_parser = subparsers.add_parser("templates", help="List available templates")
    templates_parser.set_defaults(func=cmd_templates)
    
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
