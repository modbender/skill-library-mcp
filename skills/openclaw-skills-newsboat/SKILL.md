---
name: newsboat
description: OpenClaw AI agent skill for reading and managing RSS/Atom feeds via Newsboat.
homepage: https://github.com/ianwu-ca-778/openclaw-skills-newsboat
license: MIT
metadata:
  {
    "openclaw":
      { 
        "emoji": "📰",
        "requires": { "bins": ["newsboat", "sqlite3", "pandoc"] }
      }
  }
---

# Newsboat

This guide explains how to read and manage RSS/Atom feeds using Newsboat, a command-line RSS/Atom feed reader.

## Installation

### Debian/Ubuntu

```bash
sudo apt update
sudo apt install newsboat sqlite3 pandoc
```

### macOS

```bash
brew install newsboat sqlite3 pandoc
```

### Others

Search online for “install newsboat on [your OS]” for specific instructions.

## Files
  - configuration: ~/.newsboat/config
  - feed URLs: ~/.newsboat/urls
  - cache: ~/.newsboat/cache.db

If Newsboat is not in your PATH, use your OS search to locate its files.

## List Feeds

```bash
cat ~/.newsboat/urls
```

### Example output
```
$ cat ~/.newsboat/urls
https://604now.com/rss/
```

## Add a Feed

```bash
echo "https://example.com/feed.xml" >> ~/.newsboat/urls
```

## Remove a Feed

```bash
sed -i.bak '/https:\/\/example.com\/feed.xml/d' ~/.newsboat/urls
```

This removes the feed URL and creates a backup `urls.bak`.

## Refresh All Feeds

```bash
newsboat -x reload
```

## Read an article

Retrieve articles from the Newsboat cache using `sqlite3` and convert HTML to plain text with `pandoc`.

The rss_item table schema:
```sql
CREATE TABLE rss_item (
	id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL
	,guid VARCHAR(64) NOT NULL
	,title VARCHAR(1024) NOT NULL
	,author VARCHAR(1024) NOT NULL
	,url VARCHAR(1024) NOT NULL
	,feedurl VARCHAR(1024) NOT NULL
	,pubDate INTEGER NOT NULL
	,content VARCHAR(65535) NOT NULL
	,unread INTEGER (1) NOT NULL
	,enclosure_url VARCHAR(1024)
	,enclosure_type VARCHAR(1024)
	,enqueued INTEGER (1) NOT NULL DEFAULT 0
	,flags VARCHAR(52)
	,deleted INTEGER (1) NOT NULL DEFAULT 0
	,base VARCHAR(128) NOT NULL DEFAULT ""
	,content_mime_type VARCHAR(255) NOT NULL DEFAULT ""
	,enclosure_description VARCHAR(1024) NOT NULL DEFAULT ""
	,enclosure_description_mime_type VARCHAR(128) NOT NULL DEFAULT ""
);
```

### Read the latest article

```bash
sqlite3 -noheader ~/.newsboat/cache.db \
"SELECT 'title = ' || title || '\nurl   = ' || url || '\ndate  = ' || datetime(pubDate, 'unixepoch', 'localtime') || '\n\n' || content 
 FROM rss_item ORDER BY pubDate DESC LIMIT 1;" | \
pandoc -f html-native_divs-native_spans -t plain --strip-comments
```

### Example output
```
$ sqlite3 -noheader ~/.newsboat/cache.db \
"SELECT 'title = ' || title || '\nurl   = ' || url || '\ndate  = ' || datetime(pubDate, 'unixepoch', 'localtime') || '\n\n' || content 
 FROM rss_item ORDER BY pubDate DESC LIMIT 1;" | \
pandoc -f html-native_divs-native_spans -t plain --strip-comments

title = 90+ Tri-Cities Restaurants Are Dropping Exclusive Deals And
Menus For A Full Month\nurl =
https://604now.com/taste-of-the-tri-cities-february-march-2026/\ndate =
2026-02-13 16:36:10\n\n

Taste of the Tri-Cities returns for another delicious year, treating
everyone across Metro Vancouver to the amazing culinary delights that
the Coquitlam, Port Coquitlam, and Port Moody has to offer. For a whole
month, from February 15 to March 15, you can take part in one of the
tastiest annual festivals in the Lower Mainland.
```
