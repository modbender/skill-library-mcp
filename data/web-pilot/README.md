# 🌐 Web Pilot — OpenClaw Skill

[![Ko-fi](https://img.shields.io/badge/Ko--fi-Support%20this%20project-FF5E5B?logo=ko-fi&logoColor=white)](https://ko-fi.com/liranudi)

A web search, page reading, and browser automation skill for [OpenClaw](https://github.com/openclaw/openclaw). No API keys required.

## ♿ Accessibility

This skill enables AI agents to **read, navigate, and interact with the web on behalf of users** — making it a powerful accessibility tool for people with visual impairments, motor disabilities, or cognitive challenges.

- **Screen reading on steroids** — extracts clean, structured text from any webpage, stripping away visual clutter, ads, and navigation noise
- **Voice-driven browsing** — when paired with an AI assistant, users can browse the web entirely through natural language ("scroll down", "click Sign In", "read me the Overview section")
- **Targeted content extraction** — grab specific sections, search for text, or screenshot regions without needing to visually scan a page
- **Form interaction** — fill inputs and submit forms via commands, removing the need for precise mouse/keyboard control
- **Cookie banner removal** — automatically dismisses consent popups that are notoriously difficult for screen readers

## Features

- **Web Search** — Multi-engine (DuckDuckGo, Brave, Google) with pagination
- **Page Reader** — Extract clean text from any URL with JS rendering
- **Persistent Browser** — Visible or headless browser with 20+ actions
- **Cookie Auto-Dismiss** — Automatically clears cookie consent banners
- **File Download** — Download files with auto-detection, PDF text extraction
- **Output Formats** — JSON, markdown, or plain text
- **Zero API Keys** — Everything runs locally
- **Partial Screenshots** — Capture viewport, full page, single elements, or ranges between two elements

## Requirements

- Python 3.8+
- `pip install requests beautifulsoup4 playwright Pillow`
- `playwright install chromium`
- Optional: `pip install pdfplumber` for PDF text extraction

## Installation

### As an OpenClaw Skill

```bash
cp -r web-pilot/ $(dirname $(which openclaw))/../lib/node_modules/openclaw/skills/web-pilot
```

### Standalone

```bash
git clone https://github.com/LiranUdi/web-pilot.git
cd web-pilot
pip install requests beautifulsoup4 playwright Pillow
playwright install chromium
```

## Usage

### 1. Search the Web

```bash
python3 scripts/google_search.py "search term" --pages 3 --engine brave
```

| Flag | Description | Default |
|------|-------------|---------|
| `--pages N` | Result pages (~10 results each) | 1 |
| `--engine` | `duckduckgo`, `brave`, or `google` | duckduckgo |

**Engine notes:**
- **duckduckgo** — Most reliable, no CAPTCHA
- **brave** — More results per page, broader sources
- **google** — Often blocked by CAPTCHA; last resort

### 2. Read a Page

```bash
python3 scripts/read_page.py "https://example.com" --max-chars 10000 --format markdown
```

| Flag | Description | Default |
|------|-------------|---------|
| `--max-chars N` | Max characters to extract | 50000 |
| `--visible` | Show browser window | off |
| `--format` | `json`, `markdown`, or `text` | json |
| `--no-dismiss` | Skip cookie consent auto-dismiss | off |

### 3. Persistent Browser Session

The browser session is a long-running process that stays open between commands, enabling stateful multi-step browsing.

```bash
# Open a page (flags: --headless, --proxy <url>, --user-agent <string>)
python3 scripts/browser_session.py open "https://example.com"
python3 scripts/browser_session.py open "https://example.com" --headless --user-agent "MyBot/1.0"

# Check current state
python3 scripts/browser_session.py status

# Navigate (returns response status, final URL, load time)
python3 scripts/browser_session.py navigate "https://other-site.com"

# Extract content in different formats
python3 scripts/browser_session.py extract --format markdown

# Scroll
python3 scripts/browser_session.py scroll down
python3 scripts/browser_session.py scroll up
python3 scripts/browser_session.py scroll "#section-id"   # scroll to element

# Wait
python3 scripts/browser_session.py wait 2                  # wait 2 seconds
python3 scripts/browser_session.py wait ".loading-done"    # wait for element

# Fill forms
python3 scripts/browser_session.py fill "input[name=q]" "search term"
python3 scripts/browser_session.py fill "input[name=q]" "search term" --submit

# Navigation history
python3 scripts/browser_session.py back
python3 scripts/browser_session.py forward
python3 scripts/browser_session.py reload

# Execute JavaScript
python3 scripts/browser_session.py eval "document.title"

# Extract all links
python3 scripts/browser_session.py links

# Screenshots
python3 scripts/browser_session.py screenshot /tmp/page.png              # viewport
python3 scripts/browser_session.py screenshot /tmp/full.png --full       # full page
python3 scripts/browser_session.py screenshot /tmp/el.png --element "h1" # single element
python3 scripts/browser_session.py screenshot /tmp/range.png --from "#Overview" --to "#end"  # range

# Export page as PDF (headless only)
python3 scripts/browser_session.py pdf /tmp/page.pdf

# Click elements
python3 scripts/browser_session.py click "Sign In"
python3 scripts/browser_session.py click "#submit-btn"

# Search for text in the page
python3 scripts/browser_session.py search "pricing"

# Tab management
python3 scripts/browser_session.py tab new "https://docs.example.com"
python3 scripts/browser_session.py tab list
python3 scripts/browser_session.py tab switch 0
python3 scripts/browser_session.py tab close 1

# Dismiss cookie banners
python3 scripts/browser_session.py dismiss-cookies

# Close
python3 scripts/browser_session.py close
```

### 4. Download Files

```bash
python3 scripts/download_file.py "https://example.com/report.pdf" --output ~/docs
```

| Flag | Description | Default |
|------|-------------|---------|
| `--output DIR` | Save directory | /tmp/downloads |
| `--filename` | Override filename | auto-detected |

For PDFs, returns `extracted_text` if `pdfplumber` or `PyPDF2` is installed.

## Architecture

- **Search** — HTTP requests to DuckDuckGo/Brave/Google HTML endpoints
- **Page reading** — Playwright + Chromium with read-only DOM TreeWalker
- **Browser sessions** — Unix socket server with 4-byte length-prefix framing; forked child keeps browser alive, commands return immediately
- **Screenshots** — Range mode uses full-page capture + PIL crop for pixel-perfect section captures
- **Cookie dismiss** — Tries common selectors and button text patterns (Accept All, Got It, etc.)
- **Downloads** — Streams to disk with auto filename detection from headers/URL

## Browser Session Reference

| Action | Description |
|--------|-------------|
| `open <url>` | Launch browser (flags: `--headless`, `--proxy`, `--user-agent`) |
| `navigate <url>` | Go to URL (returns status code, final URL, load time) |
| `extract` | Extract page content (`--format json\|markdown\|text`) |
| `screenshot <path>` | Capture (`--full`, `--element <sel>`, `--from <sel> --to <sel>`) |
| `click <target>` | Click by CSS selector, text, or button/link role |
| `scroll <dir\|sel>` | Scroll down/up or to a CSS selector |
| `wait <sec\|sel>` | Wait seconds or for element to appear |
| `fill <sel> <val>` | Fill input field (optional `--submit`) |
| `back` / `forward` / `reload` | Navigation history |
| `eval <js>` | Execute JavaScript, return result |
| `links` | Extract all links (href + text) |
| `search <text>` | Find text in page content |
| `pdf <path>` | Export as PDF (headless only) |
| `status` | Current URL, title, tab count |
| `tab new\|list\|switch\|close` | Multi-tab management |
| `dismiss-cookies` | Clear cookie consent banners |
| `close` | Shut down browser |

---

## For AI Agents (OpenClaw / LLM Integration)

### Workflow Pattern

1. **Search** → get URLs
2. **Read** or **Open** → extract content
3. **Scroll/Click/Navigate/Tab** → interact as needed
4. **Search** → find specific info in page
5. **Screenshot** → capture visual state (viewport, element, or range)
6. **Download** → grab linked files
7. **Close** → clean up

### Important Notes

- All output defaults to **JSON to stdout**; use `--format` for alternatives
- `browser_session.py` is **stateful** — one session at a time, persists between commands
- `read_page.py` is **stateless** — opens/closes browser each call
- Cookie consent is **auto-dismissed** on open/navigate
- Always **close** browser sessions when done
- `Pillow` is required for range screenshots (`--from`/`--to`)

## Support

If this project is useful to you, consider [buying me a coffee](https://ko-fi.com/liranudi) ☕

## License

MIT
