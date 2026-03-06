#!/usr/bin/env python3
"""
Generate an image via Runware.ai Images API and save to Downloads.
Usage:
  python generate_image.py --prompt "..." [--outfile NAME] [--size 1024x1024] [--sync]

This script requires the RUNWARE_API_KEY environment variable to be set.
It calls Runware's task-based imageInference API and supports sync and async modes.
"""
import argparse
import base64
import json
import os
import sys
import uuid
from pathlib import Path

import requests
from dotenv import load_dotenv

HERE = Path(__file__).resolve().parent.parent
CONFIG_PATH = HERE / "skill-config.json"
ENV_PATH = HERE / ".env"

load_dotenv(ENV_PATH)


def load_api_key():
    v = os.getenv("RUNWARE_API_KEY")
    if v:
        return v
    # Prompt the user for the API key if not present in the environment
    try:
        from getpass import getpass
        prompt = "Runware API key not found in environment. Enter your Runware API key (input hidden): "
        v = getpass(prompt)
        if v:
            return v
    except Exception:
        pass
    raise RuntimeError("Runware API key not provided. Set RUNWARE_API_KEY environment variable or enter it when prompted.")


def save_output_image(b64_data: str, out_path: Path):
    img = base64.b64decode(b64_data)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_bytes(img)


def validate_prompt(prompt: str):
    # Simple safety: if the prompt mentions teenage/minor words, reject.
    ban_words = ["teen", "teenage", "minor", "13", "14", "15", "16", "17", "18", "19"]
    low = prompt.lower()
    for w in ban_words:
        if w in low:
            raise RuntimeError("Prompt appears to reference a minor. Please confirm subject is 21+ and retry.")


def call_runware_generate(api_key: str, prompt: str, size: str = "1024x1024", output_format: str = "PNG", sync: bool = True, number_results: int = 1) -> dict:
    """Call Runware task API and return the parsed JSON response."""
    url = "https://api.runware.ai/v1/tasks"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    task_obj = {
        "taskType": "imageInference",
        "taskUUID": str(uuid.uuid4()),
        "outputType": "base64Data",
        "outputFormat": output_format.lower(),
        "positivePrompt": prompt,
        "height": int(size.split("x")[1]) if "x" in size else 1024,
        "width": int(size.split("x")[0]) if "x" in size else 1024,
        "model": "runware:101@1",
        "steps": 30,
        "CFGScale": 7.5,
        "numberResults": number_results,
    }
    payload = [task_obj]
    resp = requests.post(url, json=payload, headers=headers, timeout=120)
    resp.raise_for_status()
    return resp.json()


def extract_base64_from_response(resp_json: dict) -> str:
    # Runware returns an array-style response for tasks; search for expected fields.
    # Common return fields: imageBase64Data, imageDataURI, imageURL, imageBase64
    if isinstance(resp_json, dict):
        # Some responses wrap in 'results' or 'items'
        candidates = []
        for key in ("imageBase64Data", "imageBase64", "image_base64", "imageBase64Data"):
            if key in resp_json:
                return resp_json[key]
        # check common nested shapes
        for container in ("results", "items", "data"):
            if container in resp_json and isinstance(resp_json[container], list):
                for item in resp_json[container]:
                    if isinstance(item, dict):
                        for key in ("imageBase64Data", "imageBase64", "image_base64", "imageDataURI"):
                            if key in item:
                                val = item[key]
                                # if dataURI, strip prefix
                                if key == "imageDataURI" and isinstance(val, str) and val.startswith("data:"):
                                    return val.split(",", 1)[1]
                                return val
    # try pulling from first element if array
    if isinstance(resp_json, list) and len(resp_json) > 0:
        first = resp_json[0]
        if isinstance(first, dict):
            for key in ("imageBase64Data", "imageBase64", "image_base64", "imageDataURI", "imageURL"):
                if key in first:
                    val = first[key]
                    if key == "imageDataURI" and isinstance(val, str) and val.startswith("data:"):
                        return val.split(",", 1)[1]
                    return val
    raise RuntimeError(f"Couldn't find base64 image in response: {resp_json}")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--prompt", required=True)
    p.add_argument("--outfile", default=None, help="Output filename (saved to Downloads if not an absolute path)")
    p.add_argument("--size", default=None)
    p.add_argument("--sync", action="store_true", help="Request synchronous delivery (wait for result in response). If not set, an async/task id may be returned and you must poll or use webhooks.")
    args = p.parse_args()

    prompt = args.prompt
    validate_prompt(prompt)

    api_key = load_api_key()
    cfg = json.loads(CONFIG_PATH.read_text()) if CONFIG_PATH.exists() else {}
    size = args.size or cfg.get("default_size", "1024x1024")
    out_format = cfg.get("default_format", "png")

    print("Sending task to Runware...")
    resp = call_runware_generate(api_key, prompt, size=size, output_format=out_format.upper(), sync=args.sync)

    # Extract base64 image data
    b64 = extract_base64_from_response(resp)

    # Determine output directory and path. Default to config.default_output_dir (~\runware_images)
    default_dir = cfg.get("default_output_dir", "~\\runware_images")
    last_dir = cfg.get("last_output_dir")

    def slugify(s: str, max_len: int = 50):
        # simple slug: keep alnum and replace others with underscore, collapse underscores
        import re
        s = s.lower()
        s = re.sub(r"[^a-z0-9]+", "_", s)
        s = re.sub(r"_+", "_", s).strip("_")
        if len(s) > max_len:
            s = s[:max_len].rstrip("_")
        return s or "image"

    ext = out_format.lower()

    if args.outfile:
        # Expand user (~) and environment variables (%VAR%)
        outfile_expanded = os.path.expandvars(args.outfile)
        outfile_expanded = os.path.expanduser(outfile_expanded)
        out = Path(outfile_expanded)
        
        if not out.is_absolute():
            base_dir = Path(last_dir) if last_dir else Path(default_dir).expanduser()
            base_dir = base_dir.expanduser()
            base_dir.mkdir(parents=True, exist_ok=True)
            out = base_dir / out
        else:
            # if absolute path, ensure parent exists
            out.parent.mkdir(parents=True, exist_ok=True)
        # remember the directory for next time
        try:
            cfg["last_output_dir"] = str(out.parent)
            CONFIG_PATH.write_text(json.dumps(cfg, indent=2))
        except Exception:
            pass
    else:
        out_dir = Path(last_dir).expanduser() if last_dir else Path(default_dir).expanduser()
        out_dir.mkdir(parents=True, exist_ok=True)
        # create filename from prompt
        slug = slugify(prompt)
        from datetime import datetime
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{slug}_{ts}.{ext}"
        out = out_dir / filename
        # remember the directory for next time
        try:
            cfg["last_output_dir"] = str(out_dir)
            CONFIG_PATH.write_text(json.dumps(cfg, indent=2))
        except Exception:
            pass

    save_output_image(b64, out)
    print(f"Saved image to: {out}")


if __name__ == "__main__":
    main()
