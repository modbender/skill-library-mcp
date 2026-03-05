#!/usr/bin/env node

import { createClient, fetchJson } from './client.js';
import { handleCollection } from './handlers/collection.js';
import { handleSingle } from './handlers/single.js';
import { handleFiles } from './handlers/files.js';
import { handleLocale } from './handlers/locale.js';
import { handleLocalize } from './handlers/localize.js';
import { handleContent } from './handlers/content.js';
import { handleSchema } from './handlers/schema.js';
import { handleLayout } from './handlers/layout.js';
import { handleUsers } from './handlers/users.js';

function printUsage(): void {
  const usage = `
Strapi CMS Skill — CLI Interface

Usage:
  npx tsx src/index.ts <domain> <action> [args...]

Domains:
  collection  Manage collection-type content (articles, categories, users, etc.)
  single      Manage single-type content (homepage, about, etc.)
  content     Content management (types, schemas, drafts, publishing)
  schema      Modify data structure (content types, components, fields) ⚠️  DESTRUCTIVE
  layout      Manage edit form layout (field order, sizes, metadata) ⚠️  LOCAL/DEV ONLY
  files       Manage media library files (including upload)
  users       Users & Permissions (CRUD, roles, auth)
  locale      Manage i18n locales (list, create, delete)
  localize    Work with localized content (translations)
  fetch       Raw HTTP request to Strapi API

Collection actions:
  find <resource> [queryParams]
  findOne <resource> <documentID> [queryParams]
  create <resource> <data> [queryParams]
  update <resource> <documentID> <data> [queryParams]
  delete <resource> <documentID> [queryParams]

Single type actions:
  find <resource> [queryParams]
  update <resource> <data> [queryParams]
  delete <resource> [queryParams]

Files actions:
  find [queryParams]
  findOne <fileID>
  upload <source> [fileInfo] [linkInfo]     Upload a file (local path or URL)
  update <fileID> <fileInfo>
  delete <fileID>

Users & Permissions actions:
  find [queryParams]                        List end users
  findOne <userID>                          Get user by ID
  me                                        Get current authenticated user
  create <data>                             Create a new end user
  update <userID> <data>                    Update end user
  delete <userID>                           Delete end user
  count                                     Count end users
  roles                                     List all end-user roles
  role <roleID>                             Get role details with permissions
  login <credentials>                       Authenticate (returns JWT)
  register <data>                           Register a new end user
  forgot-password <data>                    Request password reset email
  reset-password <data>                     Reset password with token

Content management actions:
  types                                  List all content types with fields, relations, constraints
  schema <apiID>                         Detailed schema: field types, required, enums, relations
  components                             List all reusable components
  component <uid>                        Detailed component schema (e.g. "shared.seo")
  relations                              Map of all relations between content types
  inspect <resource> [documentID]        Fetch real entry with populated relations (collections & singles)
  drafts <resource> [queryParams]        Get all draft entries
  published <resource> [queryParams]     Get all published entries
  publish <resource> <documentID>        Publish a draft
  unpublish <resource> <documentID>      Unpublish (revert to draft)
  create-draft <resource> <data>         Create as draft (default)
  create-published <resource> <data>     Create and immediately publish

Schema actions (⚠️  modifies database, triggers Strapi restart):
  create-type <payload>                  Create a new content type
  update-type <uid> <payload>            Update content type schema
  delete-type <uid>                      Delete content type and ALL its data
  create-component <payload>             Create a new component
  update-component <uid> <payload>       Update component schema
  delete-component <uid>                 Delete a component
  add-field <uid> <fieldName> <fieldDef> Add a field to a content type
  remove-field <uid> <fieldName>         Remove a field (and its data) from a content type

Layout actions (edit form configuration, ⚠️  local/dev only):
  get <uid>                                Get edit form layout for a content type
  get-component <uid>                      Get form layout for a component
  update <uid> <payload>                   Update full layout (edit rows, list columns, field metadata)
  update-component <uid> <payload>         Update component layout
  set-field <uid> <fieldName> <metadata>   Update display settings for a single field
  reorder <uid> <editLayout>               Reorder fields in the edit form (12-column grid)

Locale actions (i18n):
  list
  get <localeID|code>
  create <data>                          e.g. '{"name":"French","code":"fr","isDefault":false}'
  delete <localeID>

Localize actions (translations):
  get <collection|single> <resource> <locale> [documentID] [queryParams]
  get-all <collection|single> <resource> [documentID] [queryParams]
  create <collection|single> <resource> <locale> <data>
  update <collection|single> <resource> <locale> <documentID> <data>   (collection)
  update single <resource> <locale> <data>                              (single type)
  delete <collection|single> <resource> <locale> [documentID]
  status <collection|single> <resource> [documentID]

Fetch:
  fetch <METHOD> <path> [body]

All JSON arguments should be valid JSON strings.

Environment:
  STRAPI_API_TOKEN  Strapi API token (required)
  STRAPI_BASE_URL   Strapi API base URL (required)
`.trim();

  console.log(usage);
}

async function handleFetch(
  client: ReturnType<typeof createClient>,
  args: string[]
): Promise<unknown> {
  const method = (args[0] ?? 'GET').toUpperCase();
  const path = args[1];

  if (!path) {
    throw new Error('Path is required for fetch (e.g. /content-type-builder/content-types)');
  }

  const options: RequestInit = { method };

  if (args[2] && ['POST', 'PUT', 'PATCH'].includes(method)) {
    options.body = args[2];
    options.headers = { 'Content-Type': 'application/json' };
  }

  return fetchJson(client, path, options);
}

async function main(): Promise<void> {
  const args = process.argv.slice(2);

  if (args.length === 0 || args[0] === '--help' || args[0] === '-h') {
    printUsage();
    process.exit(0);
  }

  const domain = args[0];
  const action = args[1];
  const restArgs = args.slice(2);

  if (!action && domain !== 'fetch') {
    throw new Error(`Action is required. Run with --help for usage.`);
  }

  const client = createClient();
  let result: unknown;

  switch (domain) {
    case 'collection':
      result = await handleCollection(client, action, restArgs);
      break;

    case 'single':
      result = await handleSingle(client, action, restArgs);
      break;

    case 'files':
      result = await handleFiles(client, action, restArgs);
      break;

    case 'locale':
      result = await handleLocale(client, action, restArgs);
      break;

    case 'localize':
      result = await handleLocalize(client, action, restArgs);
      break;

    case 'content':
      result = await handleContent(client, action, restArgs);
      break;

    case 'schema':
      result = await handleSchema(client, action, restArgs);
      break;

    case 'layout':
      result = await handleLayout(client, action, restArgs);
      break;

    case 'users':
      result = await handleUsers(client, action, restArgs);
      break;

    case 'fetch':
      result = await handleFetch(client, args.slice(1));
      break;

    default:
      throw new Error(
        `Unknown domain: "${domain}". Use: collection, single, content, schema, layout, files, users, locale, localize, fetch`
      );
  }

  console.log(JSON.stringify(result, null, 2));
}

main().catch((error: Error) => {
  const msg = error.message ?? String(error);
  const baseURL = process.env.STRAPI_BASE_URL;

  if (/ECONNREFUSED|ENOTFOUND|ETIMEDOUT|fetch failed/i.test(msg)) {
    console.error(JSON.stringify({
      error: `Cannot connect to Strapi at ${baseURL ?? '(not set)'}. Verify that STRAPI_BASE_URL is correct and the Strapi server is running.`,
      details: msg,
    }));
  } else {
    console.error(JSON.stringify({ error: msg }));
  }

  process.exit(1);
});
