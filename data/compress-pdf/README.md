
---

## `README.md`

```md
# compress-pdf (OpenClaw Skill)

Compress a PDF by uploading it to Cross-Service-Solutions and returning a download URL for the compressed file.

## What you need
- A PDF file
- A Cross-Service-Solutions API key (Bearer token)
  - Register / get key: https://login.cross-service-solutions.com/register

## How it works
1) Upload PDF to `POST https://api.xss-cross-service-solutions.com/solutions/solutions/api/29`
2) Poll `GET https://api.xss-cross-service-solutions.com/solutions/solutions/api/<job_id>` until done
3) Return `output.files[0].path` as the download URL

## Defaults
- imageQuality: 75
- dpi: 144

## Script (CLI)
A helper script is included:

```bash
python scripts/compress_pdf.py \
  --pdf "/path/to/file.pdf" \
  --api-key "$SOLUTIONS_API_KEY" \
  --image-quality 75 \
  --dpi 144
