# 🐟 openclawmp

**OpenClaw Marketplace CLI** — 水产市场命令行工具

A command-line client for the [OpenClaw Marketplace](https://openclawmp.cc), allowing you to search, install, publish, and manage agent assets (skills, plugins, triggers, channels, and more).

## Installation

```bash
npm install -g openclawmp
```

Requires **Node.js 18+** (uses built-in `fetch`).

## Quick Start

```bash
# Search for assets
openclawmp search "web search"

# Install a skill
openclawmp install skill/@cybernova/web-search

# List installed assets
openclawmp list

# View asset details
openclawmp info skill/web-search

# Publish your own skill
openclawmp publish ./my-skill
```

## Commands

### `openclawmp search <query>`

Search the marketplace for assets.

```bash
openclawmp search "文件监控"
openclawmp search weather
```

### `openclawmp install <type>/@<author>/<slug>`

Install an asset from the marketplace.

```bash
# Full format with author scope
openclawmp install trigger/@xiaoyue/fs-event-trigger
openclawmp install skill/@cybernova/web-search

# Legacy format (no author)
openclawmp install skill/web-search

# Force overwrite existing
openclawmp install skill/@cybernova/web-search --force
```

**Supported asset types:** `skill`, `config`, `plugin`, `trigger`, `channel`, `template`

### `openclawmp list`

List all assets installed via the marketplace.

```bash
openclawmp list
```

### `openclawmp uninstall <type>/<slug>`

Remove an installed asset.

```bash
openclawmp uninstall skill/web-search
openclawmp uninstall trigger/fs-event-trigger
```

### `openclawmp info <type>/<slug>`

View detailed information about an asset from the registry.

```bash
openclawmp info skill/web-search
openclawmp info trigger/fs-event-trigger
```

### `openclawmp publish [path]`

Publish a local asset directory to the marketplace. Defaults to current directory.

```bash
# Publish current directory
openclawmp publish

# Publish a specific directory
openclawmp publish ./my-skill

# Skip confirmation prompt
openclawmp publish ./my-skill --yes
```

The command will auto-detect the asset type from:
1. `SKILL.md` frontmatter (for skills)
2. `openclaw.plugin.json` (for plugins/channels)
3. `package.json` (fallback)
4. `README.md` (fallback)

### `openclawmp login`

Show device authorization information. Your OpenClaw device identity is used for publishing.

```bash
openclawmp login
```

### `openclawmp whoami`

Show current user/device info and configuration status.

```bash
openclawmp whoami
```

## Global Options

| Option | Description |
|--------|-------------|
| `--api <url>` | Override the API base URL |
| `--version`, `-v` | Show version |
| `--help`, `-h` | Show help |

## Environment Variables

| Variable | Description |
|----------|-------------|
| `OPENCLAWMP_API` | Override the default API base URL (`https://openclawmp.cc`) |
| `OPENCLAW_STATE_DIR` | Override the OpenClaw state directory (default: `~/.openclaw`) |
| `NO_COLOR` | Disable colored output |

## Configuration

Configuration files are stored in `~/.openclawmp/`:

- `auth.json` — Authentication token

Install metadata is tracked in `~/.openclaw/seafood-lock.json` (shared with the OpenClaw ecosystem).

## Asset Types

| Type | Icon | Description |
|------|------|-------------|
| `skill` | 🧩 | Agent skills and capabilities |
| `config` | ⚙️ | Configuration presets |
| `plugin` | 🔌 | Gateway plugins |
| `trigger` | ⚡ | Event triggers |
| `channel` | 📡 | Communication channels |
| `template` | 📋 | Project templates |

## Development

```bash
# Clone and run locally
git clone https://github.com/openclaw/openclawmp.git
cd openclawmp

# Run directly
node bin/openclawmp.js --help
node bin/openclawmp.js search weather

# Link globally for testing
npm link
openclawmp --help
```

## License

MIT
