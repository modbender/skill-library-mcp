# Memory Template — Postman

Create `~/postman/memory.md` with this structure:

```markdown
# Postman Memory

## Status
status: ongoing
last: YYYY-MM-DD

## Projects

### Project Name
- Base URL: https://api.example.com
- Auth: Bearer token / API key / OAuth
- Environments: dev, staging, prod
- Collection: ~/postman/collections/project.json

## Patterns

### Authentication
<!-- Common auth approach they use -->

### Collection Structure
<!-- How they organize folders/requests -->

### Testing Conventions
<!-- Standard assertions they apply -->

## Notes
<!-- Preferences, quirks, things to remember -->

---
*Updated: YYYY-MM-DD*
```

## Folder Structure

```
~/postman/
├── memory.md
├── collections/
│   ├── project-a.json
│   └── project-b.json
└── environments/
    ├── dev.json
    ├── staging.json
    └── prod.json
```

## Status Values

| Value | Meaning |
|-------|---------|
| `ongoing` | Still learning their workflow |
| `complete` | Have good context |
