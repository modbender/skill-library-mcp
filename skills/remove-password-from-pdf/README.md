
---

## `README.md`

```md
# remove-password-from-pdf (OpenClaw Skill)

Remove password protection from a PDF using the Solutions API and return a download URL for the unlocked file.

## What you need
- A password-protected PDF file
- The current password (used as `password`)
- A Solutions API key (Bearer token)
  - Register / get key: https://login.cross-service-solutions.com/register

## How it works
1) Upload PDF + current password to:
   `POST https://api.xss-cross-service-solutions.com/solutions/solutions/api/33`
2) Poll:
   `GET  https://api.xss-cross-service-solutions.com/solutions/solutions/api/<job_id>`
3) Return `output.files[0].path` as the download URL

## Script (CLI)
```bash
python scripts/remove_password_from_pdf.py \
  --pdf "/path/to/protected.pdf" \
  --password "CurrentPasswordHere" \
  --api-key "$SOLUTIONS_API_KEY"
