# Task Format Specification

## Basic Format

```markdown
- [ ] **Task title** — Brief description
  - Owner: martin
  - Due: 2026-01-29
  - Status: Todo
  - Blocks: lilla (podcast outreach)
  - Location: https://example.com
```

## Fields

| Field | Required | Description |
|-------|----------|-------------|
| title | Yes | Brief, actionable (verb + noun) |
| description | No | Additional context after `—` |
| Owner | No | Person responsible (default: martin) |
| Due | No | ASAP, YYYY-MM-DD, or "Before [event]" |
| Status | No | Todo, In Progress, Blocked, Waiting, Done |
| Blocks | No | Who/what is blocked + reason |
| Location | No | URL or file path |

## Checkbox States

- `[ ]` — Open task
- `[x]` — Completed task

## Priority Sections

| Section | Emoji | Criteria |
|---------|-------|----------|
| High Priority | 🔴 | Blocking others, critical deadline, revenue impact |
| Medium Priority | 🟡 | Important but not urgent, reviews/feedback |
| Delegated/Waiting | 🟢 | Someone else owns, monitoring only |
| Upcoming | 📅 | Future deadlines, scheduled events |
| Done | ✅ | Completed (pending archive) |

## Status Definitions

| Status | Description |
|--------|-------------|
| Todo | Not started |
| In Progress | Actively working |
| Blocked | Waiting on external dependency |
| Waiting | Delegated, monitoring for completion |
| Done | Completed |

## Due Date Formats

- `ASAP` — Do immediately
- `2026-01-29` — Specific date
- `Before Jan 29` — Deadline tied to event
- `Before IMCAS` — Named deadline
- `This week` — Current week
- `Next Monday` — Relative date

## Examples

### High Priority (Blocking)
```markdown
- [ ] **Set up Apollo.io access for Lilla** — Restore account for email finding
  - Owner: Martin
  - Due: ASAP
  - Status: Todo
  - Blocks: Lilla (podcast outreach sequence)
```

### High Priority (Deadline)
```markdown
- [ ] **Create IMCAS lead capture form** — Signup form + ActiveCampaign sequence
  - Owner: Martin
  - Due: Before Jan 29
  - Status: Todo
  - Location: https://bysha.pe/imcas
```

### Medium Priority (Review)
```markdown
- [ ] **Review Q1 promo designs** — Identify which need carousel versions
  - Owner: Martin
  - Status: Todo
  - Location: https://dropbox.com/...
```

### Delegated
```markdown
- [ ] **JGO release form signature** — Lilla following up
  - Owner: Lilla
  - Status: Waiting
```

### Completed
```markdown
- [x] **Ship IMCAS materials to France** — Completed Friday
  - Owner: Martin
  - Status: Done
```
