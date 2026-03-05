# AWS S3

## Create bucket

1. AWS Console → S3 → **Create bucket**
2. Keep **Block Public Access** enabled (all four checkboxes)
3. Enable **Bucket Versioning** (recommended — protects against accidental overwrites)
4. Use **SSE-S3** encryption (default, free)

## Credentials

Create a dedicated IAM user with programmatic access. Never use root account keys.

### Least-privilege policy

Replace `YOUR_BUCKET` with your bucket name:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "ListBucket",
      "Effect": "Allow",
      "Action": ["s3:ListBucket"],
      "Resource": "arn:aws:s3:::YOUR_BUCKET"
    },
    {
      "Sid": "ObjectAccess",
      "Effect": "Allow",
      "Action": ["s3:GetObject", "s3:PutObject", "s3:DeleteObject"],
      "Resource": "arn:aws:s3:::YOUR_BUCKET/*"
    }
  ]
}
```

Steps: IAM → Users → Create user → Attach policy above → Create access key → Copy key ID and secret.

### Alternative: named profile

If you prefer `~/.aws/credentials` profiles instead of storing keys in OpenClaw config:

```bash
aws configure --profile openclaw-backup
# Enter key ID, secret, region, output format
```

Then set `config.profile` to `openclaw-backup` instead of providing keys.

## Configure

```bash
# Required
openclaw config patch 'skills.entries.cloud-backup.config.bucket="YOUR_BUCKET"'
openclaw config patch 'skills.entries.cloud-backup.config.region="us-east-1"'

# Credentials (pick one approach)
# Option A: keys in OpenClaw config
openclaw config patch 'skills.entries.cloud-backup.env.ACCESS_KEY_ID="AKIA..."'
openclaw config patch 'skills.entries.cloud-backup.env.SECRET_ACCESS_KEY="..."'

# Option B: named profile
openclaw config patch 'skills.entries.cloud-backup.config.profile="openclaw-backup"'
```

**No `endpoint` needed** — the aws CLI defaults to AWS S3.

## Region reference

Common regions: `us-east-1`, `us-west-2`, `eu-west-1`, `eu-central-1`, `ap-southeast-1`.

Full list: https://docs.aws.amazon.com/general/latest/gr/s3.html

## Notes

- AWS S3 is the only provider where `endpoint` should be left unset.
- If using S3 Object Lock or Glacier, ensure the IAM policy covers the required actions.
- For cross-account access, the bucket policy must also grant access.
