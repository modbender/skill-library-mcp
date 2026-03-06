#!/usr/bin/env python3
"""
fal.ai API client for OpenClaw.
Handles queue-based requests with polling.

Usage:
  python fal_client.py submit <model_id> '<json_input>'
  python fal_client.py status <model_id> <request_id>
  python fal_client.py result <model_id> <request_id>
  python fal_client.py poll   # Poll all pending requests

Environment:
  FAL_KEY - API key (or reads from TOOLS.md)
"""

import os
import sys
import json
import time
import re
import requests
from pathlib import Path
from datetime import datetime

FAL_API_BASE = "https://queue.fal.run"
FAL_UPLOAD_URL = "https://fal.ai/api/storage/upload/initiate"

# Model schemas for validation
MODEL_SCHEMAS = {
    "fal-ai/nano-banana-pro": {
        "required": ["prompt"],
        "optional": ["num_images", "aspect_ratio", "resolution", "output_format", "seed", "safety_tolerance"]
    },
    "fal-ai/nano-banana-pro/edit": {
        "required": ["prompt", "image_urls"],
        "optional": ["num_images", "aspect_ratio", "resolution", "output_format", "seed", "safety_tolerance"],
        "file_fields": {"image_urls": {"type": "array", "accepts": "image"}}
    },
    "fal-ai/flux/dev/image-to-image": {
        "required": ["prompt", "image_url"],
        "optional": ["strength", "num_inference_steps", "guidance_scale", "seed", "num_images", "output_format"],
        "file_fields": {"image_url": {"type": "string", "accepts": "image"}}
    },
    "fal-ai/kling-video/o3/pro/video-to-video/edit": {
        "required": ["prompt", "video_url"],
        "optional": ["image_urls", "keep_audio", "elements", "shot_type"],
        "file_fields": {
            "video_url": {"type": "string", "accepts": "video", "formats": [".mp4", ".mov"], "max_mb": 200, "min_res": 720, "max_res": 2160, "duration": "3-10s"},
            "image_urls": {"type": "array", "accepts": "image", "max_count": 4, "description": "Style/appearance refs as @Image1, @Image2"},
            "elements": {"type": "array", "accepts": "object", "description": "Characters/objects as @Element1, @Element2. Each has reference_image_urls[] and frontal_image_url"}
        },
        "notes": [
            "Reference video in prompt as @Video1",
            "Reference images in prompt as @Image1, @Image2, etc.",
            "Elements in prompt as @Element1, @Element2, etc.",
            "Max 4 total (elements + reference images) when using video",
            "Video must be 3-10 seconds, .mp4 or .mov format"
        ]
    }
}
PENDING_FILE = Path(os.environ.get("FAL_PENDING_FILE", 
    Path.home() / ".openclaw/workspace/fal-pending.json"))
TOOLS_FILE = Path.home() / ".openclaw/workspace/TOOLS.md"

def validate_input(model_id: str, input_data: dict) -> tuple:
    """
    Validate input data against model schema.
    Returns (is_valid, errors, warnings)
    """
    errors = []
    warnings = []
    
    schema = MODEL_SCHEMAS.get(model_id)
    if not schema:
        warnings.append(f"No schema found for {model_id} - skipping validation")
        return True, errors, warnings
    
    # Check required fields
    for field in schema.get("required", []):
        if field not in input_data or input_data[field] is None:
            errors.append(f"Missing required field: {field}")
        elif input_data[field] == "" or input_data[field] == []:
            errors.append(f"Empty required field: {field}")
    
    # Check file fields
    for field, spec in schema.get("file_fields", {}).items():
        if field not in input_data:
            continue
            
        value = input_data[field]
        
        # Check array types
        if spec["type"] == "array":
            if not isinstance(value, list):
                errors.append(f"{field} must be an array")
            elif spec.get("max_count") and len(value) > spec["max_count"]:
                errors.append(f"{field} exceeds max count of {spec['max_count']}")
            elif len(value) == 0:
                errors.append(f"{field} is empty")
        
        # Check for data URI or URL
        if spec["type"] == "string" and value:
            if not (value.startswith("data:") or value.startswith("http")):
                warnings.append(f"{field} should be a URL or data URI")
    
    # Add notes as warnings
    for note in schema.get("notes", []):
        warnings.append(f"Note: {note}")
    
    return len(errors) == 0, errors, warnings

def get_model_info(model_id: str) -> dict:
    """Get model schema info for prompting user"""
    schema = MODEL_SCHEMAS.get(model_id, {})
    return {
        "model_id": model_id,
        "required": schema.get("required", []),
        "optional": list(schema.get("optional", [])),
        "file_fields": schema.get("file_fields", {}),
        "notes": schema.get("notes", [])
    }

def get_api_key():
    """Get API key from env, openclaw.json, or TOOLS.md"""
    # 1. Environment variable (highest priority)
    key = os.environ.get("FAL_KEY")
    if key:
        return key
    
    # 2. OpenClaw config (integrations.fal.apiKey)
    config_file = Path.home() / ".openclaw/openclaw.json"
    if config_file.exists():
        try:
            config = json.loads(config_file.read_text())
            key = config.get("integrations", {}).get("fal", {}).get("apiKey")
            if key:
                return key
        except:
            pass
    
    # 3. TOOLS.md fallback
    if TOOLS_FILE.exists():
        content = TOOLS_FILE.read_text()
        # Look for FAL_KEY: xxx or fal.ai key: xxx patterns
        # Key format: uuid:secret (includes colon)
        patterns = [
            r'FAL_KEY[:\s]+["\']?([a-zA-Z0-9_:-]+)["\']?',
            r'fal\.ai.*key[:\s]+["\']?([a-zA-Z0-9_:-]+)["\']?',
            r'fal.*api.*key[:\s]+["\']?([a-zA-Z0-9_:-]+)["\']?',
        ]
        for pattern in patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                return match.group(1).strip()
    
    return None

def get_headers():
    key = get_api_key()
    if not key:
        print("ERROR: No FAL_KEY found. Set FAL_KEY env var or add to TOOLS.md:")
        print("  ### fal.ai")
        print("  FAL_KEY: your-key-here")
        sys.exit(1)
    return {
        "Authorization": f"Key {key}",
        "Content-Type": "application/json"
    }

def load_pending():
    """Load pending requests from file"""
    if PENDING_FILE.exists():
        try:
            return json.loads(PENDING_FILE.read_text())
        except:
            return {"requests": []}
    return {"requests": []}

def save_pending(data):
    """Save pending requests to file"""
    PENDING_FILE.parent.mkdir(parents=True, exist_ok=True)
    PENDING_FILE.write_text(json.dumps(data, indent=2))

def submit(model_id: str, input_data: dict, skip_validation: bool = False) -> dict:
    """Submit a request to the queue with validation"""
    
    # Validate input
    if not skip_validation:
        is_valid, errors, warnings = validate_input(model_id, input_data)
        
        for warn in warnings:
            print(f"⚠️  {warn}", file=sys.stderr)
        
        if not is_valid:
            print("❌ Validation failed:", file=sys.stderr)
            for err in errors:
                print(f"   - {err}", file=sys.stderr)
            raise ValueError(f"Validation failed: {'; '.join(errors)}")
    
    url = f"{FAL_API_BASE}/{model_id}"
    resp = requests.post(url, headers=get_headers(), json=input_data)
    resp.raise_for_status()
    result = resp.json()
    
    # Add to pending
    pending = load_pending()
    pending["requests"].append({
        "request_id": result["request_id"],
        "model_id": model_id,
        "input": input_data,
        "status": "IN_QUEUE",
        "submitted_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat()
    })
    save_pending(pending)
    
    return result

def get_base_model(model_id: str) -> str:
    """Extract base model path for queue URLs (fal-ai/flux/dev/image-to-image -> fal-ai/flux)"""
    parts = model_id.split('/')
    if len(parts) >= 2:
        return '/'.join(parts[:2])  # fal-ai/flux, fal-ai/nano-banana-pro, etc.
    return model_id

def check_status(model_id: str, request_id: str) -> dict:
    """Check status of a queued request"""
    base_model = get_base_model(model_id)
    url = f"{FAL_API_BASE}/{base_model}/requests/{request_id}/status"
    resp = requests.get(url, headers=get_headers())
    resp.raise_for_status()
    return resp.json()

def get_result(model_id: str, request_id: str) -> dict:
    """Get result of a completed request"""
    base_model = get_base_model(model_id)
    url = f"{FAL_API_BASE}/{base_model}/requests/{request_id}"
    resp = requests.get(url, headers=get_headers())
    resp.raise_for_status()
    return resp.json()

def poll_pending() -> list:
    """Poll all pending requests, return completed ones"""
    pending = load_pending()
    completed = []
    still_pending = []
    
    for req in pending["requests"]:
        try:
            status = check_status(req["model_id"], req["request_id"])
            req["status"] = status.get("status", "UNKNOWN")
            req["updated_at"] = datetime.utcnow().isoformat()
            
            if status.get("status") == "COMPLETED":
                # Fetch full result
                result = get_result(req["model_id"], req["request_id"])
                req["result"] = result
                completed.append(req)
            elif status.get("status") in ["FAILED", "CANCELLED"]:
                req["error"] = status.get("error", "Unknown error")
                completed.append(req)
            else:
                # Still in progress
                req["queue_position"] = status.get("queue_position")
                still_pending.append(req)
        except Exception as e:
            req["error"] = str(e)
            req["updated_at"] = datetime.utcnow().isoformat()
            still_pending.append(req)  # Keep trying
    
    # Update pending file
    pending["requests"] = still_pending
    save_pending(pending)
    
    return completed

def list_pending() -> list:
    """List all pending requests"""
    pending = load_pending()
    return pending["requests"]

def file_to_data_uri(file_path: str) -> str:
    """Convert local file (image or video) to base64 data URI"""
    import base64
    import mimetypes
    
    mime_type, _ = mimetypes.guess_type(file_path)
    if not mime_type:
        # Default based on extension
        ext = Path(file_path).suffix.lower()
        mime_map = {
            '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.png': 'image/png',
            '.webp': 'image/webp', '.gif': 'image/gif',
            '.mp4': 'video/mp4', '.mov': 'video/quicktime', '.webm': 'video/webm',
            '.avi': 'video/x-msvideo', '.mkv': 'video/x-matroska'
        }
        mime_type = mime_map.get(ext, 'application/octet-stream')
    
    file_size = os.path.getsize(file_path)
    file_size_mb = file_size / (1024 * 1024)
    
    # Warn for large files
    if file_size_mb > 50:
        print(f"WARNING: File is {file_size_mb:.1f}MB. Large files may be slow or fail.", file=sys.stderr)
    if file_size_mb > 200:
        print(f"ERROR: File exceeds 200MB limit ({file_size_mb:.1f}MB)", file=sys.stderr)
        sys.exit(1)
    
    with open(file_path, "rb") as f:
        data = base64.b64encode(f.read()).decode("utf-8")
    
    return f"data:{mime_type};base64,{data}"

def image_to_data_uri(file_path: str) -> str:
    """Convert local image to base64 data URI (alias for backwards compat)"""
    return file_to_data_uri(file_path)

def video_to_data_uri(file_path: str) -> str:
    """Convert local video to base64 data URI with validation"""
    import subprocess
    
    # Check file size
    file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
    if file_size_mb > 200:
        print(f"ERROR: Video exceeds 200MB limit ({file_size_mb:.1f}MB)", file=sys.stderr)
        sys.exit(1)
    
    # Try to get video info with ffprobe
    try:
        result = subprocess.run(
            ['ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_streams', file_path],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            import json as json_mod
            info = json_mod.loads(result.stdout)
            for stream in info.get('streams', []):
                if stream.get('codec_type') == 'video':
                    width = stream.get('width', 0)
                    height = stream.get('height', 0)
                    if width < 720 or height < 720:
                        print(f"WARNING: Video resolution {width}x{height} may be below 720p minimum", file=sys.stderr)
                    if width > 2160 or height > 2160:
                        print(f"WARNING: Video resolution {width}x{height} may exceed 2160p maximum", file=sys.stderr)
                    break
    except FileNotFoundError:
        pass  # ffprobe not available, skip validation
    
    return file_to_data_uri(file_path)

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == "submit":
        if len(sys.argv) < 4:
            print("Usage: fal_client.py submit <model_id> '<json_input>'")
            sys.exit(1)
        model_id = sys.argv[2]
        input_data = json.loads(sys.argv[3])
        result = submit(model_id, input_data)
        print(json.dumps(result, indent=2))
    
    elif cmd == "status":
        if len(sys.argv) < 4:
            print("Usage: fal_client.py status <model_id> <request_id>")
            sys.exit(1)
        result = check_status(sys.argv[2], sys.argv[3])
        print(json.dumps(result, indent=2))
    
    elif cmd == "result":
        if len(sys.argv) < 4:
            print("Usage: fal_client.py result <model_id> <request_id>")
            sys.exit(1)
        result = get_result(sys.argv[2], sys.argv[3])
        print(json.dumps(result, indent=2))
    
    elif cmd == "poll":
        completed = poll_pending()
        print(json.dumps({"completed": completed, "count": len(completed)}, indent=2))
    
    elif cmd == "list":
        pending = list_pending()
        print(json.dumps({"pending": pending, "count": len(pending)}, indent=2))
    
    elif cmd == "check-key":
        key = get_api_key()
        if key:
            print(f"OK: Key found ({key[:8]}...)")
        else:
            print("ERROR: No key found")
            sys.exit(1)
    
    elif cmd == "to-data-uri":
        if len(sys.argv) < 3:
            print("Usage: fal_client.py to-data-uri <file_path>")
            sys.exit(1)
        uri = file_to_data_uri(sys.argv[2])
        print(uri)
    
    elif cmd == "video-to-uri":
        if len(sys.argv) < 3:
            print("Usage: fal_client.py video-to-uri <video_path>")
            sys.exit(1)
        uri = video_to_data_uri(sys.argv[2])
        print(uri)
    
    elif cmd == "model-info":
        if len(sys.argv) < 3:
            print("Usage: fal_client.py model-info <model_id>")
            print("\nAvailable models:")
            for model_id in MODEL_SCHEMAS.keys():
                print(f"  - {model_id}")
            sys.exit(0)
        info = get_model_info(sys.argv[2])
        print(json.dumps(info, indent=2))
    
    elif cmd == "models":
        print("Available models with schemas:")
        for model_id, schema in MODEL_SCHEMAS.items():
            required = ", ".join(schema.get("required", []))
            print(f"\n{model_id}")
            print(f"  Required: {required}")
            if schema.get("file_fields"):
                print(f"  File inputs: {', '.join(schema['file_fields'].keys())}")
    
    else:
        print(f"Unknown command: {cmd}")
        print(__doc__)
        sys.exit(1)

if __name__ == "__main__":
    main()
