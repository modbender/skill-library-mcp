---
description: Detect duplicate bookmarks, check for dead links, and organize bookmark exports.
---

# Browser Bookmarks

Analyze and clean up browser bookmark exports.

## Capabilities

- **Duplicate Detection**: Find duplicate URLs across folders
- **Dead Link Check**: HTTP HEAD requests to detect broken links
- **Organization**: Categorize and suggest folder restructuring
- **Export Parsing**: Chrome/Firefox HTML and JSON bookmark formats

## Instructions

1. **Parse bookmarks**: Extract URLs, titles, folders from HTML/JSON export
   ```bash
   # Extract URLs from Chrome HTML export
   grep -oP 'HREF="\K[^"]+' bookmarks.html | sort > urls.txt
   wc -l urls.txt  # total bookmarks
   ```

2. **Find duplicates**:
   ```bash
   sort urls.txt | uniq -d  # duplicate URLs
   sort urls.txt | uniq -c | sort -rn | head -20  # most duplicated
   ```

3. **Check dead links** (batch with rate limiting):
   ```bash
   while read url; do
     code=$(curl -s -o /dev/null -w "%{http_code}" -m 5 -L "$url" 2>/dev/null)
     [ "$code" != "200" ] && echo "$code $url"
     sleep 0.5  # rate limit
   done < urls.txt
   ```

4. **Report format**:
   ```
   📚 Bookmark Analysis — <filename>
   Total: 342 | Duplicates: 18 | Dead: 7

   ## Duplicates
   | URL | Count | Folders |
   |-----|-------|---------|

   ## Dead Links (non-200)
   | URL | Status | Title |
   |-----|--------|-------|
   ```

## Edge Cases

- **Large exports (>5000 bookmarks)**: Sample dead link checks; full duplicate scan is fine
- **Paywalled sites**: May return 403 — flag as "possibly paywalled" not "dead"
- **Redirects**: Follow redirects (`curl -L`); flag permanent redirects (301) for URL updates

## Security

- Bookmark files may contain private/internal URLs — don't share results publicly
- Rate-limit external requests to avoid IP blocks

## Requirements

- Exported bookmarks file (Chrome: `chrome://bookmarks` → Export, Firefox: Library → Export)
- `curl`, `grep`, `sort` (standard Unix tools)
- No API keys needed
