#!/usr/bin/env python3
"""
ElevenLabs Pro - CLI tool for TTS, voice listing, and credits management.

Usage:
  python3 elevenlabs.py "Hello world" --voice Rachel --output audio.mp3
  python3 elevenlabs.py --list-voices
  python3 elevenlabs.py --list-voices --lang en --gender female
  python3 elevenlabs.py --credits
"""

import os
import sys
import json
import argparse
import requests
from pathlib import Path

API_BASE = "https://api.elevenlabs.io/v1"

def get_api_key():
    key = os.environ.get("ELEVENLABS_API_KEY")
    if not key:
        raise ValueError("ELEVENLABS_API_KEY environment variable not set.")
    return key

def get_headers(api_key):
    return {
        "xi-api-key": api_key,
        "Content-Type": "application/json",
    }

def list_voices(api_key, lang_filter=None, gender_filter=None):
    """List available voices, optionally filtered by language and gender."""
    r = requests.get(f"{API_BASE}/voices", headers=get_headers(api_key))
    r.raise_for_status()
    voices = r.json().get("voices", [])

    result = []
    for v in voices:
        labels = v.get("labels", {})
        lang = labels.get("language", labels.get("accent", "")).lower()
        gender = labels.get("gender", "").lower()

        if lang_filter and lang_filter.lower() not in lang:
            continue
        if gender_filter and gender_filter.lower() != gender:
            continue

        result.append({
            "voice_id": v["voice_id"],
            "name": v["name"],
            "gender": gender,
            "language": lang,
            "description": labels.get("description", ""),
            "use_case": labels.get("use case", ""),
        })

    return result

def get_voice_id(api_key, voice_name):
    """Get voice_id by name (case-insensitive, supports partial match on first word)."""
    voices = list_voices(api_key)
    query = voice_name.lower()
    # Exact match first
    for v in voices:
        if v["name"].lower() == query:
            return v["voice_id"]
    # Partial match: check if query matches the beginning of the name
    for v in voices:
        if v["name"].lower().startswith(query):
            return v["voice_id"]
    raise ValueError(f"Voice '{voice_name}' not found. Use --list-voices to see available voices.")

def text_to_speech(api_key, text, voice_id, output_path, model_id="eleven_turbo_v2_5",
                   stability=0.5, similarity_boost=0.75, style=0.0, use_speaker_boost=True):
    """Convert text to speech and save as MP3."""
    url = f"{API_BASE}/text-to-speech/{voice_id}"
    payload = {
        "text": text,
        "model_id": model_id,
        "voice_settings": {
            "stability": stability,
            "similarity_boost": similarity_boost,
            "style": style,
            "use_speaker_boost": use_speaker_boost,
        }
    }
    headers = get_headers(api_key)
    headers["Accept"] = "audio/mpeg"

    r = requests.post(url, headers=headers, json=payload, stream=True)
    r.raise_for_status()

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with open(output, "wb") as f:
        for chunk in r.iter_content(chunk_size=4096):
            f.write(chunk)

    return str(output.resolve())

def get_credits(api_key):
    """Get remaining character credits from subscription info."""
    r = requests.get(f"{API_BASE}/user/subscription", headers=get_headers(api_key))
    r.raise_for_status()
    data = r.json()
    return {
        "tier": data.get("tier", "unknown"),
        "character_count": data.get("character_count", 0),
        "character_limit": data.get("character_limit", 0),
        "characters_remaining": data.get("character_limit", 0) - data.get("character_count", 0),
        "next_reset": data.get("next_character_count_reset_unix", None),
    }


def main():
    parser = argparse.ArgumentParser(
        description="ElevenLabs Pro — TTS, voice listing, credits management"
    )
    parser.add_argument("text", nargs="?", help="Text to convert to speech")
    parser.add_argument("--voice", default="Rachel", help="Voice name (default: Rachel)")
    parser.add_argument("--voice-id", help="Voice ID (overrides --voice)")
    parser.add_argument("--output", default="output.mp3", help="Output MP3 file path")
    parser.add_argument("--model", default="eleven_turbo_v2_5",
                        help="Model ID (default: eleven_turbo_v2_5)")
    parser.add_argument("--stability", type=float, default=0.5, help="Voice stability (0-1)")
    parser.add_argument("--similarity", type=float, default=0.75, help="Similarity boost (0-1)")
    parser.add_argument("--style", type=float, default=0.0, help="Style exaggeration (0-1)")
    parser.add_argument("--list-voices", action="store_true", help="List available voices")
    parser.add_argument("--lang", help="Filter voices by language (e.g. en, fr)")
    parser.add_argument("--gender", help="Filter voices by gender (male/female)")
    parser.add_argument("--credits", action="store_true", help="Show remaining credits")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--api-key", help="ElevenLabs API key (overrides env var)")

    args = parser.parse_args()

    try:
        api_key = args.api_key or get_api_key()
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    if args.list_voices:
        voices = list_voices(api_key, lang_filter=args.lang, gender_filter=args.gender)
        if args.json:
            print(json.dumps(voices, indent=2))
        else:
            print(f"{'Name':<20} {'Gender':<8} {'Language':<12} {'Use Case':<20} ID")
            print("-" * 80)
            for v in voices:
                print(f"{v['name']:<20} {v['gender']:<8} {v['language']:<12} {v['use_case']:<20} {v['voice_id']}")
        return

    if args.credits:
        credits = get_credits(api_key)
        if args.json:
            print(json.dumps(credits, indent=2))
        else:
            print(f"Tier            : {credits['tier']}")
            print(f"Used            : {credits['character_count']:,}")
            print(f"Limit           : {credits['character_limit']:,}")
            print(f"Remaining       : {credits['characters_remaining']:,}")
            if credits["next_reset"]:
                from datetime import datetime
                reset_dt = datetime.utcfromtimestamp(credits["next_reset"])
                print(f"Next reset (UTC): {reset_dt.strftime('%Y-%m-%d %H:%M')}")
        return

    if not args.text:
        parser.print_help()
        sys.exit(1)

    try:
        if args.voice_id:
            voice_id = args.voice_id
        else:
            print(f"Resolving voice '{args.voice}'...")
            voice_id = get_voice_id(api_key, args.voice)
            print(f"Voice ID: {voice_id}")

        print(f"Generating audio ({len(args.text)} chars)...")
        saved_path = text_to_speech(
            api_key=api_key,
            text=args.text,
            voice_id=voice_id,
            output_path=args.output,
            model_id=args.model,
            stability=args.stability,
            similarity_boost=args.similarity,
            style=args.style,
        )
        if args.json:
            print(json.dumps({"status": "ok", "file": saved_path, "chars": len(args.text)}))
        else:
            print(f"✅ Audio saved to: {saved_path}")
    except requests.HTTPError as e:
        print(f"API error: {e.response.status_code} - {e.response.text}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
