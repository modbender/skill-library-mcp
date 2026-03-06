---
name: hippius
description: Hippius decentralized storage on Bittensor Subnet 75 — upload files, query storage, manage buckets via S3-compatible API. Use when user asks to upload to Hippius, check storage status, set up Hippius credentials, list buckets/files, or asks about IPFS vs S3 options.
---

# Hippius Storage

Hippius is decentralized cloud storage on Bittensor SN75 with S3-compatible API.

**Recommended path:** S3 endpoint (`s3.hippius.com`) — the public IPFS node is deprecated.

## Quick Reference

| Key | Value |
|-----|-------|
| S3 Endpoint | `https://s3.hippius.com` |
| S3 Region | `decentralized` |
| Access Key Format | `hip_xxxxxxxxxxxx` |
| Console | [console.hippius.com](https://console.hippius.com) |
| Python CLI | `pip install hippius` (requires self-hosted IPFS node) |

## Setup

1. Get S3 credentials from [console.hippius.com](https://console.hippius.com/dashboard/settings) → Settings → API Keys
2. Set environment variables:
   ```bash
   export HIPPIUS_S3_ACCESS_KEY="hip_your_access_key"
   export HIPPIUS_S3_SECRET_KEY="your_secret_key"
   ```
3. Test: `aws --endpoint-url https://s3.hippius.com --region decentralized s3 ls`

## Common Operations

### Upload
```bash
aws --endpoint-url https://s3.hippius.com --region decentralized \
    s3 cp <file> s3://<bucket>/<key>
```

### Download
```bash
aws --endpoint-url https://s3.hippius.com --region decentralized \
    s3 cp s3://<bucket>/<key> <local_path>
```

### List buckets
```bash
aws --endpoint-url https://s3.hippius.com --region decentralized s3 ls
```

### List objects
```bash
aws --endpoint-url https://s3.hippius.com --region decentralized s3 ls s3://<bucket>/ --recursive
```

### Create bucket
```bash
aws --endpoint-url https://s3.hippius.com --region decentralized s3 mb s3://<bucket>
```

### Sync directory
```bash
aws --endpoint-url https://s3.hippius.com --region decentralized \
    s3 sync ./local-dir/ s3://<bucket>/remote-dir/
```

## Python (boto3)

```python
import boto3
import os

s3 = boto3.client(
    's3',
    endpoint_url='https://s3.hippius.com',
    aws_access_key_id=os.environ['HIPPIUS_S3_ACCESS_KEY'],
    aws_secret_access_key=os.environ['HIPPIUS_S3_SECRET_KEY'],
    region_name='decentralized'
)

# Upload
s3.upload_file('local.txt', 'my-bucket', 'remote.txt')

# Download
s3.download_file('my-bucket', 'remote.txt', 'downloaded.txt')

# List
for obj in s3.list_objects_v2(Bucket='my-bucket').get('Contents', []):
    print(f"{obj['Key']} ({obj['Size']} bytes)")
```

## Scripts

- `scripts/query_storage.py` — Query S3 buckets/objects and RPC account info

Usage:
```bash
# List S3 buckets
python scripts/query_storage.py --s3-buckets

# List objects in bucket
python scripts/query_storage.py --s3-objects my-bucket

# Query blockchain credits (requires account address)
python scripts/query_storage.py --account 5Grwva... --credits
```

## References

- `references/storage_guide.md` — S3 vs IPFS comparison, code examples (Python, JS)
- `references/cli_commands.md` — `hippius` CLI reference (requires self-hosted IPFS node)

## Troubleshooting

**"Public store.hippius.network has been deprecated"**
Use S3 instead. The `hippius` CLI's IPFS commands require a self-hosted IPFS node.

**S3 auth errors**
- Access key must start with `hip_`
- Region must be `decentralized` (not `us-east-1`)
- Endpoint must be `https://s3.hippius.com`

## External Links

- [Hippius Docs](https://docs.hippius.com)
- [Hippius Console](https://console.hippius.com)
- [Hippius Stats](https://hipstats.com)
- [CLI GitHub](https://github.com/thenervelab/hippius-cli)
