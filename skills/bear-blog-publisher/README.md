# Bear Blog Publisher

Publish blog posts to Bear Blog - supports user-provided markdown, AI-generated content, and auto-generated diagrams.

## Features

- **Triple Auth Methods**: Config file, environment variables, or runtime parameters
- **AI Content Generation**: Optional auto-generation using OpenAI or Kimi
- **Auto Diagrams**: Generates architecture diagrams for technical posts

## Installation

```bash
clawhub install bear-blog-publisher
```

## Authentication (Choose One)

### Method 1: OpenClaw Config File

Edit `~/.openclaw/openclaw.json`:

```json
{
  "skills": {
    "bear-blog-publisher": {
      "email": "your@email.com",
      "password": "yourpassword"
    }
  }
}
```

Set secure permissions:
```bash
chmod 600 ~/.openclaw/openclaw.json
```

### Method 2: Environment Variables

```bash
export BEAR_BLOG_EMAIL="your@email.com"
export BEAR_BLOG_PASSWORD="yourpassword"
```

### Method 3: Runtime Parameters

```python
from bear_blog_publisher import BearBlogPublisher

publisher = BearBlogPublisher(
    email="your@email.com",
    password="yourpassword"
)
```

## AI Content Generation (Optional)

To use AI content generation, configure one of the following API keys:

### OpenAI
```bash
export OPENAI_API_KEY="sk-..."
```

### Kimi
```bash
export KIMI_API_KEY="your-kimi-api-key"
```

### Usage
```python
publisher = BearBlogPublisher()
content = publisher.generate_content(
    topic="Python best practices",
    provider="openai",  # or "kimi"
    tone="professional",
    length="medium"
)
result = publisher.publish(title="My Post", content=content)
```

## Usage Examples

### AI-Generated Content
```
You: "Write and publish a blog about remote work tips"
AI: [Generates content with OpenAI/Kimi, publishes]
     ✅ Published: https://bearblog.dev/yourname/remote-work-tips/
```

### User-Provided Content
```
You: "Publish this as a blog: [paste your markdown]"
AI: [Publishes your exact content]
     ✅ Published: https://bearblog.dev/yourname/your-post/
```

## Security Notes

- **No persistent credential storage** - credentials only exist in memory during execution
- **Session-only authentication** - no tokens stored between runs
- **Config file permission check** - warns if readable by others
- **Priority**: Runtime > Environment > Config

### Operational Considerations

1. **Playwright Browser** (~100MB download) - Required for diagram generation
2. **Temporary Files** - Created in `/tmp/` for diagram processing
3. **`--no-sandbox`** - Used for container compatibility
4. **Plaintext Config** - Optional; use env vars for better security

## Requirements

- Bear Blog account
- Python 3.8+
- Playwright (auto-installed, ~100MB browser download)
- OpenAI or Kimi API key (optional, for AI content generation)

## License

MIT
