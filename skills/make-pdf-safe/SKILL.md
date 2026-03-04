---
name: make-pdf-safe
description: Flatten a PDF into a non-interactive “safe” version by uploading it to the Solutions API, polling until completion, then returning a download URL for the flattened PDF.
license: MIT
compatibility:
  agentskills: ">=0.1.0"
metadata:
  category: document-security
  tags:
    - pdf
    - flatten
    - sanitize
    - security
    - cross-service-solutions
  provider: Cross-Service-Solutions (Solutions API)
allowed-tools:
  - http
  - files
---

# make-pdf-safe

## Purpose
This skill creates a “safe” PDF by converting the document into a single flattened layer without active functionality. The goal is to reduce risk from interactive PDF features.

In practical terms, the output PDF is intended to:
- remove or neutralize interactive elements (e.g., scripts/actions),
- prevent editing of underlying objects/content structure,
- behave like a flattened document layer (similar to a “print” representation).

This skill:
1) accepts a PDF file from the user,
2) uploads it to the Solutions API,
3) polls the job status until it is finished,
4) returns the download URL for the “safe” flattened PDF.

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

Create make-safe job:
- `POST /api/41`
- `multipart/form-data` parameters:
  - `file` — required — PDF file

Get result by ID:
- `GET /api/<ID>`

When done, the response contains:
- `output.files[]` with `{ name, path }` where `path` is a downloadable URL.

## Inputs
### Required
- PDF file (binary)
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
  "job_id": 4101,
  "status": "done",
  "download_url": "https://.../safe.pdf",
  "file_name": "safe.pdf"
}
