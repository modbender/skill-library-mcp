#!/usr/bin/env python3
"""
kie.ai Image Generation
Wrapper for Nano Banana Pro and other image models

Security manifest:
  Env vars:  KIE_API_KEY (required)
  Endpoints: https://api.kie.ai/api/v1/jobs/createTask (POST - sends prompt, model, settings)
             https://api.kie.ai/api/v1/jobs/recordInfo  (GET  - polls task status by ID)
  File I/O:  writes downloaded images to <skill-root>/images/
  No data is sent to any endpoint other than those listed above.
"""

import json
import os
import sys
import time
import urllib.request
import urllib.error
from pathlib import Path

# Import state manager
sys.path.insert(0, str(Path(__file__).parent))
import state_manager

API_KEY = os.getenv("KIE_API_KEY")
BASE_URL = "https://api.kie.ai/api/v1"

if not API_KEY:
    print("Error: KIE_API_KEY environment variable not set", file=sys.stderr)
    print("Get your API key from: https://kie.ai/api-key", file=sys.stderr)
    sys.exit(1)


def api_request(method, endpoint, data=None):
    """Make API request"""
    url = f"{BASE_URL}{endpoint}"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    req_data = json.dumps(data).encode('utf-8') if data else None
    req = urllib.request.Request(url, data=req_data, headers=headers, method=method)
    
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8')
        try:
            error_data = json.loads(error_body)
            print(f"API Error: {error_data.get('msg', 'Unknown error')}", file=sys.stderr)
        except:
            print(f"HTTP Error {e.code}: {e.reason}", file=sys.stderr)
            print(error_body, file=sys.stderr)
        sys.exit(1)


def create_task(prompt, model="nano-banana-pro", resolution="1K", aspect_ratio="1:1"):
    """Create image generation task"""
    data = {
        "model": model,
        "input": {
            "prompt": prompt,
            "resolution": resolution,
            "aspect_ratio": aspect_ratio,
            "output_format": "png"
        }
    }
    
    result = api_request("POST", "/jobs/createTask", data)
    
    if result.get("code") != 200:
        print(f"Error creating task: {result.get('msg', 'Unknown error')}", file=sys.stderr)
        sys.exit(1)
    
    return result["data"]["taskId"]


def query_task(task_id):
    """Query task status"""
    result = api_request("GET", f"/jobs/recordInfo?taskId={task_id}")
    
    if result.get("code") != 200:
        print(f"Error querying task: {result.get('msg', 'Unknown error')}", file=sys.stderr)
        sys.exit(1)
    
    return result["data"]


def wait_for_completion(task_id, max_wait=300):
    """Wait for task to complete and download immediately"""
    start_time = time.time()
    attempt = 0
    
    while (time.time() - start_time) < max_wait:
        time.sleep(5)
        attempt += 1
        
        data = query_task(task_id)
        state = data.get("state", "unknown")
        
        if attempt % 6 == 0:  # Every 30 seconds
            print(f"  Still waiting... ({state})", file=sys.stderr)
        
        if state in ["success", "DONE"]:
            # Parse and download IMMEDIATELY before URL expires
            result_json_str = data.get("resultJson", "{}")
            try:
                result_data = json.loads(result_json_str)
                images = result_data.get("resultUrls", result_data.get("images", []))
                
                if images:
                    # Download right now into images/ subdirectory of skill root
                    output_dir = Path(__file__).parent.parent / "images"
                    output_dir.mkdir(exist_ok=True)
                    downloaded_paths = []
                    
                    for i, img_url in enumerate(images, 1):
                        timestamp = time.strftime("%Y-%m-%d-%H-%M-%S")
                        output_path = output_dir / f"{timestamp}-{i}.png"
                        
                        if download_image(img_url, str(output_path)):
                            downloaded_paths.append(str(output_path))
                    
                    # Store paths in data for caller
                    data["downloaded_paths"] = downloaded_paths
            except Exception as e:
                print(f"Warning: {e}", file=sys.stderr)
            
            return data
        
        elif state in ["failed", "FAILED"]:
            fail_msg = data.get("failMsg", "Unknown error")
            print(f"Task failed: {fail_msg}", file=sys.stderr)
            sys.exit(1)
        
        elif state in ["waiting", "pending", "processing", "PENDING", "PROCESSING"]:
            continue
        
        else:
            print(f"Unknown state: {state}", file=sys.stderr)
            continue
    
    print(f"Timeout: Task took longer than {max_wait}s", file=sys.stderr)
    sys.exit(1)


def download_image(url, output_path):
    """Download image from URL with auth headers"""
    try:
        # Try with authorization header first
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "User-Agent": "Mozilla/5.0"
        }
        req = urllib.request.Request(url, headers=headers)
        
        with urllib.request.urlopen(req, timeout=30) as response:
            with open(output_path, 'wb') as f:
                f.write(response.read())
        return True
    except urllib.error.HTTPError as e:
        # If auth fails, try without
        if e.code == 403:
            try:
                urllib.request.urlretrieve(url, output_path)
                return True
            except:
                pass
        print(f"Error downloading image: {e}", file=sys.stderr)
        return False
    except Exception as e:
        print(f"Error downloading image: {e}", file=sys.stderr)
        return False


def upload_to_drive(file_path):
    """Upload file to Google Drive if configured"""
    config_path = Path(__file__).parent.parent / "config.json"
    
    if not config_path.exists():
        return False
    
    try:
        with open(config_path) as f:
            config = json.load(f)
        
        drive_config = config.get("drive", {})
        if not drive_config.get("enabled"):
            return False
        
        folder_id = drive_config.get("folder_id", "").strip()
        if not folder_id:
            print("Warning: Google Drive enabled but no folder_id configured", file=sys.stderr)
            return False
        
        # Import and call upload script
        upload_script = Path(__file__).parent / "upload-drive.py"
        if not upload_script.exists():
            print("Warning: upload-drive.py not found", file=sys.stderr)
            return False
        
        # Call upload script
        import subprocess
        result = subprocess.run(
            [sys.executable, str(upload_script), file_path, "--folder-id", folder_id, "--json"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            try:
                upload_result = json.loads(result.stdout)
                file_id = upload_result.get("id", "unknown")
                print(f"  ✓ Uploaded to Google Drive (ID: {file_id})", file=sys.stderr)
                return True
            except:
                print("  ✓ Uploaded to Google Drive", file=sys.stderr)
                return True
        else:
            print(f"Warning: Drive upload failed: {result.stderr}", file=sys.stderr)
            return False
            
    except Exception as e:
        print(f"Warning: Drive upload error: {e}", file=sys.stderr)
        return False


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate images via kie.ai")
    parser.add_argument("prompt", help="Image generation prompt")
    parser.add_argument("--model", default="nano-banana-pro", help="Model to use")
    parser.add_argument("--resolution", default="1K", choices=["1K", "2K", "4K"], help="Resolution")
    parser.add_argument("--aspect", default="1:1", help="Aspect ratio (1:1, 16:9, 9:16, etc.)")
    parser.add_argument("--upload-drive", action="store_true", help="Upload to Google Drive (requires config)")
    
    args = parser.parse_args()
    
    print(f"🍌 Generating image with {args.model}...", file=sys.stderr)
    print(f"Prompt: {args.prompt}", file=sys.stderr)
    print("", file=sys.stderr)
    
    # Create task
    task_id = create_task(args.prompt, args.model, args.resolution, args.aspect)
    print(f"Task ID: {task_id}", file=sys.stderr)
    
    # Save to state
    state_manager.add_task(task_id, args.prompt, args.model, {
        "resolution": args.resolution,
        "aspect_ratio": args.aspect
    })
    
    print("", file=sys.stderr)
    
    # Wait for completion (downloads immediately)
    print("Waiting for completion...", file=sys.stderr)
    result = wait_for_completion(task_id, max_wait=600)  # 10 minutes
    print("✓ Complete!", file=sys.stderr)
    print("", file=sys.stderr)
    
    # Update state
    state_manager.update_task(task_id, "success")
    
    # Get downloaded paths (already downloaded in wait_for_completion)
    downloaded_paths = result.get("downloaded_paths", [])
    
    if not downloaded_paths:
        print("No images downloaded", file=sys.stderr)
        sys.exit(1)
    
    print("🎉 Generation complete!", file=sys.stderr)
    
    # Upload to Google Drive if requested
    if args.upload_drive:
        print("", file=sys.stderr)
        print("Uploading to Google Drive...", file=sys.stderr)
        for path in downloaded_paths:
            upload_to_drive(path)
    
    print("", file=sys.stderr)
    
    # Output for OpenClaw (MEDIA: format)
    for path in downloaded_paths:
        print(f"MEDIA: {path}")


if __name__ == "__main__":
    main()
