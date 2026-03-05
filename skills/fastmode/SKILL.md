---
name: fastmode
description: Create, deploy, and host a website for free. Build a complete website from scratch and deploy it to the cloud with free hosting, free SSL, and custom domains — all from the terminal. Full CMS included: manage blog posts, team members, pages, products, portfolios, services, testimonials, FAQs, or any structured content. Add and edit CMS content, sync database schemas, validate HTML templates, invite clients to a white-label portal, and push live deployments. Convert any existing HTML site into a CMS-powered site. One-time browser login for OAuth, then every operation runs entirely in the terminal — designed for AI agents to go from zero to a publicly accessible website in minutes.
metadata: {"openclaw":{"emoji":"⚡","homepage":"https://fastmode.ai","requires":{"bins":["fastmode"]},"install":[{"id":"npm","kind":"npm","package":"fastmode-cli","bins":["fastmode"]}]}}
user-invokable: true
---

# FastMode CLI — Complete Agent Reference

FastMode lets you create a live website, deploy it to the cloud, and manage all its content — entirely from the command line. One-time browser login for OAuth authentication, then every operation runs in the terminal. No local servers, no manual dashboards.

- **Free cloud hosting** — every site gets a live URL at `yoursite.fastmode.ai`
- **Free SSL** — HTTPS included automatically
- **Custom domains** — connect any domain (e.g. `www.example.com`)
- **Full CMS** — any content structure (blog, team, products, portfolios, anything)
- **Agent-native** — every operation works via CLI, zero human intervention needed

---

## Table of Contents

1. [End-to-End Workflow](#end-to-end-workflow)
2. [CRITICAL: Before You Build Anything](#critical-before-you-build-anything)
3. [Website Analysis](#website-analysis-do-this-before-writing-code)
4. [Command Reference](#command-reference)
5. [Project Resolution](#project-resolution)
6. [Schema & Field Types](#schema--field-types)
7. [Content Items](#content-items)
8. [Client Portal Management](#client-portal-management)
9. [Package Structure](#package-structure)
10. [Manifest Format](#manifest-format)
11. [Template Syntax](#template-syntax) (includes SEO rules, image handling, forms, inline editing)
12. [Deployment & Build Status](#deployment--build-status)
13. [Validation](#validation)
14. [Common Mistakes & How to Fix Them](#common-mistakes--how-to-fix-them)
15. [Pre-Deployment Checklist](#pre-deployment-checklist)
15. [Error Handling & Exit Codes](#error-handling--exit-codes)

---

## End-to-End Workflow

This is the complete sequence to go from nothing to a live website.

```bash
# 1. Authenticate (one-time — credentials persist at ~/.fastmode/credentials.json)
fastmode login

# 2. Create a project (gets a free hosted URL instantly)
fastmode projects create "Acme Corp"
fastmode use "Acme Corp"

# 3. Define content structure (write schema.json, then sync it)
fastmode schema sync -f schema.json

# 4. Add content
fastmode items create posts -n "Welcome" -d '{"title": "Welcome to Acme", "body": "<p>We build great things.</p>"}'
fastmode items create team -n "Jane Doe" -d '{"role": "Founder", "bio": "<p>Visionary leader.</p>"}'

# 5. Build HTML templates with {{tokens}}, package into a zip, validate, deploy
fastmode validate package site.zip
fastmode deploy site.zip
# Deploy waits for build to finish and reports success or failure with error details

# 6. If the build failed, check what went wrong
fastmode status
# Fix the issue, then re-deploy
```

---

## CRITICAL: Before You Build Anything

**STOP. Before writing ANY HTML, templates, or manifest.json, complete these steps.**

### Step 1: Check for Existing Projects

```bash
fastmode projects
```

This lists all the user's existing FastMode projects.

### Step 2: Decide — Existing or New Project

**If projects exist:** Ask the user: "Is this website for one of your existing projects, or should I create a new one?" Let the user choose.

**If NO projects exist:** This is a new user — ask: "What would you like to name your new project?"

### Step 3a: For EXISTING Projects

1. User selects the project from the list
2. Run `fastmode use "Project Name"` to set it as default
3. Run `fastmode schema show` to get the current collections and fields
4. **Use this schema to build templates with the correct field names**

### Step 3b: For NEW Projects

1. Ask for the project name if you don't have it
2. Run `fastmode projects create "Project Name"`
3. Run `fastmode use "Project Name"`
4. You'll create the schema later with `fastmode schema sync`
5. Optionally generate sample content: `fastmode generate-samples`

### Checkpoint — Confirm Before Continuing

| Requirement | How to Get It |
|-------------|---------------|
| Project selected/created | `fastmode projects` / `fastmode projects create` |
| Default set | `fastmode use "Project Name"` |
| Schema known (existing) | `fastmode schema show` |

**If you don't have a project set, DO NOT PROCEED.** Go back to Step 1.

**WHY THIS MATTERS:**
- For existing projects: The schema determines which fields to use in templates — get it wrong and the build fails
- For new projects: You need the project before you can deploy
- Always: The user must confirm which project to use — never assume

---

## Website Analysis (Do This Before Writing Code)

Before writing any HTML or templates, analyze the site:

1. **Map ALL URLs** — document every page path (`/`, `/about`, `/blog`, `/blog/post-slug`, etc.)
2. **Categorize each page** — Static (fixed content), List (shows multiple items), or Detail (single item from a collection)
3. **Identify collections** — repeating content that should be CMS-managed (blog posts, team members, products, testimonials, etc.)
4. **Document assets** — all CSS, JS, image, and font file locations
5. **PRESERVE original URLs** — if the site uses `/resources` for articles, keep `/resources`. Do NOT change it to `/blog`. Use the manifest's path configuration.

---

## Command Reference

### Authentication

```bash
fastmode login                          # Open browser for OAuth device flow
fastmode logout                         # Delete ~/.fastmode/credentials.json
fastmode whoami                         # Show current user email and name
```

- `login` uses OAuth 2.0 device authorization flow: opens a browser window where the user approves access on `fastmode.ai`, then credentials are saved automatically. The browser is only needed for this one-time login step.
- **OAuth scopes:** The token grants access to the user's FastMode projects only (project management, schema editing, content CRUD, deployments). No third-party service access is requested.
- Credentials persist at `~/.fastmode/credentials.json` with restricted file permissions (`0o600` — owner read/write only). Treat this file as a sensitive secret.
- Tokens auto-refresh. If a token expires, the next command will refresh it silently using the stored refresh token.
- If credentials are missing or invalid, most commands will trigger the login flow automatically.
- `logout` deletes `~/.fastmode/credentials.json` and revokes the stored tokens.

### Projects

```bash
fastmode projects                       # List all projects (default action)
fastmode projects list                  # Same as above
fastmode projects create "Name"         # Create a new project
fastmode projects create "Name" --subdomain custom-sub  # Custom subdomain
fastmode projects create "Name" --force                  # Skip similar-name check
fastmode use <project>                  # Set default project for all commands
```

- `projects create` checks for existing projects with similar names. Use `--force` to skip.
- Subdomain auto-generated from name if not provided (lowercase, hyphens, max 30 chars).
- `use` stores the default in `~/.fastmode/config.json`. Does NOT validate the project exists.

### Schema

```bash
fastmode schema show                    # Show all collections and fields
fastmode schema show -p "Project Name"  # Specify project
fastmode schema sync -f schema.json     # Create collections and fields from JSON file
fastmode schema field-types             # List all available field types (no auth needed)
```

- `schema show` requires authentication and a project.
- `schema sync` reads a local JSON file and creates/updates the schema. Skips duplicates. Two-phase: creates collections first, then fields (handles relation dependencies).
- `schema field-types` works without authentication.

### Content Items

```bash
fastmode items list <collection>                          # List all items
fastmode items list posts --limit 10 --sort publishedAt --order desc
fastmode items get <collection> <slug>                    # Get single item
fastmode items create <collection> -n "Name" -d '{"field": "value"}'
fastmode items create posts -n "Title" -f data.json       # Data from file
fastmode items create posts -n "Draft Post" -d '{}' --draft
fastmode items update <collection> <slug> -d '{"field": "new value"}'
fastmode items update posts my-post -n "New Title"
fastmode items update posts my-post --publish             # Publish a draft
fastmode items update posts my-post --unpublish           # Revert to draft
fastmode items delete <collection> <slug> --confirm       # REQUIRES --confirm
fastmode items relations <collection>                     # Show linkable items for relation fields
fastmode items relations posts --field author             # Options for specific field
```

See the [Content Items](#content-items) section below for detailed rules on data formats, relation fields, and drafts.

### Client Portal Management

```bash
fastmode clients list                              # List portal clients with access
fastmode clients invite client@example.com         # Invite with default permissions
fastmode clients invite client@example.com -n "Jane" --permissions cms.read,cms.write
fastmode clients invitations                       # List pending invitations
fastmode clients update-permissions <accessId> --permissions cms.read,editor
fastmode clients revoke <accessId> --confirm       # REQUIRES --confirm
fastmode clients cancel-invite <invitationId> --confirm  # REQUIRES --confirm
```

See the [Client Portal Management](#client-portal-management) section below for details on permissions, invite flow, and examples.

### Deployment & Build Status

```bash
fastmode deploy site.zip                # Deploy and wait for build to finish
fastmode deploy site.zip --force        # Skip GitHub sync check
fastmode deploy site.zip --no-wait      # Upload only, don't wait for build
fastmode deploy site.zip --timeout 300000  # Custom timeout in ms (default: 120000)
fastmode status                         # Check current build/deploy status
fastmode deploys                        # List deployment history
fastmode deploys --limit 5             # Limit number of results
```

See [Deployment & Build Status](#deployment--build-status) below for the full deploy lifecycle.

### Validation

```bash
fastmode validate manifest manifest.json
fastmode validate template index.html -t custom_index
fastmode validate template post.html -t custom_detail -c posts
fastmode validate template post.html -t custom_detail -c posts -p "My Project"
fastmode validate template about.html -t static_page
fastmode validate package site.zip
```

- Template types: `custom_index` (collection listing), `custom_detail` (single item), `static_page` (fixed page).
- `-c` specifies the collection slug (required for `custom_index` and `custom_detail`).
- `-p` validates tokens against the actual project schema (reports missing fields).
- All validation commands exit with code 1 on errors — safe for CI/CD pipelines.

### Documentation & Examples

```bash
fastmode examples <type>                # Code examples for a specific pattern
fastmode guide                          # Full website conversion guide
fastmode guide templates                # Template syntax guide
fastmode guide common_mistakes          # Common pitfalls to avoid
fastmode generate-samples               # Generate placeholder content for empty collections
fastmode generate-samples -c posts team # Specific collections only
```

Available example types: `manifest_basic`, `manifest_custom_paths`, `blog_index_template`, `blog_post_template`, `team_template`, `downloads_template`, `form_handling`, `asset_paths`, `data_edit_keys`, `each_loop`, `conditional_if`, `nested_fields`, `featured_posts`, `parent_context`, `equality_comparison`, `comparison_helpers`, `youtube_embed`, `nested_collection_loop`, `loop_variables`, `common_mistakes`.

Available guide sections: `full`, `first_steps`, `analysis`, `structure`, `seo`, `manifest`, `templates`, `tokens`, `forms`, `assets`, `checklist`, `common_mistakes`.

---

## Project Resolution

Every project-scoped command (schema, items, deploy, status, etc.) needs a project. Resolution order:

1. **`-p` / `--project` flag** — explicit on the command: `-p "My Project"` or `-p abc123-uuid`
2. **`FASTMODE_PROJECT` environment variable** — set in shell: `export FASTMODE_PROJECT="My Project"`
3. **Default project** — saved by `fastmode use "My Project"` in `~/.fastmode/config.json`

If none is set, the command prints an error and exits with code 1:
```
Error: No project specified.
Use -p <id-or-name>, set FASTMODE_PROJECT env var, or run: fastmode use <project>
```

Project identifiers can be:
- **UUID** — used directly (e.g. `550e8400-e29b-41d4-a716-446655440000`)
- **Project name** — resolved via API (exact match first, then partial match, case-insensitive)

---

## Schema & Field Types

### Creating a Schema

Write a `schema.json` file and sync it:

```bash
fastmode schema sync -f schema.json
```

### schema.json Format

```json
{
  "collections": [
    {
      "slug": "posts",
      "name": "Blog Posts",
      "nameSingular": "Blog Post",
      "fields": [
        { "slug": "title", "name": "Title", "type": "text", "isRequired": true },
        { "slug": "excerpt", "name": "Excerpt", "type": "textarea" },
        { "slug": "body", "name": "Body", "type": "richText" },
        { "slug": "featured-image", "name": "Featured Image", "type": "image" },
        { "slug": "category", "name": "Category", "type": "select", "options": "News, Tutorial, Update" },
        { "slug": "tags", "name": "Tags", "type": "multiSelect", "options": "JavaScript, Python, DevOps, AI" },
        { "slug": "featured", "name": "Featured", "type": "boolean" },
        { "slug": "author", "name": "Author", "type": "relation", "referenceCollection": "team" }
      ]
    },
    {
      "slug": "team",
      "name": "Team Members",
      "nameSingular": "Team Member",
      "fields": [
        { "slug": "role", "name": "Role", "type": "text" },
        { "slug": "bio", "name": "Bio", "type": "richText" },
        { "slug": "photo", "name": "Photo", "type": "image" },
        { "slug": "email", "name": "Email", "type": "email" }
      ]
    }
  ]
}
```

To add fields to existing collections, use `fieldsToAdd`:

```json
{
  "fieldsToAdd": [
    {
      "collectionSlug": "posts",
      "fields": [
        { "slug": "reading-time", "name": "Reading Time", "type": "number" }
      ]
    }
  ]
}
```

You can combine `collections` and `fieldsToAdd` in the same file. Duplicate collections and fields are automatically skipped.

### Available Field Types

| Type | Description | Template Usage | Notes |
|------|-------------|----------------|-------|
| `text` | Single-line text | `{{field}}` | Titles, names, short strings |
| `textarea` | Multi-line plain text | `{{field}}` | Descriptions, excerpts |
| `richText` | Formatted HTML content | `{{{field}}}` | **MUST use triple braces** |
| `number` | Numeric value | `{{field}}` | Prices, counts, order |
| `boolean` | True/false toggle | `{{#if field}}` | Toggles, flags |
| `date` | Date only | `{{field}}` | Birth dates, event dates |
| `datetime` | Date and time | `{{field}}` | Timestamps |
| `image` | Image file/URL | `{{field}}` | Renders as URL |
| `file` | Downloadable file (max 10MB) | `{{field}}` | Link as `<a href="{{field}}" download>` |
| `url` | Web link | `{{field}}` | External URLs |
| `videoEmbed` | YouTube/Vimeo/Wistia/Loom | `{{field}}` | Embed URL |
| `email` | Email with validation | `{{field}}` | Validated email addresses |
| `select` | Single dropdown | `{{field}}` | Requires `"options": "A, B, C"` |
| `multiSelect` | Multiple selections | `{{field}}` | Requires `"options": "A, B, C"` |
| `relation` | Link to another collection | `{{field.name}}` | Requires `"referenceCollection": "slug"` |

### Relation Fields — CRITICAL

Relation fields link items between collections (e.g. a post has an author from the team collection). When creating or updating items with relation fields:

- **You MUST use the item's UUID**, not its name or slug
- Use `fastmode items relations <collection>` to get the available IDs
- Example: `fastmode items relations posts --field author` shows team member IDs

```bash
# First, find the author's item ID
fastmode items relations posts --field author
# Output shows: ID: 550e8400-..., Name: Jane Doe, Slug: jane-doe

# Then use that ID when creating a post
fastmode items create posts -n "My Post" -d '{"title": "My Post", "author": "550e8400-e29b-41d4-a716-446655440000"}'
```

**WRONG:** `"author": "Jane Doe"` — this will NOT work.
**CORRECT:** `"author": "550e8400-e29b-41d4-a716-446655440000"` — use the UUID.

---

## Content Items

### Creating Items

```bash
fastmode items create <collection> -n "Item Name" -d '{"field": "value"}'
```

| Flag | Description |
|------|-------------|
| `-n, --name <name>` | **Required.** Item name/title. |
| `-s, --slug <slug>` | URL slug. Auto-generated from name if omitted. |
| `-d, --data <json>` | Field data as JSON string. |
| `-f, --file <path>` | Read field data from a JSON file (takes precedence over `-d`). |
| `-p, --project <id>` | Project ID or name. |
| `--draft` | Create as unpublished draft. |

**Data rules:**
- `-d` value must be valid JSON. Keys are field slugs.
- `-f` reads from a JSON file. If both `-f` and `-d` are given, `-f` wins.
- If neither `-d` nor `-f` is given, the item is created with just the name (no field data).
- Rich text fields accept raw HTML: `"body": "<h2>Title</h2><p>Content here.</p>"`
- Relation fields require UUIDs (see above).
- Without `--draft`, items are published immediately (`publishedAt` set to now).

### Updating Items

```bash
fastmode items update <collection> <slug> -d '{"field": "new value"}'
```

| Flag | Description |
|------|-------------|
| `-n, --name <name>` | New name/title. |
| `-d, --data <json>` | Updated fields as JSON. Only provided fields change — others are preserved. |
| `-f, --file <path>` | Read updated data from a JSON file. |
| `-p, --project <id>` | Project ID or name. |
| `--publish` | Set `publishedAt` to now (make item live). |
| `--unpublish` | Set `publishedAt` to null (revert to draft). |

**Update is a partial merge.** Only the fields you provide in `-d` are changed. All other fields remain as they are.

### Deleting Items

```bash
fastmode items delete <collection> <slug> --confirm
```

The `--confirm` flag is **required**. Without it, the command refuses to run and exits with code 1. This is a safety measure — deletion is permanent and cannot be undone.

**Always ask the user for confirmation before deleting.**

### Draft / Publish Mechanics

| Action | Command |
|--------|---------|
| Create as published (default) | `fastmode items create posts -n "Title" -d '{...}'` |
| Create as draft | `fastmode items create posts -n "Title" -d '{...}' --draft` |
| Publish a draft | `fastmode items update posts my-slug --publish` |
| Unpublish (revert to draft) | `fastmode items update posts my-slug --unpublish` |

- Draft items have `publishedAt: null` and are not visible on the live site.
- Published items have a `publishedAt` timestamp and appear on the live site.
- Without `--draft`, new items are published immediately.

---

## Client Portal Management

The client portal lets you give external clients (your customers, collaborators) limited access to manage content on your FastMode site. Clients get their own login, separate from your admin account, with configurable permissions.

### How It Works

1. **You invite a client** by email — they receive a unique invite link
2. **Client clicks the link** — creates a password and gets portal access
3. **Client manages content** — based on the permissions you assigned
4. **You control access** — update permissions or revoke access at any time

The portal is **auto-enabled** on the project when you send the first invitation. No manual setup needed.

### Available Permissions

| Permission | Description |
|------------|-------------|
| `cms.read` | View collection items |
| `cms.write` | Create, edit, archive, and delete items |
| `editor` | Access the visual editor |
| `forms.read` | View form submissions |
| `dns` | Manage DNS settings |
| `api` | Access API and integrations |
| `notifications` | Manage notification rules |
| `billing` | View plans and manage billing |

**Default permissions** (used when none specified): `cms.read`, `cms.write`, `editor`, `forms.read`

### Inviting Clients

```bash
# Invite with default permissions
fastmode clients invite client@example.com

# Invite with a name
fastmode clients invite client@example.com -n "Jane Smith"

# Invite with specific permissions
fastmode clients invite client@example.com -n "Jane Smith" --permissions cms.read,forms.read

# Invite with all permissions
fastmode clients invite client@example.com --permissions cms.read,cms.write,editor,forms.read,dns,api,notifications,billing
```

The command returns an **invite URL** — share this with the client. The link expires in 7 days.

**Important:**
- Each email can only be invited once per project
- If a client already has access, the invite will fail
- If a pending invitation already exists for the email, the invite will fail

### Listing Clients and Invitations

```bash
# See who has portal access
fastmode clients list

# See pending (unaccepted) invitations
fastmode clients invitations
```

`clients list` shows the **access ID** for each client — you need this ID to update permissions or revoke access.

### Updating Permissions

```bash
# First, get the access ID from the list
fastmode clients list

# Update permissions (replaces ALL existing permissions)
fastmode clients update-permissions <accessId> --permissions cms.read,cms.write,editor
```

**Permissions are replaced entirely** — if a client had `cms.read,cms.write,editor,forms.read` and you set `--permissions cms.read`, they will ONLY have `cms.read`.

### Revoking Access

```bash
# Revoke a client's portal access (requires --confirm)
fastmode clients revoke <accessId> --confirm
```

The `--confirm` flag is **required**. Without it, the command refuses to run.

**Always ask the user for confirmation before revoking access.**

Revoking access is a soft delete — the client's account still exists but they cannot access this project's portal. Their active sessions are terminated immediately.

### Canceling Invitations

```bash
# Cancel a pending invitation (requires --confirm)
fastmode clients cancel-invite <invitationId> --confirm
```

The invitation link will no longer work. Use `fastmode clients invitations` to get the invitation ID.

### Typical Workflow

```bash
# 1. Invite your client
fastmode clients invite designer@agency.com -n "Design Agency" --permissions cms.read,cms.write,editor

# 2. Share the invite URL from the output with the client

# 3. Later, check who has access
fastmode clients list

# 4. Restrict a client to read-only
fastmode clients update-permissions abc12345 --permissions cms.read

# 5. Remove a client who no longer needs access
fastmode clients revoke abc12345 --confirm
```

---

## Package Structure

The deployment package is a `.zip` file with this exact structure:

```
site.zip
├── manifest.json              # REQUIRED — defines pages and CMS templates
├── pages/                     # Static HTML pages
│   ├── index.html             # Homepage (REQUIRED — must have path "/")
│   ├── about.html
│   └── contact.html
├── templates/                 # CMS-powered templates (if using collections)
│   ├── posts_index.html       # Blog listing page
│   ├── posts_detail.html      # Single blog post page
│   └── team_index.html        # Team listing page
└── public/                    # ALL static assets (CSS, JS, images, fonts)
    ├── css/
    │   └── style.css
    ├── js/
    │   └── main.js
    └── images/
        ├── logo.png
        └── favicon.ico
```

### Strict Rules

1. **`manifest.json` MUST be at the root of the zip.**
2. **Static pages go in `pages/`.** One HTML file per page.
3. **CMS templates go in `templates/`.** Convention: `{collection}_index.html` and `{collection}_detail.html`.
4. **ALL static assets go in `public/`.** CSS, JavaScript, images, fonts — everything.
5. **Reference assets with `/public/` prefix in HTML.** Example: `<link href="/public/css/style.css" rel="stylesheet">`.
6. **A homepage is required.** One page must have `"path": "/"` in the manifest.

### Critical: Asset Paths

**WRONG — will 404:**
```html
<link href="/assets/css/style.css" rel="stylesheet">
<link href="/css/style.css" rel="stylesheet">
<link href="../css/style.css" rel="stylesheet">
<script src="js/main.js"></script>
```

**CORRECT:**
```html
<link href="/public/css/style.css" rel="stylesheet">
<script src="/public/js/main.js"></script>
<img src="/public/images/logo.png" alt="Logo">
```

This also applies **inside CSS files** — background images AND fonts:
```css
/* WRONG */
background-image: url('../images/bg.jpg');
background-image: url('images/bg.jpg');
src: url('../fonts/custom.woff2');

/* CORRECT */
background-image: url('/public/images/bg.jpg');
src: url('/public/fonts/custom.woff2');
```

**Asset path conversion table:**

| Original Path | Converted Path |
|---------------|----------------|
| `css/style.css` | `/public/css/style.css` |
| `../css/style.css` | `/public/css/style.css` |
| `./images/logo.png` | `/public/images/logo.png` |
| `/images/logo.png` | `/public/images/logo.png` |
| `../fonts/custom.woff` | `/public/fonts/custom.woff` |

External URLs (Google Fonts, CDNs, etc.) stay unchanged.

---

## Manifest Format

The `manifest.json` file defines the site structure. It uses a FLAT format for CMS templates (not nested).

### Basic Example (Static Only)

```json
{
  "pages": [
    { "path": "/", "file": "pages/index.html", "title": "Home" },
    { "path": "/about", "file": "pages/about.html", "title": "About" },
    { "path": "/contact", "file": "pages/contact.html", "title": "Contact" }
  ]
}
```

### With CMS Collections

```json
{
  "pages": [
    { "path": "/", "file": "pages/index.html", "title": "Home" },
    { "path": "/about", "file": "pages/about.html", "title": "About" }
  ],
  "cmsTemplates": {
    "postsIndex": "templates/posts_index.html",
    "postsIndexPath": "/blog",
    "postsDetail": "templates/posts_detail.html",
    "postsDetailPath": "/blog",
    "teamIndex": "templates/team_index.html",
    "teamIndexPath": "/team"
  }
}
```

### CMS Template Keys — FLAT Format

Each collection needs 2-4 keys in `cmsTemplates`. The format is `{collectionSlug}Index`, `{collectionSlug}IndexPath`, `{collectionSlug}Detail`, `{collectionSlug}DetailPath`.

| Key | Required | Description |
|-----|----------|-------------|
| `{slug}Index` | Yes | Path to the collection listing template file |
| `{slug}IndexPath` | Yes | URL path for the listing page (e.g. `/blog`) |
| `{slug}Detail` | No | Path to the single item template file |
| `{slug}DetailPath` | No | URL path prefix for item pages (e.g. `/blog` → `/blog/item-slug`) |

**Example for a "services" collection:**
```json
"cmsTemplates": {
  "servicesIndex": "templates/services_index.html",
  "servicesIndexPath": "/services",
  "servicesDetail": "templates/services_detail.html",
  "servicesDetailPath": "/services"
}
```

### Common Manifest Mistakes — AI Agents Frequently Get This Wrong

**AI agents frequently use a nested object format or "collections" key that FastMode does NOT support.** Read carefully.

**WRONG — using "collections" key (MOST COMMON AI MISTAKE):**
```json
{
  "collections": {
    "posts": {
      "indexPath": "/blog",
      "indexFile": "collections/posts/index.html",
      "detailPath": "/blog/:slug",
      "detailFile": "collections/posts/detail.html"
    }
  }
}
```

**WRONG — nested objects inside cmsTemplates:**
```json
"cmsTemplates": {
  "posts": {
    "indexPath": "/blog",
    "detailPath": "/blog"
  }
}
```

**WRONG — singular slug names:**
```json
"postIndex": "..."   // Should be "postsIndex"
"postDetail": "..."  // Should be "postsDetail"
```

**CORRECT — flat keys using `cmsTemplates`, matching the collection slug exactly:**
```json
"cmsTemplates": {
  "postsIndex": "templates/posts_index.html",
  "postsIndexPath": "/blog",
  "postsDetail": "templates/posts_detail.html",
  "postsDetailPath": "/blog"
}
```

Key rules:
- Use `cmsTemplates`, **NOT** `collections`
- Use **FLAT** keys: `{slug}Index`, `{slug}Detail`, `{slug}IndexPath`, `{slug}DetailPath`
- Do **NOT** nest objects inside collection names
- Use `fastmode validate manifest manifest.json` to catch these errors before deploying

### Optional: Head/Body Injection

```json
{
  "pages": [...],
  "cmsTemplates": {...},
  "defaultHeadHtml": "<link rel=\"stylesheet\" href=\"/public/css/global.css\">",
  "defaultBodyEndHtml": "<script src=\"/public/js/analytics.js\"></script>"
}
```

---

## Template Syntax

FastMode templates use Handlebars-style tokens. There are three types of templates:

- **Static pages** (`pages/`): Fixed HTML with optional `data-edit-key` attributes for inline CMS editing and optional `{{#each}}` loops for dynamic content.
- **Index templates** (`templates/`): Collection listing pages. **MUST** contain at least one `{{#each collectionSlug}}` loop.
- **Detail templates** (`templates/`): Single item pages. **MUST** contain CMS tokens like `{{name}}`, `{{{body}}}`, etc.

### SEO Tags — Do NOT Include

FastMode automatically manages all SEO meta tags. Including them in your HTML will cause duplicate tags (bad for SEO ranking). **Remove ALL of these from your templates:**

| Tag | Why to Remove |
|-----|---------------|
| `<title>...</title>` | Managed via CMS Settings |
| `<meta name="description">` | Managed via CMS Settings |
| `<meta name="keywords">` | Managed via CMS Settings |
| `<meta property="og:*">` | Open Graph auto-generated |
| `<meta name="twitter:*">` | Twitter cards auto-generated |
| `<link rel="icon">` | Favicon managed in settings |
| `<link rel="shortcut icon">` | Favicon managed in settings |
| `<link rel="apple-touch-icon">` | Managed by FastMode |
| `<meta name="google-site-verification">` | Managed in settings |

**Correct `<head>` structure:**
```html
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <!-- SEO managed by Fast Mode — do not add title, description, or OG tags -->
  <link rel="stylesheet" href="/public/css/style.css">
  <!-- External fonts, scripts, etc. are fine -->
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap" rel="stylesheet">
</head>
```

### Built-in Fields (Every Item Has These)

| Token | Description | Example |
|-------|-------------|---------|
| `{{name}}` | Item name/title | `<h1>{{name}}</h1>` |
| `{{slug}}` | URL slug | `<a href="/posts/{{slug}}">` |
| `{{url}}` | Full URL to detail page | `<a href="{{url}}">Read more</a>` |
| `{{publishedAt}}` | Publish date | `<time>{{publishedAt}}</time>` |
| `{{createdAt}}` | Creation date | |
| `{{updatedAt}}` | Last modified date | |

### Regular Fields — Double Braces `{{field}}`

Used for text, number, date, image, url, email, select, boolean fields:

```html
<h1>{{name}}</h1>
<p>{{excerpt}}</p>
<img src="{{featured-image}}" alt="{{name}}">
<span>Category: {{category}}</span>
<a href="{{website-url}}">Visit</a>
```

### Rich Text Fields — Triple Braces `{{{field}}}`

**CRITICAL:** Rich text fields contain HTML. You **MUST** use triple braces `{{{ }}}` so the HTML renders correctly. Double braces will escape the HTML and display raw tags as text.

```html
<!-- CORRECT — HTML renders properly -->
<div class="content">{{{body}}}</div>
<div class="bio">{{{bio}}}</div>

<!-- WRONG — HTML appears as escaped text like &lt;p&gt;Hello&lt;/p&gt; -->
<div class="content">{{body}}</div>
```

### Loops — `{{#each collection}}`

Used in index templates and static pages to iterate over collection items.

**Basic loop:**
```html
{{#each posts}}
  <article>
    <h2><a href="{{url}}">{{name}}</a></h2>
    <p>{{excerpt}}</p>
  </article>
{{/each}}
```

**Loop modifiers:**

| Modifier | Description | Example |
|----------|-------------|---------|
| `limit=N` | Maximum items | `{{#each posts limit=6}}` |
| `sort="field"` | Sort by field | `{{#each posts sort="publishedAt"}}` |
| `order="asc\|desc"` | Sort direction | `{{#each posts sort="name" order="asc"}}` |
| `featured=true` | Only featured items | `{{#each posts featured=true limit=3}}` |
| `where="field.slug:{{slug}}"` | Filter by relation | `{{#each posts where="author.slug:{{slug}}"}}` |

**Combined modifiers:**
```html
<!-- Latest 3 featured posts, newest first -->
{{#each posts featured=true limit=3 sort="publishedAt" order="desc"}}
  <article>{{name}}</article>
{{/each}}
```

### Loop Variables

Available only inside `{{#each}}` blocks:

| Variable | Description | Example |
|----------|-------------|---------|
| `{{@index}}` | Zero-based index (0, 1, 2...) | `Item {{@index}}` |
| `{{@first}}` | True for the first item | `{{#if @first}}hero{{/if}}` |
| `{{@last}}` | True for the last item | `{{#unless @last}},{{/unless}}` |
| `{{@length}}` | Total number of items | `Showing {{@length}} items` |

**Do NOT use loop variables outside `{{#each}}` blocks** — they will produce warnings and undefined values.

```html
{{#each posts}}
  {{#if @first}}
    <div class="hero">
      <h1>{{name}}</h1>
    </div>
  {{else}}
    <div class="card">
      <h3>{{name}}</h3>
    </div>
  {{/if}}
{{/each}}
```

### Conditionals — `{{#if}}`, `{{#unless}}`

```html
<!-- Show if field has a value -->
{{#if image}}
  <img src="{{image}}" alt="{{name}}">
{{/if}}

<!-- Show if field has a value, with fallback -->
{{#if thumbnail}}
  <img src="{{thumbnail}}" alt="">
{{else}}
  <div class="placeholder">No image</div>
{{/if}}

<!-- Show if field is empty/missing -->
{{#unless posts}}
  <p>No posts yet.</p>
{{/unless}}
```

### Equality & Comparison Helpers

```html
<!-- Equal -->
{{#if (eq status "published")}}
  <span class="badge">Published</span>
{{/if}}

<!-- Not equal — useful for "Related Items" excluding current item -->
{{#unless (eq slug ../slug)}}
  <a href="{{url}}">{{name}}</a>
{{/unless}}

<!-- Numeric comparisons -->
{{#if (lt @index 1)}}   <!-- Less than -->
{{#if (gt @index 0)}}   <!-- Greater than -->
{{#if (lte price 100)}} <!-- Less than or equal -->
{{#if (gte stock 5)}}   <!-- Greater than or equal -->
{{#if (ne status "draft")}} <!-- Not equal -->
```

**Hero + grid layout pattern:**
```html
{{#each posts}}
  {{#if (lt @index 1)}}
    <div class="hero"><h1>{{name}}</h1></div>
  {{else}}
    {{#if (lt @index 4)}}
      <div class="featured"><h3>{{name}}</h3></div>
    {{else}}
      <div class="list-item">{{name}}</div>
    {{/if}}
  {{/if}}
{{/each}}
```

### Relation Fields — Dot Notation

Access fields on related items using dot notation:

```html
{{#each posts}}
  <article>
    <h2>{{name}}</h2>
    {{#if author}}
      <span class="author">By {{author.name}}</span>
      {{#if author.photo}}
        <img src="{{author.photo}}" alt="{{author.name}}">
      {{/if}}
    {{/if}}
  </article>
{{/each}}
```

Available: `{{relation.name}}`, `{{relation.slug}}`, `{{relation.url}}`, `{{relation.anyField}}`.

### Parent Context — `../`

Inside a loop, access the parent scope (the current page's item) with `../`:

```html
<!-- On an author detail page, show only THIS author's posts -->
<h1>{{name}}</h1>

<h2>Posts by {{name}}</h2>
{{#each posts}}
  {{#if (eq author.name ../name)}}
    <article>
      <h2><a href="{{url}}">{{name}}</a></h2>
    </article>
  {{/if}}
{{/each}}
```

### Nested Loops with `@root.`

When nesting loops, use `@root.` to reference root-level collections:

```html
{{#each categories}}
  <h3>{{name}}</h3>
  {{#each @root.posts where="category.slug:{{slug}}"}}
    <a href="{{url}}">{{name}}</a>
  {{/each}}
{{/each}}
```

### Inline Editing — `data-edit-key` (CRITICAL for Static Pages)

**Without `data-edit-key` attributes, static pages have NO editable content in the CMS dashboard.** Every text element that should be editable MUST have one.

```html
<!-- Static pages — REQUIRED for editable content -->
<h1 data-edit-key="home-hero-title">Welcome to Our Site</h1>
<p data-edit-key="home-hero-subtitle">We build amazing things.</p>
<p data-edit-key="home-about-text">Our story began in 2020...</p>

<!-- Hierarchical naming for sections -->
<section class="about">
  <h2 data-edit-key="about-section-title">About Us</h2>
  <p data-edit-key="about-section-paragraph-1">First paragraph...</p>
  <p data-edit-key="about-section-paragraph-2">Second paragraph...</p>
</section>

<!-- CMS templates — optional, for hardcoded headers -->
<h1 data-edit-key="blog-page-title">Our Blog</h1>
```

**Naming convention: `{page}-{section}-{element}`**

Examples: `home-hero-title`, `about-team-heading`, `contact-form-intro`, `services-cta-button`

Rules:
- Keys must be unique across the **entire site** (not just the page).
- Use lowercase with hyphens.
- For different pages, prefix with the page name.
- Static pages without edit keys will appear in the CMS but have nothing editable.

### Video Embeds

```html
{{#if video}}
  <iframe
    src="{{video}}"
    allowfullscreen
    referrerpolicy="strict-origin-when-cross-origin"
    title="Video"
  ></iframe>
{{/if}}
```

The `referrerpolicy="strict-origin-when-cross-origin"` attribute is **required** for YouTube embeds — without it, videos may show Error 150/153.

### Images — Static vs CMS Content

There are two types of images and they are handled differently:

**1. Static/UI images** — logos, icons, decorative backgrounds bundled with the site:
```html
<!-- KEEP these as static /public/ paths -->
<img src="/public/images/logo.png" alt="Company Logo">
<img src="/public/images/icons/arrow.svg" alt="">
```

**2. CMS content images** — post images, team photos, product images managed through the CMS:
```html
<!-- USE CMS tokens — NEVER hardcode content image URLs -->
{{#if image}}
  <img src="{{image}}" alt="{{name}}">
{{/if}}
```

**Rule of thumb:** If it's site branding/design → keep static. If it's content that changes per item → use CMS tokens.

**Always wrap CMS images in `{{#if}}`** — not every item may have an image:
```html
{{#if image}}
  <img src="{{image}}" alt="{{name}}">
{{else}}
  <div class="placeholder-image"></div>
{{/if}}
```

**Common mistake — mixing static and CMS images:**
```html
<!-- WRONG: hardcoded image inside a CMS loop -->
{{#each products}}
  <img src="/images/product-placeholder.jpg" alt="Product">  <!-- BAD -->
  <h2>{{name}}</h2>
{{/each}}

<!-- CORRECT: all content comes from CMS -->
{{#each products}}
  {{#if image}}
    <img src="{{image}}" alt="{{name}}">
  {{/if}}
  <h2>{{name}}</h2>
{{/each}}
```

### Forms

```html
<form data-form-name="contact" action="/_forms/contact" method="POST">
  <input type="text" name="name" placeholder="Your name" required>
  <input type="email" name="email" placeholder="Your email" required>
  <textarea name="message" placeholder="Your message" required></textarea>
  <button type="submit">Send Message</button>
</form>
```

Rules:
- `data-form-name` attribute is required.
- `action` must point to `/_forms/{formName}`.
- All inputs must have `name` attributes.
- A submit button is required.

**CRITICAL: Remove Original Form Handlers**

If the source site has JavaScript that handles form submissions, you **MUST** remove or replace it. Original site JS often does `e.preventDefault()` and shows a "fake" success toast — the data goes nowhere.

```javascript
// PROBLEM: This blocks real submissions!
form.addEventListener('submit', (e) => {
  e.preventDefault();
  showToast('Message sent!');  // FAKE! Data not saved!
});
```

**Option A (simplest):** Remove the original JavaScript form handler entirely. The native `<form action="/_forms/contact" method="POST">` will submit correctly.

**Option B (keep JS UX):** Replace the handler with one that actually POSTs to FastMode:
```javascript
form.addEventListener('submit', async (e) => {
  e.preventDefault();
  const formName = form.dataset.formName;
  const response = await fetch('/_forms/' + formName, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(Object.fromEntries(new FormData(form)))
  });
  if (response.ok) {
    form.reset();
    alert('Message sent!');  // NOW it's real!
  }
});
```

---

## Deployment & Build Status

### How Deployment Works

1. **Upload:** `fastmode deploy site.zip` reads the zip, validates it, and uploads it to the server.
2. **Build:** The server processes the package (renders templates, publishes pages). This happens asynchronously.
3. **Wait:** By default, `deploy` polls for build status every 3 seconds until the build completes or times out (default 2 minutes).
4. **Result:** Success message with page count and version, or failure message with error details.

### Deploy Flags

| Flag | Description |
|------|-------------|
| `--force` | Skip the GitHub connection check. Use if the project has GitHub connected but you want to deploy via CLI anyway. |
| `--no-wait` | Upload only — don't wait for the build to finish. Useful for fire-and-forget. |
| `--timeout <ms>` | Custom build timeout in milliseconds. Default: `120000` (2 minutes). |

### Checking Build Status

**After every deploy or content change, check the build status:**

```bash
fastmode status
```

If the build failed, `status` shows:
- The error message
- Build logs
- What went wrong

**Always run `fastmode status` after deploying to verify the build succeeded.**

If a build fails:
1. Run `fastmode status` to see the error
2. Fix the issue (template errors, invalid tokens, missing files, etc.)
3. Re-deploy with `fastmode deploy site.zip`

### Deploy History

```bash
fastmode deploys                # Show last 10 deployments
fastmode deploys --limit 5     # Show last 5
```

Shows status, version, duration, source, and errors for each deployment.

### Exit Codes

- `deploy`: Exits 1 if the build fails (when waiting).
- `status`: Exits 1 if the latest deploy shows "Failed".
- Both: Exit 1 if no project is specified.

---

## Validation

Always validate before deploying. Validation catches errors that would cause build failures.

### Validation Workflow

```bash
# 1. Validate the manifest
fastmode validate manifest manifest.json

# 2. Validate each template
fastmode validate template pages/index.html -t static_page
fastmode validate template templates/posts_index.html -t custom_index -c posts
fastmode validate template templates/posts_detail.html -t custom_detail -c posts

# 3. Validate the complete package
fastmode validate package site.zip
```

### What Gets Checked

**Manifest validation:**
- Valid JSON syntax
- `pages` array exists and is not empty
- Homepage (path `/`) exists
- All file paths are valid
- `cmsTemplates` format is correct (flat keys, not nested)

**Template validation:**
- Balanced tags: `{{#each}}` has matching `{{/each}}`, `{{#if}}` has `{{/if}}`
- Index templates have at least one `{{#each}}` loop
- Detail templates have CMS tokens
- Rich text fields use triple braces `{{{field}}}`
- Loop variables only used inside loops
- Asset paths use `/public/` prefix
- Forms have required attributes
- YouTube iframes have `referrerpolicy`

**Package validation:**
- manifest.json exists at root
- All referenced files exist in the zip
- Assets are in `public/` (not `assets/` or root)
- Templates are in `templates/` (not `collections/`)
- All templates pass individual validation

### Validation with Schema Check

Add `-p` to validate tokens against the actual project schema:

```bash
fastmode validate template templates/posts_detail.html -t custom_detail -c posts -p "My Project"
```

This reports which tokens reference fields that don't exist in the schema yet, with instructions to create them via `fastmode schema sync`.

---

## Common Mistakes & How to Fix Them

### 1. Assets return 404

**Problem:** CSS, JS, or images don't load.
**Cause:** Files are in `/assets/` instead of `/public/`, or paths don't include `/public/`.
**Fix:** Move all static files to the `public/` folder. Reference them as `/public/css/style.css`.

### 2. Rich text shows as raw HTML

**Problem:** Content displays `<p>Hello</p>` as text instead of rendering it.
**Cause:** Using double braces `{{body}}` on a rich text field.
**Fix:** Use triple braces `{{{body}}}` for all richText fields.

### 3. Collection listing page is blank

**Problem:** Index template shows no items.
**Cause:** Missing `{{#each collectionSlug}}` loop.
**Fix:** Add a loop: `{{#each posts}}...{{/each}}`.

### 4. All detail pages look the same

**Problem:** Every item page shows identical content.
**Cause:** Detail template has no CMS tokens — just static HTML.
**Fix:** Use tokens like `{{name}}`, `{{{body}}}`, `{{image}}` in the detail template.

### 5. Manifest uses wrong format

**Problem:** Build fails with manifest errors.
**Cause:** Using nested objects or `"collections"` instead of flat `"cmsTemplates"` keys.
**Fix:** Use flat format: `"postsIndex"`, `"postsIndexPath"`, `"postsDetail"`, `"postsDetailPath"`.

### 6. Relation field is empty after create

**Problem:** Created an item with a relation field but it's null.
**Cause:** Used the item's name instead of its UUID.
**Fix:** Run `fastmode items relations <collection> --field <field>` to get the UUID, then use that.

### 7. Forms don't submit

**Problem:** Form appears to submit (shows toast/alert) but no data is received.
**Cause:** Original JavaScript calls `preventDefault()` and shows a fake success message.
**Fix:** Remove any form JavaScript that blocks submission. Use `data-form-name` and `action="/_forms/formName"`.

### 8. Static pages can't be edited in CMS

**Problem:** Pages appear in the CMS but have no editable content.
**Cause:** Missing `data-edit-key` attributes on text elements.
**Fix:** Add `data-edit-key="unique-key"` to every text element that should be editable.

### 9. Deploy blocked by GitHub

**Problem:** `deploy` refuses to upload, says GitHub is connected.
**Cause:** Project has GitHub auto-deploy enabled.
**Fix:** Use `--force` flag: `fastmode deploy site.zip --force`.

### 10. Build fails after deploy

**Problem:** Upload succeeds but build fails.
**Fix:** Run `fastmode status` to see the error. Common causes: invalid tokens, missing template files, malformed manifest. Fix the issue and re-deploy.

### 11. Template URLs don't match manifest

**Problem:** Links in templates point to wrong paths.
**Cause:** Template hardcodes `/posts/` but manifest sets `"postsIndexPath": "/blog"`.
**Fix:** Make sure hardcoded links in templates match the paths defined in `manifest.json`.

### 12. Loop variables undefined

**Problem:** `{{@index}}` or `{{@first}}` shows nothing.
**Cause:** Used outside of a `{{#each}}` block.
**Fix:** Only use loop variables inside `{{#each}}...{{/each}}`.

### 13. Duplicate SEO meta tags

**Problem:** SEO tags show up twice in the rendered HTML.
**Cause:** HTML templates include `<title>`, `<meta name="description">`, or Open Graph tags.
**Fix:** Remove all SEO tags from templates. FastMode manages them automatically via CMS Settings. See the [SEO Tags section](#seo-tags--do-not-include) above.

### 14. CSS background images and fonts broken

**Problem:** Background images or custom fonts don't load.
**Cause:** CSS files use relative paths like `url('../images/bg.jpg')` or `url('../fonts/custom.woff')`.
**Fix:** Update all paths inside CSS files to use `/public/` prefix: `url('/public/images/bg.jpg')`, `url('/public/fonts/custom.woff2')`.

### 15. Hardcoded example content instead of CMS tokens

**Problem:** Index page shows static placeholder cards instead of real CMS data.
**Cause:** Template has hardcoded HTML cards instead of `{{#each}}` loops with CMS tokens.
**Fix:** Replace hardcoded content blocks with `{{#each collection}}...{{/each}}` loops using CMS field tokens.

---

## Pre-Deployment Checklist

Run through this checklist before every deploy:

**Structure:**
- [ ] `manifest.json` at package root
- [ ] Static pages in `pages/` folder
- [ ] CMS templates in `templates/` folder
- [ ] ALL assets in `public/` folder (not `assets/`)

**SEO (CRITICAL):**
- [ ] NO `<title>` tags in HTML
- [ ] NO `<meta name="description">` tags
- [ ] NO `<meta property="og:*">` tags
- [ ] NO `<link rel="icon">` tags

**Manifest:**
- [ ] Homepage page with `"path": "/"` exists
- [ ] CMS templates use flat `cmsTemplates` keys (NOT nested, NOT `collections`)
- [ ] Paths match original site URLs

**Templates:**
- [ ] Index templates have `{{#each}}` loops
- [ ] Detail templates have CMS tokens (`{{name}}`, `{{{body}}}`, etc.)
- [ ] Rich text fields use triple braces `{{{field}}}`
- [ ] All `{{#each}}` have matching `{{/each}}`
- [ ] All `{{#if}}` have matching `{{/if}}`
- [ ] Static UI images use `/public/` paths
- [ ] Content images use CMS tokens with `{{#if}}` wrappers

**Static Pages:**
- [ ] `data-edit-key` on every editable text element
- [ ] Keys are unique across the entire site
- [ ] Forms have `data-form-name` and `action="/_forms/{name}"`
- [ ] Original form JavaScript handlers removed or replaced

**Assets:**
- [ ] All HTML asset paths use `/public/` prefix
- [ ] CSS `background-image` and font `url()` paths use `/public/` prefix
- [ ] External URLs (Google Fonts, CDNs) unchanged

**Validation:**
```bash
fastmode validate manifest manifest.json
fastmode validate template <each-template> -t <type> [-c <collection>]
fastmode validate package site.zip
```

---

## Error Handling & Exit Codes

All commands exit with code **0** on success and code **1** on failure.

### Commands that exit 1

| Scenario | Commands |
|----------|----------|
| No project specified | All project-scoped commands |
| File not found | `schema sync`, `items create -f`, `validate *` |
| Invalid JSON | `schema sync`, `items create -d`, `items update -d` |
| Validation errors | `validate manifest`, `validate template`, `validate package` |
| Build failed | `deploy` (when waiting), `status` |
| Delete without `--confirm` | `items delete` |

### Error Messages

```
Error: No project specified.
Use -p <id-or-name>, set FASTMODE_PROJECT env var, or run: fastmode use <project>
```

```
Error: File not found: schema.json
```

```
Error: Invalid JSON in --data argument
```

```
Error: Deletion requires the --confirm flag. This action cannot be undone.
```

### Authentication Errors

Most commands auto-trigger `fastmode login` if credentials are missing or expired. If authentication fails:
1. Run `fastmode login` manually
2. Complete the browser flow
3. Retry the command

### File Locations

| Path | Purpose |
|------|---------|
| `~/.fastmode/credentials.json` | OAuth tokens (auto-created by `login`) |
| `~/.fastmode/config.json` | Default project setting (created by `use`) |

Both files have restricted permissions (0o600 — owner read/write only).

---

## Notes

- All project-scoped commands use your default project (set with `fastmode use`). Override with `-p <name-or-id>`.
- Item data (`-d`) must be valid JSON. For complex data, write a file and use `-f data.json`.
- Rich text fields accept HTML content (e.g. `<p>`, `<h2>`, `<ul>`, `<a>`). Always use triple braces in templates.
- Relation fields require item IDs (UUIDs). Use `fastmode items relations` to find available IDs.
- The `--draft` flag creates unpublished items. Use `--publish`/`--unpublish` to change status.
- Every site gets free hosting, free SSL, and a `.fastmode.ai` subdomain. Custom domains can be configured.
- After deploying or making content changes, always run `fastmode status` to verify the build succeeded.
- Use `fastmode examples <type>` and `fastmode guide [section]` for built-in documentation and code snippets.

---

## Package Provenance

- **npm package:** [fastmode-cli](https://www.npmjs.com/package/fastmode-cli)
- **Source code:** [github.com/arihgoldstein/fastmode-mcp](https://github.com/arihgoldstein/fastmode-mcp)
- **Website:** [fastmode.ai](https://fastmode.ai)
- **Author:** Arih Goldstein
- **License:** MIT
