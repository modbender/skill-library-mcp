# /// script
# requires-python = ">=3.10"
# dependencies = ["httpx"]
# ///
"""
Venice AI Video Generation

Generate videos using Venice's /video/queue and /video/retrieve endpoints.
Video generation is asynchronous - queue returns immediately, then poll for completion.
API docs: https://docs.venice.ai
"""

import argparse
import base64
import os
import sys
import time
from datetime import datetime
from pathlib import Path

import httpx

VENICE_BASE_URL = "https://api.venice.ai/api/v1"

# Duration must be string per swagger
AVAILABLE_DURATIONS = ["5s", "10s"]

AVAILABLE_RESOLUTIONS = ["480p", "720p", "1080p"]


def get_api_key() -> str:
    """Get Venice API key from environment."""
    api_key = os.environ.get("VENICE_API_KEY")
    if not api_key:
        print("Error: VENICE_API_KEY environment variable is not set", file=sys.stderr)
        print("Get your API key at https://venice.ai → Settings → API Keys", file=sys.stderr)
        sys.exit(1)
    return api_key


def load_image_as_data_url(image_path: str) -> str:
    """Load an image file and convert to data URL."""
    path = Path(image_path)
    if not path.exists():
        print(f"Error: Image file not found: {image_path}", file=sys.stderr)
        sys.exit(1)
    
    image_bytes = path.read_bytes()
    b64_data = base64.b64encode(image_bytes).decode("utf-8")
    
    ext = path.suffix.lower()
    mime_type = {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".webp": "image/webp",
    }.get(ext, "image/png")
    
    return f"data:{mime_type};base64,{b64_data}"


def queue_video(
    prompt: str,
    model: str,
    image_url: str | None = None,  # Required for image-to-video models only
    duration: str = "5s",
    resolution: str = "720p",
    aspect_ratio: str | None = None,
    negative_prompt: str | None = None,
) -> str:
    """Queue a video generation job and return the queue_id."""
    api_key = get_api_key()

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    payload: dict = {
        "model": model,
        "prompt": prompt[:2500],  # Max 2500 chars
        "duration": duration,
    }

    # Handle image input - required for image-to-video models
    if image_url:
        if image_url.startswith("http://") or image_url.startswith("https://") or image_url.startswith("data:"):
            payload["image_url"] = image_url
        else:
            payload["image_url"] = load_image_as_data_url(image_url)

    if resolution:
        payload["resolution"] = resolution
    if aspect_ratio:
        payload["aspect_ratio"] = aspect_ratio
    if negative_prompt:
        payload["negative_prompt"] = negative_prompt[:2500]

    print(f"Queuing video generation...", file=sys.stderr)
    print(f"Model: {model}", file=sys.stderr)
    print(f"Duration: {duration}, Resolution: {resolution}", file=sys.stderr)
    print(f"Prompt: {prompt[:100]}{'...' if len(prompt) > 100 else ''}", file=sys.stderr)

    try:
        with httpx.Client(timeout=60.0) as client:
            response = client.post(
                f"{VENICE_BASE_URL}/video/queue",
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            
            data = response.json()
            # Response has queue_id per swagger
            queue_id = data.get("queue_id")
            
            if not queue_id:
                print("Error: No queue_id in response", file=sys.stderr)
                print(f"Response: {data}", file=sys.stderr)
                sys.exit(1)
            
            print(f"Video queued with ID: {queue_id}", file=sys.stderr)
            return queue_id

    except httpx.HTTPStatusError as e:
        print(f"HTTP Error: {e.response.status_code}", file=sys.stderr)
        try:
            error_data = e.response.json()
            print(f"Details: {error_data}", file=sys.stderr)
        except Exception:
            print(f"Response: {e.response.text[:500]}", file=sys.stderr)
        sys.exit(1)
    except httpx.RequestError as e:
        print(f"Request Error: {e}", file=sys.stderr)
        sys.exit(1)


def retrieve_video(queue_id: str, model: str, output: str, max_wait: int = 600) -> Path:
    """Poll for video completion and download when ready.
    
    /video/retrieve is a POST with queue_id and model in body.
    Returns binary video when complete, or JSON status when processing.
    """
    api_key = get_api_key()

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    start_time = time.time()
    poll_interval = 5  # Start with 5 seconds
    
    print(f"Waiting for video generation (max {max_wait}s)...", file=sys.stderr)

    try:
        with httpx.Client(timeout=30.0) as client:
            while time.time() - start_time < max_wait:
                # POST with queue_id and model in body
                response = client.post(
                    f"{VENICE_BASE_URL}/video/retrieve",
                    headers=headers,
                    json={"queue_id": queue_id, "model": model}
                )
                response.raise_for_status()
                
                content_type = response.headers.get("content-type", "")
                
                # Check if we got video or JSON status
                if "video" in content_type or "application/octet-stream" in content_type:
                    # Video is ready!
                    print("Video ready! Saving...", file=sys.stderr)
                    
                    output_path = Path(output).resolve()
                    output_path.write_bytes(response.content)
                    
                    print(f"Video saved to: {output_path}", file=sys.stderr)
                    print(f"MEDIA:{output_path}")
                    return output_path
                
                # Still processing - parse JSON status
                try:
                    data = response.json()
                except Exception:
                    # Might be video data with wrong content-type
                    if len(response.content) > 1000:
                        output_path = Path(output).resolve()
                        output_path.write_bytes(response.content)
                        print(f"Video saved to: {output_path}", file=sys.stderr)
                        print(f"MEDIA:{output_path}")
                        return output_path
                    raise
                
                status = data.get("status", "unknown")
                
                if status == "PROCESSING":
                    elapsed = int(time.time() - start_time)
                    exec_duration = data.get("execution_duration", 0) / 1000  # ms to s
                    avg_time = data.get("average_execution_time", 0) / 1000
                    
                    if avg_time > 0:
                        progress = min(99, int(exec_duration / avg_time * 100))
                        print(f"  Processing: ~{progress}% [{elapsed}s elapsed, ~{int(avg_time)}s typical]", file=sys.stderr)
                    else:
                        print(f"  Processing... [{elapsed}s elapsed]", file=sys.stderr)
                    
                    time.sleep(poll_interval)
                    if poll_interval < 15:
                        poll_interval += 2
                
                else:
                    print(f"Unexpected status: {status}", file=sys.stderr)
                    print(f"Response: {data}", file=sys.stderr)
                    sys.exit(1)
            
            print(f"Timeout: Video not ready after {max_wait}s", file=sys.stderr)
            print(f"Queue ID: {queue_id}, Model: {model} - you can retrieve it later", file=sys.stderr)
            sys.exit(1)

    except httpx.HTTPStatusError as e:
        print(f"HTTP Error: {e.response.status_code}", file=sys.stderr)
        try:
            error_data = e.response.json()
            print(f"Details: {error_data}", file=sys.stderr)
        except Exception:
            print(f"Response: {e.response.text[:500]}", file=sys.stderr)
        sys.exit(1)
    except httpx.RequestError as e:
        print(f"Request Error: {e}", file=sys.stderr)
        sys.exit(1)


def generate_video(
    prompt: str,
    output: str | None = None,
    model: str = "wan-2.6-image-to-video",
    image: str | None = None,  # Required for image-to-video models only
    duration: str = "5s",
    resolution: str = "720p",
    aspect_ratio: str | None = None,
    negative_prompt: str | None = None,
    max_wait: int = 600,
) -> Path:
    """Generate a video from a text prompt, optionally with a reference image."""
    # Queue the job
    queue_id = queue_video(
        prompt=prompt,
        model=model,
        image_url=image,
        duration=duration,
        resolution=resolution,
        aspect_ratio=aspect_ratio,
        negative_prompt=negative_prompt,
    )
    
    # Generate output filename if not provided
    if not output:
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        output = f"venice-video-{timestamp}.mp4"
    
    # Wait and retrieve
    return retrieve_video(queue_id, model, output, max_wait)


def main():
    parser = argparse.ArgumentParser(
        description="Generate videos using Venice AI"
    )
    parser.add_argument(
        "--prompt", "-p",
        required=True,
        help="Video description (max 2500 characters)"
    )
    parser.add_argument(
        "--image", "-i",
        help="Reference image (path or URL) - required for image-to-video models"
    )
    parser.add_argument(
        "--output", "-o",
        help="Output filename (default: venice-video-{timestamp}.mp4)"
    )
    parser.add_argument(
        "--model", "-m",
        default="wan-2.6-image-to-video",
        help="Video model (default: wan-2.6-image-to-video). Also: wan-2.6-text-to-video, wan-2.6-flash-image-to-video"
    )
    parser.add_argument(
        "--duration", "-d",
        choices=AVAILABLE_DURATIONS,
        default="5s",
        help="Video duration (default: 5s)"
    )
    parser.add_argument(
        "--resolution", "-r",
        choices=AVAILABLE_RESOLUTIONS,
        default="720p",
        help="Video resolution (default: 720p)"
    )
    parser.add_argument(
        "--aspect-ratio", "-a",
        help="Aspect ratio (e.g., 16:9, 9:16, 1:1)"
    )
    parser.add_argument(
        "--negative-prompt",
        help="What to avoid in the video"
    )
    parser.add_argument(
        "--max-wait",
        type=int,
        default=600,
        help="Maximum seconds to wait for completion (default: 600)"
    )

    args = parser.parse_args()
    
    generate_video(
        prompt=args.prompt,
        output=args.output,
        model=args.model,
        image=args.image,
        duration=args.duration,
        resolution=args.resolution,
        aspect_ratio=args.aspect_ratio,
        negative_prompt=args.negative_prompt,
        max_wait=args.max_wait,
    )


if __name__ == "__main__":
    main()
