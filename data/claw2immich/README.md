# Immich Skill for OpenClaw

OpenClaw agent skill for working with Immich photo libraries via the **claw2immich** MCP server.

## What is this?

This skill teaches OpenClaw agents how to search and interact with your Immich photo library using natural language queries like:
- "Show me photos of Alice and Bob together"
- "Find vacation photos from last summer"
- "Photos taken in Paris"

## Prerequisites

1. **Immich instance** running (https://immich.app)
2. **claw2immich MCP server** installed and running
   - Repository: https://github.com/JoeRu/claw2immich
   - Follow the setup instructions in the claw2immich README
3. **mcporter** configured in OpenClaw (included by default)

## Installation

### 1. Install claw2immich MCP Server

Follow the installation guide at: https://github.com/JoeRu/claw2immich

Make sure the MCP server is running and accessible from your OpenClaw host.

### 2. Install this skill

**Via ClawHub:**
```bash
clawhub install immich
```

**Manual:**
```bash
# Copy to your workspace skills directory
cp -r immich ~/.openclaw/workspace/skills/
```

### 3. Configure MCP Server

Add the claw2immich server to `~/.openclaw/workspace/config/mcporter.json`:

```json
{
  "mcpServers": {
    "immich": {
      "baseUrl": "http://your-claw2immich-host:port/sse"
    }
  }
}
```

**Replace:**
- `your-claw2immich-host` - Hostname/IP where claw2immich is running
- `port` - claw2immich server port (check claw2immich config)

### 4. Configure Photo URLs (Optional but Recommended)

For displaying/downloading photos, add your Immich server URL to `TOOLS.md`:

```markdown
### Immich
- Web-UI: http://your-immich-server:2283
- Photo URLs: http://your-immich-server:2283/api/assets/{id}/thumbnail
```

This helps the agent construct photo URLs when needed.

### 5. Verify

```bash
mcporter list
```

Should show `immich` server with ~248 tools available.

### 6. Restart Gateway

```bash
openclaw gateway restart
```

The skill will be loaded automatically on next agent interaction.

## Usage

Once installed, your agent can handle natural language photo queries:

**Examples:**
- "Show me the newest photo with Alice and Bob together"
- "Find all photos from our Paris vacation in summer 2024"
- "Search for pictures of my dog"
- "Show me favorite photos from last year"

The agent will:
1. Search for people by name to get their IDs
2. Use the correct MCP calls with proper parameters
3. Handle multi-person searches (AND logic)
4. Format results in a readable way

## Example Scripts

The skill includes two example shell scripts:

### Find people together
```bash
cd ~/.openclaw/workspace/skills/immich
./examples/find-people-together.sh "Alice" "Bob" 10
```

### Find by date range
```bash
./examples/find-by-date.sh "2024-06-01" "2024-08-31" "Paris" 20
```

### Get photo URLs
```bash
./examples/get-photo-urls.sh "Alice" 5 "http://your-immich-server:2283"
```

Generates thumbnail and original URLs for photos, with optional download.

## Documentation

- **[SKILL.md](./SKILL.md)** - Complete API reference for agents
  - Common workflows
  - Parameter documentation
  - Response structure
  - Tips and troubleshooting

## Requirements

- **Immich:** Photo management system (https://immich.app)
- **claw2immich:** MCP server for Immich (https://github.com/JoeRu/claw2immich)
- **mcporter:** MCP client (included in OpenClaw)
- **jq:** JSON processor (for example scripts, optional)

## Troubleshooting

### MCP server not found
```bash
# Check if server is running
mcporter list

# Should show:
# - immich (248 tools, ...)
```

If not listed, verify:
1. claw2immich is running
2. `mcporter.json` config is correct
3. Network connectivity to claw2immich host

### No photos found
- Verify Immich has indexed your photos
- Check person names (fuzzy search, try partial names)
- Photos might be archived: include `body_isArchived: false` in queries

## Contributing

This skill is designed to be generic and reusable.

**To contribute:**
1. Keep examples generic (no personal names/IDs)
2. Document new patterns in SKILL.md
3. Test with different Immich/claw2immich versions
4. Submit improvements via pull request

## License

MIT - Free to use, modify, and distribute

## Links

- **Immich:** https://immich.app
- **claw2immich MCP Server:** https://github.com/JoeRu/claw2immich
- **OpenClaw:** https://openclaw.ai
- **ClawHub:** https://clawhub.com
