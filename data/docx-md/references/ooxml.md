# OOXML Reference for DOCX (Word)

DOCX is a ZIP archive. This skill’s **modify** flow: the AI returns **standard edit JSON** (insert / delete / comments + positions) → the program **converts JSON to OOXML** (`w:ins` / `w:del` / comment anchors) → writes back to the docx. Below is the OOXML structure reference used for reading and writing.

Key parts:

- `word/document.xml` – main body (paragraphs, tables, runs, revisions, comment references)
- `word/comments.xml` – comment content (id, author, date, text)
- `word/_rels/document.xml.rels` – relationships (e.g. comments part)
- `[Content_Types].xml` – part types

Namespace used below: `w` = `http://schemas.openxmlformats.org/wordprocessingml/2006/main`.

## Reading

### Body and text

- Body: `w:body` in `word/document.xml`.
- Paragraphs: `w:p`; runs: `w:r`; inline text: `w:t`.
- **Insertions**: `w:ins` contains runs that are “tracked insertions”; take `w:t` inside for the inserted text.
- **Deletions**: `w:del` contains runs that are “tracked deletions”; take `w:t` inside for the deleted text.
- Final view (accept all): concatenate text from normal runs and from `w:ins`; ignore `w:del`.

### Comments

- In `word/comments.xml`: root `w:comments`, each comment is `w:comment` with attributes e.g. `w:id`, `w:author`, `w:date`, `w:initials`. Text is in child `w:p`/`w:r`/`w:t`.
- In `word/document.xml`: a comment is linked by:
  - `w:commentRangeStart w:id="…"` (start of range)
  - optional content (the range the comment refers to)
  - `w:commentRangeEnd w:id="…"`
  - `w:commentReference w:id="…"` (reference to the comment)
- Match `w:id` in document to `w:id` in comments to associate comment text with position.

## Writing (edit JSON → OOXML mapping)

- **insert** (or replace): At the corresponding block position, write `w:ins` containing the new text.
- **delete**: Wrap the original text at that position in `w:del` (requires script support).
- **comments**: Add a new `w:comment` in `word/comments.xml` and insert commentRangeStart/End and commentReference in the document.

### Adding revisions (tracked changes)

- Ensure tracking is on (e.g. in `word/settings.xml`: `w:trackRevisions` or equivalent).
- For new text: wrap the run(s) in `w:ins` with attributes e.g. `w:id`, `w:author`, `w:date`.
- For removed text: wrap the run(s) in `w:del` with the same kind of attributes.
- Use unique `w:id` values and consistent author/date so Word shows revisions correctly.

### Adding comments

1. In `word/comments.xml`: add a new `w:comment` with a new `w:id`, `w:author`, `w:date`, and body (`w:p`/`w:r`/`w:t`).
2. In `word/document.xml` at the desired position, insert in order:
   - `w:commentRangeStart w:id="<same id>"`
   - (optional) the range of content the comment refers to
   - `w:commentRangeEnd w:id="<same id>"`
   - `w:commentReference w:id="<same id>"`
3. If the comments part is new or changed, update `word/_rels/document.xml.rels` and `[Content_Types].xml` so the package is valid.

### Finalize (accept all, remove comments)

- **Accept all revisions**: Build a new body that contains only the final text (include content from `w:ins`, omit content from `w:del`), with no `w:ins` or `w:del` elements. Replace `w:body` in `word/document.xml` with this.
- **Remove all comments**: Delete every `w:commentRangeStart`, `w:commentRangeEnd`, and `w:commentReference` from `word/document.xml`. Remove or empty `word/comments.xml`, and remove its relationship and Content Type entry if the part is removed.

## Tools

- Python: `zipfile` + `lxml` (or `xml.etree`) to unzip, parse, and modify XML; then re-zip.
- Node: `jszip` + `fast-xml-parser` (or similar) to do the same. No language-specific OOXML limitation.
