# Backblaze B2 (S3-compatible API)

## Create bucket

1. Backblaze Console → **B2 Cloud Storage** → **Create a Bucket**
2. Set to **Private**
3. Disable Object Lock unless you need immutable backups

## Credentials

1. **App Keys** → **Add a New Application Key**
2. Restrict to your backup bucket
3. Allow: `listBuckets`, `listFiles`, `readFiles`, `writeFiles`, `deleteFiles`
4. Copy the **keyID** (= access key) and **applicationKey** (= secret key)

## Endpoint

Format: `https://s3.<REGION>.backblazeb2.com`

Find your region on the bucket details page (e.g., `us-west-004`, `eu-central-003`).

## Configure

```bash
openclaw config patch 'skills.entries.cloud-backup.config.bucket="my-backup-bucket"'
openclaw config patch 'skills.entries.cloud-backup.config.region="us-west-004"'
openclaw config patch 'skills.entries.cloud-backup.config.endpoint="https://s3.us-west-004.backblazeb2.com"'
openclaw config patch 'skills.entries.cloud-backup.env.ACCESS_KEY_ID="<keyID>"'
openclaw config patch 'skills.entries.cloud-backup.env.SECRET_ACCESS_KEY="<applicationKey>"'
```

## Notes

- B2 free tier: 10 GB storage, 1 GB/day egress.
- Region is part of the endpoint URL — they must match.
- Application keys scoped to one bucket can't list other buckets (that's what we want).
- If you rotate the master key, all application keys are revoked.
