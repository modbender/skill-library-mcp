# Cubox Integration Skill

A skill for integrating with [Cubox](https://cubox.pro) - a powerful read-it-later and bookmarking service.

## Features

- 📎 **Save URLs** - Bookmark web pages with metadata (title, description, tags, folder)
- 📝 **Save Memos** - Quick notes and text snippets
- 🏷️ **Tagging Support** - Organize content with tags
- 📁 **Folder Management** - Save to specific folders

## Quick Start

### 1. Get Your API URL

1. Open Cubox (web or app)
2. Go to **Preferences** > **Extension Center and Automation** > **API Extension**
3. Enable **API Link** and copy the URL

### 2. Set Environment Variable

```bash
export CUBOX_API_URL="https://cubox.pro/c/api/save/YOUR_TOKEN"
```

### 3. Install Dependencies

```bash
pip install requests
```

### 4. Usage

**Save a URL:**
```bash
python scripts/save_url.py "https://example.com" --title "Example Site" --tags "web,example"
```

**Save a memo:**
```bash
python scripts/save_memo.py "Important note to remember" --folder "Notes"
```

## API Reference

### Request Format

All requests use JSON format:

```json
{
  "type": "url",
  "content": "https://example.com",
  "title": "Optional Title",
  "description": "Optional Description",
  "tags": ["tag1", "tag2"],
  "folder": "Folder Name"
}
```

### Types

| Type | Description |
|------|-------------|
| `url` | Save a web page URL |
| `memo` | Save a quick memo/note |

### Rate Limits

- **500 API calls per day** (Premium users)

## Documentation

- [SKILL.md](./SKILL.md) - Detailed skill instructions
- [Cubox API Help](https://help.cubox.pro/save/89d3/) - Official documentation

## License

MIT
