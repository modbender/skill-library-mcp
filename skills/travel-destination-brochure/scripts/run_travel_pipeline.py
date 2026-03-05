#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["requests"]
# ///
"""
Full pipeline: geocode city -> fetch OpenStreetCam photos -> fetch Commons images -> write combined manifest and images.
Usage:
  uv run scripts/run_travel_pipeline.py --city "Paris, France" --output-dir ./travel_output
  uv run scripts/run_travel_pipeline.py --city "Tokyo" --output-dir ./travel_output --max-photos 10 --max-commons 8
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

# Assumes scripts are next to this file
SCRIPT_DIR = Path(__file__).resolve().parent


def run_cmd(cmd: list, cwd: Path | None = None) -> tuple[bool, str]:
    try:
        r = subprocess.run(
            cmd,
            cwd=cwd or SCRIPT_DIR.parent,
            capture_output=True,
            text=True,
            timeout=120,
        )
        return r.returncode == 0, (r.stdout or "") + (r.stderr or "")
    except Exception as e:
        return False, str(e)


def main() -> None:
    ap = argparse.ArgumentParser(description="Run full travel brochure pipeline: geocode -> OSC -> Commons -> manifest.")
    ap.add_argument("--city", type=str, required=True, help='Destination city, e.g. "Paris, France"')
    ap.add_argument("--output-dir", type=str, default="./travel_output", help="Output directory for images and manifest")
    ap.add_argument("--radius", type=float, default=2000, help="OpenStreetCam radius in meters (default 2000)")
    ap.add_argument("--max-photos", type=int, default=15, help="Max OpenStreetCam photos (default 15)")
    ap.add_argument("--max-commons", type=int, default=10, help="Max Commons images (default 10)")
    ap.add_argument("--skip-osc", action="store_true", help="Skip OpenStreetCam fetch")
    ap.add_argument("--skip-commons", action="store_true", help="Skip Wikimedia Commons fetch")
    args = ap.parse_args()

    out_dir = Path(args.output_dir)
    images_dir = out_dir / "images"
    images_dir.mkdir(parents=True, exist_ok=True)

    # 1) Geocode
    ok, out = run_cmd([sys.executable, str(SCRIPT_DIR / "geocode_city.py"), args.city])
    if not ok:
        print(f"Geocode failed: {out}", file=sys.stderr)
        sys.exit(1)
    try:
        geocode_line = [l for l in out.strip().splitlines() if l.strip().startswith("{")][-1]
        geo = json.loads(geocode_line)
        lat = geo["lat"]
        lng = geo["lng"]
        display = geo.get("display_name", args.city)
    except (IndexError, KeyError, json.JSONDecodeError):
        print("Could not parse geocode output:", out, file=sys.stderr)
        sys.exit(1)

    all_entries = []
    prefix = 0

    # 2) OpenStreetCam
    if not args.skip_osc:
        osc_dir = out_dir / "osc"
        osc_dir.mkdir(parents=True, exist_ok=True)
        ok, out = run_cmd([
            sys.executable, str(SCRIPT_DIR / "fetch_openstreetcam.py"),
            "--lat", str(lat), "--lng", str(lng),
            "--radius", str(args.radius), "--output", str(osc_dir),
            "--max-photos", str(args.max_photos),
        ])
        if ok:
            manifest_path = osc_dir / "osc_manifest.json"
            if manifest_path.exists():
                with open(manifest_path, encoding="utf-8") as f:
                    osc_data = json.load(f)
                for p in osc_data.get("photos", []):
                    path = p.get("path")
                    if path:
                        dest = images_dir / f"img_{prefix:04d}.jpg"
                        try:
                            Path(path).replace(dest)
                        except OSError:
                            import shutil
                            shutil.copy2(path, dest)
                        all_entries.append({"path": str(dest), "source": "openstreetcam", "caption": p.get("caption", "")})
                        prefix += 1
        else:
            print(f"OpenStreetCam fetch warning: {out[:200]}", file=sys.stderr)

    # 3) Commons
    if not args.skip_commons:
        commons_dir = out_dir / "commons"
        commons_dir.mkdir(parents=True, exist_ok=True)
        query = f"{args.city} landmarks tourism"
        ok, out = run_cmd([
            sys.executable, str(SCRIPT_DIR / "fetch_commons.py"),
            "--query", query, "--output", str(commons_dir),
            "--max-images", str(args.max_commons),
        ])
        if ok:
            manifest_path = commons_dir / "commons_manifest.json"
            if manifest_path.exists():
                with open(manifest_path, encoding="utf-8") as f:
                    comm_data = json.load(f)
                for p in comm_data.get("images", []):
                    path = p.get("path")
                    if path:
                        dest = images_dir / f"img_{prefix:04d}.jpg"
                        try:
                            Path(path).replace(dest)
                        except OSError:
                            import shutil
                            shutil.copy2(path, dest)
                        all_entries.append({"path": str(dest), "source": "commons", "caption": p.get("caption", "")})
                        prefix += 1
        else:
            print(f"Commons fetch warning: {out[:200]}", file=sys.stderr)

    if not all_entries:
        print("No images collected. Check OSC/Commons outputs.", file=sys.stderr)
        sys.exit(1)

    # 4) Combined manifest
    manifest = {
        "city": args.city,
        "display_name": display,
        "lat": lat,
        "lng": lng,
        "images": all_entries,
    }
    manifest_path = out_dir / "manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    # 5) vlmrun hint file (list of paths for easy paste into CLI)
    paths_file = out_dir / "image_paths.txt"
    with open(paths_file, "w", encoding="utf-8") as f:
        for e in all_entries:
            f.write(e["path"] + "\n")

    print(json.dumps({
        "city": args.city,
        "lat": lat,
        "lng": lng,
        "image_count": len(all_entries),
        "manifest": str(manifest_path),
        "images_dir": str(images_dir),
        "image_paths_file": str(paths_file),
        "next_step": "Run vlmrun chat with -i for each image in images_dir to generate video and travel plan.",
    }, indent=2))


if __name__ == "__main__":
    main()
