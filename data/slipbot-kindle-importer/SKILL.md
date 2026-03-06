---
name: kindle-import
description: Import reading notes from Kindle HTML exports into the slipbox. Use when user sends a Kindle notebook export file (HTML/XHTML). Parses book title and author, extracts only user's Notes (skips Highlights), then runs slipbot for each.
---

# Kindle Import

Parse Kindle notebook exports (HTML) and create slipbox entries for user's notes.

## Input Format

Kindle exports are XHTML files with this structure:

```html
<div class="bookTitle">Book Title Here</div>
<div class="authors">Author Name</div>
...
<div class="sectionHeading">Chapter/Section Name</div>
<div class="noteHeading">Highlight (yellow) - Section > Page X</div>
<div class="noteText">Highlighted text from book</div>
<div class="noteHeading">Note - Section > Page X</div>
<div class="noteText">User's own note</div>
```

**Key distinction:**
- `noteHeading` starting with "Highlight" → book text → **Skip**
- `noteHeading` starting with "Note" → user's own thoughts → **Import**

## Parsing Rules

### Metadata Extraction
1. Book title: content of `.bookTitle` div
2. Author: content of `.authors` div
3. Source type: `book`

### Content Extraction
1. Find all `.noteHeading` elements
2. If heading starts with "Note" → get the following `.noteText` content → **import**
3. If heading starts with "Highlight" → **skip**
4. Section info (e.g., "Client-side/Stateless Sessions > Page 28") can be ignored

## Workflow

1. **Parse file** → extract book title and author
2. **Extract user notes** → collect only Note entries (not Highlights)
3. **Precheck** → show user: book title, author, note count, ask for confirmation
4. **On confirmation** → for each note, invoke slipbot:
   - Type: note (`-` prefix)
   - Source: `~ book, {title} by {author}`
   - Let slipbot handle: filename, tags, links, graph update
5. **Report** → count of notes created

## Example

**Input file metadata:**
- Title: "The JWT Handbook"
- Author: "Sebastian E Peyrott"

**Parsed entries:**
```
Highlight (yellow) - Page 28: "This is easily solved by..." → SKIP
Note - Page 28: "Applications should not allow unsigned JWTs..." → IMPORT
```

**Slipbot call:**
```
- Applications should not allow unsigned JWTs to be considered valid. ~ book, The JWT Handbook by Sebastian E Peyrott
```

## Edge Cases

- **No user notes** (only Highlights): Report "no notes to import"
- **Multiple authors**: Preserve as-is from the file
- **Missing author**: Use "Unknown" as author
- **Special characters in title/content**: Preserve as-is
- **HTML entities**: Decode before storing (&amp; → &, etc.)

## Supported File Types

- `.html` files exported from Kindle app
- XHTML files (same structure)
- Files sent via Telegram (application/xml or text/plain mime types)
