---
name: deepread-form-fill
title: image.png
description: AI-powered PDF form filling. Upload any PDF form and your data as JSON — AI detects fields visually, maps your data semantically, fills the form with quality checks, and returns a completed PDF. Works with scanned forms, handwritten templates, and any PDF — no AcroForm fields required.
disable-model-invocation: true
metadata:
  {"openclaw":{"requires":{"env":["DEEPREAD_API_KEY"]},"primaryEnv":"DEEPREAD_API_KEY","homepage":"https://www.deepread.tech"}}
---

# DeepRead Form Fill — AI-Powered PDF Form Filling API

Upload any PDF form + your data as JSON. AI detects fields, maps your data, fills the form, quality-checks the result, and returns a completed PDF you can download.

**Works with any PDF** — scanned paper forms, government PDFs, custom templates. No AcroForm fields required.

## What This Skill Does

You provide:
1. A blank PDF form (upload)
2. Your data as JSON (e.g. `{"full_name": "Jane Doe", "dob": "1990-03-15"}`)

DeepRead returns:
- A filled PDF with your data placed in the correct fields
- A quality report showing what was filled, what was verified, and what needs human review

**No field mapping, no coordinates, no configuration.** The AI figures out where everything goes.

## Setup

### Get Your API Key

```bash
# Sign up (free — 2,000 pages/month, no credit card)
# https://www.deepread.tech/dashboard/?utm_source=clawdhub
```

Save your API key:
```bash
export DEEPREAD_API_KEY="sk_live_your_key_here"
```

## Quick Start

### Fill a Form (3 lines)

```bash
# 1. Submit form + data
curl -X POST https://api.deepread.tech/v1/form-fill \
  -H "X-API-Key: $DEEPREAD_API_KEY" \
  -F "file=@application.pdf" \
  -F 'form_fields={"full_name": "Jane Doe", "date_of_birth": "03/15/1990", "address": "123 Main St, Portland OR 97201"}'

# Response (immediate):
# {"id": "<job_id>", "status": "queued"}

# 2. Poll for result (use the id from step 1)
curl https://api.deepread.tech/v1/form-fill/<job_id> \
  -H "X-API-Key: $DEEPREAD_API_KEY"

# 3. Download the filled PDF from filled_form_url in the response
```

## API Reference

### POST /v1/form-fill — Submit a Form for Filling

**Authentication:** `X-API-Key` header (required)

**Content-Type:** `multipart/form-data`

**Parameters:**

| Field | Type | Required | Description |
|---|---|---|---|
| `file` | File | Yes | PDF form to fill |
| `form_fields` | JSON string | Yes | `{"field_name": "value"}` — your data |
| `webhook_url` | String | No | URL to receive results when done |
| `idempotency_key` | String | No | Prevent duplicate submissions |
| `url_expires_in` | Integer | No | Signed URL expiry in seconds (default: 604800 = 7 days, min: 3600, max: 604800) |

**Example:**
```bash
curl -X POST https://api.deepread.tech/v1/form-fill \
  -H "X-API-Key: $DEEPREAD_API_KEY" \
  -F "file=@tax_form.pdf" \
  -F 'form_fields={
    "taxpayer_name": "Jane Doe",
    "ssn": "123-45-6789",
    "filing_status": "Single",
    "total_income": "85000",
    "tax_year": "2025"
  }' \
  -F "webhook_url=https://your-app.com/webhooks/form-fill"
```

**Response (immediate):**
```json
{
  "id": "<job_id>",
  "status": "queued"
}
```

Processing is **asynchronous** — poll the GET endpoint or use a webhook.

### GET /v1/form-fill/{job_id} — Get Job Status & Results

**Authentication:** `X-API-Key` header (required)

**Rate limit:** 20 requests per 60 seconds

```bash
curl https://api.deepread.tech/v1/form-fill/<job_id> \
  -H "X-API-Key: $DEEPREAD_API_KEY"
```

**Response when completed:**
```json
{
  "id": "<job_id>",
  "status": "completed",
  "file_name": "tax_form.pdf",
  "created_at": "2025-06-15T10:00:00Z",
  "completed_at": "2025-06-15T10:00:18Z",
  "filled_form_url": "https://storage.deepread.tech/form_fill/.../filled.pdf",
  "fields_detected": 25,
  "fields_filled": 23,
  "fields_verified": 21,
  "fields_hil_flagged": 2,
  "duration_seconds": 18.3,
  "report": {
    "summary": {
      "fields_detected": 25,
      "fields_filled": 23,
      "fields_verified": 21,
      "fields_hil_flagged": 2,
      "mappings_created": 23,
      "unmapped_keys": 0,
      "adjustments_made": 3
    },
    "fields": [
      {
        "field_index": 0,
        "label": "Taxpayer Name",
        "field_type": "text",
        "page": 1,
        "value": "Jane Doe",
        "hil_flag": false,
        "verified": true
      },
      {
        "field_index": 8,
        "label": "Total Income",
        "field_type": "text",
        "page": 2,
        "value": "85000",
        "hil_flag": true,
        "verified": false,
        "reason": "Text overlaps adjacent field"
      }
    ],
    "mappings": [
      {
        "user_key": "taxpayer_name",
        "field_index": 0,
        "value_to_fill": "Jane Doe",
        "confidence": 0.95
      }
    ],
    "unmapped_user_keys": [],
    "adjustments_made": ["Field 8: reduced font size from 12pt to 8pt"],
    "qa_feedback": ["Total Income: text overlaps adjacent field"],
    "errors": []
  },
  "errors": null,
  "error_message": null
}
```

**Status values:**

| Status | Meaning |
|---|---|
| `queued` | Waiting for processing |
| `processing` | AI is filling the form |
| `completed` | Done — download from `filled_form_url` |
| `failed` | Something went wrong — check `error_message` |

**Poll every 5-10 seconds** until status is `completed` or `failed`.

### Webhook Notification (Optional)

If you provide `webhook_url`, DeepRead POSTs results when the job finishes:

**Completed:**
```json
{
  "job_id": "<job_id>",
  "status": "completed",
  "created_at": "<ISO 8601 timestamp>",
  "completed_at": "<ISO 8601 timestamp>",
  "result": {
    "filled_form_url": "<signed URL to download filled PDF>",
    "fields_detected": 25,
    "fields_filled": 23,
    "fields_verified": 21,
    "fields_hil_flagged": 2,
    "report": { ... }
  }
}
```

**Failed:**
```json
{
  "job_id": "<job_id>",
  "status": "failed",
  "created_at": "<ISO 8601 timestamp>",
  "completed_at": "<ISO 8601 timestamp>",
  "error": "Form fill timed out after 600s",
  "errors": ["Form fill timed out after 600s"]
}
```

## How It Works (Under the Hood)

```
Upload PDF + JSON data
       │
       ▼
┌──────────────────────┐
│ 1. DETECT FIELDS     │  Vision AI scans every page, finds all fillable areas
│    (visual, not PDF   │  Returns: label, type, page, bounding box coordinates
│     form fields)      │
└──────────┬───────────┘
           ▼
┌──────────────────────┐
│ 2. MAP DATA          │  AI semantically matches your JSON keys → form fields
│    "full_name" →     │  Transforms values: splits names, formats dates,
│    "Full Name" field  │  converts checkboxes, adds currency symbols
└──────────┬───────────┘
           ▼
┌──────────────────────┐
│ 3. FILL FORM         │  Places text at visual coordinates on the PDF
│    coordinate-based   │  Handles: text, checkboxes, dropdowns
│    insertion          │
└──────────┬───────────┘
           ▼
┌──────────────────────┐
│ 4. QA CHECK          │  Vision AI re-reads the filled form to verify:
│    visual verify      │  - Text is readable, not cut off
│                       │  - Positioned correctly, no overlaps
└──────────┬───────────┘
           ▼
┌──────────────────────┐
│ 5. REPAIR (if needed)│  Auto-fixes: shrink font, adjust position, remap
│    per-field fixes    │  If repair fails → flag for human review (hil_flag)
└──────────┬───────────┘
           ▼
      Filled PDF + Report
```

**Key insight:** This is visual coordinate-based filling, not AcroForm-based. It works on **any** PDF — scanned paper forms, government PDFs with no editable fields, custom templates.

## Usage Examples

### Loan Application

```bash
curl -X POST https://api.deepread.tech/v1/form-fill \
  -H "X-API-Key: $DEEPREAD_API_KEY" \
  -F "file=@loan_application.pdf" \
  -F 'form_fields={
    "applicant_name": "Jane Doe",
    "date_of_birth": "03/15/1990",
    "ssn": "123-45-6789",
    "employer": "Acme Corp",
    "annual_income": "95000",
    "loan_amount": "350000",
    "property_address": "456 Oak Ave, Portland OR 97201",
    "loan_type": "30-Year Fixed"
  }'
```

### Insurance Claim

```bash
curl -X POST https://api.deepread.tech/v1/form-fill \
  -H "X-API-Key: $DEEPREAD_API_KEY" \
  -F "file=@claim_form.pdf" \
  -F 'form_fields={
    "policy_number": "INS-2025-78901",
    "insured_name": "Jane Doe",
    "date_of_loss": "06/01/2025",
    "description": "Water damage to basement from pipe burst",
    "estimated_damage": "12500",
    "photos_attached": "true"
  }'
```

### Government Form (W-4, I-9, etc.)

```bash
curl -X POST https://api.deepread.tech/v1/form-fill \
  -H "X-API-Key: $DEEPREAD_API_KEY" \
  -F "file=@w4_form.pdf" \
  -F 'form_fields={
    "first_name": "Jane",
    "last_name": "Doe",
    "ssn": "123-45-6789",
    "address": "123 Main St",
    "city": "Portland",
    "state": "OR",
    "zip": "97201",
    "filing_status": "Single",
    "multiple_jobs": "false"
  }'
```

### Batch Processing (Same Template, Different Data)

```python
import json
import os
import requests
import time

API_KEY = os.environ["DEEPREAD_API_KEY"]
FORM_TEMPLATE = "application.pdf"

applicants = [
    {"full_name": "Jane Doe", "email": "jane@example.com", "dob": "1990-03-15"},
    {"full_name": "John Smith", "email": "john@example.com", "dob": "1985-07-22"},
    {"full_name": "Alice Chen", "email": "alice@example.com", "dob": "1992-11-08"},
]

jobs = []
for i, applicant in enumerate(applicants):
    with open(FORM_TEMPLATE, "rb") as f:
        resp = requests.post(
            "https://api.deepread.tech/v1/form-fill",
            headers={"X-API-Key": API_KEY},
            files={"file": (FORM_TEMPLATE, f, "application/pdf")},
            data={
                "form_fields": json.dumps(applicant),
                "idempotency_key": f"batch-2025-06-{i}",
            },
        )
    job_id = resp.json()["id"]
    jobs.append(job_id)
    print(f"Submitted: {applicant['full_name']} → job {job_id}")

# Poll for results
for job_id in jobs:
    while True:
        result = requests.get(
            f"https://api.deepread.tech/v1/form-fill/{job_id}",
            headers={"X-API-Key": API_KEY},
        ).json()
        if result["status"] in ("completed", "failed"):
            print(f"Job {job_id}: {result['status']}")
            if result["status"] == "completed":
                print(f"  Download: {result['filled_form_url']}")
                print(f"  Fields: {result['fields_filled']}/{result['fields_detected']} filled, "
                      f"{result['fields_hil_flagged']} need review")
            break
        time.sleep(5)
```

## Understanding the Report

### fields_detected vs fields_filled vs fields_verified

| Metric | What it means |
|---|---|
| `fields_detected` | Total form fields AI found on the PDF |
| `fields_filled` | Fields where your data was placed |
| `fields_verified` | Fields that passed visual QA (text readable, positioned correctly) |
| `fields_hil_flagged` | Fields needing human review (AI couldn't fully verify) |

**Typical result:** 90-95% of fields verified, 2-5% flagged for review.

### HIL Flags (Human-in-the-Loop)

A field gets `hil_flag: true` when:
- Text overlaps an adjacent field
- Font had to be shrunk significantly
- Value doesn't visually match field expectations
- Repair attempts didn't fully resolve the issue

**Each flagged field includes a `reason`** explaining why review is needed.

### Unmapped Keys

If your JSON has keys that don't match any form field, they appear in `unmapped_user_keys`. This means:
- The form doesn't have a matching field
- Or the field label is ambiguous

## Idempotency

Prevent duplicate submissions with `idempotency_key`:

```bash
# First request
curl -X POST https://api.deepread.tech/v1/form-fill \
  -H "X-API-Key: $DEEPREAD_API_KEY" \
  -F "file=@form.pdf" \
  -F 'form_fields={"name": "Jane"}' \
  -F "idempotency_key=submission-abc-123"
# → {"id": "<job_id>", "status": "queued"}

# Retry (same key) — returns the same job, no duplicate
curl -X POST https://api.deepread.tech/v1/form-fill \
  -H "X-API-Key: $DEEPREAD_API_KEY" \
  -F "file=@form.pdf" \
  -F 'form_fields={"name": "Jane"}' \
  -F "idempotency_key=submission-abc-123"
# → {"id": "<same job_id as above>", "status": "queued"}  ← SAME JOB
```

## When to Use This Skill

### Use DeepRead Form Fill For:
- **Loan/mortgage applications** — fill 20+ page forms from CRM data
- **Insurance claims** — populate claim forms automatically
- **Government forms** — W-4, I-9, tax forms, permits, benefits applications
- **Legal documents** — contracts, agreements with field placeholders
- **Onboarding packets** — new hire paperwork from HR systems
- **Batch processing** — same template, hundreds of applicants

### Don't Use For:
- **Creating PDFs from scratch** — this fills existing forms, doesn't generate new ones
- **Real-time (<1 second)** — processing takes 15-30 seconds (async)
- **Non-PDF formats** — PDF only (DOCX support coming soon)

## Rate Limits & Pricing

### Free Tier (No Credit Card)
- **2,000 pages/month**
- Full feature access

### Paid Plans
- **PRO**: 50,000 pages/month @ $99/mo
- **SCALE**: Custom volume pricing

**Upgrade:** https://www.deepread.tech/dashboard/billing?utm_source=clawdhub

## Troubleshooting

### Error: 400 "Only PDF files are supported"
Upload a `.pdf` file. Other formats are not yet supported.

### Error: 400 "Invalid JSON in form_fields"
Check your JSON syntax. Must be a valid JSON **object** (not array):
```
✅ {"name": "Jane Doe", "dob": "1990-03-15"}
❌ ["name", "dob"]
❌ "just a string"
```

### Error: 429 "Monthly page quota exceeded"
Upgrade to PRO or wait until next billing cycle.

### Status: "failed" with "Vision model timeout"
The form is very complex or has many pages. Try splitting into smaller sections.

### Fields not mapped correctly
Add more descriptive keys in your JSON. The AI uses your key names to match fields:
```
✅ {"applicant_full_name": "Jane Doe"}  — clear, matches form labels
❌ {"field1": "Jane Doe"}  — ambiguous, hard to map
```

### Some fields flagged for review
This is expected for 2-5% of fields. Check `report.fields` for the `reason` on each flagged field.

## Endpoints Used

| Endpoint | Method | Auth | Purpose |
|---|---|---|---|
| `https://api.deepread.tech/v1/form-fill` | POST | API Key | Submit form + data |
| `https://api.deepread.tech/v1/form-fill/{job_id}` | GET | API Key | Poll for status + results |

## Support

- **Dashboard**: https://www.deepread.tech/dashboard
- **Issues**: https://github.com/deepread-tech/deep-read-service/issues
- **Email**: hello@deepread.tech

---

**Get started free:** https://www.deepread.tech/dashboard/?utm_source=clawdhub
