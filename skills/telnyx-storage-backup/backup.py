#!/usr/bin/env python3
"""
Backup OpenClaw workspace to Telnyx Storage (S3-compatible).

Creates a compressed archive of the workspace and uploads it to Telnyx Storage.

Setup:
1. Set TELNYX_API_KEY in your environment or a .env file
2. Run: python3 backup.py
3. Schedule via cron for automated backups

Requirements:
- Python 3.8+
- boto3: pip install boto3
"""

import os
import sys
import tarfile
import tempfile
from datetime import datetime
from pathlib import Path

try:
    import boto3
    from botocore.config import Config
except ImportError:
    print("Error: boto3 not installed. Run: pip install boto3")
    sys.exit(1)


# Configuration (override via environment variables)
BUCKET = os.environ.get("BACKUP_BUCKET", "openclaw-backup")
REGION = os.environ.get("BACKUP_REGION", "us-central-1")
ENDPOINT = os.environ.get("TELNYX_STORAGE_ENDPOINT", "https://us-central-1.telnyxcloudstorage.com")
WORKSPACE = Path(os.environ.get("OPENCLAW_WORKSPACE", os.environ.get("CLAWDBOT_WORKSPACE", Path.home() / "clawd")))
MAX_BACKUPS = int(os.environ.get("MAX_BACKUPS", "48"))  # Keep ~24h of 30-min backups

# What to back up — customize as needed
FILES_TO_BACKUP = [
    "AGENTS.md",
    "SOUL.md",
    "USER.md",
    "IDENTITY.md",
    "TOOLS.md",
    "MEMORY.md",
    "HEARTBEAT.md",
    "GUARDRAILS.md",
    "STATE.md",
    "memory",
    "knowledge",
    "scripts",
    "skills",
]


def load_api_key() -> str:
    """Load Telnyx API key from environment or .env file."""
    # 1. Check environment variable
    key = os.environ.get("TELNYX_API_KEY")
    if key:
        return key

    # 2. Check .env files in workspace
    for env_path in [WORKSPACE / ".env", WORKSPACE / ".env.telnyx",
                     Path(__file__).parent / ".env"]:
        if env_path.exists():
            for line in env_path.read_text().splitlines():
                line = line.strip()
                if line.startswith("TELNYX_API_KEY="):
                    return line.split("=", 1)[1].strip().strip('"').strip("'")

    print("Error: TELNYX_API_KEY not found.")
    print("Set it as an environment variable or add it to a .env file:")
    print("  export TELNYX_API_KEY=KEYxxxxx")
    print("  # or create .env with: TELNYX_API_KEY=KEYxxxxx")
    sys.exit(1)


def create_archive(workspace: Path, files: list) -> Path:
    """Create a tar.gz archive of specified files/directories."""
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    archive_name = f"openclaw-backup-{timestamp}.tar.gz"
    archive_path = Path(tempfile.gettempdir()) / archive_name

    print(f"Creating archive: {archive_name}")

    with tarfile.open(archive_path, "w:gz") as tar:
        for item in files:
            full_path = workspace / item
            if full_path.exists():
                print(f"  + {item}")
                tar.add(full_path, arcname=item)
            else:
                print(f"  - {item} (skipping)")

    size_kb = archive_path.stat().st_size / 1024
    print(f"Archive size: {size_kb:.1f} KB")
    return archive_path


def get_s3_client(api_key: str):
    """Create S3 client for Telnyx Storage."""
    return boto3.client(
        "s3",
        endpoint_url=ENDPOINT,
        region_name=REGION,
        aws_access_key_id=api_key,
        aws_secret_access_key=api_key,  # Telnyx uses the API key for both
        config=Config(signature_version="s3v4"),
    )


def ensure_bucket(s3, bucket: str):
    """Create bucket if it doesn't exist."""
    try:
        s3.head_bucket(Bucket=bucket)
    except Exception:
        print(f"Creating bucket: {bucket}")
        try:
            s3.create_bucket(Bucket=bucket)
        except Exception as e:
            if "BucketAlreadyOwnedByYou" not in str(e):
                raise


def cleanup_old_backups(s3, bucket: str, max_keep: int):
    """Remove old backups beyond the retention limit."""
    try:
        response = s3.list_objects_v2(Bucket=bucket, Prefix="openclaw-backup-")
        objects = response.get("Contents", [])
        if len(objects) <= max_keep:
            return

        # Sort by date, oldest first
        objects.sort(key=lambda x: x["LastModified"])
        to_delete = objects[:len(objects) - max_keep]

        for obj in to_delete:
            s3.delete_object(Bucket=bucket, Key=obj["Key"])
            print(f"  Removed: {obj['Key']}")

        print(f"  Cleaned up {len(to_delete)} old backup(s)")
    except Exception as e:
        print(f"  Warning: cleanup failed: {e}")


def main():
    api_key = load_api_key()

    print("OpenClaw Backup -> Telnyx Storage")
    print("=" * 40)

    # Create archive
    archive_path = create_archive(WORKSPACE, FILES_TO_BACKUP)

    try:
        # Upload
        s3 = get_s3_client(api_key)
        ensure_bucket(s3, BUCKET)

        key = archive_path.name
        print(f"Uploading to: s3://{BUCKET}/{key}")
        s3.upload_file(str(archive_path), BUCKET, key)
        print(f"Done: s3://{BUCKET}/{key}")

        # Cleanup old backups
        cleanup_old_backups(s3, BUCKET, MAX_BACKUPS)

    finally:
        archive_path.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
