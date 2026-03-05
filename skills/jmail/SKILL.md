---
name: jmail
version: 1.6.4
description: Search and analyze the Jeffrey Epstein email archive (1.78M emails, 4,500+ iMessages, 18K photos, 1.4M documents, 473 identified people) via jmail.world's official Data API. DuckDB/Parquet queries, Web Search API, and file downloads. No auth needed.
metadata: {"homepage": "https://jmail.world", "source": "https://jmail.world/docs/introduction", "author": "Fabian & Nyx", "category": "research", "license": "MIT"}
---

# jmail-world — Epstein Archive Search & Analysis

Search and analyze Jeffrey Epstein's email archive, iMessages, documents, photos, and people on [jmail.world](https://jmail.world).

## When to Use

- Researching Epstein connections and communications
- Finding emails between specific people
- Exploring iMessage conversations
- Analyzing communication networks and timelines
- Looking up people identified in photos
- Searching documents (DOJ releases, court records)

## Data Access — Two Methods

### 1. Web Search API (quick lookups)
```
GET https://jmail.world/api/emails/search?q=QUERY&limit=50&page=1&source=all&from=NAME
```
No auth needed. Use `web_fetch` or `curl`. Good for quick keyword searches.

### 2. DuckDB + Parquet (deep analysis)
All datasets served as static Parquet files from `https://data.jmail.world/v1/`. No API key, no rate limit, no auth.

Use the included scripts:
```bash
# Full-text email search (Web API)
bash scripts/jmail-search.sh "query text"
bash scripts/jmail-search.sh "scopolamine" --from "Epstein" --limit 20

# DuckDB queries (local Parquet, no rate limits)
bash scripts/jmail-duckdb.sh search "flight manifest"
bash scripts/jmail-duckdb.sh person "Ghislaine Maxwell"
bash scripts/jmail-duckdb.sh imessages "ghislaine-maxwell"
bash scripts/jmail-duckdb.sh imessage-search "AfD"
bash scripts/jmail-duckdb.sh imessage-search "Merkel" --from "Bannon"
bash scripts/jmail-duckdb.sh imessage-list
bash scripts/jmail-duckdb.sh network "Bill Clinton"
bash scripts/jmail-duckdb.sh timeline "2005-01-01" "2005-12-31"
bash scripts/jmail-duckdb.sh top-senders
bash scripts/jmail-duckdb.sh people
bash scripts/jmail-duckdb.sh documents "flight"
bash scripts/jmail-duckdb.sh photos "person-name"
bash scripts/jmail-duckdb.sh photo-search "pool"
bash scripts/jmail-duckdb.sh photo-download "EFTA00000002-0.png" ./output
bash scripts/jmail-duckdb.sh download "EFTA02406146"
bash scripts/jmail-duckdb.sh download "HOUSE_OVERSIGHT_034601"
bash scripts/jmail-duckdb.sh stars
```

## Available Datasets

| Dataset | URL | Size | Records |
|---------|-----|------|---------|
| Emails (full) | `emails.parquet` | 334MB | 1.78M |
| Emails (slim) | `emails-slim.parquet` | 41MB | 1.78M |
| Documents | `documents.parquet` | 25MB | 1.41M |
| Photos | `photos.parquet` | ~1MB | 18K |
| People | `people.parquet` | <100KB | 473 |
| Photo Faces | `photo_faces.parquet` | <100KB | 975 |
| iMessage Conversations | `imessage_conversations.parquet` | — | — |
| iMessage Messages | `imessage_messages.parquet` | — | — |
| Star Counts | `star_counts.parquet` | ~2MB | 414K |
| Release Batches | `release_batches.parquet` | <10KB | — |

All under `https://data.jmail.world/v1/`.

## Key Schemas

### Email Columns (slim)
`id`, `doc_id`, `sender`, `subject`, `to_recipients` (json), `cc_recipients` (json), `bcc_recipients` (json), `sent_at` (timestamp), `account_email`, `email_drop_id`, `epstein_is_sender` (bool)

### Email Additional (full)
`content_markdown`, `content_html`, `attachments` (int)

### iMessage Conversations
`id`, `slug`, `name`, `bio`, `photo`, `last_message`, `last_message_time`, `pinned`, `confirmed`, `source_files` (json), `message_count`

### iMessage Messages
`id`, `conversation_slug`, `message_index`, `text`, `sender` ("me" = Epstein, "them" = contact), `time`, `timestamp`, `source_file`, `sender_name`

### People
`id`, `name`, `source`, `photo_count`

### Documents
`id`, `source`, `release_batch`, `original_filename`, `page_count`, `size`, `document_description`, `has_thumbnail`

## Web Pages (browser needed)
- `/person/SLUG` — Person profile
- `/flights` — Flight records
- `/photos` — Photo browser
- `/drive/new-only` — New documents
- `/topic/SLUG` — Topic pages

## Document Full-Text Search

Documents have **sharded full-text** files (large downloads):
- `documents-full/VOL00008.parquet` — DOJ Volume 8
- `documents-full/VOL00009.parquet` — DOJ Volume 9
- `documents-full/VOL00010.parquet` — DOJ Volume 10
- `documents-full/DataSet11.parquet` — DOJ Dataset 11
- `documents-full/other.parquet` — House Oversight, court records

Query with DuckDB:
```sql
SELECT id, original_filename, extracted_text
FROM read_parquet('https://data.jmail.world/v1/documents-full/other.parquet')
WHERE extracted_text ILIKE '%rothschild%'
LIMIT 10;
```

## Photo Columns (full schema)
`id`, `source`, `release_batch`, `original_filename`, `content_type` (MIME), `width` (px), `height` (px), `image_description` (AI-generated)

Search photos by description:
```sql
SELECT original_filename, image_description, width, height
FROM read_parquet('https://data.jmail.world/v1/photos.parquet')
WHERE image_description ILIKE '%pool%'
LIMIT 20;
```

## Downloading Files

### Universal Download (any document, email, or photo)
```bash
# Download by document ID — auto-detects type and source
bash scripts/jmail-duckdb.sh download "EFTA02406146"                    # DOJ email PDF
bash scripts/jmail-duckdb.sh download "HOUSE_OVERSIGHT_034601"          # House Oversight photo
bash scripts/jmail-duckdb.sh download "COURT_giuffre-115cv07433_1"      # Court document
bash scripts/jmail-duckdb.sh download "vol00009-efta00462570-pdf"       # DOJ volume scan
bash scripts/jmail-duckdb.sh download "EFTA02406146" ./output-dir      # Custom output dir
```

**Supported sources:**
| ID Pattern | Type | Format |
|-----------|------|--------|
| `EFTA*` | DOJ emails & photos | PDF |
| `vol*` | DOJ volume scans | PDF |
| `HOUSE_OVERSIGHT_*` | House Oversight photos | JPG (direct) |
| `COURT_giuffre*` | Giuffre court docs | PDF |

### Photo Search & Download
```bash
# Search photos by AI-generated description
bash scripts/jmail-duckdb.sh photo-search "swimming pool"
bash scripts/jmail-duckdb.sh photo-search "forced entry"

# Download a specific photo (DOJ: extracts PNG from PDF, HO: direct JPG)
bash scripts/jmail-duckdb.sh photo-download "EFTA00000002-0.png"
bash scripts/jmail-duckdb.sh photo-download "HOUSE_OVERSIGHT_034601.JPG" ./output
```

DOJ photos are stored as single-page PDFs — the download command automatically extracts the embedded image as PNG using `pdfimages`. House Oversight photos are direct JPGs. If `pdfimages` is not installed, DOJ photos are saved as PDF.

## Security

- **SQL injection prevention:** All user input is whitelist-sanitized (alphanumeric + safe chars only). SQL meta-characters, operators, and keywords are stripped before query construction.
- **Path traversal prevention:** Parquet filenames and document IDs are validated against strict patterns before use in file operations.
- **Read-only queries:** All DuckDB operations are `SELECT` on `read_parquet()` — no writes, no code execution, no network access beyond the cached Parquet files.
- **Data source:** All data comes from [jmail.world](https://jmail.world)'s public Parquet files and [assets.getkino.com](https://assets.getkino.com) (DOJ document mirror). No private APIs or credentials involved.

## Requirements
- **DuckDB** (`duckdb` CLI) — must be installed manually (`apt install duckdb` / `brew install duckdb` / [duckdb.org](https://duckdb.org/docs/installation/))
- **curl** — for web search API and downloading Parquet files
- **python3** — for URL encoding in search script
- **pdfimages** (optional, for photo-download PNG extraction) — `apt install poppler-utils`
- **jq** (optional, for JSON formatting)

## References
- [Official Docs](https://jmail.world/docs/introduction)
- [Docs Index for LLMs](https://jmail.world/docs/llms.txt)
- [API Reference](references/api-docs.md)
- [DuckDB Examples](https://jmail.world/docs/duckdb)
- [Python Client (external)](https://jmail.world/docs/python-client) — not bundled, see official docs
- [Datasets & URLs](https://jmail.world/docs/datasets)
