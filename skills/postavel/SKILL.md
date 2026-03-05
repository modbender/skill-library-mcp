---
name: postavel
description: Connect to Postavel social media management platform via MCP (Model Context Protocol). Create, schedule, and manage social media posts across Facebook, Instagram, and LinkedIn. Use when the user wants to manage social media content, create posts, schedule content, view their content calendar, or interact with their Postavel account through natural language. Activate when user mentions "Postavel", "social media", "schedule post", "create post", "content calendar", or wants to post to Facebook, Instagram, or LinkedIn via their Postavel account.
---

# Postavel

## Overview

Postavel is a multi-platform social media management tool with native MCP (Model Context Protocol) support. This skill enables AI assistants to connect to Postavel and manage social media content through natural language.

**Key Capabilities:**
- Connect to Postavel via MCP with OAuth authentication
- List workspaces, clients, and brands
- Create and schedule posts across Facebook, Instagram, and LinkedIn
- Manage approval workflows
- View content calendars and post statuses

## First Time Setup (2 Steps)

**CRITICAL:** When this skill triggers, FIRST check if MCP connection works. If not:

### Quick Setup

**Step 1:** Install mcporter:
```bash
# macOS with Homebrew:
brew install mcporter

# Or with npm (works everywhere):
npm install -g mcporter
```

**Step 2:** Add Postavel and authenticate:
```bash
# Add Postavel to mcporter
mcporter config add postavel https://postavel.com/mcp/postavel

# Authenticate (browser will open)
mcporter auth postavel
```

**Step 3:** Log in to Postavel in your browser and authorize

**Step 4:** Come back here and say **"done"**

### Alternative: Install Script

```bash
curl -fsSL https://postavel.com/install-mcp | bash
```

### Troubleshooting

**"mcporter: command not found"**
```bash
# Find it:
which mcporter || find ~ /usr/local -name mcporter 2>/dev/null | head -1

# Use full path:
/path/to/mcporter config add postavel https://postavel.com/mcp/postavel
/path/to/mcporter auth postavel
```

**"OAuth timeout"**
- The browser auth worked but mcporter didn't detect it
- Try: `mcporter auth postavel` again
- Or check if it worked: `mcporter list` — if you see "postavel", you're connected

## Quick Start

### Once Setup is Complete

The MCP connection URL for Postavel is:
```
https://postavel.com/mcp/postavel
```

**Authentication Flow:**
1. Install mcporter (one time)
2. Run: `mcporter auth https://postavel.com/mcp/postavel`
3. Log in to Postavel in browser
4. AI assistant can now connect

### Verify Connection

Once setup is complete, test with:
```
"Show me my Postavel workspaces"
```
# Find where mcporter is and run it:
MCPORter=$(which mcporter || find /usr/local /opt ~ -name mcporter 2>/dev/null | head -1)
"$MCPORter" --config ~/.config/mcporter/postavel.json
```

## Quick Start

### Once Setup is Complete

The MCP connection URL for Postavel is:
```
https://postavel.com/mcp/postavel
```

**Authentication Flow:**
1. mcporter installed and configured (via setup above)
2. OAuth token generated and bound to user's Postavel account  
3. AI can only access workspaces/clients/brands the user has permission for
4. All actions are logged in user's activity history

### Verify Connection

Once setup is complete, test with:
```
"Show me my Postavel workspaces"
```

## Core Capabilities

### 1. List Resources

**Workspaces:**
```
"Show me my Postavel workspaces"
"List all workspaces I have access to"
```

**Clients:**
```
"List clients in workspace [workspace-name]"
"What clients does my agency have?"
```

**Brands:**
```
"Show brands for client [client-name]"
"What brands can I manage?"
```

**Connected Platforms:**
```
"Which social accounts are connected for brand [brand-name]?"
"Show me available platforms"
```

### 2. Create Posts

**Basic Post Creation:**
```
"Create a Facebook post for [brand] saying: [content]"
"Draft an Instagram post about [topic]"
```

**Multi-Platform Posts:**
```
"Create a post for Facebook and LinkedIn about [topic]"
"Post to all platforms: [content]"
```

**With Media:**
```
"Create an Instagram post with this image: [URL] and caption: [text]"
"Add this video to a Facebook post: [URL]"
```

**Available Platforms:**
- `facebook` - Facebook pages
- `instagram` - Instagram business accounts
- `linkedin` - LinkedIn organizations (company pages)

### 3. Schedule Posts

**Schedule for Later:**
```
"Schedule a post for tomorrow at 2pm about [topic]"
"Create a post for next Monday at 9am"
"Schedule this for [date] at [time] CET"
```

**With Auto-Approval (Admin/Owner only):**
```
"Schedule a post for [time] and auto-approve it"
"Create and publish a post now"
```

### 4. Approval Workflow

**View Pending Posts:**
```
"Show me pending posts for [brand]"
"What posts need approval?"
```

**Approve Posts:**
```
"Approve post ID [number]"
"Approve all pending posts for [brand]"
```

## Role-Based Permissions

The AI assistant respects Postavel's permission system:

| Role | Can Create | Can Approve | Can Auto-Approve |
|------|-----------|-------------|------------------|
| **Owner** | ✅ | ✅ | ✅ |
| **Admin** | ✅ | ✅ | ✅ |
| **Member** | ✅ (assigned brands only) | ❌ | ❌ |

**Important:** If user is a Member, their posts will be created as "pending" and require Admin/Owner approval before publishing.

## Language Support

Postavel MCP works with prompts in multiple languages:

**English:**
```
"Create a Facebook and LinkedIn post about our summer sale"
"Schedule this for tomorrow at 2pm and auto-approve"
```

**Serbian/Croatian:**
```
"Kreiraj post za Facebook i LinkedIn o letnjoj rasprodaji"
"Zakaži za sutra u 14h i odmah odobri"
```

**German:**
```
"Erstelle einen Facebook- und LinkedIn-Post über unseren Sommerschlussverkauf"
"Plane dies für morgen um 14 Uhr und genehmige sofort"
```

## Common Workflows

### Workflow 1: Create and Schedule a Campaign Post

1. User: "Create a post for Facebook and Instagram about our Black Friday sale, 30% off everything"
2. AI: Creates the post (status: draft)
3. User: "Schedule it for November 29th at 9am and approve it"
4. AI: Schedules the post and approves it (if user has permissions)

### Workflow 2: Multi-Brand Management

1. User: "Show me all brands in workspace 'My Agency'"
2. AI: Lists brands
3. User: "Create a draft post for brand 'Coffee Shop' about new menu items"
4. AI: Creates draft post
5. User: "Now approve that post"
6. AI: Approves the post

### Workflow 3: Content Calendar Review

1. User: "What posts are scheduled for this week?"
2. AI: Lists scheduled posts
3. User: "Approve all pending posts for brand 'Tech Startup'"
4. AI: Approves all pending posts for that brand

## Troubleshooting

### "I can't see certain clients or brands"
- User may be a **Member** with limited access
- They only see clients where they have assigned brands
- Suggest: "Ask your workspace admin to assign you to the needed brands"

### "Auto-approve didn't work"
- Only **Admins** and **Owners** can auto-approve
- If user is a Member, post is created but remains pending
- Suggest: "Your post was created but needs admin approval to publish"

### "Wrong timezone on scheduled posts"
- Postavel uses the workspace's timezone settings
- User can specify timezone explicitly: "Schedule for 2pm CET" or "14:00 Belgrade time"

### "Post not published even though scheduled"
- Check if post is **approved** — only approved posts are published
- Check if scheduled time has passed
- User can ask: "What's the status of post ID [number]?"

## MCP Resources

- **[references/mcp-tools.md](references/mcp-tools.md)** — Complete list of available MCP tools and their parameters
- **[references/setup-guide.md](references/setup-guide.md)** — Detailed setup instructions for mcporter and OAuth
- **[scripts/setup-mcp.sh](scripts/setup-mcp.sh)** — Automated setup script (optional)

## Security & Privacy

- OAuth tokens are session-specific and expire automatically
- AI can only access data the user has permission to access
- All actions are logged in user's activity history
- User can revoke AI access at any time from Postavel settings
