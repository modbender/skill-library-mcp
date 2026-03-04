# Cloudflare R2 API Reference

## Overview

Cloudflare R2 is an S3-compatible object storage service. It supports the AWS S3 API, so boto3 works out of the box with a custom endpoint.

## Endpoint Format

```
https://<ACCOUNT_ID>.r2.cloudflarestorage.com
```

## Authentication

R2 uses S3-compatible HMAC credentials:
- **Access Key ID** — public identifier
- **Secret Access Key** — private signing key

Create/manage API tokens at: https://dash.cloudflare.com/ → R2 → Manage R2 API Tokens

## boto3 Client Setup

```python
import boto3

client = boto3.client(
    "s3",
    endpoint_url="https://<ACCOUNT_ID>.r2.cloudflarestorage.com",
    aws_access_key_id="<ACCESS_KEY_ID>",
    aws_secret_access_key="<SECRET_ACCESS_KEY>",
    region_name="auto",  # Required for R2
)
```

## Common Operations

### List Buckets
```python
response = client.list_buckets()
for bucket in response["Buckets"]:
    print(bucket["Name"])
```

### Create Bucket
```python
client.create_bucket(Bucket="my-bucket")
```

### Upload Object
```python
# From file
client.upload_file("local.txt", "my-bucket", "remote/key.txt")

# From bytes
client.put_object(Bucket="my-bucket", Key="key.txt", Body=b"hello")
```

### Download Object
```python
# To file
client.download_file("my-bucket", "key.txt", "local.txt")

# To memory
response = client.get_object(Bucket="my-bucket", Key="key.txt")
data = response["Body"].read()
```

### List Objects
```python
paginator = client.get_paginator("list_objects_v2")
for page in paginator.paginate(Bucket="my-bucket", Prefix="folder/"):
    for obj in page.get("Contents", []):
        print(obj["Key"], obj["Size"])
```

### Delete Object
```python
client.delete_object(Bucket="my-bucket", Key="key.txt")
```

### Generate Pre-signed URL
```python
url = client.generate_presigned_url(
    "get_object",
    Params={"Bucket": "my-bucket", "Key": "key.txt"},
    ExpiresIn=3600,  # seconds
)
# Returns: https://<ACCOUNT_ID>.r2.cloudflarestorage.com/my-bucket/key.txt?X-Amz-Signature=...
```

### Copy Object
```python
client.copy_object(
    CopySource={"Bucket": "src-bucket", "Key": "src-key"},
    Bucket="dst-bucket",
    Key="dst-key",
)
```

## R2 vs S3 Differences

| Feature | AWS S3 | Cloudflare R2 |
|---|---|---|
| Egress fees | Yes | **No** (free egress) |
| Region | Required | Use `"auto"` |
| Bucket creation | Regional | Global |
| Multipart uploads | ✅ | ✅ |
| Versioning | ✅ | ✅ (2023+) |
| Pre-signed URLs | ✅ | ✅ |
| ACLs | ✅ | Limited |
| Lifecycle rules | ✅ | ✅ |

## R2 Pricing (2024)

- **Storage**: $0.015/GB-month
- **Class A operations** (writes): $4.50 per million
- **Class B operations** (reads): $0.36 per million
- **Egress**: **FREE** (major advantage over S3)

## Public Bucket Access

To expose a bucket publicly, configure a custom domain in the Cloudflare dashboard:
- R2 Bucket → Settings → Custom Domains

## Links

- [R2 Docs](https://developers.cloudflare.com/r2/)
- [R2 S3 Compatibility](https://developers.cloudflare.com/r2/api/s3/api/)
- [boto3 S3 Reference](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html)
