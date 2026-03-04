# rednote-mac

**Control the RedNote (Xiaohongshu) Mac desktop app via macOS Accessibility API.**

Fills the gap that headless browser tools leave behind — DMs, comment replies, video comment reading, and more. Drives the native App directly, no browser, no API tokens, no reverse engineering.

---

## Why rednote-mac?

| Feature | rednote-mac | headless (xiaohongshu-mcp) |
|---------|:-----------:|:--------------------------:|
| Browse feed & search | ✅ | ✅ |
| Like, collect, follow | ✅ | ✅ |
| Post comments | ✅ | ✅ |
| **Reply to comments** | ✅ | ❌ |
| **Direct messages** | ✅ | ❌ |
| **Video comment list** | ✅ | ❌ |
| **Author profile stats** | ✅ | ❌ |
| Headless / no screen needed | ❌ | ✅ |

---

## Requirements

- **macOS** with [RedNote](https://www.rednote.app) installed
- **Terminal → Accessibility permission** — System Settings → Privacy & Security → Accessibility → enable Terminal
- **RedNote App visible on screen** — not minimized, screen not locked
- **Python** + [uv](https://github.com/astral-sh/uv) (recommended) or pip
- **cliclick** — `brew install cliclick`

> ⚠️ The Accessibility permission grants control over **all apps** on your Mac, not just RedNote. Only enable if you trust this skill. Consider running automation in a dedicated user account.

---

## Install

### As an OpenClaw Plugin (recommended)

```bash
# 1. Install via clawhub
clawhub install rednote-mac

# 2. Run the setup script
cd ~/.agents/skills/rednote-mac && bash install.sh

# 3. Activate
openclaw config set tools.allow '["rednote-mac"]'
openclaw gateway restart

# 4. Verify
openclaw plugins list | grep rednote-mac
```

### As a Claude Desktop / Cursor MCP server

```json
{
  "mcpServers": {
    "rednote-mac": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/rednote-mac", "python", "server.py"]
    }
  }
}
```

---

## Available Tools (20 total)

### Navigation & Search
| Tool | Parameters | Description |
|------|-----------|-------------|
| `xhs_screenshot` | — | Capture current App screen |
| `xhs_navigate` | `tab`: home \| messages \| profile | Switch bottom tab |
| `xhs_navigate_top` | `tab`: follow \| discover \| video | Switch top tab |
| `xhs_back` | — | Go back one page |
| `xhs_search` | `keyword` | Search and jump to results |

### Feed
| Tool | Parameters | Description |
|------|-----------|-------------|
| `xhs_scroll_feed` | `direction`, `times` | Scroll the feed |
| `xhs_open_note` | `col` (0/1), `row` (0…n) | Open note by grid position |

### Note Interactions
| Tool | Parameters | Description |
|------|-----------|-------------|
| `xhs_like` | — | Like current note |
| `xhs_collect` | — | Collect/save current note |
| `xhs_get_note_url` | — | Get share URL |
| `xhs_follow_author` | — | Follow the note's author |
| `xhs_open_comments` | — | Open comment section |
| `xhs_scroll_comments` | `times` | Scroll comments |
| `xhs_get_comments` | — | Get comments → `[{index, author, cx, cy}]` |
| `xhs_post_comment` | `text` | Post a top-level comment |
| `xhs_reply_to_comment` | `index`, `text` | Reply to a comment |
| `xhs_delete_comment` | `index` | ⚠️ Delete own comment (irreversible) |

### Direct Messages
| Tool | Parameters | Description |
|------|-----------|-------------|
| `xhs_open_dm` | `index` | Open DM by list position (0 = first) |
| `xhs_send_dm` | `text` | Send message in open conversation |

### Profile
| Tool | Parameters | Description |
|------|-----------|-------------|
| `xhs_get_author_stats` | — | Get following / followers / likes / bio |

---

## Known Limitations

**Image/text posts — comment text not readable**
RedNote renders image/text post comments via Metal/Canvas, bypassing macOS Accessibility API. `xhs_get_comments()` works reliably on **video posts** only. Workaround: `xhs_screenshot()` + image analysis.

**App must stay visible**
Minimizing the App or locking the screen will cause all mouse events to fail. Use `caffeinate -di &` for long-running tasks.

**Always navigate home before searching**
Call `xhs_navigate(tab="home")` before `xhs_search()` — the search bar isn't available from note detail pages.

---

## Architecture

```
xhs_controller.py     Core AX control logic (Python + atomacos + pyobjc)
index.ts              OpenClaw Plugin entry — registers 20 tools
server.py             Standard MCP server for Claude Desktop / Cursor
openclaw.plugin.json  Plugin manifest
install.sh            Guided setup script
docs/                 Reference docs (loaded on demand by the agent)
```

**How it works:** Uses `atomacos` (Python bindings for macOS Accessibility API), `cliclick` for mouse events, `CGEventPost` for keyboard and scroll, and `AppleScript` for UI interaction. No browser, no HTTP API — direct App control.

---

## License

MIT
