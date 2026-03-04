# Google Docs via TapAuth

## Provider Key

Use `google_docs` as the provider name.

## Available Scopes

| Scope | Access |
|-------|--------|
| `documents.readonly` | View documents |
| `documents` | Full read/write access to documents |

## Example: Create a Grant

```bash
./scripts/tapauth.sh google_docs "documents.readonly" "Doc Reader"
```

## Example: Read a Document

```bash
curl -H "Authorization: Bearer <token>" \
  "https://docs.googleapis.com/v1/documents/DOCUMENT_ID"
```

## Example: Insert Text

```bash
curl -X POST -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  "https://docs.googleapis.com/v1/documents/DOCUMENT_ID:batchUpdate" \
  -d '{
    "requests": [{"insertText": {"location": {"index": 1}, "text": "Hello, World!\n"}}]
  }'
```

## Gotchas

- **Document ID:** Found in the URL: `docs.google.com/document/d/{DOCUMENT_ID}/edit`
- **Structured content:** The API returns a detailed JSON structure with paragraphs, runs, and formatting — not plain text. You'll need to traverse the `body.content` array.
- **Batch updates:** All mutations use `batchUpdate` with an array of requests. You can combine multiple operations in one call.
- **Index-based editing:** Insertions and deletions reference character indices. Read the document first to determine correct positions.
- **Token refresh:** Google tokens expire after ~1 hour. Call the TapAuth token endpoint again to get a fresh one.

## Recommended Minimum Scopes

| Use Case | Scopes |
|----------|--------|
| Read documents | `documents.readonly` |
| Read & write | `documents` |
