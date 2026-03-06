# Memory Setup

```bash
mkdir -p ~/voice-notes/{transcripts,notes,archive}
touch ~/voice-notes/{memory.md,index.md}
```

## memory.md

```markdown
# Voice Notes Memory

## Tag Registry
| Tag | Description |
|-----|-------------|
| #ideas | Concepts |
| #tasks | Actions |
| #decisions | Choices |

## Recent Activity
| Date | Note | Tags |
|------|------|------|

## Active Topics
<!-- In development -->
```

## index.md

```markdown
# Index

## By Tag
### #ideas
- [[slug]] - desc

## By Date
### YYYY-MM
- DD: [[slug]]

## Link Map
[[a]] <-> [[b]] - relation
```

## Note (notes/{slug}.md)

```markdown
# {Title}
Tags: #tag
Created: YYYY-MM-DD
From: [[transcript]]

## Content
{Organized}

## Linked
- [[related]]
```

## Transcript (transcripts/YYYY-MM-DD-HHMMSS.md)

```markdown
# YYYY-MM-DD-HHMMSS
Duration: X:XX | Processed: [[slug]]

---
{Raw text}
```

## Archive (archive/{slug}.md)

```markdown
# [ARCHIVED] {Title}
Archived: YYYY-MM-DD | Superseded: [[new]]

{Content}
```
