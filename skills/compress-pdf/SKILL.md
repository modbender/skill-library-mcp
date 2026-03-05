---
name: compress-pdf
description: Compress a user-provided PDF by uploading it to Cross-Service-Solutions, polling until completion, then returning a download URL for the compressed file.
license: MIT
compatibility:
  agentskills: ">=0.1.0"
metadata:
  category: document-processing
  tags:
    - pdf
    - compression
    - cross-service-solutions
  provider: Cross-Service-Solutions (XSS)
allowed-tools:
  - http
  - files
---

# compress-pdf

## Purpose
This skill compresses a PDF by:
1) accepting a PDF file from the user,
2) uploading it to the Cross-Service-Solutions compression API,
3) polling the job status until it is finished,
4) returning the compressed file download URL.

## Credentials
The API requires an API key used as a Bearer token:
- `Authorization: Bearer <API_KEY>`

How the user gets an API key:
- They can sign up and get their key at:
  https://login.cross-service-solutions.com/register
- Or they can provide an API key directly to the bot.

**Rule:** never echo or log the API key.

## API endpoints
Base URL:
- `https://api.xss-cross-service-solutions.com/solutions/solutions`

Create compression job:
- `POST /api/29`
- `multipart/form-data` parameters:
  - `file` (PDF Dokument) — required — PDF file
  - `imageQuality` — required — number 0..100 (default 75)
  - `dpi` — required — number 72..300 (default 144)

Get result by ID:
- `GET /api/<ID>`

When done, the response contains:
- `output.files[]` with `{ name, path }` where `path` is a downloadable URL.

## Inputs
### Required
- A PDF file (binary)
- An API key (string)

### Optional
- `imageQuality` (0..100), default 75
- `dpi` (72..300), default 144

## Output
Return a structured result:
- `job_id` (number)
- `status` (string)
- `download_url` (string, when done)
- `file_name` (string, when available)
- `settings` (object)

Example output:
```json
{
  "job_id": 123,
  "status": "done",
  "download_url": "https://.../compressed.pdf",
  "file_name": "compressed.pdf",
  "settings": { "imageQuality": 75, "dpi": 144 }
}
