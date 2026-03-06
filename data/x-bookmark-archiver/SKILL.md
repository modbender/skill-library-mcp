---
name: X Bookmark Archiver
description: Archive your X (Twitter) bookmarks into categorized markdown files
  with AI-generated summaries.
---

# X Bookmark Archiver

Archive your X (Twitter) bookmarks into categorized markdown files with AI-generated summaries.

## Overview

This skill fetches your X bookmarks using the [bird CLI](https://github.com/steipete/bird), categorizes them by URL patterns, generates AI summaries using OpenAI, and saves them as organized markdown files.

## Prerequisites

1. **bird CLI** - Install from [steipete/bird](https://github.com/steipete/bird)
2. **OpenAI API Key** (optional) - Set `OPENAI_API_KEY` for AI-generated summaries
3. **Node.js 18+**

## Installation

```bash
# Ensure bird CLI is installed and authenticated
bird --version

# Set OpenAI API key (optional, for AI summaries)
export OPENAI_API_KEY="sk-..."
```

## Commands

### `run` - Full Pipeline

Fetches new bookmarks and processes them:

```bash
node skills/x-bookmark-archiver/scripts/run.cjs
```

### `run --force` - Process Existing

Skip fetch, process only pending bookmarks:

```bash
node skills/x-bookmark-archiver/scripts/run.cjs --force
```

### `fetch` - Download Bookmarks Only

```bash
node skills/x-bookmark-archiver/scripts/fetch.cjs
```

### `process` - Archive Pending Only

```bash
node skills/x-bookmark-archiver/scripts/process.cjs
```

## Category Mapping

Bookmarks are automatically categorized based on URL patterns:

| Category | Domains |
|----------|---------|
| **tools** | github.com, gitlab.com, github.io, huggingface.co, replicate.com, vercel.com, npmjs.com, pypi.org |
| **articles** | medium.com, substack.com, dev.to, hashnode.dev, x.com/i/article, blog.*, towardsdatascience.com |
| **videos** | youtube.com, youtu.be, vimeo.com, twitch.tv |
| **research** | arxiv.org, paperswithcode.com, semanticscholar.org, researchgate.net, dl.acm.org, ieee.org |
| **news** | techcrunch.com, theverge.com, hn.algolia.com, news.ycombinator.com, wired.com, arstechnica.com |
| **bookmarks** | *fallback for unmatched URLs* |

## Output Location

Markdown files are created in the **OpenClaw workspace** at:

**Legacy installs (old name):**
```
~/clawd/X-knowledge/
```

**New installs:**
```
~/.openclaw/workspace/X-knowledge/
```

**With profile (`OPENCLAW_PROFILE=prod`):**
```
~/.openclaw/workspace-prod/X-knowledge/
```

**Override with environment variable:**
```bash
export OPENCLAW_WORKSPACE=/custom/path
node skills/x-bookmark-archiver/scripts/run.cjs
# Creates: /custom/path/X-knowledge/
```

## Output Structure

```
~/.openclaw/workspace/X-knowledge/
├── tools/
│   ├── awesome-ai-project.md
│   └── useful-cli-tool.md
├── articles/
│   ├── how-to-build-x.md
│   └── ml-best-practices.md
├── videos/
│   └── conference-talk.md
├── research/
│   └── attention-is-all-you-need.md
├── news/
│   └── latest-tech-announcement.md
└── bookmarks/
    └── misc-link.md
```

## Markdown Template

Each archived bookmark gets a markdown file with frontmatter:

```markdown
---
title: "Awesome AI Project"
type: tool
date_archived: 2026-01-31
source_tweet: https://x.com/i/web/status/1234567890
link: https://github.com/user/repo
tags: ["ai", "machine-learning", "github"]
---

This project implements a novel approach to... (AI-generated summary)
```

## State Management

State files track processing progress:

```
/root/clawd/.state/
├── x-bookmark-pending.json     # Bookmarks waiting to be processed
└── x-bookmark-processed.json   # IDs of already-archived bookmarks
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENAI_API_KEY` | No | API key for AI-generated summaries |

## Workflow

1. **Fetch**: Downloads latest 50 bookmarks from X
2. **Filter**: Removes already-processed bookmarks
3. **Expand**: Resolves t.co shortened URLs
4. **Categorize**: Assigns category based on URL domain
5. **Enrich**: Generates title, summary, tags (AI or fallback)
6. **Write**: Saves as markdown in `X-knowledge/{category}/`
7. **Track**: Updates processed IDs, clears pending

## Customization

### Adding Categories

Edit `scripts/lib/categorize.cjs`:

```javascript
const CATEGORIES = {
  tools: ['github.com', '...'],
  your_category: ['example.com', '...'],
  // ...
};
```

### Changing Output Directory

Edit `scripts/process.cjs`:

```javascript
const KNOWLEDGE_DIR = 'your-directory-name';
```

### Using Different AI Provider

Modify the `generateMetadata()` function in `scripts/process.cjs` to use your preferred API.

## Testing

Run the test suite:

```bash
# Run all tests
cd skills/x-bookmark-archiver/tests
node test-all.cjs

# Run individual test suites
node lib/categorize.test.cjs
node lib/state.test.cjs
node integration.test.cjs
```

### Test Coverage

- **Unit tests**: `categorize.js` (21 tests) - URL pattern matching
- **Unit tests**: `state.js` (9 tests) - JSON read/write operations
- **Integration tests** (12 tests) - Full pipeline with mock data

### Manual Testing

Without bird CLI, you can test with mock data:

```bash
# Create mock pending data
cat > /tmp/test-pending.json << 'EOF'
[
  {
    "id": "test123",
    "url": "https://github.com/test/repo",
    "text": "Test bookmark"
  }
]
EOF

# Copy to state directory and process
mkdir -p /root/clawd/.state
cp /tmp/test-pending.json /root/clawd/.state/x-bookmark-pending.json
node skills/x-bookmark-archiver/scripts/process.cjs
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `bird: command not found` | Install bird CLI from GitHub releases |
| No bookmarks fetched | Ensure you're logged into X in bird |
| AI summaries not generating | Check `OPENAI_API_KEY` is set |
| t.co links not expanding | May be network/timeout issues; will use original URL |

## File Structure

```
skills/x-bookmark-archiver/
├── SKILL.md
├── scripts/
│   ├── fetch.cjs          # Download bookmarks from X (CommonJS)
│   ├── process.cjs        # Generate markdown files (CommonJS)
│   ├── run.cjs            # Orchestrate fetch → process (CommonJS)
│   └── lib/
│       ├── categorize.cjs # URL → category mapping (CommonJS)
│       └── state.cjs      # JSON state management (CommonJS)
└── tests/
    ├── test-all.cjs
    ├── lib/
    │   ├── categorize.test.cjs
│   │   └── state.test.cjs
    ├── integration.test.cjs
    └── fixtures/
        └── sample-bookmarks.json
```

## License

MIT
