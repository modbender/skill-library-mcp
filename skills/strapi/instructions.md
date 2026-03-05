# Strapi CMS — Agent Instructions

You can manage content in a Strapi headless CMS. The Strapi instance is
configured via environment variables `STRAPI_API_TOKEN` and `STRAPI_BASE_URL`.

All operations go through `{baseDir}/src/index.ts` which wraps the
`@strapi/client` SDK.

## Important rules

**NEVER change field types to control visual layout.** If the user asks to
reorder fields, make fields full-width, put fields on the same row, or change
how the edit form looks — use the `layout` domain (`layout reorder`,
`layout set-field`). Do NOT change field types (e.g. `string` → `text`) or
schema to affect visual appearance. Schema changes alter data structure and
validation; layout changes only affect the admin panel form.

## Available commands

Run commands via `exec`:

```bash
cd {baseDir} && npx tsx src/index.ts <command> [args...]
```

### Collection types

```bash
# List entries (with optional query params as JSON)
npx tsx src/index.ts collection find <resource> [queryParams]

# Get single entry by document ID
npx tsx src/index.ts collection findOne <resource> <documentID> [queryParams]

# Create entry (data as JSON)
npx tsx src/index.ts collection create <resource> <data> [queryParams]

# Update entry
npx tsx src/index.ts collection update <resource> <documentID> <data> [queryParams]

# Delete entry
npx tsx src/index.ts collection delete <resource> <documentID> [queryParams]
```

**resource** is the plural API name (e.g. `articles`, `categories`, `users`).

### Single types

```bash
npx tsx src/index.ts single find <resource> [queryParams]
npx tsx src/index.ts single update <resource> <data> [queryParams]
npx tsx src/index.ts single delete <resource> [queryParams]
```

**resource** is the singular API name (e.g. `homepage`, `about`).

### Content management

Use the `content` domain to understand the data model, discover content types
and their structure, manage drafts and publishing.

**IMPORTANT: Before creating or editing any content, ALWAYS run `content schema`
first to understand the exact fields, their types, constraints, and relations.
This prevents errors from passing wrong field names or invalid data.**

#### Discover data structure

```bash
# List ALL content types with their fields, types, required flags, relations
npx tsx src/index.ts content types

# Get detailed schema for a specific type — shows every field with:
# type, required, unique, default, min/max, enum values, relations, localized
npx tsx src/index.ts content schema article

# List all reusable components (used in component/dynamic zone fields)
npx tsx src/index.ts content components

# Get a specific component's schema
npx tsx src/index.ts content component shared.seo

# See ALL relations between content types (relation graph)
npx tsx src/index.ts content relations

# Fetch a real entry with all relations populated — see actual data shape
npx tsx src/index.ts content inspect articles
npx tsx src/index.ts content inspect articles abc123
npx tsx src/index.ts content inspect homepage           # single types work too
```

**What `schema` returns for each field:**
- `type` — string, richtext, integer, relation, component, dynamiczone, media, etc.
- `required` — whether the field must be provided
- `unique` — whether the value must be unique
- `default` — default value if any
- `minLength`/`maxLength` — string length constraints
- `min`/`max` — numeric range constraints
- `allowedValues` — enum options (the only valid values)
- `relation`/`target` — for relations: type (oneToOne, oneToMany, etc.) and target content type
- `component`/`repeatable` — for component fields: which component and if it's an array
- `components` — for dynamic zones: list of allowed components
- `localized` — whether the field is translatable (i18n)

#### Drafts and publishing

```bash
# List all draft entries
npx tsx src/index.ts content drafts articles
npx tsx src/index.ts content drafts articles '{"sort":"updatedAt:desc"}'

# List all published entries
npx tsx src/index.ts content published articles

# Publish a draft
npx tsx src/index.ts content publish articles abc123

# Unpublish (revert to draft)
npx tsx src/index.ts content unpublish articles abc123

# Create as draft (default behavior)
npx tsx src/index.ts content create-draft articles '{"title":"Work in progress"}'

# Create and immediately publish
npx tsx src/index.ts content create-published articles '{"title":"Ready to go","content":"..."}'
```

The `publishedAt` field in responses is `null` for drafts.

#### Recommended workflow for agents

1. `content types` — discover what content types exist
2. `content schema <type>` — understand fields, types, constraints, relations
3. `content components` — if schema has component/dynamiczone fields, inspect them
4. `content relations` — understand how types connect to each other
5. `content inspect <resource>` — see a real data example with populated relations
6. Now you know the exact shape — proceed with create/update operations

### Schema management (content types & components)

**⚠️ DANGEROUS: These operations modify the database schema. Strapi restarts
after every change. Always confirm with the user before executing.**

**IMPORTANT: Schema write operations only work on local/dev Strapi instances.
Production and cloud deployments (Strapi Cloud, Docker, etc.) block schema
modifications via API. If a schema command returns 403 or an empty response,
tell the user:**
- The Strapi instance does not allow schema changes via API
- They need to create the content type manually in the Strapi admin panel
- Once the type exists, you can populate it with data using `collection create`

```bash
# Create a new collection type
npx tsx src/index.ts schema create-type '{"contentType":{"displayName":"Review","singularName":"review","pluralName":"reviews","kind":"collectionType","attributes":{"title":{"type":"string","required":true},"rating":{"type":"integer","min":1,"max":5},"body":{"type":"richtext"}}}}'

# Create a single type
npx tsx src/index.ts schema create-type '{"contentType":{"displayName":"Settings","singularName":"setting","pluralName":"settings","kind":"singleType","attributes":{"siteName":{"type":"string"},"maintenance":{"type":"boolean","default":false}}}}'

# Update a content type (full schema required — use content schema <apiID> first)
npx tsx src/index.ts schema update-type api::review.review '{"contentType":{...full schema...}}'

# Delete a content type and ALL its data
npx tsx src/index.ts schema delete-type api::review.review

# Add a single field to an existing content type
npx tsx src/index.ts schema add-field api::article.article summary '{"type":"text","maxLength":500}'

# Remove a field (and its data)
npx tsx src/index.ts schema remove-field api::article.article summary

# Create a reusable component
npx tsx src/index.ts schema create-component '{"component":{"category":"shared","displayName":"FAQ","attributes":{"question":{"type":"string","required":true},"answer":{"type":"richtext"}}}}'

# Update a component
npx tsx src/index.ts schema update-component shared.faq '{"component":{"category":"shared","displayName":"FAQ Item","attributes":{...}}}'

# Delete a component
npx tsx src/index.ts schema delete-component shared.faq
```

**Recommended workflow for schema changes:**

1. `content schema <type>` — read current schema first
2. `schema add-field` or `schema remove-field` — for single field changes
3. `schema update-type` — for complex changes (pass the full updated schema)
4. Wait for Strapi to restart (10–30 seconds)
5. `content schema <type>` — verify the change applied

**If a schema command fails with HTTP 403 or "unauthorized":**
The Strapi instance does not allow schema modifications via API. This is
the expected behavior on production and cloud deployments. Offer the user
two options:
1. **Admin panel** — go to Strapi admin → Content-Type Builder, create the
   content type or component manually with the required fields, then you can
   populate data via `collection create`
2. **Dev mode** — switch Strapi to local/dev mode where the Content-Type
   Builder API allows write operations, then retry the command

**Available field types:** string, text, richtext, integer, biginteger, float,
decimal, boolean, date, time, datetime, json, uid, email, password,
enumeration, relation, component, dynamiczone, media.

### Edit form layout (field order, sizes, metadata)

**Only works on local/dev Strapi instances.** Production deployments block
layout configuration via API.

```bash
# Get the current edit form layout for a content type
npx tsx src/index.ts layout get api::article.article

# Get layout for a component
npx tsx src/index.ts layout get-component shared.seo

# Update a single field's display settings (label, description, placeholder, size)
npx tsx src/index.ts layout set-field api::article.article title '{"edit":{"label":"Article Title","description":"Main heading of the article","size":6}}'

# Reorder fields in the edit form (12-column grid, sizes per row must sum to 12)
npx tsx src/index.ts layout reorder api::article.article '[[{"name":"title","size":6},{"name":"slug","size":6}],[{"name":"content","size":12}],[{"name":"cover","size":6},{"name":"category","size":6}]]'

# Full layout update (edit rows + list columns + field metadata)
npx tsx src/index.ts layout update api::article.article '{"layouts":{"edit":[[{"name":"title","size":6},{"name":"slug","size":6}],[{"name":"content","size":12}]],"list":["title","createdAt","updatedAt"]},"metadatas":{"title":{"edit":{"label":"Title","visible":true,"editable":true}}}}'

# Update component layout
npx tsx src/index.ts layout update-component shared.seo '{"layouts":{"edit":[[{"name":"metaTitle","size":6},{"name":"metaDescription","size":6}]]}}'
```

**Typical use case — stack fields vertically, pair only coordinates:**

```bash
# All fields full-width (size:12) EXCEPT latitude+longitude side by side (size:6 each)
npx tsx src/index.ts layout reorder api::reception-address.reception-address '[[{"name":"name","size":12}],[{"name":"address","size":12}],[{"name":"description","size":12}],[{"name":"latitude","size":6},{"name":"longitude","size":6}]]'
```

This puts each field on its own row (full width) except lat/lng which share a row.
**No schema changes needed** — field types stay the same, only visual layout changes.

**Recommended workflow:**

1. `layout get <uid>` — read current layout first to see field names, sizes, order
2. `layout set-field` — for changing a single field's label/description/size
3. `layout reorder` — for reordering fields (each row is an array of `{name, size}`)
4. `layout update` — for complex changes (full replacement of layouts + metadatas)

**Edit layout grid:** Strapi uses a 12-column grid. Field `size` values in a row
must sum to 12. Common sizes: 12 (full width), 6 (half), 4 (third), 3 (quarter).

**Field metadata properties (edit):**
- `label` — display label in the form
- `description` — help text below the field
- `placeholder` — placeholder text for text inputs
- `visible` — whether the field is shown in the edit form
- `editable` — whether the field can be edited
- `mainField` — for relation fields, which field of the related type to display
- `size` — column width (1–12)

**Field metadata properties (list):**
- `label` — column header in list view
- `searchable` — whether the field is searchable in list view
- `sortable` — whether the column is sortable

**If layout commands fail with 403:** Offer the user two options:
1. **Admin panel** — configure the layout in Strapi admin → Content-Type
   Builder → select the type → Configure the view
2. **Dev mode** — switch Strapi to local/dev mode where the API allows
   layout configuration, then retry the command

### Files (Media Library)

```bash
npx tsx src/index.ts files find [queryParams]
npx tsx src/index.ts files findOne <fileID>
npx tsx src/index.ts files update <fileID> <fileInfo>
npx tsx src/index.ts files delete <fileID>

# Upload from local filesystem
npx tsx src/index.ts files upload /path/to/image.jpg

# Upload from URL
npx tsx src/index.ts files upload https://example.com/photo.png

# Upload with metadata (name, alt text, caption)
npx tsx src/index.ts files upload /path/to/hero.png '{"name":"homepage-hero","alternativeText":"Hero banner","caption":"Main page hero image"}'

# Upload from URL with metadata
npx tsx src/index.ts files upload https://example.com/banner.jpg '{"alternativeText":"Banner image"}'

# Upload and link to a content entry (attach cover image to an article)
npx tsx src/index.ts files upload /path/to/cover.jpg '{"alternativeText":"Article cover"}' '{"ref":"api::article.article","refId":"abc123","field":"cover"}'
```

**Upload parameters:**
- `source` (required) — local file path OR URL (`http://` / `https://`)
- `fileInfo` (optional) — JSON with `name`, `alternativeText`, `caption`
- `linkInfo` (optional) — JSON with `ref` (content type UID), `refId` (document ID), `field` (media field name)

When uploading from URL, the file is downloaded first and then uploaded to Strapi.
MIME type is detected from the URL's Content-Type header (with fallback to file extension).
Files uploaded via API are placed in the "API Uploads" folder in Strapi's Media Library.

### Users & Permissions

Manage end users (not admin users), their roles, and authentication.

```bash
# List all end users
npx tsx src/index.ts users find

# List with filters (e.g. only confirmed users)
npx tsx src/index.ts users find '{"confirmed":"true"}'

# Get a specific user
npx tsx src/index.ts users findOne 3

# Get current authenticated user
npx tsx src/index.ts users me

# Create a new end user
npx tsx src/index.ts users create '{"username":"jane","email":"jane@example.com","password":"Str0ng!Pass","role":1}'

# Update user
npx tsx src/index.ts users update 3 '{"blocked":false,"confirmed":true}'

# Delete user
npx tsx src/index.ts users delete 3

# Count users
npx tsx src/index.ts users count
```

**Roles management:**

```bash
# List all end-user roles (Public, Authenticated, custom)
npx tsx src/index.ts users roles

# Get role details with its permissions
npx tsx src/index.ts users role 1
```

**Authentication (for front-end user flows):**

```bash
# Login — returns JWT token and user data
npx tsx src/index.ts users login '{"identifier":"user@example.com","password":"password123"}'

# Register a new end user (if signups are enabled)
npx tsx src/index.ts users register '{"username":"newuser","email":"new@example.com","password":"Str0ng!Pass"}'

# Request password reset email
npx tsx src/index.ts users forgot-password '{"email":"user@example.com"}'

# Reset password with token from email
npx tsx src/index.ts users reset-password '{"code":"resetToken","password":"NewPass!123","passwordConfirmation":"NewPass!123"}'
```

**Important notes:**
- `users find/findOne/create/update/delete` require the API token to have
  permissions for "Users-permissions" → "User" actions
- `users login/register` work without authentication (public endpoints)
- `identifier` in login can be either email or username
- The `role` field in create/update is the numeric role ID (get IDs from `users roles`)

### Locales (i18n)

```bash
# List all configured locales
npx tsx src/index.ts locale list

# Get a specific locale by ID or code
npx tsx src/index.ts locale get fr
npx tsx src/index.ts locale get 2

# Create a new locale
npx tsx src/index.ts locale create '{"name":"French (France)","code":"fr","isDefault":false}'

# Delete a locale by ID
npx tsx src/index.ts locale delete 3
```

Locale codes follow ISO format (e.g. `en`, `fr`, `de`, `es`, `uk`, `ja`, `zh`).
Locales must exist in Strapi before you can create or query localized content.

### Localized content (translations)

Use the `localize` domain for all translation workflows. It provides locale-first
commands that are clearer than passing `locale` as a query param.

```bash
# Get content in a specific locale
npx tsx src/index.ts localize get collection articles fr
npx tsx src/index.ts localize get collection articles fr abc123
npx tsx src/index.ts localize get single homepage es

# Get content in ALL configured locales at once
npx tsx src/index.ts localize get-all collection articles abc123
npx tsx src/index.ts localize get-all single homepage

# Check translation status — which locales exist for a document
npx tsx src/index.ts localize status collection articles abc123
npx tsx src/index.ts localize status single homepage

# Create a localized version
npx tsx src/index.ts localize create collection articles fr '{"title":"Bonjour"}'
npx tsx src/index.ts localize create single homepage es '{"title":"Bienvenidos"}'

# Update a localized version
npx tsx src/index.ts localize update collection articles fr abc123 '{"title":"Titre mis à jour"}'
npx tsx src/index.ts localize update single homepage es '{"title":"Página principal"}'

# Delete a specific locale version only
npx tsx src/index.ts localize delete collection articles fr abc123
npx tsx src/index.ts localize delete single homepage fr
```

**Workflow for translating content:**

1. Use `localize status` to see which locales exist for a document
2. Use `localize get` to read the source locale content
3. Use `localize create` or `localize update` to write the translation
4. Use `localize get-all` to verify all translations

### Raw fetch

```bash
npx tsx src/index.ts fetch <method> <path> [body]
```

Example: `npx tsx src/index.ts fetch GET /content-type-builder/content-types`

## JSON arguments

Pass JSON arguments as single-quoted strings:

```bash
npx tsx src/index.ts collection find articles '{"sort":"title","locale":"en"}'
npx tsx src/index.ts collection create articles '{"title":"Hello","content":"World"}'
```

## Query parameters reference

Strapi supports these query params for `find`:
- `sort` — field or array of fields (`title:asc`, `createdAt:desc`)
- `filters` — nested filter object (`{"title":{"$contains":"hello"}}`)
- `populate` — relations to include (`*` for all, or specific field names)
- `fields` — select specific fields
- `pagination` — `{"page":1,"pageSize":25}` or `{"start":0,"limit":25}`
- `locale` — content locale
- `status` — `draft` or `published`

## Error handling

All commands print JSON to stdout. On success you get the Strapi response.
On error you get `{"error": "message"}`. Check the output before proceeding.

## Important notes

- The `users` collection (users-permissions plugin) has a different API contract.
  The SDK handles this automatically — no `data` wrapper needed.
- File upload is not supported through this CLI. Use the Strapi admin panel
  or direct HTTP multipart requests for uploading new files.
- Always use `populate` to include relations in responses — Strapi does not
  include them by default.
