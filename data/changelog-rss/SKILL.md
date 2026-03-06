---
name: changelog-rss
description: Convert CHANGELOG.md files into RSS 2.0 feeds for release monitoring.
---


# Changelog RSS

Convert CHANGELOG.md into an RSS feed for release tracking.

## Instructions

### Step 1: Locate the Changelog
Accept from user:
- Local `CHANGELOG.md` path
- GitHub repo URL → fetch `CHANGELOG.md` or use Releases API as fallback
- npm/pip package names → locate their changelogs

### Step 2: Parse and Convert
Parse [Keep a Changelog](https://keepachangelog.com/) format:
- Extract version headers: `## [x.y.z] - YYYY-MM-DD`
- Extract sections: Added, Changed, Deprecated, Removed, Fixed, Security
- Handle variations: `## x.y.z`, `## v1.2.3`, date in various formats

Generate valid RSS 2.0:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>{Project} Changelog</title>
    <link>{repo-url}</link>
    <description>Release notes for {Project}</description>
    <item>
      <title>v1.2.0</title>
      <pubDate>Mon, 01 Jan 2025 00:00:00 GMT</pubDate>
      <description><![CDATA[<h3>Added</h3><ul><li>...</li></ul>]]></description>
    </item>
  </channel>
</rss>
```

### Step 3: Output
- Save RSS file and provide the path
- Suggest hosting on GitHub Pages or a static file server
- For ongoing monitoring: regenerate via cron job

## Edge Cases

- **Non-standard formats**: Best-effort parsing; warn user about unparsed sections
- **No dates**: Use file modification date or git log dates as fallback
- **Multiple changelogs**: Aggregate into a single feed with source prefixes
- **Unreleased section**: Skip `## [Unreleased]` entries

## Requirements

- No dependencies for basic conversion (text processing)
- Optional: `curl` for fetching remote changelogs
- No API keys needed
