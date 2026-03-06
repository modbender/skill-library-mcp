#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "httpx>=0.25.0",
# ]
# ///
"""
Generate UGC-style promotional videos with AI lip-sync using Veed-UGC workflow.

Usage:
    uv run generate.py --image person.jpg --script "Hola! Les quiero mostrar esto." --output video.mp4
"""

import argparse
import httpx
import os
import sys
import time
from pathlib import Path

# Force unbuffered output
sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)


DEPLOYMENT_ID = "627c8fb5-1285-4074-a17c-ae54f8a5b5c6"
API_BASE = "https://api.comfydeploy.com/api"
DEFAULT_VOICE_ID = "PBi4M0xL4G7oVYxKgqww"


def get_api_key(provided_key: str | None) -> str | None:
    """Get API key from argument or environment."""
    if provided_key:
        return provided_key
    return os.environ.get("COMFY_DEPLOY_API_KEY")


def upload_file(client: httpx.Client, api_key: str, file_path: str) -> str:
    """Upload a file to ComfyDeploy and return the URL."""
    path = Path(file_path)
    print(f"[DEBUG] upload_file called for: {file_path}", flush=True)
    
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    # Determine content type
    suffix = path.suffix.lower()
    if suffix in [".jpg", ".jpeg"]:
        content_type = "image/jpeg"
    elif suffix == ".png":
        content_type = "image/png"
    elif suffix == ".webp":
        content_type = "image/webp"
    else:
        content_type = "application/octet-stream"
    
    print(f"[DEBUG] Content type: {content_type}", flush=True)
    
    # Upload file using multipart form
    print(f"[DEBUG] Opening file and preparing upload...", flush=True)
    with open(path, "rb") as f:
        files = {"file": (path.name, f, content_type)}
        print(f"[DEBUG] Sending POST to {API_BASE}/file/upload", flush=True)
        response = client.post(
            f"{API_BASE}/file/upload",
            headers={"Authorization": f"Bearer {api_key}"},
            files=files
        )
    
    print(f"[DEBUG] Response status: {response.status_code}", flush=True)
    print(f"[DEBUG] Response body: {response.text[:500]}", flush=True)
    
    if response.status_code != 200:
        raise Exception(f"Failed to upload file: {response.text}")
    
    upload_info = response.json()
    file_url = upload_info.get("file_url") or upload_info.get("url") or upload_info.get("download_url")
    
    if not file_url:
        raise Exception(f"No URL in response: {upload_info}")
    
    print(f"Uploaded: {path.name} -> {file_url}", flush=True)
    return file_url


def queue_run(client: httpx.Client, api_key: str, inputs: dict) -> str:
    """Queue a run and return the run_id."""
    response = client.post(
        f"{API_BASE}/run/deployment/queue",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        },
        json={
            "deployment_id": DEPLOYMENT_ID,
            "inputs": inputs
        }
    )
    
    if response.status_code != 200:
        raise Exception(f"Failed to queue run: {response.text}")
    
    data = response.json()
    run_id = data.get("run_id")
    print(f"Queued run: {run_id}")
    return run_id


def poll_run(client: httpx.Client, api_key: str, run_id: str, timeout: int = 600) -> dict:
    """Poll for run completion."""
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        response = client.get(
            f"{API_BASE}/run/{run_id}",
            headers={"Authorization": f"Bearer {api_key}"}
        )
        
        if response.status_code != 200:
            raise Exception(f"Failed to get run status: {response.text}")
        
        data = response.json()
        status = data.get("status")
        
        if status == "success":
            print("Run completed successfully!")
            return data
        elif status in ["failed", "error"]:
            raise Exception(f"Run failed: {data}")
        
        print(f"Status: {status}... waiting")
        time.sleep(5)
    
    raise TimeoutError(f"Run timed out after {timeout}s")


def download_output(client: httpx.Client, output_url: str, output_path: str):
    """Download the output video."""
    print(f"Downloading from: {output_url}")
    response = client.get(output_url, follow_redirects=True)
    if response.status_code != 200:
        raise Exception(f"Failed to download output: {response.status_code}")
    
    with open(output_path, "wb") as f:
        f.write(response.content)
    
    print(f"Saved: {output_path}")


def find_video_output(outputs: list) -> str | None:
    """Find video URL in outputs."""
    for output in outputs:
        data = output.get("data", {})
        
        # Check for video files
        if "files" in data:
            for file_info in data["files"]:
                url = file_info.get("url", "")
                if any(ext in url.lower() for ext in [".mp4", ".webm", ".mov"]):
                    return url
        
        # Check for gifs/videos array
        if "gifs" in data:
            for gif_info in data["gifs"]:
                url = gif_info.get("url", "")
                if url:
                    return url
        
        # Check for videos array
        if "videos" in data:
            for video_info in data["videos"]:
                url = video_info.get("url", "")
                if url:
                    return url
        
        # Check direct url
        url = data.get("url", "")
        if any(ext in url.lower() for ext in [".mp4", ".webm", ".mov"]):
            return url
    
    return None


def main():
    parser = argparse.ArgumentParser(description="Generate UGC videos with Veed-UGC")
    
    # Required inputs
    parser.add_argument("--image", "-i", required=True, help="Image path or URL (person with product)")
    parser.add_argument("--script", "-s", required=True, help="Pure dialogue text (no annotations, just what the person says)")
    parser.add_argument("--output", "-o", required=True, help="Output video filename")
    
    # Optional inputs
    parser.add_argument("--voice-id", "-v", default=DEFAULT_VOICE_ID, help=f"ElevenLabs voice ID (default: {DEFAULT_VOICE_ID})")
    parser.add_argument("--api-key", "-k", help="ComfyDeploy API key")
    parser.add_argument("--timeout", "-t", type=int, default=600, help="Timeout in seconds (default: 600)")
    
    args = parser.parse_args()
    
    # Get API key
    api_key = get_api_key(args.api_key)
    if not api_key:
        print("Error: No API key provided.", file=sys.stderr)
        print("Set COMFY_DEPLOY_API_KEY or use --api-key", file=sys.stderr)
        sys.exit(1)
    
    # Determine if image is URL or file
    image_url = args.image
    
    # Create HTTP client
    with httpx.Client(timeout=120.0) as client:
        # Upload image if it's a local file
        if not args.image.startswith(("http://", "https://")):
            print("Uploading image...")
            image_url = upload_file(client, api_key, args.image)
        else:
            print(f"Using image URL: {image_url}")
        
        # Build inputs
        inputs = {
            "image": image_url,
            "script": args.script,
            "voice_id": args.voice_id
        }
        
        print(f"\nInputs:")
        print(f"  Image: {image_url}")
        print(f"  Script: {args.script[:100]}{'...' if len(args.script) > 100 else ''}")
        print(f"  Voice ID: {args.voice_id}")
        
        # Queue run
        print("\nQueuing generation...")
        run_id = queue_run(client, api_key, inputs)
        
        # Poll for completion
        print("Waiting for completion...")
        result = poll_run(client, api_key, run_id, timeout=args.timeout)
        
        # Find and download video output
        outputs = result.get("outputs", [])
        video_url = find_video_output(outputs)
        
        if video_url:
            download_output(client, video_url, args.output)
        else:
            print("Warning: No video output found in results")
            print(f"Outputs: {outputs}")
            
            # Try to find any URL
            for output in outputs:
                data = output.get("data", {})
                print(f"Output data: {data}")


if __name__ == "__main__":
    main()
