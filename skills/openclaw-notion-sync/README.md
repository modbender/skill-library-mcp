# openclaw-notion-sync

> Sync any workspace or directory to Notion -- folders become pages, files become content.

## Install

```bash
npm install -g @kitakitsune/notion-sync
```

Requires Node.js >= 18.

## Setup

1. Create a Notion integration at [notion.so/my-integrations](https://notion.so/my-integrations)
2. Copy your API token (`ntn_...`)
3. Create a root Notion page and share it with your integration
4. Copy the page ID from the URL

```bash
cd your-project
notion-sync init --token ntn_xxx --page your-page-id
```

This creates a `.notion-sync.json` config file in your project root.

## Usage

```bash
# Sync everything
notion-sync sync

# Preview without making changes
notion-sync sync --dry-run

# Only sync changed files (faster)
notion-sync sync --diff

# Sync a specific directory
notion-sync sync --dir /path/to/folder

# Check sync status
notion-sync status

# Manage ignore patterns
notion-sync ignore list
notion-sync ignore add "*.env"
```

## How it works

notion-sync mirrors your directory structure into Notion:

```
your-project/
  src/           ->  Notion page "src"
    index.ts     ->  Sub-page with file content
  README.md      ->  Notion page with content
  package.json   ->  Notion page with content
```

- **Folders** become Notion pages (folder icon)
- **Files** become Notion sub-pages with their content
- **Checksums** (MD5) track changes so `--diff` only pushes what changed
- **Existing pages** are updated in place (blocks are cleared and re-added)
- Content is chunked into 1800-char blocks to stay within Notion API limits

## Commands

| Command | Description |
|---------|-------------|
| `init --token <token> --page <id> [--dir <path>]` | Initialize config in current (or specified) directory |
| `sync [--dry-run] [--diff] [--dir <path>]` | Sync workspace to Notion |
| `status [--dir <path>]` | Show sync status |
| `ignore list [--dir <path>]` | List ignore patterns |
| `ignore add <pattern> [--dir <path>]` | Add an ignore pattern |

## Config

Config is stored in `.notion-sync.json` in your project root:

```json
{
  "path": "/absolute/path/to/directory",
  "notion": {
    "token": "ntn_...",
    "rootPageId": "your-page-id"
  },
  "ignore": [
    "node_modules",
    ".git",
    "dist",
    ".notion-sync.json",
    "*.lock",
    "*.log"
  ],
  "checksums": {}
}
```

All six ignore patterns above are included by default when you run `init`.

## Programmatic API

You can also use notion-sync as a library:

```typescript
import { syncWorkspace, initConfig, loadConfig, saveConfig } from '@kitakitsune/notion-sync';
import type { NotionSyncConfig } from '@kitakitsune/notion-sync';

const config = loadConfig(process.cwd());
const result = await syncWorkspace(config, { dryRun: false, diffOnly: true });

console.log(result.pushed);  // files synced
console.log(result.skipped); // unchanged files
console.log(result.errors);  // any errors
```

## License

MIT
