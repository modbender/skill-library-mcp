# skill-library-mcp

**690+ ready-to-use skills for AI coding assistants, served on demand via MCP.**

[![npm version](https://img.shields.io/npm/v/skill-library-mcp)](https://www.npmjs.com/package/skill-library-mcp)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Node.js](https://img.shields.io/badge/node-%3E%3D22-brightgreen)](https://nodejs.org)

An MCP server that provides on-demand skill loading for AI coding assistants. Instead of stuffing your system prompt with every skill you might need, this server indexes 690+ skills and serves only the ones relevant to your current task — keeping context windows lean and responses focused.

## Why?

- **690+ skills** covering frontend, backend, DevOps, security, testing, databases, AI/ML, automation, and more
- **On-demand loading** — skills are fetched only when needed, not crammed into every conversation
- **IDF-weighted search** — finds the right skill even from natural language queries like "help me debug a memory leak"
- **Works with any MCP-compatible tool** — Claude Code, Cursor, Windsurf, VS Code, Claude Desktop, and others
- **Zero config** — run with `npx`, no setup needed

## Quick Start

```
npx -y skill-library-mcp
```

Add it to your tool's MCP configuration:

<details>
<summary><strong>Claude Code (CLI)</strong></summary>

Add to `~/.claude/settings.json`:

```json
{
  "mcpServers": {
    "skill-library": {
      "command": "npx",
      "args": ["-y", "skill-library-mcp"]
    }
  }
}
```

</details>

<details>
<summary><strong>Claude Desktop</strong></summary>

Add to your `claude_desktop_config.json` ([location varies by OS](https://modelcontextprotocol.io/quickstart/user)):

```json
{
  "mcpServers": {
    "skill-library": {
      "command": "npx",
      "args": ["-y", "skill-library-mcp"]
    }
  }
}
```

</details>

<details>
<summary><strong>Cursor</strong></summary>

Add to `.cursor/mcp.json` (project) or `~/.cursor/mcp.json` (global):

```json
{
  "mcpServers": {
    "skill-library": {
      "command": "npx",
      "args": ["-y", "skill-library-mcp"]
    }
  }
}
```

</details>

<details>
<summary><strong>Windsurf</strong></summary>

Add to `~/.codeium/windsurf/mcp_config.json`:

```json
{
  "mcpServers": {
    "skill-library": {
      "command": "npx",
      "args": ["-y", "skill-library-mcp"]
    }
  }
}
```

</details>

<details>
<summary><strong>VS Code (Copilot)</strong></summary>

Add to `.vscode/mcp.json`:

```json
{
  "servers": {
    "skill-library": {
      "command": "npx",
      "args": ["-y", "skill-library-mcp"]
    }
  }
}
```

</details>

<details>
<summary><strong>Antigravity</strong></summary>

See [Antigravity docs](https://docs.antigravity.dev) for MCP server configuration format.

</details>

<details>
<summary><strong>Manual installation</strong></summary>

```bash
git clone https://github.com/modbender/skill-library-mcp
cd skill-library-mcp
pnpm install
pnpm build
```

Then point your MCP config to the built binary:

```json
{
  "mcpServers": {
    "skill-library": {
      "command": "node",
      "args": ["/path/to/skill-library-mcp/dist/index.js"]
    }
  }
}
```

</details>

## Tools

### `search_skill`

Search for skills by keyword. Returns a ranked list of matching skill names and descriptions.

```
search_skill({ query: "react patterns" })
```

### `load_skill`

Load the full content of a skill by name. Optionally includes resource files.

```
load_skill({ name: "brainstorming", include_resources: true })
```

## Skill Categories

The library includes 690+ skills across areas like:

| Category | Examples |
|----------|----------|
| **Frontend** | React patterns, Angular, Tailwind, accessibility, web performance |
| **Backend** | Node.js, FastAPI, Django, NestJS, GraphQL, API design |
| **DevOps & Cloud** | Terraform, Kubernetes, Docker, AWS, CI/CD, GitOps |
| **Testing** | TDD workflows, Playwright, testing patterns, E2E testing |
| **Security** | Penetration testing, OWASP, threat modeling, security scanning |
| **AI & ML** | LLM application dev, RAG implementation, agent patterns, prompt engineering |
| **Databases** | PostgreSQL, database design, migrations, SQL optimization |
| **Automation** | Slack, GitHub, Jira, Salesforce, Zapier, and 40+ integrations |
| **Architecture** | Microservices, event sourcing, CQRS, clean code, design patterns |

## Skill Format

Skills are directories containing a `SKILL.md` file with YAML frontmatter:

```markdown
---
name: my-skill
description: What this skill does
---

# My Skill

Skill content here...
```

Skills can optionally include a `resources/` directory with additional `.md` files that are appended when `include_resources: true` is set.

## Contributing

Contributions are welcome! To add a new skill:

1. Create a directory under `skills/` with your skill name
2. Add a `SKILL.md` file with YAML frontmatter (`name`, `description`)
3. Run `pnpm dedup` to check for duplicates
4. Submit a PR

## Development

```bash
pnpm install          # Install dependencies
pnpm test             # Run tests
pnpm build            # Build to dist/
pnpm dev              # Run server locally
pnpm dedup            # Check for duplicate skills
make ci               # Run test + build
```

## License

[MIT](LICENSE)
