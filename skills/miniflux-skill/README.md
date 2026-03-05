# Miniflux Skill for OpenClaw

Manage Miniflux - Modern minimalist feed reader via REST API.

## Overview

This skill provides a CLI interface to Miniflux, allowing you to:
- List feeds and entries
- Create/remove/update subscriptions
- Search and read articles
- Manage categories
- Mark entries as read/unread
- Discover new subscriptions

## Installation

1. Install the Python Miniflux client:

```bash
python3 -m pip install --user --break-system-packages miniflux
```

Or using uv (recommended):

```bash
uv pip install --system miniflux
```

2. Set up environment variables:

```bash
export MINIFLUX_URL="https://reader.etereo.cloud"
export MINIFLUX_TOKEN="your-api-token-here"
```

To get an API token:
- Log in to your Miniflux instance
- Go to Settings > API Keys
- Click "Create a new API key"
- Copy the token

## Usage

### Basic Commands

```bash
# List all feeds
bash /home/moltbot/clawd/skills/miniflux/scripts/miniflux.sh feeds

# List categories
bash /home/moltbot/clawd/skills/miniflux/scripts/miniflux.sh categories

# Get unread entries (last 10)
bash /home/moltbot/clawd/skills/miniflux/scripts/miniflux.sh entries --status unread --limit 10

# Search for articles
bash /home/moltbot/clawd/skills/miniflux/scripts/miniflux.sh entries --search "kubernetes"

# Get current user info
bash /home/moltbot/clawd/skills/miniflux/scripts/miniflux.sh me

# Get counters
bash /home/moltbot/clawd/skills/miniflux/scripts/miniflux.sh counters
```

### Feed Management

```bash
# Create a new feed
bash /home/moltbot/clawd/skills/miniflux/scripts/miniflux.sh create-feed --url "https://example.com/feed.xml" --category 1

# Update a feed
bash /home/moltbot/clawd/skills/miniflux/scripts/miniflux.sh update-feed --feed-id 42 --title "New Title" --category 3

# Delete a feed
bash /home/moltbot/clawd/skills/miniflux/scripts/miniflux.sh delete-feed --feed-id 42

# Refresh all feeds
bash /home/moltbot/clawd/skills/miniflux/scripts/miniflux.sh refresh-all

# Refresh a specific feed
bash /home/moltbot/clawd/skills/miniflux/scripts/miniflux.sh refresh-feed --feed-id 42
```

### Entry Management

```bash
# Get specific entry
bash /home/moltbot/clawd/skills/miniflux/scripts/miniflux.sh entry --entry-id 123

# Mark entries as read
bash /home/moltbot/clawd/skills/miniflux/scripts/miniflux.sh mark-read --entry-ids "123,456,789"

# Mark entries as unread
bash /home/moltbot/clawd/skills/miniflux/scripts/miniflux.sh mark-unread --entry-ids "123,456"

# Mark all entries in a feed as read
bash /home/moltbot/clawd/skills/miniflux/scripts/miniflux.sh mark-feed-read --feed-id 42
```

### Category Management

```bash
# Create a new category
bash /home/moltbot/clawd/skills/miniflux/scripts/miniflux.sh create-category --title "Tech News"

# Delete a category
bash /home/moltbot/clawd/skills/miniflux/scripts/miniflux.sh delete-category --category-id 5
```

### Discovery

```bash
# Discover feeds from a website
bash /home/moltbot/clawd/skills/miniflux/scripts/miniflux.sh discover --url "https://example.org"
```

## Advanced Filters

For the `entries` command, you can use these filters:

- `--status`: Entry status (unread, read, or removed)
- `--limit`: Number of entries to return (default: 100)
- `--offset`: Number of entries to skip
- `--direction`: Sort direction (asc or desc)
- `--search`: Search query string
- `--category-id`: Filter by category ID
- `--feed-id`: Filter by feed ID
- `--starred`: Filter starred entries (true/false)
- `--before`: Unix timestamp for entries before this time
- `--after`: Unix timestamp for entries after this time
- `--full-content`: Show full content (default: summary)

## Examples

```bash
# Get last 20 unread entries from a specific category
bash /home/moltbot/clawd/skills/miniflux/scripts/miniflux.sh entries --status unread --category-id 2 --limit 20

# Search for Kubernetes articles published recently
bash /home/moltbot/clawd/skills/miniflux/scripts/miniflux.sh entries --search "kubernetes" --status unread --limit 10

# Get starred entries with full content
bash /home/moltbot/clawd/skills/miniflux/scripts/miniflux.sh entries --starred true --full-content

# Create a feed with crawler enabled
bash /home/moltbot/clawd/skills/miniflux/scripts/miniflux.sh create-feed --url "https://techcrunch.com/feed/" --category 1 --crawler
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `MINIFLUX_URL` | Miniflux base URL | https://reader.etereo.cloud |
| `MINIFLUX_TOKEN` | API authentication token | Required |

## API Reference

Full API documentation: https://miniflux.app/docs/api.html

## Troubleshooting

### Error: miniflux package not installed

```bash
python3 -m pip install --user --break-system-packages miniflux
```

### Error: MINIFLUX_TOKEN not set

Make sure to set the environment variable:

```bash
export MINIFLUX_TOKEN="your-token-here"
```

### API returns 404

Make sure the MINIFLUX_URL is set correctly (without `/v1/` at the end):

```bash
export MINIFLUX_URL="https://reader.etereo.cloud"  # Correct
export MINIFLUX_URL="https://reader.etereo.cloud/v1/"  # Wrong
```

## License

This skill is part of OpenClaw and follows the same license.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines.

### Semantic Releases

This project uses [semantic releases](https://www.conventionalcommits.org/) with [release-please-action](https://github.com/googleapis/release-please-action).

#### Commit Format

```
<type>(<scope>): <subject>
```

Types:
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation
- `test:` Tests
- `chore:` Build/auxiliary changes

Example:
```bash
git commit -m "feat(feeds): add OPML import support"
git commit -m "fix(auth): handle missing MINIFLUX_TOKEN gracefully"
```

#### Release Process

1. Create PR with conventional commits
2. CI runs tests
3. Merge to `master` triggers release workflow
4. Automatic version bump based on commit types
5. CHANGELOG.md updated automatically
6. Published to ClawHub

## Tests

```bash
# Install dependencies
make install

# Run tests
make test

# Run all checks
make check
```

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history.
