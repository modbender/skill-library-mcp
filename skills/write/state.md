# State & Tracking Reference

## Piece IDs

Every piece gets an ID:
```
{type}-{YYYYMMDD}-{HHMMSS}
```

Examples:
- `article-20260211-143052`
- `email-20260211-150030`
- `book-20260211-090000`

## Project Structure

```
~/writing/
  config.json           # workspace settings
  index.json            # all pieces index
  pieces/
    article-20260211-143052/
      meta.json         # piece metadata
      brief.md          # requirements
      content.md        # current version
    email-20260211-150030/
      ...
  versions/
    article-20260211-143052/
      v1_20260211-143100.md
      v2_20260211-151023.md
  audits/
    article-20260211-143052/
      audit_20260211-160000.md
  research/
    article-20260211-143052/
      sources.md
      notes.md
```

## Tracking Multiple Pieces

When working on multiple pieces:

```
Active:
  [article-20260211-143052] Blog post about X — drafting
  [email-20260211-150030] Reply to Y — audit pending

Queued:
  [tweet-20260211-160000] Thread about Z — waiting
```

## Handling Interruptions

| User Says | Action |
|-----------|--------|
| "Edit the article" | Check: which piece? Ask if ambiguous |
| "Go back to previous" | Use restore.sh with piece ID |
| "Add section about X" | New draft via edit.sh (auto-versions) |
| "Make it shorter" | New draft via edit.sh (auto-versions) |
| "Delete old versions" | Use cleanup.sh (asks confirmation) |

## Never Lose Work

The script system guarantees:
- Every edit creates a backup first
- Restores create backups too
- Only cleanup.sh deletes (with confirmation)
- User can always go back
