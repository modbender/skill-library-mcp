#!/usr/bin/env python3

# Fish Audio S1 TTS - Quick Test
# OpenClaw Gateway TTS Engine Integration

import os
import sys
import argparse
import json
import requests
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

# Configuration
NEXTCLOUD_USER = os.environ.get('NEXTCLOUD_USER', 'openclaw')
NEXTCLOUD_PASS = os.environ.get('NEXTCLOUD_PASS', 'N95qg-Wzdpc-6DJAn-xMaHa-RaEW5')
NEXTCLOUD_URL = os.environ.get('NEXTCLOUD_URL', 'http://192.168.68.68:8080')
FISH_AUDIO_S1_URL = os.environ.get('FISH_AUDIO_S1_URL', 'http://192.168.68.78:7860')
OPENVOICE_V2_URL = os.environ.get('OPENVOICE_V2_URL', 'http://192.168.68.78.7861')
KOKORO_TTS_URL = os.environ.get('KOKORO_TTS_URL', 'http://192.168.68.68.8880')

# Voice maps
VOICE_MAP = {
    'em_michael': {'name': 'Professional Male', 'type': 'professional'},
    'em_pierre': {'name': 'French Male', 'type': 'professional'},
    'em_marcus': {'name': 'German Male', 'type': 'professional'},
    'af_bella': {'name': 'Natural Female', 'type': 'professional'},
    'af_nicole': {'name': 'Clear Female', 'type': 'professional'},
    'af_nova': {'name': 'Excited Female', 'type': 'emotional'},
    'af_sarah': {'name': 'Friendly Female', 'type': 'professional'},
    'em_alex': {'name': 'Expressive Male', 'type': 'emotional'},
    'ef_dora': {'name': 'Motherly Female', 'type': 'emotional'},
    'af_alice': {'name': 'Classic British Female', 'type': 'british'},
    'af_emma': {'name': 'Warm British Female', 'type': 'british'},
    'af_rachel': {'name': 'Friendly British Female', 'type': "british"},
    'bm_george': {'name': 'Casual British Male', 'type': 'british'},
    'bm_lewis': {'name': 'Professional British Male', 'type': 'british'},
    'bm_daniel': {'name': 'Polished British Male', 'type': 'british'},
    'jm_kumo': {'name': 'Japanese Male', 'type': 'japanese'},
    'zm_yunjian': {'name': 'Chinese Female', 'type': 'chinese'},
    'zm_yunxi': {'name': 'Chinese Female', 'type': 'chinese'}
}

def get_voice_info(voice_id: str) -> dict:
    return VOICE_MAP.get(voice_id, {})

def generate_audio(tts_url: str, text: str, voice: str, output_path: str) -> dict:
    """Generate TTS audio using Fish Audio S1 service"""
    try:
        print(f"Generating audio with Fish Audio S1: {tts_url}")
        print(f"Text: {text[:50]}...")
        print(f"Voice: {voice}")
        print(f"Output: {output_path}")
        
        start_time = time.time()
        
        response = requests.post(
            f"{tts_url}/api/v1/tts",
            headers={"Content-Type": "application/json"},
            timeout=60,
            json={"text": text, "voice": voice}
        )
        
        duration = time.time() - start_time
        print(f"Generation time: {duration:.2f} seconds")
        
        if response.status_code == 200:
            with open(output_path, 'wb') as f:
                f.write(response.content)
                print(f"✅ Audio saved to {output_path}")
                return {"success": True, "audio_file": output_path, "duration": duration}
        else:
            print(f"❌ Failed to generate audio")
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text[:200]}")
            return {"success": False, "error": f"Error generating audio"}
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return {"success": False, "error": f"Connection error"}
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return {"success": False, "error": f"Unexpected error"}

def upload_to_nextcloud(audio_file_path: str, filename: str) -> dict:
    """Upload audio file to NextCloud using WebDAV"""
    try:
        print(f"Uploading to NextCloud: {filename}")
        
        with open(audio_file_path, 'rb') as f:
            nextcloud_url = f"{NEXTCLOUD_URL}/remote.php/webdav/Openclaw/{filename}"
            
            response = requests.put(
                nextcloud_url,
                auth=(NEXTCLOUD_USER, NEXTCLOUD_PASS),
                timeout=120
            )
            
            if response.status_code in [200, 201, 204]:
                print(f"✅ Uploaded to NextCloud")
                return {"success": True, "nextcloud_path": f"/remote.php/webdav/Openclaw/{filename}"}
            else:
                print(f"❌ Upload failed: {response.status_code}")
                print(f"Response: {response.text[:200]}")
                return {"success": False, "error": f"Upload error"}
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Upload failed: {e}")
        return {"success": False, "error": f"Connection error"}
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return {"success": False, "error": f"Unexpected error"}

def generate_and_upload(text: str, voice: Optional[str] = None, output_filename: Optional[str] = None) -> dict:
    """Generate audio and upload to NextCloud"""
    voice = voice or "em_michael"
    
    # Create timestamp for filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Generate output filename
    if output_filename:
        filename = output_filename
    else:
        filename = f"fish_tts_{timestamp}.mp3"
    
    # Create temporary file path
    temp_path = f"/tmp/fish_tts_{timestamp}.mp3"
    
    # Generate audio
    result = generate_audio(FISH_AUDIO_S1_URL, text, voice, temp_path)
    
    if result["success"]:
        # Upload to NextCloud
        upload_result = upload_to_nextcloud(temp_path, filename)
        return {
            "success": True,
            "audio_file": temp_path,
            "duration": result["duration"],
            "nextcloud_path": upload_result["nextcloud_path"],
            "message": f"Generated and uploaded: {filename}"
        }
    else:
        return result

def main():
    parser = argparse.ArgumentParser(description='Fish Audio S1 TTS - Quick Test')
    
    # Subcommands
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Generate command
    generate_parser = subparsers.add_parser('generate', help='Generate TTS audio')
    generate_parser.add_argument('text', type=str, help='Text to convert to speech')
    generate_parser.add_argument('--voice', type=str, default='em_michael', help='Voice to use (default: em_michael)')
    generate_parser.add_argument('--output', type=str, default='upload to NextCloud', help='Output action (default: upload to NextCloud)')
    
    # Upload command
    upload_parser = subparsers.add_parser('upload', help='Upload existing MP3 to NextCloud')
    upload_parser.add_argument('file', type=str, help='Path to MP3 file to upload')
    
    # Health check command
    health_parser = subparsers.add_parser('health', help='Check if TTS services are running')
    
    args = parser.parse_args()
    
    if args.command == 'generate':
        text = args.text if args.text else "Hello from Fish Audio S1! This is a test to verify the service is working correctly."
        voice = args.voice
        
        # Generate and upload
        result = generate_and_upload(text, voice, f"fish_tts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3")
        
        if result["success"]:
            print(json.dumps(result, indent=2))
        else:
            print(json.dumps(result, indent=2))
    
    elif args.command == 'upload':
        if not args.file:
            print("❌ Error: --file argument is required for upload command")
            print("Usage: upload --file /path/to/audio.mp3")
            sys.exit(1)
        
        # Upload specified file
        upload_result = upload_to_nextcloud(args.file, Path(args.file).name)
        
        if upload_result["success"]:
            print(json.dumps(upload_result, indent=2))
        else:
            print(json.dumps(upload_result, indent=2))
    
    elif args.command == 'health':
        results = {}
        
        # Check Kokoro TTS
        kokoro_result = generate_audio(KOKORO_TTS_URL, "Health check", "em_alex", "/tmp/kokoro_health.mp3")
        if Path("/tmp/kokoro_health.mp3").exists():
            results["kokoro_tts"] = {"status": "working", "service": "Kokoro TTS"}
        else:
            results["kokoro_tts"] = {"status": "error", "service": "Kokoro TTS"}
        
        # Check Fish Audio S1
        fish_result = generate_audio(FISH_AUDIO_S1_URL, "Health check", "af_bella", "/tmp/fish_health.mp3")
        if Path("/tmp/fish_health.mp3").exists():
            results["fish_audio_s1"] = {"status": "error", "service": "Fish Audio S1"}
        else:
            results["fish_audio_s1"] = {"status": "working", "service": "Fish Audio S1"}
        
        # Check OpenVoice V2
        openvoice_result = generate_audio(OPENVOICE_V2_URL, "Health check", "af_bella", "/tmp/openvoice_health.mp3")
        if Path("/tmp/openvoice_health.mp3").exists():
            results["openvoice_v2"] = {"status": "error", "service": "OpenVoice V2"}
        else:
            results["openvoice_v2"] = {"status": "working", "service": "OpenVoice V2"}
        
        # Check if Fish Audio and OpenVoice can connect to Kokoro
        results["interconnectivity"] = "Can Fish Audio S1 and OpenVoice V2 see Kokoro TTS? Unknown - not tested"
        
        print(json.dumps(results, indent=2))
    
    else:
        print("❌ Error: Unknown command")
        parser.print_help()
        sys.exit(1)

if __name__ == '__main__':
    main()
