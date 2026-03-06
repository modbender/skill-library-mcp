import argparse
import sys
import json
import os
import urllib.request
import urllib.error
import uuid

API_URL = "http://localhost:8000"

def check_health():
    try:
        with urllib.request.urlopen(f"{API_URL}/health", timeout=2) as response:
            if response.status == 200:
                data = json.loads(response.read().decode())
                print(f"✅ Voice Agent API is UP ({data})")
                return True
            else:
                print(f"❌ Voice Agent API returned status {response.status}")
                return False
    except urllib.error.URLError:
        print("❌ Could not connect to Voice Agent API (localhost:8000). Is the Docker container running?")
        print("Ensure your Voice Agent backend service is running and reachable.")
        return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

# --- LIVE TOOLS REMOVED ---


# --- FILE TOOLS (Zero Dependency) ---

def transcribe(filename):
    if not os.path.exists(filename):
        print(f"❌ File not found: {filename}")
        return

    try:
        print(f"📤 Transcribing {filename}...")
        
        # Multipart upload using standard library
        boundary = uuid.uuid4().hex
        headers = {'Content-Type': f'multipart/form-data; boundary={boundary}'}

        data = b''
        data += f'--{boundary}\r\n'.encode()
        data += f'Content-Disposition: form-data; name="file"; filename="{os.path.basename(filename)}"\r\n'.encode()
        data += b'Content-Type: application/octet-stream\r\n\r\n'
        with open(filename, 'rb') as f:
            data += f.read()
        data += f'\r\n--{boundary}--\r\n'.encode()

        req = urllib.request.Request(f"{API_URL}/transcribe", data=data, headers=headers)
        
        with urllib.request.urlopen(req) as response:
            if response.status == 200:
                resp_data = json.loads(response.read().decode())
                text = resp_data.get("text", "")
                print(f"📝 Transcription: \"{text}\"")
            else:
                print(f"❌ API Error: {response.read().decode()}")

    except Exception as e:
        print(f"❌ Error transcribing: {e}")

def synthesize(text, output_file):
    if not text:
        print("❌ No text provided.")
        return

    try:
        # Determine format from extension
        ext = os.path.splitext(output_file)[1].lower()
        fmt = "mp3"
        if ext == ".wav":
            fmt = "pcm"
        elif ext == ".ogg":
            # Force MP3 for OGG files to ensure WhatsApp mobile compatibility
            fmt = "mp3"
        elif ext == ".mp3":
            fmt = "mp3"
        
        print(f"🗣️  Synthesizing to {output_file} (format: {fmt})...")
        
        headers = {'Content-Type': 'application/json'}
        data = json.dumps({"text": text, "format": fmt}).encode('utf-8')
        req = urllib.request.Request(f"{API_URL}/tts", data=data, headers=headers)
        
        with urllib.request.urlopen(req) as response:
            with open(output_file, 'wb') as f:
                # Read safely
                while True:
                    chunk = response.read(8192)
                    if not chunk:
                        break
                    f.write(chunk)
                
        print(f"✅ Audio saved to {output_file}")

    except Exception as e:
        print(f"❌ Error synthesizing: {e}")

def main():
    parser = argparse.ArgumentParser(description="Voice Agent Skill Client")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    subparsers.add_parser("health", help="Check API health")
    
    transcribe_parser = subparsers.add_parser("transcribe", help="Transcribe audio file")
    transcribe_parser.add_argument("file", type=str, help="Path to audio file")
    
    synth_parser = subparsers.add_parser("synthesize", help="Synthesize text to file")
    synth_parser.add_argument("text", type=str, help="Text to speak")
    synth_parser.add_argument("--output", "-o", type=str, required=True, help="Output audio file path")
    
    args = parser.parse_args()
    
    # Simple direct calls
    if args.command == "health":
        if not check_health():
            sys.exit(1)
    elif args.command == "transcribe":
        transcribe(args.file)
    elif args.command == "synthesize":
        synthesize(args.text, args.output)

if __name__ == "__main__":
    main()
