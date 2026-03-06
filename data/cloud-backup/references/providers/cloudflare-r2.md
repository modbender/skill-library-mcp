# Cloudflare R2

## Create bucket

1. Cloudflare Dashboard → **R2 Object Storage** → **Create bucket**
2. Pick a name (lowercase, no dots)
3. Location hint: choose closest region or "Automatic"

## Credentials

1. R2 → **Manage R2 API Tokens** → **Create API token**
2. Permissions: **Object Read & Write**
3. Scope: restrict to your backup bucket only
4. Copy the **Access Key ID** and **Secret Access Key**

## Endpoint

Format: `https://<ACCOUNT_ID>.r2.cloudflarestorage.com`

Find your Account ID: Cloudflare Dashboard → right sidebar or R2 overview page.

## Configure

```bash
openclaw config patch 'skills.entries.cloud-backup.config.bucket="my-backup-bucket"'
openclaw config patch 'skills.entries.cloud-backup.config.region="auto"'
openclaw config patch 'skills.entries.cloud-backup.config.endpoint="https://<ACCOUNT_ID>.r2.cloudflarestorage.com"'
openclaw config patch 'skills.entries.cloud-backup.env.ACCESS_KEY_ID="..."'
openclaw config patch 'skills.entries.cloud-backup.env.SECRET_ACCESS_KEY="..."'
```

## Notes

- R2 region is always `auto` — it's a single global namespace.
- R2 has zero egress fees — reads are free.
- Free tier: 10 GB storage, 10 million reads/month, 1 million writes/month.
- R2 does not support `s3:ListAllMyBuckets` — this is fine, we only list objects.
- If you get signature errors, double-check the Account ID in the endpoint URL.
