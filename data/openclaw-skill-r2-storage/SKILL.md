---
name: r2-storage
description: >
  Manage Cloudflare R2 object storage (upload, download, list, delete, presigned URLs)
  using boto3 S3-compatible API. Supports CLI usage and importable Python module.
license: MIT
metadata:
  author: Jack2
  tags: cloudflare, r2, s3, storage
---

# r2-storage Skill

Manage **Cloudflare R2** buckets and objects via the S3-compatible API. Uses `boto3` under the hood.

## When to Use This Skill

Use this skill whenever Marouane needs to:
- Upload files to R2 (backups, assets, media)
- Download files from R2
- List bucket contents
- Delete objects
- Generate temporary pre-signed URLs for sharing

## Credentials

Set via environment variables (defaults are pre-configured for Marouane's account):

| Variable | Description |
|---|---|
| `R2_ACCESS_KEY_ID` | R2 Access Key ID |
| `R2_SECRET_ACCESS_KEY` | R2 Secret Access Key |
| `R2_ENDPOINT` | R2 endpoint URL |
| `R2_ACCOUNT_ID` | Cloudflare Account ID |

## CLI Usage

```bash
# Upload
python3 scripts/r2.py upload myfile.txt my-bucket
python3 scripts/r2.py upload myfile.txt my-bucket --key folder/myfile.txt

# Download
python3 scripts/r2.py download my-bucket/folder/myfile.txt ./local-copy.txt

# List
python3 scripts/r2.py list my-bucket
python3 scripts/r2.py list my-bucket --prefix folder/

# Delete
python3 scripts/r2.py delete my-bucket/folder/myfile.txt

# Pre-signed URL (default 1h)
python3 scripts/r2.py presign my-bucket/folder/myfile.txt
python3 scripts/r2.py presign my-bucket/folder/myfile.txt --expires 86400
```

## Python Import Usage

```python
from scripts.r2 import upload, download, list_objects, delete, presign

# Upload
upload("local.txt", "my-bucket", key="optional/key.txt")

# List
objects = list_objects("my-bucket", prefix="folder/")
for obj in objects:
    print(obj["key"], obj["size"])

# Pre-signed URL
url = presign("my-bucket", "folder/file.txt", expires=3600)
```

## Requirements

- Python 3.8+
- `boto3` (`python3-boto3` on Ubuntu — already installed on vps118558)

## Notes

- Cloudflare R2 is S3-compatible; standard boto3 patterns apply.
- Pre-signed URLs work for **GET** requests only (public download links).
- The `region_name="auto"` is required for R2 compatibility.
