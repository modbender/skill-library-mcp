---
name: tor-browser
description: Headless browser automation with Tor SOCKS5 proxy support for accessing .onion sites and anonymous browsing. Use when navigating dark web resources, scraping Tor hidden services, conducting security research on dark web forums, or when anonymity is required. Supports navigation, element interaction, screenshots, and data extraction through Tor network.
metadata:
  openclaw:
    emoji: onion
    category: browser-automation
    version: 1.1.0
    author: OpenClaw
    requirements:
      - python >= 3.8
      - playwright
      - tor service running on socks5://127.0.0.1:9050
    allowed-tools: ["Bash"]
---

# Tor Browser Automation

Headless browser automation with Tor SOCKS5 proxy support for accessing `.onion` sites and anonymous web browsing.

## Prerequisites

- Tor service running with SOCKS5 proxy on port 9050
- Python 3.8+
- Playwright with Chromium browser

Quick setup:
```bash
# Install Tor
sudo apt install tor && sudo systemctl start tor

# Install Python dependencies
pip install playwright
playwright install chromium
```

## Quick Start

```bash
# Check Tor connection
tor-browser check-tor

# Navigate to a .onion site
tor-browser open http://3g2upl4pq6kufc4m.onion

# Get page snapshot
tor-browser snapshot -i

# Click an element
tor-browser click @e1

# Take screenshot
tor-browser screenshot -o output.png --full
```

## Commands

### Navigation

```bash
# Open URL via Tor
tor-browser open <url> [--proxy socks5://host:port]

# Check Tor connection status
tor-browser check-tor
```

### Page Analysis

```bash
# Get full page snapshot
tor-browser snapshot

# Get interactive elements only (forms, buttons, links)
tor-browser snapshot -i

# Extract all links
tor-browser links

# Get page text
tor-browser gettext
tor-browser gettext --ref @e5
```

### Interaction

```bash
# Click element by ref
tor-browser click @e1

# Fill input field
tor-browser fill @e2 "text to enter"

# Wait for page load
tor-browser wait 2000
```

### Screenshots

```bash
# Take viewport screenshot
tor-browser screenshot

# Save to file
tor-browser screenshot -o capture.png

# Full page screenshot
tor-browser screenshot --full -o page.png
```

## Python API

```python
from scripts.tor_browser import TorBrowser, Config
import asyncio

async def main():
    # Configure browser
    config = Config(
        tor_proxy="socks5://127.0.0.1:9050",
        headless=True,
        timeout=30000
    )
    
    # Initialize and start
    browser = TorBrowser(config)
    await browser.start()
    
    # Navigate
    result = await browser.navigate("http://3g2upl4pq6kufc4m.onion")
    print(f"Loaded: {result['title']}")
    
    # Get snapshot
    snapshot = await browser.get_snapshot(interactive_only=True)
    for elem in snapshot['elements']:
        print(f"{elem['ref']}: {elem['tag']} - {elem['text'][:30]}")
    
    # Interact
    await browser.fill("@e2", "search query")
    await browser.click("@e3")
    
    # Extract data
    links = await browser.extract_links()
    for link in links:
        print(f"{link['text']}: {link['href']}")
    
    # Cleanup
    await browser.close()

asyncio.run(main())
```

## Configuration Options

| Option | Default | Description |
|--------|---------|-------------|
| `tor_proxy` | `socks5://127.0.0.1:9050` | Tor SOCKS5 proxy URL |
| `headless` | `true` | Run without GUI |
| `timeout` | `30000` | Page load timeout (ms) |
| `user_agent` | Tor Browser UA | Browser user agent |
| `viewport` | `1920x1080` | Browser viewport size |

## Security & Legal

**Intended Use:**
- Security research and threat intelligence
- Anonymous web scraping of public dark web resources
- Testing .onion site accessibility
- Privacy-preserving web automation

**Important:**
- Only use for legal purposes
- Respect site Terms of Service
- Do not use for unauthorized access
- Comply with local laws regarding dark web access
- Be aware that some activities may be monitored

## Troubleshooting

### Tor Connection Issues

```bash
# Check Tor is running
sudo systemctl status tor

# Test SOCKS5 proxy
curl --socks5-hostname 127.0.0.1:9050 https://check.torproject.org/api/ip

# View Tor logs
sudo journalctl -u tor -f
```

### Common Errors

**Connection refused:**
- Ensure Tor service is started
- Check firewall rules
- Verify proxy URL

**Timeout:**
- .onion sites may be slow; increase timeout
- Try different Tor circuits: restart Tor service

**CAPTCHA blocking:**
- Use `--headed` mode to manually solve
- Some sites block automation

## Docker Setup

```dockerfile
FROM python:3.11-slim

RUN apt-get update && apt-get install -y tor
RUN pip install playwright && playwright install chromium

COPY . /app
WORKDIR /app

CMD ["tor-browser", "check-tor"]
```

## References

- Setup Guide: [references/setup-guide.md](references/setup-guide.md)
- Playwright Docs: https://playwright.dev/python/
- Tor Project: https://www.torproject.org/

## License

MIT - See original licenses for Playwright and Tor Project components.
