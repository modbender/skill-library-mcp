
---

## `README.md`

```md
# convert-to-pdf (OpenClaw Skill)

Convert one or multiple documents into PDF(s) using the Solutions API and return download URL(s).
If multiple files are converted, the API may also provide a ZIP file for download.

## What you need
- 1+ input file(s) (e.g. docx, pptx, images, etc.)
- A Solutions API key (Bearer token)
  - Register / get key: https://login.cross-service-solutions.com/register

## How it works
1) Upload files to:
   `POST https://api.xss-cross-service-solutions.com/solutions/solutions/api/31`
2) Poll:
   `GET  https://api.xss-cross-service-solutions.com/solutions/solutions/api/<job_id>`
3) Return `output.files[].path` as download URL(s)

## Script (CLI)
```bash
python scripts/convert_to_pdf.py \
  --file "/path/to/a.docx" \
  --file "/path/to/b.pptx" \
  --api-key "$SOLUTIONS_API_KEY"
