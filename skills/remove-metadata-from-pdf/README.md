
---

## `README.md`

```md
# remove-metadata-from-pdf (OpenClaw Skill)

Remove metadata from one or multiple PDFs using the Solutions API and return download URL(s).
If multiple PDFs are processed, the API may also provide a ZIP file.

## What you need
- 1+ PDF file(s)
- A Solutions API key (Bearer token)
  - Register / get key: https://login.cross-service-solutions.com/register

## How it works
1) Upload PDFs to:
   `POST https://api.xss-cross-service-solutions.com/solutions/solutions/api/40`
2) Poll:
   `GET  https://api.xss-cross-service-solutions.com/solutions/solutions/api/<job_id>`
3) Return `output.files[].path` as download URL(s)

## Script (CLI)
```bash
python scripts/remove_metadata_from_pdf.py \
  --pdf "/path/to/a.pdf" \
  --pdf "/path/to/b.pdf" \
  --api-key "$SOLUTIONS_API_KEY"
