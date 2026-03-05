# Jmail Data API — Complete Reference

Source: https://jmail.world/docs/llms.txt

## Overview

The Jmail Data API serves **static Parquet files** from `data.jmail.world`. No API key, no rate limit, no authentication required.

All datasets available as both Parquet and NDJSON (gzipped) at `https://data.jmail.world/v1/`.

## Web Search API

```
GET https://jmail.world/api/emails/search
```

**Parameters:**
| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `q` | string | required | Search query |
| `limit` | int | 50 | Results per page |
| `page` | int | 1 | Page number |
| `source` | string | "all" | Filter by source |
| `from` | string | — | Filter by sender name |

**Example:**
```bash
curl "https://jmail.world/api/emails/search?q=flight+manifest&limit=10&page=1"
```

## Datasets

### Emails
- **Full:** `emails.parquet` (334MB, 1.78M records) — includes body text
- **Slim:** `emails-slim.parquet` (41MB, 1.78M records) — metadata only

**Slim columns:** id, doc_id, sender, subject, to_recipients (json), cc_recipients (json), bcc_recipients (json), sent_at (timestamp), account_email, email_drop_id, epstein_is_sender (bool)

**Full adds:** content_markdown, content_html, attachments (int)

### Documents
`documents.parquet` (25MB, 1.41M records)

**Columns:** id, source, release_batch, original_filename, page_count, size, document_description, has_thumbnail

**Full-text shards** (too large for single file):
- `documents-full/VOL00008.parquet` — DOJ Volume 8
- `documents-full/VOL00009.parquet` — DOJ Volume 9
- `documents-full/VOL00010.parquet` — DOJ Volume 10
- `documents-full/DataSet11.parquet` — DOJ Dataset 11
- `documents-full/other.parquet` — House Oversight, court records, etc.

### Photos
`photos.parquet` (~1MB, 18K records)

**Columns:** id, source, release_batch, original_filename, content_type (MIME), width (px), height (px), image_description (AI-generated)

### People
`people.parquet` (<100KB, 473 records)

**Columns:** id, name, source, photo_count

### Photo Faces
`photo_faces.parquet` (<100KB, 975 records)

Links photos to identified people via `person_id`.

### iMessage Conversations
`imessage_conversations.parquet`

**Columns:** id, slug, name, bio, photo, last_message, last_message_time, pinned, confirmed, source_files (json), message_count

### iMessage Messages
`imessage_messages.parquet`

**Columns:** id, conversation_slug, message_index, text, sender ("me" = Epstein, "them" = contact), time, timestamp, source_file, sender_name

### Star Counts
`star_counts.parquet` (~2MB, 414K records)

Crowd-sourced star/interest counts per entity.

### Release Batches
`release_batches.parquet` (<10KB)

## DuckDB Quick Reference

```sql
-- Top senders
SELECT sender, COUNT(*) as n
FROM read_parquet('https://data.jmail.world/v1/emails-slim.parquet')
GROUP BY sender ORDER BY n DESC LIMIT 20;

-- Epstein's sent emails
SELECT subject, sent_at, to_recipients
FROM read_parquet('https://data.jmail.world/v1/emails-slim.parquet')
WHERE epstein_is_sender = true
ORDER BY sent_at DESC LIMIT 20;

-- Search documents
SELECT original_filename, document_description, page_count
FROM read_parquet('https://data.jmail.world/v1/documents.parquet')
WHERE document_description ILIKE '%flight%'
LIMIT 20;

-- Photo appearances by person
SELECT p.name, COUNT(*) as appearances
FROM read_parquet('https://data.jmail.world/v1/photo_faces.parquet') pf
JOIN read_parquet('https://data.jmail.world/v1/people.parquet') p
  ON pf.person_id = p.id
GROUP BY p.name ORDER BY appearances DESC;

-- Star counts by entity type
SELECT entity_type, SUM(count) as total_stars
FROM read_parquet('https://data.jmail.world/v1/star_counts.parquet')
GROUP BY entity_type ORDER BY total_stars DESC;

-- iMessage conversations
SELECT name, message_count, last_message
FROM read_parquet('https://data.jmail.world/v1/imessage_conversations.parquet')
ORDER BY message_count DESC;

-- Messages in a conversation
SELECT sender, text, timestamp
FROM read_parquet('https://data.jmail.world/v1/imessage_messages.parquet')
WHERE conversation_slug = 'ghislaine-maxwell'
ORDER BY message_index;
```

## NDJSON Alternatives

Every dataset also available as `.ndjson.gz`:
```
https://data.jmail.world/v1/emails-slim.ndjson.gz
https://data.jmail.world/v1/documents.ndjson.gz
https://data.jmail.world/v1/photos.ndjson.gz
...etc
```

## Web Pages (browser required)
- `https://jmail.world/person/SLUG` — Person profile page
- `https://jmail.world/flights` — Flight records visualization
- `https://jmail.world/photos` — Photo browser
- `https://jmail.world/drive/new-only` — Newly released documents
- `https://jmail.world/topic/SLUG` — Topic/investigation pages
