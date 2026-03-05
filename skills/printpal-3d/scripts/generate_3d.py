#!/usr/bin/env python3
"""
PrintPal 3D Model Generator

Generates 3D models from images or text prompts using PrintPal API.
For text prompts, optionally generates an image first using WaveSpeed API.
"""

import argparse
import os
import sys
import json
import urllib.request
from datetime import datetime
from pathlib import Path

# Output directory for generated files
# Default is "printpal-output" in workspace, can be overridden with PRINTPAL_OUTPUT_DIR env var
WORKSPACE_DIR = Path(__file__).resolve().parent.parent.parent
OUTPUT_DIR = Path(os.environ.get("PRINTPAL_OUTPUT_DIR", WORKSPACE_DIR / "printpal-output"))


def ensure_output_dir():
    """Create output directory if it doesn't exist."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    return OUTPUT_DIR


def get_timestamp():
    """Get timestamp for unique filenames."""
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def download_file(url, dest_path):
    """Download a file from URL to destination path."""
    dest_path = Path(dest_path)  # Ensure it's a Path object
    print(f"Downloading: {url}")
    print(f"Saving to: {dest_path}")
    
    req = urllib.request.Request(url, headers={'User-Agent': 'PrintPal-Skill/1.0'})
    with urllib.request.urlopen(req) as response:
        with open(dest_path, 'wb') as f:
            f.write(response.read())
    
    return str(dest_path)


def generate_image_wavespeed(prompt, output_dir, timestamp):
    """
    Generate an image from text using WaveSpeed API.
    
    The user's prompt is wrapped in a 3D render template for better results.
    
    Returns (path_string, error) tuple.
    """
    api_key = os.environ.get("WAVESPEED_API_KEY")
    if not api_key:
        return None, "WAVESPEED_API_KEY environment variable not set. Please configure it in OpenClaw config or set it as an environment variable."
    
    try:
        import wavespeed
    except ImportError:
        return None, "wavespeed package not installed. Run: pip install wavespeed"
    
    # Wrap user prompt in 3D render template for better results
    full_prompt = f"Generate a 3D render of {prompt}, isometric view, clear white background."
    
    print(f"Generating image from prompt using WaveSpeed...")
    print(f"User input: {prompt}")
    print(f"Full prompt: {full_prompt}")
    
    try:
        output = wavespeed.run(
            "google/nano-banana/text-to-image",
            {
                "enable_base64_output": False,
                "enable_sync_mode": True,
                "output_format": "png",
                "prompt": full_prompt
            }
        )
        
        # Debug: show what we got
        print(f"WaveSpeed response keys: {list(output.keys()) if isinstance(output, dict) else type(output)}")
        
        # WaveSpeed returns different formats depending on mode:
        # - Sync mode: {"outputs": ["url1", ...]} - no status field
        # - Async mode: {"id": "...", "status": "completed", "outputs": ["url1", ...]}
        
        image_url = None
        
        if isinstance(output, dict):
            # Check for outputs array (present in both sync and completed async)
            if output.get("outputs") and len(output["outputs"]) > 0:
                image_url = output["outputs"][0]
            # Check for failed status
            elif output.get("status") == "failed":
                return None, f"WaveSpeed generation failed: {output.get('error', 'Unknown error')}"
            # Check for pending/processing (shouldn't happen with sync mode)
            elif output.get("status") in ("pending", "processing"):
                return None, f"WaveSpeed still processing. This shouldn't happen with sync mode. Response: {output}"
        
        if not image_url:
            return None, f"WaveSpeed returned no image URL. Response: {output}"
        
        # Download the generated image
        image_path = Path(output_dir) / f"image_{timestamp}.png"
        download_file(image_url, image_path)
        return str(image_path), None
            
    except Exception as e:
        return None, f"WaveSpeed error: {str(e)}"


def generate_3d_printpal(image_path, output_dir, timestamp, quality="super", output_format="stl"):
    """
    Generate a 3D model from an image using PrintPal API.
    
    Returns (path_string, error) tuple.
    """
    api_key = os.environ.get("PRINTPAL_API_KEY")
    if not api_key:
        return None, "PRINTPAL_API_KEY environment variable not set. Please configure it in OpenClaw config or set it as an environment variable."
    
    try:
        from printpal import PrintPal, Quality, Format
    except ImportError:
        return None, "printpal package not installed. Run: pip install printpal"
    
    # Map quality string to enum
    quality_map = {
        "default": Quality.DEFAULT,
        "high": Quality.HIGH,
        "ultra": Quality.ULTRA,
        "super": Quality.SUPER,
        "super_texture": Quality.SUPER_TEXTURE,
        "superplus": Quality.SUPERPLUS,
        "superplus_texture": Quality.SUPERPLUS_TEXTURE,
    }
    
    # Map format string to enum
    format_map = {
        "stl": Format.STL,
        "glb": Format.GLB,
        "obj": Format.OBJ,
        "ply": Format.PLY,
        "fbx": Format.FBX,
    }
    
    quality_enum = quality_map.get(quality.lower(), Quality.SUPER)
    format_enum = format_map.get(output_format.lower(), Format.STL)
    
    print(f"Generating 3D model using PrintPal...")
    print(f"Image: {image_path}")
    print(f"Quality: {quality}")
    print(f"Format: {output_format}")
    
    try:
        client = PrintPal(api_key=api_key)
        
        # Check credits first
        credits = client.get_credits()
        print(f"Available credits: {credits.credits}")
        
        # Generate 3D model
        model_path = Path(output_dir) / f"model_{timestamp}.{output_format}"
        
        result_path = client.generate_and_download(
            image_path=str(image_path),
            output_path=str(model_path),
            quality=quality_enum,
            format=format_enum,
        )
        
        return str(result_path), None
        
    except Exception as e:
        error_msg = str(e)
        # Check for common errors
        if "insufficient" in error_msg.lower() or "credit" in error_msg.lower():
            return None, f"Insufficient PrintPal credits. Purchase more at https://printpal.io/buy-credits"
        return None, f"PrintPal error: {error_msg}"


def main():
    parser = argparse.ArgumentParser(
        description="Generate 3D models from images or text prompts"
    )
    parser.add_argument(
        "--image", "-i",
        help="Path to input image file or URL"
    )
    parser.add_argument(
        "--prompt", "-p",
        help="Text prompt to generate image from (requires WAVESPEED_API_KEY)"
    )
    parser.add_argument(
        "--quality", "-q",
        default="super",
        choices=["default", "high", "ultra", "super", "super_texture", "superplus", "superplus_texture"],
        help="Quality level for 3D generation (default: super)"
    )
    parser.add_argument(
        "--format", "-f",
        default="stl",
        choices=["stl", "glb", "obj", "ply", "fbx"],
        help="Output format for 3D model (default: stl)"
    )
    parser.add_argument(
        "--output-dir", "-o",
        help="Output directory for generated files"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON"
    )
    
    args = parser.parse_args()
    
    # Validate input
    if not args.image and not args.prompt:
        error_output = {
            "success": False,
            "image_path": None,
            "model_path": None,
            "error": "Either --image or --prompt must be provided"
        }
        if args.json:
            print(json.dumps(error_output, indent=2))
        else:
            print(f"Error: {error_output['error']}", file=sys.stderr)
        sys.exit(1)
    
    # Set output directory
    output_dir = Path(args.output_dir) if args.output_dir else ensure_output_dir()
    output_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = get_timestamp()
    
    # Build result dict with proper string conversion
    result = {
        "success": False,
        "image_path": None,
        "model_path": None,
        "error": None,
        "output_dir": str(output_dir)
    }
    
    # Handle image input
    image_path = args.image
    
    # Check if image is a URL and download it
    if image_path and (image_path.startswith('http://') or image_path.startswith('https://')):
        print(f"Detected URL input, downloading image...")
        downloaded_path = output_dir / f"downloaded_{timestamp}.png"
        try:
            download_file(image_path, downloaded_path)
            image_path = str(downloaded_path)
            result["image_path"] = image_path
            print(f"Downloaded to: {image_path}")
        except Exception as e:
            result["error"] = f"Failed to download image from URL: {e}"
            if args.json:
                print(json.dumps(result, indent=2))
            else:
                print(f"Error: {result['error']}", file=sys.stderr)
            sys.exit(1)
    elif image_path:
        # Local file path
        result["image_path"] = image_path
    
    if not image_path and args.prompt:
        # Generate image from prompt
        generated_image, error = generate_image_wavespeed(args.prompt, output_dir, timestamp)
        if error:
            result["error"] = error
            if args.json:
                print(json.dumps(result, indent=2))
            else:
                print(f"Error: {error}", file=sys.stderr)
            sys.exit(1)
        image_path = generated_image
        result["image_path"] = str(image_path)
    
    # Validate image exists
    if not image_path:
        result["error"] = "No image path provided or generated"
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"Error: {result['error']}", file=sys.stderr)
        sys.exit(1)
    
    if not Path(image_path).exists():
        result["error"] = f"Image file not found: {image_path}"
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"Error: {result['error']}", file=sys.stderr)
        sys.exit(1)
    
    # Generate 3D model
    model_path, error = generate_3d_printpal(
        image_path=image_path,
        output_dir=output_dir,
        timestamp=timestamp,
        quality=args.quality,
        output_format=args.format
    )
    
    if error:
        result["error"] = error
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"Error: {error}", file=sys.stderr)
        sys.exit(1)
    
    result["success"] = True
    result["image_path"] = str(image_path)
    result["model_path"] = str(model_path)
    
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"\n{'='*40}")
        print(f"Generation Complete!")
        print(f"{'='*40}")
        print(f"Image:     {image_path}")
        print(f"3D Model:  {model_path}")
        print(f"{'='*40}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
