---
name: instapaper-import
description: Import reading notes from Instapaper exports into the slipbox. Use when user pastes an Instapaper highlight export with article title and notes. Parses title/URL from header, extracts user's own notes (plain text lines), skips original highlights (> lines), then runs slipbot for each.
---

# Instapaper Import

Parse Instapaper highlight exports and create slipbox entries for user's notes.

## Input Format

```
# [[Article Title](url)]
> Original highlight from article (SKIP)
User's note about the highlight (IMPORT)
> Another highlight (SKIP)
Another user note (IMPORT)
```

**Key distinction:**
- `> lines` = Original article highlights → **Skip these**
- Plain text lines = User's own ideas/takeaways → **Import these as notes**

## Parsing Rules

### Header Line
1. Extract title from: `# [[Title](url)]`
2. URL may be `instapaper-private://...` (private) or regular URL
3. Source type: `article`
4. Author: `null` (Instapaper doesn't include author)

### Content Lines
1. Lines starting with `>` = original highlights → **skip**
2. Plain text lines after `>` lines = user notes → **import**
3. Empty lines → skip
4. Each user note becomes a separate slipbox entry

## Workflow

1. **Parse header** → extract article title and URL
2. **Extract user notes** → collect plain text lines (not starting with `>`)
3. **Precheck** → show user: article title, note count, ask for confirmation
4. **On confirmation** → for each note, invoke slipbot:
   - Type: note (`-` prefix)
   - Source: `~ article, {title}`
   - Let slipbot handle: filename, tags, links, graph update
5. **Report** → count of notes created

## Example

**Input:**
```
# [[How to Learn Faster](https://example.com/article)]
> Get feedback more often
To learn faster we need faster feedback loops.
> Latent learning occurs without reinforcement
Testing yourself proactively speeds up learning.
```

**Extracted notes:**
1. "To learn faster we need faster feedback loops."
2. "Testing yourself proactively speeds up learning."

**Slipbot calls:**
```
- To learn faster we need faster feedback loops. ~ article, How to Learn Faster
- Testing yourself proactively speeds up learning. ~ article, How to Learn Faster
```

## Edge Cases

- **No user notes** (only `>` lines): Report "no notes to import"
- **Multi-line user notes**: Treat each paragraph as separate note
- **Title with special chars**: Preserve as-is for source metadata
