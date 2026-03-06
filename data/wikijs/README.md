# wikijs-cli

A comprehensive command-line interface for [Wiki.js](https://js.wiki/) - the powerful open-source wiki software.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Node.js Version](https://img.shields.io/badge/node-%3E%3D18.0.0-brightgreen)](https://nodejs.org/)

## Features

- **Full CRUD operations** - Create, read, update, and delete wiki pages
- **Tag management** - Add, remove, and list tags
- **Asset management** - Upload, list, and delete images/files
- **Search** - Full-text search and content grep
- **Backup & Restore** - Export and import wiki content
- **Bulk operations** - Create/update multiple pages from files with progress bars
- **Version control** - View history and revert to previous versions
- **Watch mode** - Automatic periodic synchronization and page monitoring
- **Tree view** - Visual hierarchy of all pages
- **Link checker** - Find broken internal links
- **Orphan detection** - Find pages with no incoming links
- **Duplicate detection** - Find similar content across pages
- **Templates** - Create pages from reusable templates
- **Shell completion** - Auto-completion for bash/zsh/fish
- **Interactive shell** - REPL mode for multiple commands
- **Markdown linting** - Validate and fix markdown issues
- **Spell checking** - Basic spell check with multilingual support
- **Page validation** - Check images, links, and content quality
- **Search & replace** - Find and replace text across pages
- **Sitemap generation** - Generate XML sitemaps for SEO
- **Offline mode** - Work with cached data when server unavailable
- **Rate limiting** - Configurable delays for bulk operations
- **Debug mode** - Verbose output for troubleshooting

## Installation

```bash
# Clone the repository
git clone https://github.com/your-username/wikijs-cli.git
cd wikijs-cli

# Install dependencies
npm install

# Link globally (optional, for system-wide access)
npm link
```

## Configuration

1. Copy the example configuration:
```bash
cp config/wikijs.example.json ~/.config/wikijs.json
```

2. Edit `~/.config/wikijs.json` with your Wiki.js details:
```json
{
  "url": "http://your-wiki-server:3000",
  "apiToken": "YOUR_API_TOKEN_HERE",
  "defaultEditor": "markdown",
  "defaultLocale": "en"
}
```

### Getting an API Token

1. Log in to your Wiki.js instance as an administrator
2. Go to **Administration** > **API Access**
3. Create a new API key with the required permissions
4. Copy the token to your configuration file

## Usage

### Basic Commands

```bash
# Check connection
wikijs health

# List pages
wikijs list
wikijs list --limit 20 --locale en

# Search pages
wikijs search "documentation"

# Get a page
wikijs get 1                    # By ID
wikijs get "/docs/guide"        # By path
wikijs get 1 --raw --metadata   # With metadata header
```

### Creating & Editing Pages

```bash
# Create a page with inline content
wikijs create "/docs/intro" "Introduction" --content "# Welcome\n\nThis is the intro."

# Create from a file
wikijs create "/docs/guide" "User Guide" --file ./guide.md --tag "docs,guide"

# Create from stdin
cat document.md | wikijs create "/docs/readme" "README" --stdin

# Update a page
wikijs update 1 --content "New content here"
wikijs update "/docs/guide" --file ./updated-guide.md
wikijs update 1 --title "New Title" --add-tags "important"

# Move a page
wikijs move 1 "/new/path"

# Delete a page (with confirmation)
wikijs delete 1
wikijs delete 1 --force  # Skip confirmation
```

### Tag Management

```bash
# List all tags
wikijs tags
wikijs tags --format json

# Manage page tags
wikijs tag 1 add "important"
wikijs tag 1 remove "draft"
wikijs tag 1 set "tag1,tag2,tag3"  # Replace all tags
```

### Search & Discovery

```bash
# Full-text search
wikijs search "configuration"

# Search within page content (grep)
wikijs grep "TODO"
wikijs grep "deprecated" --path "/docs" --case-sensitive

# Get page info
wikijs info 1

# View statistics
wikijs stats
wikijs stats --detailed
```

### Backup & Restore

```bash
# Create a backup
wikijs backup
wikijs backup --output my-backup.json --pages-only

# Export pages to files
wikijs export ./backup --format markdown
wikijs export ./backup --format json --with-assets

# Restore from backup
wikijs restore-backup backup.json --dry-run  # Preview
wikijs restore-backup backup.json --skip-existing
wikijs restore-backup backup.json --force    # Overwrite existing
```

### Version Control

```bash
# View page history
wikijs versions 1

# Revert to a previous version
wikijs revert 1 5  # Revert page 1 to version 5
```

### Bulk Operations

```bash
# Create pages from a folder of markdown files
wikijs bulk-create ./pages --path-prefix "/docs" --tag "imported"
wikijs bulk-create ./pages --dry-run  # Preview

# Update existing pages from files
wikijs bulk-update ./pages --path-prefix "/docs"

# Sync all pages to local directory
wikijs sync --output ./local-wiki
wikijs sync --output ./local-wiki --format json

# Watch mode (sync periodically)
wikijs sync --output ./local-wiki --watch --interval 300
```

### Asset Management

```bash
# List assets
wikijs images
wikijs images --folder "/uploads" --limit 100

# Upload a file
wikijs upload ./image.png
wikijs upload ./doc.pdf --folder "/documents" --rename "manual.pdf"

# Delete an asset
wikijs delete-image 42
```

### Tree View & Analysis

```bash
# Display page hierarchy as a tree
wikijs tree
wikijs tree --locale en

# Find broken internal links
wikijs check-links
wikijs check-links --path "/docs"

# Compare page versions
wikijs diff 1

# Find orphan pages (no incoming links)
wikijs orphans

# Find similar/duplicate content
wikijs duplicates --threshold 70

# Generate table of contents
wikijs toc 1 --format markdown
```

### Page Operations

```bash
# Clone/duplicate a page
wikijs clone 1 "/docs/copy-of-page" --with-tags

# Search and replace across pages
wikijs replace "old-term" "new-term" --path "/docs" --dry-run
wikijs replace "oldAPI" "newAPI" --regex --case-sensitive

# Generate XML sitemap
wikijs sitemap --output sitemap.xml --base-url "https://wiki.example.com"
```

### Content Quality

```bash
# Lint markdown files
wikijs lint ./document.md
wikijs lint ./document.md --fix

# Lint a wiki page
wikijs lint --id 1

# Spell check a page
wikijs spellcheck 1 --lang en
wikijs spellcheck 1 --lang fr --ignore "API,CLI"

# Validate page content (images, links, quality)
wikijs validate 1
wikijs validate --all --format json
```

### Interactive & Watch

```bash
# Interactive shell mode
wikijs shell

# Watch a page for changes
wikijs watch 1 --interval 30
wikijs watch "/docs/important" --interval 60
```

### Offline Mode

```bash
# Save pages for offline use
wikijs list --save-offline

# Use cached data (offline mode)
wikijs list --offline

# Automatic fallback on connection failure
wikijs list  # Will use cache if server unavailable
```

### Templates

```bash
# List available templates
wikijs template list

# Create a template
wikijs template create doc --content "# {{title}}\n\nCreated: {{date}}"

# Use a template when creating a page
wikijs create "/docs/new-page" "New Page" --template doc

# Show/delete templates
wikijs template show doc
wikijs template delete doc
```

### Shell Completion

```bash
# Generate completion script
wikijs completion bash >> ~/.bashrc
wikijs completion zsh >> ~/.zshrc
wikijs completion fish > ~/.config/fish/completions/wikijs.fish
```

## Global Options

```bash
wikijs --verbose <command>     # Verbose output
wikijs --debug <command>       # Debug output (includes verbose)
wikijs --no-color <command>    # Disable colors (for CI/scripts)
wikijs --rate-limit 500 <cmd>  # Add 500ms delay between API calls
```

## Output Formats

Most commands support multiple output formats:

```bash
wikijs list --format table  # Default, human-readable
wikijs list --format json   # Machine-readable JSON
```

## Configuration Options

| Option | Description | Default |
|--------|-------------|---------|
| `url` | Wiki.js server URL | Required |
| `apiToken` | API authentication token | Required |
| `defaultEditor` | Default editor type | `markdown` |
| `defaultLocale` | Default page locale | `en` |
| `autoSync.enabled` | Enable auto-sync | `false` |
| `autoSync.path` | Local sync directory | - |
| `autoSync.intervalHours` | Sync interval | `24` |
| `backup.enabled` | Enable backups | `true` |
| `backup.path` | Backup directory | - |
| `backup.keepDays` | Backup retention | `30` |

## Error Handling

The CLI provides detailed error messages for common issues:

```bash
# Connection errors
✗ Connection failed: ECONNREFUSED
  Config path: ~/.config/wikijs.json

# GraphQL errors (detailed)
✗ Field "nonexistent" not found in type "Page"

# Page not found
✗ Page not found: /invalid/path
```

## Troubleshooting

### Connection Refused
- Verify the `url` in your config file is correct
- Ensure Wiki.js is running and accessible
- Check firewall settings

### Authentication Failed
- Regenerate your API token in Wiki.js admin
- Ensure the token has the required permissions
- Check the token hasn't expired

### Page Not Found (by path)
- Paths are case-sensitive
- Use `wikijs list` to see existing paths
- Try specifying `--locale` if using multiple languages

## API Compatibility

This CLI is compatible with **Wiki.js 2.x** using the GraphQL API.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [Wiki.js](https://js.wiki/) - The amazing wiki platform
- [Commander.js](https://github.com/tj/commander.js/) - CLI framework
- [Ora](https://github.com/sindresorhus/ora) - Elegant terminal spinners
- [Chalk](https://github.com/chalk/chalk) - Terminal string styling
