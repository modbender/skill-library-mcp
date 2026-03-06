# QST Memory Structure

## Layers

### 1. Short-Term Memory (Daily Logs)
- **Location**: `memory/YYYY-MM-DD.md`
- **Purpose**: Raw conversation logs, immediate context
- **Retention**: 7-30 days
- **Content**: Everything said, no filtering

### 2. Long-Term Memory (Permanent)
- **Location**: `MEMORY.md`
- **Purpose**: Curated, permanent memories
- **Retention**: Indefinite
- **Content**:
  - Key decisions
  - Important facts
  - User preferences
  - Project state
  - Learned lessons

## Migration Criteria

### Promote to Long-Term When:
- [ ] Decision made that affects future behavior
- [ ] Fact verified and likely needed again
- [ ] Preference expressed by user
- [ ] Project milestone reached
- [ ] Lesson learned that should not be forgotten

### Don't Migrate:
- [ ] Routine acknowledgments
- [ ] Temporary context
- [ ] Information likely to change soon

## Coherence Rules

### Deduplication
- Merge similar entries
- Keep most complete version
- Track source dates

### Conflict Resolution
- Prefer recent verified information
- Mark contradictions with `[CONFLICT: date]`
- Flag for human review if unresolved

### Expiration
- Review memories quarterly
- Flag outdated entries
- Archive or delete as needed
