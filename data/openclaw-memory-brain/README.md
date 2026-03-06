# openclaw-memory-brain

OpenClaw plugin: **Personal Brain Memory** (v0.2.0).

A lightweight OpenClaw Gateway plugin that acts as a personal brain:
- Listens for inbound messages and captures likely-valuable notes based on configurable triggers.
- Stores everything locally in a JSONL file with optional secret redaction.
- Supports semantic-ish search via hash-based embeddings.
- Provides slash commands for manual CRUD operations.
- Enforces a configurable item cap (`maxItems`) with oldest-first eviction.

## Install

### ClawHub

```bash
clawhub install openclaw-memory-brain
```

### Local development

```bash
openclaw plugins install -l ~/.openclaw/workspace/openclaw-memory-brain
openclaw gateway restart
```

## Commands

### `/remember-brain <text> [--tags tag1,tag2]`

Explicitly save a personal brain memory item. Optionally add custom tags.

```
/remember-brain TypeScript 5.5 requires explicit return types on exported functions
/remember-brain Use Redis for session caching --tags arch,caching
```

Custom tags are merged with the configured `defaultTags` (duplicates are removed automatically). Returns a confirmation message. If `redactSecrets` is enabled (default), any detected secrets are automatically redacted before storage and the response notes it.

### `/search-brain <query> [--tags tag1,tag2] [limit]`

Search brain memory items by semantic similarity. Optionally filter by tags (AND logic - items must have ALL specified tags).

```
/search-brain TypeScript configuration
/search-brain architecture decisions 10
/search-brain caching strategy --tags arch
/search-brain API design --tags api,design 5
```

- `query` - the search text (required)
- `--tags tag1,tag2` - filter by tags, comma-separated (optional, AND logic)
- `limit` - maximum number of results (optional, default 5, max 20)

The trailing argument is interpreted as a limit if it is a bare number and more than one argument is present. A sole numeric argument is treated as the query itself. Returns scored results sorted by relevance.

### `/list-brain [--tags tag1,tag2] [limit]`

List the most recent brain memory items. Optionally filter by tags (AND logic).

```
/list-brain
/list-brain 20
/list-brain --tags arch
/list-brain --tags api,design 10
```

- `--tags tag1,tag2` - filter by tags, comma-separated (optional, AND logic)
- `limit` - maximum number of items to return (optional, default 10, max 50)

Returns items in insertion order (oldest first), showing date and a truncated preview.

### `/tags-brain`

List all unique tags across all brain memory items, sorted alphabetically.

```
/tags-brain
```

Returns a comma-separated list of all tags with a count, e.g. `Tags (4): api, arch, brain, design`.

### `/export-brain [--tags tag1,tag2]`

Export brain memory items as JSON for backup or portability. Optionally filter by tags.

```
/export-brain
/export-brain --tags arch,design
```

Returns a JSON object with a version envelope:

```json
{
  "version": 1,
  "exportedAt": "2026-02-27T10:30:00.000Z",
  "count": 2,
  "items": [...]
}
```

The `items` array contains full `MemoryItem` objects with all fields preserved. Copy the output to a file for backup, or pass it to `/import-brain` on another instance.

### `/import-brain <json>`

Import brain memory items from a JSON export. Requires authentication. Accepts either:
- A JSON array of memory items
- An envelope object (as produced by `/export-brain`) with an `items` array

```
/import-brain [{"id":"...","kind":"note","text":"...","createdAt":"..."}]
/import-brain {"version":1,"items":[...]}
```

- Items that already exist (by ID) are skipped automatically
- Items missing an `id` field get a new UUID assigned
- Items with an invalid or missing `kind` default to `"note"`
- Items without `tags` receive the configured `defaultTags`
- Returns a summary: `Imported N items. X skipped (already exist). Y skipped (invalid format).`

### `/purge-brain [--dry-run]`

Delete brain memory items older than the configured retention period (`retention.maxAgeDays`). Requires authentication.

```
/purge-brain
/purge-brain --dry-run
```

- Returns `"Retention policy is not configured."` if `maxAgeDays` is 0 or unset.
- Use `--dry-run` to preview how many items would be deleted without actually removing them.
- Returns a summary: `Purged N item(s) older than X day(s). M item(s) remaining.`

When `retention.maxAgeDays` is configured, expired items are also automatically purged on plugin startup.

### `/forget-brain <id>`

Delete a brain memory item by its unique ID. Requires authentication.

```
/forget-brain 550e8400-e29b-41d4-a716-446655440000
```

Returns a confirmation or a not-found message.

## Tool: `brain_memory_search`

An AI-callable tool for searching brain memories programmatically. Supports optional tag-based filtering.

### Input schema

```json
{
  "query": "string (required) - the search text",
  "limit": "number (optional, 1-20, default 5)",
  "tags": "string[] (optional) - filter results to items that have ALL of these tags"
}
```

### Example calls

```json
{ "query": "Anthropic reset schedule", "limit": 5 }
{ "query": "caching strategy", "tags": ["arch", "caching"] }
```

### Response format

```json
{
  "hits": [
    {
      "score": 0.87,
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "createdAt": "2026-02-27T10:30:00.000Z",
      "tags": ["brain"],
      "text": "Remember: Anthropic resets usage limits on the 1st of each month."
    }
  ]
}
```

Returns an empty `hits` array when no results match.

## Auto-capture (message_received hook)

The plugin listens on the `message_received` event and conditionally captures inbound messages as memory items.

### Capture rules (defaults)

A message is captured when **all** of the following are true:

1. Message content is not empty
2. Message length >= `minChars` (default: 80 characters)
3. At least one of:
   - The message contains an **explicit trigger** (e.g. "remember this", "keep this")
   - `requireExplicit` is `false` AND the message contains an **auto-topic** keyword (e.g. "decision")

Convention: brain-memory should **not** silently store large amounts of chat. The recommended default is `requireExplicit: true`.

### Trigger matching

- Case-insensitive substring matching (e.g. "merke dir" also matches "Merke dir:" naturally)
- Default explicit triggers: `merke dir`, `remember this`, `notiere`, `keep this`
- Default auto-topics: `entscheidung`, `decision`

## Configuration

All configuration is provided via `openclaw.plugin.json` or the plugin config block.

```json
{
  "plugins": {
    "entries": {
      "openclaw-memory-brain": {
        "enabled": true,
        "config": {
          "storePath": "~/.openclaw/workspace/memory/brain-memory.jsonl",
          "dims": 256,
          "redactSecrets": true,
          "maxItems": 5000,
          "capture": {
            "minChars": 80,
            "requireExplicit": true,
            "explicitTriggers": ["merke dir", "remember this", "notiere", "keep this"],
            "autoTopics": ["entscheidung", "decision"]
          },
          "defaultTags": ["brain"],
          "retention": {
            "maxAgeDays": 90
          }
        }
      }
    }
  }
}
```

### Configuration options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `enabled` | boolean | `true` | Enable or disable the plugin entirely |
| `storePath` | string | `~/.openclaw/workspace/memory/brain-memory.jsonl` | Path to the JSONL storage file (must be inside home directory) |
| `dims` | number | `256` | Embedding vector dimensions (32-2048) |
| `redactSecrets` | boolean | `true` | Redact detected secrets (API keys, tokens, passwords) before storage |
| `maxItems` | number | `5000` | Maximum number of memory items to keep (oldest are evicted, 100-100000) |
| `defaultTags` | string[] | `["brain"]` | Default tags applied to all captured items |
| `retention.maxAgeDays` | number | `0` | Delete items older than this many days. 0 = disabled. Expired items are purged on startup and via `/purge-brain`. |
| `capture.minChars` | number | `80` | Minimum message length for auto-capture (10+) |
| `capture.requireExplicit` | boolean | `true` | When true, only explicit triggers cause capture (recommended) |
| `capture.explicitTriggers` | string[] | see above | Phrases that trigger explicit capture (substring match, case-insensitive) |
| `capture.autoTopics` | string[] | `["entscheidung", "decision"]` | Topic keywords that trigger capture when `requireExplicit` is false |

## Safety

- The plugin redacts common secrets (API keys, tokens, passwords, private key blocks, JWTs, connection strings) before storage.
- Redaction uses pattern-based detection and never stores matched secret values - only the rule name and count.
- The store path is validated to stay inside the user's home directory (path traversal guard).
- PII is only stored locally on disk in the JSONL file - no external transmission.

## Development

```bash
npm install
npm run build       # TypeScript type-check (noEmit, strict mode)
npm test            # Run vitest test suite (168 tests)
npm run test:watch  # Watch mode
```

### Test coverage

The test suite covers all plugin functionality:

- Plugin registration (commands, tool, event handler, disabled state, invalid config)
- `/remember-brain` (save, usage, empty args, secret redaction, source context, --tags flag, tag merging)
- `/search-brain` (query, usage, no-match, trailing limit, sole numeric arg, --tags filtering)
- `/list-brain` (empty store, populated listing, limit argument, default limit, --tags filtering)
- `/forget-brain` (usage, not-found, delete + verify, requireAuth)
- `/tags-brain` (empty store, unique tag listing, deduplication, alphabetical sort)
- `/export-brain` (empty store, JSON envelope format, MemoryItem fields, --tags filtering, valid JSON output)
- `/import-brain` (usage, invalid JSON, invalid structure, empty array, bare array import, envelope import, duplicate skipping, invalid entry skipping, default tags, kind preservation, kind defaulting, UUID generation, requireAuth)
- Export/import round-trip (data preservation, idempotent re-import)
- `/purge-brain` (not-configured, delete expired, no items to purge, --dry-run preview, requireAuth, metadata)
- Retention startup cleanup (auto-purge on startup, logging, disabled when maxAgeDays=0, no log when nothing expired)
- Retention edge cases (invalid createdAt, empty store, purge all items)
- `brain_memory_search` tool (result shape, empty/undefined query, limit, schema, tags parameter)
- Tag-based filtering (AND logic, single tag, multiple tags, no-match tag, empty tags, merged tags with defaults)
- Auto-capture (explicit trigger, auto-topic, short message rejection, no-trigger rejection, requireExplicit enforcement, empty content, case-insensitivity, secret redaction, error handling, custom minChars, custom triggers)
- Custom configuration (defaultTags, custom autoTopics, redactSecrets toggle)
- Output formatting (text truncation at 120 chars, ellipsis behavior)
- Edge cases (sole numeric arg, whitespace-only arg, limit clamping, multiple captures)
- Logger verification (startup info, capture info, error on invalid path)
- Command metadata (name, description, usage, requireAuth, acceptsArgs)

### Dependencies

- **Runtime**: `@elvatis_com/openclaw-memory-core` (local linked package)
- **Dev**: `typescript`, `vitest`, `@types/node`

## License

MIT
