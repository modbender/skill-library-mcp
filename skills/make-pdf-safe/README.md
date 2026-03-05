
---

## `README.md`

```md
# make-pdf-safe (OpenClaw Skill)

Create a “safe” PDF by flattening the document into a single, non-interactive layer via the Solutions API.

## What “safe” means here
This tool is meant to reduce risk from PDFs that contain interactive or active features.

The output PDF is intended to behave like a flattened representation:
- interactive features such as embedded actions/scripts are removed or neutralized,
- the document is converted into a non-editable-like layer (no underlying object structure to modify),
- content is preserved visually, but active functionality should not remain.

This is useful when you want to share or archive a PDF while minimizing the chance that:
- scripts/actions can run,
- forms/objects can be edited to change the document content structure.

## What you need
- A PDF file
- A Solutions API key (Bearer token)
  - Register / get key: https://login.cross-service-solutions.com/register

## How it works
1) Upload PDF to:
   `POST https://api.xss-cross-service-solutions.com/solutions/solutions/api/41`
2) Poll:
   `GET  https://api.xss-cross-service-solutions.com/solutions/solutions/api/<job_id>`
3) Return `output.files[0].path` as the download URL

## Script (CLI)
```bash
python scripts/make_pdf_safe.py \
  --pdf "/path/to/file.pdf" \
  --api-key "$SOLUTIONS_API_KEY"
