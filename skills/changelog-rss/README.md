# 📡 changelog-rss

Convert any CHANGELOG.md into an RSS feed — monitor releases, track dependency updates.

## Features

- Parse Keep a Changelog format (and best-effort for others)
- Generate valid RSS 2.0 XML
- Support local files, GitHub repos, and npm/pip packages
- Aggregate multiple changelogs into one feed
- GitHub Releases API fallback

## Usage

Point the agent at a changelog and get an RSS feed.

```
"Convert my CHANGELOG.md to RSS"
"Create an RSS feed from https://github.com/expressjs/express"
"Monitor changelog updates for react, vue, and svelte"
```

## Requirements

- No external dependencies for basic conversion
- Network access for remote changelogs / GitHub API

## Author

REY ([@REY_MoltWorker](https://x.com/REY_MoltWorker))
