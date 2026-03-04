#!/usr/bin/env python3
"""
UGC-Manual: Generate lip-sync videos from image + audio.

Usage:
    uv run generate.py --image <path_or_url> --audio <path_or_url> --output <output.mp4>
"""

import argparse
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from urllib.parse import urlparse

import requests

# ComfyDeploy API configuration
COMFY_DEPLOY_API_URL = "https://api.comfydeploy.com/api"
DEPLOYMENT_ID = "075ce7d3-81a6-4e3e-ab0e-7a25edf601b5"


def get_api_key():
    """Get API key from environment."""
    api_key = os.environ.get("COMFY_DEPLOY_API_KEY")
    if not api_key:
        raise ValueError(
            "COMFY_DEPLOY_API_KEY environment variable is required. "
            "Set it with: export COMFY_DEPLOY_API_KEY='your-key'"
        )
    return api_key


def is_url(string: str) -> bool:
    """Check if string is a valid URL."""
    try:
        result = urlparse(string)
        return all([result.scheme in ("http", "https"), result.netloc])
    except:
        return False


def convert_audio_to_wav(input_path: str, output_path: str = None) -> str:
    """
    Convert audio to WAV PCM 16-bit mono 48kHz.
    
    FabricLipsync requires proper WAV format. This converts any audio
    (MP3, OGG, M4A, etc.) to the correct format.
    
    Args:
        input_path: Path to input audio file
        output_path: Optional output path (defaults to temp file)
    
    Returns:
        Path to the converted WAV file
    """
    if output_path is None:
        # Create temp file with .wav extension
        fd, output_path = tempfile.mkstemp(suffix=".wav")
        os.close(fd)
    
    print(f"Converting audio to WAV PCM 16-bit mono 48kHz...")
    
    cmd = [
        "ffmpeg", "-y",
        "-i", input_path,
        "-ac", "1",           # mono
        "-ar", "48000",       # 48kHz sample rate
        "-c:a", "pcm_s16le",  # PCM 16-bit little-endian
        output_path
    ]
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        print(f"Converted: {input_path} -> {output_path}")
        return output_path
    except subprocess.CalledProcessError as e:
        print(f"FFmpeg error: {e.stderr}", file=sys.stderr)
        raise RuntimeError(f"Failed to convert audio: {e.stderr}")
    except FileNotFoundError:
        raise RuntimeError(
            "FFmpeg not found. Install with: sudo apt install ffmpeg"
        )


def upload_file(file_path: str, api_key: str) -> str:
    """Upload a local file to ComfyDeploy and return the URL."""
    print(f"Uploading: {file_path}")
    
    # Determine content type
    ext = Path(file_path).suffix.lower()
    content_types = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".mp3": "audio/mpeg",
        ".wav": "audio/wav",
        ".ogg": "audio/ogg",
    }
    content_type = content_types.get(ext, "application/octet-stream")
    
    with open(file_path, "rb") as f:
        files = {"file": (os.path.basename(file_path), f, content_type)}
        headers = {"Authorization": f"Bearer {api_key}"}
        
        response = requests.post(
            f"{COMFY_DEPLOY_API_URL}/file/upload",
            headers=headers,
            files=files
        )
        response.raise_for_status()
        
    result = response.json()
    url = result.get("file_url")
    print(f"Uploaded: {os.path.basename(file_path)} -> {url}")
    return url


def queue_workflow(image_url: str, audio_url: str, api_key: str) -> str:
    """Queue the UGC-MANUAL workflow and return run_id."""
    print(f"\nQueuing UGC-MANUAL workflow...")
    print(f"  Image: {image_url}")
    print(f"  Audio: {audio_url}")
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    payload = {
        "deployment_id": DEPLOYMENT_ID,
        "inputs": {
            "image": image_url,
            "input_audio": audio_url
        }
    }
    
    response = requests.post(
        f"{COMFY_DEPLOY_API_URL}/run/deployment/queue",
        headers=headers,
        json=payload
    )
    response.raise_for_status()
    
    result = response.json()
    run_id = result.get("run_id")
    print(f"Queued run: {run_id}")
    return run_id


def poll_for_completion(run_id: str, api_key: str, timeout: int = 600) -> dict:
    """Poll for run completion and return the result."""
    print("Waiting for completion...")
    
    headers = {"Authorization": f"Bearer {api_key}"}
    start_time = time.time()
    
    while True:
        if time.time() - start_time > timeout:
            raise TimeoutError(f"Run did not complete within {timeout} seconds")
        
        response = requests.get(
            f"{COMFY_DEPLOY_API_URL}/run/{run_id}",
            headers=headers
        )
        response.raise_for_status()
        
        result = response.json()
        status = result.get("status")
        live_status = result.get("live_status", "")
        progress = result.get("progress", 0)
        
        print(f"Status: {status} | {live_status} | {progress*100:.0f}%")
        
        if status == "success":
            print("Run completed successfully!")
            return result
        elif status in ("failed", "cancelled"):
            raise RuntimeError(f"Run {status}: {result}")
        
        time.sleep(5)


def download_video(result: dict, output_path: str) -> str:
    """Download the output video and return the path."""
    outputs = result.get("outputs", [])
    
    video_url = None
    for output in outputs:
        data = output.get("data", {})
        # Try images (video might be in images array)
        images = data.get("images", [])
        for img in images:
            url = img.get("url", "")
            if url.endswith(".mp4") or "video" in img.get("type", ""):
                video_url = url
                break
        # Try videos array
        videos = data.get("videos", [])
        for vid in videos:
            video_url = vid.get("url")
            if video_url:
                break
        if video_url:
            break
    
    if not video_url:
        # Fallback: look for any URL ending in .mp4
        import json
        result_str = json.dumps(result)
        import re
        mp4_urls = re.findall(r'https://[^"]+\.mp4', result_str)
        if mp4_urls:
            video_url = mp4_urls[0]
    
    if not video_url:
        raise ValueError("No video URL found in outputs")
    
    print(f"Downloading from: {video_url}")
    
    response = requests.get(video_url)
    response.raise_for_status()
    
    with open(output_path, "wb") as f:
        f.write(response.content)
    
    print(f"Saved: {output_path}")
    return output_path


def main():
    parser = argparse.ArgumentParser(
        description="Generate lip-sync videos from image + audio"
    )
    parser.add_argument(
        "--image", "-i",
        required=True,
        help="Path or URL to the image file"
    )
    parser.add_argument(
        "--audio", "-a",
        required=True,
        help="Path or URL to the audio file"
    )
    parser.add_argument(
        "--output", "-o",
        required=True,
        help="Output video path"
    )
    parser.add_argument(
        "--timeout", "-t",
        type=int,
        default=600,
        help="Timeout in seconds (default: 600)"
    )
    
    args = parser.parse_args()
    
    try:
        api_key = get_api_key()
        
        # Handle image input
        if is_url(args.image):
            image_url = args.image
            print(f"Using image URL: {image_url}")
        else:
            if not os.path.exists(args.image):
                raise FileNotFoundError(f"Image not found: {args.image}")
            image_url = upload_file(args.image, api_key)
        
        # Handle audio input - always convert to WAV PCM for FabricLipsync
        temp_wav = None
        if is_url(args.audio):
            # Download the audio first, then convert
            print(f"Downloading audio from URL: {args.audio}")
            response = requests.get(args.audio)
            response.raise_for_status()
            
            # Save to temp file
            ext = Path(urlparse(args.audio).path).suffix or ".mp3"
            fd, temp_audio = tempfile.mkstemp(suffix=ext)
            os.close(fd)
            with open(temp_audio, "wb") as f:
                f.write(response.content)
            
            # Convert to WAV
            temp_wav = convert_audio_to_wav(temp_audio)
            os.unlink(temp_audio)  # Clean up temp audio
            audio_url = upload_file(temp_wav, api_key)
        else:
            if not os.path.exists(args.audio):
                raise FileNotFoundError(f"Audio not found: {args.audio}")
            
            # Convert to WAV (even if already WAV, ensures correct format)
            temp_wav = convert_audio_to_wav(args.audio)
            audio_url = upload_file(temp_wav, api_key)
        
        # Queue the workflow
        run_id = queue_workflow(image_url, audio_url, api_key)
        
        # Wait for completion
        result = poll_for_completion(run_id, api_key, timeout=args.timeout)
        
        # Download the video
        download_video(result, args.output)
        
        # Cleanup temp WAV file
        if temp_wav and os.path.exists(temp_wav):
            os.unlink(temp_wav)
        
        print(f"\n✅ Video saved to: {args.output}")
        
    except Exception as e:
        # Cleanup on error
        if 'temp_wav' in locals() and temp_wav and os.path.exists(temp_wav):
            os.unlink(temp_wav)
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
