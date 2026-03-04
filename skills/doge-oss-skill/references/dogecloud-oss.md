# DogeCloud OSS Notes

Source seed: `doge.md` -> https://docs.dogecloud.com/oss/sdk-full-python

## Core Endpoints

- API signing and helper: `https://docs.dogecloud.com/oss/api-access-token.md`
- Temporary token (STS): `POST /auth/tmp_token.json`
- Python SDK guide: `https://docs.dogecloud.com/oss/sdk-full-python.md`

## Minimal Server-Side Flow

1. Use permanent AccessKey/SecretKey only on server side.
2. Call `/auth/tmp_token.json` with:
   - `channel`: `OSS_UPLOAD` (preferred least privilege) or `OSS_FULL`
   - `scopes`: list like `["mybucket:uploads/a.jpg"]` or `["mybucket:uploads/*"]`
3. Read response `data.Credentials` and `data.Buckets[*]`:
   - `name`: Doge bucket name
   - `s3Bucket`: S3 bucket value for SDK
   - `s3Endpoint`: endpoint URL for SDK
4. Upload file via Boto3 `upload_file` or `upload_fileobj`.

## Public URL Notes

- Doge console docs state each bucket gets a test domain ending with `.oss.dogecdn.com`.
- Test domain is not production-grade and can expire (commonly after 30 days if not replaced).
- For production/stable links, bind a custom acceleration domain and use it as the public base URL.
- `s3Bucket` and `s3Endpoint` can be used to construct S3-style candidate URLs, but CDN/custom domain is recommended for public distribution.
