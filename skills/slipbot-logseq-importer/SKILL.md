---
name: logseq-import
description: Import notes from Logseq pages into the slipbox. Use when user pastes a Logseq page with properties and bulleted notes. Parses page-level properties, extracts each bullet as an individual note, handles nested bullets by adding parent context, then runs slipbot for each.
---

# Logseq Import

Parse a Logseq page and create individual slipbox entries for each bullet point.

## Critical Rule: Ignore All Tags

**Do not import any tags from Logseq.** This includes:
- Page-level `tags::` property
- Inline `#tags` in bullet content
- `block-tags::` metadata

Slipbot generates its own tags based on content. Logseq tags would conflict with this.

## Input Format

Logseq pages have two parts:

**1. Page Properties** (top of page, `key:: value` format):
```
type:: #literature
source:: Book
author:: David Kadavy
title:: Digital Zettelkasten
alias:: zettelkasten-book
status::
tags::
```

**2. Bulleted Notes** (markdown list):
```
- First note content here
- Second note with [[page ref]] link
  - Nested bullet under second
- Third note id:: abc123-uuid
```

## Property Mapping

| Logseq Property | Slipbox Field |
|-----------------|---------------|
| `title::` | `source.title` |
| `source::` | `source.type` (if plain text like "Book") |
| `source:: [text](url)` | `source.title` + `source.url` (if markdown link) |
| `author::` | `source.author` |
| `type:: #literature` | Note type hint (maps to `note`) |
| `alias::` | Ignore |
| `status::` | Ignore |
| `tags::` | **Ignore** (slipbot generates better tags) |

Empty properties (e.g., `author::` with no value) → `null`

## Parsing Rules

### Properties
1. Extract all `key:: value` lines at the top
2. Stop when hitting first bullet (`- `)
3. Strip `#` from values like `#literature`
4. Parse markdown links: `[text](url)` → extract both parts

### Bullets
1. Each top-level bullet (`- `) becomes its own slipbox note
2. **Nested bullets**: Add parent context to make them standalone
   - Example parent: `- [[Fleeting Notes]]: quick notes written anywhere`
   - Example child: `  - Can be on paper or digital`
   - Result: "Fleeting Notes (quick notes written anywhere) can be on paper or digital"
3. Strip Logseq metadata from bullets:
   - `id:: uuid` → remove
   - `block-tags:: #xxx` → remove entirely
   - `#tag` inline tags → remove entirely (slipbot generates its own)
   - `#{"{"` or malformed tags → remove
4. Convert `[[page refs]]` → plain text (potential link targets)

### Content Cleanup
- Remove trailing `id:: xxx` from bullets
- Remove `block-tags:: xxx` entirely
- Remove all `#tag` inline tags (slipbot generates its own tags)
- Preserve markdown formatting (bold, italic, code)

## Workflow

1. **Precheck (before import)**
   - Parse the page properties and bullets (don't create notes yet)
   - Generate a brief summary of what the page is about (1-2 sentences based on title, author, and content themes)
   - Count total notes that will be created (including nested bullets that become standalone)
   - Present to user: summary, note count, source info
   - **Ask for confirmation** before proceeding with import
   - If user declines, stop and don't create any notes

2. **Parse the page** (after confirmation)
   - Extract page properties → source metadata
   - Extract all bullets → note list
   - Handle nesting by enriching child bullets with parent context

3. **For each bullet**, invoke slipbot workflow:
   - Use `- {content}` prefix (note type)
   - Include source: `~ {source.type}, {source.title} by {source.author}`
   - Let slipbot handle: filename, tags, links, graph update

4. **Report results**
   - Count of notes created
   - Any issues encountered

## Example

**Input:**
```
type:: #literature
source:: Book
author:: David Kadavy
title:: Digital Zettelkasten

- Rewriting ideas helps decide their importance
- [[Fleeting Notes]]: quick notes written anywhere
  - Can be captured on paper or digitally
- Keywords should be specific to the idea id:: abc123
```

**Processing:**
1. Source: `Book, "Digital Zettelkasten" by David Kadavy`
2. Bullets extracted:
   - "Rewriting ideas helps decide their importance"
   - "Fleeting Notes: quick notes written anywhere"
   - "Fleeting Notes can be captured on paper or digitally" (nested, parent context added)
   - "Keywords should be specific to the idea" (id stripped)

3. Each sent to slipbot as:
   - `- Rewriting ideas helps decide their importance ~ Book, Digital Zettelkasten by David Kadavy`
   - etc.

## Edge Cases

- **No properties**: Treat as standalone notes without source
- **Deeply nested bullets (3+ levels)**: Flatten, accumulating context from all ancestors
- **Citation sections** (`## Citation:`): Ignore (redundant with properties)
- **Non-bullet content**: Ignore headers, paragraphs outside bullets
- **Multiple `[[refs]]` in one bullet**: Keep all, convert to plain text
