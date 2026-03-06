---
name: notion-md
description: Convert Markdown to Notion blocks with full format support. Handles bold, italic, strikethrough, inline code, headings, lists, tables, callouts, and more.
homepage: https://developers.notion.com/reference/block
metadata:
  openclaw:
    emoji: "📝"
    requires:
      env: ["NOTION_API_KEY"]
    primaryEnv: "NOTION_API_KEY"
---

# notion-md

Convert Markdown to Notion blocks with full format support.

## Features

- **Rich Text**: Bold, italic, strikethrough, inline code, underline, color
- **Headings**: H1, H2, H3 with proper styling
- **Lists**: Bulleted, numbered, toggle lists
- **Blocks**: Quotes, callouts, dividers, code blocks
- **Advanced**: Tables, nested content, links
- **Parent Page**: Configurable parent page ID

## Setup

### 1. Get Notion API Key

1. Go to https://www.notion.so/my-integrations
2. Create new integration
3. Copy the API key (starts with `ntn_`)

### 2. Configure API Key

```bash
# Option A: Environment variable
export NOTION_API_KEY="ntn_your_key"

# Option B: Config file
mkdir -p ~/.config/notion
echo "ntn_your_key" > ~/.config/notion/api_key
```

### 3. Get Parent Page ID

The parent page where new pages will be created:

```bash
notion-md list-pages
```

Or set default:

```bash
export NOTION_PARENT_PAGE_ID="parent_page_id"
```

## Usage

### Create Page from File

```bash
notion-md create --file article.md --title "My Article" --emoji 📝
```

### Create from stdin

```bash
echo "# Hello World" | notion-md create "Page Title"
```

### Options

| Option | Description |
|--------|-------------|
| `--file, -f` | Input Markdown file |
| `--title, -t` | Page title (required) |
| `--emoji, -e` | Page icon (default: 📄) |
| `--parent-id, -p` | Parent page ID |
| `--dry-run` | Preview without creating |

### List Pages

```bash
notion-md list-pages
```

### Append to Page

```bash
echo "## New Section" | notion-md append --page-id "abc123..."
```

## Notion Format Mapping

| Markdown | Notion Block |
|----------|--------------|
| `# Title` | heading_1 |
| `## Title` | heading_2 |
| `### Title` | heading_3 |
| `**bold**` | bold annotation |
| `*italic*` | italic annotation |
| `~~text~~` | strikethrough |
| `` `code` `` | code annotation |
| `---` | divider |
| `- item` | bulleted_list_item |
| `1. item` | numbered_list_item |
| `> quote` | quote |
| ````text```` | code block |
| `::: callout` | callout |
| `\| table \|` | table (basic) |

## Examples

### Rich Content

```markdown
# My Article

**This is bold** and *this is italic*.

> Important quote here

## Code Example

```python
def hello():
    print("Hello World")
```

- Item 1
- Item 2
```

### Create with Options

```bash
notion-md create \
  --file blog-post.md \
  --title "My Blog Post" \
  --emoji ✍️ \
  --parent-id "page_id_here"
```

## Environment Variables

| Variable | Description |
|----------|-------------|
| `NOTION_API_KEY` | Notion API key |
| `NOTION_PARENT_PAGE_ID` | Default parent page ID |

## API Version

Notion API: 2022-06-28
