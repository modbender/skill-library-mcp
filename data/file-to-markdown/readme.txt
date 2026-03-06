File to Markdown Skill

Overview
This skill converts files into clean, structured, AI-ready Markdown using the https://markdown.new API powered by Cloudflare Workers AI.

No authentication is required. The service supports 500 requests per day per IP.

Supported Formats

* Documents: PDF, DOCX, ODT
* Spreadsheets: XLSX, XLS, XLSM, XLSB, ODS, NUMBERS, ET
* Images: JPG, PNG, WEBP, SVG
* Text/Data: TXT, MD, CSV, JSON, XML, HTML

Capabilities

* Convert remote files via URL
* Upload local files for conversion
* Extract structured content for AI processing
* Generate Markdown suitable for RAG pipelines
* Convert images into AI-generated descriptions
* Normalize documents for summarization or analysis

Typical Use Cases

* Knowledge base ingestion
* Document summarization
* Dataset extraction
* Spreadsheet analysis
* Webpage content conversion
* Automation workflows

API Base
https://markdown.new

Key Endpoints
GET /:url
Convert a public file URL to Markdown.

POST /
Send a URL in JSON and receive structured metadata + Markdown.

POST /convert
Upload a local file when no public URL is available.

Notes

* Prefer URL conversion when possible for speed.
* Use file upload only for private or local files.
* Complex layouts may lose some formatting.
* Results are optimized for AI consumption rather than visual fidelity.

For full documentation and examples, see SKILL.md.
