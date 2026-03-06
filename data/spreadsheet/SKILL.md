---
name: Spreadsheet
slug: spreadsheet
version: 1.0.0
description: Read, write, and analyze tabular data with schema memory, format preservation, and multi-platform support.
metadata: {"clawdbot":{"emoji":"📊","requires":{"bins":[]},"os":["linux","darwin","win32"]}}
---

## When to Use

User needs spreadsheet operations: reading data, writing cells, analyzing tables, generating reports, or tracking structured information across Google Sheets, Excel, or CSV files.

## Architecture

Memory lives in `~/spreadsheet/`. See `memory-template.md` for setup.

```
~/spreadsheet/
  memory.md           # Preferences, recent sheets, format rules
  projects/           # Per-project schemas and configs
    {name}.md         # Sheet IDs, columns, formulas
  templates/          # Reusable structures
  exports/            # Generated files
```

## Quick Reference

| Topic | File |
|-------|------|
| Memory setup | `memory-template.md` |
| Google Sheets API | `google-sheets.md` |
| Excel operations | `excel.md` |
| CSV handling | `csv.md` |

## Scope

This skill ONLY:
- Reads/writes spreadsheets user explicitly requests
- Stores schemas and preferences in `~/spreadsheet/`
- Processes files user provides

This skill NEVER:
- Accesses sheets without user request
- Stores passwords, API keys, or sensitive financial data
- Modifies files outside `~/spreadsheet/` or user paths

## Data Storage

All data stored in `~/spreadsheet/`. Create on first use:
```bash
mkdir -p ~/spreadsheet/{projects,templates,exports}
```

## Self-Modification

This skill NEVER modifies its own SKILL.md.
All user data stored in `~/spreadsheet/` only.

## Core Rules

### 1. Schema First
On first access to any sheet:
1. Document columns (name, type, sample)
2. Save to `projects/{name}.md`
3. Reference schema in future ops

### 2. Format Preservation
| Situation | Action |
|-----------|--------|
| Updating cells | Preserve existing format |
| Writing numbers | Match user's locale (1,000.00 vs 1.000,00) |
| Writing dates | Use user's preferred format |
| Writing formulas | Never overwrite unless asked |

### 3. Large Data Strategy
| Row Count | Approach |
|-----------|----------|
| <1000 | Load fully |
| 1000-10000 | Sample + targeted queries |
| >10000 | Paginate, warn before loading |

### 4. Integration Priority
1. **Google Sheets** - if API configured
2. **Excel (.xlsx)** - local files, use openpyxl
3. **CSV** - universal fallback

### 5. Memory Updates
| Event | Action |
|-------|--------|
| New sheet accessed | Add ID + schema to memory |
| User corrects format | Save preference |
| Column renamed | Update project schema |

## Common Traps

- **Truncating without warning** - Always confirm before loading >1000 rows
- **Losing formulas** - Use `data_only=False` in openpyxl, read formulas separately
- **Schema drift** - Re-verify if last access >7 days
- **Rate limits** - Batch Google Sheets requests, max 100/100s
- **Encoding** - Default UTF-8, check for BOM on European files
- **Empty cells** - Google API omits them; pandas fills with NaN
