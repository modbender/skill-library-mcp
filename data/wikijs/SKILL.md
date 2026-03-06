---
name: Wiki.js Skill v1.4
description: A complete CLI for managing Wiki.js via the GraphQL API.
---

# Wiki.js Skill v1.4

A complete CLI for managing Wiki.js via the GraphQL API.

## Quick Start

```bash
# Install
npm install && npm link

# Configure
cp config/wikijs.example.json ~/.config/wikijs.json
# Edit with your Wiki.js URL and API token

# Test connection
wikijs health
```

## Commands Reference

### Reading

| Command | Description |
|---------|-------------|
| `wikijs list` | List all pages |
| `wikijs search "query"` | Search pages |
| `wikijs get <id-or-path>` | Read a page |
| `wikijs info <id-or-path>` | Show page metadata |
| `wikijs grep "pattern"` | Search within content |
| `wikijs tree` | Display page hierarchy |

### Writing

| Command | Description |
|---------|-------------|
| `wikijs create <path> <title>` | Create a page |
| `wikijs create ... --template doc` | Create from template |
| `wikijs update <id>` | Update a page |
| `wikijs move <id> <new-path>` | Move a page |
| `wikijs delete <id>` | Delete a page |

### Tags

| Command | Description |
|---------|-------------|
| `wikijs tags` | List all tags |
| `wikijs tag <id> add <tag>` | Add a tag |
| `wikijs tag <id> remove <tag>` | Remove a tag |

### Backup & Restore

| Command | Description |
|---------|-------------|
| `wikijs backup` | Create backup |
| `wikijs restore-backup <file>` | Restore from backup |
| `wikijs export <dir>` | Export to files |

### Versions

| Command | Description |
|---------|-------------|
| `wikijs versions <id>` | Show history |
| `wikijs revert <id> <version>` | Restore version |
| `wikijs diff <id>` | Compare versions |

### Assets

| Command | Description |
|---------|-------------|
| `wikijs images` | List assets |
| `wikijs upload <file>` | Upload asset |
| `wikijs delete-image <id>` | Delete asset |

### Bulk Operations

| Command | Description |
|---------|-------------|
| `wikijs bulk-create <folder>` | Create from files |
| `wikijs bulk-update <folder>` | Update from files |
| `wikijs sync` | Sync to local |
| `wikijs sync --watch` | Watch mode |

### Analysis

| Command | Description |
|---------|-------------|
| `wikijs tree` | Page hierarchy tree |
| `wikijs check-links` | Find broken links |
| `wikijs stats` | Show statistics |
| `wikijs lint <file>` | Lint markdown file |
| `wikijs lint --id <id>` | Lint wiki page |
| `wikijs orphans` | Find pages with no incoming links |
| `wikijs duplicates` | Find similar/duplicate content |
| `wikijs toc <id>` | Generate table of contents |
| `wikijs validate <id>` | Validate page content |
| `wikijs validate --all` | Validate all pages |
| `wikijs spellcheck <id>` | Check spelling |

### Content Operations

| Command | Description |
|---------|-------------|
| `wikijs clone <id> <path>` | Duplicate a page |
| `wikijs replace "old" "new"` | Search/replace across pages |
| `wikijs sitemap` | Generate XML sitemap |

### Interactive

| Command | Description |
|---------|-------------|
| `wikijs shell` | Interactive shell mode |
| `wikijs watch <id>` | Watch page for changes |

### Templates

| Command | Description |
|---------|-------------|
| `wikijs template list` | List templates |
| `wikijs template show <name>` | Show template |
| `wikijs template create <name>` | Create template |
| `wikijs template delete <name>` | Delete template |

### System

| Command | Description |
|---------|-------------|
| `wikijs health` | Check connection |
| `wikijs cache clear` | Clear cache |
| `wikijs completion bash` | Shell completion |

## Global Options

| Option | Description |
|--------|-------------|
| `-v, --verbose` | Verbose output |
| `-d, --debug` | Debug output |
| `--no-color` | Disable colors |
| `--rate-limit <ms>` | API rate limiting |

## Common Options

| Option | Description |
|--------|-------------|
| `--format json\|table` | Output format |
| `--limit <n>` | Limit results |
| `--force` | Skip confirmations |
| `--locale <locale>` | Specify locale |
| `--dry-run` | Preview changes |

## Examples

```bash
# Create page with template
wikijs template create doc --content "# {{title}}\n\n{{date}}"
wikijs create "/docs/api" "API Docs" --template doc

# Find broken links in docs section
wikijs check-links --path "/docs"

# Bulk import with rate limiting
wikijs --rate-limit 500 bulk-create ./pages --path-prefix "/imported"

# Watch mode for continuous sync
wikijs sync --output ~/wiki-mirror --watch --interval 60

# Debug API issues
wikijs --debug list

# Clone a page
wikijs clone 42 "/docs/new-page" --with-tags

# Find orphan pages (no incoming links)
wikijs orphans

# Search and replace across wiki
wikijs replace "oldterm" "newterm" --path "/docs" --dry-run

# Generate table of contents
wikijs toc 42 --format markdown

# Find duplicate content
wikijs duplicates --threshold 80

# Generate sitemap for SEO
wikijs sitemap --output sitemap.xml

# Interactive shell mode
wikijs shell

# Watch a page for changes
wikijs watch "/docs/api" --interval 60

# Spell check a page
wikijs spellcheck 42 --lang en --ignore "API,CLI,GraphQL"

# Validate all pages
wikijs validate --all --format json
```

## Integration Notes

- All commands return exit code 0 on success, 1 on failure
- Use `--format json` for machine-readable output
- Delete operations prompt for confirmation unless `--force` is used
- Escape sequences (`\n`, `\t`) are interpreted in `--content` strings
- Templates support placeholders: `{{title}}`, `{{path}}`, `{{date}}`
