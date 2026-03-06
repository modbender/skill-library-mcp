---
name: password-protect-pdf
description: Add password protection to a PDF by uploading it to the Solutions API, polling until completion, then returning a download URL for the protected PDF.
license: MIT
compatibility:
  agentskills: ">=0.1.0"
metadata:
  category: document-security
  tags:
    - pdf
    - password
    - encrypt
    - security
    - cross-service-solutions
  provider: Cross-Service-Solutions (Solutions API)
allowed-tools:
  - http
  - files
---

# password-protect-pdf

## Purpose
This skill password-protects a PDF by:
1) accepting a PDF file from the user,
2) accepting a password from the user,
3) uploading both to the Solutions API,
4) polling the job status until it is finished,
5) returning the download URL for the password-protected PDF.

## Credentials
The API requires an API key used as a Bearer token:
- `Authorization: Bearer <API_KEY>`

How the user gets an API key:
- https://login.cross-service-solutions.com/register
- Or the user can provide an API key directly.

**Rule:** never echo or log the API key.

## API endpoints
Base URL:
- `https://api.xss-cross-service-solutions.com/solutions/solutions`

Create password-protect job:
- `POST /api/32`
- `multipart/form-data` parameters:
  - `file` (PDF-Datei) — required — PDF file
  - `userPass` (Passwort) — required — string password

Get result by ID:
- `GET /api/<ID>`

When done, the response contains:
- `output.files[]` with `{ name, path }` where `path` is a downloadable URL.

## Inputs
### Required
- PDF file (binary)
- Password (`userPass`, string)
- API key (string)

### Optional
- None

## Output
Return a structured result:
- `job_id` (number)
- `status` (string)
- `download_url` (string, when done)
- `file_name` (string, when available)

Example output:
```json
{
  "job_id": 321,
  "status": "done",
  "download_url": "https://.../protected.pdf",
  "file_name": "protected.pdf"
}
