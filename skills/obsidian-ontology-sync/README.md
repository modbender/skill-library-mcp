# Obsidian-Ontology Sync

**Automatic bidirectional sync** between Obsidian PKM (human-friendly notes) and structured ontology (machine-queryable graph).

## Quick Start

```bash
# Test extraction (dry run)
python3 skills/obsidian-ontology-sync/scripts/sync.py extract --dry-run --verbose

# Run actual extraction
python3 skills/obsidian-ontology-sync/scripts/sync.py extract

# Analyze the graph
python3 skills/obsidian-ontology-sync/scripts/sync.py analyze

# Generate feedback
python3 skills/obsidian-ontology-sync/scripts/sync.py feedback
```

## What It Does

1. **Extract** - Scans your Obsidian notes and extracts:
   - Entities (Person, Organization, Project)
   - Relationships (works_at, assigned_to, etc.)
   - Properties (email, phone, etc.)

2. **Analyze** - Provides insights:
   - Entity counts by type
   - Relationship statistics
   - Data quality issues (missing emails, orphaned entities)

3. **Feedback** - Generates suggestions:
   - Missing information to fill in
   - Relationship insights
   - Template improvements

## Setup Automatic Sync

```bash
# Via OpenClaw cron (recommended)
cron add \
  --schedule "0 */3 * * *" \
  --payload '{"kind":"systemEvent","text":"Run obsidian-ontology sync"}' \
  --name "Obsidian-Ontology Sync"
```

## File Structure

```
/root/life/pkm/
├── references/contacts/     # Your notes (source)
├── references/clients/      # Your notes (source)
├── references/team/         # Your notes (source)
│
├── memory/ontology/         # Generated ontology
│   └── graph.jsonl         # Entity/relation storage
│
└── ontology-sync/feedback/  # Generated feedback
    └── feedback-YYYY-MM-DD.md
```

## Benefits

- ✅ **Zero extra work** - Just write normal Obsidian notes
- ✅ **Automatic structure** - Ontology extracted automatically
- ✅ **Powerful queries** - Find patterns across all data
- ✅ **Quality improvement** - Feedback catches missing info
- ✅ **Single source of truth** - Obsidian is primary

## Example Queries (After Sync)

```bash
# Find all team members without email
grep -l "type.*Person" memory/ontology/graph.jsonl | \
  while read f; do 
    jq 'select(.entity.properties.email == null) | .entity.properties.name' $f
  done

# Count entities by type
jq -s 'group_by(.entity.type) | map({type: .[0].entity.type, count: length})' \
  memory/ontology/graph.jsonl

# Find people at specific organization
jq 'select(.rel == "works_at" and .to == "organization_acme_corp")' \
  memory/ontology/graph.jsonl
```

## Tags

`obsidian` `ontology` `knowledge-graph` `pkm` `automation` `sync`
