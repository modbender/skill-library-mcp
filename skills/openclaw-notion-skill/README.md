<div align="center">

# 🔗 OpenClaw Notion Skill

**Seamlessly integrate your Notion workspace with OpenClaw agents**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![OpenClaw](https://img.shields.io/badge/Built%20for-OpenClaw-6E4C9E)](https://openclaw.ai)
[![Notion](https://img.shields.io/badge/Powered%20by-Notion-black)](https://notion.so)
[![Support Project](https://img.shields.io/badge/💝%20Support-ETH%20Tip-orange)](./SUPPORT.md)

</div>

Transform your Notion workspace into a living knowledge base that your AI agents can read, write, and manage. Perfect for content pipelines, project tracking, CRMs, and collaborative documentation.

---

## ✨ What It Does

| Feature | Description |
|---------|-------------|
| 📊 **Query Databases** | Pull structured data from any Notion database |
| 📝 **Create Entries** | Add new rows from agent research and discoveries |
| 🔍 **Search Workspace** | Find pages across your entire shared workspace |
| 🔄 **Update Content** | Modify properties and append blocks dynamically |
| 🗂️ **View Schemas** | Inspect database structures programmatically |
| 🔢 **Smart ID Reference** | Use Notion ID `#3` or direct UUID — your choice |

**Perfect for:**
- Content creators managing editorial calendars
- Solo entrepreneurs tracking projects and leads
- Teams building knowledge bases
- Researchers compiling findings
- Anyone who wants their AI to *actually use* Notion

---

## 🚀 Quick Start (5 Minutes)

### Install via Clawhub (Coming Soon)

Once published:
```bash
openclaw skills install notion-enhanced
```

### Manual Install

### 1. Create Notion Integration

```
notion.so/my-integrations → New integration → Copy token
```

The token starts with `secret_`. Keep it safe.

### 2. Install the Skill

```bash
git clone https://github.com/MoikasLabs/openclaw-notion-skill.git
cd openclaw-notion-skill
./install.sh
```

### 3. Configure

```bash
# Add to ~/.openclaw/.env
NOTION_TOKEN=secret_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### 4. Share Your Database

In Notion:
1. Open your database/page
2. Click **Share** → **Add connections**
3. Select your integration name

### 5. Test Connection

```bash
node notion-cli.js test
```

You'll see all accessible pages and databases. ✅

---

## 🎯 Usage Examples

### Command Line

```bash
# List all entries in your Content Ideas database
node notion-cli.js query-database abc123def456...

# Filter by status
node notion-cli.js query-database abc123... \
  --filter '{"property":"Status","select":{"equals":"Idea"}}'

# Add a new research finding
node notion-cli.js add-entry abc123... \
  --title "AI-Generated Support Structures in 3D Printing" \
  --properties '{"Status":{"select":{"name":"Idea"}},"Platform":{"multi_select":[{"name":"YouTube"}]}}'

# Search across workspace
node notion-cli.js search "tree support"

# Mark as drafted
node notion-cli.js update-page page-id-123... \
  --properties '{"Status":{"select":{"name":"Draft"}}}'
```

### Smart ID Resolution (Notion ID or UUID)

**Reference entries by Notion ID (what you see in the ID column):**

```bash
# Get page by Notion ID #3 - auto-resolves to actual page ID
node notion-cli.js get-page '#3' DATABASE_ID

# Append content using Notion ID
node notion-cli.js append-body '#3' \
  --database DATABASE_ID \
  --text "Research notes here" \
  --type h2

# Add a link to entry #3
node notion-cli.js append-body '#3' \
  --database DATABASE_ID \
  --text "Example: https://makerworld.com/models/123" \
  --type bullet
```

**Or use direct UUID for automation:**

```bash
# Direct UUID (copy from URL)
node notion-cli.js append-body 2fb3e4ac... \
  --text "Content here" \
  --type paragraph
```

The CLI auto-detects:
- Starts with `#` → **Notion ID** lookup (requires database ID)
- 32-char hex → **Direct UUID** (no database needed)

### From OpenClaw

```typescript
// Check your content pipeline
await exec({
  command: `node openclaw-notion-skill/notion-cli.js query-database ${CONTENT_DB_ID}`
});

// Log a discovery
await exec({
  command: `node openclaw-notion-skill/notion-cli.js add-entry ${PROJECTS_DB_ID} \\
    --title "${discoveryTitle}" \\
    --properties '{"Priority":{"select":{"name":"High"}}}'`
});
```

### In Cron Jobs

```typescript
// Research Topic Scout → Pushes directly to Notion
"Research 3D printing trends and add ideas to Notion database"
```

---

## 📁 Database Templates

### Content Pipeline

| Property | Type | Values |
|----------|------|--------|
| Title | Title | - |
| Status | Select | Idea → Draft → Scheduled → Posted |
| Platform | Multi-select | X/Twitter, YouTube, MakerWorld, Blog |
| Publish Date | Date | - |
| Tags | Multi-select | 3D Printing, AI, Entrepreneurship |
| Draft Content | Rich Text | - |

### Project Tracker

| Property | Type | Values |
|----------|------|--------|
| Name | Title | - |
| Status | Select | Not Started → In Progress → Blocked → Done |
| Priority | Select | Low → Medium → High → Critical |
| Due Date | Date | - |
| Est. Hours | Number | - |
| Links | URL | GitHub, MakerWorld, etc. |

### CRM (3D Printing Business)

| Property | Type | Values |
|----------|------|--------|
| Customer | Title | - |
| Status | Select | Lead → Quote → Ordered → Printing → Shipped |
| Email | Email | - |
| Quote Value | Number | $ |
| Filament | Select | PLA, PETG, ABS, etc. |

---

## 🔐 Security

- **Token isolation:** Stored in `~/.openclaw/.env` — never in code
- **Granular permissions:** Integration only sees pages you explicitly share
- **No blanket access:** Cannot touch private pages or unshared teamspaces
- **Your control:** Revoke anytime via [notion.so/my-integrations](https://www.notion.so/my-integrations)

```bash
# Check what's shared
node notion-cli.js test
```

---

## 🛠️ Advanced Usage

### Property Types Reference

```typescript
// Select (single choice)
{ "select": { "name": "In Progress" } }

// Multi-select
{ "multi_select": [{ "name": "Tag 1" }, { "name": "Tag 2" }] }

// Status (new type)
{ "status": { "name": "In progress" } }

// Rich text
{ "rich_text": [{ "text": { "content": "Notes here" } }] }

// Date
{ "date": { "start": "2026-02-15" } }

// Number
{ "number": 42 }

// Checkbox
{ "checkbox": true }
```

### Error Handling

| Error | Fix |
|-------|-----|
| `API token is invalid` | Check token at notion.so/my-integrations |
| `object_not_found` | Share the page with your integration |
| `validation_error` | Check property type matches database schema |
| `rate_limited` | Add 350ms delay between requests |

---

## 🧰 Installation Options

### Option A: Quick (Standalone)

```bash
git clone https://github.com/MoikasLabs/openclaw-notion-skill.git
cd openclaw-notion-skill
npm install
```

Uses `notion-cli.js` — no build step.

### Option B: Full (TypeScript)

```bash
git clone https://github.com/MoikasLabs/openclaw-notion-skill.git
cd openclaw-notion-skill
npm install
npm run build
```

Uses compiled `dist/cli.js` with full TypeScript support.

---

## 📝 CLI Reference

```
notion-cli.js <command> [options]

Commands:
  test                          Test connection, list accessible pages
  query-database <id>           Query database entries
  add-entry <id>                Add new database row
  get-page <id>                 Get page content
  update-page <id>              Update page properties
  get-database <id>             Show database schema
  search <query>                Search workspace

Options:
  --filter '<json>'             Filter query results
  --title "text"                Set entry title
  --properties '<json>'         Set additional properties
  --help                        Show help

Database ID Format:
  From URL: notion.so/workspace/ABC123...
  Use: ABC123... (32 chars, no hyphens)
```

---

## 🌟 Why This Exists

Most AI "integrations" just read a static export. This skill lets your agents:

- ✅ Write findings *back* to your knowledge base
- ✅ Update project status as work progresses
- ✅ Query structured data for context
- ✅ Build living documentation

**Real use case:**
> Your nightly Research Topic Scout cron job searches 3D printing trends, finds 5 interesting techniques, and automatically adds them to your Content Ideas database with status "Idea" and tags extracted from the source.

---

## 🤝 Contributing

1. Fork the repo
2. Create a branch: `git checkout -b feature/amazing-thing`
3. Commit changes: `git commit -m 'Add amazing thing'`
4. Push: `git push origin feature/amazing-thing`
5. Open a Pull Request

Ideas welcome: webhooks, bidirectional sync, bulk operations, templates.

---

## 📜 License

MIT — Built with ❤️ by the OpenClaw community at MoikasLabs

---

## 🔗 Links

- [OpenClaw Docs](https://docs.openclaw.ai)
- [Notion API Docs](https://developers.notion.com)
- [Issue Tracker](https://github.com/MoikasLabs/openclaw-notion-skill/issues)
- [Support Project](./SUPPORT.md) 💝
- [MoikasLabs](https://github.com/MoikasLabs)

---

<div align="center">

**Built for agents who actually get work done.** 🐉

</div>

---

## 📦 Quick Start Templates

Don't build from scratch. Use our pre-configured templates:

| Template | Best For | File |
|----------|----------|------|
| 📝 Content Pipeline | Writers, YouTubers, social media | `templates/content-pipeline.json` |
| 🎯 Project Tracker | Freelancers, solo entrepreneurs | `templates/project-tracker.json` |
| 🖨️ 3D Print CRM | Makers, print shops | `templates/crm-3d-printing.json` |
| 📚 Knowledge Base | SOPs, documentation, wikis | `templates/knowledge-base.json` |

**See [templates/README.md](templates/README.md)** for detailed setup instructions and automation examples.

---

<div align="center">

**Built for agents who actually get work done.** 🐉

</div>
