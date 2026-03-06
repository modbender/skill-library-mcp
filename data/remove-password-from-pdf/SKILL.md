---
name: remove-password-from-pdf
description: Remove password protection from a PDF by uploading it (with its current password) to the Solutions API, polling until completion, then returning a download URL for the unlocked PDF.
license: MIT
compatibility:
  agentskills: ">=0.1.0"
metadata:
  category: document-security
  tags:
    - pdf
    - unlock
    - remove-password
    - decrypt
    - cross-service-solutions
  provider: Cross-Service-Solutions (Solutions API)
allowed-tools:
  - http
  - files
---

# remove-password-from-pdf

## Purpose
This skill removes password protection from a PDF by:
1) accepting a password-protected PDF from the user,
2) accepting the current password from the user,
3) uploading both to the Solutions API,
4) polling the job status until it is finished,
5) returning the download URL for the unlocked PDF.

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

Create remove-password job:
- `POST /api/33`
- `multipart/form-data` parameters:
  - `file` (PDF-Datei) — required — PDF file
  - `password` (Password) — required — string (current password to unlock)

Get result by ID:
- `GET /api/<ID>`

When done, the response contains:
- `output.files[]` with `{ name, path }` where `path` is a downloadable URL.

## Inputs
### Required
- PDF file (binary)
- Current password (`password`, string)
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
  "job_id": 654,
  "status": "done",
  "download_url": "https://.../unlocked.pdf",
  "file_name": "unlocked.pdf"
}
