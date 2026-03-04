# Knowledge management

This section applies when `ORG_MEMORY_USE_FOR_AGENT` is `true`. All commands operate against `$ORG_MEMORY_AGENT_DIR` and `$ORG_MEMORY_AGENT_DATABASE_LOCATION`.

## Always search before creating

Before creating a node or link, check if the entity already exists:

```bash
org roam node find 'Sarah' -d "$ORG_MEMORY_AGENT_DIR" --db "$ORG_MEMORY_AGENT_DATABASE_LOCATION" -f json
```

- If found: use the existing node's ID and file path
- If not found (`headline_not_found` error): create a new node

**Never create a node without searching first.** Duplicates fragment your knowledge graph.

## Record an entity

Only after confirming no existing node:

```bash
org roam node create 'Sarah' -d "$ORG_MEMORY_AGENT_DIR" --db "$ORG_MEMORY_AGENT_DATABASE_LOCATION" -t person -t work -f json
```

## Add structure to a node

Use the file path returned by create/find commands:

```bash
# Add a headline to the node (response includes auto-assigned custom_id)
org add <file> 'Unavailable March 2026' --tag scheduling --db "$ORG_MEMORY_AGENT_DATABASE_LOCATION" -f json
# → {"ok":true,"data":{"custom_id":"k4t","title":"Unavailable March 2026",...}}

# Use the custom_id for follow-up commands
org note k4t 'Out all of March per human.' -d "$ORG_MEMORY_AGENT_DIR" --db "$ORG_MEMORY_AGENT_DATABASE_LOCATION" -f json

# Append body text to an existing headline
org append k4t 'Confirmed by email on 2026-02-20.' -d "$ORG_MEMORY_AGENT_DIR" --db "$ORG_MEMORY_AGENT_DATABASE_LOCATION" -f json

# Append multi-line text via stdin
printf '%s' 'First paragraph.

Second paragraph.' | org append k4t --stdin -d "$ORG_MEMORY_AGENT_DIR" --db "$ORG_MEMORY_AGENT_DATABASE_LOCATION" -f json
```

**`org note` vs `org append`:** `note` adds a timestamped entry to the LOGBOOK drawer (metadata). `append` adds text to the headline body (visible content). Use `note` for audit trail, `append` for building up content.

**Note:** Both commands attach to *headlines*, not file-level nodes. If a roam node is file-level (no headlines yet), first add a headline with `org add`, then use `note` or `append` on it.

## Link two nodes

**Always search for both nodes first** to get their IDs:

```bash
# Find source node
org roam node find 'Bob' -d "$ORG_MEMORY_AGENT_DIR" --db "$ORG_MEMORY_AGENT_DATABASE_LOCATION" -f json
# → Returns {"ok":true,"data":{"id":"e5f6a7b8-...","file":"/path/to/bob.org",...}}

# Find target node
org roam node find 'Alice' -d "$ORG_MEMORY_AGENT_DIR" --db "$ORG_MEMORY_AGENT_DATABASE_LOCATION" -f json
# → Returns {"ok":true,"data":{"id":"a1b2c3d4-...",...}}
```

If either node doesn't exist, create it first. Then link using the IDs from the responses:

```bash
org roam link add <source-file> '<source-id>' '<target-id>' -d "$ORG_MEMORY_AGENT_DIR" --db "$ORG_MEMORY_AGENT_DATABASE_LOCATION" --description 'manages' -f json
```

The `--description` is optional metadata about the relationship.

## Query your knowledge

```bash
# Find a node by name
org roam node find 'Sarah' -d "$ORG_MEMORY_AGENT_DIR" --db "$ORG_MEMORY_AGENT_DATABASE_LOCATION" -f json

# Read a headline's full content (body, properties, logbook)
org read <file> 'Unavailable March 2026' -d "$ORG_MEMORY_AGENT_DIR" -f json

# Full-text search across all indexed headlines (fast, supports boolean/prefix/phrase)
org fts 'sarah AND march' -d "$ORG_MEMORY_AGENT_DIR" --db "$ORG_MEMORY_AGENT_DATABASE_LOCATION" -f json

# Regex search (slower, use when FTS isn't precise enough)
org search 'Sarah.*March' -d "$ORG_MEMORY_AGENT_DIR" -f json

# Browse by graph structure
org roam backlinks 'a1b2c3d4-...' -d "$ORG_MEMORY_AGENT_DIR" --db "$ORG_MEMORY_AGENT_DATABASE_LOCATION" -f json
org roam tag find person -d "$ORG_MEMORY_AGENT_DIR" --db "$ORG_MEMORY_AGENT_DATABASE_LOCATION" -f json
```

**`org fts` vs `org search`:** Use `fts` by default — it's faster and handles natural language well. Use `search` when you need regex patterns (e.g. matching across fields or partial words that aren't prefixes).

## Aliases and refs

Aliases let a node be found by multiple names. Refs associate URLs or external identifiers.

```bash
org roam alias add <file> 'a1b2c3d4-...' 'Sarah Chen' --db "$ORG_MEMORY_AGENT_DATABASE_LOCATION"
org roam ref add <file> 'a1b2c3d4-...' 'https://github.com/sarahchen' --db "$ORG_MEMORY_AGENT_DATABASE_LOCATION"
```

## Node conventions

Use consistent tags for easy querying:

- `person` — people the human knows or works with
- `project` — software projects, initiatives
- `lesson` — things the agent learned the hard way
- `preference` — how the human likes things done
- `fact` — technical details, configuration, reference data
