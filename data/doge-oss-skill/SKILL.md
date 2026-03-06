---
name: doge-oss-upload
description: Upload a local file to DogeCloud OSS (DogeCloud 对象存储) and return a public URL + metadata. Use when the user asks to “upload to doge/dogecloud”, “生成公网链接”, “把截图传到 OSS 并给我链接”.
metadata:
  openclaw:
    requires:
      bins: [python3]
---

# Doge Upload Public Info

Use the bundled uploader script to upload a local file with DogeCloud temporary credentials and print machine-readable public access info.

Read `references/dogecloud-oss.md` when API details are needed.

## Quick Start

1. Export environment variables (camelCase or `DOGECLOUD_*` both supported):
   - `accessKey` / `DOGECLOUD_ACCESS_KEY`
   - `secretKey` / `DOGECLOUD_SECRET_KEY`
   - `bucket` / `DOGECLOUD_BUCKET` (bucket name or `s3Bucket`)
   - `endpoint` / `DOGECLOUD_ENDPOINT`
   - `publicBaseUrl` / `DOGECLOUD_PUBLIC_BASE_URL`
   - `prefix` / `DOGECLOUD_PREFIX`
2. Install dependencies:

```bash
python3 -m pip install -U boto3 requests
```

3. Run:

```bash
python3 scripts/doge_upload_public_info.py ./local/file.jpg
```

## Workflow

1. Resolve bucket from env/CLI (support bucket name or `s3Bucket`).
2. Resolve upload key from `--key`, otherwise use `prefix/<local-filename>`.
3. Request temporary credentials from `/auth/tmp_token.json` using scoped permissions.
4. Upload file with Boto3 S3 client and returned `s3Bucket` + `s3Endpoint`.
5. Return JSON with upload metadata and public URL candidates.

## Output Contract

Return a JSON object with:
- `bucket`, `s3_bucket`, `s3_endpoint`, `object_key`
- `file` metadata (`path`, `size_bytes`, `md5`)
- `tmp_token` metadata (`channel`, `expired_at`)
- `public_info`:
  - `primary_url`
  - `candidates` (custom domain, derived test domain, and S3 endpoint style candidate)
  - `notes`

## Guardrails

- Keep permanent AccessKey/SecretKey on server side only.
- Default to `OSS_UPLOAD` for least privilege; use `OSS_FULL` only when explicitly required.
- If required env vars are missing, fail fast and print a clear reminder listing all missing keys.
- Warn that test domains ending with `.oss.dogecdn.com` can expire (commonly after 30 days).
- Prefer `--public-base-url` when the user requests a production-ready public URL.

## Resources

### scripts/
- `scripts/doge_upload_public_info.py`: upload and public-info extractor CLI.

### references/
- `references/dogecloud-oss.md`: minimal API notes and URL caveats from official docs.
