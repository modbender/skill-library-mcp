# Notion API Setup Guide

## Getting Your API Key

### Step 1: Create a Notion Integration

1. Go to [Notion Integrations](https://www.notion.so/my-integrations)
2. Click "Create new integration"
3. Enter a name (e.g., "Markdown Converter")
4. Select the workspace you want to use
5. Click "Submit"

### Step 2: Copy Your API Token

1. On the integration details page, find the "Secrets" section
2. Click "Show" next to the "Internal Integration Secret"
3. Copy the token (it starts with `notioneq_...`)
4. **Keep this token secret** - treat it like a password

### Step 3: Share Pages with Your Integration

Notion pages must be explicitly shared with your integration for it to access them:

1. Open the Notion page you want to convert
2. Click "Share" in the top right
3. Search for your integration name (e.g., "Markdown Converter")
4. Click to add it
5. Grant "Editor" or "Reader" access

For databases, share the database parent page with your integration.

### Step 4: Set the Environment Variable

Add your API key to your shell configuration:

```bash
export NOTION_API_KEY="notioneq_your_token_here"
```

Add to `~/.bashrc`, `~/.zshrc`, or equivalent.

## Finding Page IDs

### From URL

The page ID is in the URL:
```
https://www.notion.so/MyWorkspace/Page-Title-abc123def456?v=123abc
                                           ↑ Page ID (remove hyphens)
```

Copy `abc123def456` (the ID without hyphens).

### From Database

For database exports, use the database ID from its URL:
```
https://www.notion.so/MyWorkspace/Database-Name-abc123def456
                                         ↑ Database ID
```

## Permissions & Access Control

### What Your Integration Can Access

- ✅ Pages and databases explicitly shared with it
- ✅ All blocks and properties within shared pages
- ✅ Images and embeds (downloaded as URLs)
- ❌ Pages or databases NOT shared with the integration

### Required Permissions

Your integration needs:
- **Read** permission for basic conversion
- **Write** permission if you need to add comments or update content

## API Rate Limits

Notion API has rate limits:
- 3 requests per second (burst)
- Generous daily limits for most use cases

For large bulk exports, add small delays between requests:

```bash
# Small delay between conversions
sleep 0.5
```

## Troubleshooting

### "Invalid Notion API key"

- Check the token was copied completely
- Verify it starts with `notioneq_`
- Ensure the environment variable is set: `echo $NOTION_API_KEY`

### "Page not found"

- The page ID might be incorrect
- The integration hasn't been shared with the page
- Check the page is accessible in your Notion workspace

### "Validation error: Invalid page ID"

- Remove hyphens from the page ID
- Use only alphanumeric characters (no `-` in the ID)

## Security Best Practices

1. **Never commit API keys** to version control
2. **Use environment variables** instead
3. **Rotate tokens** if you suspect compromise
4. **Share pages minimally** - only with the integration
5. **Use read-only access** when you don't need write permission

## API Documentation

Full Notion API documentation: https://developers.notion.com/reference
