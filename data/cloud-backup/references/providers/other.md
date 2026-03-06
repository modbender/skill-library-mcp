# Other / Custom S3-Compatible Provider

Any storage service with an S3-compatible API works. You need three things:

1. **Bucket name** — create a private bucket in your provider's console.
2. **Endpoint URL** — the S3-compatible API endpoint (always required for non-AWS providers).
3. **Credentials** — an access key ID and secret key pair, scoped to the bucket if possible.

## Finding the endpoint

The endpoint is always a full URL: `https://...`

Common patterns:
- `https://s3.<region>.<provider>.com`
- `https://<account-id>.r2.cloudflarestorage.com`
- `https://<region>.digitaloceanspaces.com`
- `https://minio.your-server.com:9000`

Check your provider's S3 compatibility docs — look for "S3 API endpoint" or "S3-compatible endpoint."

## Configure

```bash
openclaw config patch 'skills.entries.cloud-backup.config.bucket="my-bucket"'
openclaw config patch 'skills.entries.cloud-backup.config.endpoint="https://s3.your-provider.com"'
openclaw config patch 'skills.entries.cloud-backup.config.region="us-east-1"'
openclaw config patch 'skills.entries.cloud-backup.env.ACCESS_KEY_ID="..."'
openclaw config patch 'skills.entries.cloud-backup.env.SECRET_ACCESS_KEY="..."'
```

## Region

Some providers ignore the region entirely. If unsure, use `us-east-1` (the aws CLI default) or `auto`. Check your provider's docs.

## Credentials

Most S3-compatible providers issue access key / secret key pairs through their console. Look for:
- "API keys", "access keys", "S3 credentials", or "application keys"
- Scope to a single bucket if the provider supports it

## Verifying compatibility

This skill uses only basic `aws s3` commands: `cp`, `ls`, `rm`. Any provider that supports these operations will work. We do **not** use:
- Multipart uploads
- Presigned URLs
- Bucket creation/deletion
- ACLs or bucket policies

If `aws s3 ls s3://your-bucket/ --endpoint-url https://...` works, you're good.

## Troubleshooting

- **`SignatureDoesNotMatch`** — region mismatch or wrong endpoint. Try `region=auto` or `region=us-east-1`.
- **SSL errors** — for self-hosted services with self-signed certs, set `AWS_CA_BUNDLE=/path/to/ca.pem` in your environment.
- **Connection refused** — include the port in the endpoint if it's non-standard: `https://host:9000`.
- **Path-style vs virtual-hosted** — some providers need path-style access. Set `AWS_S3_FORCE_PATH_STYLE=true` in your environment if you get bucket-name DNS errors.
