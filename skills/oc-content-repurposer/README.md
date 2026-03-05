# Content Repurposer

Turn any blog post or article into multi-platform social media content in seconds.

## Features

- **5 Platform Formats** — Twitter/X thread, LinkedIn, Instagram, Email, Summary
- **URL Extraction** — Paste a URL, get content automatically extracted
- **Character Limits** — Enforced per platform (280 for tweets, 2200 for Instagram, etc.)
- **Thread Builder** — Smart tweet splitting with hooks and hashtags
- **Batch Output** — Save all formats to separate files at once
- **JSON Output** — Perfect for automation pipelines
- **Minimal Dependencies** — Only beautifulsoup4 for URL mode

## Installation

### As an OpenClaw/ClawHub skill

```bash
clawhub install content-repurposer
```

### Standalone

```bash
git clone https://github.com/YOUR_USERNAME/content-repurposer.git
cd content-repurposer
pip install beautifulsoup4  # Only needed for URL extraction
```

## Usage

```bash
# From URL
python scripts/repurpose.py url "https://example.com/blog-post"

# From file
python scripts/repurpose.py file my-article.md

# From stdin
cat article.txt | python scripts/repurpose.py stdin
```

## Use Cases

- **Content creators** — Repurpose weekly blog posts across all social platforms
- **Marketing teams** — Consistent multi-channel messaging from one source
- **Agencies** — Quick content turnaround for clients
- **Solo entrepreneurs** — Maximize reach without writing 5 separate posts

## License

MIT

## Author

Built by OpenClaw Setup Services — Professional AI agent configuration and custom skill development.

**Need automated content pipelines?** Contact us for custom content automation setups.
