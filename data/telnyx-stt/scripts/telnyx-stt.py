#!/usr/bin/env python3
"""
Telnyx Speech-to-Text CLI wrapper for OpenClaw.
Usage: telnyx-stt.py <audio_file>
Requires: TELNYX_API_KEY environment variable
"""

import json
import os
import sys
import urllib.request
import urllib.error
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
import uuid


def transcribe(audio_path: str, api_key: str, language: str = "en") -> str:
    """Transcribe audio file using Telnyx Whisper API."""
    
    # Read audio file
    with open(audio_path, "rb") as f:
        audio_data = f.read()
    
    filename = os.path.basename(audio_path)
    
    # Detect content type from extension
    ext = os.path.splitext(filename)[1].lower()
    content_types = {
        '.ogg': 'audio/ogg',
        '.mp3': 'audio/mpeg',
        '.wav': 'audio/wav',
        '.m4a': 'audio/mp4',
        '.webm': 'audio/webm',
    }
    content_type = content_types.get(ext, 'application/octet-stream')
    
    # Build multipart form data manually
    boundary = f"----WebKitFormBoundary{uuid.uuid4().hex[:16]}"
    
    body = []
    
    # Add file part
    body.append(f"--{boundary}".encode())
    body.append(f'Content-Disposition: form-data; name="file"; filename="{filename}"'.encode())
    body.append(f"Content-Type: {content_type}".encode())
    body.append(b"")
    body.append(audio_data)
    
    # Add model part
    body.append(f"--{boundary}".encode())
    body.append(b'Content-Disposition: form-data; name="model"')
    body.append(b"")
    body.append(b"openai/whisper-large-v3-turbo")
    
    # Add language hint
    body.append(f"--{boundary}".encode())
    body.append(b'Content-Disposition: form-data; name="language"')
    body.append(b"")
    body.append(language.encode())
    
    # End boundary
    body.append(f"--{boundary}--".encode())
    body.append(b"")
    
    body_bytes = b"\r\n".join(body)
    
    url = "https://api.telnyx.com/v2/ai/audio/transcriptions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": f"multipart/form-data; boundary={boundary}",
    }
    
    req = urllib.request.Request(url, data=body_bytes, headers=headers, method='POST')
    
    try:
        with urllib.request.urlopen(req, timeout=60) as response:
            result = json.loads(response.read().decode('utf-8'))
            return result.get('text', '').strip()
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8') if e.fp else str(e)
        print(f"HTTP Error {e.code}: {error_body}", file=sys.stderr)
        return ""
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return ""


def main():
    if len(sys.argv) < 2:
        print("Usage: telnyx-stt.py <audio_file> [language]", file=sys.stderr)
        print("  language: ISO 639-1 code (e.g., 'en' for English, 'es' for Spanish)", file=sys.stderr)
        print("  Default: en (English)", file=sys.stderr)
        sys.exit(1)
    
    audio_path = sys.argv[1]
    language = sys.argv[2] if len(sys.argv) > 2 else "en"
    
    if not os.path.exists(audio_path):
        print(f"Error: File not found: {audio_path}", file=sys.stderr)
        sys.exit(1)
    
    api_key = os.environ.get("TELNYX_API_KEY")
    if not api_key:
        print("Error: TELNYX_API_KEY environment variable not set", file=sys.stderr)
        sys.exit(1)
    
    transcript = transcribe(audio_path, api_key, language)
    print(transcript)


if __name__ == "__main__":
    main()
