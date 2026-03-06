
---

## `README.md`

```md
# merge-pdf (OpenClaw Skill)

Merge multiple PDFs by uploading them to Cross-Service-Solutions and returning a download URL for the merged PDF.

## What you need
- At least 2 PDF files
- A Cross-Service-Solutions API key (Bearer token)
  - Register / get key: https://login.cross-service-solutions.com/register

## How it works
1) Upload PDFs to `POST https://api.xss-cross-service-solutions.com/solutions/solutions/api/30`
2) Poll `GET https://api.xss-cross-service-solutions.com/solutions/solutions/api/<job_id>` until done
3) Return `output.files[0].path` as the download URL

## Script (CLI)
```bash
python scripts/merge_pdf_files.py \
  --pdf "/path/to/a.pdf" \
  --pdf "/path/to/b.pdf" \
  --pdf "/path/to/c.pdf" \
  --api-key "$SOLUTIONS_API_KEY"
