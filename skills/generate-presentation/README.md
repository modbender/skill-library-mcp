# Presentation Generation Skill

An [Agent Skill](https://agentskills.io) that generates professional HTML and PDF presentations from markdown content, URLs, or topic descriptions. It creates visually stunning slides with AI-generated illustrations, keyboard navigation, and automatic PDF export.

Works with **Claude Code**, **Cursor**, and **OpenClaw** — any AI coding agent that supports the SKILL.md format.

## Features

- **Multiple input sources** — markdown files, URLs, plain text, or topic descriptions
- **Design matching** — analyzes reference images in `references/` folder and replicates the visual style
- **AI-generated illustrations** — creates custom images for each slide using OpenAI GPT Image models
- **Interactive HTML** — full-viewport slides with keyboard navigation, progress bar, and slide counter
- **PDF export** — automatic conversion of slides to a single PDF document
- **Editable content** — exports `content.md` for easy re-generation with updated text

## Prerequisites

- [Node.js](https://nodejs.org/) 18+ (for the MCP server)
- [Python 3](https://www.python.org/) + [Pillow](https://pillow.readthedocs.io/) (for PDF export)
- [OpenAI API key](https://platform.openai.com/api-keys) (for image generation)
- Playwright MCP server (optional, for slide screenshot validation)

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/nhype/presentation-generation-skill.git
```

### 2. Build the MCP server

The skill requires the OpenAI GPT Image MCP server for generating slide illustrations.

```bash
cd presentation-generation-skill/mcp-servers/openai-gpt-image
npm install
npm run build
```

### 3. Configure the MCP server

Add to your project's MCP config file (`.mcp.json` for Claude Code / Cursor, or `openclaw.json` for OpenClaw):

```json
{
  "mcpServers": {
    "openai-gpt-image-mcp": {
      "command": "node",
      "args": [
        "/absolute/path/to/mcp-servers/openai-gpt-image/dist/index.js",
        "--env-file",
        "/absolute/path/to/.env"
      ]
    }
  }
}
```

Create a `.env` file with your OpenAI API key:

```
OPENAI_API_KEY=sk-your-key-here
```

### 4. Install Python dependency

```bash
pip install Pillow
```

### 5. Install the skill for your agent

Pick the section that matches your AI coding agent:

---

#### Claude Code

**Project-level** (this project only):

```bash
cp -r skills/generate-presentation YOUR_PROJECT/.claude/skills/
```

**Personal** (available in all your projects):

```bash
cp -r skills/generate-presentation ~/.claude/skills/
```

The skill becomes available as a slash command:

```
/generate-presentation My startup pitch deck about AI-powered analytics
```

See the [Claude Code skills docs](https://docs.anthropic.com/en/docs/claude-code/skills) for more details.

---

#### Cursor

Cursor discovers skills through its rules system or via the [cursor-skills](https://github.com/chrisboden/cursor-skills) MCP server.

**Option A — Cursor rules directory** (simplest):

```bash
cp -r skills/generate-presentation YOUR_PROJECT/.cursor/skills/
```

Then add a rule file at `.cursor/rules/generate-presentation.mdc`:

```yaml
---
description: Generate professional HTML/PDF presentations from topics, URLs, or markdown files
globs: []
alwaysApply: false
---

@skills/generate-presentation/SKILL.md
```

When you ask Cursor's agent to create a presentation, it will pick up the skill from the rules.

**Option B — cursor-skills MCP server** (if you use [cursor-skills](https://github.com/chrisboden/cursor-skills)):

```bash
cp -r skills/generate-presentation /path/to/cursor-skills/skills/
```

The MCP server auto-discovers skills in its `skills/` directory. Ask the agent:

> Use the generate-presentation skill to create a pitch deck about AI analytics

Or import directly from GitHub:

> Please import https://github.com/nhype/presentation-generation-skill

See the [Cursor skills guide](https://design.dev/guides/claude-skills/) for more details.

---

#### OpenClaw

OpenClaw uses the same SKILL.md format. Install the skill to one of these locations:

**Workspace-level** (this agent only):

```bash
cp -r skills/generate-presentation YOUR_WORKSPACE/skills/
```

**Global** (all agents on your machine):

```bash
cp -r skills/generate-presentation ~/.openclaw/skills/
```

Configure the OpenAI API key for the skill in `~/.openclaw/openclaw.json`:

```json
{
  "skills": {
    "entries": {
      "generate-presentation": {
        "enabled": true,
        "env": {
          "OPENAI_API_KEY": "sk-your-key-here"
        }
      }
    }
  }
}
```

Then ask your OpenClaw agent:

> Generate a presentation about AI-powered analytics

Or invoke it directly:

> /generate-presentation My startup pitch deck

See the [OpenClaw skills docs](https://docs.openclaw.ai/tools/skills) for more details.

---

## Usage

Tell your AI agent what to present. The skill accepts:

**A topic:**
```
/generate-presentation My startup pitch deck about AI-powered analytics
```

**A markdown file:**
```
/generate-presentation presentation/content.md
```

**A URL:**
```
/generate-presentation https://example.com/blog-post-to-present
```

### Design References

Place reference images in a `references/` folder in your project root. The skill will analyze these images and match the visual style (colors, typography, layout) in the generated slides.

```
your-project/
├── references/
│   ├── design-reference-1.png
│   └── design-reference-2.jpg
├── presentation/           # Generated output goes here
│   ├── slides.html
│   ├── presentation.pdf
│   ├── content.md
│   ├── slide_1.png
│   └── images/
└── skills/
    └── generate-presentation/
```

If no reference images are provided, the skill uses a clean modern default style.

### Re-generating

After the presentation is created, edit `presentation/content.md` and run:

```
/generate-presentation presentation/content.md
```

This regenerates all slides with your updated content while keeping the same visual style.

## Output

| File | Description |
|------|-------------|
| `presentation/slides.html` | Interactive HTML presentation (open in browser) |
| `presentation/presentation.pdf` | PDF export (one slide per page, 1920x1080) |
| `presentation/slide_N.png` | Individual slide screenshots |
| `presentation/images/` | AI-generated illustrations |
| `presentation/content.md` | Editable markdown source |

## How It Works

1. **Content gathering** — Reads your input (markdown, URL, or topic) and structures it into slides
2. **Design analysis** — Studies reference images to extract color palette, typography, and layout patterns
3. **HTML generation** — Creates a self-contained HTML file with all slides
4. **Image generation** — Uses OpenAI GPT Image to create custom illustrations for slides
5. **Validation** — Screenshots each slide and compares against reference design, iterating until it matches
6. **PDF export** — Converts slide screenshots into a single PDF document
7. **Content export** — Generates editable `content.md` for future regeneration

## Project Structure

```
presentation-generation-skill/
├── skills/
│   └── generate-presentation/
│       ├── SKILL.md                 # Main skill definition (cross-platform)
│       ├── scripts/
│       │   └── slides_to_pdf.py     # PDF conversion utility
│       └── templates/
│           └── slide-template.html  # HTML slide template
├── mcp-servers/
│   └── openai-gpt-image/           # Bundled MCP server for image generation
│       ├── src/index.ts
│       ├── package.json
│       └── tsconfig.json
├── examples/
│   └── example-content.md          # Example input markdown
├── README.md
└── LICENSE                          # Apache 2.0
```

## Platform Compatibility

| Feature | Claude Code | Cursor | OpenClaw |
|---------|-------------|--------|----------|
| Skill format | SKILL.md | SKILL.md | SKILL.md |
| Slash command | `/generate-presentation` | Agent-driven | `/generate-presentation` |
| MCP server | `.mcp.json` | `.cursor/mcp.json` | `openclaw.json` |
| Skill location | `.claude/skills/` | `.cursor/skills/` or `skills/` | `skills/` or `~/.openclaw/skills/` |
| Auto-discovery | Yes (via description) | Yes (via rules/MCP) | Yes (via description) |

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## License

Apache 2.0 — see [LICENSE](LICENSE) for details.
