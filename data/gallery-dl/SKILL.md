---
name: gallery-dl
description: "Download image galleries and collections from 100+ sites. Use
  when: (1) Downloading from Reddit, Twitter, Instagram, Pixiv, Danbooru, (2)
  Batch downloading image galleries, (3) Archiving artist portfolios, (4)
  Downloading from specific tags or users."
---


# gallery-dl

Download image galleries and collections from 100+ sites.

## When This Skill Activates

This skill triggers when user wants to download images from Reddit, Twitter, Instagram, Pixiv, Danbooru, or other supported sites.

## Reasoning Framework

| Step | Action | Why |
|------|--------|-----|
| 1 | **INSTALL** | Install gallery-dl via pip |
| 2 | **AUTH** | Configure authentication if needed |
| 3 | **EXTRACT** | Determine site and URL type |
| 4 | **DOWNLOAD** | Fetch images with options |
| 5 | **ORGANIZE** | Save to appropriate folder |

---

## Install

```bash
pip install gallery-dl
```

---

## Decision Tree

### What are you trying to do?

```
├── Download from Reddit
│   └── Use: gallery-dl "https://www.reddit.com/r/subreddit/"
│
├── Download from Twitter/X
│   └── Use: gallery-dl "https://twitter.com/user/media"
│
├── Download from Pixiv
│   └── Use: gallery-dl "https://www.pixiv.net/users/12345"
│
├── Download from Danbooru
│   └── Use: gallery-dl "https://danbooru.donmai.us/posts?tags=tag"
│
├── Batch download
│   └── Use: gallery-dl "URL" --limit 10
│
└── Custom filename
    └── Use: gallery-dl "URL" -f "{id}.{extension}"
```

---

## Supported Sites

Reddit, Twitter/X, Instagram, Tumblr, Pixiv, Danbooru, Gelbooru, Furbooru, ArtStation, DeviantArt, Flickr, Newgrounds, HBO, TikTok, YouTube, and 100+ more.

Full list: https://github.com/mikf/gallery-dl#supported-services

---

## Basic Usage

### Command

```bash
gallery-dl "URL" [options]
```

### Examples

```bash
# Download from Reddit
gallery-dl "https://www.reddit.com/r/wallpapers/"

# Download to specific folder
gallery-dl "URL" -D /path/to/folder

# Download specific user's posts
gallery-dl "https://twitter.com/username/media"

# Download from Pixiv artist
gallery-dl "https://www.pixiv.net/users/12345"

# Download from Danbooru tags
gallery-dl "https://danbooru.donmai.us/posts?tags=cat"
```

---

## Options

| Flag | Description | Default |
|------|-------------|---------|
| `-D, --directory PATH` | Download location | ./gallery-dl |
| `-f, --filename FORMAT` | Filename template | {id}.{extension} |
| `--range RANGE` | Download range (e.g., 1-10) | all |
| `--limit N` | Limit number of downloads | no limit |
| `--username USER` | Login username | - |
| `--password PASS` | Login password | - |
| `--netrc` | Use .netrc for auth | false |

---

## Filename Templates

```bash
# Default (id.extension)
gallery-dl "URL" -f "{id}.{extension}"

# By date (YYYY/id.extension)
gallery-dl "URL" -f "{date:%Y}/{id}.{extension}"

# By site (site/id.extension)
gallery-dl "URL" -f "{domain}/{id}.{extension}"

# Original filename
gallery-dl "URL" -f "/O"
```

---

## Authentication

Many sites need login. Choose one method:

### 1. Command Line

```bash
gallery-dl "URL" --username USER --password PASS
```

### 2. .netrc File

Create `~/.netrc`:

```
machine twitter.com
login username
password password
```

### 3. Config File

Create `~/.config/gallery-dl/config.json`:

```json
{
    "extractor": {
        "twitter": {
            "username": "user",
            "password": "pass"
        },
        "pixiv": {
            "username": "user", 
            "password": "pass"
        }
    }
}
```

---

## Common Examples

```bash
# Reddit subreddit
gallery-dl "https://www.reddit.com/r/earthporn/" -D ./earthporn

# Twitter user media
gallery-dl "https://twitter.com/elonmusk/media" -D ./elon

# Pixiv artist
gallery-dl "https://www.pixiv.net/users/12345" -D ./pixiv

# Danbooru tag
gallery-dl "https://danbooru.donmai.us/posts?tags=cat" -D ./cat

# Download only first 10
gallery-dl "URL" --limit 10

# Download range
gallery-dl "URL" --range 1-50
```

---

## Troubleshooting

### Problem: "gallery-dl: command not found"

- **Cause:** Not installed
- **Fix:** `pip install gallery-dl`

### Problem: "HTTP Error 401: Unauthorized"

- **Cause:** Need login
- **Fix:** Configure authentication (--username/--password or config)

### Problem: "HTTP Error 403: Forbidden"

- **Cause:** Rate limited or private content
- **Fix:** Wait or check credentials

### Problem: "No images found"

- **Cause:** Wrong URL or no media
- **Fix:** Verify URL is correct for the site

### Problem: "Permission denied"

- **Cause:** No write permission
- **Fix:** Check folder permissions or use -D with writable path

---

## Self-Check

- [ ] gallery-dl installed: `gallery-dl --version`
- [ ] URL is correct for the site
- [ ] For private sites: authentication configured
- [ ] Output directory exists and is writable
- [ ] Rate limiting respected (don't spam)

---

## Quick Reference

| Task | Command |
|------|---------|
| Download Reddit | `gallery-dl "https://www.reddit.com/r/sub/"` |
| Download Twitter | `gallery-dl "https://twitter.com/user/media"` |
| Download Pixiv | `gallery-dl "https://www.pixiv.net/users/12345"` |
| Custom folder | `gallery-dl "URL" -D ./folder` |
| Limit 10 | `gallery-dl "URL" --limit 10` |
| Custom name | `gallery-dl "URL" -f "{id}.{extension}"` |

---
