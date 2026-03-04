---
domain: rss-manager
topic: feed-formats-parsing-and-content-extraction
priority: high
ttl: 30d
---

# RSS/Atom Feed Formats, XML Parsing & Content Extraction

## Feed Format Specifications

### RSS 2.0 (Really Simple Syndication)

RSS 2.0 is the most widely deployed syndication format. A valid RSS 2.0 document is XML with a root `<rss>` element containing a single `<channel>`.

#### Channel-Level Elements

| Element | Required | Description |
|---------|----------|-------------|
| `<title>` | Yes | Name of the feed (e.g., "TechCrunch") |
| `<link>` | Yes | URL of the HTML website associated with the feed |
| `<description>` | Yes | Summary of what the feed contains |
| `<language>` | No | Language code (e.g., "en-us", "zh-cn") |
| `<lastBuildDate>` | No | Last time feed content changed (RFC 822 date) |
| `<pubDate>` | No | Publication date of the feed content (RFC 822 date) |
| `<ttl>` | No | Minutes the feed can be cached before refresh |
| `<image>` | No | Channel logo with `<url>`, `<title>`, `<link>` sub-elements |
| `<generator>` | No | Software that generated the feed |
| `<managingEditor>` | No | Email of the editorial contact |
| `<category>` | No | One or more categories for the feed |

#### Item-Level Elements

| Element | Required | Description |
|---------|----------|-------------|
| `<title>` | Conditional | Title of the article (required if no description) |
| `<link>` | No | URL of the full article |
| `<description>` | Conditional | Article summary or full content (required if no title) |
| `<author>` | No | Email address of the author |
| `<category>` | No | One or more categories |
| `<pubDate>` | No | Publication date (RFC 822 format) |
| `<guid>` | No | Globally unique identifier; `isPermaLink="true"` means it is a URL |
| `<enclosure>` | No | Attached media; attributes: `url`, `length`, `type` |
| `<comments>` | No | URL of the comments page |
| `<source>` | No | Original feed the item came from; attribute: `url` |

#### RSS 2.0 Namespace Extensions

Common namespace extensions enrich standard RSS:

- **`content:encoded`** (xmlns:content="http://purl.org/rss/1.0/modules/content/") — Full HTML content body, preferred over `<description>` for complete article text
- **`dc:creator`** (xmlns:dc="http://purl.org/dc/elements/1.1/") — Dublin Core author name (more reliable than `<author>`)
- **`dc:date`** — ISO 8601 date (more precise than `<pubDate>`)
- **`slash:comments`** — Comment count (integer)
- **`wfw:commentRss`** — RSS feed URL for the item's comments
- **`media:content`** — Rich media attachments with `url`, `medium`, `type`, `width`, `height`
- **`media:thumbnail`** — Thumbnail image URL

### RSS 1.0 (RDF Site Summary)

RSS 1.0 is RDF-based and uses XML namespaces extensively. Less common than RSS 2.0 but still found in academic and government feeds.

#### Key Differences from RSS 2.0

- Root element is `<rdf:RDF>` (not `<rss>`)
- Items are listed both inside `<channel><items><rdf:Seq>` as references and as top-level `<item>` elements
- Uses `rdf:about` attribute for resource identification
- Relies heavily on Dublin Core (`dc:`) namespace for metadata
- Extensible through RDF modules: `mod_syndication` (update schedule), `mod_taxonomy` (topic classification)

### Atom 1.0 (RFC 4287)

Atom is a more formally specified format than RSS, with clearer semantics and mandatory fields.

#### Feed-Level Elements

| Element | Required | Description |
|---------|----------|-------------|
| `<title>` | Yes | Feed title (supports `type` attribute: text, html, xhtml) |
| `<id>` | Yes | Permanent, universally unique feed identifier (IRI) |
| `<updated>` | Yes | Last time the feed was modified (RFC 3339 / ISO 8601) |
| `<author>` | Yes | At least one `<author>` with `<name>`, optional `<email>`, `<uri>` |
| `<link>` | Yes | Must include `rel="self"` (feed URL) and `rel="alternate"` (website URL) |
| `<subtitle>` | No | Feed description |
| `<generator>` | No | Software that generated the feed |
| `<icon>` | No | Small feed icon URL |
| `<logo>` | No | Feed logo URL |
| `<rights>` | No | Copyright notice |
| `<category>` | No | One or more categories with `term`, `scheme`, `label` attributes |

#### Entry-Level Elements

| Element | Required | Description |
|---------|----------|-------------|
| `<title>` | Yes | Entry title (with `type` attribute) |
| `<id>` | Yes | Permanent unique identifier for the entry (IRI) |
| `<updated>` | Yes | Last modification timestamp |
| `<published>` | No | Original publication timestamp |
| `<author>` | Conditional | Required if feed-level author is absent |
| `<content>` | Recommended | Full entry content; `type` attribute: text, html, xhtml, or media type |
| `<summary>` | Recommended | Short summary; required if `<content>` is absent or non-text |
| `<link>` | Recommended | `rel="alternate"` for the article URL |
| `<category>` | No | One or more categories |
| `<contributor>` | No | Additional contributors |
| `<source>` | No | Original feed metadata if the entry was aggregated |

## XML Parsing Considerations

### Encoding Detection Priority

1. HTTP `Content-Type` header charset (highest priority)
2. XML declaration encoding attribute: `<?xml version="1.0" encoding="UTF-8"?>`
3. BOM (Byte Order Mark) detection
4. Default to UTF-8 if none specified

### Common Encoding Issues

- **Double encoding**: Content encoded as UTF-8 then re-encoded, producing mojibake (e.g., `Ã©` instead of `e`)
- **Windows-1252 mislabeled as ISO-8859-1**: Characters in the 0x80-0x9F range render incorrectly
- **HTML entities in XML**: `&nbsp;` is valid in HTML but not in XML -- must use `&#160;` or be wrapped in CDATA
- **Unescaped ampersands**: `&` in URLs or text breaks XML parsing -- must be `&amp;`

### CDATA Section Handling

Many feeds wrap HTML content in CDATA sections to avoid XML escaping issues:

```xml
<description><![CDATA[<p>Article with <a href="https://example.com">links</a> and <img src="photo.jpg" /></p>]]></description>
```

Processing steps:
1. Extract raw content from CDATA (stripping `<![CDATA[` and `]]>`)
2. Parse the inner HTML separately
3. Sanitize: strip `<script>`, `<iframe>`, event handlers, `javascript:` URIs
4. Extract plain text for indexing; preserve HTML for display

### Namespace Resolution

Feeds commonly use multiple namespaces. A robust parser must:

1. Resolve namespace prefixes to their URIs (prefixes may differ between feeds)
2. Recognize elements by namespace URI, not prefix (e.g., `content:encoded` and `c:encoded` are the same if both map to `http://purl.org/rss/1.0/modules/content/`)
3. Handle default namespace declarations on the root element
4. Gracefully ignore unknown namespaces rather than failing

## Content Extraction

### Extracting Article Text

Priority order for obtaining article body:

1. **Atom `<content type="html">`** or **`<content type="xhtml">`** -- fullest content
2. **RSS `<content:encoded>`** -- full HTML body (namespace extension)
3. **Atom `<summary>`** -- may be full text or truncated
4. **RSS `<description>`** -- may be full text, truncated, or just a snippet
5. **Fetch the linked URL** -- fallback when feed only provides a title or minimal snippet

### Metadata Extraction Checklist

For each feed item, extract and normalize:

| Field | Primary Source | Fallback | Normalization |
|-------|---------------|----------|---------------|
| Title | `<title>` | First line of description | Strip HTML, decode entities, trim whitespace |
| URL | `<link>` / `<guid isPermaLink="true">` | `<id>` (Atom) | Canonicalize: lowercase host, remove tracking params |
| Author | `<dc:creator>` / `<author><name>` | `<author>` (email) / `<managingEditor>` | Extract name, discard email if present |
| Date | `<dc:date>` / `<published>` / `<updated>` | `<pubDate>` | Parse to ISO 8601 UTC; handle RFC 822, RFC 3339, and common non-standard formats |
| Body | `<content:encoded>` / `<content>` | `<description>` / `<summary>` | Sanitize HTML, extract plain text, calculate word count |
| Categories | `<category>` (multiple) | `<dc:subject>` | Normalize casing, map synonyms |
| Media | `<enclosure>` / `<media:content>` | `<media:thumbnail>` / embedded `<img>` | Extract URL, MIME type, dimensions |
| GUID | `<guid>` / `<id>` | URL | Use as-is for deduplication key |

### Date Parsing

Feeds use inconsistent date formats. A robust parser must handle:

- **RFC 822**: `Mon, 15 Jan 2024 13:45:00 GMT` (RSS 2.0 standard)
- **RFC 3339 / ISO 8601**: `2024-01-15T13:45:00Z` (Atom standard)
- **Non-standard variations**: `Jan 15, 2024`, `2024/01/15`, `15-01-2024`, `1705322700` (Unix timestamp)
- **Timezone ambiguity**: `EST` vs `-0500`; always convert to UTC for consistent comparison
- **Missing timezone**: Assume UTC and flag as uncertain

### URL Canonicalization

To detect duplicate URLs pointing to the same article:

1. Convert scheme and host to lowercase: `HTTPS://WWW.Example.COM` -> `https://www.example.com`
2. Remove default ports: `:80` for HTTP, `:443` for HTTPS
3. Remove trailing slashes on paths (unless the path is `/`)
4. Sort query parameters alphabetically
5. Remove known tracking parameters: `utm_source`, `utm_medium`, `utm_campaign`, `utm_content`, `utm_term`, `ref`, `source`, `fbclid`, `gclid`, `mc_cid`, `mc_eid`
6. Decode unnecessary percent-encoding: `%41` -> `A`
7. Remove fragment identifiers (`#section`) unless they are part of a single-page app route

### Feed Discovery

When given a website URL instead of a feed URL, discover feeds by:

1. Check `<link rel="alternate" type="application/rss+xml">` in HTML `<head>`
2. Check `<link rel="alternate" type="application/atom+xml">` in HTML `<head>`
3. Try common paths: `/feed`, `/rss`, `/atom.xml`, `/feed.xml`, `/rss.xml`, `/index.xml`, `/feeds/posts/default` (Blogger)
4. Check `/.well-known/` resources
5. Parse the page for embedded feed links in the body content
