# Capture Patterns

## Trigger Phrases
User says: "archive this", "save this", "keep this", "store this for later"

## Capture Flow

1. **Identify content type** (URL, text, image, file)
2. **Extract content** based on type
3. **Ask for context**: "What's this for? Any project?"
4. **Generate metadata**: summary, tags, project link
5. **Confirm**: "Archived: [title]. Tagged: [tags]. Project: [project]"

## Extraction by Type

### URLs
```
1. Fetch full content (web_fetch or browser)
2. Extract: title, author, date, main text
3. Identify: key quotes, data points, conclusions
4. Store: full content + metadata + extracted insights
```

### Videos (YouTube)
```
1. Get video metadata (title, creator, duration)
2. If user mentions timestamps → note them
3. If transcript available → store key sections
4. Otherwise: store metadata + user's description of why
```

### PDFs/Papers
```
1. Extract: title, authors, abstract
2. Note: publication date, source
3. If user highlights sections → store those
4. Store full PDF path if local
```

### Raw Text/Ideas
```
1. Store as-is with timestamp
2. Ask: "Related to anything you've saved before?"
3. Link to similar items if found
```

## Quality Signals
- User says "important" → flag as priority
- User mentions project → link to project
- User mentions person → tag with name
- User says "for later" → add to resurface queue
