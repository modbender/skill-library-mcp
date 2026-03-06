---
name: notion-to-markdown
description: "Convert Notion pages and databases to markdown format using the official Notion API. Use when you need to: (1) Export a single Notion page to markdown, (2) Bulk export entire Notion databases, (3) Automate Notion content publishing, or (4) Integrate Notion content into documentation workflows. Requires Notion API token setup."
metadata:
  requiredCredentials: "NOTION_API_KEY"
  credentialsType: "Notion API token (personal integration)"
  networkAccess: "Notion API only (@notionhq/client)"
  supplyChainRisk: "Low - only talks to official Notion API, no external data sources"
  security: "Read-only access recommended. Only shares specific pages, not entire workspace."
---

# Notion to Markdown Converter

Convert Notion pages and databases to clean, readable markdown using the official Notion API.

## ⚠️ Security & Credentials

**Required Credentials:**
- `NOTION_API_KEY` - Your personal Notion integration token (required)

**Security Best Practices:**
1. **Create a dedicated integration** - Go to [notion.so/my-integrations](https://www.notion.so/my-integrations) and create an integration for this tool only
2. **Use read-only permissions** - Grant the integration "Reader" access, not "Editor"
3. **Share selectively** - Only share specific pages/databases with the integration, not your entire workspace
4. **Protect your token** - Never commit `.env` files containing `NOTION_API_KEY` to version control
5. **Use temporary tokens** - Consider creating a rotation policy for tokens or using temporary tokens
6. **Code inspection** - This tool only uses the official `@notionhq/client` library and communicates exclusively with Notion's API. No data is sent elsewhere.

**Network Access:**
- Only connects to: `https://api.notion.com` (official Notion API)
- No external APIs or data sources
- No telemetry or logging sent elsewhere

## Requirements

- **Node.js:** 14.0.0 or higher
- **npm:** 6.0.0 or higher
- **Notion API Token:** Required (get from [notion.so/my-integrations](https://www.notion.so/my-integrations))

Check your Node version:
```bash
node --version  # Should be v14.0.0 or higher
npm --version
```

## Quick Start

### 1. Get Your Notion API Key

See [Notion API Setup](references/notion-api-setup.md) for complete instructions:

- Create an integration at [notion.so/my-integrations](https://www.notion.so/my-integrations)
- Copy your API token (`notioneq_...`)
- Share your Notion pages with the integration
- Set environment variable: `export NOTION_API_KEY="your_token"`

### 2. Install Dependencies

```bash
cd scripts
npm install
```

### 3. Convert Pages

**Single page:**
```bash
NOTION_API_KEY=your_token node convert.js <page-id> > output.md
```

**Database export:**
```bash
NOTION_API_KEY=your_token node convert.js <database-id> --database ./exports
```

## Usage Patterns

### Convert Single Notion Page

Extract a page and output to a file:

```bash
node scripts/convert.js a1b2c3d4e5f6g7h8 > my-page.md
```

The converter automatically:
- Fetches the page from Notion
- Converts all blocks to markdown
- Preserves formatting (bold, italic, links, etc.)
- Outputs to stdout or file

### Bulk Export Database

Convert all pages in a Notion database:

```bash
node scripts/convert.js a1b2c3d4e5f6g7h8 --database ./notion-export
```

Creates individual markdown files for each page:
```
notion-export/
├── page-one.md
├── page-two.md
└── page-three.md
```

### Extract Page Metadata

The converter preserves page properties:

```javascript
const result = await convertPageToMarkdown(pageId);
console.log(result.title);      // Page title from Notion
console.log(result.markdown);   // Converted markdown content
console.log(result.pageId);     // Original page ID
```

## What Gets Converted

### Supported Block Types

✅ Text, headings, and paragraphs
✅ Bold, italic, underline, strikethrough, code inline
✅ Links (internal and external)
✅ Lists (ordered and unordered)
✅ Code blocks with syntax highlighting
✅ Tables
✅ Quotes and callouts
✅ Images (as markdown image syntax)
✅ Dividers and separators
✅ Database properties as frontmatter

### Formatting Preserved

- Heading hierarchy (H1, H2, H3, etc.)
- List nesting
- Code block languages
- Link URLs and text
- Emphasis and styling

### Not Preserved

- Notion databases (converted as tables where possible)
- Some advanced formatting (superscript, subscript)
- Canvas blocks
- Embedded web content (converted to links)

## Environment Setup

### Setting the API Key

**Option 1: Using `.env` file (Recommended)**

Create a `.env` file in the scripts directory:

```bash
# scripts/.env
NOTION_API_KEY=ntn_your_api_key_here
```

Then run the converter normally:
```bash
node convert.js <page-id> > output.md
```

The script automatically loads environment variables from `.env` via the `dotenv` package.

**Option 2: Export environment variable**

Permanently set in your shell:

```bash
# ~/.bashrc, ~/.zshrc, or ~/.config/fish/config.fish
export NOTION_API_KEY="notioneq_..."
```

**Option 3: Set for a single command**

```bash
NOTION_API_KEY=your_token node convert.js <page-id>
```

**Security Note:** Add `.env` to `.gitignore` to prevent accidentally committing your API key:

```bash
echo ".env" >> .gitignore
```

## Finding IDs

### Page ID from URL

Notion URL format:
```
https://www.notion.so/Workspace-Name/Page-Title-abc123def456?v=xyz
                                                    ↑ Page ID
```

Copy the ID part (without hyphens in the URL).

### Database ID

Same as page URL - find the ID in the database's URL.

## Troubleshooting

### "NOTION_API_KEY is not set"

Make sure the environment variable is exported:

```bash
export NOTION_API_KEY="notioneq_..."
echo $NOTION_API_KEY  # Verify it's set
```

### "Page not found or not accessible"

- Verify the page ID is correct
- Check that you've shared the page with your Notion integration
- Ensure the integration has access to that workspace

### "Invalid page ID format"

- Notion page IDs are 32-character alphanumeric strings
- Remove hyphens from the URL
- Example valid ID: `a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6`

### Markdown output is incomplete

- The API might have rate-limited your request
- Try again after a moment
- For bulk exports, add delays: `sleep 0.5` between conversions

## Advanced Usage

### Custom Output Processing

Modify `scripts/convert.js` to process markdown before saving:

```javascript
let markdown = result.markdown;
// Add custom processing
markdown = markdown.replace(/\n{3,}/g, '\n\n');  // Clean up spacing
fs.writeFileSync('output.md', markdown);
```

### Batch Processing

Convert multiple pages in a loop:

```bash
for pageId in page1 page2 page3; do
  node convert.js $pageId > "$pageId.md"
done
```

### Integration with Other Tools

The markdown output is plain text and compatible with:
- Static site generators (Hugo, Jekyll, Next.js)
- Documentation platforms (Docusaurus, Doclify)
- Version control (git, GitHub)
- Publishing tools (WordPress, Medium)

## API Reference

For advanced usage, see the [notion-to-md documentation](https://github.com/souvikinator/notion-to-md) and [Notion API reference](https://developers.notion.com/).

## Security Notes

- Keep your `NOTION_API_KEY` secret
- Don't commit API keys to version control
- Use `.gitignore` for `.env` files
- Rotate tokens if compromised
- Share Notion pages with integration only as needed

## See Also

- [Notion API Setup Guide](references/notion-api-setup.md) - Complete setup instructions
- [notion-to-md GitHub](https://github.com/souvikinator/notion-to-md) - Source library
- [Notion API Docs](https://developers.notion.com/) - Official API documentation
