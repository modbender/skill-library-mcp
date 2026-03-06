# Tag Management

## Why Tags Over Folders

- Note can have multiple tags
- No reorganization needed
- Flexible filtering
- Scales better

## Tag Registry

All tags in `~/voice-notes/memory.md` under `## Tag Registry`:

```markdown
## Tag Registry
| Tag | Description |
|-----|-------------|
| #product | Product decisions |
| #product/pricing | Pricing specifically |
```

Use `/` for hierarchy: `#category/subcategory`

## Creating Tags

Before creating new tag:
1. Check if existing tag covers it
2. Check if should be subtag
3. If new -> add to registry with description

If unsure, ask user:
> "Should I create #newtag or use #existingtag?"

## Tag Assignment

| Content Type | Tags |
|--------------|------|
| Action item | #tasks + domain |
| Decision | #decisions + domain |
| Random idea | #ideas + topic |
| Meeting note | #meetings + project |

## User Granularity

First session, establish preference:

**Broad:**
```
#work #personal #ideas #tasks
```

**Specific:**
```
#work/client-a #work/client-b
#ideas/product #ideas/content
```

## Maintenance

Periodically:
- Merge similar tags (ask user)
- Archive unused tags
- Never delete - mark deprecated
