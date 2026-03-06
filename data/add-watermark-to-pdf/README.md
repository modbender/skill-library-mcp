
---

## `README.md`

```md
# add-watermark-to-pdf (OpenClaw Skill)

Add a text watermark to one or multiple PDFs using the Solutions API and return download URL(s).
If multiple PDFs are processed, the API may also provide a ZIP file.

## What you need
- 1+ PDF file(s)
- Watermark text (string) used as `text`
- A Solutions API key (Bearer token)
  - Register / get key: https://login.cross-service-solutions.com/register

## How it works
1) Upload PDFs + watermark text to:
   `POST https://api.xss-cross-service-solutions.com/solutions/solutions/api/61`
2) Poll:
   `GET  https://api.xss-cross-service-solutions.com/solutions/solutions/api/<job_id>`
3) Return `output.files[].path` as download URL(s)

## Script (CLI)
```bash
python scripts/add_watermark_to_pdf.py \
  --pdf "/path/to/a.pdf" \
  --pdf "/path/to/b.pdf" \
  --text "CONFIDENTIAL" \
  --api-key "$SOLUTIONS_API_KEY"
