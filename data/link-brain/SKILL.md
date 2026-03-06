---
name: link-brain
version: 4.3.0
description: "Local knowledge base for links. Save URLs with summaries and tags, search later using natural language, build collections, and review your backlog with spaced repetition. Includes a standalone HTML graph view."
---

# Link Brain

Your personal bookmark graveyard, except things actually come back.

## Quick Start

```bash
python3 scripts/brain.py quickstart           # auto-imports browser bookmarks + opens GUI
python3 scripts/brain.py save "https://example.com" --auto
python3 scripts/brain.py search "that article about sqlite"
```

### First Run

On first run, use `quickstart` instead of `setup`. It:
1. Creates the database
2. Scans Chrome, Safari, and Firefox for bookmarks
3. Imports everything it finds (skips duplicates)
4. Generates the visual GUI console
5. Returns JSON with import stats

`setup` also detects browsers and reports what it finds, but doesn't auto-import. Use `quickstart` when the user wants the fastest path to a working knowledge base.

## What It Does

- Saves URLs with titles, summaries, tags, and metadata
- Full-text search with natural language filters
- Auto-fetches and summarizes pages locally (no API keys)
- Spaced repetition so your saved links don't rot
- Collections for organizing reading lists
- Knowledge graph visualization
- Reading stats, streaks, and weekly digests
- Imports from Chrome, Safari, Firefox, Pocket, YouTube, Reddit
- Everything in SQLite. Everything on disk. No accounts. No telemetry.

Data lives in `~/.link-brain/`. Override with `LINK_BRAIN_DIR=/your/path`.

## Saving Links

### Manual

You know the title. You know what it's about. Just tell it.

```bash
python3 scripts/brain.py save "https://docs.python.org" \
  --title "Python docs" \
  --summary "Standard library reference." \
  --tags "python, docs"
```

### Auto

Point it at a URL. It fetches the page, extracts readable text, generates a summary, and suggests tags based on your existing collection. No LLM needed.

```bash
python3 scripts/brain.py auto-save "https://example.com"
```

Or equivalently:

```bash
python3 scripts/brain.py save "https://example.com" --auto
```

This is the only command that makes a network request. Everything else is local.

## Finding Stuff

### Search

SQLite FTS5 under the hood, but you can write queries like a person.

```bash
python3 scripts/brain.py search "last week unread from github"
python3 scripts/brain.py search "best rated rust"
python3 scripts/brain.py search "unrated videos from youtube"
python3 scripts/brain.py search "oldest unread" --limit 10
```

### Tags

```bash
python3 scripts/brain.py tags                    # list all tags
python3 scripts/brain.py tags python             # links tagged "python"
```

### Related

Find links that share tags with a specific one.

```bash
python3 scripts/brain.py related 42
```

### Tag Suggestions

Get tag ideas for a URL based on your patterns.

```bash
python3 scripts/brain.py suggest-tags "https://example.com"
```

## Discovery

When you don't know what to read next.

- `digest` pulls a batch of links for review
- `recommend` surfaces links based on your most-used tags
- `gems` shows your highest-rated links and hidden finds
- `random` grabs something from the backlog

```bash
python3 scripts/brain.py digest
python3 scripts/brain.py recommend
python3 scripts/brain.py gems
python3 scripts/brain.py random
```

## Reading Tracking

```bash
python3 scripts/brain.py read 42                # mark as read
python3 scripts/brain.py unread                  # show unread links
python3 scripts/brain.py rate 42 5               # rate 1-5
python3 scripts/brain.py streak                  # current streak and activity
python3 scripts/brain.py insights                # reading personality, analytics
python3 scripts/brain.py weekly                  # weekly summary, WhatsApp-ready
```

`streak` tracks consecutive days you've read something. `insights` tells you things like your most active hours and top domains. `weekly` is a formatted digest you can send straight to a chat.

## Collections

Reading lists that reference your saved links.

```bash
python3 scripts/brain.py collection create "Rust" --description "Systems stuff"
python3 scripts/brain.py collection add "Rust" 42
python3 scripts/brain.py collection show "Rust"
python3 scripts/brain.py collection list
python3 scripts/brain.py collection remove "Rust" 42
python3 scripts/brain.py collection export "Rust"            # markdown
python3 scripts/brain.py collection export "Rust" --html     # standalone HTML
```

## Review Queue

Spaced repetition for your bookmarks. Every saved link enters the queue. Intervals grow as you review: 1 day, 3 days, 7 days, and so on.

```bash
python3 scripts/brain.py review                  # next due item
python3 scripts/brain.py review done 42          # reviewed, advance interval
python3 scripts/brain.py review skip 42          # not now
python3 scripts/brain.py review reset 42         # back to 1-day interval
python3 scripts/brain.py review stats            # queue overview
```

## Auto-Save

The `--auto` flag on `save` (or the `auto-save` shortcut) handles fetching, summarizing, and tagging in one shot. It uses `urllib` to grab the page, extracts the readable content, and picks tags that match your existing vocabulary. No external services involved.

## Knowledge Graph

```bash
python3 scripts/brain.py graph --open
```

Generates a standalone HTML file at `~/.link-brain/graph.html` with an interactive canvas. Links are nodes. Shared tags are edges. No external JS libraries. Just open it in a browser.

## GUI Console

```bash
python3 scripts/brain.py gui
```

Opens `~/.link-brain/console.html` in your browser. Single self-contained HTML file, nothing external. Includes search, tag cloud, knowledge graph, collections, review queue, reading timeline, and dark/light mode.

Add `--no-open` to generate without launching.

## Importing

### Browsers

Pull bookmarks directly:

```bash
python3 scripts/brain.py scan chrome
python3 scripts/brain.py scan safari
python3 scripts/brain.py scan firefox
```

Reads from the browser's local bookmark storage. No export step needed.

### Platforms

Import from exported files:

```bash
python3 scripts/brain.py import pocket_export.html
python3 scripts/brain.py import youtube_history.json
python3 scripts/brain.py import reddit_saved.csv
```

**How to get your exports:**

- **Pocket**: Go to getpocket.com/export. You'll get an HTML file.
- **YouTube**: Use Google Takeout. Select YouTube, then pick watch history. You'll get a JSON file.
- **Reddit**: Go to reddit.com/prefs/data-request or old.reddit.com and export saved posts.

## Syncing

Check for bookmarks that have been removed from a browser source:

```bash
python3 scripts/brain.py sync chrome
python3 scripts/brain.py sources              # see connected sources and sync status
```

## Feedback

```bash
python3 scripts/brain.py feedback "your message"
python3 scripts/brain.py feedback --bug "something broke"
python3 scripts/brain.py feedback --idea "wouldn't it be cool if..."
python3 scripts/brain.py debug                # system info for bug reports
```

## Config

All data is stored in `~/.link-brain/`:

- `brain.db` (SQLite database)
- `graph.html` (knowledge graph output)
- `console.html` (GUI console)
- `collection-*.md` and `collection-*.html` (exported collections)

Override the directory:

```bash
LINK_BRAIN_DIR=/tmp/test-brain python3 scripts/brain.py setup
```

## Tips

- `search` understands time filters like "last week" and reading states like "unread" or "best rated"
- Use `--auto` on every save unless you have a specific summary in mind. It's fast and surprisingly good.
- `review stats` tells you how many links are overdue. Check it weekly.
- `gems` is great for rediscovering old links you forgot you loved
- Export a collection as HTML to share a reading list with someone
- The graph gets more interesting after about 50 links. Before that, it's a bit lonely.
- `random` is the "I'm bored" button
- Combine `scan` with `sync` to keep browser bookmarks in check
