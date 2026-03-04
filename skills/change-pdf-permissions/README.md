
---

## `README.md`

```md
# change-pdf-permissions (OpenClaw Skill)

Change PDF permission flags (edit, print, copy/extract, forms, annotations, etc.) using the Solutions API and return a download URL for the updated PDF.

## What this does
PDF “permissions” are flags that PDF viewers should respect, such as:
- allow printing (and high-quality printing),
- allow editing content,
- allow adding/modifying annotations,
- allow extracting/copying content,
- allow form filling,
- allow assembling pages (insert/delete/rotate).

Note: different viewers may enforce these flags differently.

## What you need
- A PDF file
- Permission flag values (true/false)
- A Solutions API key (Bearer token)
  - Register / get key: https://login.cross-service-solutions.com/register

## Defaults (if you don’t specify anything)
- Disallow editing and extracting
- Allow printing (including high quality)
- Allow form filling
- Allow accessibility extraction

You can override all flags via CLI.

## How it works
1) Upload PDF + flags to:
   `POST https://api.xss-cross-service-solutions.com/solutions/solutions/api/75`
2) Poll:
   `GET  https://api.xss-cross-service-solutions.com/solutions/solutions/api/<job_id>`
3) Return `output.files[0].path` as download URL

## Script (CLI)
```bash
python scripts/change_pdf_permissions.py \
  --pdf "/path/to/file.pdf" \
  --can-modify false \
  --can-modify-annotations false \
  --can-print true \
  --can-print-high-quality true \
  --can-assemble-document false \
  --can-fill-in-form true \
  --can-extract-content false \
  --can-extract-for-accessibility true \
  --api-key "$SOLUTIONS_API_KEY"
