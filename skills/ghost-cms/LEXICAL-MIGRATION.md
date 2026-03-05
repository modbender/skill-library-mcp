# Lexical Migration Guide

## Background

Ghost migrated from MobileDoc to **Lexical format** in Ghost 5.0+ (Aug 2023). The Lexical editor is built on Meta's Lexical framework - the same technology powering Facebook and Instagram's text editing.

**Current Ghost version:** 6.0 (released Aug 2025)

## What Changed

### OLD (Ghost < 5.0):
- HTML for create/update operations
- MobileDoc as storage format
- Limited editor capabilities

### NEW (Ghost 5.0+):
- **Lexical format for create/update operations**
- Ghost converts Lexical → mobiledoc internally for storage
- Rich editor with better mobile support, undo/redo, post history
- Faster performance on large posts

## API Behavior

### Writing Content (POST/PUT):
```json
{
  "posts": [{
    "title": "My Post",
    "lexical": "{\"root\":{\"children\":[...],\"type\":\"root\",\"version\":1}}"
  }]
}
```

Ghost accepts the `lexical` field and converts it internally to mobiledoc for storage.

### Reading Content (GET):
- `?formats=html` - Returns rendered HTML in `html` field (recommended for display)
- `?formats=lexical` - Returns `null` (Ghost stores as mobiledoc internally)
- `?formats=mobiledoc` - Returns raw mobiledoc (legacy)

**Best practice:** Write with `lexical`, read with `?formats=html`

## Lexical Format Structure

### Minimal Document
```json
{
  "root": {
    "children": [],
    "direction": "ltr",
    "format": "",
    "indent": 0,
    "type": "root",
    "version": 1
  }
}
```

### Simple Paragraph
```json
{
  "root": {
    "children": [
      {
        "children": [
          {
            "detail": 0,
            "format": 0,
            "mode": "normal",
            "style": "",
            "text": "Your paragraph text",
            "type": "extended-text",
            "version": 1
          }
        ],
        "direction": "ltr",
        "format": "",
        "indent": 0,
        "type": "paragraph",
        "version": 1
      }
    ],
    "direction": "ltr",
    "format": "",
    "indent": 0,
    "type": "root",
    "version": 1
  }
}
```

### Text Formatting
- `format: 0` - Normal
- `format: 1` - Bold
- `format: 2` - Italic
- `format: 3` - Bold + Italic

### Headings
```json
{
  "type": "heading",
  "tag": "h2",  // or h1, h3, h4, h5, h6
  "children": [
    {
      "text": "Heading Text",
      "type": "extended-text",
      "format": 1  // Bold by default
    }
  ]
}
```

## Helper Tools

### lexical-builder.js
Utility functions for building Lexical content:

```javascript
import { textToLexical, structuredToLexical } from './lexical-builder.js';

// Simple text (auto-split paragraphs on \n\n)
const lexical1 = textToLexical("Para 1\n\nPara 2");

// Structured content
const lexical2 = structuredToLexical([
  { type: 'h2', text: 'Title' },
  { type: 'p', text: 'Content', bold: true }
]);
```

### ghost-crud.js
Complete CRUD operations using Lexical:

```bash
# Create
node ghost-crud.js create "Title" "Content"

# Read
node ghost-crud.js read <post-id>

# Update
node ghost-crud.js update <post-id> "New content"

# List
node ghost-crud.js list "status:draft"

# Publish
node ghost-crud.js publish <post-id>

# Schedule
node ghost-crud.js schedule <post-id> "2026-02-10T09:00:00Z"

# Delete
node ghost-crud.js delete <post-id>
```

## Migration Checklist

When updating code that creates/updates Ghost content:

- [ ] Replace `html` field with `lexical` field
- [ ] Convert content to Lexical format before sending
- [ ] Use `?formats=html` when reading for display
- [ ] Update tests to expect Lexical input format
- [ ] Update documentation to show Lexical examples

## Testing

Tested against:
- Ghost 6.0 (chrisgiddings.net Ghost instance)
- API version: v5.0
- Operations verified: create, read, update, list

**Test results:**
- ✅ Create posts with Lexical content
- ✅ Update existing posts with Lexical content
- ✅ Ghost converts Lexical → mobiledoc internally
- ✅ HTML output renders correctly
- ✅ Multiple paragraphs and headings work

## References

- Ghost Admin API: https://ghost.org/docs/admin-api/
- Ghost 6.0 Announcement: https://ghost.org/changelog/6/
- New Editor: https://ghost.org/changelog/new-editor/
- Lexical Framework: https://lexical.dev/

## Troubleshooting

**Q: API returns `lexical: null` when I request `?formats=lexical`**
A: This is expected. Ghost stores content as mobiledoc internally, not Lexical. Use `?formats=html` to get rendered output.

**Q: Can I still use HTML for content?**
A: Not recommended. HTML might work for reading but not for writing. Use Lexical format for all create/update operations.

**Q: What about mobiledoc?**
A: Mobiledoc is the legacy format. Ghost converts Lexical → mobiledoc for storage, but you should write in Lexical format.

**Q: How do I handle complex formatting?**
A: Use the structured content approach with `structuredToLexical()` for headings, bold, italic, etc. See `lexical-builder.js` for examples.
