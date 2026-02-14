# skill-library-mcp

An MCP server that provides on-demand skill loading for Claude Code. Search and load skills from your local skill library without keeping them all in context.

## Installation

### Using npx (recommended)

Add to your Claude Code MCP config (`~/.claude/settings.json`):

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

### Manual

```bash
git clone <repo-url>
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

## Tools

### search_skill

Search for skills by keyword. Returns a ranked list of matching skill names and descriptions.

**Parameters:**
- `query` (string) — Keywords to search for (e.g. "debugging", "react patterns", "terraform")

**Example:**
```
search_skill({ query: "react" })
→ Found 5 skills matching "react":
  - react-patterns (react-patterns) — Common React component patterns
  - react-best-practices (react-best-practices) — Best practices for React apps
  ...
```

### load_skill

Load the full content of a skill by name. Returns the complete SKILL.md content and optionally resources.

**Parameters:**
- `name` (string) — Skill name or directory name (e.g. "brainstorming", "ai-engineer")
- `include_resources` (boolean, default: false) — Whether to include resource files

**Example:**
```
load_skill({ name: "brainstorming", include_resources: true })
→ [Full SKILL.md content with appended resource files]
```

## Skill Format

Skills are directories containing a `SKILL.md` file with YAML frontmatter:

```
my-skill/
  SKILL.md
  resources/        # Optional
    guide.md
    examples.md
```

`SKILL.md` format:

```markdown
---
name: my-skill
description: What this skill does
metadata:
  category: development
---

# My Skill

Skill content here...
```

## Configuration

The server looks for skills in `../skills` relative to the built `dist/index.js`. Skills are shipped with the package — no additional setup needed.

## Development

```bash
pnpm install          # Install dependencies
pnpm test             # Run tests
pnpm test:watch       # Run tests in watch mode
pnpm build            # Build to dist/
pnpm dev              # Run server locally via tsx
make ci               # Run test + build
make mcp-test         # Build and test MCP initialize handshake
```

## License

MIT
