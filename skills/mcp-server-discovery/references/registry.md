# MCP Server Registry Reference

## Official MCP Servers

Maintained by the Model Context Protocol team at Anthropic.

### Filesystem
- **Name**: filesystem
- **Description**: Secure file system access with configurable permissions
- **Install**: `npx -y @modelcontextprotocol/server-filesystem`
- **Use case**: Allow AI to read/write files within allowed directories

### GitHub
- **Name**: github
- **Description**: GitHub API integration for repository management
- **Install**: `npx -y @modelcontextprotocol/server-github`
- **Use case**: Search repos, create PRs, manage issues
- **Requires**: GITHUB_TOKEN environment variable

### PostgreSQL
- **Name**: postgres
- **Description**: PostgreSQL database integration with schema inspection
- **Install**: `npx -y @modelcontextprotocol/server-postgres`
- **Use case**: Query databases, inspect schemas

### SQLite
- **Name**: sqlite
- **Description**: SQLite database operations and querying
- **Install**: `npx -y @modelcontextprotocol/server-sqlite`
- **Use case**: Local database operations

### Puppeteer
- **Name**: puppeteer
- **Description**: Web scraping and browser automation
- **Install**: `npx -y @modelcontextprotocol/server-puppeteer`
- **Use case**: Screenshot web pages, extract content

### Brave Search
- **Name**: brave-search
- **Description**: Brave Search API integration
- **Install**: `npx -y @modelcontextprotocol/server-brave-search`
- **Use case**: Web search without API key requirements

### Fetch
- **Name**: fetch
- **Description**: Web content fetching and processing
- **Install**: `npx -y @modelcontextprotocol/server-fetch`
- **Use case**: Fetch and process web content

### Memory
- **Name**: memory
- **Description**: Knowledge graph-based persistent memory
- **Install**: `npx -y @modelcontextprotocol/server-memory`
- **Use case**: Store and recall information across sessions

## Community MCP Servers

Third-party servers extending MCP capabilities.

### Notable Categories
- **Cloud**: AWS, GCP, Azure integrations
- **Communication**: Slack, Discord, Email
- **Productivity**: Notion, Trello, Linear
- **Data**: Various database and analytics tools

## Configuration Format

MCP client configuration (Claude Desktop, etc.):

```json
{
  "mcpServers": {
    "server-name": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-name"],
      "env": {
        "API_KEY": "your-key"
      }
    }
  }
}
```
