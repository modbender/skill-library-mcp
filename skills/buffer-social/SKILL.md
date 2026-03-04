# Buffer Skill for OpenClaw

Use this skill to create and manage Buffer content from OpenClaw or terminal commands.

## Quick Start

1. Install dependencies:
   ```bash
   cd skills/buffer
   npm install
   ```
2. Configure API key:
   ```bash
   cp .env.example .env
   # set BUFFER_API_KEY
   ```
3. Run a command:
   ```bash
   node ./buffer.js profiles
   ```

## Authentication Setup

Set in `.env`:

```env
BUFFER_API_KEY=your_buffer_api_key
BUFFER_API_URL=https://api.buffer.com/graphql
```

Get key: https://publish.buffer.com/settings/api

## Command Reference

### `buffer profiles`

List all connected profiles.

### `buffer post <text>`

Create content.

Options:

- `--profile <id>`: single target profile
- `--profiles <ids>`: comma-separated profile IDs
- `--all`: all connected profiles
- `--time <datetime>`: ISO 8601 scheduled time
- `--queue`: add to queue
- `--image <path>`: attach local image path (validated; upload flow limited by current API docs)
- `--draft`: save as idea/draft instead of post

### `buffer queue`

View scheduled/queued posts.

Options:

- `--profile <id>`: filter by profile
- `--limit <n>`: max results

### `buffer ideas`

List saved ideas.

Options:

- `--limit <n>`: max results

## Common Use Cases

```bash
# Post to one profile
node ./buffer.js post "Just shipped 🚀" --profile <id>

# Schedule for tomorrow
node ./buffer.js post "Tomorrow update" --profile <id> --time "2026-03-03T14:00:00Z"

# Multi-channel post
node ./buffer.js post "New blog live" --profiles id1,id2

# Save draft
node ./buffer.js post "Draft concept" --profile <id> --draft
```

## Troubleshooting

- **Auth errors (401/403):** check `BUFFER_API_KEY`, regenerate key if needed.
- **Rate limits (429):** wait ~60s and retry.
- **Invalid date:** use ISO format like `2026-03-03T14:00:00Z`.
- **Image path error:** verify file exists and path is correct.

## OpenClaw Integration Examples

- “Post to Buffer: `Just shipped a new feature! 🚀` to profile `<id>`”
- “Queue this in Buffer for all profiles: `Weekly recap is live`”
- “Save this as Buffer draft for profile `<id>`: `Campaign angle #3`”
