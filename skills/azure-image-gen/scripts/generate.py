#!/usr/bin/env python3
"""
Azure OpenAI DALL-E Image Generator

Generate images using Azure OpenAI's DALL-E deployment.
"""

import argparse
import json
import os
import sys
import base64
import urllib.request
import urllib.error
from datetime import datetime
from pathlib import Path


def load_env():
    """Load environment variables from .env file if present."""
    env_file = Path(__file__).parent.parent / ".env"
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    os.environ.setdefault(key.strip(), value.strip().strip('"\''))


def generate_image(
    prompt: str,
    endpoint: str,
    api_key: str,
    deployment: str,
    api_version: str = "2024-02-01",
    size: str = "1024x1024",
    quality: str = "standard",
    style: str = "vivid",
) -> dict:
    """Generate a single image using Azure OpenAI DALL-E."""
    
    url = f"{endpoint}/openai/deployments/{deployment}/images/generations?api-version={api_version}"
    
    payload = {
        "prompt": prompt,
        "size": size,
        "quality": quality,
        "style": style,
        "n": 1,
        "response_format": "b64_json"
    }
    
    headers = {
        "Content-Type": "application/json",
        "api-key": api_key
    }
    
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    
    try:
        with urllib.request.urlopen(req, timeout=120) as response:
            result = json.loads(response.read().decode("utf-8"))
            return result
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8")
        print(f"HTTP Error {e.code}: {error_body}", file=sys.stderr)
        raise
    except urllib.error.URLError as e:
        print(f"URL Error: {e.reason}", file=sys.stderr)
        raise


def save_image(b64_data: str, filepath: Path) -> None:
    """Save base64 image data to file."""
    image_data = base64.b64decode(b64_data)
    with open(filepath, "wb") as f:
        f.write(image_data)


def create_gallery_html(images: list, out_dir: Path) -> None:
    """Create an HTML gallery for the generated images."""
    html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Azure DALL-E Generated Images</title>
    <style>
        * { box-sizing: border-box; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #1a1a2e; 
            color: #eee; 
            padding: 2rem;
            margin: 0;
        }
        h1 { text-align: center; margin-bottom: 2rem; }
        .gallery { 
            display: grid; 
            grid-template-columns: repeat(auto-fill, minmax(400px, 1fr)); 
            gap: 1.5rem;
            max-width: 1400px;
            margin: 0 auto;
        }
        .card { 
            background: #16213e; 
            border-radius: 12px; 
            overflow: hidden;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        }
        .card img { 
            width: 100%; 
            height: auto; 
            display: block;
            cursor: pointer;
            transition: transform 0.2s;
        }
        .card img:hover { transform: scale(1.02); }
        .card-body { padding: 1rem; }
        .prompt { 
            font-size: 0.9rem; 
            color: #aaa; 
            margin: 0;
            line-height: 1.4;
        }
        .meta { 
            font-size: 0.75rem; 
            color: #666; 
            margin-top: 0.5rem;
        }
        .timestamp { text-align: center; color: #666; margin-top: 2rem; }
    </style>
</head>
<body>
    <h1>🎨 Azure DALL-E Gallery</h1>
    <div class="gallery">
"""
    
    for img in images:
        html += f"""        <div class="card">
            <a href="{img['filename']}" target="_blank">
                <img src="{img['filename']}" alt="{img['prompt'][:100]}">
            </a>
            <div class="card-body">
                <p class="prompt">{img['prompt']}</p>
                <p class="meta">{img['size']} • {img['quality']} • {img['style']}</p>
            </div>
        </div>
"""
    
    html += f"""    </div>
    <p class="timestamp">Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
</body>
</html>"""
    
    with open(out_dir / "index.html", "w") as f:
        f.write(html)


def main():
    parser = argparse.ArgumentParser(description="Generate images using Azure OpenAI DALL-E")
    parser.add_argument("--prompt", "-p", required=True, help="Image prompt")
    parser.add_argument("--count", "-n", type=int, default=1, help="Number of images (default: 1)")
    parser.add_argument("--size", "-s", default="1024x1024", 
                        choices=["1024x1024", "1792x1024", "1024x1792"],
                        help="Image size (default: 1024x1024)")
    parser.add_argument("--quality", "-q", default="standard",
                        choices=["standard", "hd"],
                        help="Image quality (default: standard)")
    parser.add_argument("--style", default="vivid",
                        choices=["vivid", "natural"],
                        help="Image style (default: vivid)")
    parser.add_argument("--out-dir", "-o", default="./azure-images",
                        help="Output directory (default: ./azure-images)")
    parser.add_argument("--api-version", default="2024-02-01",
                        help="Azure OpenAI API version")
    
    args = parser.parse_args()
    
    # Load .env if present
    load_env()
    
    # Get Azure credentials
    endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")
    api_key = os.environ.get("AZURE_OPENAI_API_KEY")
    deployment = os.environ.get("AZURE_OPENAI_DALLE_DEPLOYMENT")
    
    if not all([endpoint, api_key, deployment]):
        print("Error: Missing required environment variables:", file=sys.stderr)
        if not endpoint:
            print("  - AZURE_OPENAI_ENDPOINT", file=sys.stderr)
        if not api_key:
            print("  - AZURE_OPENAI_API_KEY", file=sys.stderr)
        if not deployment:
            print("  - AZURE_OPENAI_DALLE_DEPLOYMENT", file=sys.stderr)
        sys.exit(1)
    
    # Clean endpoint URL
    endpoint = endpoint.rstrip("/")
    
    # Create output directory
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"🎨 Generating {args.count} image(s)...")
    print(f"   Prompt: {args.prompt[:80]}{'...' if len(args.prompt) > 80 else ''}")
    print(f"   Size: {args.size} | Quality: {args.quality} | Style: {args.style}")
    print()
    
    images = []
    manifest = {
        "prompt": args.prompt,
        "settings": {
            "size": args.size,
            "quality": args.quality,
            "style": args.style,
        },
        "images": []
    }
    
    for i in range(args.count):
        try:
            print(f"   [{i+1}/{args.count}] Generating...", end=" ", flush=True)
            
            result = generate_image(
                prompt=args.prompt,
                endpoint=endpoint,
                api_key=api_key,
                deployment=deployment,
                api_version=args.api_version,
                size=args.size,
                quality=args.quality,
                style=args.style,
            )
            
            # Get image data
            b64_data = result["data"][0]["b64_json"]
            revised_prompt = result["data"][0].get("revised_prompt", args.prompt)
            
            # Save image
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"image_{timestamp}_{i+1}.png"
            filepath = out_dir / filename
            save_image(b64_data, filepath)
            
            print(f"✓ Saved: {filename}")
            
            images.append({
                "filename": filename,
                "prompt": revised_prompt,
                "size": args.size,
                "quality": args.quality,
                "style": args.style,
            })
            
            manifest["images"].append({
                "filename": filename,
                "revised_prompt": revised_prompt,
            })
            
        except Exception as e:
            print(f"✗ Failed: {e}")
            continue
    
    if images:
        # Save manifest
        with open(out_dir / "manifest.json", "w") as f:
            json.dump(manifest, f, indent=2)
        
        # Create gallery
        create_gallery_html(images, out_dir)
        
        print()
        print(f"✅ Done! Generated {len(images)} image(s)")
        print(f"   Output: {out_dir.absolute()}")
        print(f"   Gallery: {out_dir.absolute()}/index.html")
    else:
        print()
        print("❌ No images were generated")
        sys.exit(1)


if __name__ == "__main__":
    main()
