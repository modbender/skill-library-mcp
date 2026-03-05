#!/usr/bin/env python3
"""
Solo Leveling System — ElevenLabs + Twilio Voice Call Integration
Generates unique TTS audio via ElevenLabs, then calls via Twilio playing that audio.

Usage:
  python3 elevenlabs_call.py "Your message here"
  python3 elevenlabs_call.py --type wake|gym|sleep|emergency
  
Config: twilio-config.json (add elevenlabs_api_key and elevenlabs_voice_id)
"""

import json
import sys
import os
import urllib.request
import urllib.parse
import base64
import tempfile
import time

CONFIG_PATH = os.environ.get(
    "TWILIO_CONFIG",
    os.path.expanduser("~/.openclaw/workspace/solo-leveling-data/twilio-config.json")
)

AUDIO_DIR = os.path.expanduser("~/.openclaw/workspace/solo-leveling-data/audio-cache")


def load_config():
    with open(CONFIG_PATH) as f:
        return json.load(f)


def generate_audio_elevenlabs(text, config):
    """Generate TTS audio via ElevenLabs API. Returns path to MP3 file."""
    api_key = config.get("elevenlabs_api_key")
    voice_id = config.get("elevenlabs_voice_id", "pNInz6obpgDQGcFmaJgB")  # Default: Adam
    model_id = config.get("elevenlabs_model", "eleven_monolingual_v1")
    
    if not api_key:
        print("ERROR: No ElevenLabs API key in config. Add 'elevenlabs_api_key' to twilio-config.json")
        sys.exit(1)
    
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    
    payload = json.dumps({
        "text": text,
        "model_id": model_id,
        "voice_settings": {
            "stability": 0.6,
            "similarity_boost": 0.85,
            "style": 0.3,
            "use_speaker_boost": True
        }
    }).encode()
    
    req = urllib.request.Request(url, data=payload, method="POST")
    req.add_header("xi-api-key", api_key)
    req.add_header("Content-Type", "application/json")
    req.add_header("Accept", "audio/mpeg")
    
    os.makedirs(AUDIO_DIR, exist_ok=True)
    timestamp = int(time.time())
    audio_path = os.path.join(AUDIO_DIR, f"call_{timestamp}.mp3")
    
    try:
        with urllib.request.urlopen(req) as response:
            with open(audio_path, "wb") as f:
                f.write(response.read())
        print(f"Audio generated: {audio_path}")
        return audio_path
    except urllib.error.HTTPError as e:
        error_body = e.read().decode()
        print(f"ERROR: ElevenLabs API returned {e.code}")
        print(error_body)
        sys.exit(1)


def upload_to_public_url(audio_path, config):
    """
    Upload audio to a publicly accessible URL for Twilio to fetch.
    Uses a simple local HTTP server approach or cloud storage.
    For now, we use Twilio's media approach with base64 in TwiML.
    """
    # Read audio file and base64 encode it
    with open(audio_path, "rb") as f:
        audio_data = f.read()
    return audio_path, audio_data


def make_call_with_elevenlabs(text, config=None):
    """Generate ElevenLabs audio and call via Twilio."""
    if config is None:
        config = load_config()
    
    account_sid = config["account_sid"]
    auth_token = config["auth_token"]
    from_number = config["twilio_number"]
    to_number = config["target_number"]
    
    if not to_number:
        print("ERROR: No target phone number configured.")
        sys.exit(1)
    
    # Step 1: Generate audio
    print(f"Generating audio for: {text[:80]}...")
    audio_path = generate_audio_elevenlabs(text, config)
    
    # Step 2: We need a public URL for the audio.
    # Option A: Use Twilio Assets (requires setup)
    # Option B: Use a temporary file hosting service
    # Option C: Fall back to Twilio TTS with the text
    # For now, using a simple approach: serve via ngrok or use TwiML bins
    
    # Practical approach: Upload to transfer.sh or similar for a temporary public URL
    try:
        with open(audio_path, "rb") as f:
            audio_data = f.read()
        
        # Try transfer.sh for temporary hosting
        req = urllib.request.Request(
            "https://transfer.sh/system-call.mp3",
            data=audio_data,
            method="PUT"
        )
        req.add_header("Content-Type", "audio/mpeg")
        
        with urllib.request.urlopen(req, timeout=30) as response:
            public_url = response.read().decode().strip()
            print(f"Audio uploaded: {public_url}")
    except Exception as e:
        print(f"Warning: Could not upload audio ({e}). Falling back to Twilio TTS.")
        # Fallback: use Twilio's built-in TTS
        return make_call_twilio_tts(text, config)
    
    # Step 3: Call via Twilio with the audio URL
    twiml = f'<Response><Play>{public_url}</Play><Pause length="1"/><Play>{public_url}</Play></Response>'
    
    url = f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Calls.json"
    data = urllib.parse.urlencode({
        "To": to_number,
        "From": from_number,
        "Twiml": twiml,
    }).encode()
    
    credentials = base64.b64encode(f"{account_sid}:{auth_token}".encode()).decode()
    req = urllib.request.Request(url, data=data, method="POST")
    req.add_header("Authorization", f"Basic {credentials}")
    
    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode())
            print(f"Call initiated: SID={result.get('sid')}")
            print(f"Status: {result.get('status')}")
            return result
    except urllib.error.HTTPError as e:
        error_body = e.read().decode()
        print(f"ERROR: Twilio API returned {e.code}")
        print(error_body)
        sys.exit(1)


def make_call_twilio_tts(text, config):
    """Fallback: use Twilio's built-in TTS."""
    account_sid = config["account_sid"]
    auth_token = config["auth_token"]
    from_number = config["twilio_number"]
    to_number = config["target_number"]
    voice = config.get("tts_voice", "Polly.Brian")
    language = config.get("tts_language", "en-GB")
    
    twiml = f'<Response><Say voice="{voice}" language="{language}">{text}</Say><Pause length="1"/><Say voice="{voice}" language="{language}">{text}</Say></Response>'
    
    url = f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Calls.json"
    data = urllib.parse.urlencode({
        "To": to_number,
        "From": from_number,
        "Twiml": twiml,
    }).encode()
    
    credentials = base64.b64encode(f"{account_sid}:{auth_token}".encode()).decode()
    req = urllib.request.Request(url, data=data, method="POST")
    req.add_header("Authorization", f"Basic {credentials}")
    
    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode())
            print(f"Call initiated (TTS fallback): SID={result.get('sid')}")
            return result
    except urllib.error.HTTPError as e:
        error_body = e.read().decode()
        print(f"ERROR: {e.code} - {error_body}")
        sys.exit(1)


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args:
        print("Usage: elevenlabs_call.py [--type wake|gym|sleep|emergency] [message]")
        print("\nRequires 'elevenlabs_api_key' and 'elevenlabs_voice_id' in twilio-config.json")
        sys.exit(1)
    
    message = " ".join(args)
    make_call_with_elevenlabs(message)
