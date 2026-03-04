# SKILL.md — Reddit Archive

_Download and archive Reddit posts (images, GIFs, videos) from users or subreddits._

## Auto-Installation

This script automatically checks for and installs its dependencies on first run:

- **requests** — Python HTTP library
- **yt-dlp** — video downloader

If missing, it will attempt to install them via `pip install --user`. You can also:
- Pre-install: `pip3 install requests yt-dlp`
- Override yt-dlp path: `export YTDLP_PATH=/your/custom/path/yt-dlp`

## When to Use

You want to archive content from Reddit — either from a specific user (`u/username`) or a subreddit (`r/subname`).

## Usage

```bash
python3 ~/path/to/reddit_archive.py [options]
```

### Options

| Flag | Description | Default |
|------|-------------|---------|
| `-u, --user` | Reddit username (either this OR --subreddit required) | — |
| `-s, --subreddit` | Subreddit name (either this OR --user required) | — |
| `-o, --output` | Output directory | `~/temp/.reddit_<target>` |
| `--sort` | Sort order: hot, new, rising, top, controversial | `hot` |
| `--time` | Time filter for top/controversial: hour, day, week, month, year, all | — |
| `--after` | Start date (YYYY-MM-DD) | No filter |
| `--before` | End date (YYYY-MM-DD) | No filter |
| `--limit` | Max posts to fetch (0 = unlimited) | 0 |
| `--images` | Download images (jpg, png, webp) | ✓ |
| `--gifs` | Download GIFs/videos (gfycat, redgifs, imgur) | ✓ |
| `--skip-existing` | Skip already-downloaded files | ✓ |
| `--workers` | Parallel download workers | 4 |

### Examples

```bash
# All posts from a user
python3 reddit_archive.py -u someuser

# Subreddit with date range
python3 reddit_archive.py -s orlando --after 2025-01-01 --before 2025-12-31

# Top 10 most upvoted posts of all time from a subreddit
python3 reddit_archive.py -s funny --sort top --time all --limit 10

# New posts only
python3 reddit_archive.py -s orlando --sort new

# GIFs only, specific user
python3 reddit_archive.py -u someguy --gifs

# Custom output dir
python3 reddit_archive.py -u someuser -o ~/Downloads/reddit_archive
```

## Output

Downloads are saved to the output directory with the following structure:

```
output_directory/
├── Pictures/
│   ├── {target}_{post_id}.jpg
│   ├── {target}_{post_id}.png
│   └── ...
└── Videos/
    ├── {target}_{post_id}.mp4
    └── ...
```

## File Organization

The skill is organized as:

```
reddit-archive/
├── SKILL.md              ← This file
└── scripts/
    ├── reddit_archive.py ← Main downloader script
    └── requirements.txt  ← Python dependencies
```

## Rate Limiting

- Pauses 0.8s between Reddit API calls to avoid 403s
- Uses `requests` with proper User-Agent header
- Run one instance at a time — parallel runs trigger rate limits

## Technical Notes

- Uses Reddit's JSON API (`/user/{name}/submitted.json` or `/r/{name}/hot.json`)
- For galleries, extracts all images from `media_metadata`
- GIF/video downloads use `yt-dlp`
- Date filtering is done client-side after fetching (filters by Reddit's `created_utc`)
