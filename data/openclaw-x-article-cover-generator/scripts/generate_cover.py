#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["requests>=2.31.0"]
# ///

import argparse
import base64
import os
import sys
import time
from pathlib import Path
import requests

BASE_URL = "https://api.bltcy.ai/v1"
MODEL = "gemini-3.1-flash-image-preview"


def b64_data_uri(path: str) -> str:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(path)
    mime = "image/png" if p.suffix.lower() == ".png" else "image/jpeg"
    data = base64.b64encode(p.read_bytes()).decode()
    return f"data:{mime};base64,{data}"


def normalize_reference(ref: str) -> str:
    """Support local file path or http(s) URL as reference image input."""
    if ref.startswith("http://") or ref.startswith("https://"):
        return ref
    return b64_data_uri(ref)


def build_prompt(title: str, subtitle: str | None) -> str:
    text = f"标题：{title}"
    if subtitle:
        text += f"；副标题：{subtitle}"
    return (
        "按参考图风格生成 OpenClaw 的 X（Twitter）文章封面图。"
        "保持龙虾logo主体形象不变。"
        "构图要求：龙虾logo主体位于画面右侧1/4，文字区域占据左侧3/4。"
        "文字要清晰可读、对比强、留白充足。"
        "整体风格：科技感、深色背景、简洁高级。"
        f"请在左侧文字区排版：{text}。"
    )


def post_generation(api_key: str, prompt: str, ref: str, size: str, async_mode: bool):
    url = f"{BASE_URL}/images/generations"
    if async_mode:
        url += "?async=true"
    payload = {
        "model": MODEL,
        "prompt": prompt,
        "aspect_ratio": "21:9",  # 5:2 nearest
        "image_size": size,
        "response_format": "url",
        "image": [ref],
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    r = requests.post(url, headers=headers, json=payload, timeout=180)
    r.raise_for_status()
    return r.json()


def get_task(api_key: str, task_id: str):
    r = requests.get(
        f"{BASE_URL}/images/tasks/{task_id}",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        timeout=60,
    )
    r.raise_for_status()
    return r.json()


def save_from_url(url: str, out: Path):
    data = requests.get(url, timeout=120).content
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(data)


def main():
    ap = argparse.ArgumentParser(description="Generate OpenClaw X article cover")
    ap.add_argument("--title", required=True, help="封面标题（必填）")
    ap.add_argument("--subtitle", help="副标题（可选）")
    ap.add_argument("--reference", required=True, help="主参考图（支持本地路径或 http(s) URL；若多图场景请传用户指定主参考图）")
    ap.add_argument("--output", required=True, help="输出文件名，如 cover.png")
    ap.add_argument("--size", choices=["1K", "2K", "4K"], default="2K")
    ap.add_argument("--async-mode", action="store_true")
    ap.add_argument("--api-key")
    args = ap.parse_args()

    if not args.title.strip():
        print("Error: title is required", file=sys.stderr)
        sys.exit(1)

    api_key = args.api_key or os.environ.get("BLT_API_KEY")
    if not api_key:
        print("Error: BLT_API_KEY not found", file=sys.stderr)
        sys.exit(1)

    ref = normalize_reference(args.reference)
    prompt = build_prompt(args.title.strip(), args.subtitle.strip() if args.subtitle else None)

    result = post_generation(api_key, prompt, ref, args.size, args.async_mode)
    out = Path(args.output)

    if args.async_mode:
        task_id = result.get("task_id") or result.get("data")
        if not task_id:
            print(f"Unexpected async response: {result}", file=sys.stderr)
            sys.exit(1)
        print(f"Task ID: {task_id}")
        for _ in range(80):
            s = get_task(api_key, task_id)
            d = s.get("data", {})
            status = d.get("status")
            if status == "SUCCESS":
                url = d.get("data", {}).get("data", [{}])[0].get("url")
                if not url:
                    print(f"No image url: {s}", file=sys.stderr)
                    sys.exit(1)
                save_from_url(url, out)
                print(f"Image saved: {out.resolve()}")
                return
            if status == "FAILURE":
                print(f"Task failed: {d.get('fail_reason','unknown')}", file=sys.stderr)
                sys.exit(1)
            time.sleep(5)
        print("Timeout waiting async task", file=sys.stderr)
        sys.exit(1)
    else:
        data = result.get("data", [{}])
        if isinstance(data, dict):
            data = data.get("data", [{}])
        url = data[0].get("url") if data else None
        if not url:
            print(f"No image url in sync response: {result}", file=sys.stderr)
            sys.exit(1)
        save_from_url(url, out)
        print(f"Image saved: {out.resolve()}")


if __name__ == "__main__":
    main()
