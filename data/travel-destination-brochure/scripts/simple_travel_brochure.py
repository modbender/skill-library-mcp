#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["requests"]
# ///
"""
Simplified travel brochure generator: gets 5 images and generates video with vlmrun.
Usage:
  uv run scripts/simple_travel_brochure.py --city "Doha, Qatar"
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
import requests

SCRIPT_DIR = Path(__file__).resolve().parent
OSC_BASE = "https://api.openstreetcam.org"
OSC_PHOTO_BASE = "https://api.openstreetcam.org/"
NEARBY_PHOTOS = f"{OSC_BASE}/1.0/list/nearby-photos/"
COMMONS_API = "https://commons.wikimedia.org/w/api.php"
NOMINATIM = "https://nominatim.openstreetmap.org/search"
HEADERS = {"User-Agent": "TravelBrochureSkill/1.0"}


def geocode_city(city: str) -> dict:
    """Geocode city name to lat/lng."""
    params = {"q": city, "format": "json", "limit": 1}
    r = requests.get(NOMINATIM, params=params, headers=HEADERS, timeout=30)
    r.raise_for_status()
    results = r.json()
    if not results:
        raise ValueError(f"City not found: {city}")
    return {
        "lat": float(results[0]["lat"]),
        "lng": float(results[0]["lon"]),
        "display_name": results[0].get("display_name", city)
    }


def fetch_osc_photos(lat: float, lng: float, count: int = 3) -> list:
    """Fetch OpenStreetCam photos."""
    data = {"lat": lat, "lng": lng, "radius": 3000, "page": 1, "ipp": count + 5}
    r = requests.post(NEARBY_PHOTOS, data=data, headers=HEADERS, timeout=30)
    r.raise_for_status()
    resp = r.json()

    raw_items = resp.get("currentPageItems") or resp.get("result") or []
    if isinstance(raw_items, dict):
        items = raw_items.get("data", [])
    else:
        items = raw_items

    photos = []
    for item in items:
        if isinstance(item, dict):
            url = item.get("lth_name") or item.get("name") or item.get("th_name")
            if url:
                if not url.startswith("http"):
                    url = OSC_PHOTO_BASE + url
                photos.append({
                    "url": url,
                    "caption": f"Street view at {item.get('lat')}, {item.get('lng')}"
                })
        if len(photos) >= count:
            break

    return photos[:count]


def fetch_commons_images(query: str, count: int = 2) -> list:
    """Fetch Wikimedia Commons images."""
    # Search for files
    search_params = {
        "action": "query",
        "list": "search",
        "srsearch": query,
        "srnamespace": 6,
        "srlimit": count + 10,
        "format": "json"
    }
    r = requests.get(COMMONS_API, params=search_params, headers=HEADERS, timeout=30)
    r.raise_for_status()
    search_results = r.json()

    titles = [item["title"] for item in search_results.get("query", {}).get("search", [])][:count + 5]
    if not titles:
        return []

    # Get image info
    info_params = {
        "action": "query",
        "titles": "|".join(titles),
        "prop": "imageinfo",
        "iiprop": "url|extmetadata",
        "format": "json"
    }
    r = requests.get(COMMONS_API, params=info_params, headers=HEADERS, timeout=30)
    r.raise_for_status()
    info_resp = r.json()

    images = []
    pages = info_resp.get("query", {}).get("pages", {})
    for pid, page in pages.items():
        if pid == "-1" or "missing" in page:
            continue
        ii = (page.get("imageinfo") or [None])[0]
        if not ii:
            continue
        url = ii.get("url")
        if not url or url.lower().endswith(".pdf"):
            continue

        extmeta = ii.get("extmetadata") or {}
        desc = (extmeta.get("ImageDescription") or {}).get("value") or ""
        obj = (extmeta.get("ObjectName") or {}).get("value") or ""
        caption = (obj or desc or page.get("title", "")).replace("File:", "").strip()
        if len(caption) > 200:
            caption = caption[:197] + "..."

        images.append({"url": url, "caption": caption})
        if len(images) >= count:
            break

    return images[:count]


def download_image(url: str, path: Path) -> bool:
    """Download image to path."""
    try:
        r = requests.get(url, headers=HEADERS, timeout=30, stream=True)
        r.raise_for_status()
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
        return True
    except Exception as e:
        print(f"Download failed for {url}: {e}", file=sys.stderr)
        return False


def generate_video(images_dir: Path, city: str, output_dir: Path) -> bool:
    """Generate travel video using vlmrun."""
    image_files = sorted(images_dir.glob("*.jpg"))[:5]
    if not image_files:
        print("No images found to generate video", file=sys.stderr)
        return False

    # Build vlmrun command
    prompt = f"Create a 30-second travel video showcasing {city}. Use these images to highlight the city's beauty and culture. Add smooth transitions and subtle captions. Use an inspiring, calm travel documentary style."

    cmd = ["vlmrun", "chat", prompt]
    for img in image_files:
        cmd.extend(["-i", str(img)])
    cmd.extend(["-o", str(output_dir / "video")])

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        if result.returncode == 0:
            print("   Video generated successfully!")
            return True
        else:
            # Check if it's an API key error
            if "API key not found" in result.stderr:
                print("   Skipped: VLMRUN_API_KEY not set", file=sys.stderr)
            else:
                print(f"   Error: vlmrun failed (code {result.returncode})", file=sys.stderr)
            return False
    except FileNotFoundError:
        print("   Skipped: vlmrun not installed", file=sys.stderr)
        return False
    except Exception as e:
        print(f"   Error: {e}", file=sys.stderr)
        return False


def generate_travel_plan(images_dir: Path, city: str, output_dir: Path) -> bool:
    """Generate travel plan using vlmrun."""
    image_files = sorted(images_dir.glob("*.jpg"))[:5]
    if not image_files:
        return False

    prompt = f"Based on these images of {city}, create a detailed one-day travel plan with morning, midday, and evening activities. Include specific places to visit, local tips, and practical recommendations. Format as structured markdown."

    cmd = ["vlmrun", "chat", prompt]
    for img in image_files:
        cmd.extend(["-i", str(img)])
    cmd.extend(["-o", str(output_dir)])

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        if result.returncode == 0:
            # Save the plan
            plan_file = output_dir / "travel_plan.md"
            with open(plan_file, "w", encoding="utf-8") as f:
                f.write(result.stdout)
            print(f"   Travel plan saved to {plan_file}")
            return True
        else:
            # Check if it's an API key error
            if "API key not found" in result.stderr:
                print("   Skipped: VLMRUN_API_KEY not set", file=sys.stderr)
            else:
                print(f"   Error: vlmrun failed (code {result.returncode})", file=sys.stderr)
            return False
    except FileNotFoundError:
        print("   Skipped: vlmrun not installed", file=sys.stderr)
        return False
    except Exception as e:
        print(f"   Error: {e}", file=sys.stderr)
        return False


def cleanup_temp_files(temp_dir: Path):
    """Remove temporary files."""
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
        print(f"Cleaned up temporary files in {temp_dir}")


def main():
    ap = argparse.ArgumentParser(description="Generate travel brochure with 5 images and video")
    ap.add_argument("--city", type=str, required=True, help='City name, e.g. "Doha, Qatar"')
    ap.add_argument("--output", type=str, default="./travel_brochure", help="Output directory")
    ap.add_argument("--osc-count", type=int, default=3, help="Number of OpenStreetCam photos (default 3)")
    ap.add_argument("--commons-count", type=int, default=2, help="Number of Commons images (default 2)")
    args = ap.parse_args()

    output_dir = Path(args.output)
    images_dir = output_dir / "images"
    images_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n[*] Generating travel brochure for: {args.city}")

    # Step 1: Geocode
    print("[1/5] Geocoding city...")
    try:
        geo = geocode_city(args.city)
        # Try to print display name, but skip if encoding issues
        try:
            print(f"   Found: {geo['display_name']}")
        except UnicodeEncodeError:
            print(f"   Found: {args.city} (lat: {geo['lat']:.4f}, lng: {geo['lng']:.4f})")
    except Exception as e:
        print(f"ERROR: Geocoding failed: {e}", file=sys.stderr)
        sys.exit(1)

    # Step 2: Fetch images
    print(f"[2/5] Fetching {args.osc_count} street photos from OpenStreetCam...")
    try:
        osc_photos = fetch_osc_photos(geo["lat"], geo["lng"], args.osc_count)
        print(f"   Got {len(osc_photos)} photos")
    except Exception as e:
        print(f"WARNING: OpenStreetCam failed: {e}", file=sys.stderr)
        osc_photos = []

    print(f"[2/5] Fetching {args.commons_count} landmark images from Wikimedia Commons...")
    try:
        commons_images = fetch_commons_images(f"{args.city} landmarks", args.commons_count)
        print(f"   Got {len(commons_images)} images")
    except Exception as e:
        print(f"WARNING: Commons failed: {e}", file=sys.stderr)
        commons_images = []

    # Step 3: Download images
    all_images = osc_photos + commons_images
    if len(all_images) < 3:
        print(f"ERROR: Not enough images collected ({len(all_images)}), need at least 3", file=sys.stderr)
        sys.exit(1)

    print(f"[3/5] Downloading {len(all_images)} images...")
    downloaded = 0
    for i, img in enumerate(all_images[:5]):
        dest = images_dir / f"image_{i:02d}.jpg"
        if download_image(img["url"], dest):
            downloaded += 1
            print(f"   [OK] Image {i+1}/5")

    if downloaded < 3:
        print(f"ERROR: Only downloaded {downloaded} images, need at least 3", file=sys.stderr)
        sys.exit(1)

    print(f"\nSuccessfully downloaded {downloaded} images")

    # Step 4: Generate video
    print("[4/5] Generating travel video with vlmrun...")
    video_success = generate_video(images_dir, args.city, output_dir)

    # Step 5: Generate travel plan
    print("[5/5] Generating travel plan with vlmrun...")
    plan_success = generate_travel_plan(images_dir, args.city, output_dir)

    # Step 6: Save manifest
    manifest = {
        "city": args.city,
        "display_name": geo["display_name"],
        "lat": geo["lat"],
        "lng": geo["lng"],
        "images": [{"path": str(p), "caption": all_images[i].get("caption", "")}
                   for i, p in enumerate(sorted(images_dir.glob("*.jpg"))[:5])],
        "video_generated": video_success,
        "plan_generated": plan_success
    }

    manifest_file = output_dir / "manifest.json"
    with open(manifest_file, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    # Step 7: Cleanup (optional - remove intermediate API response files if any)
    # Images are kept in output_dir/images/

    print(f"\nDone! Results saved to: {output_dir.resolve()}")
    print(f"   Manifest: {manifest_file}")
    if video_success:
        print(f"   Video: {output_dir / 'video'}")
    if plan_success:
        print(f"   Travel plan: {output_dir / 'travel_plan.md'}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
