---
name: docstrange
description: Document extraction API by Nanonets. Convert PDFs and images to markdown, JSON, or CSV with confidence scoring. Use when you need to OCR documents, extract invoice fields, parse receipts, or convert tables to structured data.
---

# DocStrange by Nanonets

Document extraction API — convert PDFs, images, and documents to markdown, JSON, or CSV with per-field confidence scoring.

> **Get your API key:** https://docstrange.nanonets.com/app

## Quick Start

```bash
curl -X POST "https://extraction-api.nanonets.com/api/v1/extract/sync" \
  -H "Authorization: Bearer $DOCSTRANGE_API_KEY" \
  -F "file=@document.pdf" \
  -F "output_format=markdown"
```

Response:
```json
{
  "success": true,
  "record_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "result": {
    "markdown": {
      "content": "# Invoice\n\n**Invoice Number:** INV-2024-001..."
    }
  }
}
```

## Setup

### 1. Get Your API Key

```bash
# Visit the dashboard
https://docstrange.nanonets.com/app
```

Save your API key:
```bash
export DOCSTRANGE_API_KEY="your_api_key_here"
```

### 2. OpenClaw Configuration (Optional)

**Recommended: Use environment variables** (most secure):
```json5
{
  skills: {
    entries: {
      "docstrange": {
        enabled: true,
        // API key loaded from environment variable DOCSTRANGE_API_KEY
      },
    },
  },
}
```

**Alternative: Store in config file** (use with caution):
```json5
{
  skills: {
    entries: {
      "docstrange": {
        enabled: true,
        env: {
          DOCSTRANGE_API_KEY: "your_api_key_here",
        },
      },
    },
  },
}
```

**Security Note:** If storing API keys in `~/.openclaw/openclaw.json`:
- Set file permissions: `chmod 600 ~/.openclaw/openclaw.json`
- Never commit this file to version control
- Prefer environment variables or your agent's secret store when possible
- Rotate keys regularly and limit API key permissions if supported

## Common Tasks

### Extract to Markdown

```bash
curl -X POST "https://extraction-api.nanonets.com/api/v1/extract/sync" \
  -H "Authorization: Bearer $DOCSTRANGE_API_KEY" \
  -F "file=@document.pdf" \
  -F "output_format=markdown"
```

Access content: `response["result"]["markdown"]["content"]`

### Extract JSON Fields

**Simple field list:**
```bash
curl -X POST "https://extraction-api.nanonets.com/api/v1/extract/sync" \
  -H "Authorization: Bearer $DOCSTRANGE_API_KEY" \
  -F "file=@invoice.pdf" \
  -F "output_format=json" \
  -F 'json_options=["invoice_number", "date", "total_amount", "vendor"]' \
  -F "include_metadata=confidence_score"
```

**With JSON schema:**
```bash
curl -X POST "https://extraction-api.nanonets.com/api/v1/extract/sync" \
  -H "Authorization: Bearer $DOCSTRANGE_API_KEY" \
  -F "file=@invoice.pdf" \
  -F "output_format=json" \
  -F 'json_options={"type": "object", "properties": {"invoice_number": {"type": "string"}, "total_amount": {"type": "number"}}}'
```

Response with confidence scores:
```json
{
  "result": {
    "json": {
      "content": {
        "invoice_number": "INV-2024-001",
        "total_amount": 500.00
      },
      "metadata": {
        "confidence_score": {
          "invoice_number": 98,
          "total_amount": 99
        }
      }
    }
  }
}
```

### Extract Tables to CSV

```bash
curl -X POST "https://extraction-api.nanonets.com/api/v1/extract/sync" \
  -H "Authorization: Bearer $DOCSTRANGE_API_KEY" \
  -F "file=@table.pdf" \
  -F "output_format=csv" \
  -F "csv_options=table"
```

### Async Extraction (Large Documents)

For documents >5 pages, use async and poll:

**Queue the document:**
```bash
curl -X POST "https://extraction-api.nanonets.com/api/v1/extract/async" \
  -H "Authorization: Bearer $DOCSTRANGE_API_KEY" \
  -F "file=@large-document.pdf" \
  -F "output_format=markdown"

# Returns: {"record_id": "12345", "status": "processing"}
```

**Poll for results:**
```bash
curl -X GET "https://extraction-api.nanonets.com/api/v1/extract/results/12345" \
  -H "Authorization: Bearer $DOCSTRANGE_API_KEY"

# Returns: {"status": "completed", "result": {...}}
```

## Advanced Features

### Bounding Boxes
Get element coordinates for layout analysis:
```bash
-F "include_metadata=bounding_boxes"
```

### Hierarchy Output
Extract document structure (sections, tables, key-value pairs):
```bash
-F "json_options=hierarchy_output"
```

### Financial Documents Mode
Enhanced table and number formatting:
```bash
-F "markdown_options=financial-docs"
```

### Custom Instructions
Guide extraction with prompts:
```bash
-F "custom_instructions=Focus on financial data. Ignore headers."
-F "prompt_mode=append"
```

### Multiple Formats
Request multiple formats in one call:
```bash
-F "output_format=markdown,json"
```

## When to Use

### Use DocStrange For:
- Invoice and receipt processing
- Contract text extraction
- Bank statement parsing
- Form digitization
- Image OCR (scanned documents)

### Don't Use For:
- Documents >5 pages with sync (use async)
- Video/audio transcription
- Non-document images

## Best Practices

| Document Size | Endpoint | Notes |
|---------------|----------|-------|
| <=5 pages | `/extract/sync` | Immediate response |
| >5 pages | `/extract/async` | Poll for results |

**JSON Extraction:**
- Field list: `["field1", "field2"]` — quick extractions
- JSON schema: `{"type": "object", ...}` — strict typing, nested data

**Confidence Scores:**
- Add `include_metadata=confidence_score`
- Scores are 0-100 per field
- Review fields <80 manually

## Schema Templates

### Invoice
```json
{
  "type": "object",
  "properties": {
    "invoice_number": {"type": "string"},
    "date": {"type": "string"},
    "vendor": {"type": "string"},
    "total": {"type": "number"},
    "line_items": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "description": {"type": "string"},
          "quantity": {"type": "number"},
          "price": {"type": "number"}
        }
      }
    }
  }
}
```

### Receipt
```json
{
  "type": "object",
  "properties": {
    "merchant": {"type": "string"},
    "date": {"type": "string"},
    "total": {"type": "number"},
    "items": {
      "type": "array",
      "items": {"type": "object", "properties": {"name": {"type": "string"}, "price": {"type": "number"}}}
    }
  }
}
```

## Security & Privacy

### Data Handling

**Important:** Documents uploaded to DocStrange are transmitted to `https://extraction-api.nanonets.com` and processed on external servers.

**Before uploading sensitive documents:**
- Review Nanonets' privacy policy and data retention policies: https://docstrange.nanonets.com/docs
- Verify encryption in transit (HTTPS) and at rest
- Confirm data deletion/retention timelines
- Test with non-sensitive sample documents first

**Best practices:**
- Do not upload highly sensitive PII (SSNs, medical records, financial account numbers) until you've confirmed the service's security and compliance posture
- Use API keys with limited permissions/scopes if available
- Rotate API keys regularly (every 90 days recommended)
- Monitor API usage logs for unauthorized access
- Never log or commit API keys to repositories or examples

### File Size Limits

- **Sync endpoint:** Recommended for documents ≤5 pages
- **Async endpoint:** Use for documents >5 pages to avoid timeouts
- **Large files:** Consider using `file_url` with publicly accessible URLs instead of uploading large files directly

### Operational Safeguards

- Always use environment variables or secure secret stores for API keys
- Never include real API keys in code examples or documentation
- Use placeholder values like `"your_api_key_here"` in examples
- Set appropriate file permissions on configuration files (600 for JSON configs)
- Enable API key rotation and monitor usage through the dashboard

## Troubleshooting

**400 Bad Request:**
- Provide exactly one input: `file`, `file_url`, or `file_base64`
- Verify API key is valid

**Sync Timeout:**
- Use async for documents >5 pages
- Poll `/extract/results/{record_id}`

**Missing Confidence Scores:**
- Requires `json_options` (field list or schema)
- Add `include_metadata=confidence_score`

**Authentication Errors:**
- Verify `DOCSTRANGE_API_KEY` environment variable is set
- Check API key hasn't expired or been revoked
- Ensure no extra whitespace in API key value

## Pre-Publish Security Checklist

Before publishing or updating this skill, verify:

- [ ] `package.json` declares `requiredEnv` and `primaryEnv` for `DOCSTRANGE_API_KEY`
- [ ] `package.json` lists API endpoints in `endpoints` array
- [ ] All code examples use placeholder values (`"your_api_key_here"`) not real keys
- [ ] No API keys or secrets are embedded in `SKILL.md` or `package.json`
- [ ] Security & Privacy section documents data handling and risks
- [ ] Configuration examples include security warnings for plaintext storage
- [ ] File permission guidance is included for config files

## References

- **API Docs:** https://docstrange.nanonets.com/docs
- **Get API Key:** https://docstrange.nanonets.com/app
- **Privacy Policy:** https://docstrange.nanonets.com/docs (check for privacy/data policy links)
