# Memory Setup — Spreadsheet

## Initial Setup

```bash
mkdir -p ~/spreadsheet/{projects,templates,exports}
touch ~/spreadsheet/memory.md
```

## memory.md Template

```markdown
# Spreadsheet Memory

## Preferences
date_format: YYYY-MM-DD
number_locale: en-US
default_integration: google-sheets

## Recent Sheets
| Name | ID/Path | Last Access |
|------|---------|-------------|

## Auto-categorization
food: [supermarket, restaurant, cafe]
transport: [uber, gas, metro]

---
*Last: YYYY-MM-DD*
```

## projects/{name}.md Template

```markdown
# {Project} Sheets

## Main Sheet
id: 1abc...xyz
url: https://docs.google.com/spreadsheets/d/...

## Schema
| Column | Letter | Type |
|--------|--------|------|
| Date | A | date |
| Amount | B | currency |
| Category | C | enum |

## API Config
service_account: ~/credentials.json

---
*Last sync: YYYY-MM-DD*
```
