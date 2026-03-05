# Output mapping (placeholders → extracted artefacts)

Mistral OCR returns each page's main content as Markdown. When you ask it to extract images and/or tables, the Markdown contains **placeholders** that reference those extracted artefacts.

Common placeholder patterns:

- Images: `![img-0.jpeg](img-0.jpeg)`
- Tables: `[tbl-3.html](tbl-3.html)` or similar

The OCR response also includes structured arrays:

- `page.images`: list of extracted images with bounding boxes and (optionally) `image_base64`
- `page.tables`: list of extracted tables when `table_format` is `"markdown"` or `"html"`

## How the bundled script writes outputs

The script writes:

- `pages/page-XYZ.md`: per-page markdown exactly as returned
- `combined.md`: a concatenation of per-page markdown with clear separators
- `images/<id>`: decoded image bytes, where `<id>` matches the placeholder filename in markdown
- `tables/<id>.(html|md|json)`: tables saved in a format matching what the API returns
- `raw_response.json`: full OCR response for auditing and custom post-processing

## Recommended downstream approach

If you need a fully self-contained Markdown export:

1. Keep the page markdown unchanged.
2. Store extracted images/tables on disk.
3. When rendering, resolve placeholder filenames relative to the output directory.
