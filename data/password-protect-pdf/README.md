
---

## `README.md`

```md
# password-protect-pdf (OpenClaw Skill)

Add password protection to a PDF using the Solutions API and return a download URL for the protected file.

## What you need
- A PDF file
- A password (will be used as `userPass`)
- A Solutions API key (Bearer token)
  - Register / get key: https://login.cross-service-solutions.com/register

## How it works
1) Upload PDF + password to:
   `POST https://api.xss-cross-service-solutions.com/solutions/solutions/api/32`
2) Poll:
   `GET  https://api.xss-cross-service-solutions.com/solutions/solutions/api/<job_id>`
3) Return `output.files[0].path` as the download URL

## Script (CLI)
```bash
python scripts/password_protect_pdf.py \
  --pdf "/path/to/file.pdf" \
  --password "YourPasswordHere" \
  --api-key "$SOLUTIONS_API_KEY"
