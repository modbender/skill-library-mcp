#!/usr/bin/env python3
"""
Telnyx Text-to-Speech CLI for OpenClaw.
Usage: telnyx-tts.py <text> [-o output.mp3] [--voice VOICE]
Requires: TELNYX_API_KEY environment variable

Uses Telnyx WebSocket TTS API:
wss://api.telnyx.com/v2/text-to-speech/speech

The API sends audio in two forms:
1. Streaming chunks (small 1KB frames with text=null) for real-time playback
2. Complete blob (entire audio with text=<original>) 
3. Final frame (isFinal=true)

We use only the streaming chunks to avoid duplication.
"""

import argparse
import asyncio
import base64
import json
import os
import sys

try:
    import websockets
except ImportError:
    print("Error: websockets library required. Install with: pip install websockets", file=sys.stderr)
    sys.exit(1)


async def text_to_speech(text: str, api_key: str, voice: str, output_path: str) -> bool:
    """Convert text to speech using Telnyx WebSocket TTS API."""

    url = f"wss://api.telnyx.com/v2/text-to-speech/speech?voice={voice}"
    headers = {
        "Authorization": f"Bearer {api_key}"
    }

    audio_chunks = []
    
    try:
        async with websockets.connect(url, additional_headers=headers) as ws:
            # Send initialization frame (required)
            await ws.send(json.dumps({"text": " "}))

            # Send text frame
            await ws.send(json.dumps({"text": text}))

            # Send stop frame
            await ws.send(json.dumps({"text": ""}))

            # Receive audio chunks
            while True:
                try:
                    response = await asyncio.wait_for(ws.recv(), timeout=30.0)
                    data = json.loads(response)

                    # Stop on final frame
                    if data.get("isFinal"):
                        break
                    
                    # Skip the complete blob (has text set to original input)
                    if data.get("text") is not None:
                        continue
                    
                    # Collect streaming chunks only
                    if "audio" in data and data["audio"]:
                        audio_chunk = base64.b64decode(data["audio"])
                        audio_chunks.append(audio_chunk)

                except asyncio.TimeoutError:
                    break
                except websockets.exceptions.ConnectionClosed:
                    break

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return False

    if not audio_chunks:
        print("Error: No audio received", file=sys.stderr)
        return False

    # Write streaming chunks only
    with open(output_path, "wb") as f:
        for chunk in audio_chunks:
            f.write(chunk)

    return True


def main():
    parser = argparse.ArgumentParser(description="Telnyx Text-to-Speech")
    parser.add_argument("text", help="Text to convert to speech")
    parser.add_argument("-o", "--output", default="output.mp3", help="Output file path (default: output.mp3)")
    parser.add_argument("--voice", default="Telnyx.NaturalHD.astra",
                       help="Voice ID (default: Telnyx.NaturalHD.astra)")

    args = parser.parse_args()

    api_key = os.environ.get("TELNYX_API_KEY")
    if not api_key:
        print("Error: TELNYX_API_KEY environment variable not set", file=sys.stderr)
        sys.exit(1)

    success = asyncio.run(text_to_speech(args.text, api_key, args.voice, args.output))

    if success:
        print(args.output)
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
