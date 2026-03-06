# Strapi CMS Skill for OpenClaw

Manage your Strapi headless CMS content directly through [OpenClaw](https://github.com/open-claw) using the official [@strapi/client](https://github.com/strapi/client) SDK.

## Features

- **Collection types** — full CRUD (find, findOne, create, update, delete)
- **Single types** — find, update, delete
- **Content introspection** — discover types, schemas, components, relations; inspect real data shape
- **Schema management** — create/update/delete content types, components, fields (local/dev only; production blocks this)
- **Form layout** — configure edit form field order, sizes, labels, descriptions (local/dev only)
- **Draft & publish** — list drafts/published, publish, unpublish, create as draft or published
- **Media library** — list, get, upload, update metadata, delete files
- **Users & Permissions** — end-user CRUD, roles, authentication (login, register, password reset)
- **Locales (i18n)** — list, create, delete locales
- **Localized content** — CRUD per locale, translation status, fetch all locales at once
- **Raw fetch** — direct HTTP requests to any Strapi endpoint

## Requirements

- Node.js >= 18
- Strapi v5 instance with API token

## Installation

### From ClawHub

```bash
openclaw skills install strapi
```

### Manual

```bash
git clone https://github.com/open-claw/strapi.git ~/.openclaw/skills/strapi
cd ~/.openclaw/skills/strapi
npm install
```

## Configuration

During installation, enter your **Strapi API Token** in the API Key field.
Then add `STRAPI_BASE_URL` to the `env` section in `~/.openclaw/openclaw.json`:

| Variable | Required | Description |
|----------|----------|-------------|
| `STRAPI_API_TOKEN` | yes | Strapi API token (entered as API Key during install) |
| `STRAPI_BASE_URL` | yes | Strapi API endpoint (e.g. `http://localhost:1337/api`) |

```json5
{
  skills: {
    entries: {
      strapi: {
        enabled: true,
        apiKey: "your-strapi-api-token",     // → STRAPI_API_TOKEN
        env: {
          STRAPI_BASE_URL: "http://localhost:1337/api"
        }
      }
    }
  }
}
```

Or as system environment variables:

```bash
export STRAPI_API_TOKEN="your-api-token-here"
export STRAPI_BASE_URL="http://localhost:1337/api"
```

## Usage

All commands follow the pattern:

```bash
npx tsx src/index.ts <domain> <action> [args...]
```

### Content introspection

Understand your data model before creating or editing content.

```bash
# List all content types with fields, constraints, relations
npx tsx src/index.ts content types

# Detailed schema for a specific type
npx tsx src/index.ts content schema article

# List all reusable components
npx tsx src/index.ts content components

# Specific component schema
npx tsx src/index.ts content component shared.seo

# Relation map between content types
npx tsx src/index.ts content relations

# Inspect a real entry with all relations populated
npx tsx src/index.ts content inspect articles
npx tsx src/index.ts content inspect articles abc123
npx tsx src/index.ts content inspect homepage          # single types work too
```

### Schema management (content types & components)

> **Warning:** These operations modify the database schema and trigger a Strapi restart.
> **Only works on local/dev Strapi instances.** Production and cloud deployments
> block schema modifications via API — if you get a 403 error, create the content
> type in the Strapi admin panel and use `collection create` to populate data.

```bash
# Create a collection type
npx tsx src/index.ts schema create-type '{"contentType":{"displayName":"Review","singularName":"review","pluralName":"reviews","attributes":{"title":{"type":"string","required":true},"rating":{"type":"integer","min":1,"max":5}}}}'

# Add a field to an existing type
npx tsx src/index.ts schema add-field api::article.article summary '{"type":"text","maxLength":500}'

# Remove a field
npx tsx src/index.ts schema remove-field api::article.article summary

# Delete a content type
npx tsx src/index.ts schema delete-type api::review.review

# Create a component
npx tsx src/index.ts schema create-component '{"component":{"category":"shared","displayName":"FAQ","attributes":{"question":{"type":"string","required":true},"answer":{"type":"richtext"}}}}'

# Delete a component
npx tsx src/index.ts schema delete-component shared.faq
```

### Edit form layout

> **Only works on local/dev Strapi.** Production deployments block this API.

```bash
# Get current form layout
npx tsx src/index.ts layout get api::article.article

# Change a field's label and size
npx tsx src/index.ts layout set-field api::article.article title '{"edit":{"label":"Article Title","size":6}}'

# Reorder fields (12-column grid)
npx tsx src/index.ts layout reorder api::article.article '[[{"name":"title","size":6},{"name":"slug","size":6}],[{"name":"content","size":12}]]'
```

### Draft & publish workflow

```bash
npx tsx src/index.ts content drafts articles
npx tsx src/index.ts content published articles
npx tsx src/index.ts content publish articles abc123
npx tsx src/index.ts content unpublish articles abc123
npx tsx src/index.ts content create-draft articles '{"title":"WIP"}'
npx tsx src/index.ts content create-published articles '{"title":"Ready","content":"..."}'
```

### Collection types

```bash
npx tsx src/index.ts collection find articles
npx tsx src/index.ts collection find articles '{"sort":"title:asc","populate":"*"}'
npx tsx src/index.ts collection findOne articles abc123
npx tsx src/index.ts collection create articles '{"title":"New Post","content":"Hello"}'
npx tsx src/index.ts collection update articles abc123 '{"title":"Updated"}'
npx tsx src/index.ts collection delete articles abc123
```

### Single types

```bash
npx tsx src/index.ts single find homepage
npx tsx src/index.ts single update homepage '{"title":"Welcome"}'
npx tsx src/index.ts single delete homepage
```

### Media files

```bash
npx tsx src/index.ts files find
npx tsx src/index.ts files findOne 1
npx tsx src/index.ts files update 1 '{"name":"new-name","alternativeText":"Alt text"}'
npx tsx src/index.ts files delete 1

# Upload from local file
npx tsx src/index.ts files upload ./hero.jpg '{"alternativeText":"Hero image"}'

# Upload from URL
npx tsx src/index.ts files upload https://example.com/photo.png '{"alternativeText":"Downloaded photo"}'

# Upload and link to a content entry
npx tsx src/index.ts files upload ./cover.png '{"alternativeText":"Cover"}' '{"ref":"api::article.article","refId":"abc123","field":"cover"}'
```

### Users & Permissions

```bash
# List / get users
npx tsx src/index.ts users find
npx tsx src/index.ts users findOne 3
npx tsx src/index.ts users me

# Create / update / delete
npx tsx src/index.ts users create '{"username":"jane","email":"jane@example.com","password":"Str0ng!Pass","role":1}'
npx tsx src/index.ts users update 3 '{"blocked":false}'
npx tsx src/index.ts users delete 3

# Roles
npx tsx src/index.ts users roles
npx tsx src/index.ts users role 1

# Auth
npx tsx src/index.ts users login '{"identifier":"user@example.com","password":"pass123"}'
npx tsx src/index.ts users register '{"username":"new","email":"new@example.com","password":"Str0ng!Pass"}'
npx tsx src/index.ts users forgot-password '{"email":"user@example.com"}'
```

### Locales (i18n)

```bash
npx tsx src/index.ts locale list
npx tsx src/index.ts locale get fr
npx tsx src/index.ts locale create '{"name":"French","code":"fr","isDefault":false}'
npx tsx src/index.ts locale delete 3
```

### Localized content (translations)

```bash
# Get content in a specific locale
npx tsx src/index.ts localize get collection articles fr
npx tsx src/index.ts localize get collection articles fr abc123
npx tsx src/index.ts localize get single homepage es

# Get content in ALL locales
npx tsx src/index.ts localize get-all collection articles abc123
npx tsx src/index.ts localize get-all single homepage

# Translation status
npx tsx src/index.ts localize status collection articles abc123

# Create/update/delete translations
npx tsx src/index.ts localize create collection articles fr '{"title":"Bonjour"}'
npx tsx src/index.ts localize update collection articles fr abc123 '{"title":"Titre"}'
npx tsx src/index.ts localize delete collection articles fr abc123
```

### Raw fetch

```bash
npx tsx src/index.ts fetch GET /content-type-builder/content-types
npx tsx src/index.ts fetch POST /custom-endpoint '{"key":"value"}'
```

## Query Parameters

| Parameter    | Description              | Example                                     |
|-------------|--------------------------|---------------------------------------------|
| `sort`      | Sort by field(s)         | `"title:asc"` or `["title:asc","date:desc"]` |
| `filters`   | Filter entries           | `{"title":{"$contains":"hello"}}`           |
| `populate`  | Include relations        | `"*"` or `["author","category"]`            |
| `fields`    | Select specific fields   | `["title","content"]`                       |
| `pagination`| Paginate results         | `{"page":1,"pageSize":25}`                  |
| `locale`    | Content locale           | `"en"`, `"fr"`                              |
| `status`    | Draft or published       | `"draft"`, `"published"`                    |

## Project Structure

```
strapi/
├── claw.json            # OpenClaw skill manifest
├── SKILL.md             # Skill metadata and gating
├── instructions.md      # Agent instructions
├── README.md
├── LICENSE
├── package.json
├── tsconfig.json
├── examples/
│   └── usage.md         # Conversation examples
└── src/
    ├── index.ts         # CLI entry point and router
    ├── client.ts        # Strapi client factory
    ├── types.ts         # Shared TypeScript interfaces
    └── handlers/
        ├── collection.ts  # Collection type CRUD
        ├── single.ts      # Single type operations
        ├── content.ts     # Schema introspection + draft/publish
        ├── schema.ts      # Content type & component CRUD (destructive)
        ├── layout.ts      # Edit form layout configuration
        ├── files.ts       # Media library operations + upload
        ├── users.ts       # Users & Permissions + auth
        ├── locale.ts      # i18n locale management
        └── localize.ts    # Localized content operations
```

## License

MIT
