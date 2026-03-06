---
name: reducto
description: |
  Reducto document processing API integration with managed API key authentication. Parse, extract, split, and edit documents.
  Use this skill when users want to process documents, extract structured data, or modify PDFs and DOCX files.
  For other third party apps, use the api-gateway skill (https://clawhub.ai/byungkyu/api-gateway).
compatibility: Requires network access and valid Maton API key
metadata:
  author: maton
  version: "1.0"
  clawdbot:
    emoji:
    homepage: "https://maton.ai"
    requires:
      env:
        - MATON_API_KEY
---

# Reducto

Access the Reducto document processing API with managed API key authentication. Parse documents, extract structured data, split documents into sections, and edit PDFs/DOCX files.

## Quick Start

```bash
# Parse a document
python <<'EOF'
import urllib.request, os, json
data = json.dumps({'document_url': 'https://example.com/document.pdf'}).encode()
req = urllib.request.Request('https://gateway.maton.ai/reducto/parse', data=data, method='POST')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Content-Type', 'application/json')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

## Base URL

```
https://gateway.maton.ai/reducto/{native-api-path}
```

Replace `{native-api-path}` with the actual Reducto API endpoint path. The gateway proxies requests to `platform.reducto.ai` and automatically injects your API key.

## Authentication

All requests require the Maton API key in the Authorization header:

```
Authorization: Bearer $MATON_API_KEY
```

**Environment Variable:** Set your API key as `MATON_API_KEY`:

```bash
export MATON_API_KEY="YOUR_API_KEY"
```

### Getting Your API Key

1. Sign in or create an account at [maton.ai](https://maton.ai)
2. Go to [maton.ai/settings](https://maton.ai/settings)
3. Copy your API key

## Connection Management

Manage your Reducto API key connections at `https://ctrl.maton.ai`.

### List Connections

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://ctrl.maton.ai/connections?app=reducto&status=ACTIVE')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

### Create Connection

```bash
python <<'EOF'
import urllib.request, os, json
data = json.dumps({'app': 'reducto'}).encode()
req = urllib.request.Request('https://ctrl.maton.ai/connections', data=data, method='POST')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Content-Type', 'application/json')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

### Get Connection

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://ctrl.maton.ai/connections/{connection_id}')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

**Response:**
```json
{
  "connection": {
    "connection_id": "f7579208-276c-455f-9962-4635fca739b9",
    "status": "ACTIVE",
    "creation_time": "2026-02-28T00:12:24.797884Z",
    "last_updated_time": "2026-02-28T00:16:13.509841Z",
    "url": "https://connect.maton.ai/?session_token=...",
    "app": "reducto",
    "metadata": {},
    "method": "API_KEY"
  }
}
```

Open the returned `url` in a browser to enter your Reducto API key.

### Delete Connection

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://ctrl.maton.ai/connections/{connection_id}', method='DELETE')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

### Specifying Connection

If you have multiple Reducto connections, specify which one to use with the `Maton-Connection` header:

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/reducto/parse')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Maton-Connection', 'f7579208-276c-455f-9962-4635fca739b9')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

If omitted, the gateway uses the default (oldest) active connection.

## API Reference

### Parse Document

Parse a document and extract structured content (text, tables, figures).

#### Synchronous Parse

```bash
POST /reducto/parse
Content-Type: application/json

{
  "document_url": "https://example.com/document.pdf"
}
```

**Response:**
```json
{
  "job_id": "04b8aa38-7eb3-4151-98b0-dbaea71358d9",
  "duration": 17.85,
  "pdf_url": "https://...",
  "studio_link": "https://studio.reducto.ai/job/...",
  "usage": {
    "num_pages": 15,
    "credits": 15.0
  },
  "result": {
    "chunks": [
      {
        "content": "Extracted text content...",
        "blocks": [...]
      }
    ]
  }
}
```

#### Asynchronous Parse

For long documents, use async to avoid timeouts:

```bash
POST /reducto/parse_async
Content-Type: application/json

{
  "document_url": "https://example.com/document.pdf"
}
```

**Response:**
```json
{
  "job_id": "e234ba95-410a-4dd0-8a14-743dbfc49470"
}
```

Poll the job status with `GET /reducto/job/{job_id}`.

---

### Extract Data

Extract specific fields from documents using a JSON schema.

#### Synchronous Extract

```bash
POST /reducto/extract
Content-Type: application/json

{
  "document_url": "https://example.com/document.pdf",
  "schema": {
    "type": "object",
    "properties": {
      "title": {"type": "string", "description": "The document title"},
      "authors": {"type": "array", "items": {"type": "string"}, "description": "List of author names"}
    }
  }
}
```

**Response:**
```json
{
  "job_id": "36f01a34-7ef6-40da-9e74-7c14902b6182",
  "usage": {
    "num_pages": 15,
    "num_fields": 9,
    "credits": 45.0
  },
  "studio_link": "https://studio.reducto.ai/job/...",
  "result": [
    {
      "title": "Document Title",
      "authors": ["Author One", "Author Two"]
    }
  ]
}
```

#### Asynchronous Extract

```bash
POST /reducto/extract_async
Content-Type: application/json

{
  "document_url": "https://example.com/document.pdf",
  "schema": {
    "type": "object",
    "properties": {
      "title": {"type": "string"}
    }
  }
}
```

**Response:**
```json
{
  "job_id": "0cdb6a50-df92-438b-875b-8b5c72d5b089"
}
```

---

### Split Document

Divide documents into logical sections based on content categories.

#### Synchronous Split

```bash
POST /reducto/split
Content-Type: application/json

{
  "document_url": "https://example.com/document.pdf",
  "split_description": [
    {"name": "abstract", "description": "The abstract section"},
    {"name": "introduction", "description": "The introduction section"},
    {"name": "conclusion", "description": "The conclusion section"}
  ]
}
```

**Response:**
```json
{
  "usage": {
    "num_pages": 15,
    "credits": 15.0
  },
  "result": {
    "section_mapping": {
      "abstract": [1],
      "introduction": [1, 2],
      "conclusion": [14, 15]
    },
    "splits": [
      {
        "name": "abstract",
        "pages": [1],
        "conf": "high"
      }
    ]
  }
}
```

#### Asynchronous Split

```bash
POST /reducto/split_async
Content-Type: application/json

{
  "document_url": "https://example.com/document.pdf",
  "split_description": [
    {"name": "abstract", "description": "The abstract section"}
  ]
}
```

**Response:**
```json
{
  "job_id": "381de5fe-e162-4039-9ef9-8522fb34056b"
}
```

---

### Edit Document

Fill forms and modify PDF/DOCX documents with natural language instructions.

#### Synchronous Edit

```bash
POST /reducto/edit
Content-Type: application/json

{
  "document_url": "https://example.com/form.pdf",
  "edit_instructions": "Fill in the name field with 'John Doe' and check the consent box"
}
```

**Response:**
```json
{
  "document_url": "https://presigned-url.s3.amazonaws.com/...",
  "form_schema": [...],
  "usage": {
    "num_pages": 2,
    "credits": 2.0
  }
}
```

#### Asynchronous Edit

```bash
POST /reducto/edit_async
Content-Type: application/json

{
  "document_url": "https://example.com/form.pdf",
  "edit_instructions": "Highlight all mentions of 'important' in red"
}
```

**Response:**
```json
{
  "job_id": "575189cb-8732-429a-ba8a-06de8ee03208"
}
```

---

### Upload File

Upload a document to Reducto and get a presigned URL for processing.

```bash
POST /reducto/upload
Content-Type: application/json

{}
```

**Response:**
```json
{
  "file_id": "reducto://18d574c7-4144-4f50-b7af-b8aba83ada5d",
  "presigned_url": "https://prod-storage.s3.amazonaws.com/...?AWSAccessKeyId=...&Signature=...&Expires=..."
}
```

Upload your file to the `presigned_url` using a PUT request, then use the `file_id` as `document_url` in parse/extract/split/edit requests.

---

### Pipeline

Execute pre-configured processing pipelines.

```bash
POST /reducto/pipeline
Content-Type: application/json

{
  "input": "https://example.com/document.pdf",
  "pipeline_id": "your-pipeline-id"
}
```

**Note:** `pipeline_id` must be a valid pipeline ID configured in your Reducto account via the Reducto Studio.

**Response:**
```json
{
  "job_id": "...",
  "usage": {
    "num_pages": 15,
    "credits": 15.0
  },
  "result": {
    "parse": {...},
    "extract": {...},
    "split": {...},
    "edit": {...}
  }
}
```

---

### Jobs

#### List Jobs

```bash
GET /reducto/jobs
```

**Response:**
```json
{
  "jobs": [
    {
      "job_id": "8c25561f-247a-4843-b561-1eb94c3792d1",
      "status": "Completed",
      "type": "Parse",
      "created_at": "2026-02-27T23:11:39.787917",
      "num_pages": 15,
      "duration": 6.62
    }
  ],
  "next_cursor": null
}
```

#### Get Job Status

```bash
GET /reducto/job/{job_id}
```

**Response (Pending):**
```json
{
  "status": "Pending",
  "result": null,
  "progress": 0.5,
  "reason": null
}
```

**Response (Completed):**
```json
{
  "status": "Completed",
  "result": {
    "job_id": "...",
    "duration": 17.85,
    "usage": {...},
    "result": {...}
  },
  "progress": null,
  "reason": null
}
```

Job status values: `Pending`, `InProgress`, `Completed`, `Failed`

---

### Version

```bash
GET /reducto/version
```

**Response:**
```json
"VERSION_GOES_HERE"
```

---

## Document URL Formats

The `document_url` parameter accepts several formats:

1. **Public URL**: `https://example.com/document.pdf`
2. **Presigned S3 URL**: `https://bucket.s3.amazonaws.com/key?...`
3. **Reducto Upload**: `reducto://file-id` (from `/upload` endpoint)
4. **Previous Job**: `jobid://job-id` (reuse parsed content from previous job)

## Code Examples

### JavaScript

```javascript
// Parse a document
const response = await fetch(
  'https://gateway.maton.ai/reducto/parse',
  {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${process.env.MATON_API_KEY}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      document_url: 'https://example.com/document.pdf'
    })
  }
);
const data = await response.json();
console.log(data.result.chunks);
```

### Python

```python
import os
import requests

# Extract data from a document
response = requests.post(
    'https://gateway.maton.ai/reducto/extract',
    headers={
        'Authorization': f'Bearer {os.environ["MATON_API_KEY"]}',
        'Content-Type': 'application/json'
    },
    json={
        'document_url': 'https://example.com/document.pdf',
        'schema': {
            'type': 'object',
            'properties': {
                'title': {'type': 'string'},
                'date': {'type': 'string'}
            }
        }
    }
)
result = response.json()
print(result['result'])
```

### Async Job Polling

```python
import os
import time
import requests

# Start async parse
response = requests.post(
    'https://gateway.maton.ai/reducto/parse_async',
    headers={
        'Authorization': f'Bearer {os.environ["MATON_API_KEY"]}',
        'Content-Type': 'application/json'
    },
    json={'document_url': 'https://example.com/large-document.pdf'}
)
job_id = response.json()['job_id']

# Poll for completion
while True:
    status = requests.get(
        f'https://gateway.maton.ai/reducto/job/{job_id}',
        headers={'Authorization': f'Bearer {os.environ["MATON_API_KEY"]}'}
    ).json()

    print(f"Status: {status['status']}, Progress: {status.get('progress')}")

    if status['status'] == 'Completed':
        print(status['result'])
        break
    elif status['status'] == 'Failed':
        print(f"Failed: {status['reason']}")
        break

    time.sleep(2)
```

## Notes

- Synchronous endpoints may timeout for large documents; use async endpoints instead
- Upload presigned URLs expire quickly; upload files immediately after calling `/upload`
- The `reducto://` prefix URLs from `/upload` can be used in subsequent parse/extract/split/edit calls
- Use `jobid://` prefix to reuse parsed content from a previous job (saves processing time)
- Connection uses API_KEY authentication method (not OAuth)
- Credits are consumed based on page count and operation type

## Error Handling

| Status | Meaning |
|--------|---------|
| 400 | Invalid request (missing required fields, invalid format) |
| 401 | Invalid or missing Maton API key |
| 404 | Resource not found |
| 422 | Validation error (check response body for details) |
| 4xx/5xx | Passthrough error from Reducto API |

### Troubleshooting: API Key Issues

1. Check that the `MATON_API_KEY` environment variable is set:

```bash
echo $MATON_API_KEY
```

2. Verify the API key is valid by listing connections:

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://ctrl.maton.ai/connections')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

### Troubleshooting: Invalid App Name

Ensure your URL path starts with `reducto`. For example:

- Correct: `https://gateway.maton.ai/reducto/parse`
- Incorrect: `https://gateway.maton.ai/parse`

## Resources

- [Reducto Documentation](https://docs.reducto.ai)
- [Reducto API Reference](https://docs.reducto.ai/api-reference)
- [Reducto Studio](https://studio.reducto.ai)
- [Maton Community](https://discord.com/invite/dBfFAcefs2)
- [Maton Support](mailto:support@maton.ai)
