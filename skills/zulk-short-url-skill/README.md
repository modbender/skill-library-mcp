# Zulk Skills Repository

A collection of AI Agent Skills and Model Context Protocol (MCP) integrations for [Zu.lk](https://zu.lk) - the AI-first premium URL shortener.

## 🚀 Mission

Empowering AI agents to manage digital presence through seamless URL shortening, real-time tracking, and advanced analytics.

## 📦 What's inside?

- **[SKILL.md](./SKILL.md)**: The primary Agent Skill definition compatible with OpenClaw, Cursor, VS Code, and other `AgentSkills` compliant assistants.
- **MCP Server Integration**: Direct access to the Zulk MCP server with multiple transport options (HTTP, SSE, Stdio).

## 🛠️ Quick Start

### For Cursor / Claude Desktop / VS Code
Add the following to your MCP configuration:

```json
{
  "mcpServers": {
    "zulk-url-shortener": {
      "url": "https://mcp.zu.lk/mcp"
    }
  }
}
```

### For OpenClaw
1. Add the repository URL `https://github.com/Zu-lk/zulk-short-url-skill` to your OpenClaw skills list.
2. The agent will automatically detect `SKILL.md` and configure the Zulk capabilities.

## 🔐 Security & Privacy

Zulk uses Google OAuth 2 for secure authentication. Your links and analytics are only accessible to you and your authorized team members.

## 📖 Links
- [Zu.lk Website](https://zu.lk)
- [Zu.lk MCP Details](https://zu.lk/-/mcp)
- [API Documentation](https://zu.lk/-/api)

---
© 2025 Zulk. Blazing-fast redirects for the AI era.
