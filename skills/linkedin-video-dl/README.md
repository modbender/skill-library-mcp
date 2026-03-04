# linkedin-video-dl

A fast, zero-dependency CLI tool written in Go to download videos from LinkedIn posts.

## Features

- Downloads videos from public LinkedIn posts
- No authentication or API keys required
- Zero external dependencies (Go standard library only)
- Progress bar with percentage and file size
- Safe downloads — uses temp files to prevent corruption on interruption
- Auto-generates filenames from the post URL

## Installation

### From source

```bash
git clone https://github.com/yourusername/linkedin-video-dl.git
cd linkedin-video-dl
go build -o linkedin-video-dl .
```

### Go install

```bash
go install github.com/yourusername/linkedin-video-dl@latest
```

## Usage

```bash
linkedin-video-dl "<linkedin-post-url>"
```

### Example

```bash
linkedin-video-dl "https://www.linkedin.com/posts/midudev_anthropic-ha-acusado-a-deepseek-activity-7432111870431449089-9evi"
```

Output:

```
Obteniendo página del post...
Buscando URLs de video...
Video encontrado: https://dms.licdn.com/playlist/vid/v2/...
Descargando a: midudev_anthropic-ha-acusado-a-deepseek-activity-743.mp4
  [████████████████████████████████████████] 100.0% (519.6 KB / 519.6 KB)

Descarga completada: midudev_anthropic-ha-acusado-a-deepseek-activity-743.mp4
```

## How it works

1. Fetches the LinkedIn post HTML with browser-like headers
2. Extracts video URLs from LinkedIn's CDN (`dms.licdn.com`) using multiple patterns:
   - Direct MP4 URLs in HTML
   - URL-encoded and unicode-escaped URLs
   - `contentUrl` fields in JSON-LD structured data
   - `src` attributes in embedded JSON
3. Selects the best quality available
4. Downloads the MP4 file with a real-time progress bar

## Supported URL formats

```
https://www.linkedin.com/posts/{username}_{slug}-activity-{id}-{hash}
https://www.linkedin.com/posts/{username}_{slug}-activity-{id}-{hash}?utm_source=...
```

## Limitations

- Only works with **public** posts — private or restricted posts require authentication
- LinkedIn may rate-limit or block requests if used excessively
- Only downloads video content (not images or documents)
- Extracts videos embedded directly in posts (not external links like YouTube)

## License

MIT
