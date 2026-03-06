#!/usr/bin/env python3
"""
Watch kie.ai task progress
Polls task status without creating duplicates

Security manifest:
  Env vars:  KIE_API_KEY (required)
  Endpoints: https://api.kie.ai/api/v1/jobs/recordInfo (GET - polls task status by ID)
  File I/O:  writes downloaded images to <skill-root>/images/
             reads/writes <skill-root>/.task-state.json
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
    sys.exit(1)


def query_task(task_id):
    """Query task status from API"""
    url = f"{BASE_URL}/jobs/recordInfo?taskId={task_id}"
    headers = {"Authorization": f"Bearer {API_KEY}"}
    
    req = urllib.request.Request(url, headers=headers)
    
    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            return result
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8')
        print(f"HTTP Error {e.code}: {error_body}", file=sys.stderr)
        return None


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


def watch_task(task_id, max_wait=600, download=True):
    """Watch task until completion"""
    start_time = time.time()
    attempt = 0
    last_state = None
    
    print(f"Watching task: {task_id}", file=sys.stderr)
    print("", file=sys.stderr)
    
    while (time.time() - start_time) < max_wait:
        time.sleep(5)
        attempt += 1
        
        result = query_task(task_id)
        
        if not result or result.get("code") != 200:
            print(f"Error querying task (attempt {attempt})", file=sys.stderr)
            continue
        
        data = result["data"]
        state = data.get("state", "unknown")
        
        # Only log state changes
        if state != last_state:
            elapsed = int(time.time() - start_time)
            print(f"  [{elapsed}s] State: {state}", file=sys.stderr)
            last_state = state
            
            # Update local state
            state_manager.update_task(task_id, state)
        
        # Terminal states
        if state in ["success", "DONE"]:
            print("", file=sys.stderr)
            print("✓ Complete!", file=sys.stderr)
            
            # Parse results
            result_json_str = data.get("resultJson", "{}")
            try:
                result_data = json.loads(result_json_str)
            except:
                result_data = {}
            
            images = result_data.get("resultUrls", result_data.get("images", []))
            
            if not images:
                print("No images generated", file=sys.stderr)
                return None
            
            # Update state with results
            state_manager.update_task(task_id, "success", {"images": images})
            
            if not download:
                # Just return URLs
                for url in images:
                    print(f"MEDIA_URL: {url}")
                return images
            
            # Download images into images/ subdirectory of skill root
            output_dir = Path(__file__).parent.parent / "images"
            output_dir.mkdir(exist_ok=True)
            downloaded_paths = []
            
            for i, img_url in enumerate(images, 1):
                timestamp = time.strftime("%Y-%m-%d-%H-%M-%S")
                output_path = output_dir / f"{timestamp}-{i}.png"
                
                print(f"Downloading image {i}/{len(images)}...", file=sys.stderr)
                if download_image(img_url, str(output_path)):
                    downloaded_paths.append(str(output_path))
                    print(f"✓ Saved: {output_path}", file=sys.stderr)
            
            print("", file=sys.stderr)
            print("🎉 Generation complete!", file=sys.stderr)
            
            # Output for OpenClaw
            for path in downloaded_paths:
                print(f"MEDIA: {path}")
            
            return downloaded_paths
        
        elif state in ["failed", "FAILED"]:
            fail_msg = data.get("failMsg", "Unknown error")
            print(f"❌ Task failed: {fail_msg}", file=sys.stderr)
            state_manager.update_task(task_id, "failed", {"error": fail_msg})
            return None
        
        # Keep waiting
        elif state in ["waiting", "pending", "processing", "running", "PENDING", "PROCESSING"]:
            continue
        
        else:
            print(f"Unknown state: {state}", file=sys.stderr)
            continue
    
    # Timeout
    print(f"⏱️  Timeout: Task took longer than {max_wait}s", file=sys.stderr)
    print(f"Task is still {last_state}. Check logs: https://kie.ai/logs", file=sys.stderr)
    print(f"Resume with: kie-ai.sh watch {task_id}", file=sys.stderr)
    return None


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Watch kie.ai task progress")
    parser.add_argument("task_id", help="Task ID to watch")
    parser.add_argument("--max-wait", type=int, default=600, help="Max wait time in seconds (default: 600)")
    parser.add_argument("--no-download", action="store_true", help="Don't download, just show URLs")
    
    args = parser.parse_args()
    
    watch_task(args.task_id, max_wait=args.max_wait, download=not args.no_download)


if __name__ == "__main__":
    main()
