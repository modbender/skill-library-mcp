# DigitalOcean Spaces

## Create Space

1. DigitalOcean Console → **Spaces Object Storage** → **Create a Space**
2. Choose a datacenter region (e.g., `nyc3`, `sfo3`, `ams3`, `sgp1`, `fra1`)
3. Restrict file listing: **Private**

## Credentials

1. **API** → **Spaces Keys** → **Generate New Key**
2. Copy the **Key** (= access key) and **Secret** (= secret key)
3. Spaces keys are global — they work across all Spaces in your account

## Endpoint

Format: `https://<REGION>.digitaloceanspaces.com`

Examples: `https://nyc3.digitaloceanspaces.com`, `https://fra1.digitaloceanspaces.com`

## Configure

```bash
openclaw config patch 'skills.entries.cloud-backup.config.bucket="my-backup-space"'
openclaw config patch 'skills.entries.cloud-backup.config.region="nyc3"'
openclaw config patch 'skills.entries.cloud-backup.config.endpoint="https://nyc3.digitaloceanspaces.com"'
openclaw config patch 'skills.entries.cloud-backup.env.ACCESS_KEY_ID="..."'
openclaw config patch 'skills.entries.cloud-backup.env.SECRET_ACCESS_KEY="..."'
```

## Notes

- Spaces keys are account-wide — there's no per-Space scoping (unlike AWS IAM).
- Region in the endpoint and `config.region` should match.
- Free tier: none (Spaces starts at $5/mo for 250 GB).
- CDN is available but not needed for backups.
- If you get `SignatureDoesNotMatch`, verify the endpoint region matches your Space's region.
