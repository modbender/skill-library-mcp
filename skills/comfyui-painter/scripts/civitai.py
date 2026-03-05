#!/usr/bin/env python3
"""CivitAI integration for ComfyUI Painter skill.

Features:
- Search models by keyword, type, sort
- Get model details and version info
- Check local models for updates (by SHA256/AutoV2 hash)
- Download models directly to ComfyUI checkpoints dir
- Fetch recommended parameters for a model
"""

import json
import os
import subprocess
import sys
import urllib.request
import urllib.parse
import re
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
SKILL_DIR = SCRIPT_DIR.parent
CONFIG_PATH = SKILL_DIR / "config.json"
CREDENTIALS_DIR = Path.home() / ".openclaw" / "workspace" / "credentials"

API_BASE = "https://civitai.com/api/v1"


def _load_config():
    with open(CONFIG_PATH) as f:
        return json.load(f)


def _save_config(cfg):
    with open(CONFIG_PATH, "w") as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)


def _get_api_key():
    """Load CivitAI API key from credentials."""
    cred_file = CREDENTIALS_DIR / "civitai.md"
    if cred_file.exists():
        text = cred_file.read_text()
        for line in text.splitlines():
            if line.startswith("Token:"):
                return line.split(":", 1)[1].strip()
    return os.environ.get("CIVITAI_API_KEY", "")


def _api_get(endpoint, params=None, use_auth=False):
    """Make a GET request to CivitAI API using curl (more reliable than urllib).
    """
    url = f"{API_BASE}/{endpoint}"
    if params:
        url += "?" + urllib.parse.urlencode(params)
    
    cmd = ["curl", "-s", "--max-time", "15"]
    if use_auth:
        key = _get_api_key()
        if key:
            cmd.extend(["-H", f"Authorization: Bearer {key}"])
    
    cmd.append(url)
    
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
    if result.returncode != 0:
        raise RuntimeError(f"curl failed: {result.stderr}")
    
    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError:
        raise RuntimeError(f"Invalid JSON from {url}: {result.stdout[:200]}")
    
    # Check for error responses
    if isinstance(data, dict) and data.get("error"):
        raise RuntimeError(f"API error: {data['error']}")
    
    return data


def search(query, model_type="Checkpoint", sort="Highest Rated", period="AllTime",
           limit=10, nsfw=True):
    """Search CivitAI models.
    
    Args:
        query: Search keywords
        model_type: Checkpoint, LORA, TextualInversion, etc.
        sort: Highest Rated, Most Downloaded, Newest
        period: AllTime, Year, Month, Week, Day
        limit: Max results (1-100)
        nsfw: Include NSFW results
    
    Returns:
        List of model dicts with id, name, type, stats, versions
    """
    params = {
        "query": query,
        "types": model_type,
        "sort": sort,
        "period": period,
        "limit": limit,
        "nsfw": str(nsfw).lower(),
    }
    data = _api_get("models", params, use_auth=True)
    results = []
    for m in data.get("items", []):
        versions = []
        for v in m.get("modelVersions", [])[:5]:
            files = v.get("files", [])
            f = files[0] if files else {}
            versions.append({
                "id": v["id"],
                "name": v["name"],
                "baseModel": v.get("baseModel", "?"),
                "filename": f.get("name", "?"),
                "sizeGB": round(f.get("sizeKB", 0) / 1024 / 1024, 1),
                "downloadUrl": f.get("downloadUrl", ""),
                "publishedAt": v.get("publishedAt", "")[:10],
            })
        
        stats = m.get("stats", {})
        results.append({
            "id": m["id"],
            "name": m["name"],
            "type": m["type"],
            "tags": m.get("tags", []),
            "thumbsUp": stats.get("thumbsUpCount", 0),
            "downloads": stats.get("downloadCount", 0),
            "url": f"https://civitai.com/models/{m['id']}",
            "versions": versions,
        })
    return results


def get_model(model_id):
    """Get full model details by ID."""
    data = _api_get(f"models/{model_id}")
    return data


def get_version(version_id):
    """Get model version details."""
    return _api_get(f"model-versions/{version_id}")


def lookup_by_hash(hash_value):
    """Look up a model version by file hash (SHA256 or AutoV2).
    
    Works best with curl/no-auth. Uses AutoV2 (first 10 hex chars of SHA256 uppercase).
    """
    return _api_get(f"model-versions/by-hash/{hash_value}")


def get_autov2_hash(filepath):
    """Compute AutoV2 hash (first 10 chars of SHA256, uppercase) for a model file."""
    result = subprocess.run(
        ["sha256sum", filepath],
        capture_output=True, text=True, timeout=300
    )
    if result.returncode != 0:
        raise RuntimeError(f"sha256sum failed: {result.stderr}")
    return result.stdout.split()[0][:10].upper()


def check_updates(checkpoints_dir=None):
    """Check all local checkpoints for updates on CivitAI.
    
    Returns list of dicts: {filename, local_version, latest_version, has_update, download_url}
    """
    cfg = _load_config()
    if checkpoints_dir is None:
        checkpoints_dir = cfg["comfyui"]["output_dir_linux"].replace("/output", "/models/checkpoints/sd")
    
    results = []
    ckpt_dir = Path(checkpoints_dir)
    
    for f in sorted(ckpt_dir.glob("*.safetensors")):
        print(f"Checking {f.name}...", file=sys.stderr)
        try:
            autov2 = get_autov2_hash(str(f))
            version_data = lookup_by_hash(autov2)
            model_id = version_data.get("modelId")
            current_vid = version_data.get("id")
            current_vname = version_data.get("name", "?")
            
            # Get full model to check latest
            model_data = _api_get(f"models/{model_id}")
            latest = model_data["modelVersions"][0]
            latest_file = latest["files"][0] if latest.get("files") else {}
            
            has_update = latest["id"] != current_vid
            results.append({
                "filename": f.name,
                "model_name": model_data["name"],
                "model_id": model_id,
                "local_version": current_vname,
                "latest_version": latest["name"],
                "has_update": has_update,
                "latest_sizeGB": round(latest_file.get("sizeKB", 0) / 1024 / 1024, 1),
                "download_url": latest_file.get("downloadUrl", ""),
                "url": f"https://civitai.com/models/{model_id}",
            })
        except Exception as e:
            results.append({
                "filename": f.name,
                "error": str(e),
            })
    
    return results


def get_recommended_params(model_id):
    """Fetch recommended generation parameters from CivitAI model page.
    
    Extracts from model description and sample image metadata.
    """
    data = _api_get(f"models/{model_id}")
    latest = data["modelVersions"][0]
    
    # Extract params from sample images metadata
    params_list = []
    for img in latest.get("images", [])[:10]:
        meta = img.get("meta", {})
        if meta:
            params_list.append({
                "sampler": meta.get("sampler", ""),
                "steps": meta.get("steps", ""),
                "cfg": meta.get("cfgScale", ""),
                "size": meta.get("Size", ""),
                "negative": meta.get("negativePrompt", ""),
                "hires_upscaler": meta.get("Hires upscaler", ""),
                "hires_steps": meta.get("Hires steps", ""),
                "hires_upscale": meta.get("Hires upscale", ""),
                "denoising": meta.get("Denoising strength", ""),
                "scheduler": meta.get("Schedule type", ""),
                "prompt": meta.get("prompt", "")[:200],
            })
    
    # Aggregate most common params
    if not params_list:
        return {"error": "No sample metadata found"}
    
    # Find most common values
    from collections import Counter
    agg = {}
    for key in ["sampler", "steps", "cfg", "scheduler"]:
        values = [p[key] for p in params_list if p[key]]
        if values:
            most_common = Counter(values).most_common(1)[0][0]
            agg[key] = most_common
    
    # Get common negative prompt
    negs = [p["negative"] for p in params_list if p["negative"]]
    if negs:
        agg["negative_prompt"] = Counter(negs).most_common(1)[0][0]
    
    # Get common size
    sizes = [p["size"] for p in params_list if p["size"]]
    if sizes:
        agg["size"] = Counter(sizes).most_common(1)[0][0]
    
    agg["model_name"] = data["name"]
    agg["model_id"] = model_id
    agg["samples_analyzed"] = len(params_list)
    
    return agg


def download_model(url, dest_dir=None, filename=None):
    """Download a model from CivitAI.
    
    Args:
        url: CivitAI download URL
        dest_dir: Destination directory (default: checkpoints/sd)
        filename: Override filename (auto-detected from headers if None)
    
    Returns:
        Path to downloaded file
    """
    cfg = _load_config()
    if dest_dir is None:
        dest_dir = cfg["comfyui"]["output_dir_linux"].replace("/output", "/models/checkpoints/sd")
    
    api_key = _get_api_key()
    
    # Use curl for reliable downloads with progress
    cmd = ["curl", "-L", "-#", "-o"]
    
    if filename:
        dest = os.path.join(dest_dir, filename + ".tmp")
        final = os.path.join(dest_dir, filename)
    else:
        # Download to temp, detect filename from headers
        dest = os.path.join(dest_dir, "download.tmp")
        final = None
    
    cmd.append(dest)
    
    if api_key:
        cmd.extend(["-H", f"Authorization: Bearer {api_key}"])
    
    cmd.append(url)
    
    print(f"Downloading to {dest}...", file=sys.stderr)
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)
    
    if result.returncode != 0:
        raise RuntimeError(f"Download failed: {result.stderr}")
    
    if final:
        os.rename(dest, final)
        return final
    
    return dest


# CLI interface
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="CivitAI integration for ComfyUI Painter")
    sub = parser.add_subparsers(dest="command")
    
    # search
    s = sub.add_parser("search", help="Search models")
    s.add_argument("query", help="Search keywords")
    s.add_argument("--type", default="Checkpoint")
    s.add_argument("--sort", default="Highest Rated")
    s.add_argument("--limit", type=int, default=5)
    
    # info
    i = sub.add_parser("info", help="Get model info")
    i.add_argument("model_id", type=int)
    
    # params
    p = sub.add_parser("params", help="Get recommended params")
    p.add_argument("model_id", type=int)
    
    # check-updates
    sub.add_parser("check-updates", help="Check local models for updates")
    
    # download
    d = sub.add_parser("download", help="Download a model")
    d.add_argument("url", help="Download URL")
    d.add_argument("--filename", help="Override filename")
    
    args = parser.parse_args()
    
    if args.command == "search":
        results = search(args.query, model_type=args.type, sort=args.sort, limit=args.limit)
        print(json.dumps(results, indent=2, ensure_ascii=False))
    
    elif args.command == "info":
        data = get_model(args.model_id)
        # Simplified output
        s = data.get("stats", {})
        print(f"Name: {data['name']}")
        print(f"Type: {data['type']}")
        print(f"Downloads: {s.get('downloadCount', 0)}")
        print(f"Likes: {s.get('thumbsUpCount', 0)}")
        print(f"Tags: {', '.join(data.get('tags', []))}")
        print(f"\nVersions:")
        for v in data.get("modelVersions", [])[:8]:
            f = v.get("files", [{}])[0] if v.get("files") else {}
            print(f"  v{v['name']} | {v.get('baseModel','?')} | {f.get('name','?')} | {v.get('publishedAt','')[:10]}")
    
    elif args.command == "params":
        result = get_recommended_params(args.model_id)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    elif args.command == "check-updates":
        results = check_updates()
        for r in results:
            if "error" in r:
                print(f"❌ {r['filename']}: {r['error']}")
            elif r["has_update"]:
                print(f"🆕 {r['model_name']}: {r['local_version']} → {r['latest_version']}")
                print(f"   ⬇️ {r['download_url']}")
            else:
                print(f"✅ {r['model_name']}: {r['local_version']} — up to date")
    
    else:
        parser.print_help()
