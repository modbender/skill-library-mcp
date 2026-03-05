# Memory Setup — Robot Skill

## Initial Setup

Create the directory structure on first robotics interaction:

```bash
mkdir -p ~/robot/projects ~/robot/archive
touch ~/robot/memory.md ~/robot/inventory.md ~/robot/corrections.md
```

## File Templates

### memory.md (HOT — always read)

```markdown
# Robot Memory

## Active Project
<!-- Current project name and status -->
<!-- Format: "project: status (board)" -->

## Quick Inventory
<!-- Most-used hardware, 1 line each -->
<!-- Format: "type: model (notes)" -->

## Recent Corrections
<!-- Last 5 fixes, newest first -->
<!-- Format: "symptom → fix" -->

## Index
- Full inventory: `inventory.md`
- Project details: `projects/{name}.md`
- All corrections: `corrections.md`

---
*Last: YYYY-MM-DD*
```

### inventory.md (WARM — load when selecting hardware)

```markdown
# Hardware Inventory

## Microcontrollers
<!-- Format: model | voltage | pins | notes -->
| Model | Logic | USB | Notes |
|-------|-------|-----|-------|
| | | | |

## Sensors
<!-- Format: model | type | interface | address/pins -->
| Model | Type | I/F | Addr/Pins | Notes |
|-------|------|-----|-----------|-------|
| | | | | |

## Actuators
<!-- Format: model | type | voltage | current -->
| Model | Type | Voltage | Current | Notes |
|-------|------|---------|---------|-------|
| | | | | |

## Drivers & Modules
<!-- Motor drivers, power modules, communication -->
| Model | Purpose | Notes |
|-------|---------|-------|
| | | |

## Power Supplies
| Source | Voltage | Current | Notes |
|--------|---------|---------|-------|
| | | | |

---
*Last updated: YYYY-MM-DD*
```

### corrections.md (WARM — check before debugging)

```markdown
# Corrections Log

## Format
Each entry: date | symptom | root cause | fix

## Log

<!-- Newest first, keep last 30 -->

---
*Entries older than 90 days archived to archive/corrections-YYYY.md*
```

### projects/{name}.md (COLD — load for specific project)

```markdown
# Project: {Name}

## Status
<!-- active | paused | complete -->

## Hardware
- Board: 
- Sensors: 
- Actuators: 
- Power: 

## Wiring
<!-- Pin assignments -->
| Component | Pin | Notes |
|-----------|-----|-------|
| | | |

## Code
- Repo/location: 
- Libraries: 

## Issues Found
<!-- Project-specific gotchas -->

## Notes

---
*Started: YYYY-MM-DD*
*Last: YYYY-MM-DD*
```

## Memory Rules

### Budget Limits
| File | Max Lines | Action When Exceeded |
|------|-----------|---------------------|
| memory.md | 50 | Move details to inventory/projects |
| inventory.md | 150 | Archive unused hardware |
| corrections.md | 100 | Archive old entries |
| project/*.md | 100 | Summarize, archive details |

### When to Update

| Event | Update |
|-------|--------|
| User mentions hardware they own | Add to inventory.md, update memory.md quick list |
| User starts new project | Create projects/{name}.md, set as active in memory.md |
| Code fails → fix found | Add to corrections.md, summarize in memory.md |
| User asks about past project | Load from projects/ or archive/ |
| Project completed | Move to archive/, clear from memory.md active |

### Tiered Loading

1. **Always load:** `memory.md` (50 lines max)
2. **Load on hardware selection:** `inventory.md`
3. **Load on debugging:** `corrections.md`
4. **Load on project context:** `projects/{name}.md`
5. **Load on explicit request:** `archive/*`

### Archive Rules

- Projects inactive >30 days → prompt to archive
- Corrections >90 days old → move to `archive/corrections-YYYY.md`
- Completed projects → `archive/{name}-summary.md` (condensed)
