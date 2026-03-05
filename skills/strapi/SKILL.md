---
name: strapi
description: Manage Strapi CMS content through the official @strapi/client SDK. CRUD on collection types, single types, and media files. Upload files to media library. Introspect content type schemas, relations, and components. Manage i18n locales and localized content (translations). Draft/publish workflow. Configure edit form layout (field order, sizes, labels). Manage end users, roles, and authentication. Use when the user asks about Strapi, headless CMS, content management, managing articles, blog posts, pages, entries, media files, upload images, upload from URL, download and upload, translations, localization, publishing, drafts, content types, schemas, form layout, edit view, users, roles, permissions, authentication, login, register, REST API, or creating/updating/deleting CMS content.
metadata: {"openclaw": {"emoji": "🔵", "requires": {"bins": ["node"], "env": ["STRAPI_API_TOKEN", "STRAPI_BASE_URL"]}, "primaryEnv": "STRAPI_API_TOKEN", "install": [{"id": "node", "kind": "node", "package": ".", "bins": ["node"], "label": "Install Strapi skill dependencies"}]}}
---

# Strapi CMS Skill

Manage content in a Strapi headless CMS instance via the official `@strapi/client` SDK.

## Setup

During installation, enter your **Strapi API Token** in the API Key field.
Then add `STRAPI_BASE_URL` to the `env` section:

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

## Capabilities

- **Collection types**: find, findOne, create, update, delete entries
- **Single types**: find, update, delete the document
- **Content introspection**: discover types, schemas, components, relations, inspect real data
- **Schema management**: create/update/delete content types, components, fields (destructive)
- **Form layout**: configure edit form field order, sizes, labels, descriptions (local/dev only)
- **Draft & publish**: list drafts, publish, unpublish, create as draft or published
- **Files**: list, get, upload (local path or URL), update metadata, delete media files
- **Users & Permissions**: list, create, update, delete end users; view roles; login, register, password reset
- **Locales (i18n)**: list, create, delete locales
- **Localized content**: CRUD per locale, translation status, fetch all locales at once
- **Raw fetch**: direct HTTP to any Strapi endpoint

## Usage

See [instructions.md](instructions.md) for full agent instructions.
See [examples/usage.md](examples/usage.md) for conversation examples.
