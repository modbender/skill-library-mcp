#!/usr/bin/env python3
"""
one_way_call.py — Generate ElevenLabs audio and play it on a Twilio call.
Usage: python3 one_way_call.py --to "+13105551234" --text "Hello!" [--voice VOICE_ID]
"""
import os, argparse, requests, tempfile
from twilio.rest import Client

ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY", "")
TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID", "")
TWILIO_AUTH_TOKEN  = os.environ.get("TWILIO_AUTH_TOKEN", "")
TWILIO_FROM        = os.environ.get("TWILIO_PHONE_NUMBER", "")
DEFAULT_VOICE      = "tyepWYJJwJM9TTFIg5U7"  # Clara — Australian female


def generate_audio(text: str, voice_id: str) -> bytes:
    r = requests.post(
        f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
        headers={"xi-api-key": ELEVENLABS_API_KEY, "Content-Type": "application/json"},
        json={
            "text": text,
            "model_id": "eleven_turbo_v2_5",
            "voice_settings": {"stability": 0.45, "similarity_boost": 0.8, "style": 0.5}
        }
    )
    r.raise_for_status()
    return r.content


def upload_audio(audio_bytes: bytes) -> str:
    """Upload to tmpfiles.org, return direct download URL (60 min TTL)."""
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
        f.write(audio_bytes)
        tmp_path = f.name
    resp = requests.post("https://tmpfiles.org/api/v1/upload", files={"file": open(tmp_path, "rb")})
    resp.raise_for_status()
    url = resp.json()["data"]["url"].replace("tmpfiles.org/", "tmpfiles.org/dl/")
    return url


def make_call(to: str, audio_url: str) -> str:
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    call = client.calls.create(
        from_=TWILIO_FROM,
        to=to,
        twiml=f"<Response><Play>{audio_url}</Play></Response>"
    )
    return call.sid


def main():
    parser = argparse.ArgumentParser(description="Make an AI-voiced phone call")
    parser.add_argument("--to",    required=True,         help="Phone number to call e.g. +13105551234")
    parser.add_argument("--text",  required=True,         help="Message to speak")
    parser.add_argument("--voice", default=DEFAULT_VOICE, help="ElevenLabs voice ID")
    parser.add_argument("--file",  default=None,          help="Pre-generated MP3 file (skips TTS)")
    args = parser.parse_args()

    if args.file:
        with open(args.file, "rb") as f:
            audio_bytes = f.read()
    else:
        print(f"🎙️  Generating audio...")
        audio_bytes = generate_audio(args.text, args.voice)

    print(f"📤  Uploading audio...")
    url = upload_audio(audio_bytes)
    print(f"📡  Audio URL: {url}")

    print(f"📞  Calling {args.to}...")
    sid = make_call(args.to, url)
    print(f"✅  Call initiated: {sid}")


if __name__ == "__main__":
    main()
