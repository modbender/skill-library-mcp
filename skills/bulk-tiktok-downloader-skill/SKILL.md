---
name: bulk-tiktok-downloader
description: Bulk download TikTok videos from a text file of URLs using yt-dlp. Use when a user asks to download many TikTok videos at once, process a URL list file, or save TikTok videos to a specific folder from local terminal.
---

# bulk TikTok downloader

Use this skill to run a local bulk TikTok downloader safely and reproducibly.

## Safety + legality

- Download only content you are authorized to download.
- Respect platform Terms of Service, local copyright rules, and user privacy.
- Do not bypass paywalls or private/protected content.

## Inputs

- URL list file (one URL per line)
- Optional output directory

Lines starting with `#` are comments and ignored.

## Setup

From workspace root:

```bash
python3 -m pip install --user -r skills/bulk-tiktok-downloader/scripts/requirements.txt
```

## Run

Default (uses `urls.txt` next to script and `downloads/` output):

```bash
python3 skills/bulk-tiktok-downloader/scripts/downloader.py
```

Custom URL file:

```bash
python3 skills/bulk-tiktok-downloader/scripts/downloader.py my_urls.txt
```

Custom URL file + output directory:

```bash
python3 skills/bulk-tiktok-downloader/scripts/downloader.py my_urls.txt my_downloads
```

## Recommended workflow

1. Validate URL list file exists and is non-empty.
2. Run downloader.
3. Report successful vs failed counts.
4. Surface failed URLs and likely reason (private/deleted/region restricted/rate limit).

## Troubleshooting

- `No module named yt_dlp` → install requirements.
- `File not found` → verify URL file path.
- Frequent failures/rate limit → reduce batch size and retry later.

## Upstream reference

See:
- `skills/bulk-tiktok-downloader/references/upstream-readme.md`
