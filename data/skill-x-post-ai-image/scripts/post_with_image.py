#!/usr/bin/env python3
"""
Post to X (Twitter) with an AI-generated image via Gemini.
Usage: python3 post_with_image.py --text "tweet" --prompt "image prompt"
"""
import argparse, base64, os, subprocess, sys, tempfile

# Set via env vars
CK  = os.environ["X_CONSUMER_KEY"]
CS  = os.environ["X_CONSUMER_SECRET"]
AT  = os.environ["X_ACCESS_TOKEN"]
ATS = os.environ["X_ACCESS_TOKEN_SECRET"]

NANO_BANANA_SCRIPT = os.environ.get(
    "NANO_BANANA_SCRIPT",
    "/home/linuxbrew/.linuxbrew/lib/node_modules/openclaw/skills/nano-banana-pro/scripts/generate_image.py"
)

def generate_image(prompt: str, out_path: str) -> str:
    result = subprocess.run(
        ["uv", "run", NANO_BANANA_SCRIPT, "--prompt", prompt, "--filename", out_path, "--resolution", "1K"],
        capture_output=True, text=True,
        env={**os.environ, "GEMINI_API_KEY": os.environ.get("GEMINI_API_KEY", "")}
    )
    if result.returncode != 0:
        raise RuntimeError(f"Image gen failed: {result.stderr}")
    return out_path

def compress_image(src: str, dst: str, width=1200, height=675):
    from PIL import Image
    img = Image.open(src).resize((width, height))
    img.save(dst, "JPEG", quality=82)
    return dst

def upload_image(path: str) -> str:
    from requests_oauthlib import OAuth1Session
    oauth = OAuth1Session(CK, client_secret=CS, resource_owner_key=AT, resource_owner_secret=ATS)
    with open(path, "rb") as f:
        img_data = base64.b64encode(f.read()).decode()
    r = oauth.post(
        "https://upload.twitter.com/1.1/media/upload.json",
        data={"media_data": img_data, "media_category": "tweet_image"}
    )
    r.raise_for_status()
    return r.json()["media_id_string"]

def post_tweet(text: str, media_id: str = None):
    cmd = ["xurl", "post", text]
    if media_id:
        cmd += ["--media-id", media_id]
    result = subprocess.run(cmd, capture_output=True, text=True)
    print(result.stdout)
    if result.returncode != 0:
        raise RuntimeError(result.stderr)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--text", required=True)
    parser.add_argument("--prompt", default=None)
    parser.add_argument("--no-image", action="store_true")
    args = parser.parse_args()

    media_id = None
    if args.prompt and not args.no_image:
        with tempfile.TemporaryDirectory() as tmpdir:
            raw = f"{tmpdir}/raw.png"
            compressed = f"{tmpdir}/post.jpg"
            print("Generating image...")
            generate_image(args.prompt, raw)
            print("Compressing...")
            compress_image(raw, compressed)
            print("Uploading...")
            media_id = upload_image(compressed)
            print(f"Media ID: {media_id}")

    print("Posting tweet...")
    post_tweet(args.text, media_id)
    print("Done!")
