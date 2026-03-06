# Advanced API Reference

## Custom Objects — `/objects/`
| Method | Path | Description |
|--------|------|-------------|
| GET | `/objects/` | List object schemas |
| GET | `/objects/{key}` | Get schema by key |
| PUT | `/objects/{key}` | Update schema |
| GET | `/objects/{schemaKey}/records?locationId={id}` | List records |
| POST | `/objects/{schemaKey}/records` | Create record |
| GET | `/objects/{schemaKey}/records/{id}` | Get record |
| PUT | `/objects/{schemaKey}/records/{id}` | Update record |
| DELETE | `/objects/{schemaKey}/records/{id}` | Delete record |

**Scopes**: `objects/schema.*`, `objects/record.*`

## Associations — `/associations/`
| Method | Path | Description |
|--------|------|-------------|
| GET | `/associations/?locationId={id}` | List associations |
| POST | `/associations/` | Create association |
| GET | `/associations/{associationId}` | Get association |
| PUT | `/associations/{associationId}` | Update association |
| DELETE | `/associations/{associationId}` | Delete association |
| GET | `/associations/key/{key_name}` | Get by key name |
| POST | `/associations/relations/` | Create relation |
| GET | `/associations/relations/{objectKey}` | Get relations |

**Scopes**: `associations.*`, `associations/relation.*`

## Proposals/Documents — `/proposals/`
| Method | Path | Description |
|--------|------|-------------|
| GET | `/proposals/document?locationId={id}` | List documents |
| POST | `/proposals/document/send` | Send document |
| GET | `/proposals/templates?locationId={id}` | List templates |
| POST | `/proposals/templates/send` | Send template |

**Scopes**: `documents_contracts/list.readonly`, `documents_contracts/sendlink.write`, `documents_contracts_templates/list.readonly`, `documents_contracts_templates/sendlink.write`

## Snapshots — `/snapshots/` (Agency Only)
| Method | Path | Description |
|--------|------|-------------|
| GET | `/snapshots/` | List snapshots |
| GET | `/snapshots/snapshot-status/{snapshotId}` | Snapshot status |
| POST | `/snapshots/share/link` | Create share link |

**Scopes**: `snapshots.readonly`, `snapshots.write`

## SaaS — `/saas/` (Agency $497 Plan)
| Method | Path | Description |
|--------|------|-------------|
| PUT | `/update-saas-subscription/{locationId}` | Update subscription |
| POST | `/enable-saas/{locationId}` | Enable SaaS |
| POST | `/bulk-disable-saas/{companyId}` | Bulk disable |
| POST | `/saas/bulk-enable` | Bulk enable |
| GET | `/saas/agency/plans` | List agency plans |
| GET | `/saas/location/{locationId}/subscription` | Location subscription |

**Rate Limit**: 10 req/sec (global). **Scopes**: `saas/location.*`, `saas/company.write`

## Voice AI — `/voice-ai/`
| Method | Path | Description |
|--------|------|-------------|
| GET | `/voice-ai/dashboard/call-logs` | Call logs |
| GET/POST/PATCH/DELETE | `/voice-ai/agents/...` | Agent CRUD |
| GET/POST/PUT/DELETE | `/voice-ai/actions/...` | Actions CRUD |
| GET/POST/PUT/DELETE | `/voice-ai/goals/...` | Goals CRUD |

**Scopes**: `voice-ai-dashboard.readonly`, `voice-ai-agents.*`, `voice-ai-agent-goals.*`

## Blogs — `/blogs/`
| Method | Path | Description |
|--------|------|-------------|
| POST | `/blogs/posts/{postId}` | Create blog post |
| PUT | `/blogs/posts/{postId}` | Update blog post |
| GET | `/blogs/posts/url-slug-exists` | Check slug availability |
| GET | `/blogs/categories?locationId={id}` | List categories |
| GET | `/blogs/authors?locationId={id}` | List authors |

**Scopes**: `blogs/post.write`, `blogs/post-update.write`, `blogs/check-slug.readonly`, `blogs/category.readonly`, `blogs/author.readonly`

## Courses — `/courses/`
| Method | Path | Description |
|--------|------|-------------|
| POST | `/courses/courses-exporter/public/import` | Import course |

**Scopes**: `courses.write` — Note: Currently limited to import only

## Businesses — `/businesses/`
| Method | Path | Description |
|--------|------|-------------|
| GET | `/businesses/?locationId={id}` | List businesses |
| GET/POST/PUT/DELETE | `/businesses/{businessId}` | Business CRUD |

**Scopes**: `businesses.readonly`, `businesses.write`

## Marketplace — `/marketplace/`
| Method | Path | Description |
|--------|------|-------------|
| GET | `/marketplace/app/{appId}/installations` | List installations |
| DELETE | `/marketplace/app/{appId}/installations` | Delete installation |
| GET/POST/DELETE | `/marketplace/billing/charges/...` | Billing CRUD |

**Scopes**: `marketplace-installer-details.readonly`, `charges.*`

## Other Groups (Newer/Limited Documentation)
- **Email** (`/emails/`) — Template CRUD, scheduled emails
- **Media** (`/medias/`) — File upload/list/delete
- **Custom Menus** (`/custom-menus/`) — Agency menu link CRUD
- **Phone System** (`/phone-system/`) — Phone numbers, number pools
- **Conversation AI** (`/conversation-ai/`) — Chatbot config
- **Knowledge Base** (`/knowledge-base/`) — AI knowledge base
- **AI Agent Studio** (`/agent-studio/`) — Custom AI agents
- **Brand Boards** (`/brand-boards/`) — Brand management
- **Store** (`/store/`) — E-commerce store
- **LC Email** (`/lc-email/`) — Email ISV infrastructure
