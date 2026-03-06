# TikTok Bulk Video Downloader

A simple Python script to download multiple TikTok videos at once from a list of URLs.

## Features

- Download multiple TikTok videos in one go
- Read URLs from a text file (one URL per line)
- Automatic folder creation for downloads
- Progress tracking and error handling
- Downloads best quality available

## Requirements

- Python 3.7 or higher
- yt-dlp library

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

Or install yt-dlp directly:
```bash
pip install yt-dlp
```

## Usage

### Basic Usage

1. Add your TikTok video URLs to `urls.txt` (one URL per line)
2. Run the script:
```bash
python downloader.py
```

Videos will be downloaded to the `downloads/` folder.

### Custom URLs File

You can use a different file for URLs:
```bash
python downloader.py my_urls.txt
```

### Custom Output Folder

Specify both the URLs file and output folder:
```bash
python downloader.py urls.txt my_videos
```

## URLs File Format

Create a text file with TikTok URLs, one per line:

```
https://www.tiktok.com/@username/video/1234567890123456789
https://vm.tiktok.com/ZMabcdefg/
https://www.tiktok.com/@user2/video/9876543210987654321

# Lines starting with # are ignored (comments)
# Both full URLs and short vm.tiktok.com links work
```

## Example

```bash
# 1. Add URLs to urls.txt
echo "https://www.tiktok.com/@username/video/1234567890123456789" >> urls.txt

# 2. Run the downloader
python downloader.py

# Output:
# ==================================================
# TikTok Bulk Video Downloader
# ==================================================
# Found 1 URL(s) to download
# Saving videos to: /path/to/downloads/
#
# [1/1] Downloading: https://www.tiktok.com/@username/video/1234567890123456789
# ✓ Successfully downloaded
#
# ==================================================
# Download complete!
# Successful: 1/1
# ==================================================
```

## Troubleshooting

### "No module named 'yt_dlp'"
Install the required dependency:
```bash
pip install yt-dlp
```

### "File 'urls.txt' not found"
Create a `urls.txt` file in the same directory as the script and add your URLs.

### Download fails for specific videos
Some videos may be private, deleted, or region-restricted. The script will continue with remaining URLs and show a summary of failed downloads.

## Notes

- The script downloads the best quality version available
- Video files are saved as: `{video_title}_{video_id}.mp4`
- Failed downloads are reported at the end
- TikTok may rate-limit requests if downloading many videos quickly

## License

Free to use for personal projects.
