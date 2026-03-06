# Setup - Notion API Integration

## First-Time Setup

### 1. Create Integration

1. Go to https://www.notion.so/my-integrations
2. Click "New integration"
3. Name it (e.g., "My Agent")
4. Select workspace
5. Copy the "Internal Integration Token"

### 2. Set Environment Variable

```bash
export NOTION_API_KEY="ntn_xxxxxxxxxxxx"
# Or for older tokens:
export NOTION_API_KEY="secret_xxxxxxxxxxxx"
```

### 3. Share Pages with Integration

Integration can only access pages explicitly shared with it:

1. Open the page/database in Notion
2. Click "..." menu (top right)
3. Click "Add connections"
4. Select your integration

### 4. Test Connection

```bash
curl 'https://api.notion.com/v1/users/me' \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2022-06-28"
```

Expected: `{"object":"user","id":"...","type":"bot"}`

## Memory Setup

Create workspace context:

```bash
mkdir -p ~/notion-api-integration
```

Then initialize memory by asking the agent about your Notion workspace.

## Integration Permissions

Configure in integration settings:

| Permission | Use Case |
|------------|----------|
| Read content | Query databases, read pages |
| Update content | Edit pages, update properties |
| Insert content | Create pages, add blocks |
| Read comments | Fetch page comments |
| Create comments | Add comments to pages |

## Troubleshooting

### 404 Not Found
- Page not shared with integration
- Page ID has dashes (remove them)
- Page was deleted

### 401 Unauthorized
- Invalid or expired token
- Wrong token format

### 400 Bad Request
- Missing Notion-Version header
- Invalid JSON in request body
- Wrong property type format
