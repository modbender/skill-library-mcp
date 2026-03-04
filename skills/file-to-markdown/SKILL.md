# File to Markdown — Skill

## Overview

Convert files into **clean, structured, AI-ready Markdown** using the `markdown.new` API powered by **Cloudflare Workers AI toMarkdown()**.

Supports 20+ formats including documents, spreadsheets, images, and structured data.

No authentication required (500 requests/day per IP).

---

## When to Use This Skill

Use this skill whenever you need to:

* Extract text from files for LLM processing
* Convert PDFs or Office files into Markdown
* Normalize data into structured text
* Process uploaded user files
* Scrape webpage content into Markdown
* Convert images into AI-generated descriptions + content

Common AI workflows:

* RAG ingestion pipelines
* Knowledge base creation
* Document summarization
* Dataset extraction
* Spreadsheet analysis
* OCR-like extraction from images

---

## Supported Formats

### Documents

* `.pdf`
* `.docx`
* `.odt`

### Spreadsheets

* `.xlsx`
* `.xls`
* `.xlsm`
* `.xlsb`
* `.et`
* `.ods`
* `.numbers`

### Images

* `.jpg`
* `.jpeg`
* `.png`
* `.webp`
* `.svg`

### Text & Structured Data

* `.txt`
* `.md`
* `.csv`
* `.json`
* `.xml`
* `.html`
* `.htm`

Notes:

* Image conversion uses AI object detection + summarization.
* HTML URL conversion uses a web page pipeline.
* Uploaded HTML uses Workers AI conversion.

---

## API Base URL

```
https://markdown.new
```

---

## Endpoints

### 1️⃣ Convert Remote File (Simple GET)

Returns plain Markdown text.

```
GET /:file-url
```

Example:

```bash
curl -s "https://markdown.new/https://example.com/report.pdf"
```

---

### 2️⃣ Convert Remote File (JSON Response)

Returns metadata + Markdown.

```
GET /:file-url?format=json
```

Example:

```bash
curl -s "https://markdown.new/https://example.com/report.pdf?format=json"
```

---

### 3️⃣ Convert Remote File via POST

Use when you want structured JSON response.

```
POST /
Content-Type: application/json
```

Body:

```json
{
  "url": "https://example.com/report.pdf"
}
```

Example:

```bash
curl -s https://markdown.new/ \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com/report.pdf"}'
```

---

### 4️⃣ Upload Local File

Use when file is not publicly accessible.

```
POST /convert
multipart/form-data
```

Example:

```bash
curl -s https://markdown.new/convert \
  -F "file=@document.pdf"
```

---

## Response Formats

### URL Conversion Response

```json
{
  "success": true,
  "url": "https://example.com/report.pdf",
  "title": "Quarterly Report",
  "content": "# Quarterly Report\n\n...",
  "method": "Workers AI (file)",
  "duration_ms": 1200,
  "tokens": 850
}
```

---

### Upload Conversion Response

```json
{
  "success": true,
  "data": {
    "title": "Q4 Report",
    "content": "# Q4 Report\n\n...",
    "filename": "report.xlsx",
    "file_type": ".xlsx",
    "tokens": 1250,
    "processing_time_ms": 320
  }
}
```

---

## Best Practices for AI Agents

### Prefer GET for Simple Workflows

Use:

```
GET /:url
```

When:

* You only need Markdown text
* Speed is important
* No metadata required

---

### Prefer POST for Structured Pipelines

Use POST when:

* Metadata is needed
* Token counts are required
* Monitoring or logging is implemented
* Building automation workflows

---

### File Upload Strategy

Use `/convert` only if:

* File is local
* File is private
* File requires authentication to access

Otherwise always prefer URL conversion.

---

## Error Handling Strategy

Agents should:

1. Check `"success": true`
2. Retry once if network failure
3. Validate content length > 0
4. Fallback to alternate extraction if needed

---

## Rate Limits

* 500 requests/day per IP without API key
* No signup required

Agents should:

* Cache results when possible
* Avoid duplicate conversions

---

## Integration Examples

### JavaScript (Node.js)

```js
const res = await fetch("https://markdown.new/", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    url: "https://example.com/file.pdf"
  })
});

const data = await res.json();
console.log(data.content);
```

---

### Python

```python
import requests

res = requests.post(
    "https://markdown.new/",
    json={"url": "https://example.com/file.pdf"}
)

data = res.json()
print(data["content"])
```

---

## Agent Decision Tree

If user provides:

| Input Type      | Action                 |
| --------------- | ---------------------- |
| Public file URL | Use GET or POST        |
| Local file      | Use POST /convert      |
| Image           | Convert then summarize |
| Spreadsheet     | Convert then analyze   |
| Webpage         | Convert URL HTML       |

---

## Output Expectations

The Markdown should be:

* Clean
* Structured
* AI-friendly
* Minimal noise
* Ready for LLM ingestion

---

## Limitations

* Complex PDF layouts may lose formatting
* Large spreadsheets may be truncated
* Images rely on AI interpretation accuracy
* Token limits may apply

---

## Summary

This skill provides a **universal file-to-Markdown conversion layer** for AI systems with:

* No authentication
* Simple HTTP interface
* Multi-format support
* Structured output
* Fast processing

Ideal for document ingestion, RAG pipelines, and automation agents.

---
