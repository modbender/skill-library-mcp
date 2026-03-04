#!/usr/bin/env python3
"""
upload_card.py — Upload a card PNG to Cloudflare R2 and return the public URL.

Usage:
  python upload_card.py <png_path> [--secrets <path to r2 secrets json>]

Output (JSON to stdout):
  {"status": "ok", "url": "https://pub-xxx.r2.dev/cards/filename.png"}
"""
import sys
import os
import json
import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("png_path")
    parser.add_argument("--secrets", default=None,
                        help="Path to r2 secrets JSON. Defaults to workspace secrets/r2-birdfolio.json")
    args = parser.parse_args()

    png_path = os.path.abspath(args.png_path)
    if not os.path.exists(png_path):
        print(json.dumps({"status": "error", "message": f"File not found: {png_path}"}))
        sys.exit(1)

    # Resolve secrets file
    if args.secrets:
        secrets_path = args.secrets
    else:
        # Walk up from this script to find the workspace secrets folder
        script_dir = os.path.dirname(os.path.abspath(__file__))
        workspace = os.path.abspath(os.path.join(script_dir, "..", "..", ".."))
        secrets_path = os.path.join(workspace, "secrets", "r2-birdfolio.json")

    if not os.path.exists(secrets_path):
        print(json.dumps({"status": "error", "message": f"R2 secrets not found at {secrets_path}"}))
        sys.exit(1)

    with open(secrets_path) as f:
        cfg = json.load(f)

    try:
        import boto3
    except ImportError:
        print(json.dumps({"status": "error", "message": "boto3 not installed. Run: pip install boto3"}))
        sys.exit(1)

    s3 = boto3.client(
        "s3",
        endpoint_url=cfg["endpoint"],
        aws_access_key_id=cfg["access_key_id"],
        aws_secret_access_key=cfg["secret_access_key"],
        region_name="auto",
    )

    key = "cards/" + os.path.basename(png_path)

    with open(png_path, "rb") as f:
        s3.put_object(
            Bucket=cfg["bucket"],
            Key=key,
            Body=f,
            ContentType="image/png",
        )

    # Public URL — requires public access enabled on the bucket in Cloudflare dashboard
    public_url = cfg.get("public_url", "").rstrip("/")
    if not public_url:
        print(json.dumps({
            "status": "ok",
            "url": "",
            "note": "No public_url configured in r2-birdfolio.json. Enable public access on the bucket and add public_url to secrets."
        }))
        return

    url = f"{public_url}/{key}"
    print(json.dumps({"status": "ok", "url": url}))


if __name__ == "__main__":
    main()
