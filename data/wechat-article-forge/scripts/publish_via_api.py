#!/usr/bin/env python3
"""
WeChat Official Account API publisher (Path C).

Uploads images to WeChat CDN, then creates a draft article via the draft/add API.
Works for both verified and unverified subscription accounts.

Usage:
    python3 publish_via_api.py \
        --draft-dir ~/.wechat-article-writer/drafts/<slug> \
        --title "草稿标题（<=18字）" \
        --author "作者" \
        --source-url "https://github.com/..."

Requirements:
    Credentials file at path configured by `wechat_secrets_path` in config.json
    Default: ~/.wechat-article-writer/secrets.json -- {"appid": "wx...", "appsecret": "..."}
    pip install requests

KNOWN FIELD LIMITS (empirically confirmed, unverified accounts, 2026-02-28):
    title   <= 18 Chinese chars (36 bytes)
    author  <= 8 bytes  (2 Chinese chars or ~4 ASCII chars)
    digest  ~  28 Chinese chars
    content ~  18KB UTF-8 bytes
"""

import argparse, json, os, re, sys, time
import requests

def _get_secrets_path(data_dir=None):
    """Read wechat_secrets_path from config.json, fall back to default."""
    if data_dir is None:
        data_dir = os.path.expanduser("~/.wechat-article-writer")
    config_file = os.path.join(data_dir, "config.json")
    if os.path.exists(config_file):
        cfg = json.load(open(config_file))
        if "wechat_secrets_path" in cfg:
            return os.path.expanduser(cfg["wechat_secrets_path"])
    return os.path.expanduser("~/.wechat-article-writer/secrets.json")

SECRETS_PATH = _get_secrets_path()


def load_credentials():
    if not os.path.exists(SECRETS_PATH):
        print(f"ERROR: {SECRETS_PATH} not found", file=sys.stderr)
        sys.exit(1)
    return json.load(open(SECRETS_PATH))


def get_access_token(creds):
    resp = requests.get(
        "https://api.weixin.qq.com/cgi-bin/token",
        params={"grant_type": "client_credential", "appid": creds["appid"], "secret": creds["appsecret"]},
        timeout=30,
    )
    data = resp.json()
    if "access_token" not in data:
        print(f"ERROR: {data}", file=sys.stderr)
        sys.exit(1)
    return data["access_token"]


def upload_image_cdn(token, img_path, retries=5, delay=4):
    """Upload image, return temporary WeChat CDN URL for use in <img src="">."""
    for attempt in range(retries):
        with open(img_path, "rb") as f:
            resp = requests.post(
                "https://api.weixin.qq.com/cgi-bin/media/uploadimg",
                params={"access_token": token},
                files={"media": (os.path.basename(img_path), f, "image/png")},
                timeout=60,
            )
        data = resp.json()
        if "url" in data:
            return data["url"]
        print(f"  Attempt {attempt+1}: {data}", file=sys.stderr)
        time.sleep(delay)
    raise RuntimeError(f"Upload failed: {img_path}")


def upload_cover_permanent(token, img_path):
    """Upload cover as permanent material, return thumb_media_id."""
    with open(img_path, "rb") as f:
        resp = requests.post(
            "https://api.weixin.qq.com/cgi-bin/material/add_material",
            params={"access_token": token, "type": "image"},
            files={"media": (os.path.basename(img_path), f, "image/png")},
            timeout=60,
        )
    data = resp.json()
    if "media_id" not in data:
        raise RuntimeError(f"Cover upload failed: {data}")
    return data["media_id"]


def clean_html(raw):
    """Strip WeChat-incompatible wrappers and junk from formatted.html."""
    body_match = re.search(r'<body[^>]*>(.*)</body>', raw, re.DOTALL | re.IGNORECASE)
    content = body_match.group(1).strip() if body_match else raw
    content = re.sub(r'<meta[^>]+>', '', content)
    content = re.sub(r'<div>Preview build:[^<]+</div>', '', content)
    content = re.sub(r' style="[^"]{100,}"', '', content)
    content = re.sub(r'</?section[^>]*>', '', content)
    content = re.sub(r'\n\s*\n', '\n', content).strip()
    return content


def create_draft(token, title, author, digest, content, source_url, thumb_media_id):
    """
    Create draft via WeChat API.
    CRITICAL: Uses ensure_ascii=False -- requests json= parameter escapes Chinese as \\uXXXX.
    """
    payload = {
        "articles": [{
            "title": title,
            "author": author,
            "digest": digest,
            "content": content,
            "content_source_url": source_url,
            "thumb_media_id": thumb_media_id,
            "need_open_comment": 1,
            "only_fans_can_comment": 0,
        }]
    }
    # MUST use ensure_ascii=False to preserve Chinese characters
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    resp = requests.post(
        "https://api.weixin.qq.com/cgi-bin/draft/add",
        params={"access_token": token},
        data=body,
        headers={"Content-Type": "application/json; charset=utf-8"},
        timeout=60,
    )
    return resp.json()


def main():
    parser = argparse.ArgumentParser(description="WeChat draft publisher via API (Path C)")
    parser.add_argument("--draft-dir", required=True)
    parser.add_argument("--title", required=True, help="<= 18 Chinese chars")
    parser.add_argument("--author", default="", help="<= 2 Chinese chars or 4 ASCII")
    parser.add_argument("--digest", default="", help="~28 Chinese chars")
    parser.add_argument("--source-url", default="")
    parser.add_argument("--html-file", default="formatted.html")
    parser.add_argument("--cover", default="images/img1.png")
    args = parser.parse_args()

    draft_dir = os.path.expanduser(args.draft_dir)

    # Warn on limit violations
    if len(args.title) > 18:
        print(f"WARNING: title has {len(args.title)} chars; actual limit is 18. Will likely fail.", file=sys.stderr)
    if len(args.author.encode("utf-8")) > 8:
        print(f"WARNING: author exceeds 8 bytes; use <= 2 Chinese chars or <= 4 ASCII.", file=sys.stderr)

    creds = load_credentials()
    token = get_access_token(creds)
    print(f"Access token obtained.")

    cover_path = os.path.join(draft_dir, args.cover)
    print(f"Uploading cover...")
    thumb_media_id = upload_cover_permanent(token, cover_path)
    print(f"Cover media_id: {thumb_media_id[:40]}...")

    img_dir = os.path.join(draft_dir, "images")
    img_url_map = {}
    if os.path.exists(img_dir):
        pngs = sorted(f for f in os.listdir(img_dir) if f.endswith(".png"))
        print(f"Uploading {len(pngs)} images to WeChat CDN...")
        for fname in pngs:
            img_path = os.path.join(img_dir, fname)
            wx_url = upload_image_cdn(token, img_path)
            img_url_map[fname] = wx_url
            print(f"  {fname} -> {wx_url[:60]}...")
    with open(os.path.join(draft_dir, "wechat_image_urls.json"), "w") as f:
        json.dump(img_url_map, f, indent=2)

    html_path = os.path.join(draft_dir, args.html_file)
    with open(html_path) as f:
        raw = f.read()
    content = clean_html(raw)

    # Replace local img paths with WeChat CDN URLs
    for fname, wx_url in img_url_map.items():
        content = content.replace(f'src="images/{fname}"', f'src="{wx_url}"')
        content = content.replace(f'src="{fname}"', f'src="{wx_url}"')

    content_bytes = len(content.encode("utf-8"))
    print(f"Content: {len(content)} chars, {content_bytes} bytes ({content_bytes//1024}KB)")
    if content_bytes > 18000:
        print(f"WARNING: Content {content_bytes}b is close to ~18KB limit. Strip more styles if it fails.", file=sys.stderr)

    print("Creating draft...")
    result = create_draft(token, args.title, args.author, args.digest, content, args.source_url, thumb_media_id)

    if "media_id" in result:
        print(f"\nDraft created successfully!")
        print(f"  media_id: {result['media_id']}")
        print(f"  Title: {args.title}")
        print(f"  Open WeChat MP -> Drafts (草稿箱) to review and edit before publishing")
        with open(os.path.join(draft_dir, "wechat_draft_id.json"), "w") as f:
            json.dump({"media_id": result["media_id"], "title": args.title}, f, ensure_ascii=False, indent=2)
    else:
        errcode = result.get("errcode")
        errmsg = result.get("errmsg", "")
        print(f"\nDraft creation failed: {errcode} -- {errmsg}", file=sys.stderr)
        print("Error code guide (codes are often misleading -- test fields individually):", file=sys.stderr)
        print("  45003: title or content too large", file=sys.stderr)
        print("  45004: digest too large", file=sys.stderr)
        print("  45110: author too large (or content too large)", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
