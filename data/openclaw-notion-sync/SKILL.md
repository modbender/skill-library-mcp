---
name: notion-sync
description: Sync local workspace directories and files to Notion pages using the notion-sync CLI or programmatic API. Use when the user wants to push files to Notion, mirror a directory structure into Notion, initialize notion-sync config, manage ignore patterns, or check sync status.
---

# notion-sync

CLI and library for syncing a local directory tree into Notion. Folders become Notion pages, files become sub-pages with content.

## Quick Reference

### Installation

```bash
npm install -g @kitakitsune/notion-sync
```

Requires Node.js >= 18.

### Initialization

```bash
notion-sync init --token ntn_xxx --page <notion-page-id> [--dir <path>]
```

- Creates `.notion-sync.json` in the target directory
- The Notion integration must be shared with the target root page first

### Sync Commands

```bash
notion-sync sync                   # sync everything
notion-sync sync --dry-run         # preview changes
notion-sync sync --diff            # only sync changed files
notion-sync sync --dir /some/path  # sync a specific directory
notion-sync status                 # show sync state
notion-sync ignore list            # list ignore patterns
notion-sync ignore add "*.env"     # add ignore pattern
```

### Default Ignore Patterns

`node_modules`, `.git`, `dist`, `.notion-sync.json`, `*.lock`, `*.log`

## Programmatic Usage

```typescript
import { syncWorkspace, initConfig, loadConfig, saveConfig } from '@kitakitsune/notion-sync';
import type { NotionSyncConfig } from '@kitakitsune/notion-sync';

const config = loadConfig(process.cwd());
const result = await syncWorkspace(config, { dryRun: false, diffOnly: true });
// result.pushed   - files that were synced
// result.skipped  - files unchanged (when diffOnly)
// result.errors   - files that failed
```

## Architecture

```
src/
  cli.ts     - Commander.js CLI (init, sync, ignore, status)
  sync.ts    - Core sync logic, Notion API calls, checksum diffing
  config.ts  - Load/save/init .notion-sync.json
  types.ts   - NotionSyncConfig interface
  index.ts   - Public API exports
bin/
  notion-sync.js - CLI entry point
```

### Key Implementation Details

- **Checksums**: MD5 hashes stored in `.notion-sync.json` under `checksums` field. Used by `--diff` to skip unchanged files.
- **Content chunking**: File content is split into 1800-character blocks for the Notion API.
- **Page upsert**: Existing pages are updated by deleting all blocks then re-appending. New pages are created with content inline.
- **Folder hierarchy**: Directories are created as Notion pages with folder icon. A `folderCache` avoids redundant API calls.

### Config File Structure

`.notion-sync.json`:

```json
{
  "path": "/absolute/path",
  "notion": {
    "token": "ntn_...",
    "rootPageId": "page-id"
  },
  "ignore": ["node_modules", ".git", "dist", ".notion-sync.json", "*.lock", "*.log"],
  "checksums": { "src/index.ts": "md5hash" }
}
```

## Development

```bash
npm run dev    # watch mode (tsup)
npm run build  # production build
```

Build uses `tsup` to bundle TypeScript to ESM format. Output goes to `dist/`.
