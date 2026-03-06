import base64
import json
import os
import sys
import time
import requests
from urllib.parse import urlparse


def _guess_ext_from_mime(mime: str) -> str:
    if not mime:
        return "png"
    if "png" in mime:
        return "png"
    if "jpeg" in mime or "jpg" in mime:
        return "jpg"
    if "webp" in mime:
        return "webp"
    return "png"


def _save_data_url(data_url: str, out_dir: str, idx: int) -> str:
    header, b64 = data_url.split(",", 1)
    mime = None
    if ";base64" in header and header.startswith("data:"):
        mime = header.split(";", 1)[0].replace("data:", "")
    ext = _guess_ext_from_mime(mime)
    filename = f"openrouter_image_{int(time.time())}_{idx}.{ext}"
    path = os.path.join(out_dir, filename)
    with open(path, "wb") as f:
        f.write(base64.b64decode(b64))
    return path


def _download_url(url: str, out_dir: str, idx: int) -> str:
    parsed = urlparse(url)
    ext = os.path.splitext(parsed.path)[1].lstrip(".") or "png"
    filename = f"openrouter_image_{int(time.time())}_{idx}.{ext}"
    path = os.path.join(out_dir, filename)
    r = requests.get(url, timeout=60)
    r.raise_for_status()
    with open(path, "wb") as f:
        f.write(r.content)
    return path


def _extract_image_urls(resp: dict) -> list:
    urls = []

    choices = resp.get("choices") or []
    for ch in choices:
        msg = ch.get("message", {})

        # OpenRouter Gemini image models return message.images
        images = msg.get("images")
        if isinstance(images, list):
            for img in images:
                if isinstance(img, dict):
                    url = None
                    if "image_url" in img and isinstance(img["image_url"], dict):
                        url = img["image_url"].get("url")
                    url = url or img.get("url") or img.get("data")
                    if url:
                        urls.append(url)

        content = msg.get("content")
        if isinstance(content, list):
            for part in content:
                ptype = part.get("type")
                if ptype in ("image_url", "image"):
                    image_url = part.get("image_url", {})
                    url = image_url.get("url") or part.get("url") or part.get("data")
                    if url:
                        urls.append(url)
        elif isinstance(content, str):
            if "data:image/" in content:
                for token in content.split():
                    if token.startswith("data:image/"):
                        urls.append(token)
            if "http://" in content or "https://" in content:
                for token in content.split():
                    if token.startswith("http://") or token.startswith("https://"):
                        urls.append(token)

    for key in ("images", "data"):
        items = resp.get(key)
        if isinstance(items, list):
            for item in items:
                url = None
                if isinstance(item, dict):
                    url = item.get("url") or item.get("image_url") or item.get("b64_json")
                    if item.get("b64_json"):
                        url = f"data:image/png;base64,{item.get(b64_json)}"
                elif isinstance(item, str):
                    url = item
                if url:
                    urls.append(url)

    return urls


def generate(prompt: str, api_key: str, model: str, out_dir: str) -> list:
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://openclaw.local",
        "X-Title": "OpenClaw Gemini TG Image Gen",
    }
    payload = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt}
                ],
            }
        ],
    }

    resp = requests.post(url, headers=headers, data=json.dumps(payload), timeout=120)
    if resp.status_code != 200:
        raise RuntimeError(f"OpenRouter error {resp.status_code}: {resp.text}")

    data = resp.json()
    urls = _extract_image_urls(data)
    if not urls:
        raise RuntimeError("No image URLs found in OpenRouter response")

    paths = []
    for i, u in enumerate(urls):
        if u.startswith("data:image/"):
            paths.append(_save_data_url(u, out_dir, i))
        else:
            paths.append(_download_url(u, out_dir, i))
    return paths


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 generate_image.py <prompt> [model]", file=sys.stderr)
        sys.exit(1)

    prompt = sys.argv[1]
    model = sys.argv[2] if len(sys.argv) > 2 else "google/gemini-2.5-flash-image"
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        print("OPENROUTER_API_KEY is not set", file=sys.stderr)
        sys.exit(2)

    out_dir = "/root/.openclaw/workspace/tmp"
    os.makedirs(out_dir, exist_ok=True)

    paths = generate(prompt, api_key, model, out_dir)
    print(json.dumps({"paths": paths}, ensure_ascii=False))
