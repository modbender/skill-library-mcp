# Safe-Web

A secure, drop-in replacement for OpenClaw's native `web_fetch` and `web_search` tools with built-in prompt injection protection.

## What It Does

Safe-web wraps all web operations with **PromptGuard** scanning to detect and block prompt injection attacks hidden in web content, emails, PDFs, and documents before they reach the AI.

## Why Use This?

By default, OpenClaw's native `web_fetch` and `web_search` tools fetch content directly without security scanning. Safe-web provides the same functionality but adds a critical security layer that scans all content for:

- Instruction override attempts ("ignore previous instructions")
- Role manipulation attacks ("you are now DAN")
- System impersonation patterns
- Hidden malicious payloads in web pages

## Installation

### 1. Install Dependencies

```bash
# Install PromptGuard first
cd /home/linuxbrew/.openclaw/workspace/skills/prompt-guard
pip3 install --break-system-packages -e .

# Install web dependencies
pip3 install --break-system-packages requests beautifulsoup4
```

### 2. Create Symlink (Optional but Recommended)

```bash
sudo ln -s /home/linuxbrew/.openclaw/workspace/skills/safe-web/scripts/safe-web.py /usr/local/bin/safe-web
```

### 3. Configure Brave API Key (for search)

Get a free API key at https://brave.com/search/api/ and set it:

```bash
export BRAVE_API_KEY="your-key-here"
```

## Usage

Safe-web is designed as a drop-in replacement. Use it anywhere you would use the native tools:

```bash
# Instead of web_fetch
safe-web fetch https://example.com/article

# Instead of web_search  
safe-web search "AI safety research"
```

See [SKILL.md](SKILL.md) for full documentation and examples.

## Disabling Native Tools (Recommended)

Once safe-web and promptguard are installed and working, you should disable the native `web_fetch` and `web_search` tools in your OpenClaw configuration. This ensures the model **always** uses local prompt injection detection when browsing.

To disable native tools, add this to your OpenClaw config:

```json
{
  "tools": {
    "disable": ["web_fetch", "web_search"]
  }
}
```

Or set via environment:

```bash
export OPENCLAW_DISABLE_TOOLS="web_fetch,web_search"
```

**Why disable them?** If both native and safe-web tools are available, the model may choose the native tools for convenience, bypassing security scanning. Disabling native tools forces secure-by-default behavior.

## Security Model

- **Fail-closed:** If scanning fails, content is blocked, not passed through
- **No execution:** Only fetches and scans; never executes JavaScript or commands
- **Local scanning:** All detection happens locally; no data sent to third parties

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success - content is clean |
| 1 | Error (network, parsing, etc.) |
| 2 | Threat detected - content blocked |

## Requirements

- Python 3.8+
- [PromptGuard](https://clawhub.ai/seojoonkim/prompt-guard)
- `requests` and `beautifulsoup4` packages
- Brave Search API key (for search functionality)

## License

MIT - See LICENSE file for details.
