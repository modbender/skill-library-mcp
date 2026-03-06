import sys
import json
import requests
import os
import argparse
import base64
import mimetypes

BASE_URL = "https://dashscope.aliyuncs.com"


def get_api_key():
    api_key = os.environ.get("DASHSCOPE_API_KEY")
    if not api_key:
        print("Error: DASHSCOPE_API_KEY environment variable is not set.", file=sys.stderr)
        sys.exit(1)
    return api_key


def encode_local_image(path):
    """If path is a local file, return a data URI (data:{mime};base64,...).
    Otherwise return the original string (assumed to be a URL)."""
    if path.startswith(("http://", "https://", "oss://", "data:")):
        return path
    abs_path = os.path.expanduser(path)
    if not os.path.isfile(abs_path):
        print(f"Error: file not found: {abs_path}", file=sys.stderr)
        sys.exit(1)
    mime, _ = mimetypes.guess_type(abs_path)
    if mime is None:
        mime = "image/png"  # fallback
    with open(abs_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")
    print(f"  [base64] Encoded local file: {abs_path} ({mime}, {len(b64)} chars)")
    return f"data:{mime};base64,{b64}"


def get_headers(api_key, async_mode=False):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }
    if async_mode:
        headers["X-DashScope-Async"] = "enable"
    return headers


# ──────────────────────────────────────────────
#  text2image  (wan2.6-t2i, HTTP sync)
# ──────────────────────────────────────────────
def text2image(args):
    api_key = get_api_key()
    url = f"{BASE_URL}/api/v1/services/aigc/multimodal-generation/generation"

    payload = {
        "model": "wan2.6-t2i",
        "input": {
            "messages": [
                {
                    "role": "user",
                    "content": [{"text": args.prompt}],
                }
            ]
        },
        "parameters": {
            "size": args.size,
            "n": args.quantity,
            "prompt_extend": True,
            "watermark": False,
        },
    }

    headers = get_headers(api_key)

    print(f"[text2image] Generating image …")
    print(f"  Prompt  : {args.prompt}")
    print(f"  Size    : {args.size}")
    print(f"  Quantity: {args.quantity}")

    resp = requests.post(url, headers=headers, json=payload, timeout=300)
    result = resp.json()

    if "code" in result:
        print(f"Error: {result.get('code')} - {result.get('message')}", file=sys.stderr)
        sys.exit(1)

    choices = result.get("output", {}).get("choices", [])
    image_urls = []
    for choice in choices:
        for item in choice.get("message", {}).get("content", []):
            if "image" in item:
                image_urls.append(item["image"])

    print(f"\nGenerated {len(image_urls)} image(s):")
    for i, u in enumerate(image_urls, 1):
        print(f"  [{i}] {u}")

    print("\n--- Full Response ---")
    print(json.dumps(result, ensure_ascii=False, indent=2))


# ──────────────────────────────────────────────
#  image-edit  (wan2.6-image, HTTP sync)
# ──────────────────────────────────────────────
def image_edit(args):
    api_key = get_api_key()
    url = f"{BASE_URL}/api/v1/services/aigc/multimodal-generation/generation"

    content = [{"text": args.prompt}]
    for img_url in args.images:
        content.append({"image": encode_local_image(img_url)})

    payload = {
        "model": "wan2.6-image",
        "input": {
            "messages": [
                {
                    "role": "user",
                    "content": content,
                }
            ]
        },
        "parameters": {
            "size": args.size,
            "n": args.quantity,
            "prompt_extend": True,
            "watermark": False,
            "enable_interleave": False,
        },
    }

    headers = get_headers(api_key)

    print(f"[image-edit] Editing image …")
    print(f"  Prompt  : {args.prompt}")
    print(f"  Images  : {args.images}")
    print(f"  Size    : {args.size}")
    print(f"  Quantity: {args.quantity}")

    resp = requests.post(url, headers=headers, json=payload, timeout=300)
    result = resp.json()

    if "code" in result:
        print(f"Error: {result.get('code')} - {result.get('message')}", file=sys.stderr)
        sys.exit(1)

    choices = result.get("output", {}).get("choices", [])
    image_urls = []
    for choice in choices:
        for item in choice.get("message", {}).get("content", []):
            if "image" in item:
                image_urls.append(item["image"])

    print(f"\nGenerated {len(image_urls)} image(s):")
    for i, u in enumerate(image_urls, 1):
        print(f"  [{i}] {u}")

    print("\n--- Full Response ---")
    print(json.dumps(result, ensure_ascii=False, indent=2))


# ──────────────────────────────────────────────
#  text2video-gen  (wan2.6-t2v, HTTP async)
# ──────────────────────────────────────────────
def text2video_gen(args):
    api_key = get_api_key()
    url = f"{BASE_URL}/api/v1/services/aigc/video-generation/video-synthesis"

    payload = {
        "model": "wan2.6-t2v",
        "input": {
            "prompt": args.prompt,
        },
        "parameters": {
            "size": args.size,
            "duration": args.duration,
            "prompt_extend": True,
        },
    }

    headers = get_headers(api_key, async_mode=True)

    print(f"[text2video-gen] Submitting task …")
    print(f"  Prompt  : {args.prompt}")
    print(f"  Size    : {args.size}")
    print(f"  Duration: {args.duration}s")

    resp = requests.post(url, headers=headers, json=payload, timeout=60)
    result = resp.json()

    if "code" in result:
        print(f"Error: {result.get('code')} - {result.get('message')}", file=sys.stderr)
        sys.exit(1)

    output = result.get("output", {})
    task_id = output.get("task_id", "")
    task_status = output.get("task_status", "")

    print(f"\nTask submitted successfully!")
    print(f"  Task ID : {task_id}")
    print(f"  Status  : {task_status}")
    print(f"\nTo check the result, run:")
    print(f"  python3 wan-magic.py text2video-get --task-id {task_id}")

    print("\n--- Full Response ---")
    print(json.dumps(result, ensure_ascii=False, indent=2))


# ──────────────────────────────────────────────
#  text2video-get  (poll async task)
# ──────────────────────────────────────────────
def text2video_get(args):
    api_key = get_api_key()
    url = f"{BASE_URL}/api/v1/tasks/{args.task_id}"
    headers = {"Authorization": f"Bearer {api_key}"}

    print(f"[text2video-get] Checking task: {args.task_id}")

    resp = requests.get(url, headers=headers, timeout=60)
    result = resp.json()

    if "code" in result:
        print(f"Error: {result.get('code')} - {result.get('message')}", file=sys.stderr)
        sys.exit(1)

    output = result.get("output", {})
    task_status = output.get("task_status", "")

    print(f"  Task ID : {output.get('task_id', '')}")
    print(f"  Status  : {task_status}")

    if task_status == "SUCCEEDED":
        video_url = output.get("video_url", "")
        print(f"  Video   : {video_url}")
    elif task_status == "FAILED":
        print(f"  Error   : {output.get('code', '')} - {output.get('message', '')}")
    else:
        print(f"\nTask is still {task_status}. Please check again later:")
        print(f"  python3 wan-magic.py text2video-get --task-id {args.task_id}")

    print("\n--- Full Response ---")
    print(json.dumps(result, ensure_ascii=False, indent=2))


# ──────────────────────────────────────────────
#  image2video-gen  (wan2.6-i2v-flash, HTTP async)
# ──────────────────────────────────────────────
def image2video_gen(args):
    api_key = get_api_key()
    url = f"{BASE_URL}/api/v1/services/aigc/video-generation/video-synthesis"

    img_value = encode_local_image(args.image)

    payload = {
        "model": "wan2.6-i2v-flash",
        "input": {
            "prompt": args.prompt,
            "img_url": img_value,
        },
        "parameters": {
            "resolution": args.resolution,
            "duration": args.duration,
            "prompt_extend": True,
        },
    }

    headers = get_headers(api_key, async_mode=True)

    print(f"[image2video-gen] Submitting task …")
    print(f"  Prompt    : {args.prompt}")
    print(f"  Image     : {args.image}")
    print(f"  Resolution: {args.resolution}")
    print(f"  Duration  : {args.duration}s")

    resp = requests.post(url, headers=headers, json=payload, timeout=60)
    result = resp.json()

    if "code" in result:
        print(f"Error: {result.get('code')} - {result.get('message')}", file=sys.stderr)
        sys.exit(1)

    output = result.get("output", {})
    task_id = output.get("task_id", "")
    task_status = output.get("task_status", "")

    print(f"\nTask submitted successfully!")
    print(f"  Task ID : {task_id}")
    print(f"  Status  : {task_status}")
    print(f"\nTo check the result, run:")
    print(f"  python3 wan-magic.py image2video-get --task-id {task_id}")

    print("\n--- Full Response ---")
    print(json.dumps(result, ensure_ascii=False, indent=2))


# ──────────────────────────────────────────────
#  image2video-get  (poll async task)
# ──────────────────────────────────────────────
def image2video_get(args):
    api_key = get_api_key()
    url = f"{BASE_URL}/api/v1/tasks/{args.task_id}"
    headers = {"Authorization": f"Bearer {api_key}"}

    print(f"[image2video-get] Checking task: {args.task_id}")

    resp = requests.get(url, headers=headers, timeout=60)
    result = resp.json()

    if "code" in result:
        print(f"Error: {result.get('code')} - {result.get('message')}", file=sys.stderr)
        sys.exit(1)

    output = result.get("output", {})
    task_status = output.get("task_status", "")

    print(f"  Task ID : {output.get('task_id', '')}")
    print(f"  Status  : {task_status}")

    if task_status == "SUCCEEDED":
        video_url = output.get("video_url", "")
        print(f"  Video   : {video_url}")
    elif task_status == "FAILED":
        print(f"  Error   : {output.get('code', '')} - {output.get('message', '')}")
    else:
        print(f"\nTask is still {task_status}. Please check again later:")
        print(f"  python3 wan-magic.py image2video-get --task-id {args.task_id}")

    print("\n--- Full Response ---")
    print(json.dumps(result, ensure_ascii=False, indent=2))


# ──────────────────────────────────────────────
#  CLI entry point
# ──────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="Wan Models Magic - Image & Video Generation / Editing Tool"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # --- text2image ---
    p = subparsers.add_parser("text2image", help="Generate images from text (wan2.6-t2i)")
    p.add_argument("--prompt", required=True, help="Text prompt for image generation")
    p.add_argument("--size", default="1280*1280", help="Image resolution WxH (default: 1280*1280)")
    p.add_argument("--quantity", type=int, default=1, help="Number of images, 1-4 (default: 1)")

    # --- image-edit ---
    p = subparsers.add_parser("image-edit", help="Edit images with text prompt (wan2.6-image)")
    p.add_argument("--prompt", required=True, help="Text prompt for image editing")
    p.add_argument("--images", nargs="+", required=True, help="Input image URLs or local file paths (1-4 images)")
    p.add_argument("--size", default="1280*1280", help="Output image resolution WxH (default: 1280*1280)")
    p.add_argument("--quantity", type=int, default=1, help="Number of output images, 1-4 (default: 1)")

    # --- text2video-gen ---
    p = subparsers.add_parser("text2video-gen", help="Submit text-to-video task (wan2.6-t2v)")
    p.add_argument("--prompt", required=True, help="Text prompt for video generation")
    p.add_argument("--size", default="1920*1080", help="Video resolution WxH (default: 1920*1080)")
    p.add_argument("--duration", type=int, default=5, help="Video duration in seconds, 1-15 (default: 5)")

    # --- text2video-get ---
    p = subparsers.add_parser("text2video-get", help="Get text-to-video task result")
    p.add_argument("--task-id", required=True, help="Task ID from text2video-gen")

    # --- image2video-gen ---
    p = subparsers.add_parser("image2video-gen", help="Submit image-to-video task (wan2.6-i2v-flash)")
    p.add_argument("--prompt", required=True, help="Text prompt for video generation")
    p.add_argument("--image", required=True, help="Input image URL or local file path as first frame")
    p.add_argument("--resolution", default="1080P", help="Video resolution: 720P or 1080P (default: 1080P)")
    p.add_argument("--duration", type=int, default=5, help="Video duration in seconds, 1-15 (default: 5)")

    # --- image2video-get ---
    p = subparsers.add_parser("image2video-get", help="Get image-to-video task result")
    p.add_argument("--task-id", required=True, help="Task ID from image2video-gen")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    command_map = {
        "text2image": text2image,
        "image-edit": image_edit,
        "text2video-gen": text2video_gen,
        "text2video-get": text2video_get,
        "image2video-gen": image2video_gen,
        "image2video-get": image2video_get,
    }

    handler = command_map.get(args.command)
    if handler:
        handler(args)
    else:
        print(f"Unknown command: {args.command}", file=sys.stderr)
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
