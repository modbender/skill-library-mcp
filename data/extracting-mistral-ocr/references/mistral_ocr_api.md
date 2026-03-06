# Mistral OCR API (quick reference)

This skill targets Mistral's OCR endpoint and its companion Files endpoint.

## Endpoints

- **OCR**: `POST https://api.mistral.ai/v1/ocr`
- **Files upload**: `POST https://api.mistral.ai/v1/files` with `purpose="ocr"`

## Default model

- `mistral-ocr-latest`

## Input options (PDF)

Pick the most reliable option for the situation:

1. **Local PDF path** (most common): upload the PDF via the Files endpoint, then OCR using the returned `file_id`.
2. **Public URL**: call OCR directly using a `document_url` (must be reachable by Mistral's API without auth/cookies).

### Upload (Python SDK)

```python
upload = client.files.upload(
    file={"file_name": "document.pdf", "content": open("document.pdf", "rb")},
    purpose="ocr",
)
file_id = upload.id
```

### OCR request fields (common)

```json
{
  "model": "mistral-ocr-latest",
  "document": { "file_id": "..." }
}
```

Common parameters you may set (names match the OCR docs):

- `model`: string
- `document`: one of
  - `{ "type": "document_url", "document_url": "<public url>" }`
  - `{ "type": "image_url", "image_url": "<public url>" }`
  - `{ "file_id": "<uploaded id>" }`
- `table_format`: `null` | `"markdown"` | `"html"`
- `extract_header`: bool (default false)
- `extract_footer`: bool (default false)
- `include_image_base64`: bool (when true, embedded images are returned with base64)
- `pages`: list[int] (0-indexed)
- `image_limit`: int (max images to extract)
- `image_min_size`: int (min width/height for extracted images)
- `document_annotation_prompt`: string (optional)
- `document_annotation_format`: object like `{ "type": "text" | "json_object" | "json_schema" }` (must be provided when using `document_annotation_prompt`)

## Response shape (high level)

Top-level fields:

- `pages`: list[page]
- `model`: string
- `usage_info`: object
- `document_annotation`: string|null (only when using document annotations)

Each `page` commonly includes:

- `index`: page index
- `markdown`: extracted page content in Markdown
- `images`: list[{id, top_left_x, top_left_y, bottom_right_x, bottom_right_y, image_base64?}]
- `tables`: list[...] (when using `table_format="markdown"` or `"html"`)
- `hyperlinks`: list[...]
- `header` / `footer`: strings when enabled
- `dimensions`: object (dpi, width, height)

## Practical notes

- When extracting images/tables, page Markdown will contain placeholders like `![img-0.jpeg](img-0.jpeg)` and `[tbl-3.html](tbl-3.html)`. Map placeholders to the extracted artefacts using the `images` and `tables` fields.
- For high throughput, Mistral recommends using Batch Inference for OCR workloads.
- File upload size limits are documented as 512 MB; for huge PDFs, use page selection or split the document.
