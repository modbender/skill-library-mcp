#!/usr/bin/env python3
"""
r2.py - Cloudflare R2 CLI & importable module (boto3 / S3-compatible)

Usage:
  python3 r2.py upload <local_file> <bucket> [--key object_key]
  python3 r2.py download <bucket/key> <local_dest>
  python3 r2.py list <bucket> [--prefix PREFIX]
  python3 r2.py delete <bucket/key>
  python3 r2.py presign <bucket/key> [--expires 3600]

Credentials (env vars or defaults):
  R2_ACCESS_KEY_ID
  R2_SECRET_ACCESS_KEY
  R2_ENDPOINT
  R2_ACCOUNT_ID
"""

import os
import sys
import argparse
import boto3
from botocore.exceptions import ClientError

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

DEFAULT_ENDPOINT = "https://b04c163cb488b020063281fc01b85b03.r2.cloudflarestorage.com"
DEFAULT_ACCESS_KEY = "5230d31f45dfeccd1a1d31f51efda4e8"
DEFAULT_SECRET_KEY = "dbfc3723949f8f8d6c31eacb547c89ac83f49154025916cc4f8388075019b4e8"

def get_client():
    """Create and return a boto3 S3 client configured for Cloudflare R2."""
    endpoint = os.environ.get("R2_ENDPOINT", DEFAULT_ENDPOINT)
    access_key = os.environ.get("R2_ACCESS_KEY_ID", DEFAULT_ACCESS_KEY)
    secret_key = os.environ.get("R2_SECRET_ACCESS_KEY", DEFAULT_SECRET_KEY)

    client = boto3.client(
        "s3",
        endpoint_url=endpoint,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name="auto",
    )
    return client


# ---------------------------------------------------------------------------
# Core functions (importable)
# ---------------------------------------------------------------------------

def upload(local_path: str, bucket: str, key: str = None) -> dict:
    """Upload a file to R2. Returns S3 response."""
    if key is None:
        key = os.path.basename(local_path)
    client = get_client()
    response = client.upload_file(local_path, bucket, key)
    return {"bucket": bucket, "key": key, "local": local_path}


def download(bucket: str, key: str, dest: str) -> dict:
    """Download a file from R2 to dest path."""
    client = get_client()
    client.download_file(bucket, key, dest)
    return {"bucket": bucket, "key": key, "dest": dest}


def list_objects(bucket: str, prefix: str = "") -> list:
    """List objects in a bucket, optionally filtered by prefix."""
    client = get_client()
    paginator = client.get_paginator("list_objects_v2")
    results = []
    kwargs = {"Bucket": bucket}
    if prefix:
        kwargs["Prefix"] = prefix
    for page in paginator.paginate(**kwargs):
        for obj in page.get("Contents", []):
            results.append({
                "key": obj["Key"],
                "size": obj["Size"],
                "last_modified": obj["LastModified"].isoformat(),
            })
    return results


def delete(bucket: str, key: str) -> dict:
    """Delete an object from R2."""
    client = get_client()
    client.delete_object(Bucket=bucket, Key=key)
    return {"bucket": bucket, "key": key, "deleted": True}


def presign(bucket: str, key: str, expires: int = 3600) -> str:
    """Generate a pre-signed URL for temporary access."""
    client = get_client()
    url = client.generate_presigned_url(
        "get_object",
        Params={"Bucket": bucket, "Key": key},
        ExpiresIn=expires,
    )
    return url


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_bucket_key(arg: str):
    """Parse 'bucket/key' into (bucket, key)."""
    parts = arg.split("/", 1)
    if len(parts) != 2 or not parts[1]:
        print(f"Error: expected 'bucket/key', got '{arg}'", file=sys.stderr)
        sys.exit(1)
    return parts[0], parts[1]


def cmd_upload(args):
    key = args.key or os.path.basename(args.local_file)
    result = upload(args.local_file, args.bucket, key)
    print(f"✅ Uploaded '{result['local']}' → s3://{result['bucket']}/{result['key']}")


def cmd_download(args):
    bucket, key = parse_bucket_key(args.bucket_key)
    result = download(bucket, key, args.dest)
    print(f"✅ Downloaded s3://{result['bucket']}/{result['key']} → {result['dest']}")


def cmd_list(args):
    objects = list_objects(args.bucket, args.prefix or "")
    if not objects:
        print(f"(bucket '{args.bucket}' is empty or prefix not found)")
        return
    print(f"{'Key':<60} {'Size':>10}  Last Modified")
    print("-" * 90)
    for obj in objects:
        print(f"{obj['key']:<60} {obj['size']:>10}  {obj['last_modified']}")
    print(f"\n{len(objects)} object(s)")


def cmd_delete(args):
    bucket, key = parse_bucket_key(args.bucket_key)
    delete(bucket, key)
    print(f"🗑️  Deleted s3://{bucket}/{key}")


def cmd_presign(args):
    bucket, key = parse_bucket_key(args.bucket_key)
    url = presign(bucket, key, args.expires)
    print(f"🔗 Pre-signed URL (expires in {args.expires}s):\n{url}")


def main():
    parser = argparse.ArgumentParser(
        prog="r2",
        description="Cloudflare R2 CLI (boto3/S3-compatible)",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # upload
    p_up = sub.add_parser("upload", help="Upload a file to R2")
    p_up.add_argument("local_file", help="Local file path")
    p_up.add_argument("bucket", help="Target bucket name")
    p_up.add_argument("--key", help="Object key (default: filename)")
    p_up.set_defaults(func=cmd_upload)

    # download
    p_dl = sub.add_parser("download", help="Download a file from R2")
    p_dl.add_argument("bucket_key", help="bucket/key")
    p_dl.add_argument("dest", help="Local destination path")
    p_dl.set_defaults(func=cmd_download)

    # list
    p_ls = sub.add_parser("list", help="List objects in a bucket")
    p_ls.add_argument("bucket", help="Bucket name")
    p_ls.add_argument("--prefix", help="Filter by prefix", default="")
    p_ls.set_defaults(func=cmd_list)

    # delete
    p_rm = sub.add_parser("delete", help="Delete an object from R2")
    p_rm.add_argument("bucket_key", help="bucket/key")
    p_rm.set_defaults(func=cmd_delete)

    # presign
    p_ps = sub.add_parser("presign", help="Generate a pre-signed URL")
    p_ps.add_argument("bucket_key", help="bucket/key")
    p_ps.add_argument("--expires", type=int, default=3600, help="Expiry in seconds (default 3600)")
    p_ps.set_defaults(func=cmd_presign)

    args = parser.parse_args()
    try:
        args.func(args)
    except ClientError as e:
        print(f"❌ R2 error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
