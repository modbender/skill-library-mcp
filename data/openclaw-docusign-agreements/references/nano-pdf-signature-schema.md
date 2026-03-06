# NanoPDF Signature Block Schema

This skill expects NanoPDF to return a JSON object with a `blocks` array.

## Request Contract (expected)

POST `${NANOPDF_BASE_URL}${NANOPDF_DETECT_PATH}`

```json
{
  "document_name": "nda.pdf",
  "document_base64": "<base64>",
  "labels": ["signature"]
}
```

## Response Contract (expected)

```json
{
  "blocks": [
    {
      "id": "blk_001",
      "type": "signature",
      "page": 1,
      "x": 72,
      "y": 540,
      "width": 160,
      "height": 36,
      "confidence": 0.98,
      "signer_key": "client"
    }
  ]
}
```

## Required Fields Per Block

- `type` must be `signature`
- `page` integer, 1-based page number
- `x` and `y` numeric upper-left coordinates

## Optional Fields

- `width`, `height`
- `signer_key` for explicit signer assignment
- `confidence` for quality checks

If your NanoPDF endpoint uses a different schema, adapt `scripts/send_agreement.py` in `extract_signature_blocks`.
