---
name: remove-metadata-from-pdf
description: Remove metadata from one or multiple PDFs by uploading them to the Solutions API, polling until completion, then returning download URL(s) for the cleaned PDF(s) (or a ZIP if multiple).
license: MIT
compatibility:
  agentskills: ">=0.1.0"
metadata:
  category: document-security
  tags:
    - pdf
    - metadata
    - privacy
    - sanitize
    - cross-service-solutions
  provider: Cross-Service-Solutions (Solutions API)
allowed-tools:
  - http
  - files
---

# remove-metadata-from-pdf

## Purpose
This skill removes metadata from one or multiple PDFs by:
1) accepting one or multiple PDF files from the user,
2) uploading them to the Solutions API,
3) polling the job status until it is finished,
4) returning download URL(s) for the cleaned file(s).
If multiple PDFs are processed, the output may include multiple PDFs and/or a ZIP for download.

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

Create job:
- `POST /api/40`
- `multipart/form-data` parameters:
  - `files` — required — multiple PDF files (multiple_files)

Get result by ID:
- `GET /api/<ID>`

When done, the response contains:
- `output.files[]` with `{ name, path }` where `path` is a downloadable URL (PDFs and/or ZIP).

## Inputs
### Required
- One or more PDF files (binary)
- API key (string)

### Optional
- None

## Output
Return a structured result:
- `job_id` (number)
- `status` (string)
- `outputs` (array) containing `{ name, path }` for each output file
- Convenience fields:
  - `download_url` (string) if exactly one output exists
  - `download_urls` (array of strings) for all outputs
- `input_files` (array of strings)

Example output:
```json
{
  "job_id": 990,
  "status": "done",
  "outputs": [
    { "name": "cleaned.pdf", "path": "https://.../cleaned.pdf" }
  ],
  "download_url": "https://.../cleaned.pdf",
  "download_urls": ["https://.../cleaned.pdf"],
  "input_files": ["input.pdf"]
}
