---
name: convert-to-pdf
description: Convert one or multiple documents to PDF by uploading them to Cross-Service-Solutions, polling until completion, then returning download URL(s) for the converted PDF(s) (or a ZIP if multiple).
license: MIT
compatibility:
  agentskills: ">=0.1.0"
metadata:
  category: document-processing
  tags:
    - pdf
    - convert
    - doc-to-pdf
    - cross-service-solutions
  provider: Cross-Service-Solutions (Solutions API)
allowed-tools:
  - http
  - files
---

# convert-to-pdf

## Purpose
This skill converts one or multiple documents to PDF by:
1) accepting one or multiple input files from the user,
2) uploading them to the Solutions API convert endpoint,
3) polling the job status until it is finished,
4) returning download URL(s) for the resulting file(s).
If multiple files are converted, the output may contain multiple PDFs and/or a ZIP for download.

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

Create convert job:
- `POST /api/31`
- `multipart/form-data` parameters:
  - `files` (Dokument) — required — multiple files (multiple_files)
    - You can convert multiple files and different types into multiple PDFs.
    - Multiple files can be downloadable as a zip-file.

Get result by ID:
- `GET /api/<ID>`

When done, the response contains:
- `output.files[]` with `{ name, path }` where `path` is a downloadable URL (PDFs and/or ZIP).

## Inputs
### Required
- One or more input files (binary)
- An API key (string)

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
  "job_id": 789,
  "status": "done",
  "outputs": [
    { "name": "file1.pdf", "path": "https://.../file1.pdf" },
    { "name": "file2.pdf", "path": "https://.../file2.pdf" },
    { "name": "converted.zip", "path": "https://.../converted.zip" }
  ],
  "download_urls": [
    "https://.../file1.pdf",
    "https://.../file2.pdf",
    "https://.../converted.zip"
  ],
  "input_files": ["file1.docx", "file2.pptx"]
}
