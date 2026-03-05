# Scrapling Web Scraping Skill

Advanced web scraping for OpenClaw with anti-bot bypass and adaptive selectors.

## Features

✅ **Anti-Bot Bypass** - Automatically handles Cloudflare Turnstile, bot detection  
✅ **JavaScript Support** - Scrape React, Vue, Angular apps with full browser automation  
✅ **Adaptive Selectors** - Elements auto-relocate when websites redesign  
✅ **Session Management** - Persistent cookies, login state across requests  
✅ **Multiple Modes** - HTTP (fast), Stealth (anti-bot), Dynamic (full browser)  
✅ **Flexible Output** - JSON, JSONL, CSV, Markdown, plain text  

## Quick Start

### Install Skill

Via OpenClaw Gateway UI:
1. Navigate to Skills section
2. Click "Install Skill"
3. Select or upload `scrapling` skill
4. Wait for dependencies to install (~2-5 minutes for browsers)

Via CLI:
```bash
# Install dependencies
cd ~/.openclaw/skills/scrapling
pip install -r requirements.txt
scrapling install  # Downloads browsers (~500MB)
```

### Basic Usage

```bash
# Scrape a static site
python scrape.py --url "https://example.com" --selector ".product" --output products.json

# Bypass anti-bot protection
python scrape.py --url "https://protected-site.com" --stealth --selector ".content"

# Scrape JavaScript-rendered content
python scrape.py --url "https://spa-app.com" --dynamic --selector ".item"

# Adaptive mode (survives website changes)
python scrape.py --url "https://site.com" --selector ".product" --adaptive-save
# Later, even if site redesigns:
python scrape.py --url "https://site.com" --adaptive
```

## Examples

Check the `examples/` directory for:
- `basic.py` - Simple HTTP scraping
- `stealth.py` - Cloudflare bypass example
- `dynamic.py` - JavaScript-heavy sites
- `adaptive.py` - Adaptive selector demo

## Documentation

Full documentation in `SKILL.md` including:
- All command-line options
- Selector types (CSS, XPath)
- Output formats
- Session management
- Troubleshooting guide

## Requirements

- Python 3.10+
- ~500MB disk space for browsers (Chromium)
- Internet connection for first-run browser download

## Support

- Scrapling Docs: https://scrapling.readthedocs.io
- GitHub: https://github.com/D4Vinci/Scrapling
- Discord: https://discord.gg/EMgGbDceNQ

## License

BSD-3-Clause (same as Scrapling library)
