---
name: merge-pdf
description: Merge multiple user-provided PDF files by uploading them to Cross-Service-Solutions, polling until completion, then returning a download URL for the merged PDF.
license: MIT
compatibility:
  agentskills: ">=0.1.0"
metadata:
  category: document-processing
  tags:
    - pdf
    - merge
    - cross-service-solutions
  provider: Cross-Service-Solutions (XSS)
allowed-tools:
  - http
  - files
---

# merge-pdf-files

## Purpose
This skill merges multiple PDFs by:
1) accepting multiple PDF files from the user,
2) uploading them to the Cross-Service-Solutions merge API,
3) polling the job status until it is finished,
4) returning the merged PDF download URL.

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

Create merge job:
- `POST /api/30`
- `multipart/form-data` parameters:
  - `files` (PDF Dokument) — required — multiple PDF files (multiple_files)

Get result by ID:
- `GET /api/<ID>`

When done, the response contains:
- `output.files[]` with `{ name, path }` where `path` is a downloadable URL.

## Inputs
### Required
- One or more PDF files (binary)
- An API key (string)

### Optional
- None (ordering is determined by the provided file list order)

## Output
Return a structured result:
- `job_id` (number)
- `status` (string)
- `download_url` (string, when done)
- `file_name` (string, when available)
- `input_files` (array of strings)

Example output:
```json
{
  "job_id": 456,
  "status": "done",
  "download_url": "https://.../merged.pdf",
  "file_name": "merged.pdf",
  "input_files": ["a.pdf", "b.pdf", "c.pdf"]
}
