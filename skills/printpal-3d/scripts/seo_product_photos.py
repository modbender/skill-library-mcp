#!/usr/bin/env python3
"""
SEO Product Listing Generator for PrintPal

This script generates SEO-optimized metadata and product photos for 3D models/prints.
Workflow:
1. Takes user input: image + description (item, purpose, audience)
2. Generates SEO-optimized title, description, tags via OpenRouter MiniMax
3. Generates 5 product photos using WaveSpeed nano-banana/edit
4. Saves everything to a ZIP file and provides download URL
"""

import argparse
import json
import os
import requests
import shutil
import subprocess
import sys
import tempfile
import zipfile
from datetime import datetime
from pathlib import Path
from pathlib import Path

# Configuration
WORKSPACE = Path(__file__).resolve().parent.parent.parent
OUTPUT_DIR = WORKSPACE / "printpal-seo-output"
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"


def setup_output_dir():
    """Create output directory if it doesn't exist."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print(f"Output directory: {OUTPUT_DIR}")


def call_openrouter(prompt: str, system_prompt: str = None) -> str:
    """Call OpenRouter MiniMax API to generate SEO content."""
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY environment variable not set")
    
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://openclaw.ai",
        "X-Title": "PrintPal SEO Generator"
    }
    
    data = {
        "model": "minimax/minimax-m2.5",
        "messages": messages,
        "max_tokens": 2000
    }
    
    print("Calling OpenRouter MiniMax API...")
    response = requests.post(OPENROUTER_API_URL, headers=headers, json=data, timeout=60)
    response.raise_for_status()
    
    result = response.json()
    content = result['choices'][0]['message']['content']
    print("OpenRouter API call completed.")
    return content


def generate_seo_metadata(image_path: str, description: str, purpose: str, audience: str) -> dict:
    """Generate SEO-optimized title, description, and tags using OpenRouter."""
    
    system_prompt = """You are an expert SEO copywriter specializing in 3D printed products for marketplaces like Etsy, TikTok Shop, and similar platforms. 
Generate compelling, search-optimized metadata that will help products rank well and convert sales.
Output ONLY valid JSON, no markdown formatting."""
    
    prompt = f"""Generate SEO-optimized metadata for a 3D print product based on the following information:

Image: {image_path}
Product Description: {description}
Product Purpose/Use: {purpose}
Target Audience: {audience}

Generate a JSON object with these exact fields:
{{
    "title": "SEO-optimized product title (max 140 characters, include relevant keywords)",
    "short_title": "Short catchy title for thumbnails (max 40 characters)",
    "description": "Detailed product description for listing (500-1000 words, include keywords naturally, highlight features and benefits)",
    "tags": ["tag1", "tag2", "tag3", "tag4", "tag5", "tag6", "tag7", "tag8", "tag9", "tag10", "tag11", "tag12", "tag13", "tag14", "tag15"],
    "category": "Primary marketplace category",
    "search_terms": ["term1", "term2", "term3", "term4", "term5"],
    "key_features": ["feature1", "feature2", "feature3", "feature4"],
    "target_marketplace": "Best marketplace for this product"
}}

Make the title and description compelling for buyers while being optimized for search. Include relevant 3D printing keywords like "3D printed", "STL file", "download", etc. as appropriate."""

    result = call_openrouter(prompt, system_prompt)
    
    # Parse JSON from response (handle potential markdown code blocks)
    result = result.strip()
    if result.startswith("```json"):
        result = result[7:]
    if result.startswith("```"):
        result = result[3:]
    if result.endswith("```"):
        result = result[:-3]
    result = result.strip()
    
    try:
        metadata = json.loads(result)
    except json.JSONDecodeError as e:
        print(f"JSON parse error: {e}")
        print(f"Raw response: {result}")
        raise
    
    print(f"Generated SEO metadata:")
    print(f"  Title: {metadata.get('title', 'N/A')}")
    print(f"  Tags: {', '.join(metadata.get('tags', [])[:5])}...")
    
    return metadata


def generate_product_photos(image_path: str, description: str, num_photos: int = 5) -> list:
    """Generate product photos using WaveSpeed nano-banana/edit."""
    
    api_key = os.environ.get("WAVESPEED_API_KEY")
    if not api_key:
        raise ValueError("WAVESPEED_API_KEY environment variable not set")
    
    # Check for wavespeed package
    try:
        from wavespeed import Client
    except ImportError:
        raise ImportError(
            "wavespeed package not installed. Run: pip install wavespeed printpal\n"
            "This is required for product photo generation."
        )
    
    client = Client(api_key=api_key)
    
    # Photo prompts for different product photo styles
    prompts = [
        f"Professional product photography on clean white background, {description}, studio lighting, e-commerce ready",
        f"Lifestyle product photo on rustic wooden surface, {description}, warm natural lighting, inviting atmosphere",
        f"Product shown in creative display, {description}, minimalist modern setting, soft shadows",
        f"Product photography with gradient background, {description}, vibrant colors, social media ready",
        f"Clean professional product shot, {description}, against soft gray background, high detail, commercial use"
    ]
    
    # Handle image input - could be path or URL
    if os.path.isfile(image_path):
        # Upload local image to get URL
        print(f"Uploading local image: {image_path}")
        try:
            import wavespeed
            image_url = wavespeed.upload(image_path)
        except Exception as e:
            print(f"Upload failed: {e}, using local path as-is")
            image_url = image_path
    else:
        image_url = image_path
    
    print(f"Using image URL: {image_url}")
    
    generated_urls = []
    for i, prompt in enumerate(prompts[:num_photos]):
        print(f"Generating photo {i+1}/{num_photos}...")
        
        try:
            result = client.run("google/nano-banana/edit", {
                "enable_sync_mode": True,
                "enable_base64_output": False,
                "images": [image_url],
                "output_format": "png",
                "prompt": prompt
            })
            
            print(f"  API result: {result}")
            
            if result.get("status") == "completed" and result.get("outputs"):
                photo_url = result["outputs"][0]
                generated_urls.append(photo_url)
                print(f"  ✓ Photo {i+1}: {photo_url}")
            elif result.get("outputs"):
                # Handle case where status not set but outputs present
                photo_url = result["outputs"][0]
                generated_urls.append(photo_url)
                print(f"  ✓ Photo {i+1}: {photo_url}")
            else:
                print(f"  ✗ Photo {i+1} failed: {result.get('error', 'No outputs')}")
                
        except Exception as e:
            print(f"  ✗ Photo {i+1} error: {e}")
            continue
    
    return generated_urls


def download_images(urls: list, output_dir: str) -> list:
    """Download images from URLs to local files."""
    local_paths = []
    
    for i, url in enumerate(urls):
        try:
            print(f"Downloading image {i+1}/{len(urls)}...")
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            ext = ".png" if url.endswith(".png") else ".jpg"
            filename = f"product_photo_{i+1:02d}{ext}"
            filepath = os.path.join(output_dir, filename)
            
            with open(filepath, "wb") as f:
                f.write(response.content)
            
            local_paths.append(filepath)
            print(f"  ✓ Saved: {filename}")
            
        except Exception as e:
            print(f"  ✗ Failed to download {url}: {e}")
            continue
    
    return local_paths


def save_metadata(metadata: dict, output_dir: str) -> str:
    """Save metadata to text file."""
    filepath = os.path.join(output_dir, "seo_metadata.txt")
    
    with open(filepath, "w") as f:
        f.write("=" * 60 + "\n")
        f.write("SEO PRODUCT LISTING METADATA\n")
        f.write("=" * 60 + "\n\n")
        
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write("TITLE (Full)\n")
        f.write("-" * 40 + "\n")
        f.write(metadata.get("title", "N/A") + "\n\n")
        
        f.write("TITLE (Short/Thumbnail)\n")
        f.write("-" * 40 + "\n")
        f.write(metadata.get("short_title", "N/A") + "\n\n")
        
        f.write("DESCRIPTION\n")
        f.write("-" * 40 + "\n")
        f.write(metadata.get("description", "N/A") + "\n\n")
        
        f.write("TAGS (15 max)\n")
        f.write("-" * 40 + "\n")
        f.write(", ".join(metadata.get("tags", [])) + "\n\n")
        
        f.write("CATEGORY\n")
        f.write("-" * 40 + "\n")
        f.write(metadata.get("category", "N/A") + "\n\n")
        
        f.write("SEARCH TERMS\n")
        f.write("-" * 40 + "\n")
        f.write(", ".join(metadata.get("search_terms", [])) + "\n\n")
        
        f.write("KEY FEATURES\n")
        f.write("-" * 40 + "\n")
        for feature in metadata.get("key_features", []):
            f.write(f"  • {feature}\n")
        
        f.write("\nTARGET MARKETPLACE\n")
        f.write("-" * 40 + "\n")
        f.write(metadata.get("target_marketplace", "N/A") + "\n")
    
    print(f"Metadata saved to: {filepath}")
    return filepath


def create_download_package(output_dir: str) -> str:
    """Create ZIP file containing all outputs."""
    zip_path = os.path.join(OUTPUT_DIR, "seo_product_listing.zip")
    
    # Remove existing zip if present
    if os.path.exists(zip_path):
        os.remove(zip_path)
    
    print(f"Creating ZIP package: {zip_path}")
    
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(output_dir):
            for file in files:
                if file == "seo_product_listing.zip":
                    continue
                filepath = os.path.join(root, file)
                arcname = file
                zf.write(filepath, arcname)
                print(f"  Added: {arcname}")
    
    print(f"ZIP package created: {zip_path}")
    return zip_path


def start_file_server(port: int = 8766) -> subprocess.Popen:
    """Start HTTP server for file downloads."""
    print(f"Starting file server on port {port}...")
    
    # Kill any existing server on this port
    try:
        subprocess.run(["pkill", "-f", f"serve_files.py.*{port}"], stderr=subprocess.DEVNULL)
    except:
        pass
    
    # Start new server
    server_script = os.path.join(os.path.dirname(__file__), "serve_files.py")
    
    proc = subprocess.Popen(
        [sys.executable, server_script, "-d", OUTPUT_DIR, "-p", str(port)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Wait a moment for server to start
    import time
    time.sleep(2)
    
    return proc


def main():
    parser = argparse.ArgumentParser(
        description="Generate SEO-optimized metadata and product photos for 3D prints"
    )
    parser.add_argument("-i", "--image", required=True, help="Path or URL to input image")
    parser.add_argument("-d", "--description", required=True, help="Description of the 3D model/print")
    parser.add_argument("-p", "--purpose", required=True, help="What the item is for/its use")
    parser.add_argument("-a", "--audience", required=True, help="Target audience/customers")
    parser.add_argument("-n", "--num-photos", type=int, default=5, help="Number of product photos to generate (default: 5)")
    parser.add_argument("--port", type=int, default=8766, help="Download server port (default: 8766)")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("SEO PRODUCT LISTING GENERATOR")
    print("=" * 60)
    
    # Setup
    setup_output_dir()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    session_dir = os.path.join(OUTPUT_DIR, f"session_{timestamp}")
    os.makedirs(session_dir, exist_ok=True)
    
    results = {
        "timestamp": timestamp,
        "input": {
            "image": args.image,
            "description": args.description,
            "purpose": args.purpose,
            "audience": args.audience
        },
        "metadata": None,
        "photos": [],
        "download_url": None
    }
    
    try:
        # Step 1: Generate SEO metadata
        print("\n[1/3] Generating SEO-optimized metadata...")
        metadata = generate_seo_metadata(
            args.image,
            args.description,
            args.purpose,
            args.audience
        )
        results["metadata"] = metadata
        
        # Save metadata
        metadata_path = save_metadata(metadata, session_dir)
        
        # Step 2: Generate product photos
        print("\n[2/3] Generating product photos...")
        photo_urls = generate_product_photos(args.image, args.description, args.num_photos)
        results["photos"] = photo_urls
        
        # Download images locally
        print("\nDownloading generated images...")
        local_photos = download_images(photo_urls, session_dir)
        
        # Step 3: Create download package
        print("\n[3/3] Creating download package...")
        zip_path = create_download_package(session_dir)
        
        # Start file server
        server_proc = start_file_server(args.port)
        
        # Get download URL (hostname will need to be adjusted for actual access)
        import socket
        hostname = socket.gethostname()
        download_url = f"http://{hostname}:{args.port}/seo_product_listing.zip"
        results["download_url"] = download_url
        
        print("\n" + "=" * 60)
        print("COMPLETE!")
        print("=" * 60)
        print(f"\nDownload URL: {download_url}")
        print(f"\nOutput files in: {session_dir}")
        
        if args.json:
            print("\n" + json.dumps(results, indent=2))
        
        return 0
        
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
