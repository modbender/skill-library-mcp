#!/usr/bin/env python3
"""Generate Discord voice message waveform from an ogg file.
Usage: gen_waveform.py <ogg_file>
Output: JSON with duration_secs and base64-encoded waveform (256 points, 0-255).
"""

import subprocess
import struct
import base64
import json
import sys

def main():
    if len(sys.argv) < 2:
        print("Usage: gen_waveform.py <ogg_file>")
        sys.exit(1)

    ogg_file = sys.argv[1]

    # Get duration
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "csv=p=0", ogg_file],
        capture_output=True, text=True
    )
    duration_secs = float(result.stdout.strip())

    # Extract raw PCM (mono, 16-bit, 48kHz)
    result = subprocess.run(
        ["ffmpeg", "-i", ogg_file, "-f", "s16le", "-ac", "1",
         "-ar", "48000", "-"],
        capture_output=True
    )
    pcm_data = result.stdout

    # Parse samples
    num_samples = len(pcm_data) // 2
    samples = struct.unpack(f"<{num_samples}h", pcm_data[:num_samples * 2])

    # Generate 256-point waveform
    points = 256
    chunk_size = max(1, num_samples // points)
    waveform = []

    for i in range(points):
        start = i * chunk_size
        end = min(start + chunk_size, num_samples)
        if start >= num_samples:
            waveform.append(0)
            continue
        chunk = samples[start:end]
        avg = sum(abs(s) for s in chunk) / len(chunk)
        # Map to 0-255
        val = min(255, int(avg / 32768 * 255))
        waveform.append(val)

    waveform_b64 = base64.b64encode(bytes(waveform)).decode()

    print(json.dumps({
        "duration_secs": round(duration_secs, 2),
        "waveform": waveform_b64
    }))

if __name__ == "__main__":
    main()
