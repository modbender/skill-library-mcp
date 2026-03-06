# Output Platform Reference

This document lists supported output platforms, required tools, and configuration methods.

---

## Platform Classification

### Type 1: Chat Response

**Use Case**: Quick replies, temporary content

**Required Tools**: No additional tools

**Usage**:
```
Reply directly
```

**Pros**: Immediate, simple  
**Cons**: Hard to maintain, difficult to collaborate

---

### Type 2: Feishu Document

**Use Case**: Team collaboration, enterprise knowledge management

**Required Tools**:
- MCP feishu (recommended)
- Or built-in feishu.doc tools

**Configuration**:

1. **MCP Configuration** (`/root/config/mcporter.json`):
```json
{
  "mcpServers": {
    "feishu": {
      "command": "npx",
      "args": ["-y", "mcp-server-feishu"],
      "env": {
        "FEISHU_APP_ID": "your_app_id",
        "FEISHU_APP_SECRET": "your_app_secret"
      }
    }
  }
}
```

2. **Permission Configuration**:
   - Document read/write permissions
   - Wiki permissions (if using wiki)

**Usage**:
```bash
# Create document
mcporter call feishu.doc.create --title "Document Title" --content "Content"

# Update document
mcporter call feishu.doc.update --doc_id "xxx" --content "Content"
```

**API Reference**:
- `feishu.doc.create` - Create document
- `feishu.doc.update` - Update document
- `feishu.wiki.create` - Create wiki page

---

### Type 3: Local Markdown File

**Use Case**: Local document management, version control

**Required Tools**:
- `write` tool (built-in)

**Usage**:
```python
# Save to workspace
write --path /root/.openclaw/workspace/docs/filename.md --content "Content"
```

**Default Path**:
```
/root/.openclaw/workspace/docs/
├── tutorials/
├── how-to-guides/
├── reference/
└── explanation/
```

**Pros**: 
- No additional configuration needed
- Supports version control
- Easy to backup

---

### Type 4: GitHub Repo

**Use Case**: Tech blog, open source documentation

**Required Tools**:
- MCP github (recommended)
- Or built-in git + exec tools

**Configuration**:

1. **MCP Configuration**:
```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "mcp-server-github"],
      "env": {
        "GITHUB_TOKEN": "your_token"
      }
    }
  }
}
```

2. **Or use git commands**:
```bash
# Configure git
git config --global user.name "Your Name"
git config --global user.email "your@email.com"
```

**Usage**:
```bash
# Method 1: MCP github
mcporter call github.repos.createFile --repo "owner/repo" --path "docs/file.md" --content "Content"

# Method 2: git commands
cd /root/.openclaw/workspace
git add docs/file.md
git commit -m "Add new document"
git push
```

---

### Type 5: Notion

**Use Case**: Personal knowledge base, structured notes

**Required Tools**:
- MCP notion

**Configuration**:
```json
{
  "mcpServers": {
    "notion": {
      "command": "npx",
      "args": ["-y", "mcp-server-notion"],
      "env": {
        "NOTION_TOKEN": "your_token"
      }
    }
  }
}
```

**Usage**:
```bash
mcporter call notion.pages.create --parent "database_id" --title "Title" --content "Content"
```

---

### Type 6: Google Docs

**Use Case**: Google Workspace users

**Required Tools**:
- MCP google-docs

**Configuration**:
```json
{
  "mcpServers": {
    "google-docs": {
      "command": "npx",
      "args": ["-y", "mcp-server-google"],
      "env": {
        "GOOGLE_APPLICATION_CREDENTIALS": "/path/to/credentials.json"
      }
    }
  }
}
```

---

### Type 7: Other Platforms

**User-Provided Platforms**:

If users need to output to other platforms, need to provide:

1. **Platform Name**: e.g., "Confluence", "Medium", etc.
2. **Available Tools**: 
   - MCP server name
   - Or API endpoint and authentication method
3. **Output Format**: Markdown, HTML, rich text, etc.

**Configuration Template**:
```json
{
  "platform": "Platform Name",
  "tool": "MCP server or tool name",
  "config": {
    "endpoint": "API endpoint",
    "auth": "Authentication method",
    "format": "Output format"
  }
}
```

---

## Tool Detection Methods

### Auto-Detection Script

Use `scripts/output-handler.py` to automatically detect available tools:

```python
# Detect MCP servers
def check_mcp_servers():
    # Read mcporter.json
    # Return available server list
    pass

# Detect built-in tools
def check_builtin_tools():
    # Check write, exec, etc. tools
    pass

# Generate recommendations
def generate_recommendations():
    # Recommend best output method based on available tools
    pass
```

### Detection Result Example

```
Detected available tools:

✅ Feishu Document
   Tool: MCP feishu
   Status: Configured
   Capabilities: Create, edit, share

✅ Local Files
   Tool: write
   Status: Built-in
   Capabilities: Create, update

⚠️  GitHub
   Tool: MCP github
   Status: Not configured
   Requires: GITHUB_TOKEN

❌ Notion
   Tool: MCP notion
   Status: Not installed

Recommended: Feishu Document (configured and suitable for collaborative documents)
```

---

## Selection Guide

### Choose by Scenario

| Scenario | Recommended Platform | Reason |
|----------|---------------------|--------|
| Quick reply | Chat | Immediate, no configuration |
| Team collaborative document | Feishu | Enterprise integration, permission management |
| Personal knowledge management | Local MD | Simple, easy version control |
| Tech blog | GitHub | Version control, public sharing |
| Structured notes | Notion | Database, strong connectivity |
| Google ecosystem | Google Docs | Integration with Workspace |

### Choose by Tool Availability

**Priority**:
1. Configured tools
2. Built-in tools
3. Tools requiring simple configuration
4. Tools requiring complex configuration

---

## Configuration Checklist

Check before output:

- [ ] Target platform confirmed
- [ ] Required tools installed
- [ ] Authentication information configured
- [ ] Permissions granted
- [ ] Output format correct
- [ ] Backup plan prepared

---

**Version**: 1.0  
**Last Updated**: 2026-02-25  
**Maintenance**: Update this document when adding new tools
