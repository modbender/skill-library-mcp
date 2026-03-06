---
name: miniflux
description: Manage Miniflux - Modern minimalist feed reader via REST API. Use for listing feeds and entries, creating/removing subscriptions, searching articles, managing categories, and marking entries as read/unread.
metadata:
  {
    "openclaw":
      {
        "requires": { "bins": ["python3"], "env": ["MINIFLUX_URL", "MINIFLUX_TOKEN"] },
        "primaryEnv": "MINIFLUX_TOKEN"
      }
  }
---

# Miniflux Skill

Manage Miniflux - Modern minimalist feed reader via REST API.

Use for listing feeds and entries, creating/removing subscriptions, searching articles, managing categories, and marking entries as read/unread.

## Setup

This skill requires Python and the Miniflux Python client.

```bash
# Install the miniflux Python package
uv pip install miniflux
```

## Configuration

Set the following environment variables:

```bash
export MINIFLUX_URL="https://your-miniflux-instance.com"
export MINIFLUX_TOKEN="your-api-token-here"
```

To get an API token:
1. Log in to your Miniflux instance
2. Go to Settings > API Keys
3. Click "Create a new API key"
4. Copy the token and set it in MINIFLUX_TOKEN

## Usage

### CLI Wrapper

```bash
# List all feeds
bash miniflux.sh feeds

# List categories
bash miniflux.sh categories

# Get unread entries
bash miniflux.sh entries --status unread

# Search entries
bash miniflux.sh entries --search "kubernetes"

# Create a new feed
bash miniflux.sh create-feed --url "https://example.com/feed.xml" --category 1

# Refresh all feeds
bash miniflux.sh refresh-all

# Mark entries as read
bash miniflux.sh mark-read --entry-ids 123,456

# Mark feed as read
bash miniflux.sh mark-feed-read --feed-id 42

# Toggle bookmark/star
bash miniflux.sh toggle-bookmark --entry-id 123

# Discover subscriptions from a website
bash miniflux.sh discover --url "https://example.org"

# Delete a feed
bash miniflux.sh delete-feed --feed-id 42

# Get feed details
bash miniflux.sh feed --feed-id 42

# Get counters (unread/read)
bash miniflux.sh counters

# Get current user info
bash miniflux.sh me

# Get specific entry
bash miniflux.sh entry --entry-id 123

# Create category
bash miniflux.sh create-category --title "Tech News"

# Delete category
bash miniflux.sh delete-category --category-id 5

# Update feed
bash miniflux.sh update-feed --feed-id 42 --title "New Title" --category-id 3
```

## Commands Reference

| Command | Description |
|---------|-------------|
| `feeds` | List all feeds |
| `categories` | List all categories |
| `entries` | List entries with filters (status, search, limit, etc.) |
| `entry` | Get a specific entry by ID |
| `create-feed` | Create a new feed subscription |
| `update-feed` | Update an existing feed |
| `delete-feed` | Delete a feed |
| `refresh-all` | Refresh all feeds |
| `refresh-feed` | Refresh a specific feed |
| `mark-read` | Mark specific entries as read |
| `mark-unread` | Mark specific entries as unread |
| `mark-feed-read` | Mark all entries of a feed as read |
| `toggle-bookmark` | Toggle bookmark/star status of an entry |
| `discover` | Discover subscriptions from a URL |
| `counters` | Get unread/read counters per feed |
| `me` | Get current user info |
| `create-category` | Create a new category |
| `delete-category` | Delete a category |

## Filters for Entries

When using the `entries` command, you can filter by:

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

## Examples

```bash
# Get last 10 unread entries
bash miniflux.sh entries --status unread --limit 10

# Search for Kubernetes articles
bash miniflux.sh entries --search "kubernetes" --limit 20

# Get entries from a specific feed
bash miniflux.sh entries --feed-id 42 --limit 15

# Get starred entries
bash miniflux.sh entries --starred true

# Create a feed with crawler enabled
bash miniflux.sh create-feed --url "https://techcrunch.com/feed/" --category 1 --crawler true

# Discover feeds from a blog
bash miniflux.sh discover --url "https://example.com"
```

## API Endpoints Supported

- `/v1/feeds` - List feeds
- `/v1/feeds/{id}` - Get feed details
- `/v1/feeds/{id}/entries` - Get feed entries
- `/v1/feeds/{id}/refresh` - Refresh feed
- `/v1/feeds/{id}/mark-all-as-read` - Mark feed entries as read
- `/v1/categories` - List categories
- `/v1/categories/{id}/entries` - Get category entries
- `/v1/entries` - List entries
- `/v1/entries/{id}` - Get entry
- `/v1/entries/{id}/bookmark` - Toggle bookmark
- `/v1/feeds/refresh` - Refresh all feeds
- `/v1/discover` - Discover subscriptions
- `/v1/feeds/counters` - Get counters
- `/v1/me` - Current user info

## Error Handling

The script will exit with error code 1 on API errors and display the error message from Miniflux.

## Dependencies

- Python 3.8+
- Miniflux Python client (`uv pip install miniflux`)

## Documentation

Full API documentation: https://miniflux.app/docs/api.html
