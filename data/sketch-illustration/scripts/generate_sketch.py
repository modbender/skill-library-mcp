#!/usr/bin/env python3
"""
Generate a sketch-style illustration using ZenMux Imagen 3 API.
"""

import argparse
import base64
import json
import os
import sys
import urllib.request

ZENMUX_BASE_URL = "https://zenmux.ai/api/v1"
DEFAULT_MODEL = "google/gemini-3-pro-image-preview"


def generate_image(prompt: str, output_path: str, model: str = DEFAULT_MODEL) -> bool:
    api_key = os.environ.get("ZENMUX_API_KEY")
    if not api_key:
        # Try reading from openclaw.json
        config_path = os.path.expanduser("~/.openclaw/openclaw.json")
        try:
            with open(config_path) as f:
                config = json.load(f)
            api_key = config["models"]["providers"]["ZenMux"]["apiKey"]
        except Exception as e:
            print(f"Error: Could not find ZENMUX_API_KEY. Set env var or check openclaw.json. {e}")
            return False

    payload = {
        "model": model,
        "input": prompt,
        "modalities": ["text", "image"],
    }

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        f"{ZENMUX_BASE_URL}/responses",
        data=data,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    print(f"Generating image with model: {model}")
    try:
        with urllib.request.urlopen(req) as resp:
            status = resp.status
            body = resp.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        print(f"HTTP Error {e.code}: {e.read().decode()}")
        return False

    if status != 200:
        print(f"Error: status {status}\n{body}")
        return False

    result = json.loads(body)

    # Extract image from response
    image_data = None
    for item in result.get("output", []):
        if item.get("type") == "image_generation_call":
            image_data = item.get("result")
            break
        for content in item.get("content", []):
            if content.get("type") == "image_url":
                url = content["image_url"]["url"]
                if url.startswith("data:"):
                    image_data = url.split(",", 1)[1]
                    break
            elif content.get("type") == "image":
                image_data = content.get("data") or content.get("image_url", {}).get("url", "").split(",", 1)[-1]
                break

    if not image_data:
        print(f"Error: No image found in response.\n{body[:500]}")
        return False

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with open(output_path, "wb") as f:
        f.write(base64.b64decode(image_data))

    print(f"Success! Image saved to: {output_path}")
    return True


def main():
    parser = argparse.ArgumentParser(description="Generate sketch illustration via ZenMux Imagen 3")
    parser.add_argument("--prompt", required=True, help="Image generation prompt")
    parser.add_argument("--output", default="/root/myfiles/sketch_output.png", help="Output file path")
    parser.add_argument("--model", default=DEFAULT_MODEL, help="Model to use")
    args = parser.parse_args()

    success = generate_image(args.prompt, args.output, args.model)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
