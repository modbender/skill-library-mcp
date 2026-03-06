#!/usr/bin/env python3
"""
🦞 Gradient AI — DO Spaces Operations

Upload, list, and delete files in DigitalOcean Spaces (S3-compatible).
This is the storage layer for the Knowledge Base pipeline — documents
land here before being indexed.

Usage:
    python3 gradient_spaces.py --upload /path/to/report.md --bucket my-data
    python3 gradient_spaces.py --list --bucket my-data --prefix "research/"
    python3 gradient_spaces.py --delete "research/old.md" --bucket my-data

Docs: https://docs.digitalocean.com/products/spaces/
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import boto3
import requests
from botocore.config import Config


def get_spaces_client(
    access_key: Optional[str] = None,
    secret_key: Optional[str] = None,
    endpoint: Optional[str] = None,
):
    """Create an S3-compatible client for DO Spaces.

    Falls back to environment variables if args aren't provided.

    Args:
        access_key: Spaces access key. Falls back to DO_SPACES_ACCESS_KEY.
        secret_key: Spaces secret key. Falls back to DO_SPACES_SECRET_KEY.
        endpoint: Spaces endpoint URL. Falls back to DO_SPACES_ENDPOINT.

    Returns:
        boto3 S3 client configured for DO Spaces.
    """
    access_key = access_key or os.environ.get("DO_SPACES_ACCESS_KEY", "")
    secret_key = secret_key or os.environ.get("DO_SPACES_SECRET_KEY", "")
    endpoint = endpoint or os.environ.get("DO_SPACES_ENDPOINT", "https://nyc3.digitaloceanspaces.com")

    return boto3.client(
        "s3",
        endpoint_url=endpoint,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        config=Config(signature_version="s3v4"),
    )


def build_key(prefix: str, filename: str) -> str:
    """Build the S3 key (path) for a file.

    Args:
        prefix: Key prefix (folder path), e.g., 'research/2026-02-15/'
        filename: File name to append.

    Returns:
        The full S3 key string.
    """
    prefix = prefix.rstrip("/")
    if prefix:
        return f"{prefix}/{filename}"
    return filename


def upload_file(
    content: str,
    key: str,
    bucket: Optional[str] = None,
    client=None,
    content_type: str = "text/markdown",
) -> dict:
    """Upload content to DO Spaces.

    Args:
        content: The text content to upload.
        key: S3 key (full path in the bucket).
        bucket: Bucket name. Falls back to DO_SPACES_BUCKET.
        client: Pre-configured S3 client (optional).
        content_type: MIME type of the content.

    Returns:
        dict with 'success', 'key', 'bucket', and 'message'.
    """
    bucket = bucket or os.environ.get("DO_SPACES_BUCKET", "")

    if not bucket:
        return {"success": False, "key": key, "bucket": "", "message": "No bucket specified."}

    try:
        if client is None:
            client = get_spaces_client()

        client.put_object(
            Bucket=bucket,
            Key=key,
            Body=content.encode("utf-8"),
            ContentType=content_type,
            ACL="private",
        )

        return {
            "success": True,
            "key": key,
            "bucket": bucket,
            "message": f"Uploaded {key} to {bucket}",
        }
    except Exception as e:
        return {
            "success": False,
            "key": key,
            "bucket": bucket,
            "message": f"Upload failed: {str(e)}",
        }


def list_files(
    bucket: Optional[str] = None,
    prefix: str = "",
    client=None,
) -> dict:
    """List files in a DO Spaces bucket.

    Args:
        bucket: Bucket name. Falls back to DO_SPACES_BUCKET.
        prefix: Only list files with this key prefix.
        client: Pre-configured S3 client (optional).

    Returns:
        dict with 'success', 'files' (list of dicts), and 'message'.
    """
    bucket = bucket or os.environ.get("DO_SPACES_BUCKET", "")

    if not bucket:
        return {"success": False, "files": [], "message": "No bucket specified."}

    try:
        if client is None:
            client = get_spaces_client()

        kwargs = {"Bucket": bucket}
        if prefix:
            kwargs["Prefix"] = prefix

        resp = client.list_objects_v2(**kwargs)
        contents = resp.get("Contents", [])

        files = [
            {
                "key": obj["Key"],
                "size": obj["Size"],
                "last_modified": obj["LastModified"].isoformat() if hasattr(obj["LastModified"], "isoformat") else str(obj["LastModified"]),
            }
            for obj in contents
        ]

        return {
            "success": True,
            "files": files,
            "message": f"Found {len(files)} file(s) in {bucket}/{prefix}",
        }
    except Exception as e:
        return {"success": False, "files": [], "message": f"List failed: {str(e)}"}


def delete_file(
    key: str,
    bucket: Optional[str] = None,
    client=None,
) -> dict:
    """Delete a file from DO Spaces.

    Args:
        key: S3 key of the file to delete.
        bucket: Bucket name. Falls back to DO_SPACES_BUCKET.
        client: Pre-configured S3 client (optional).

    Returns:
        dict with 'success', 'key', and 'message'.
    """
    bucket = bucket or os.environ.get("DO_SPACES_BUCKET", "")

    if not bucket:
        return {"success": False, "key": key, "message": "No bucket specified."}

    try:
        if client is None:
            client = get_spaces_client()

        client.delete_object(Bucket=bucket, Key=key)

        return {
            "success": True,
            "key": key,
            "message": f"Deleted {key} from {bucket}",
        }
    except Exception as e:
        return {"success": False, "key": key, "message": f"Delete failed: {str(e)}"}


# ─── CLI Interface ────────────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser(
        description="🦞 Manage files in DO Spaces"
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--upload", metavar="FILE", help="Upload a file")
    group.add_argument("--list", action="store_true", help="List files")
    group.add_argument("--delete", metavar="KEY", help="Delete a file by key")

    parser.add_argument("--bucket", default=None, help="Spaces bucket name")
    parser.add_argument("--prefix", default="", help="Key prefix (folder)")
    parser.add_argument("--key", default=None, help="Custom S3 key for uploads")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    if args.upload:
        filepath = Path(args.upload)
        if not filepath.exists():
            print(f"Error: File not found: {filepath}", file=sys.stderr)
            sys.exit(1)

        content = filepath.read_text()
        key = args.key or build_key(args.prefix, filepath.name)
        result = upload_file(content, key, bucket=args.bucket)

    elif args.list:
        result = list_files(bucket=args.bucket, prefix=args.prefix)

    elif args.delete:
        result = delete_file(args.delete, bucket=args.bucket)

    if args.json:
        print(json.dumps(result, indent=2, default=str))
    else:
        if result["success"]:
            print(f"✅ {result['message']}")
            if "files" in result:
                for f in result["files"]:
                    print(f"  📄 {f['key']} ({f['size']} bytes)")
        else:
            print(f"❌ {result['message']}", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()
