# GOYFILES Bot Access (GitHub Package)

This folder is a standalone package for external bot integration docs.

## Contents

- `skill.md` - core external-bot contract
- `bot-docs/tool-reference.md` - full tool list, args, enums
- `bot-docs/dataset-reference.md` - source/dataset guide
- `bot-docs/fulltext-guide.md` - text retrieval and troubleshooting

## Source of truth

Canonical docs are served from:

- `dashboard/public/skill.md`
- `dashboard/public/bot-docs/*`

This folder is a publishable mirror for GitHub/distribution.

## Sync command (PowerShell)

```powershell
Copy-Item dashboard/public/skill.md goyfiles/skill.md -Force
Copy-Item dashboard/public/bot-docs/dataset-reference.md goyfiles/bot-docs/dataset-reference.md -Force
Copy-Item dashboard/public/bot-docs/fulltext-guide.md goyfiles/bot-docs/fulltext-guide.md -Force
Copy-Item dashboard/public/bot-docs/tool-reference.md goyfiles/bot-docs/tool-reference.md -Force
```
