# notion-md

Convert Markdown to Notion blocks with full format support.

## Features

- **Rich Text**: Bold, italic, strikethrough, inline code, underline
- **Headings**: H1, H2, H3
- **Lists**: Bulleted, numbered, toggle
- **Blocks**: Quote, callout, divider, code block
- **Links**: Automatic link parsing

## Quick Start

```bash
# Install
pip install -r requirements.txt

# Create a page
echo "# Hello World" | notion-md create -t "My Page"

# With file
notion-md create -t "Article" -f article.md
```

## Format Support

| Markdown | Notion |
|----------|--------|
| `**bold**` | Bold text |
| `*italic*` | Italic text |
| `~~text~~` | Strikethrough |
| `` `code` `` | Inline code |
| `# Title` | Heading 1 |
| `## Title` | Heading 2 |
| `- item` | Bulleted list |
| `1. item` | Numbered list |
| `> quote` | Quote block |
| `---` | Divider |
| ````python code```` | Code block |

## License

MIT
