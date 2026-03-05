# Dessix Skill

A Claude Code skill for interacting with the local [Dessix](https://github.com/openclaw/clawhub) desktop workspace. It calls the Electron MCP bridge directly via a line-delimited JSON socket protocol, letting an agent read, search, and invoke Dessix tools programmatically.

## Installation

### Via npx (recommended)

```bash
npx skills add dessix-skill
```

### Via git clone

```bash
git clone https://github.com/DessixIO/skill.git
cd skill
```

### Manual

Copy `SKILL.md`, `scripts/`, and `references/` into your project.

## Prerequisites

- **Node.js** (v18+)
- **Dessix desktop app** running (the bridge is served by the Electron process)
- (Optional) Set `DESSIX_MCP_BRIDGE_ENDPOINT` to override the default socket path

## Usage

Check bridge connectivity:

```bash
node scripts/dessix-bridge.mjs health
```

List workspaces:

```bash
node scripts/dessix-bridge.mjs invoke --tool dessix_list_workspaces --args '{}'
```

Search blocks:

```bash
node scripts/dessix-bridge.mjs invoke --tool dessix_search_blocks --args '{"query":"MCP","limit":10}'
```

See `SKILL.md` for full workflow examples and `references/dessix-tools.md` for the complete tool reference.

## Publishing to ClawHub

Install the CLI globally:

```bash
npm i -g clawhub
```

Login (opens browser):

```bash
clawhub login
```

### First release

```bash
npm run clawhub:publish -- --version 1.0.0 --changelog "Initial release"
```

### Iterative updates (auto patch bump)

```bash
npm run clawhub:sync
```

### Minor / major release

```bash
npm run clawhub:sync -- --bump minor --changelog "Add new workflow"
npm run clawhub:sync -- --bump major --changelog "Breaking changes"
```

### Dry run (preview without uploading)

```bash
clawhub sync --root . --dry-run
```

## Project Structure

```
├── SKILL.md              # Skill definition (consumed by Claude Code)
├── package.json          # npm scripts for bridge & publishing
├── scripts/
│   └── dessix-bridge.mjs # Bridge client (health, invoke, locate-mcp-script)
└── references/
    └── dessix-tools.md   # Tool names and argument templates
```

## License

See [LICENSE](./LICENSE).
