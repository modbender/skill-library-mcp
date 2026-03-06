---
name: xiaohongshu-downloader
description: Download videos from Xiaohongshu (小红书) pages. Use when the user wants to save or download a video from a xiaohongshu.com URL, or mentions "小红书视频下载", "保存小红书视频", or similar requests.
---

# Xiaohongshu Video Downloader

Download videos from Xiaohongshu (小红书) by extracting the real CDN URL from the page.

## How It Works

Xiaohongshu videos use blob URLs in the browser, which cannot be downloaded directly. This skill:

1. Uses browser automation to load the page (required for JS rendering)
2. Extracts the real CDN video URL from the page HTML
3. Downloads the video with proper headers

## Method 1: Browser Automation (Recommended)

Use the browser tool to extract the video URL:

1. Navigate to the Xiaohongshu page:
```
browser action=navigate targetUrl="https://www.xiaohongshu.com/explore/NOTE_ID"
```

2. Extract the video URL with JavaScript:
```javascript
(() => {
  const html = document.documentElement.outerHTML;
  const mp4Matches = html.match(/https?:\/\/[^"\s]+\.mp4[^"\s]*/g);
  if (mp4Matches) return [...new Set(mp4Matches)];
  return null;
})()
```

3. Download with curl:
```bash
curl -L -o output.mp4 "<VIDEO_URL>" \
  -H "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36" \
  -H "Referer: https://www.xiaohongshu.com/"
```

## Method 2: Python Script

For pages that don't require authentication:

```bash
python3 scripts/download_video.py "https://www.xiaohongshu.com/explore/NOTE_ID"
```

Note: The Python script may not work for all pages due to:
- JavaScript rendering requirements
- Authentication/login requirements
- Rate limiting

## Notes

- Videos are typically hosted on `xhscdn.com` CDN
- User-Agent and Referer headers are required to avoid 403 errors
- Output directory: `~/Downloads/xiaohongshu/`
- Video URLs follow pattern: `https://sns-video-*.xhscdn.com/stream/.../*.mp4`
