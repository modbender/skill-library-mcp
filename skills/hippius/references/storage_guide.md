# Hippius Storage Guide

## Overview

Hippius offers S3-compatible storage with a decentralized backend on Bittensor Subnet 75.

**Current Status:**

| Storage Type | Status | Endpoint |
|-------------|--------|----------|
| **S3** | **Active (Recommended)** | `s3.hippius.com` |
| **IPFS** | Deprecated public node | Requires self-hosted IPFS node |

## S3-Compatible Storage

**Configuration:**
- Endpoint: `https://s3.hippius.com`
- Region: `decentralized`
- Auth: Access keys from console.hippius.com (prefix: `hip_`)

### AWS CLI

```bash
# Set credentials
export AWS_ACCESS_KEY_ID="hip_your_access_key"
export AWS_SECRET_ACCESS_KEY="your_secret_key"

# Create bucket
aws --endpoint-url https://s3.hippius.com --region decentralized \
    s3 mb s3://my-bucket

# Upload a file
aws --endpoint-url https://s3.hippius.com --region decentralized \
    s3 cp local_file.txt s3://my-bucket/remote_file.txt

# Download a file
aws --endpoint-url https://s3.hippius.com --region decentralized \
    s3 cp s3://my-bucket/remote_file.txt local_file.txt

# List files
aws --endpoint-url https://s3.hippius.com --region decentralized \
    s3 ls s3://my-bucket/

# List recursively
aws --endpoint-url https://s3.hippius.com --region decentralized \
    s3 ls s3://my-bucket/ --recursive

# Sync directory
aws --endpoint-url https://s3.hippius.com --region decentralized \
    s3 sync ./local-dir/ s3://my-bucket/remote-dir/

# Delete file
aws --endpoint-url https://s3.hippius.com --region decentralized \
    s3 rm s3://my-bucket/file.txt
```

### Python (boto3)

```python
import boto3

s3 = boto3.client(
    's3',
    endpoint_url='https://s3.hippius.com',
    aws_access_key_id='hip_your_access_key',
    aws_secret_access_key='your_secret_key',
    region_name='decentralized'
)

# Upload
s3.upload_file('local_file.txt', 'my-bucket', 'remote_file.txt')

# Download
s3.download_file('my-bucket', 'remote_file.txt', 'downloaded_file.txt')

# List objects
response = s3.list_objects_v2(Bucket='my-bucket')
for obj in response.get('Contents', []):
    print(f"{obj['Key']} ({obj['Size']} bytes)")

# Create bucket
s3.create_bucket(Bucket='my-new-bucket')
```

### Python (MinIO)

```python
from minio import Minio

client = Minio(
    "s3.hippius.com",
    access_key="hip_your_access_key",
    secret_key="your_secret_key",
    secure=True,
    region="decentralized"
)

# Upload
client.fput_object("my-bucket", "file.txt", "/path/to/file.txt")

# Download
client.fget_object("my-bucket", "file.txt", "/path/to/downloaded.txt")

# List objects
for obj in client.list_objects("my-bucket", recursive=True):
    print(f"{obj.object_name} ({obj.size} bytes)")
```

### JavaScript (MinIO)

```javascript
const { Client } = require('minio');

const client = new Client({
  endPoint: 's3.hippius.com',
  port: 443,
  useSSL: true,
  accessKey: 'hip_your_access_key',
  secretKey: 'your_secret_key',
  region: 'decentralized'
});

// Upload
await client.fPutObject('my-bucket', 'file.txt', '/path/to/file.txt');

// Download
await client.fGetObject('my-bucket', 'file.txt', '/path/to/downloaded.txt');

// List objects
const stream = client.listObjects('my-bucket', '', true);
stream.on('data', (obj) => console.log(obj.name, obj.size));
```

## IPFS Storage (Advanced)

The public IPFS endpoint is deprecated. To use IPFS:

1. Install and run IPFS daemon:
   ```bash
   brew install ipfs  # or equivalent
   ipfs init
   ipfs daemon
   ```

2. Configure hippius CLI:
   ```bash
   pip install hippius
   hippius config set ipfs api_url http://localhost:5001
   hippius config set ipfs local_ipfs true
   ```

3. Use hippius commands:
   ```bash
   hippius store /path/to/file.txt --no-encrypt
   hippius download QmYourCID /path/to/output.txt
   hippius pin QmYourCID
   hippius files
   ```

## Best Practices

1. **Use `decentralized` region** — not `us-east-1`
2. **Secure credentials** — use environment variables
3. **Organize with prefixes** — e.g., `snapshots/`, `files/`
4. **Keep a `latest` alias** — copy important files to a known key like `latest.tar.gz`
5. **Test round-trips** — verify upload AND download work

## Troubleshooting

**S3 Access Errors:**
- Verify access key starts with `hip_`
- Region must be `decentralized`
- Endpoint must be `https://s3.hippius.com`

**"Public store.hippius.network has been deprecated":**
Use S3 instead, or set up a local IPFS node.
