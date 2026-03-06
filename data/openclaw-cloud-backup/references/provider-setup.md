# Provider Setup Guide

This guide explains how to obtain the cloud configuration values:

- `BUCKET`
- `REGION`
- `ENDPOINT` (for non-AWS providers)
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`

For all providers:

1. Create a private bucket.
2. Create credentials scoped to that bucket only.
3. Allow minimum actions: list, read, write, delete.
4. Put values into `~/.openclaw-cloud-backup.conf`.

---

## AWS S3

### 1) Create bucket

- AWS Console -> S3 -> Create bucket
- Keep "Block Public Access" enabled
- Enable bucket versioning (recommended)

### 2) Create IAM user/key with least privilege

- IAM -> Users -> Create user (programmatic access)
- Attach a policy similar to:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["s3:ListBucket"],
      "Resource": "arn:aws:s3:::YOUR_BUCKET"
    },
    {
      "Effect": "Allow",
      "Action": ["s3:GetObject", "s3:PutObject", "s3:DeleteObject"],
      "Resource": "arn:aws:s3:::YOUR_BUCKET/*"
    }
  ]
}
```

### 3) Config values

- `BUCKET="YOUR_BUCKET"`
- `REGION="us-east-1"` (or your region)
- `ENDPOINT=""`
- `AWS_ACCESS_KEY_ID="<from IAM>"`
- `AWS_SECRET_ACCESS_KEY="<from IAM>"`

---

## Cloudflare R2

### 1) Create bucket

- Cloudflare Dashboard -> R2 -> Create bucket

### 2) Create API token

- R2 -> API Tokens
- Create token scoped to only this bucket
- Permissions: Object Read and Object Write

### 3) Collect config values

- Endpoint format: `https://<account_id>.r2.cloudflarestorage.com`
- `BUCKET="<r2-bucket-name>"`
- `REGION="auto"` (R2 commonly uses `auto`)
- Access key ID / Secret access key from token creation

### 4) Config values

- `ENDPOINT="https://<account_id>.r2.cloudflarestorage.com"`
- `BUCKET="<r2-bucket-name>"`
- `REGION="auto"`
- `AWS_ACCESS_KEY_ID="<r2_access_key_id>"`
- `AWS_SECRET_ACCESS_KEY="<r2_secret_access_key>"`

---

## Backblaze B2 (S3 API)

### 1) Create bucket

- Backblaze Console -> B2 Cloud Storage -> Create bucket
- Keep bucket private

### 2) Create application key

- App Keys -> Create New Application Key
- Restrict to the target bucket
- Allow read/write/list/delete for objects as needed

### 3) Collect config values

- Endpoint format: `https://s3.<region>.backblazeb2.com`
- Region examples: `us-west-004`, `eu-central-003`

### 4) Config values

- `ENDPOINT="https://s3.us-west-004.backblazeb2.com"`
- `BUCKET="<b2-bucket-name>"`
- `REGION="us-west-004"`
- `AWS_ACCESS_KEY_ID="<b2_key_id>"`
- `AWS_SECRET_ACCESS_KEY="<b2_application_key>"`

---

## MinIO

### 1) Create bucket and access key

- In MinIO console:
  - Create bucket (private)
  - Create access key / secret key pair with required object permissions

### 2) Config values

- `ENDPOINT="https://minio.example.com"`
- `BUCKET="<minio-bucket>"`
- `REGION="us-east-1"` (or your configured region)
- `AWS_ACCESS_KEY_ID="<minio_access_key>"`
- `AWS_SECRET_ACCESS_KEY="<minio_secret_key>"`

---

## DigitalOcean Spaces

### 1) Create Space

- DigitalOcean -> Spaces -> Create Space
- Keep private for backups

### 2) Create access key pair

- API -> Spaces Keys -> Generate New Key

### 3) Config values

- Endpoint format: `https://<region>.digitaloceanspaces.com`
- Example endpoint: `https://nyc3.digitaloceanspaces.com`

- `ENDPOINT="https://nyc3.digitaloceanspaces.com"`
- `BUCKET="<space-name>"`
- `REGION="us-east-1"` (S3 signing region for Spaces)
- `AWS_ACCESS_KEY_ID="<spaces_key>"`
- `AWS_SECRET_ACCESS_KEY="<spaces_secret>"`

---

## Verify Configuration

After filling config:

```bash
bash scripts/openclaw-cloud-backup.sh status
bash scripts/openclaw-cloud-backup.sh backup full
bash scripts/openclaw-cloud-backup.sh list
```

If backup or list fails, see `references/security-troubleshooting.md`.
