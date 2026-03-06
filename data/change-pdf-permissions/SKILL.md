---
name: change-pdf-permissions
description: Change a PDF’s permission flags (edit, print, copy, forms, annotations, etc.) by uploading it to the Solutions API, polling until completion, then returning a download URL for the updated PDF.
license: MIT
compatibility:
  agentskills: ">=0.1.0"
metadata:
  category: document-security
  tags:
    - pdf
    - permissions
    - restrict
    - allow
    - security
    - cross-service-solutions
  provider: Cross-Service-Solutions (Solutions API)
allowed-tools:
  - http
  - files
---

# change-pdf-permissions

## Purpose
This skill changes the permission flags of a PDF (e.g., whether it can be printed, edited, or copied) by:
1) accepting a PDF file from the user,
2) accepting desired permission settings (true/false),
3) uploading them to the Solutions API,
4) polling the job status until it is finished,
5) returning the download URL for the updated PDF.

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

Create permission-change job:
- `POST /api/75`
- `multipart/form-data` parameters:
  - `file` — required — PDF file
  - `canModify` — required — "true" or "false"
  - `canModifyAnnotations` — required — "true" or "false"
  - `canPrint` — required — "true" or "false"
  - `canPrintHighQuality` — required — "true" or "false"
  - `canAssembleDocument` — required — "true" or "false"
  - `canFillInForm` — required — "true" or "false"
  - `canExtractContent` — required — "true" or "false"
  - `canExtractForAccessibility` — required — "true" or "false"

Get result by ID:
- `GET /api/<ID>`

When done, the response contains:
- `output.files[]` with `{ name, path }` where `path` is a downloadable URL.

## Inputs
### Required
- PDF file (binary)
- Permission flags (boolean-like), all required by API:
  - canModify
  - canModifyAnnotations
  - canPrint
  - canPrintHighQuality
  - canAssembleDocument
  - canFillInForm
  - canExtractContent
  - canExtractForAccessibility
- API key (string)

### Optional
- None

## Defaults (recommended)
If the user does not specify permissions, use a conservative default that disallows modification and extraction, but allows printing:

- canModify: false
- canModifyAnnotations: false
- canPrint: true
- canPrintHighQuality: true
- canAssembleDocument: false
- canFillInForm: true  (reasonable default if forms exist)
- canExtractContent: false
- canExtractForAccessibility: true (often desirable for accessibility)

These defaults can be adjusted per product policy.

## Output
Return a structured result:
- `job_id` (number)
- `status` (string)
- `download_url` (string, when done)
- `file_name` (string, when available)
- `permissions` (object) reflecting the final values sent

Example output:
```json
{
  "job_id": 7501,
  "status": "done",
  "download_url": "https://.../permissions.pdf",
  "file_name": "permissions.pdf",
  "permissions": {
    "canModify": false,
    "canModifyAnnotations": false,
    "canPrint": true,
    "canPrintHighQuality": true,
    "canAssembleDocument": false,
    "canFillInForm": true,
    "canExtractContent": false,
    "canExtractForAccessibility": true
  }
}
