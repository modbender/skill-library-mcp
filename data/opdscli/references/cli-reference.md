# opdscli CLI Reference

## Installation

```bash
brew tap rafadc/opdscli
brew install opdscli
```

## Global Flags

| Flag | Short | Description |
|------|-------|-------------|
| `--verbose` | `-v` | Show HTTP requests and parsing details |
| `--quiet` | `-q` | Suppress all output except errors and data |
| `--catalog` | `-c` | Override the default catalog for this command |
| `--version` | | Print version and exit |

## Commands

### `opdscli catalog` — Manage catalogs

```bash
# Add a public catalog
opdscli catalog add <name> <url>

# Add with Basic Auth (prompts for username and password)
opdscli catalog add <name> <url> --auth-type basic

# Add with Bearer token auth (prompts for token)
opdscli catalog add <name> <url> --auth-type bearer

# List all configured catalogs
opdscli catalog list

# Set the default catalog
opdscli catalog set-default <name>

# Remove a catalog
opdscli catalog remove <name>
```

### `opdscli search` — Search for books

```bash
# Search the default catalog
opdscli search "science fiction"

# Search a specific catalog
opdscli search "python programming" --catalog mylib

# Increase crawl depth (default: 3) when server-side OpenSearch is unavailable
opdscli search "rare book" --depth 5
```

Search tries server-side OpenSearch first. If unsupported by the catalog, it falls back to local crawling, matching against title, author, and description.

### `opdscli download` — Download a book

```bash
# Download as epub (default format)
opdscli download "The Great Adventure"

# Specify format: epub, pdf, mobi, cbz, cbr
opdscli download "The Great Adventure" --format pdf

# Specify output directory
opdscli download "The Great Adventure" --output ~/Books

# From a specific catalog
opdscli download "The Great Adventure" --catalog mylib
```

If no exact match is found, the tool shows up to 5 fuzzy suggestions.

### `opdscli latest` — Browse latest additions

```bash
# Show 20 latest additions (default)
opdscli latest

# Show more entries
opdscli latest --limit 50

# From a specific catalog
opdscli latest --catalog mylib
```

## Supported Formats

| Format | MIME type |
|--------|-----------|
| EPUB | `application/epub+zip` |
| PDF | `application/pdf` |
| MOBI | `application/x-mobipocket-ebook` |
| CBZ | `application/x-cbz` |
| CBR | `application/x-cbr` |

## Configuration

Config file: `~/.config/opdscli.yaml`

```yaml
default_catalog: mylib
catalogs:
  mylib:
    url: https://my-library.example.com/opds
    auth:
      type: basic
      username: user
      password: pass
  public:
    url: https://public.example.com/opds
settings:
  default_format: epub
```

File permissions are set to `600`. Do not manually edit — use `opdscli catalog` subcommands.
