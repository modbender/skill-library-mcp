# MiniMax MCP Usage Examples

## web_search - Web Search

### Basic Search

```bash
mcporter call minimax.web_search query="what is artificial intelligence"
```

**Return Structure:**
```json
{
  "organic": [
    {
      "title": "Result Title",
      "link": "https://example.com",
      "snippet": "Result snippet...",
      "date": "2026-01-01"
    }
  ],
  "related_searches": [
    { "query": "related search query" }
  ],
  "base_resp": {
    "status_code": 0,
    "status_msg": "success"
  }
}
```

### Search Tips

| Scenario | Query Style | Example |
|----------|-------------|---------|
| News | Add year | "AI 2026" |
| Tech Docs | Add tech term | "Python tutorial" |
| Products | Add product name | "iPhone review" |

---

## understand_image - Image Understanding

### Analyze Image from URL

```bash
mcporter call minimax.understand_image \
  prompt="Describe what's in this image" \
  image_source="https://example.com/image.jpg"
```

### Analyze Local Image

```bash
mcporter call minimax.understand_image \
  prompt="What's in this image?" \
  image_source="/path/to/local/image.png"
```

### Advanced Usage

| Task | Prompt Example |
|------|----------------|
| Describe scene | "Describe this scene in detail" |
| Extract text | "What text is in this image? Please extract it." |
| Identify type | "What type of image is this? Photo/screenshot/poster?" |
| Analyze chart | "Describe the data and trends in this chart" |

---

## Common Error Handling

### Image Download Failed

**Error:** `Failed to download image from URL: 400 Bad Request`

**Solutions:**
- Ensure URL is publicly accessible
- Check image format (JPEG/PNG/WebP)
- Try downloading locally first, then use local path

### Invalid API Key

**Error:** `API Error: invalid api key`

**Solutions:**
- Confirm API Key and Host are from the same region
- China users: use `https://api.minimaxi.com`
- Global users: use `https://api.minimax.io`

### uvx Not Found

**Error:** `spawn uvx ENOENT`

**Solutions:**
```bash
# Find uvx path
which uvx

# If not found, install uv first
brew install uv
# or
curl -LsSf https://astral.sh/uv/install.sh | sh
```

---

## Integration: Claude Desktop / Cursor

Edit `~/

### Claude DesktopLibrary/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "MiniMax": {
      "command": "uvx",
      "args": ["minimax-coding-plan-mcp", "-y"],
      "env": {
        "MINIMAX_API_KEY": "your-api-key",
        "MINIMAX_API_HOST": "https://api.minimaxi.com"
      }
    }
  }
}
```

### Cursor

Preferences → Cursor Settings → MCP → Add new global MCP Server

---

## Cost Notice

⚠️ Using these tools will incur API call fees. Please monitor your MiniMax account usage.
