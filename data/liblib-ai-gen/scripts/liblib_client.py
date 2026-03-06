#!/usr/bin/env python3
"""LiblibAI API client for image generation (Seedream4.5) and video generation (Kling)."""

import hmac
import hashlib
import base64
import time
import uuid
import json
import os
import sys
import argparse
import requests

BASE_URL = "https://openapi.liblibai.cloud"


def make_sign(uri: str, access_key: str, secret_key: str) -> dict:
    """Generate auth query params for LiblibAI API."""
    timestamp = str(int(time.time() * 1000))
    nonce = uuid.uuid4().hex[:10]
    content = f"{uri}&{timestamp}&{nonce}"
    digest = hmac.new(secret_key.encode(), content.encode(), hashlib.sha1).digest()
    signature = base64.urlsafe_b64encode(digest).rstrip(b"=").decode()
    return {
        "AccessKey": access_key,
        "Signature": signature,
        "Timestamp": timestamp,
        "SignatureNonce": nonce,
    }


def api_request(uri: str, body: dict, ak: str, sk: str) -> dict:
    """Make authenticated POST request to LiblibAI API."""
    params = make_sign(uri, ak, sk)
    url = f"{BASE_URL}{uri}"
    resp = requests.post(url, params=params, json=body, headers={"Content-Type": "application/json"}, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    if data.get("code") and data["code"] != 0:
        print(f"API Error: {data}", file=sys.stderr)
        sys.exit(1)
    return data.get("data", data)


def generate_image(prompt: str, ak: str, sk: str, width=2048, height=2048, img_count=1, ref_images=None, prompt_magic=0):
    """Generate image using Seedream4.5 via LiblibAI API."""
    uri = "/api/generate/seedreamV4"
    params = {
        "prompt": prompt,
        "width": width,
        "height": height,
        "imgCount": img_count,
        "model": "doubao-seedream-4-5-251128",
        "sequentialImageGeneration": "disabled",
    }
    if prompt_magic:
        params["promptMagic"] = 1
    if ref_images:
        params["referenceImages"] = ref_images
    body = {
        "templateUuid": "0b6bad2fd350433ebb5abc7eb91f2ec9",
        "generateParams": params,
    }
    return api_request(uri, body, ak, sk)


def generate_video_text(prompt: str, ak: str, sk: str, model="kling-v2-6", aspect="16:9", duration="5", mode="pro", sound="on", prompt_magic=0):
    """Generate video from text using Kling via LiblibAI API."""
    uri = "/api/generate/video/kling/text2video"
    params = {
        "prompt": prompt,
        "model": model,
        "aspectRatio": aspect,
        "duration": duration,
        "mode": mode,
        "sound": sound,
    }
    if prompt_magic:
        params["promptMagic"] = 1
    body = {
        "templateUuid": "61cd8b60d340404394f2a545eeaf197a",
        "generateParams": params,
    }
    return api_request(uri, body, ak, sk)


def generate_video_img(prompt: str, start_frame: str, ak: str, sk: str, end_frame=None, model="kling-v2-6", duration="5", mode="pro", sound="on", prompt_magic=0):
    """Generate video from image(s) using Kling via LiblibAI API."""
    uri = "/api/generate/video/kling/img2video"
    params = {
        "prompt": prompt,
        "model": model,
        "duration": duration,
        "mode": mode,
    }
    if model == "kling-v2-6":
        params["images"] = [start_frame]
        params["sound"] = sound
    else:
        params["startFrame"] = start_frame
        if end_frame:
            params["endFrame"] = end_frame
    if prompt_magic:
        params["promptMagic"] = 1
    body = {
        "templateUuid": "180f33c6748041b48593030156d2a71d",
        "generateParams": params,
    }
    return api_request(uri, body, ak, sk)


def query_status(generate_uuid: str, ak: str, sk: str) -> dict:
    """Query task result by UUID."""
    uri = "/api/generate/status"
    body = {"generateUuid": generate_uuid}
    return api_request(uri, body, ak, sk)


def poll_result(generate_uuid: str, ak: str, sk: str, interval=5, max_wait=600):
    """Poll for task completion. Returns result dict."""
    start = time.time()
    while time.time() - start < max_wait:
        result = query_status(generate_uuid, ak, sk)
        status = result.get("generateStatus", 0)
        pct = result.get("percentCompleted", 0)
        # Status: 1=waiting, 2=processing, 5=completed, 6=failed
        if status == 6 or (result.get("generateMsg") and "fail" in result.get("generateMsg", "").lower()):
            print(f"Task failed: {result.get('generateMsg', 'Unknown error')}", file=sys.stderr)
            return result
        images = result.get("images", [])
        videos = result.get("videos", [])
        if images or videos or status == 5:
            return result
        print(f"  Progress: {pct:.0%} (status={status})", file=sys.stderr)
        time.sleep(interval)
    print("Timeout waiting for result", file=sys.stderr)
    return result


def main():
    parser = argparse.ArgumentParser(description="LiblibAI Image & Video Generation")
    sub = parser.add_subparsers(dest="command", required=True)

    # Image generation
    img_p = sub.add_parser("image", help="Generate image with Seedream4.5")
    img_p.add_argument("prompt", help="Text prompt")
    img_p.add_argument("--width", type=int, default=2048)
    img_p.add_argument("--height", type=int, default=2048)
    img_p.add_argument("--count", type=int, default=1, help="Number of images (1-15)")
    img_p.add_argument("--ref-images", nargs="*", help="Reference image URLs")
    img_p.add_argument("--prompt-magic", action="store_true", help="Enable prompt expansion")
    img_p.add_argument("--no-poll", action="store_true", help="Don't poll for result")

    # Text-to-video
    t2v_p = sub.add_parser("text2video", help="Generate video from text with Kling")
    t2v_p.add_argument("prompt", help="Text prompt")
    t2v_p.add_argument("--model", default="kling-v2-6", choices=["kling-v1-6", "kling-v2-master", "kling-v2-1-master", "kling-v2-5-turbo", "kling-v2-6"])
    t2v_p.add_argument("--aspect", default="16:9", choices=["16:9", "9:16", "1:1"])
    t2v_p.add_argument("--duration", default="5", choices=["5", "10"])
    t2v_p.add_argument("--mode", default="pro", choices=["std", "pro"])
    t2v_p.add_argument("--sound", default="on", choices=["on", "off"])
    t2v_p.add_argument("--prompt-magic", action="store_true")
    t2v_p.add_argument("--no-poll", action="store_true")

    # Image-to-video
    i2v_p = sub.add_parser("img2video", help="Generate video from image with Kling")
    i2v_p.add_argument("prompt", help="Text prompt")
    i2v_p.add_argument("--start-frame", required=True, help="Start frame image URL")
    i2v_p.add_argument("--end-frame", help="End frame image URL (only kling-v1-6)")
    i2v_p.add_argument("--model", default="kling-v2-6")
    i2v_p.add_argument("--duration", default="5", choices=["5", "10"])
    i2v_p.add_argument("--mode", default="pro", choices=["std", "pro"])
    i2v_p.add_argument("--sound", default="on", choices=["on", "off"])
    i2v_p.add_argument("--prompt-magic", action="store_true")
    i2v_p.add_argument("--no-poll", action="store_true")

    # Query status
    q_p = sub.add_parser("status", help="Query task status")
    q_p.add_argument("uuid", help="Task generateUuid")

    args = parser.parse_args()

    ak = os.environ.get("LIB_ACCESS_KEY")
    sk = os.environ.get("LIB_SECRET_KEY")
    if not ak or not sk:
        print("Error: Set LIB_ACCESS_KEY and LIB_SECRET_KEY environment variables", file=sys.stderr)
        sys.exit(1)

    if args.command == "image":
        result = generate_image(args.prompt, ak, sk, args.width, args.height, args.count, args.ref_images, args.prompt_magic)
        task_uuid = result.get("generateUuid")
        print(f"Task submitted: {task_uuid}")
        if not args.no_poll and task_uuid:
            result = poll_result(task_uuid, ak, sk)

    elif args.command == "text2video":
        result = generate_video_text(args.prompt, ak, sk, args.model, args.aspect, args.duration, args.mode, args.sound, args.prompt_magic)
        task_uuid = result.get("generateUuid")
        print(f"Task submitted: {task_uuid}")
        if not args.no_poll and task_uuid:
            result = poll_result(task_uuid, ak, sk, interval=10, max_wait=900)

    elif args.command == "img2video":
        result = generate_video_img(args.prompt, args.start_frame, ak, sk, args.end_frame, args.model, args.duration, args.mode, args.sound, args.prompt_magic)
        task_uuid = result.get("generateUuid")
        print(f"Task submitted: {task_uuid}")
        if not args.no_poll and task_uuid:
            result = poll_result(task_uuid, ak, sk, interval=10, max_wait=900)

    elif args.command == "status":
        result = query_status(args.uuid, ak, sk)

    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
